from typing import Optional
from pydantic import BaseModel


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