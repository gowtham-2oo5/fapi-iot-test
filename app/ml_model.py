import pickle
import numpy as np
import faiss
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta
from sqlalchemy import select
from database import SensorReading, WeatherData, AIPrediction, async_session_maker
from pathlib import Path
import json

MODEL_PATH = Path("models/trained_model.pkl")
SCALER_PATH = Path("models/scaler.pkl")
FAISS_INDEX_PATH = Path("models/faiss_index.bin")
FAISS_METADATA_PATH = Path("models/faiss_metadata.json")
TRAINING_DATA_PATH = Path("models/training_vectors.npy")

# Ensure models directory exists
Path("models").mkdir(exist_ok=True)


class ApplianceScheduler:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.faiss_index = None
        self.metadata = []
        self.load_model()
        self.load_faiss_index()
    
    def load_model(self):
        """Load trained model and scaler from disk"""
        if MODEL_PATH.exists() and SCALER_PATH.exists():
            with open(MODEL_PATH, "rb") as f:
                self.model = pickle.load(f)
            with open(SCALER_PATH, "rb") as f:
                self.scaler = pickle.load(f)
            print("✓ Model loaded from disk")
        else:
            print("⚠ No trained model found")
    
    def save_model(self):
        """Save trained model and scaler to disk"""
        with open(MODEL_PATH, "wb") as f:
            pickle.dump(self.model, f)
        with open(SCALER_PATH, "wb") as f:
            pickle.dump(self.scaler, f)
        print("✓ Model saved to disk")
    
    def load_faiss_index(self):
        """Load FAISS index and metadata from disk"""
        if FAISS_INDEX_PATH.exists() and FAISS_METADATA_PATH.exists():
            self.faiss_index = faiss.read_index(str(FAISS_INDEX_PATH))
            with open(FAISS_METADATA_PATH, "r") as f:
                self.metadata = json.load(f)
            print(f"✓ FAISS index loaded: {self.faiss_index.ntotal} vectors")
        else:
            print("⚠ No FAISS index found, will create on first training")
    
    def save_faiss_index(self):
        """Save FAISS index and metadata to disk"""
        if self.faiss_index is not None:
            faiss.write_index(self.faiss_index, str(FAISS_INDEX_PATH))
            with open(FAISS_METADATA_PATH, "w") as f:
                json.dump(self.metadata, f)
            print(f"✓ FAISS index saved: {self.faiss_index.ntotal} vectors")
    
    def add_to_faiss(self, vectors, metadata_list):
        """Add vectors to FAISS index"""
        vectors = np.array(vectors, dtype=np.float32)
        
        if self.faiss_index is None:
            # Create new index (using L2 distance)
            dimension = vectors.shape[1]
            self.faiss_index = faiss.IndexFlatL2(dimension)
            self.metadata = []
        
        # Add vectors to index
        self.faiss_index.add(vectors)
        self.metadata.extend(metadata_list)
        
        print(f"✓ Added {len(vectors)} vectors to FAISS index")
    
    def search_similar(self, query_vector, k=5):
        """Search for k most similar vectors in FAISS index"""
        if self.faiss_index is None or self.faiss_index.ntotal == 0:
            return []
        
        query_vector = np.array([query_vector], dtype=np.float32)
        distances, indices = self.faiss_index.search(query_vector, min(k, self.faiss_index.ntotal))
        
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.metadata):
                results.append({
                    "distance": float(dist),
                    "metadata": self.metadata[idx]
                })
        
        return results
    
    async def train_model(self):
        """Train the Linear Regression model with historical data and store in FAISS"""
        async with async_session_maker() as session:
            # Fetch sensor readings
            sensor_result = await session.execute(
                select(SensorReading).order_by(SensorReading.timestamp)
            )
            sensors = sensor_result.scalars().all()
            
            # Fetch weather data
            weather_result = await session.execute(
                select(WeatherData).order_by(WeatherData.timestamp)
            )
            weathers = weather_result.scalars().all()
            
            if len(sensors) < 10 or len(weathers) < 1:
                print(f"⚠ Insufficient data for training (sensors: {len(sensors)}, weather: {len(weathers)})")
                return False
            
            # Prepare training data
            X = []
            y = []
            metadata_list = []
            
            for sensor in sensors:
                # Find closest weather data
                if not weathers:
                    continue
                    
                closest_weather = min(
                    weathers,
                    key=lambda w: abs((w.timestamp - sensor.timestamp).total_seconds())
                )
                
                # Features: ldr_value, temperature, humidity, cloud_cover, hour_of_day
                hour = sensor.timestamp.hour
                features = [
                    sensor.ldr_value,
                    closest_weather.temperature,
                    closest_weather.humidity,
                    closest_weather.cloud_cover,
                    hour
                ]
                X.append(features)
                
                # Target: optimal usage score (higher LDR = better for solar-powered appliances)
                optimal_score = sensor.ldr_value / 1024.0  # assuming 10-bit ADC
                y.append(optimal_score)
                
                # Metadata for FAISS
                metadata_list.append({
                    "timestamp": sensor.timestamp.isoformat(),
                    "device_id": sensor.device_id,
                    "ldr_value": sensor.ldr_value,
                    "temperature": closest_weather.temperature,
                    "humidity": closest_weather.humidity,
                    "cloud_cover": closest_weather.cloud_cover,
                    "hour": hour,
                    "optimal_score": optimal_score
                })
            
            if len(X) < 10:
                print(f"⚠ Insufficient valid data pairs (got {len(X)})")
                return False
            
            X = np.array(X)
            y = np.array(y)
            
            # Scale features
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X)
            
            # Train model
            self.model = LinearRegression()
            self.model.fit(X_scaled, y)
            
            # Store vectors in FAISS
            self.add_to_faiss(X_scaled, metadata_list)
            
            # Save everything
            self.save_model()
            self.save_faiss_index()
            
            # Save raw training data
            np.save(TRAINING_DATA_PATH, X_scaled)
            
            print(f"✓ Model trained with {len(X)} samples")
            print(f"✓ Training data stored in FAISS index")
            return True
    
    async def predict_optimal_hours(self, use_similar=True):
        """Predict optimal appliance usage hours for next 24 hours using FAISS similarity"""
        if self.model is None or self.scaler is None:
            print("⚠ Model not trained yet")
            return []
        
        async with async_session_maker() as session:
            # Get latest sensor and weather data
            latest_sensor = await session.execute(
                select(SensorReading).order_by(SensorReading.timestamp.desc()).limit(1)
            )
            sensor = latest_sensor.scalar_one_or_none()
            
            latest_weather = await session.execute(
                select(WeatherData).order_by(WeatherData.timestamp.desc()).limit(1)
            )
            weather = latest_weather.scalar_one_or_none()
            
            if not sensor or not weather:
                print("⚠ No sensor or weather data available")
                return []
            
            predictions = []
            current_time = datetime.utcnow()
            
            # Predict for next 24 hours
            for hour_offset in range(24):
                future_hour = (current_time.hour + hour_offset) % 24
                
                # Use current readings as baseline
                features = np.array([[
                    sensor.ldr_value,
                    weather.temperature,
                    weather.humidity,
                    weather.cloud_cover,
                    future_hour
                ]])
                
                features_scaled = self.scaler.transform(features)
                score = self.model.predict(features_scaled)[0]
                
                # Enhance prediction with FAISS similarity search
                if use_similar and self.faiss_index is not None and self.faiss_index.ntotal > 0:
                    similar = self.search_similar(features_scaled[0], k=5)
                    if similar:
                        # Weight prediction with similar historical patterns
                        similar_scores = [s["metadata"]["optimal_score"] for s in similar]
                        avg_similar_score = np.mean(similar_scores)
                        # Blend model prediction with historical similarity
                        score = 0.7 * score + 0.3 * avg_similar_score
                
                # Determine recommendation
                if score > 0.7:
                    recommendation = "optimal"
                elif score > 0.4:
                    recommendation = "good"
                else:
                    recommendation = "poor"
                
                predictions.append({
                    "hour": future_hour,
                    "score": float(score),
                    "recommendation": recommendation
                })
            
            # Save best prediction to database
            best_pred = max(predictions, key=lambda x: x["score"])
            pred_record = AIPrediction(
                predicted_hour=best_pred["hour"],
                confidence_score=best_pred["score"],
                recommendation=best_pred["recommendation"],
                timestamp=current_time
            )
            session.add(pred_record)
            await session.commit()
            
            return predictions
    
    def get_index_stats(self):
        """Get statistics about the FAISS index"""
        if self.faiss_index is None:
            return {
                "total_vectors": 0,
                "dimension": 0,
                "index_type": "None"
            }
        
        return {
            "total_vectors": self.faiss_index.ntotal,
            "dimension": self.faiss_index.d,
            "index_type": type(self.faiss_index).__name__,
            "metadata_count": len(self.metadata)
        }


scheduler = ApplianceScheduler()
