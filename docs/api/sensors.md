# Sensors

The weather station's sensor system is designed with flexibility and extensibility in mind. It provides protocols and abstract base classes that define the interface for sensor implementations.

## SensorInterface

A Protocol defining the required interface for weather sensors.

```python
class SensorInterface(Protocol):
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
```

## BaseSensor

An abstract base class that provides a foundation for sensor implementations.

```python
class BaseSensor(ABC):
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
```

### Key Methods

- `initialize()`: Set up the sensor hardware and any required resources
- `cleanup()`: Release resources and perform cleanup when the sensor is no longer needed
- `get_reading()`: Collect all sensor measurements and return a complete `SensorReading`

## MockSensor

A mock implementation of the sensor interface for testing and development.

```python
class MockSensor(BaseSensor):
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
```

## Exceptions

```python
class SensorError(Exception):
    """Base exception for sensor-related errors."""
    pass
```

## Creating Custom Sensors

To implement a custom sensor, you can either:

1. Implement the `SensorInterface` protocol directly
2. Extend the `BaseSensor` class (recommended)

Here's an example of a custom sensor implementation:

```python
class BME280Sensor(BaseSensor):
    def __init__(self, i2c_address: int = 0x76):
        self.i2c_address = i2c_address
        self.device = None

    def initialize(self) -> None:
        """Initialize the BME280 sensor."""
        import board
        import adafruit_bme280.advanced as adafruit_bme280
        i2c = board.I2C()
        self.device = adafruit_bme280.Adafruit_BME280_I2C(i2c, self.i2c_address)
        
    def cleanup(self) -> None:
        """Clean up I2C resources."""
        if self.device:
            self.device.deinit()
            self.device = None

    def read_temperature(self) -> float:
        if not self.device:
            raise SensorError("Sensor not initialized")
        return self.device.temperature

    def read_humidity(self) -> float:
        if not self.device:
            raise SensorError("Sensor not initialized")
        return self.device.relative_humidity

    def read_pressure(self) -> float:
        if not self.device:
            raise SensorError("Sensor not initialized")
        return self.device.pressure

    def read_wind_speed(self) -> Optional[float]:
        return None  # BME280 doesn't measure wind speed

    def read_wind_direction(self) -> Optional[float]:
        return None  # BME280 doesn't measure wind direction

    def read_rainfall(self) -> Optional[float]:
        return None  # BME280 doesn't measure rainfall
```

## Usage Example

```python
from weather_station.sensors import MockSensor

# Create and initialize a sensor
sensor = MockSensor()
sensor.initialize()

try:
    # Get a reading
    reading = sensor.get_reading()
    print(f"Temperature: {reading.temperature_celsius}°C")
    print(f"Humidity: {reading.humidity_percent}%")
    print(f"Pressure: {reading.pressure_hpa} hPa")
finally:
    # Clean up
    sensor.cleanup()
```

## Best Practices

1. Always implement proper resource cleanup in the `cleanup()` method
2. Handle hardware-specific errors and wrap them in `SensorError`
3. Validate sensor readings before returning them
4. Use type hints and docstrings for better code maintainability
5. Implement proper error handling for hardware communication
6. Consider adding calibration and configuration options where appropriate
