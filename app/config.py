from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    openweather_api_key: str = ""
    openweather_city: str = "London"
    openweather_lat: float = 51.5074
    openweather_lon: float = -0.1278
    database_url: str = "sqlite+aiosqlite:///./iot_data.db"
    weather_fetch_interval: int = 1800  # 30 minutes in seconds
    model_retrain_threshold: int = 50  # retrain after N new records

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
