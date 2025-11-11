from fastapi import APIRouter, HTTPException
from typing import List
from models import Device, CommandRequest, CommandResponse, Telemetry

router = APIRouter()


# simple in-memory store
_DEVICES = {
    "dev-1": Device(id="dev-1", name="Temperature Sensor", status="online"),
    "dev-2": Device(id="dev-2", name="Light Actuator", status="offline"),
}


@router.get("/devices", response_model=List[Device])
async def list_devices():
    return list(_DEVICES.values())


@router.get("/devices/{device_id}", response_model=Device)
async def get_device(device_id: str):
    device = _DEVICES.get(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="device not found")
    return device


@router.post("/devices/{device_id}/command", response_model=CommandResponse)
async def send_command(device_id: str, req: CommandRequest):
    device = _DEVICES.get(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="device not found")
    # fake command handling
    resp = CommandResponse(
        device_id=device_id,
        command=req.command,
        status="accepted",
        detail=f"params={req.params}",
    )
    return resp


@router.post("/telemetry")
async def post_telemetry(t: Telemetry):
    # simple logging; extend to persist later
    print("telemetry:", t)
    return {"status": "ok"}