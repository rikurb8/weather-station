from abc import ABC, abstractmethod
from typing import Optional, Protocol, runtime_checkable
from datetime import datetime, UTC
import logging
from contextlib import contextmanager

from .models import SensorReading


class SensorError(Exception):
    """Base exception for sensor-related errors."""

    def __init__(self, message: str, sensor_id: Optional[str] = None):
        """
        Initialize a sensor error with optional sensor identification.

        Args:
            message: Descriptive error message
            sensor_id: Optional identifier for the specific sensor
        """
        self.sensor_id = sensor_id
        super().__init__(f"[{sensor_id or 'Unknown Sensor'}] {message}")


@runtime_checkable
class SensorInterface(Protocol):
    """Protocol defining the interface for weather sensors."""

    def read_temperature(self) -> float:
        """
        Read temperature in Celsius.

        Returns:
            Temperature in Celsius

        Raises:
            SensorError: If temperature reading fails
        """
        ...

    def read_humidity(self) -> float:
        """
        Read relative humidity percentage.

        Returns:
            Humidity percentage

        Raises:
            SensorError: If humidity reading fails
        """
        ...

    def read_pressure(self) -> float:
        """
        Read atmospheric pressure in hPa.

        Returns:
            Pressure in hectopascals

        Raises:
            SensorError: If pressure reading fails
        """
        ...

    def read_wind_speed(self) -> Optional[float]:
        """
        Read wind speed in meters per second.

        Returns:
            Wind speed or None if not available

        Raises:
            SensorError: If wind speed reading fails
        """
        ...

    def read_wind_direction(self) -> Optional[float]:
        """
        Read wind direction in degrees.

        Returns:
            Wind direction or None if not available

        Raises:
            SensorError: If wind direction reading fails
        """
        ...

    def read_rainfall(self) -> Optional[float]:
        """
        Read rainfall in millimeters.

        Returns:
            Rainfall amount or None if not available

        Raises:
            SensorError: If rainfall reading fails
        """
        ...


class BaseSensor(ABC):
    """Abstract base class for weather sensors with enhanced error handling and logging."""

    def __init__(self, sensor_id: Optional[str] = None):
        """
        Initialize the base sensor.

        Args:
            sensor_id: Optional unique identifier for the sensor
        """
        self.sensor_id = sensor_id or self.__class__.__name__
        self.logger = logging.getLogger(f"sensor.{self.sensor_id}")
        self._is_initialized = False

    @contextmanager
    def sensor_context(self):
        """
        Context manager for sensor initialization and cleanup.

        Ensures proper initialization and resource management.
        """
        try:
            self.initialize()
            self._is_initialized = True
            yield self
        except Exception as e:
            self.logger.error(f"Sensor initialization failed: {e}")
            raise SensorError(
                f"Sensor initialization failed: {e}", self.sensor_id
            ) from e
        finally:
            try:
                self.cleanup()
            except Exception as e:
                self.logger.warning(f"Sensor cleanup failed: {e}")
            self._is_initialized = False

    @abstractmethod
    def initialize(self) -> None:
        """
        Initialize the sensor hardware.

        Raises:
            SensorError: If initialization fails
        """
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """
        Cleanup sensor resources.

        Raises:
            SensorError: If cleanup fails
        """
        pass

    def get_reading(self) -> SensorReading:
        """
        Get a complete sensor reading.

        Returns:
            A SensorReading instance with current measurements

        Raises:
            SensorError: If any reading fails
        """
        if not self._is_initialized:
            raise SensorError("Sensor not initialized", self.sensor_id)

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
            self.logger.error(f"Failed to get sensor reading: {e}")
            raise SensorError(
                f"Failed to get sensor reading: {e}", self.sensor_id
            ) from e


class MockSensor(BaseSensor):
    """Mock sensor implementation for testing with configurable readings."""

    def __init__(
        self,
        temperature: float = 20.0,
        humidity: float = 65.0,
        pressure: float = 1013.25,
        wind_speed: Optional[float] = 5.0,
        wind_direction: Optional[float] = 180.0,
        rainfall: Optional[float] = 0.0,
        sensor_id: Optional[str] = None,
    ):
        """
        Initialize mock sensor with configurable readings.

        Args:
            temperature: Simulated temperature in Celsius
            humidity: Simulated humidity percentage
            pressure: Simulated atmospheric pressure in hPa
            wind_speed: Simulated wind speed in m/s
            wind_direction: Simulated wind direction in degrees
            rainfall: Simulated rainfall in mm
            sensor_id: Optional unique identifier
        """
        super().__init__(sensor_id)
        self._temperature = temperature
        self._humidity = humidity
        self._pressure = pressure
        self._wind_speed = wind_speed
        self._wind_direction = wind_direction
        self._rainfall = rainfall

    def initialize(self) -> None:
        """Mock initialization."""
        self.logger.info("Mock sensor initialized")

    def cleanup(self) -> None:
        """Mock cleanup."""
        self.logger.info("Mock sensor cleaned up")

    def read_temperature(self) -> float:
        return self._temperature

    def read_humidity(self) -> float:
        return self._humidity

    def read_pressure(self) -> float:
        return self._pressure

    def read_wind_speed(self) -> Optional[float]:
        return self._wind_speed

    def read_wind_direction(self) -> Optional[float]:
        return self._wind_direction

    def read_rainfall(self) -> Optional[float]:
        return self._rainfall
