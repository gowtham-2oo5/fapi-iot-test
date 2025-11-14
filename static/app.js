let ws = null;
let sunlightChart = null;
let predictionChart = null;
let sensorHistory = [];

// WebSocket Connection
function connectWebSocket() {
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  ws = new WebSocket(`${protocol}//${window.location.host}/ws`);

  ws.onopen = () => {
    updateConnectionStatus(true);
    console.log("WebSocket connected");
  };

  ws.onmessage = (event) => {
    const message = JSON.parse(event.data);
    handleWebSocketMessage(message);
  };

  ws.onclose = () => {
    updateConnectionStatus(false);
    console.log("WebSocket disconnected, reconnecting...");
    setTimeout(connectWebSocket, 3000);
  };

  ws.onerror = (error) => {
    console.error("WebSocket error:", error);
  };
}

function updateConnectionStatus(connected) {
  const statusEl = document.getElementById("connection-status");
  if (connected) {
    statusEl.innerHTML =
      '<span class="inline-block w-2 h-2 rounded-full bg-green-500 mr-2"></span><span>Connected</span>';
  } else {
    statusEl.innerHTML =
      '<span class="inline-block w-2 h-2 rounded-full bg-red-500 mr-2"></span><span>Disconnected</span>';
  }
}

function handleWebSocketMessage(message) {
  if (message.type === "sensor_update") {
    updateSensorData(message.data);
  } else if (message.type === "weather_update") {
    displayWeatherData(message.data);
  }
}

// Update Sensor Data Display
function updateSensorData(data) {
  const container = document.getElementById("sensor-data");
  const intensity = ((data.ldr_value / 1024) * 100).toFixed(1);

  container.innerHTML = `
    <div class="space-y-3">
      <div>
        <div class="text-sm text-slate-600">Device ID</div>
        <div class="text-lg font-semibold">${data.device_id}</div>
      </div>
      <div>
        <div class="text-sm text-slate-600">LDR Value</div>
        <div class="text-3xl font-bold text-blue-600">${data.ldr_value}</div>
      </div>
      <div>
        <div class="text-sm text-slate-600">Intensity</div>
        <div class="text-2xl font-semibold">${intensity}%</div>
      </div>
      <div class="text-xs text-slate-400">
        Last update: ${new Date(data.timestamp).toLocaleTimeString()}
      </div>
    </div>
  `;

  // Add to history for chart
  sensorHistory.push({
    time: new Date(data.timestamp),
    value: data.ldr_value,
  });

  // Keep last 20 readings
  if (sensorHistory.length > 20) {
    sensorHistory.shift();
  }

  updateSunlightChart();
}

// Display Weather Data
function displayWeatherData(weather) {
  if (!weather) {
    document.getElementById("weather-data").innerHTML =
      '<div class="text-slate-400">No data available</div>';
    return;
  }

  const container = document.getElementById("weather-data");
  container.innerHTML = `
    <div class="space-y-3">
      <div>
        <div class="text-sm text-slate-600">Condition</div>
        <div class="text-lg font-semibold capitalize">${weather.weather_description}</div>
      </div>
      <div>
        <div class="text-sm text-slate-600">Temperature</div>
        <div class="text-3xl font-bold text-orange-600">${weather.temperature}°C</div>
      </div>
      <div class="grid grid-cols-2 gap-2">
        <div>
          <div class="text-xs text-slate-600">Humidity</div>
          <div class="text-lg font-semibold">${weather.humidity}%</div>
        </div>
        <div>
          <div class="text-xs text-slate-600">Cloud Cover</div>
          <div class="text-lg font-semibold">${weather.cloud_cover}%</div>
        </div>
      </div>
    </div>
  `;
}

// Update Weather Data
async function loadWeatherData() {
  try {
    const res = await fetch("/api/weather/latest");
    const weather = await res.json();
    displayWeatherData(weather);
  } catch (error) {
    console.error("Error loading weather:", error);
  }
}

// Load Predictions
async function loadPredictions() {
  try {
    const res = await fetch("/api/predictions");
    const data = await res.json();

    if (!data.predictions || data.predictions.length === 0) {
      return;
    }

    updatePredictionChart(data.predictions);
    updateHourlyRecommendations(data.predictions);
    updateCurrentRecommendation(data.predictions);
  } catch (error) {
    console.error("Error loading predictions:", error);
  }
}

