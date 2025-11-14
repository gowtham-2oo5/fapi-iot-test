from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import asyncio
from datetime import datetime

from app.database import init_db, SensorReading, async_session_maker
from app.weather_service import fetch_weather_data, get_latest_weather
from app.ml_model import scheduler
from app.websocket_manager import manager
from app.config import get_settings
from pydantic import BaseModel
from sqlalchemy import select

settings = get_settings()


# Background tasks
async def weather_fetch_task():
    """Periodically fetch weather data"""
    while True:
        await asyncio.sleep(settings.weather_fetch_interval)
        await fetch_weather_data()


async def model_retrain_task():
    """Check if model needs retraining"""
    while True:
        await asyncio.sleep(3600)  # Check every hour
        async with async_session_maker() as session:
            result = await session.execute(select(SensorReading))
            count = len(result.scalars().all())
            if count >= settings.model_retrain_threshold and count % settings.model_retrain_threshold == 0:
                print("Retraining model...")
                await scheduler.train_model()


async def broadcast_updates_task():
    """Periodically broadcast weather and prediction updates"""
    while True:
        await asyncio.sleep(60)  # Every minute
        
        # Broadcast weather update
        weather = await get_latest_weather()
        if weather:
            await manager.broadcast({
                "type": "weather_update",
                "data": {
                    "temperature": weather.temperature,
                    "humidity": weather.humidity,
                    "cloud_cover": weather.cloud_cover,
                    "weather_main": weather.weather_main,
                    "weather_description": weather.weather_description,
                    "timestamp": weather.timestamp.isoformat()
                }
            })


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    print("Database initialized")
    
    # Start background tasks
    asyncio.create_task(weather_fetch_task())
    asyncio.create_task(model_retrain_task())
    asyncio.create_task(broadcast_updates_task())
    
    # Initial weather fetch
    await fetch_weather_data()
    
    yield
    # Shutdown
    print("Shutting down...")


app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "title": "Solar Appliance Scheduler"})


# IoT Data Reception Endpoint
class SensorData(BaseModel):
    device_id: str
    ldr_value: float


@app.post("/api/sensor/data")
async def receive_sensor_data(data: SensorData):
    """Receive LDR sensor data from NodeMCU ESP8266"""
    try:
        async with async_session_maker() as session:
            reading = SensorReading(
                device_id=data.device_id,
                ldr_value=data.ldr_value,
                timestamp=datetime.utcnow()
            )
            session.add(reading)
            await session.commit()
            await session.refresh(reading)
        
        # Broadcast to WebSocket clients
        await manager.broadcast({
            "type": "sensor_update",
            "data": {
                "device_id": data.device_id,
                "ldr_value": data.ldr_value,
                "timestamp": reading.timestamp.isoformat()
            }
        })
        
        return {"status": "success", "id": reading.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sensor/latest")
async def get_latest_sensor():
    """Get latest sensor reading"""
    async with async_session_maker() as session:
        result = await session.execute(
            select(SensorReading).order_by(SensorReading.timestamp.desc()).limit(1)
        )
        reading = result.scalar_one_or_none()
        if not reading:
            return None
        return {
            "device_id": reading.device_id,
            "ldr_value": reading.ldr_value,
            "timestamp": reading.timestamp.isoformat()
        }


@app.get("/api/weather/latest")
async def get_weather():
    """Get latest weather data"""
    weather = await get_latest_weather()
    if not weather:
        return None
    return {
        "temperature": weather.temperature,
        "humidity": weather.humidity,
        "cloud_cover": weather.cloud_cover,
        "weather_main": weather.weather_main,
        "weather_description": weather.weather_description,
        "timestamp": weather.timestamp.isoformat()
    }


@app.get("/api/predictions")
async def get_predictions():
    """Get 24-hour optimal usage predictions"""
    predictions = await scheduler.predict_optimal_hours()
    return {"predictions": predictions}


@app.post("/api/model/train")
async def train_model():
    """Manually trigger model retraining"""
    success = await scheduler.train_model()
    if success:
        stats = scheduler.get_index_stats()
        return {
            "status": "success",
            "message": "Model trained successfully",
            "faiss_stats": stats
        }
    return {"status": "error", "message": "Insufficient data for training"}


@app.get("/api/model/stats")
async def get_model_stats():
    """Get model and FAISS index statistics"""
    stats = scheduler.get_index_stats()
    return {
        "model_trained": scheduler.model is not None,
        "scaler_ready": scheduler.scaler is not None,
        "faiss_index": stats
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and listen for client messages
            data = await websocket.receive_text()
            # Echo back or handle client requests
            if data == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        manager.disconnect(websocket)


from app.routes import router as devices_router
app.include_router(devices_router, prefix="/api", tags=["devices"])