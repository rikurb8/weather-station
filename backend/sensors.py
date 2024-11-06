from abc import ABC, abstractmethod
from typing import Optional, Protocol
from datetime import datetime, UTC

from .models import SensorReading


class SensorError(Exception):
    """Base exception for sensor-related errors."""

    pass


class SensorInterface(Protocol):
    """Protocol defining the interface for weather sensors."""

    def read_temperature(self) -> float:
        """Read temperature in Celsius."""
        ...

    def read_humidity(self) -> float:
        """Read relative humidity percentage."""
        ...

    def read_pressure(self) -> float:
        """Read atmospheric pressure in hPa."""
        ...

    def read_wind_speed(self) -> Optional[float]:
        """Read wind speed in meters per second."""
        ...

    def read_wind_direction(self) -> Optional[float]:
        """Read wind direction in degrees."""
        ...

    def read_rainfall(self) -> Optional[float]:
        """Read rainfall in millimeters."""
        ...


class BaseSensor(ABC):
    """Abstract base class for weather sensors."""

    @abstractmethod
    def initialize(self) -> None:
        """Initialize the sensor hardware."""
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """Cleanup sensor resources."""
        pass

    def get_reading(self) -> SensorReading:
        """Get a complete sensor reading."""
        try:
            return SensorReading(
                timestamp=datetime.now(UTC),
                temperature_celsius=self.read_temperature(),
                humidity_percent=self.read_humidity(),
                pressure_hpa=self.read_pressure(),
                wind_speed_ms=self.read_wind_speed(),
                wind_direction_degrees=self.read_wind_direction(),
                rain_mm=self.read_rainfall(),
            )
        except Exception as e:
            raise SensorError(f"Failed to get sensor reading: {str(e)}") from e


class MockSensor(BaseSensor):
    """Mock sensor implementation for testing."""

    def initialize(self) -> None:
        pass

    def cleanup(self) -> None:
        pass

    def read_temperature(self) -> float:
        return 20.0

    def read_humidity(self) -> float:
        return 65.0

    def read_pressure(self) -> float:
        return 1013.25

    def read_wind_speed(self) -> Optional[float]:
        return 5.0

    def read_wind_direction(self) -> Optional[float]:
        return 180.0

    def read_rainfall(self) -> Optional[float]:
        return 0.0
