# 🔌 Hardware Setup Guide

Complete guide for building and configuring the NodeMCU ESP8266 + LDR sensor module.

---

## 📦 Bill of Materials (BOM)

| Item | Quantity | Specification | Approx. Cost | Purchase Link |
|------|----------|---------------|--------------|---------------|
| NodeMCU ESP8266 | 1 | ESP-12E Module | $3-5 | Amazon, AliExpress |
| LDR Sensor | 1 | 5mm Photoresistor, GL5528 | $0.50 | Electronics store |
| Resistor | 1 | 10kΩ, 1/4W | $0.10 | Electronics store |
| Breadboard | 1 | 400 or 830 points | $2-3 | Amazon |
| Jumper Wires | 3 | Male-to-Male | $0.50 | Electronics store |
| USB Cable | 1 | Micro USB | $2 | Amazon |

**Total Cost: ~$8-12**

---

## 🔧 Circuit Assembly

### Step-by-Step Instructions

#### 1. Understand the Components

**NodeMCU ESP8266:**
- WiFi-enabled microcontroller
- 10-bit ADC (Analog-to-Digital Converter) on pin A0
- Reads voltage: 0V = 0, 3.3V = 1024

**LDR (Light Dependent Resistor):**
- Resistance decreases with light intensity
- Dark: ~1MΩ
- Bright: ~1kΩ

**10kΩ Resistor:**
- Forms voltage divider with LDR
- Provides stable reference

#### 2. Build the Circuit

```
Circuit Schematic:

        3.3V (VCC)
           │
           │
        ┌──┴──┐
        │ LDR │  (Photoresistor)
        └──┬──┘
           │
           ├────────── A0 (Analog Input)
           │
        ┌──┴──┐
        │10kΩ│  (Resistor)
        └──┬──┘
           │
          GND
```

**Physical Connections:**

1. **LDR Top Leg** → **3.3V pin** on NodeMCU
2. **LDR Bottom Leg** → **Junction Point** (breadboard row)
3. **Junction Point** → **A0 pin** on NodeMCU
4. **10kΩ Resistor** → Between **Junction Point** and **GND**
5. **GND pin** → **Breadboard ground rail**

#### 3. Breadboard Layout

```
NodeMCU Pinout (Top View):
┌─────────────────────────┐
│  RST          D0    D1  │
│  A0           D2    D3  │
│  GND          D4    3V3 │
│  ...          ...   ... │
└─────────────────────────┘

Breadboard Layout:
Row 1:  3.3V ──────── LDR (Leg 1)
Row 2:  LDR (Leg 2) ── Junction ── A0
Row 3:  Junction ──── 10kΩ ──── GND
```

#### 4. Verify Connections

**Checklist:**
- [ ] LDR connected to 3.3V
- [ ] LDR connected to A0 through junction
- [ ] 10kΩ resistor between junction and GND
- [ ] No short circuits
- [ ] All connections secure

---

## 🧮 Understanding the Voltage Divider

### Theory

The LDR and resistor form a voltage divider:

```
Vout = Vin × (R2 / (R1 + R2))

Where:
- Vin = 3.3V (supply voltage)
- R1 = LDR resistance (varies with light)
- R2 = 10kΩ (fixed resistor)
- Vout = Voltage at A0 pin
```

### Example Calculations

**Bright Light (LDR = 1kΩ):**
```
Vout = 3.3V × (10kΩ / (1kΩ + 10kΩ))
     = 3.3V × 0.909
     = 3.0V
ADC Reading = (3.0 / 3.3) × 1024 = 930
```

**Dark (LDR = 100kΩ):**
```
Vout = 3.3V × (10kΩ / (100kΩ + 10kΩ))
     = 3.3V × 0.091
     = 0.3V
ADC Reading = (0.3 / 3.3) × 1024 = 93
```

**Result:** Higher light = Higher ADC value

---

## 💻 Software Setup

### Arduino IDE Configuration

#### 1. Install Arduino IDE

Download from: https://www.arduino.cc/en/software

**Supported Versions:** 1.8.x or 2.x

#### 2. Add ESP8266 Board Support

**Method 1: Preferences**
1. Open Arduino IDE
2. **File → Preferences**
3. In "Additional Board Manager URLs", add:
   ```
   http://arduino.esp8266.com/stable/package_esp8266com_index.json
   ```
