from datetime import datetime, UTC
from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator, ConfigDict


class SensorReading(BaseModel):
    """Individual sensor reading with timestamp."""

    model_config = ConfigDict(
        extra="forbid",  # Prevent additional fields
        frozen=True,  # Immutable model
        validate_assignment=True,  # Validate on attribute modification
    )

    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    temperature_celsius: float = Field(
        ..., description="Temperature in Celsius", gt=-273.15
    )
    humidity_percent: float = Field(
        ..., ge=0, le=100, description="Relative humidity percentage"
    )
    pressure_hpa: float = Field(..., description="Atmospheric pressure in hPa", gt=0)
    wind_speed_ms: Optional[float] = Field(
        None, ge=0, description="Wind speed in meters per second"
    )
    wind_direction_degrees: Optional[float] = Field(
        None, ge=0, lt=360, description="Wind direction in degrees"
    )
    rain_mm: Optional[float] = Field(None, ge=0, description="Rainfall in millimeters")

    @field_validator("temperature_celsius")
    @classmethod
    def validate_temperature(cls, v: float) -> float:
        """Ensure temperature is within realistic bounds."""
        if v < -100 or v > 100:
            raise ValueError("Temperature must be between -100°C and 100°C")
        return v


class WeatherStation(BaseModel):
    """Weather station configuration and metadata."""

    model_config = ConfigDict(extra="forbid", frozen=True, validate_assignment=True)

    station_id: str = Field(
        ...,
        description="Unique identifier for the weather station",
        min_length=3,
        max_length=50,
    )
    name: str = Field(
        ...,
        description="Human-readable name for the station",
        min_length=1,
        max_length=100,
    )
    latitude: float = Field(..., ge=-90, le=90, description="Station latitude")
    longitude: float = Field(..., ge=-180, le=180, description="Station longitude")
    altitude_meters: float = Field(
        ..., description="Station altitude above sea level", ge=-500, le=9000
    )
    last_reading: Optional[SensorReading] = Field(
        None, description="Most recent sensor reading"
    )


class WeatherAlert(BaseModel):
    """Weather alert or warning."""

    model_config = ConfigDict(extra="forbid", frozen=True, validate_assignment=True)

    alert_id: str = Field(
        ..., description="Unique identifier for the alert", min_length=3, max_length=50
    )
    station_id: str = Field(
        ...,
        description="ID of the station that triggered the alert",
        min_length=3,
        max_length=50,
    )
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    alert_type: Literal[
        "high_temperature",
        "low_temperature",
        "high_wind",
        "storm_warning",
        "flood_warning",
        "extreme_pressure",
    ] = Field(..., description="Predefined alert types")
    severity: Literal["info", "warning", "critical"] = Field(
        ..., description="Alert severity level"
    )
    message: str = Field(
        ..., description="Alert description", min_length=10, max_length=500
    )
    reading: SensorReading = Field(
        ..., description="Sensor reading that triggered the alert"
    )
