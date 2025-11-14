# 🛠️ Setup Guide

Complete installation and configuration guide for the Solar Appliance Scheduler.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Software Installation](#software-installation)
- [Configuration](#configuration)
- [Running the Server](#running-the-server)
- [Testing](#testing)
- [Hardware Setup](#hardware-setup)

---

## Prerequisites

### Required Software

1. **Python 3.8 or higher**
   - Download: https://www.python.org/downloads/
   - Check version: `python --version`

2. **pip** (Python package manager)
   - Usually comes with Python
   - Check: `pip --version`

3. **Git** (optional, for cloning)
   - Download: https://git-scm.com/downloads

4. **OpenWeatherMap API Key** (free)
   - Sign up: https://openweathermap.org/api
   - Free tier: 1000 calls/day

### Optional (for hardware)

- Arduino IDE (for NodeMCU programming)
- USB drivers for NodeMCU ESP8266

---

## Software Installation

### Step 1: Get the Code

**Option A: Clone with Git**
```bash
git clone <repository-url>
cd fapi-iot-test
```

**Option B: Download ZIP**
1. Download ZIP from repository
2. Extract to folder
3. Open terminal in that folder

### Step 2: Create Virtual Environment

A virtual environment keeps project dependencies isolated.

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

You should see `(.venv)` in your terminal prompt.

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `fastapi` - Web framework
- `uvicorn` - Web server
- `scikit-learn` - Machine learning
- `faiss-cpu` - Vector search
- `httpx` - HTTP client
- `sqlalchemy` - Database
- And more...

**Installation takes 2-5 minutes.**

---

## Configuration

### Step 1: Create Environment File

```bash
# Copy the example file
cp .env.example .env
```

**Windows (if cp doesn't work):**
```bash
copy .env.example .env
```

### Step 2: Get OpenWeatherMap API Key

1. Go to https://openweathermap.org/api
2. Click "Sign Up" (free)
3. Verify your email
4. Go to "API keys" section
5. Copy your API key

### Step 3: Edit .env File

Open `.env` in any text editor and update:

```env
# Required: Your OpenWeatherMap API key
OPENWEATHER_API_KEY=paste_your_key_here

# Optional: Your location (for weather data)
OPENWEATHER_CITY=London
OPENWEATHER_LAT=51.5074
OPENWEATHER_LON=-0.1278

# Database (default is fine)
DATABASE_URL=sqlite+aiosqlite:///./iot_data.db
```

**Find your coordinates:**
- Google Maps: Right-click location → Copy coordinates
- Or use: https://www.latlong.net/

---

## Running the Server

### Start the Server

```bash
python start.py
```

**Expected output:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
Database initialized
✓ Model loaded from disk
✓ FAISS index loaded: 0 vectors
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Access the Dashboard

Open your browser and go to:
```
http://localhost:8000
```

You should see the Solar Appliance Scheduler dashboard!

### Stop the Server

Press `Ctrl+C` in the terminal.

---

## Testing

### Test 1: Simulate Sensor Data

Without any hardware, you can simulate a light sensor:

```bash
# Open a NEW terminal window
cd fapi-iot-test
.venv\Scripts\activate  # Activate virtual environment

# Run simulation
python tests/test_sensor.py
```

**Output:**
```
Starting sensor data simulation...
[19:00:00] Sent LDR: 456 - Response: 200
[19:00:05] Sent LDR: 789 - Response: 200
[19:00:10] Sent LDR: 623 - Response: 200
```

**What's happening:**
- Sends fake light sensor readings every 5 seconds
- Dashboard updates in real-time
- Data stored in database

**Let it run for 1-2 minutes** to collect data.

### Test 2: Check Weather & Train Model

```bash
python tests/test_weather.py
```

**Output:**
```
Testing Direct OpenWeatherMap API Call
✓ API Key is valid!
✓ Location: London
✓ Temperature: 15.2°C

Testing Weather API Integration
1. Testing GET /api/weather/latest
   ✓ Temperature: 15.2°C
   ✓ Humidity: 72%

3. Testing GET /api/predictions
   📊 Next 6 Hours:
   🟢 Hour 14:00 → OPTIMAL (score: 0.856)
   🟡 Hour 15:00 → GOOD (score: 0.623)

5. Testing POST /api/model/train
   ✓ Model trained successfully
   ✓ FAISS Index: 20 vectors stored
```

**What's happening:**
- Verifies your API key works
- Fetches real weather data
- Trains the AI model
- Shows predictions

### Test 3: Check Dashboard

Go to http://localhost:8000 and verify:

- ✅ Connection status shows "Connected"
- ✅ Live sensor data updates
- ✅ Weather information displays
- ✅ Charts show data
- ✅ Hourly recommendations appear

---

## Hardware Setup

See [HARDWARE_GUIDE.md](HARDWARE_GUIDE.md) for:
- Circuit diagram
- NodeMCU wiring
- Arduino code
- Upload instructions

**Quick summary:**
1. Connect LDR sensor to NodeMCU
2. Upload Arduino code
3. Configure WiFi credentials
4. Point to your server IP
5. Data flows automatically!

---

## Next Steps

### 1. Customize Location

Edit `.env` to use your location:
```env
OPENWEATHER_CITY=YourCity
OPENWEATHER_LAT=your_latitude
OPENWEATHER_LON=your_longitude
```

### 2. Adjust Update Intervals

Edit `app/config.py`:
```python
weather_fetch_interval: int = 1800  # 30 minutes
model_retrain_threshold: int = 50   # Retrain after 50 readings
```

### 3. Train Model with Real Data

Once you have 10+ sensor readings:
```bash
curl -X POST http://localhost:8000/api/model/train
```

### 4. Check Model Stats

```bash
curl http://localhost:8000/api/model/stats
```

### 5. View Predictions

```bash
curl http://localhost:8000/api/predictions
```

---

## Common Issues

### "Module not found" error

```bash
# Make sure virtual environment is activated
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Mac/Linux

# Reinstall dependencies
pip install -r requirements.txt
```

### "Port 8000 already in use"

**Windows:**
```bash
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Mac/Linux:**
```bash
lsof -ti:8000 | xargs kill -9
```

### "API key not configured"

- Check `.env` file exists
- Verify `OPENWEATHER_API_KEY` is set
- No quotes needed around the key
- Restart server after editing `.env`

### "Insufficient data for training"

- Run `test_sensor.py` for 1-2 minutes
- Need at least 10 sensor readings
- Weather data fetches automatically every 30 min

### Dashboard not updating

- Check browser console (F12) for errors
- Verify WebSocket connection status
- Restart server
- Clear browser cache

---

## Advanced Configuration

### Change Server Port

Edit `start.py`:
```python
uvicorn.run(
    "main:app",
    host="0.0.0.0",
    port=8080,  # Change this
    reload=True
)
```

### Use PostgreSQL Instead of SQLite

Edit `.env`:
```env
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/dbname
```

Install driver:
```bash
pip install asyncpg
```

### Enable Debug Logging

Edit `start.py`:
```python
uvicorn.run(
    "main:app",
    log_level="debug"  # Change from "info"
)
```

---

## Production Deployment

For production use:

1. **Use proper database** (PostgreSQL)
2. **Set secure environment variables**
3. **Use reverse proxy** (nginx)
4. **Enable HTTPS**
5. **Set up monitoring**

See [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) for details.

---

## Getting Help

- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Review [API.md](API.md) for endpoint details
- Open an issue on GitHub
- Check server logs for errors

---

**Setup complete! 🎉**

Your Solar Appliance Scheduler is ready to optimize energy usage!
