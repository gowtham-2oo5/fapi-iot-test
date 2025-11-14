from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class Device(BaseModel):
    id: str
    name: str
    status: Optional[str] = "offline"


class CommandRequest(BaseModel):
    command: str
    params: Optional[dict] = {}


class CommandResponse(BaseModel):
    device_id: str
    command: str
    status: str
    detail: Optional[str] = None


class Telemetry(BaseModel):
    device_id: str
    metric: str
    value: float
    ts: Optional[str] = None


class SensorData(BaseModel):
    device_id: str
    ldr_value: float
    timestamp: Optional[datetime] = None


class WeatherResponse(BaseModel):
    temperature: float
    humidity: float
    cloud_cover: float
    weather_main: str
    weather_description: str
    timestamp: datetime


class PredictionResponse(BaseModel):
    hour: int
    score: float
    recommendation: str