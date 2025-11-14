# 🔧 Troubleshooting Guide

Common issues and solutions for the Solar Appliance Scheduler.

---

## Server Issues

### Port Already in Use

**Error:**
```
OSError: [Errno 98] Address already in use
```

**Solution (Windows):**
```bash
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID)
taskkill /PID 12345 /F
```

**Solution (Mac/Linux):**
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

**Alternative:** Change port in `start.py`:
```python
uvicorn.run("main:app", port=8080)
```

---

### Module Not Found

**Error:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution:**
```bash
# Activate virtual environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Mac/Linux

# Reinstall dependencies
pip install -r requirements.txt
```

---

### Import Errors After Restructure

**Error:**
```
ImportError: cannot import name 'scheduler' from 'ml_model'
```

**Solution:**
```bash
# Update imports to use app package
# Should be: from app.ml_model import scheduler
# Not: from ml_model import scheduler

# Restart server
python start.py
```

---

## Weather API Issues

### API Key Not Configured

**Error in logs:**
```
Warning: OpenWeatherMap API key not configured
```

**Solution:**
1. Check `.env` file exists
2. Verify `OPENWEATHER_API_KEY=your_key_here`
3. No quotes around the key
4. Restart server

---

### Invalid API Key

**Error:**
```
401 Unauthorized
```

**Solution:**
1. Get new key from https://openweathermap.org/api
2. Wait 10-15 minutes for activation
3. Update `.env` file
4. Restart server

---

### Weather Data Not Updating

**Issue:** Weather shows old data

**Solution:**
- Weather updates every 30 minutes (default)
- Check server logs for fetch errors
- Verify internet connection
- Test API key manually:
```bash
python tests/test_weather.py
```

---

## Model Training Issues

### Insufficient Data

**Error:**
```
⚠ Insufficient data for training (sensors: 5, weather: 0)
```

**Solution:**
```bash
# Generate sensor data
python tests/test_sensor.py
# Let it run for 1-2 minutes

# Wait for weather data (auto-fetches every 30 min)
# Or manually trigger:
curl http://localhost:8000/api/weather/latest

# Try training again
curl -X POST http://localhost:8000/api/model/train
```

**Requirements:**
- Minimum 10 sensor readings
- Minimum 1 weather data point

---

### No Predictions Available

**Issue:** `/api/predictions` returns empty array

**Solution:**
```bash
# Check if model is trained
curl http://localhost:8000/api/model/stats

# If model_trained is false, train it
curl -X POST http://localhost:8000/api/model/train

# Check predictions again
curl http://localhost:8000/api/predictions
```

---

### FAISS Import Error

**Error:**
```
ModuleNotFoundError: No module named 'faiss'
```

**Solution:**
```bash
# Install FAISS
pip install faiss-cpu

# For GPU support (optional)
pip install faiss-gpu
```

---

## Database Issues

### Database Locked

**Error:**
```
sqlite3.OperationalError: database is locked
```

**Solution:**
```bash
# Stop all server instances
# Delete database and restart
rm iot_data.db
python start.py
```

---

### Corrupted Database

**Error:**
```
sqlite3.DatabaseError: database disk image is malformed
```

**Solution:**
```bash
# Backup if needed
cp iot_data.db iot_data.db.backup

# Delete and recreate
rm iot_data.db
python start.py
```

---

## Hardware Issues

### NodeMCU Not Connecting to WiFi

**Issue:** Serial monitor shows "Connecting..." forever

**Solutions:**
1. **Check WiFi credentials**
   - SSID is case-sensitive
   - Password is correct
   
2. **Use 2.4GHz WiFi**
   - ESP8266 doesn't support 5GHz
   - Check router settings
   
3. **Check signal strength**
   - Move closer to router
   - Reduce obstacles

4. **Reset NodeMCU**
   - Press RST button
   - Re-upload code

---

### HTTP Error -1

**Issue:** NodeMCU shows `HTTP Response: -1`

**Solutions:**
1. **Check server IP**
   ```cpp
   // Use your computer's local IP, not localhost
   const char* serverUrl = "http://192.168.1.100:8000/api/sensor/data";
   ```
   
2. **Find your IP:**
   - Windows: `ipconfig`
   - Mac/Linux: `ifconfig` or `ip addr`
   
3. **Check firewall**
   - Allow port 8000
   - Temporarily disable to test
   
4. **Verify server is running**
   ```bash
   curl http://localhost:8000/api/sensor/latest
   ```

---

### LDR Always Reads 0 or 1024

**Issue:** Sensor values stuck at extremes

