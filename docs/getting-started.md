# Getting Started with Weather Station

## Prerequisites

- Python 3.9+
- `uv` or `pip`
- Virtual environment recommended

## Installation

### Quick Install

```bash
# Create virtual environment
uv venv
source .venv/bin/activate  # Unix/macOS
# or
.venv\Scripts\activate     # Windows

# Install package
uv pip install .
```

### Development Installation

```bash
# Install with development dependencies
uv pip install -e ".[dev]"
```

## Basic Configuration

Create a basic configuration file `config.yaml`:

```yaml
station:
  id: home-station
  name: Home Weather Monitor
  location:
    latitude: 51.5074
    longitude: -0.1278
    altitude: 100.0

sensors:
  - type: temperature
    model: bme280
    pin: 4

alerts:
  high_temperature: 30.0
  low_temperature: 10.0
```

## First Run

```python
import asyncio
from weather_station import WeatherStation, WeatherStationController

async def main():
    # Initialize and run your weather station
    station = WeatherStation.from_config('config.yaml')
    controller = WeatherStationController(station)
    await controller.start()

asyncio.run(main())
```

## Troubleshooting

- Ensure all dependencies are installed
- Check sensor connections
- Verify Python version compatibility
