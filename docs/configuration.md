# Configuration Guide

This guide covers comprehensive configuration options for the weather station system, including station setup, sensor configuration, alert thresholds, and advanced deployment strategies.

## Station Configuration

### Basic Configuration

The `WeatherStation` model defines the core station configuration:

```python
from weather_station.models import WeatherStation

station = WeatherStation(
    station_id="station-001",      # Unique identifier
    name="Rooftop Station",        # Human-readable name
    latitude=51.5074,              # Station latitude (-90 to 90)
    longitude=-0.1278,             # Station longitude (-180 to 180)
    altitude_meters=100.0          # Altitude above sea level
)
```

#### Station ID Best Practices

- Must be unique across your network of stations
- Recommended format: `{location}-{number}` or `{purpose}-{number}`
- Examples: `rooftop-001`, `garden-001`, `research-001`

## Sensor Configuration

### Sensor Initialization

The system supports a flexible sensor interface with robust error handling:

```python
from weather_station.sensors import BaseSensor, SensorError

class CustomSensor(BaseSensor):
    def __init__(self, sensor_id: Optional[str] = None):
        super().__init__(sensor_id)
        self._device = None

    def initialize(self) -> None:
        try:
            # Initialize hardware connection
            self._device = connect_to_sensor()
            self.logger.info(f"Sensor {self.sensor_id} initialized successfully")
        except Exception as e:
            self.logger.error(f"Sensor initialization failed: {e}")
            raise SensorError(f"Initialization failed: {e}", self.sensor_id)

    def cleanup(self) -> None:
        if self._device:
            try:
                self._device.close()
                self.logger.info(f"Sensor {self.sensor_id} cleaned up")
            except Exception as e:
                self.logger.warning(f"Sensor cleanup failed: {e}")

    # Implement reading methods...
```

### Sensor Context Management

Use the `sensor_context()` for safe sensor operations:

```python
with sensor.sensor_context():
    reading = sensor.get_reading()
    process_reading(reading)
```

## Controller Configuration

The `WeatherStationController` offers extensive configuration options:

```python
from pathlib import Path
from weather_station.station import WeatherStationController

controller = WeatherStationController(
    station=station,
    sensor=sensor,
    reading_interval=60.0,         # Seconds between readings
    data_dir=Path("weather_data"),  # Data storage directory
    alert_thresholds={
        "high_temperature": 35.0,   # Customizable alert thresholds
        "low_temperature": 0.0,
        "high_wind_speed": 20.0,
        "high_humidity": 90.0,
        "low_humidity": 20.0,
        "high_pressure": 1030.0,
        "low_pressure": 980.0,
    },
    max_consecutive_errors=5       # Stop monitoring after 5 consecutive errors
)
```

### Configuration Parameters

#### `reading_interval`
- `30-60 seconds`: Standard weather monitoring
- `5-15 seconds`: Detailed tracking
- `300 seconds`: Long-term, low-power monitoring

#### `max_consecutive_errors`
Prevents continuous operation with persistent sensor issues:
- `3-5`: Sensitive systems
- `10-15`: Robust, mission-critical deployments

## Alert Configuration

### Alert Thresholds

Customize alert conditions with flexible thresholds:

```python
alert_config = {
    "high_temperature": 35.0,  # Adjust for local climate
    "low_temperature": 0.0,
    "high_wind_speed": 20.0,   # m/s, adjust for location
    "high_humidity": 90.0,     # Percent
    "low_humidity": 20.0,
    "high_pressure": 1030.0,   # hPa
    "low_pressure": 980.0
}

controller = WeatherStationController(
    station=station,
    sensor=sensor,
    alert_thresholds=alert_config
)
```

### Alert Callbacks

Add multiple alert handling mechanisms:

```python
def log_alert(alert):
    logging.warning(f"Alert: {alert.message}")

def send_email_alert(alert):
    email_service.send(
        to="admin@example.com",
        subject=f"Weather Alert: {alert.alert_type}",
        body=str(alert)
    )

def send_sms_alert(alert):
    sms_service.send(
        to="+1234567890",
        message=alert.message
    )

# Add multiple callbacks
controller.add_alert_callback(log_alert)
controller.add_alert_callback(send_email_alert)
controller.add_alert_callback(send_sms_alert)
```

## Logging Configuration

Configure comprehensive logging:

```python
import logging
import structlog
from pathlib import Path

def configure_logging(
    log_dir: Path,
    station_id: str,
    level: int = logging.INFO,
    retention_days: int = 30
) -> None:
    """
    Configure structured logging with rotation and station-specific tracking.
    
    Args:
        log_dir: Base directory for log storage
        station_id: Unique identifier for log segregation
        level: Logging level
        retention_days: Number of days to retain log files
    """
    station_log_dir = log_dir / station_id
    station_log_dir.mkdir(parents=True, exist_ok=True)

    # Structured logging configuration
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        wrapper_class=structlog.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Rotating file handler
    from logging.handlers import TimedRotatingFileHandler
    file_handler = TimedRotatingFileHandler(
        station_log_dir / "weather_station.log",
        when="midnight",
        interval=1,
        backupCount=retention_days
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)
    root_logger.setLevel(level)

# Usage
configure_logging(
    log_dir=Path("/var/log/weather_station"),
    station_id=station.station_id,
    level=logging.DEBUG,
    retention_days=60
)
```

## Environment Variable Configuration

Support configuration via environment variables:

```python
import os
from pathlib import Path

def load_config_from_env():
    """
    Load weather station configuration from environment variables.
    
    Returns:
        Dictionary of configuration parameters
    """
    return {
        'station': {
            'id': os.getenv('WEATHER_STATION_ID', 'default-001'),
            'name': os.getenv('WEATHER_STATION_NAME', 'Default Station'),
            'latitude': float(os.getenv('WEATHER_STATION_LAT', '0.0')),
            'longitude': float(os.getenv('WEATHER_STATION_LON', '0.0')),
            'altitude': float(os.getenv('WEATHER_STATION_ALT', '0.0'))
        },
        'controller': {
            'reading_interval': float(os.getenv('WEATHER_READING_INTERVAL', '60.0')),
            'max_consecutive_errors': int(os.getenv('WEATHER_MAX_ERRORS', '5'))
        },
        'alerts': {
            'high_temperature': float(os.getenv('ALERT_HIGH_TEMP', '35.0')),
            'low_temperature': float(os.getenv('ALERT_LOW_TEMP', '0.0')),
            'high_wind_speed': float(os.getenv('ALERT_HIGH_WIND', '20.0'))
        }
    }
```

## Best Practices

1. Use environment variables for deployment-specific configuration
2. Keep sensitive values in secure vaults or environment variables
3. Implement reasonable defaults for all configuration options
4. Use structured logging for better debugging
5. Implement configuration validation
6. Consider using configuration files for complex setups
7. Regularly rotate and backup log files
8. Monitor and log sensor and system health

## Troubleshooting

- Check sensor connections and power supply
- Verify network connectivity
- Monitor system logs
- Implement redundant alert mechanisms
- Perform regular maintenance and calibration
