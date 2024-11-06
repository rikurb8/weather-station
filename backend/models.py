from datetime import datetime, UTC
from typing import Optional
from pydantic import BaseModel, Field


class SensorReading(BaseModel):
    """Individual sensor reading with timestamp."""

    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    temperature_celsius: float = Field(..., description="Temperature in Celsius")
    humidity_percent: float = Field(
        ..., ge=0, le=100, description="Relative humidity percentage"
    )
    pressure_hpa: float = Field(..., description="Atmospheric pressure in hPa")
    wind_speed_ms: Optional[float] = Field(
        None, ge=0, description="Wind speed in meters per second"
    )
    wind_direction_degrees: Optional[float] = Field(
        None, ge=0, lt=360, description="Wind direction in degrees"
    )
    rain_mm: Optional[float] = Field(None, ge=0, description="Rainfall in millimeters")


class WeatherStation(BaseModel):
    """Weather station configuration and metadata."""

    station_id: str = Field(
        ..., description="Unique identifier for the weather station"
    )
    name: str = Field(..., description="Human-readable name for the station")
    latitude: float = Field(..., ge=-90, le=90, description="Station latitude")
    longitude: float = Field(..., ge=-180, le=180, description="Station longitude")
    altitude_meters: float = Field(..., description="Station altitude above sea level")
    last_reading: Optional[SensorReading] = Field(
        None, description="Most recent sensor reading"
    )


class WeatherAlert(BaseModel):
    """Weather alert or warning."""

    alert_id: str = Field(..., description="Unique identifier for the alert")
    station_id: str = Field(
        ..., description="ID of the station that triggered the alert"
    )
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    alert_type: str = Field(
        ..., description="Type of alert (e.g., 'high_temperature', 'storm_warning')"
    )
    severity: str = Field(..., description="Alert severity level")
    message: str = Field(..., description="Alert description")
    reading: SensorReading = Field(
        ..., description="Sensor reading that triggered the alert"
    )