// Update Current Recommendation
function updateCurrentRecommendation(predictions) {
  const currentHour = new Date().getHours();
  const current =
    predictions.find((p) => p.hour === currentHour) || predictions[0];

  const colors = {
    optimal: {
      bg: "bg-green-100",
      text: "text-green-800",
      border: "border-green-500",
    },
    good: {
      bg: "bg-yellow-100",
      text: "text-yellow-800",
      border: "border-yellow-500",
    },
    poor: { bg: "bg-red-100", text: "text-red-800", border: "border-red-500" },
  };

  const color = colors[current.recommendation] || colors.poor;

  const container = document.getElementById("current-recommendation");
  container.innerHTML = `
    <div class="text-center space-y-4">
      <div class="${color.bg} ${color.text} px-6 py-3 rounded-lg border-2 ${
    color.border
  }">
        <div class="text-sm font-medium">Current Status</div>
        <div class="text-3xl font-bold uppercase mt-2">${
          current.recommendation
        }</div>
      </div>
      <div>
        <div class="text-sm text-slate-600">Confidence Score</div>
        <div class="text-2xl font-bold">${(current.score * 100).toFixed(
          1
        )}%</div>
      </div>
      <div class="text-xs text-slate-500">
        Hour: ${current.hour}:00
      </div>
    </div>
  `;
}

// Update Hourly Recommendations
function updateHourlyRecommendations(predictions) {
  const container = document.getElementById("hourly-recommendations");

  const colors = {
    optimal: "bg-green-500",
    good: "bg-yellow-500",
    poor: "bg-red-500",
  };

  container.innerHTML = predictions
    .map(
      (p) => `
    <div class="text-center p-2 rounded ${colors[p.recommendation]} text-white">
      <div class="text-xs font-semibold">${p.hour}:00</div>
      <div class="text-xs mt-1">${(p.score * 100).toFixed(0)}%</div>
    </div>
  `
    )
    .join("");
}

// Initialize Sunlight Chart
function initSunlightChart() {
  const ctx = document.getElementById("sunlightChart").getContext("2d");
  sunlightChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: [],
      datasets: [
        {
          label: "LDR Value",
          data: [],
          borderColor: "rgb(59, 130, 246)",
          backgroundColor: "rgba(59, 130, 246, 0.1)",
          tension: 0.4,
          fill: true,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      scales: {
        y: {
          beginAtZero: true,
          max: 1024,
        },
      },
      plugins: {
        legend: {
          display: false,
        },
      },
    },
  });
}

// Update Sunlight Chart
function updateSunlightChart() {
  if (!sunlightChart) return;

  sunlightChart.data.labels = sensorHistory.map((h) =>
    h.time.toLocaleTimeString()
  );
  sunlightChart.data.datasets[0].data = sensorHistory.map((h) => h.value);
  sunlightChart.update();
}

// Initialize Prediction Chart
function initPredictionChart() {
  const ctx = document.getElementById("predictionChart").getContext("2d");
  predictionChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: [],
      datasets: [
        {
          label: "Optimal Usage Score",
          data: [],
          backgroundColor: [],
          borderWidth: 0,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      scales: {
        y: {
          beginAtZero: true,
          max: 1,
        },
      },
      plugins: {
        legend: {
          display: false,
        },
      },
    },
  });
}

// Update Prediction Chart
function updatePredictionChart(predictions) {
  if (!predictionChart) return;

  const colors = predictions.map((p) => {
    if (p.recommendation === "optimal") return "rgba(34, 197, 94, 0.8)";
    if (p.recommendation === "good") return "rgba(234, 179, 8, 0.8)";
    return "rgba(239, 68, 68, 0.8)";
  });

  predictionChart.data.labels = predictions.map((p) => `${p.hour}:00`);
  predictionChart.data.datasets[0].data = predictions.map((p) => p.score);
  predictionChart.data.datasets[0].backgroundColor = colors;
  predictionChart.update();
}

// Load initial sensor data
async function loadInitialSensorData() {
  try {
    const res = await fetch("/api/sensor/latest");
    const data = await res.json();
    if (data) {
      updateSensorData(data);
    }
  } catch (error) {
    console.error("Error loading sensor data:", error);
  }
}

// Initialize on page load
document.addEventListener("DOMContentLoaded", () => {
  initSunlightChart();
  initPredictionChart();
  connectWebSocket();
  loadInitialSensorData();
  loadWeatherData();
  loadPredictions();

  // Refresh weather and predictions periodically
  setInterval(loadWeatherData, 60000); // Every minute
  setInterval(loadPredictions, 300000); // Every 5 minutes
});