4. Click **OK**

**Method 2: Manual**
1. **Tools → Board → Boards Manager**
2. Search: "esp8266"
3. Install: "esp8266 by ESP8266 Community"
4. Wait for installation to complete

#### 3. Select Board

1. **Tools → Board → ESP8266 Boards**
2. Select: **NodeMCU 1.0 (ESP-12E Module)**

#### 4. Configure Board Settings

```
Board: "NodeMCU 1.0 (ESP-12E Module)"
Upload Speed: "115200"
CPU Frequency: "80 MHz"
Flash Size: "4MB (FS:2MB OTA:~1019KB)"
Port: [Select your COM port]
```

---

## 📝 Arduino Code

### Complete Sketch

```cpp
/*
 * Solar Appliance Scheduler - NodeMCU Client
 * 
 * Reads LDR sensor and sends data to FastAPI server
 * 
 * Hardware:
 * - NodeMCU ESP8266
 * - LDR connected to A0 via voltage divider
 * - 10kΩ resistor to GND
 */

#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>

// ============ CONFIGURATION ============

// WiFi Credentials
const char* WIFI_SSID = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";

// Server Configuration
const char* SERVER_URL = "http://192.168.1.100:8000/api/sensor/data";
const char* DEVICE_ID = "ESP8266_001";

// Sensor Configuration
const int LDR_PIN = A0;              // Analog pin for LDR
const int SEND_INTERVAL = 5000;      // Send data every 5 seconds (ms)
const int WIFI_TIMEOUT = 20000;      // WiFi connection timeout (ms)

// ============ GLOBAL VARIABLES ============

unsigned long lastSendTime = 0;
int consecutiveErrors = 0;
const int MAX_ERRORS = 5;

// ============ SETUP ============

void setup() {
  // Initialize Serial
  Serial.begin(115200);
  delay(100);
  Serial.println("\n\n=================================");
  Serial.println("Solar Appliance Scheduler Client");
  Serial.println("=================================\n");
  
  // Connect to WiFi
  connectWiFi();
  
  // Print configuration
  Serial.println("Configuration:");
  Serial.print("  Device ID: ");
  Serial.println(DEVICE_ID);
  Serial.print("  Server URL: ");
  Serial.println(SERVER_URL);
  Serial.print("  Send Interval: ");
  Serial.print(SEND_INTERVAL / 1000);
  Serial.println(" seconds\n");
}

// ============ MAIN LOOP ============

void loop() {
  unsigned long currentTime = millis();
  
  // Check WiFi connection
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi disconnected! Reconnecting...");
    connectWiFi();
  }
  
  // Send data at specified interval
  if (currentTime - lastSendTime >= SEND_INTERVAL) {
    lastSendTime = currentTime;
    
    // Read sensor
    int ldrValue = readLDR();
    
    // Send to server
    bool success = sendSensorData(ldrValue);
    
    // Handle errors
    if (success) {
      consecutiveErrors = 0;
    } else {
      consecutiveErrors++;
      if (consecutiveErrors >= MAX_ERRORS) {
        Serial.println("Too many errors! Restarting...");
        delay(1000);
        ESP.restart();
      }
    }
  }
  
  delay(100);  // Small delay to prevent watchdog issues
}

// ============ FUNCTIONS ============

void connectWiFi() {
  Serial.print("Connecting to WiFi: ");
  Serial.println(WIFI_SSID);
  
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  
  unsigned long startTime = millis();
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    
    // Timeout check
    if (millis() - startTime > WIFI_TIMEOUT) {
      Serial.println("\nWiFi connection timeout!");
      Serial.println("Restarting...");
      delay(1000);
      ESP.restart();
    }
  }
  
  Serial.println("\n✓ WiFi connected!");
  Serial.print("  IP Address: ");
  Serial.println(WiFi.localIP());
  Serial.print("  Signal Strength: ");
  Serial.print(WiFi.RSSI());
  Serial.println(" dBm\n");
}

int readLDR() {
  // Read analog value (0-1024)
  int rawValue = analogRead(LDR_PIN);
  
  // Optional: Average multiple readings for stability
  int sum = rawValue;
  for (int i = 1; i < 5; i++) {
    delay(10);
    sum += analogRead(LDR_PIN);
  }
  int avgValue = sum / 5;
  
  return avgValue;
}

bool sendSensorData(int ldrValue) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("✗ WiFi not connected");
    return false;
  }
  
  WiFiClient client;
  HTTPClient http;
  
  // Begin HTTP connection
  http.begin(client, SERVER_URL);
  http.addHeader("Content-Type", "application/json");
  http.setTimeout(5000);  // 5 second timeout
  
  // Create JSON payload
  String payload = "{\"device_id\":\"" + String(DEVICE_ID) + 
                   "\",\"ldr_value\":" + String(ldrValue) + "}";
  
  // Send POST request
  int httpCode = http.POST(payload);
  
  // Handle response
  bool success = false;
  
  if (httpCode > 0) {
    Serial.print("[");
    Serial.print(getTimestamp());
    Serial.print("] LDR: ");
    Serial.print(ldrValue);
    Serial.print(" → HTTP ");
    Serial.print(httpCode);
    
    if (httpCode == 200) {
      Serial.println(" ✓");
      success = true;
    } else {
      Serial.print(" ✗ Error: ");
      Serial.println(http.getString());
    }
  } else {
    Serial.print("✗ Connection failed: ");
    Serial.println(http.errorToString(httpCode));
  }
  
  http.end();
  return success;
}

String getTimestamp() {
  unsigned long seconds = millis() / 1000;
  unsigned long minutes = seconds / 60;
  unsigned long hours = minutes / 60;
  
  seconds = seconds % 60;
  minutes = minutes % 60;
  hours = hours % 24;
  
  char buffer[9];
  sprintf(buffer, "%02lu:%02lu:%02lu", hours, minutes, seconds);
  return String(buffer);
}
```

