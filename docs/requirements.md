# Software Requirements
## Functional Requirements

reReal-time data reception from NodeMCU ESP8266 microcontroller transmitting sunlight intensity sensed by an LDR sensor.

Periodic retrieval of live weather data from OpenWeatherMap API for enhanced prediction accuracy.

Processing and storing combined sunlight and weather data in the FastAPI server backend.

AI-driven scheduling algorithm implemented using Python machine learning libraries, specifically a Linear Regression model using scikit-learn, to predict optimal appliance usage times.

Continuous retraining and updating of the AI model as new data arrives, improving prediction over time.

Real-time web dashboard functionalities using FastAPI with WebSockets for live update delivery.

Visualization on the dashboard through HTML and Chart.js showing live sensor data, weather information, and AI-based appliance usage recommendations with color-coded indicators.

Non-Functional Requirements
FastAPI server must support asynchronous processing to handle real-time data efficiently.

WebSocket implementation should ensure low latency communication between server and dashboard.

Scalability to handle increasing data volume and expanding users or devices.

Secure communication protocols for IoT device data transmission (e.g., HTTPS/WSS).

Cross-browser compatibility and responsiveness for the web dashboard.

Reliability in retrieving and integrating external weather data (OpenWeatherMap API).

Maintainability and modular design of the AI algorithm and web server components.