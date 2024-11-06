# Getting Started

This guide will help you set up and run the weather station monitoring system.

## Installation

### Prerequisites

- Python 3.9 or higher
- `uv` package manager (recommended) or `pip`

### Setting Up the Environment

1. Create and activate a virtual environment:
```bash
uv venv
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate  # On Windows
```

2. Install the package:
```bash
uv pip install .
```

For development installation:
```bash
uv pip install -e ".[dev]"
```

## Basic Usage

Here's a minimal example to get started:

```python
import asyncio
from pathlib import Path
from weather_station.models import WeatherStation
from weather_station.sensors import MockSensor
from weather_station.station import WeatherStationController

async def main():
    # Create station configuration
    station = WeatherStation(
        station_id="my-station",
        name="My Weather Station",
        latitude=51.5074,
        longitude=-0.1278,
        altitude_meters=100.0
    )

    # Initialize sensor
    sensor = MockSensor()
    
    # Create controller
    controller = WeatherStationController(
        station=station,
        sensor=sensor,
        reading_interval=60.0,  # Read every minute
        data_dir=Path("weather_data")
    )

    # Add simple alert handling
    def print_alert(alert):
        print(f"Weather Alert: {alert.message}")

    controller.add_alert_callback(print_alert)

    # Run the station
    try:
        await controller.start()
    except KeyboardInterrupt:
        controller.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

Save this as `run_station.py` and run it:
```bash
python run_station.py
```

## Using Real Sensors

The example above uses `MockSensor` for testing. For real hardware, implement a custom sensor class:

```python
from weather_station.sensors import BaseSensor, SensorError

class MyCustomSensor(BaseSensor):
    def __init__(self):
        self.device = None

    def initialize(self) -> None:
        try:
            # Initialize your hardware
            self.device = setup_hardware()
        except Exception as e:
            raise SensorError(f"Failed to initialize sensor: {e}")

    def cleanup(self) -> None:
        if self.device:
            self.device.close()
            self.device = None

    def read_temperature(self) -> float:
        if not self.device:
            raise SensorError("Sensor not initialized")
        return self.device.get_temperature()

    # Implement other required methods...
```

## Alert Handling

Add custom alert handling for different notification methods:

```python
import smtplib
from email.message import EmailMessage

def email_alert(alert):
    msg = EmailMessage()
    msg.set_content(alert.message)
    msg['Subject'] = f'Weather Alert: {alert.alert_type}'
    msg['From'] = "weather@example.com"
    msg['To'] = "admin@example.com"

    # Send email
    with smtplib.SMTP('smtp.example.com', 587) as server:
        server.starttls()
        server.login("user", "password")
        server.send_message(msg)

# Add to controller
controller.add_alert_callback(email_alert)
```

## Data Storage

Data is automatically saved in JSONL format. Access stored data:

```python
import json
from pathlib import Path
from datetime import datetime

def read_days_data(date: datetime) -> list:
    filename = f"readings_{date.strftime('%Y%m%d')}.jsonl"
    filepath = Path("weather_data") / filename
    
    readings = []
    with open(filepath) as f:
        for line in f:
            readings.append(json.loads(line))
    
    return readings

# Example: Read today's data
today = datetime.now()
readings = read_days_data(today)
```

## Running Tests

The project includes a test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=weather_station

# Run specific test file
pytest tests/test_weather_station.py
```

## Common Issues

### Sensor Initialization Failed

If sensor initialization fails:

1. Check hardware connections
2. Verify power supply
3. Check permissions (for I2C/SPI devices)
4. Ensure required kernel modules are loaded

```bash
# Check I2C devices
i2cdetect -y 1

# Check USB devices
lsusb
```

### Data Storage Issues

If data isn't being saved:

1. Check directory permissions
2. Verify disk space
3. Ensure the data directory exists

```bash
# Create data directory if missing
mkdir -p weather_data

# Check permissions
ls -l weather_data
```

## Next Steps

1. Implement a custom sensor for your hardware
2. Set up meaningful alert thresholds
3. Configure data backup
4. Add visualization tools
5. Set up automated deployment

For more detailed information, see:

- [API Reference](api/models.md)
- [Configuration Guide](configuration.md)
- [Examples](examples.md)
