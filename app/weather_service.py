import httpx
from datetime import datetime
from app.config import get_settings
from app.database import WeatherData, async_session_maker
from sqlalchemy import select

settings = get_settings()


async def fetch_weather_data():
    """Fetch current weather data from OpenWeatherMap API"""
    if not settings.openweather_api_key or settings.openweather_api_key == "your_api_key_here":
        print("Warning: OpenWeatherMap API key not configured")
        return None
    
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": settings.openweather_lat,
        "lon": settings.openweather_lon,
        "appid": settings.openweather_api_key,
        "units": "metric"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            
            weather_record = WeatherData(
                temperature=data["main"]["temp"],
                humidity=data["main"]["humidity"],
                cloud_cover=data["clouds"]["all"],
                uv_index=None,  # requires separate API call
                weather_main=data["weather"][0]["main"],
                weather_description=data["weather"][0]["description"],
                timestamp=datetime.utcnow()
            )
            
            async with async_session_maker() as session:
                session.add(weather_record)
                await session.commit()
                await session.refresh(weather_record)
            
            print(f"Weather data fetched: {weather_record.temperature}°C, {weather_record.weather_description}")
            return weather_record
            
    except Exception as e:
        print(f"Error fetching weather data: {e}")
        return None


async def get_latest_weather():
    """Get the most recent weather data from database"""
    async with async_session_maker() as session:
        result = await session.execute(
            select(WeatherData).order_by(WeatherData.timestamp.desc()).limit(1)
        )
        return result.scalar_one_or_none()
