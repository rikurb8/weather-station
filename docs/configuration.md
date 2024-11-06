# Configuration Guide

This guide covers all configurable aspects of the weather station system, including station setup, sensor configuration, alert thresholds, and data storage options.

## Station Configuration

The `WeatherStation` model defines the basic station configuration:

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

### Station ID Format

- Must be unique across your network of stations
- Recommended format: `{location}-{number}` or `{purpose}-{number}`
- Examples: `rooftop-001`, `garden-001`, `research-001`

## Controller Configuration

The `WeatherStationController` accepts several configuration parameters:

```python
from pathlib import Path
from weather_station.station import WeatherStationController

controller = WeatherStationController(
    station=station,
    sensor=sensor,
    reading_interval=60.0,         # Seconds between readings
    data_dir=Path("weather_data")  # Data storage directory
)
```

### Reading Interval

Choose an appropriate interval based on your needs:
- 60 seconds: Standard weather monitoring
- 30 seconds: Detailed weather tracking
- 300 seconds (5 minutes): Long-term monitoring
- 1 second: Storm or research monitoring

```python
# Example: High-frequency monitoring
controller = WeatherStationController(
    station=station,
    sensor=sensor,
    reading_interval=1.0  # 1-second intervals
)
```

### Data Storage

Configure the data directory structure:

```python
# Custom directory structure
data_dir = Path("data/weather/station_001")
controller = WeatherStationController(
    station=station,
    sensor=sensor,
    data_dir=data_dir
)
```

Recommended directory structure:
```
data/
├── weather/
│   ├── station_001/
│   │   ├── readings_20240101.jsonl
│   │   ├── readings_20240102.jsonl
│   │   └── ...
│   └── station_002/
│       ├── readings_20240101.jsonl
│       └── ...
└── backup/
    └── ...
```

## Alert Configuration

Create a custom alert configuration class:

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class AlertThresholds:
    high_temperature: float = 35.0
    low_temperature: float = 0.0
    high_wind: float = 20.0
    low_pressure: float = 980.0
    high_pressure: float = 1030.0
    rain_rate: Optional[float] = 10.0  # mm/hour

class ConfigurableController(WeatherStationController):
    def __init__(
        self,
        station: WeatherStation,
        sensor: SensorInterface,
        thresholds: AlertThresholds,
        **kwargs
    ):
        super().__init__(station, sensor, **kwargs)
        self.thresholds = thresholds

    def _check_alerts(self, reading: SensorReading) -> None:
        alerts = []

        if reading.temperature_celsius > self.thresholds.high_temperature:
            alerts.append(
                WeatherAlert(
                    alert_id=f"high_temp_{reading.timestamp.isoformat()}",
                    station_id=self.station.station_id,
                    alert_type="high_temperature",
                    severity="warning",
                    message=f"High temperature: {reading.temperature_celsius}°C",
                    reading=reading
                )
            )

        # Add other threshold checks...

        for alert in alerts:
            for callback in self.alert_callbacks:
                try:
                    callback(alert)
                except Exception as e:
                    logger.error(f"Alert callback failed: {str(e)}")
```

Usage:
```python
thresholds = AlertThresholds(
    high_temperature=30.0,  # Lower threshold for tropical climate
    high_wind=15.0,        # Lower threshold for urban area
    rain_rate=5.0          # Lower threshold for flood-prone area
)

controller = ConfigurableController(
    station=station,
    sensor=sensor,
    thresholds=thresholds
)
```

## Logging Configuration

Configure logging for better monitoring:

```python
import logging
import structlog
from pathlib import Path

def configure_logging(
    log_dir: Path,
    level: int = logging.INFO,
    retention_days: int = 30
) -> None:
    """Configure structured logging with rotation."""
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure structlog
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

    # Add file handler with rotation
    from logging.handlers import TimedRotatingFileHandler
    handler = TimedRotatingFileHandler(
        log_dir / "weather_station.log",
        when="midnight",
        interval=1,
        backupCount=retention_days
    )
    
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(level)
```

Usage:
```python
configure_logging(
    log_dir=Path("logs"),
    level=logging.DEBUG,  # More detailed logging
    retention_days=60     # Keep logs for 60 days
)
```

## Environment Variables

The system supports configuration via environment variables:

```bash
# Station configuration
WEATHER_STATION_ID=station-001
WEATHER_STATION_NAME="Rooftop Station"
WEATHER_STATION_LAT=51.5074
WEATHER_STATION_LON=-0.1278
WEATHER_STATION_ALT=100.0

# Controller configuration
WEATHER_READING_INTERVAL=60
WEATHER_DATA_DIR=/path/to/data

# Alert thresholds
WEATHER_HIGH_TEMP=35.0
WEATHER_LOW_TEMP=0.0
WEATHER_HIGH_WIND=20.0

# Logging
WEATHER_LOG_LEVEL=INFO
WEATHER_LOG_DIR=/path/to/logs
```

Load configuration from environment:

```python
import os
from pathlib import Path

def load_config():
    """Load configuration from environment variables."""
    return {
        'station': WeatherStation(
            station_id=os.getenv('WEATHER_STATION_ID', 'default-001'),
            name=os.getenv('WEATHER_STATION_NAME', 'Default Station'),
            latitude=float(os.getenv('WEATHER_STATION_LAT', '0.0')),
            longitude=float(os.getenv('WEATHER_STATION_LON', '0.0')),
            altitude_meters=float(os.getenv('WEATHER_STATION_ALT', '0.0'))
        ),
        'controller': {
            'reading_interval': float(os.getenv('WEATHER_READING_INTERVAL', '60.0')),
            'data_dir': Path(os.getenv('WEATHER_DATA_DIR', 'data'))
        },
        'thresholds': AlertThresholds(
            high_temperature=float(os.getenv('WEATHER_HIGH_TEMP', '35.0')),
            low_temperature=float(os.getenv('WEATHER_LOW_TEMP', '0.0')),
            high_wind=float(os.getenv('WEATHER_HIGH_WIND', '20.0'))
        )
    }
```

## Best Practices

1. Use environment variables for deployment-specific configuration
2. Keep sensitive values in environment variables or secure vaults
3. Use configuration classes for type safety and validation
4. Implement reasonable defaults for all configuration options
5. Document all configuration options and their impacts
6. Use structured logging for better debugging
7. Implement configuration validation
8. Consider using configuration files for complex setups
