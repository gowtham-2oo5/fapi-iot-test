# 📡 API Reference

Complete API documentation for the Solar Appliance Scheduler.

## Base URL

```
http://localhost:8000
```

---

## Sensor Endpoints

### POST /api/sensor/data

Receive sensor data from IoT device.

**Request Body:**
```json
{
  "device_id": "ESP8266_001",
  "ldr_value": 512
}
```

**Response:**
```json
{
  "status": "success",
  "id": 1
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/sensor/data \
  -H "Content-Type: application/json" \
  -d '{"device_id":"ESP8266_001","ldr_value":512}'
```

---

### GET /api/sensor/latest

Get the most recent sensor reading.

**Response:**
```json
{
  "device_id": "ESP8266_001",
  "ldr_value": 512,
  "timestamp": "2024-11-14T19:00:00"
}
```

**Example:**
```bash
curl http://localhost:8000/api/sensor/latest
```

---

## Weather Endpoints

### GET /api/weather/latest

Get current weather data.

**Response:**
```json
{
  "temperature": 15.2,
  "humidity": 72,
  "cloud_cover": 40,
  "weather_main": "Clouds",
  "weather_description": "scattered clouds",
  "timestamp": "2024-11-14T19:00:00"
}
```

**Example:**
```bash
curl http://localhost:8000/api/weather/latest
```

---

## Prediction Endpoints

### GET /api/predictions

Get 24-hour optimal usage predictions.

**Response:**
```json
{
  "predictions": [
    {
      "hour": 0,
      "score": 0.234,
      "recommendation": "poor"
    },
    {
      "hour": 14,
      "score": 0.856,
      "recommendation": "optimal"
    }
  ]
}
```

**Recommendation Levels:**
- `optimal` - Score > 0.7 (best time)
- `good` - Score 0.4-0.7 (acceptable)
- `poor` - Score < 0.4 (avoid)

**Example:**
```bash
curl http://localhost:8000/api/predictions
```

---

## Model Endpoints

### POST /api/model/train

Manually trigger model training.

**Response:**
```json
{
  "status": "success",
  "message": "Model trained successfully",
  "faiss_stats": {
    "total_vectors": 150,
    "dimension": 5,
    "index_type": "IndexFlatL2",
    "metadata_count": 150
  }
}
```

**Error Response:**
```json
{
  "status": "error",
  "message": "Insufficient data for training"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/model/train
```

---

### GET /api/model/stats

Get model and FAISS index statistics.

**Response:**
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

**Example:**
```bash
curl http://localhost:8000/api/model/stats
```

---

## WebSocket

### WS /ws

Real-time bidirectional communication.

**Connection:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = () => {
  console.log('Connected');
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log('Received:', message);
};
```

**Server Messages:**

**Sensor Update:**
```json
{
  "type": "sensor_update",
  "data": {
    "device_id": "ESP8266_001",
    "ldr_value": 512,
    "timestamp": "2024-11-14T19:00:00"
  }
}
```

**Weather Update:**
```json
{
  "type": "weather_update",
  "data": {
    "temperature": 15.2,
    "humidity": 72,
    "cloud_cover": 40,
    "weather_main": "Clouds",
    "weather_description": "scattered clouds",
    "timestamp": "2024-11-14T19:00:00"
  }
}
```

**Client Messages:**

**Ping:**
```json
"ping"
```

**Response:**
```json
{
  "type": "pong"
}
```

---

## Error Responses

All endpoints may return error responses:

**400 Bad Request:**
```json
{
  "detail": "Invalid request format"
}
```

**404 Not Found:**
```json
{
  "detail": "Resource not found"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Internal server error message"
}
```

---

## Rate Limits

No rate limits currently enforced. For production:
- Consider implementing rate limiting
- Use API keys for authentication
- Monitor usage patterns

---

## Data Types

### SensorData
```typescript
{
  device_id: string,
  ldr_value: number  // 0-1024
}
```

### WeatherData
```typescript
{
  temperature: number,      // Celsius
  humidity: number,         // Percentage
  cloud_cover: number,      // Percentage
  weather_main: string,
  weather_description: string,
  timestamp: string         // ISO 8601
}
```

### Prediction
```typescript
{
  hour: number,            // 0-23
  score: number,           // 0-1
  recommendation: string   // "optimal" | "good" | "poor"
}
```

---

## Testing with curl

**Complete workflow:**

```bash
# 1. Send sensor data
curl -X POST http://localhost:8000/api/sensor/data \
  -H "Content-Type: application/json" \
  -d '{"device_id":"TEST_001","ldr_value":750}'

# 2. Check latest reading
curl http://localhost:8000/api/sensor/latest

# 3. Get weather
curl http://localhost:8000/api/weather/latest

# 4. Train model
curl -X POST http://localhost:8000/api/model/train

# 5. Get predictions
curl http://localhost:8000/api/predictions

# 6. Check stats
curl http://localhost:8000/api/model/stats
```

---

## Python Client Example

```python
import httpx
import asyncio

async def main():
    async with httpx.AsyncClient() as client:
        # Send sensor data
        response = await client.post(
            "http://localhost:8000/api/sensor/data",
            json={"device_id": "ESP8266_001", "ldr_value": 512}
        )
        print(response.json())
        
        # Get predictions
        response = await client.get(
            "http://localhost:8000/api/predictions"
        )
        predictions = response.json()
        
        # Find best hour
        best = max(predictions["predictions"], key=lambda x: x["score"])
        print(f"Best hour: {best['hour']}:00 with score {best['score']}")

asyncio.run(main())
```

---

## JavaScript Client Example

```javascript
// Send sensor data
async function sendSensorData(deviceId, ldrValue) {
  const response = await fetch('http://localhost:8000/api/sensor/data', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      device_id: deviceId,
      ldr_value: ldrValue
    })
  });
  return response.json();
}

// Get predictions
async function getPredictions() {
  const response = await fetch('http://localhost:8000/api/predictions');
  const data = await response.json();
  
  // Find optimal hours
  const optimal = data.predictions.filter(p => p.recommendation === 'optimal');
  console.log('Optimal hours:', optimal);
}
```
