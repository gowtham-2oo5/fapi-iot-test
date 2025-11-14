# FAISS Vector Storage Guide

## Overview

The ML model now uses FAISS (Facebook AI Similarity Search) to store and retrieve historical training data as vectors. This enables:

- **Fast similarity search** - Find similar historical patterns in milliseconds
- **Persistent storage** - Training data saved to disk in vector format
- **Enhanced predictions** - Blend model predictions with similar historical data
- **Scalable** - Efficiently handle growing datasets

## File Structure

```
models/
├── trained_model.pkl       # Scikit-learn Linear Regression model
├── scaler.pkl             # StandardScaler for feature normalization
├── faiss_index.bin        # FAISS vector index (binary format)
├── faiss_metadata.json    # Metadata for each vector (timestamps, values, etc.)
└── training_vectors.npy   # Raw training vectors (NumPy format)
```

## How It Works

### 1. Training Phase
When you train the model:
- Sensor + Weather data → Feature vectors (5D: LDR, temp, humidity, cloud, hour)
- Vectors are normalized using StandardScaler
- Stored in FAISS index with metadata
- Model learns patterns from these vectors

### 2. Prediction Phase
When making predictions:
- Current conditions → Query vector
- FAISS finds 5 most similar historical patterns
- Prediction = 70% model + 30% similar historical scores
- More accurate predictions based on past similar conditions

## API Endpoints

### Check Model Status
```bash
curl http://localhost:8000/api/model/stats
```

Response:
```json
{
  "model_trained": true,
  "scaler_ready": true,
  "faiss_index": {
    "total_vectors": 150,
    "dimension": 5,
    "index_type": "IndexFlatL2",
    "metadata_count": 150
  }
}
```

### Train Model
```bash
curl -X POST http://localhost:8000/api/model/train
```

Response:
```json
{
  "status": "success",
  "message": "Model trained with 150 samples",
  "faiss_stats": {
    "total_vectors": 150,
    "dimension": 5
  }
}
```

## Installation

Install FAISS:
```bash
pip install faiss-cpu
```

Or for GPU support:
```bash
pip install faiss-gpu
```

## Testing

1. Generate sensor data:
```bash
python test_sensor.py
```

2. Wait for weather data to be fetched (automatic every 30 min)

3. Train the model:
```bash
python test_weather.py
```

4. Check FAISS stats in the output

## Benefits

- **Memory Efficient**: Vectors stored in optimized binary format
- **Fast Retrieval**: L2 distance search in O(n) time
- **Persistent**: Data survives server restarts
- **Scalable**: Can handle millions of vectors
- **Contextual**: Predictions consider similar historical patterns

## Vector Format

Each vector contains 5 features (normalized):
1. LDR Value (0-1024 → normalized)
2. Temperature (°C → normalized)
3. Humidity (% → normalized)
4. Cloud Cover (% → normalized)
5. Hour of Day (0-23 → normalized)

Metadata includes:
- Timestamp
- Device ID
- Raw sensor values
- Weather conditions
- Optimal score

## Future Enhancements

- Use IndexIVFFlat for faster search on large datasets
- Add time-weighted similarity (recent patterns matter more)
- Implement incremental training (add new vectors without full retrain)
- Add vector visualization dashboard