### Code Explanation

**Key Features:**
- ✅ Automatic WiFi reconnection
- ✅ Error handling with retry logic
- ✅ Averaged sensor readings for stability
- ✅ Watchdog timer protection
- ✅ Detailed serial logging
- ✅ Automatic restart on persistent errors

---

## 🔍 Testing & Calibration

### 1. Upload Code

1. Connect NodeMCU via USB
2. Select correct **Port** in Arduino IDE
3. Click **Upload** button
4. Wait for "Done uploading" message

### 2. Open Serial Monitor

1. **Tools → Serial Monitor**
2. Set baud rate to **115200**
3. Observe output

**Expected Output:**
```
=================================
Solar Appliance Scheduler Client
=================================

Connecting to WiFi: MyNetwork
.....
✓ WiFi connected!
  IP Address: 192.168.1.150
  Signal Strength: -45 dBm

Configuration:
  Device ID: ESP8266_001
  Server URL: http://192.168.1.100:8000/api/sensor/data
  Send Interval: 5 seconds

[00:00:05] LDR: 512 → HTTP 200 ✓
[00:00:10] LDR: 487 → HTTP 200 ✓
```

### 3. Calibrate Sensor

**Test Different Light Conditions:**

| Condition | Expected Range | Action |
|-----------|----------------|--------|
| Complete darkness | 0-100 | Cover sensor completely |
| Indoor lighting | 200-500 | Normal room light |
| Bright indoor | 500-700 | Near window |
| Direct sunlight | 800-1024 | Outdoor or direct sun |

**Calibration Steps:**
1. Cover LDR completely → Note minimum value
2. Shine flashlight directly → Note maximum value
3. Adjust thresholds in server if needed

### 4. Verify Server Reception

Check server logs for incoming data:
```
INFO: Sensor data received: device_id=ESP8266_001, ldr_value=512
```

Or check dashboard at `http://localhost:8000`

---

## 🐛 Troubleshooting

### WiFi Issues

**Problem:** Can't connect to WiFi
```
Solutions:
1. Verify SSID and password (case-sensitive)
2. Ensure 2.4GHz network (ESP8266 doesn't support 5GHz)
3. Check WiFi signal strength
4. Disable MAC filtering on router
5. Try different WiFi channel
```

**Problem:** Frequent disconnections
```
Solutions:
1. Move closer to router
2. Check power supply (use quality USB cable)
3. Add WiFi.setAutoReconnect(true) in setup()
4. Reduce send interval to lower power consumption
```

### Sensor Issues

**Problem:** LDR always reads 0
```
Solutions:
1. Check if LDR is connected to 3.3V (not GND)
2. Verify resistor is 10kΩ (not 10Ω or 100kΩ)
3. Test LDR with multimeter (resistance should change with light)
4. Check for loose connections
```