**Solutions:**
1. **Check wiring**
   - LDR to A0 and VCC
   - 10kΩ resistor to A0 and GND
   - Verify connections are tight
   
2. **Test LDR**
   - Use multimeter
   - Resistance should change with light
   - Typical: 1kΩ (bright) to 100kΩ (dark)
   
3. **Check resistor value**
   - Should be 10kΩ (brown-black-orange)
   - Try different value if needed

4. **Test with serial monitor**
   ```cpp
   void loop() {
     int ldr = analogRead(A0);
     Serial.println(ldr);
     delay(1000);
   }
   ```

---

## Dashboard Issues

### Dashboard Not Loading

**Issue:** Browser shows "Can't reach this page"

**Solutions:**
1. **Check server is running**
   ```bash
   # Should see "Uvicorn running on..."
   python start.py
   ```
   
2. **Try different browser**
   - Chrome, Firefox, Edge
   
3. **Clear cache**
   - Ctrl+Shift+Delete
   - Clear cached images and files
   
4. **Check URL**
   - Should be `http://localhost:8000`
   - Not `https://`

---

### WebSocket Not Connecting

**Issue:** Connection status shows "Disconnected"

**Solutions:**
1. **Check browser console** (F12)
   - Look for WebSocket errors
   
2. **Verify server supports WebSocket**
   ```bash
   # Should see /ws endpoint
   curl http://localhost:8000/docs
   ```
   
3. **Check firewall**
   - Allow WebSocket connections
   
4. **Try different browser**

---

### Charts Not Displaying

**Issue:** Empty chart areas

**Solutions:**
1. **Check data is available**
   ```bash
   curl http://localhost:8000/api/sensor/latest
   curl http://localhost:8000/api/predictions
   ```
   
2. **Check browser console** (F12)
   - Look for JavaScript errors
   
3. **Verify Chart.js loaded**
   - Check network tab for CDN errors
   
4. **Clear browser cache**

---

### Live Updates Not Working

**Issue:** Dashboard doesn't update automatically

**Solutions:**
1. **Check WebSocket connection**
   - Should show "Connected" in dashboard
   
2. **Send test data**
   ```bash
   python tests/test_sensor.py
   ```
   
3. **Refresh page**
   - Hard refresh: Ctrl+Shift+R
   
4. **Check server logs**
   - Look for WebSocket errors

---

## Performance Issues

### Slow Predictions

**Issue:** `/api/predictions` takes long time

**Solutions:**
1. **Check FAISS index size**
   ```bash
   curl http://localhost:8000/api/model/stats
   ```
   
2. **Reduce data if too large**
   - Archive old data
   - Limit training set size
   
3. **Use faster index type**
   - Edit `app/ml_model.py`
   - Use IndexIVFFlat for large datasets

---

### High Memory Usage

**Issue:** Server uses too much RAM

**Solutions:**
1. **Limit data retention**
   - Delete old sensor readings
   - Keep last 30 days only
   
2. **Reduce FAISS index size**
   - Train with subset of data
   
3. **Use database cleanup**
   ```python
   # Add to database.py
   async def cleanup_old_data(days=30):
       cutoff = datetime.now() - timedelta(days=days)
       # Delete old records
   ```

---

## Testing Issues

### test_sensor.py Fails

**Error:**
```
Connection refused
```

**Solution:**
1. Start server first: `python start.py`
2. Then run test: `python tests/test_sensor.py`

---

### test_weather.py Shows Errors

**Issue:** All tests fail

**Solutions:**
1. **Check server is running**
2. **Verify API key in `.env`**
3. **Check internet connection**
4. **Wait for initial weather fetch** (30 seconds)

---

## Getting More Help

### Enable Debug Logging

Edit `start.py`:
```python
uvicorn.run(
    "main:app",
    log_level="debug"  # More detailed logs
)
```

### Check Server Logs

Look for error messages in terminal where server is running.

### Test Individual Components

```bash
# Test database
python -c "from app.database import init_db; import asyncio; asyncio.run(init_db())"

# Test weather service
python -c "from app.weather_service import fetch_weather_data; import asyncio; asyncio.run(fetch_weather_data())"

# Test model
python -c "from app.ml_model import scheduler; print(scheduler.get_index_stats())"
```

### Still Stuck?

1. Check GitHub issues
2. Review documentation in `docs/`
3. Open new issue with:
   - Error message
   - Steps to reproduce
   - Server logs
   - System info (OS, Python version)

---

**Most issues are solved by:**
1. Restarting the server
2. Checking `.env` configuration
3. Verifying virtual environment is activated
4. Ensuring dependencies are installed
