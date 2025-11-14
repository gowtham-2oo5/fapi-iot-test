"""
Test script to verify weather API integration
"""
import httpx
import asyncio
from datetime import datetime


async def test_weather_endpoints():
    """Test all weather-related endpoints"""
    base_url = "http://localhost:8000"
    
    print("=" * 60)
    print("Testing Weather API Integration")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        # Test 1: Get latest weather data
        print("\n1. Testing GET /api/weather/latest")
        try:
            response = await client.get(f"{base_url}/api/weather/latest", timeout=10.0)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                if data:
                    print(f"   ✓ Temperature: {data['temperature']}°C")
                    print(f"   ✓ Humidity: {data['humidity']}%")
                    print(f"   ✓ Cloud Cover: {data['cloud_cover']}%")
                    print(f"   ✓ Condition: {data['weather_description']}")
                    print(f"   ✓ Timestamp: {data['timestamp']}")
                else:
                    print("   ⚠ No weather data available yet")
            else:
                print(f"   ✗ Error: {response.text}")
        except Exception as e:
            print(f"   ✗ Error: {e}")
        
        # Test 2: Get latest sensor data
        print("\n2. Testing GET /api/sensor/latest")
        try:
            response = await client.get(f"{base_url}/api/sensor/latest", timeout=10.0)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                if data:
                    print(f"   ✓ Device ID: {data['device_id']}")
                    print(f"   ✓ LDR Value: {data['ldr_value']}")
                    print(f"   ✓ Timestamp: {data['timestamp']}")
                else:
                    print("   ⚠ No sensor data available yet")
            else:
                print(f"   ✗ Error: {response.text}")
        except Exception as e:
            print(f"   ✗ Error: {e}")
        
        # Test 3: Get predictions
        print("\n3. Testing GET /api/predictions")
        try:
            response = await client.get(f"{base_url}/api/predictions", timeout=10.0)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                predictions = data.get('predictions', [])
                if predictions:
                    print(f"   ✓ Got {len(predictions)} hourly predictions")
                    print(f"\n   📊 Next 6 Hours:")
                    for pred in predictions[:6]:
                        emoji = "🟢" if pred['recommendation'] == 'optimal' else "🟡" if pred['recommendation'] == 'good' else "🔴"
                        print(f"   {emoji} Hour {pred['hour']:02d}:00 → {pred['recommendation'].upper():8s} (score: {pred['score']:.3f})")
                    
                    # Show best hour
                    best = max(predictions, key=lambda x: x['score'])
                    print(f"\n   ⭐ Best Hour: {best['hour']:02d}:00 with score {best['score']:.3f}")
                else:
                    print("   ⚠ No predictions available (model may not be trained yet)")
                    print("   💡 Run: curl -X POST http://localhost:8000/api/model/train")
            else:
                print(f"   ✗ Error: {response.text}")
        except Exception as e:
            print(f"   ✗ Error: {e}")
        
        # Test 4: Check model stats
        print("\n4. Testing GET /api/model/stats")
        try:
            response = await client.get(f"{base_url}/api/model/stats", timeout=10.0)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Model Trained: {data['model_trained']}")
                print(f"   Scaler Ready: {data['scaler_ready']}")
                print(f"   FAISS Vectors: {data['faiss_index']['total_vectors']}")
                print(f"   Vector Dimension: {data['faiss_index']['dimension']}")
            else:
                print(f"   ✗ Error: {response.text}")
        except Exception as e:
            print(f"   ✗ Error: {e}")
        
        # Test 5: Manually trigger model training
        print("\n5. Testing POST /api/model/train")
        try:
            response = await client.post(f"{base_url}/api/model/train", timeout=30.0)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✓ {data['message']}")
                if 'faiss_stats' in data:
                    print(f"   ✓ FAISS Index: {data['faiss_stats']['total_vectors']} vectors stored")
            else:
                print(f"   ✗ Error: {response.text}")
        except Exception as e:
            print(f"   ✗ Error: {e}")
    
    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)
    print("\nTips:")
    print("- If weather data is null, check your .env file for OPENWEATHER_API_KEY")
    print("- If predictions fail, you need at least 10 sensor readings and 5 weather records")
    print("- Run test_sensor.py to generate sensor data")
    print("- Check server logs for detailed error messages")


async def test_direct_weather_fetch():
    """Test direct OpenWeatherMap API call"""
    print("\n" + "=" * 60)
    print("Testing Direct OpenWeatherMap API Call")
    print("=" * 60)
    
    # Read API key from .env
    try:
        with open('.env', 'r') as f:
            for line in f:
                if line.startswith('OPENWEATHER_API_KEY='):
                    api_key = line.split('=')[1].strip()
                    break
        
        if not api_key or api_key == "your_api_key_here":
            print("✗ API key not configured in .env file")
            return
        
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "lat": 51.5074,
            "lon": -0.1278,
            "appid": api_key,
            "units": "metric"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=10.0)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ API Key is valid!")
                print(f"✓ Location: {data['name']}")
                print(f"✓ Temperature: {data['main']['temp']}°C")
                print(f"✓ Weather: {data['weather'][0]['description']}")
            elif response.status_code == 401:
                print("✗ Invalid API key")
            else:
                print(f"✗ Error: {response.text}")
                
    except FileNotFoundError:
        print("✗ .env file not found")
    except Exception as e:
        print(f"✗ Error: {e}")


if __name__ == "__main__":
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Starting weather tests...")
    print("Make sure the FastAPI server is running on http://localhost:8000\n")
    
    asyncio.run(test_direct_weather_fetch())
    asyncio.run(test_weather_endpoints())
