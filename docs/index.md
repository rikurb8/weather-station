# Weather Station

A Python-based weather station monitoring system that provides a robust framework for collecting, storing, and analyzing weather data from various sensors.

## Features

- Real-time weather data collection
- Support for multiple sensor types through a flexible interface
- Automated data logging and storage
- Configurable alert system
- Type-safe implementation using Pydantic models
- Async-first architecture for efficient operation

## System Components

### Models

The system uses Pydantic models for type-safe data handling:

- `SensorReading`: Represents individual sensor measurements
- `WeatherStation`: Contains station configuration and metadata
- `WeatherAlert`: Defines weather alerts and warnings

### Sensors

The sensor system is built around a flexible interface:

- `SensorInterface`: Protocol defining required sensor methods
- `BaseSensor`: Abstract base class for sensor implementations
- `MockSensor`: Example implementation for testing

### Station Controller

The `WeatherStationController` manages:

- Periodic sensor readings
- Data storage
- Alert monitoring and notification
- Async operation for efficient resource usage

## Quick Start

```python
from weather_station.models import WeatherStation
from weather_station.sensors import MockSensor
from weather_station.station import WeatherStationController

# Create a weather station configuration
station = WeatherStation(
    station_id="station-001",
    name="Test Station",
    latitude=51.5074,
    longitude=-0.1278,
    altitude_meters=11.0
)

# Initialize sensor and controller
sensor = MockSensor()
controller = WeatherStationController(
    station=station,
    sensor=sensor,
    reading_interval=60.0
)

# Add an alert callback
def alert_handler(alert):
    print(f"Alert received: {alert.message}")

controller.add_alert_callback(alert_handler)

# Start monitoring
await controller.start()
```

## Requirements

- Python 3.9+
- Dependencies:
    - pydantic >= 2.0.0
    - pytest >= 7.0.0 (for testing)
    - pytest-asyncio >= 0.21.0 (for async tests)
    - httpx >= 0.24.0

## Installation

```bash
uv venv
uv pip install .