**Problem:** LDR always reads 1024
```
Solutions:
1. Check if resistor is connected to GND
2. Verify junction point connects LDR, resistor, and A0
3. Test with different resistor value (try 4.7kΩ or 22kΩ)
```

**Problem:** Erratic readings
```
Solutions:
1. Add 0.1µF capacitor between A0 and GND (noise filtering)
2. Increase averaging samples in code
3. Shield sensor from electromagnetic interference
4. Use shielded cable for long connections
```

### Upload Issues

**Problem:** "espcomm_open failed"
```
Solutions:
1. Check USB cable (must support data, not just power)
2. Install CH340 or CP2102 drivers
3. Try different USB port
4. Press FLASH button while uploading
5. Reduce upload speed to 57600
```

**Problem:** "Board not found"
```
Solutions:
1. Reinstall ESP8266 board package
2. Restart Arduino IDE
3. Check Device Manager for COM port
4. Try different USB cable
```

### Server Communication Issues

**Problem:** HTTP -1 error
```
Solutions:
1. Verify server IP address (use ipconfig/ifconfig)
2. Ensure server is running (python start.py)
3. Check firewall settings
4. Test with curl from same network
5. Use server's local IP, not localhost
```

**Problem:** HTTP 404 error
```
Solutions:
1. Verify endpoint URL: /api/sensor/data
2. Check server logs for errors
3. Ensure FastAPI server started successfully
```

---

## 🔋 Power Considerations

### Power Consumption

| Mode | Current Draw | Notes |
|------|--------------|-------|
| Active (WiFi TX) | 170-260 mA | During data transmission |
| Active (WiFi RX) | 50-70 mA | Idle with WiFi connected |
| Light Sleep | 0.5-15 mA | WiFi off, quick wake |
| Deep Sleep | 20 µA | Requires hardware modification |

### Power Supply Options

**1. USB Power (Recommended for Development)**
- Stable 5V supply
- Easy debugging via serial
- No battery management needed

**2. Battery Power**
- Use 3.7V LiPo battery with voltage regulator
- Add TP4056 charging module
- Implement deep sleep for longer runtime

**3. Solar Power**
- 5V solar panel (>500mA)
- Battery backup for night operation
- Charge controller required

---

## 📊 Advanced Features

### 1. Add Temperature Sensor

```cpp
#include <DHT.h>

#define DHT_PIN D4
#define DHT_TYPE DHT22

DHT dht(DHT_PIN, DHT_TYPE);

void setup() {
  dht.begin();
}

void loop() {
  float temp = dht.readTemperature();
  float humidity = dht.readHumidity();
  
  // Add to JSON payload
  String payload = "{\"device_id\":\"" + String(DEVICE_ID) + 
                   "\",\"ldr_value\":" + String(ldrValue) +
                   ",\"temperature\":" + String(temp) +
                   ",\"humidity\":" + String(humidity) + "}";
}
```

### 2. Add OLED Display

```cpp
#include <Wire.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

void setup() {
  display.begin(SSD1306_SWITCHCAPVCC, 0x3C);
  display.clearDisplay();
}

void displayData(int ldrValue) {
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(WHITE);
  display.setCursor(0, 0);
  display.println("Solar Scheduler");
  display.println();
  display.print("LDR: ");
  display.println(ldrValue);
  display.display();
}
```

### 3. OTA (Over-The-Air) Updates

```cpp
#include <ArduinoOTA.h>

void setup() {
  ArduinoOTA.setHostname("solar-sensor");
  ArduinoOTA.setPassword("admin");
  
  ArduinoOTA.onStart([]() {
    Serial.println("OTA Update Starting...");
  });
  
  ArduinoOTA.begin();
}

void loop() {
  ArduinoOTA.handle();
  // ... rest of code
}
```

---

## 📚 Additional Resources

- [ESP8266 Arduino Core Documentation](https://arduino-esp8266.readthedocs.io/)
- [NodeMCU Pinout Reference](https://randomnerdtutorials.com/esp8266-pinout-reference-gpios/)
- [LDR Sensor Guide](https://www.electronics-tutorials.ws/io/io_4.html)
- [Voltage Divider Calculator](https://ohmslawcalculator.com/voltage-divider-calculator)

---

**Happy Building! 🔧⚡**
