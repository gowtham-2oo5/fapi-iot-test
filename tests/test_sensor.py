"""
Test script to simulate NodeMCU ESP8266 sending sensor data
Run this to test the IoT data reception endpoint
"""
import httpx
import asyncio
import random
from datetime import datetime


async def send_sensor_data():
    """Simulate sending LDR sensor readings"""
    url = "http://localhost:8000/api/sensor/data"
    
    for i in range(10):
        # Simulate varying sunlight intensity (0-1024)
        ldr_value = random.randint(200, 1000)
        
        data = {
            "device_id": "ESP8266_001",
            "ldr_value": ldr_value
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=data, timeout=5.0)
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Sent LDR: {ldr_value} - Response: {response.status_code}")
        except Exception as e:
            print(f"Error: {e}")
        
        await asyncio.sleep(5)  # Send every 5 seconds


if __name__ == "__main__":
    print("Starting sensor data simulation...")
    print("Make sure the FastAPI server is running on http://localhost:8000")
    asyncio.run(send_sensor_data())
