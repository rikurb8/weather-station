# Weather Station Controller

The `WeatherStationController` is the main component responsible for managing weather station operations, including data collection, storage, and alert handling.

## WeatherStationController

```python
class WeatherStationController:
    def __init__(
        self,
        station: WeatherStation,
        sensor: SensorInterface,
        reading_interval: float = 60.0,
        data_dir: Optional[Path] = None,
    ) -> None:
```

### Parameters

- `station`: WeatherStation configuration and metadata
- `sensor`: Implementation of the SensorInterface
- `reading_interval`: Time between readings in seconds (default: 60.0)
- `data_dir`: Directory for storing readings (default: "./data")

## Key Methods

### Adding Alert Callbacks

```python
def add_alert_callback(self, callback: Callable[[WeatherAlert], None]) -> None:
    """Add a callback for weather alerts."""
```

Alert callbacks are functions that will be called when weather alerts are triggered. Multiple callbacks can be registered.

### Starting the Controller

```python
async def start(self) -> None:
    """Start the weather station monitoring."""
```

Starts the asynchronous monitoring loop. The controller will:
1. Take periodic readings from the sensor
2. Save readings to storage
3. Check for alert conditions
4. Update the station's last reading

### Stopping the Controller

```python
def stop(self) -> None:
    """Stop the weather station monitoring."""
```

Gracefully stops the monitoring loop.

## Internal Operations

### Alert Checking

```python
def _check_alerts(self, reading: SensorReading) -> None:
    """Check for alert conditions and trigger callbacks."""
```

The controller checks each reading against predefined alert conditions. When conditions are met, it:
1. Creates a WeatherAlert instance
2. Calls all registered alert callbacks with the alert

Default alert conditions include:
- High temperature (>35°C)

### Data Storage

```python
def _save_reading(self, reading: SensorReading) -> None:
    """Save the reading to a file."""
```

Readings are saved in JSONL format (one JSON object per line) in daily files:
- File naming: `readings_YYYYMMDD.jsonl`
- Each line contains a complete serialized SensorReading
- Files are stored in the configured data directory

## Usage Example

```python
import asyncio
from pathlib import Path
from weather_station.models import WeatherStation
from weather_station.sensors import MockSensor
from weather_station.station import WeatherStationController

# Create station configuration
station = WeatherStation(
    station_id="station-001",
    name="Rooftop Station",
    latitude=51.5074,
    longitude=-0.1278,
    altitude_meters=100.0
)

# Initialize sensor and controller
sensor = MockSensor()
controller = WeatherStationController(
    station=station,
    sensor=sensor,
    reading_interval=30.0,
    data_dir=Path("weather_data")
)

# Add alert handling
def handle_alert(alert: WeatherAlert) -> None:
    print(f"ALERT: {alert.message}")
    # Add your alert handling logic here
    # e.g., send email, SMS, or push notification

controller.add_alert_callback(handle_alert)

# Run the controller
async def main():
    try:
        await controller.start()
    except KeyboardInterrupt:
        controller.stop()

asyncio.run(main())
```

## Data Storage Format

Readings are stored in JSONL format. Example file content (`readings_20240101.jsonl`):

```jsonl
{"timestamp": "2024-01-01T00:00:00Z", "temperature_celsius": 20.0, "humidity_percent": 65.0, "pressure_hpa": 1013.25, "wind_speed_ms": 5.0, "wind_direction_degrees": 180.0, "rain_mm": 0.0}
{"timestamp": "2024-01-01T00:01:00Z", "temperature_celsius": 20.1, "humidity_percent": 64.8, "pressure_hpa": 1013.20, "wind_speed_ms": 5.2, "wind_direction_degrees": 185.0, "rain_mm": 0.0}
```

## Best Practices

1. **Error Handling**: Implement robust error handling in alert callbacks
   ```python
   def alert_callback(alert: WeatherAlert) -> None:
       try:
           # Handle alert
           send_notification(alert)
       except Exception as e:
           logging.error(f"Alert handling failed: {e}")
   ```

2. **Resource Management**: Use async context managers for clean setup/teardown
   ```python
   async with WeatherStationController(...) as controller:
       await controller.start()
   ```

3. **Data Backup**: Regularly backup the data directory
   ```python
   # Example backup script
   from shutil import copytree
   from datetime import datetime
   
   def backup_data():
       timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
       copytree("weather_data", f"backup/weather_data_{timestamp}")
   ```

4. **Alert Configuration**: Consider implementing configurable alert thresholds
   ```python
   class AlertConfig:
       def __init__(self):
           self.high_temp_threshold = 35.0
           self.low_temp_threshold = 0.0
           self.high_wind_threshold = 20.0
   ```

5. **Logging**: Use structured logging for better monitoring
   ```python
   import structlog
   logger = structlog.get_logger()
   
   logger.info(
       "sensor_reading",
       temperature=reading.temperature_celsius,
       humidity=reading.humidity_percent
   )
