from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from app.config import get_settings

settings = get_settings()

engine = create_async_engine(settings.database_url, echo=False)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()


class SensorReading(Base):
    __tablename__ = "sensor_readings"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, index=True)
    ldr_value = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


class WeatherData(Base):
    __tablename__ = "weather_data"
    
    id = Column(Integer, primary_key=True, index=True)
    temperature = Column(Float)
    humidity = Column(Float)
    cloud_cover = Column(Float)
    uv_index = Column(Float, nullable=True)
    weather_main = Column(String)
    weather_description = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


class AIPrediction(Base):
    __tablename__ = "ai_predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    predicted_hour = Column(Integer)
    confidence_score = Column(Float)
    recommendation = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    async with async_session_maker() as session:
        yield session
