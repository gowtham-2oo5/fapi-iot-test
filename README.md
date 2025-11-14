# ☀️ Solar Appliance Scheduler

AI-powered IoT systm for optimal appoptimal times to runsed on realiances based on real-time sunlight r data.ty and weather data.

## What Does It Do?

This sTable of Contentsave energy by:
- 📊 Monitoriintensity with a lighr
- 🌦️ Tracking weather )
- [Systeng AI to predict -system-architecturun appliances
- [Hardware Requiremenmmendations on aequirements)

## Quick Start

### 1. Install Pyion](#-api-documentation)
- [Project Structure](#-project-structure)
- [Troubleshooting](#-troubleshooting)
reate virtual envir
--thon -m nv
.venv\Scripts\activa
## ✨urce .venv/biLinux

# Instaleal-time L
pip install -r ather integratio
```

### 2. Chnfigure API Key

```basFAISS vector storage** for fast similarity search
- 🔄 **Automatic moig
cp .env.example .envsign** with Tailwind CSS

---rMap API key
# Ge
## 🏗️ System Architecture

### 3. Start Server

```bash
│   + LDtart.py
```

Open b   ▼000**

### 4. Test Without Hardware

```bash
# Simulate sensor datagration     │  │
│ython tests/test_sear Regression)│  │
│  │  FAISS Vector Storage        │  │
# Test weather &Bro model
python tests/test_────────────────┘  │
└────────┬────────────────────────────┘

## Features

- 🌞 Real-time light sensor data from NodeMCU ESP8
- 🌦️ Live weather integrn (OpenWeatherMap)
- 🤖 AI predictions using Linear Regression + F
``` dashboith live charts
- 🎯 Coecommendations
- - storage for pattern matching
- ta grows

## Document
### Required Components
p Guide](docs/SETUP.md)** - Detaita
- **[Hardware Guide   | Specification DE.md)** - Ne                rogramming
- **[API Ref--------- | ---------* - All endpoints & exa---------------- |
| **[FAISS GESP8266** | AISS_GUIDE.md)    | WiFor storage exrocontroller |
| **[Troubleshooting](docs/TRhotoresiOTING.md)** -es mmon issues & fixes |

## PBreadboarducture  | Standard          | Circuit prototyping          |
| **Jumper Wires**    | Male-to-Male      | Connections                  |
| **USB Cable**       | Micro USB         | Power & programming          |
/                    # 
│   ├── config.py  ngs
│   ├── databasy        # Database 
│   ├── ml_mo     
NodeMCU weather_service.py # W
┌────── websocket_manager.py
├── tem       │   # HTML dashboar
│    tat  A0  ├          ───── VCC (3.3Script
├── tests/           │ # Test scripts
├── docs/                 tion
├── models/   │            # Trained models (gen
├── main.py   ├──┬───┴──────FastAPI aon
│             │           # Server
```

#          oints

| Endpo | Method | Descriptn |
|--------------
**Voltage T | Dashboard UI |
| `/i/sensoreive sens |
| `/api/sn × (R2 / (R1 + R2))
Where: R1 = LDR, R2 = 10kΩT | Current weather |
| `/adictio | GET | 24-hour fo
`/api/model/train` | POST |
| `/apmodel/s
| `/ws` | WS |time updates |
## 💻 Software Setup
Requireme
### What You'll Need
*Software:**
Before starting, make sure you have:
- **Python** (verAPI key (free)

* **A text (Optional):Like Notepad, VS Code, or any code editor
- **deMCU ESPconnection** - To download packages and get weather data
- **OpenWeathersor
- 1r

## Tech 

- **Backe* Fasthemy, scikit-learn, FAISS
-it clone <repository-urvaScript, Chart.js, Tailwind CSS
cd fapi-iot-test
``**Database:** SQLite 

## License

See [lect "E](LICENSE) fi
3. Extract the ZIP file to a folder
4.-

**Made with ☀️ for sustainable energy*

# Solution: Add API key to .env file
OPENWEATHER_API_KEY=your_actual_key_here
```

**Problem:** `401 Unauthorized`
- API key is invalid
- Get new key from openweathermap.org

### Model Training Issues

**Problem:** `Insufficient data for training`
```bash
# Solution: Generate more data
python test_sensor.py  # Run for 1-2 minutes
```

**Problem:** `No predictions available`
```bash
# Solution: Train model manually
curl -X POST http://localhost:8000/api/model/train
```

### Hardware Issues

**Problem:** NodeMCU not connecting to WiFi
- Check SSID and password
- Ensure 2.4GHz WiFi (ESP8266 doesn't support 5GHz)
- Check WiFi signal strength

**Problem:** `HTTP Response: -1`
- Server IP incorrect
- Firewall blocking connection
- Server not running

**Problem:** LDR always reads 0 or 1024
- Check circuit connections
- Verify resistor value (10kΩ)
- Test LDR with multimeter

### Dashboard Issues

**Problem:** Dashboard not updating
- Check WebSocket connection status
- Open browser console for errors
- Verify server is running

**Problem:** Charts not displaying
- Clear browser cache
- Check Chart.js CDN availability
- Verify data is being received

---

## 📚 Additional Resources

- [FAISS Documentation](FAISS_GUIDE.md)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [ESP8266 Arduino Core](https://arduino-esp8266.readthedocs.io/)
- [OpenWeatherMap API](https://openweathermap.org/api)
- [Chart.js Documentation](https://www.chartjs.org/docs/)

---

## 📄 License

See [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Contributions welcome! Please open an issue or submit a pull request.

---

**Made with ☀️ for sustainable energy optimization**n.py`):**
- Receives data from the sensor
- Gets weather information every 30 minutes
- Runs the AI to make predictions
- Sends updates to your browser in real-time

**The Database (`iot_data.db`):**
- Stores all sensor readings
- Stores weather data
- Stores AI predictions
- Like a digital notebook that remembers everything

**The AI Model (`models/` folder):**
- Learns patterns from your data
- Predicts best times to use appliances
- Gets smarter as it collects more data
- Uses FAISS to remember similar situations

**The Dashboard (`templates/index.html`):**
- Shows everything in a nice visual way
- Updates automatically without refreshing
- Displays charts and recommendations
- Works on phone, tablet, or computer