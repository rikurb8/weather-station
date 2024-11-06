# Getting Started with Weather Station Monitoring System

## System Requirements

### Hardware
- Python 3.9+
- Recommended: Raspberry Pi 4 (2GB+ RAM)
- Compatible sensor hardware
- Network connectivity

### Software Dependencies
- Python 3.9 or higher
- `uv` package manager
- `pip` (optional)

## Installation

### 1. Create Project Directory

```bash
mkdir weather-station
cd weather-station
```

### 2. Set Up Virtual Environment

```bash
# Using uv (recommended)
uv venv
source .venv/bin/activate  # Unix/macOS
# or
.venv\Scripts\activate     # Windows
```

### 3. Install Package

For production:
```bash
uv pip install .
```

For development:
```bash
uv pip install -e ".[dev]"
```

## Basic Usage

### Minimal Example

```python
import asyncio
from pathlib import Path
from weather_station.models import WeatherStation
from weather_station.sensors import MockSensor
from weather_station.station import WeatherStationController

async def main():
    # Create station configuration
    station = WeatherStation(
        station_id="home-station",
        name="Home Weather Monitor",
        latitude=51.5074,
        longitude=-0.1278,
        altitude_meters=100.0
    )

    # Initialize mock sensor (replace with real sensor)
    sensor = MockSensor(
        temperature=22.5,
        humidity=45.0,
        pressure=1013.25
    )
    
    # Create controller with custom configuration
    controller = WeatherStationController(
        station=station,
        sensor=sensor,
        reading_interval=60.0,  # Read every minute
        data_dir=Path("weather_data"),
        alert_thresholds={
            "high_temperature": 30.0,
            "low_temperature": 10.0
        }
    )

    # Add alert handling
    def print_alert(alert):
        print(f"🚨 Weather Alert: {alert.message}")

    controller.add_alert_callback(print_alert)

    # Run the station
    try:
        await controller.start()
    except KeyboardInterrupt:
        controller.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

### Real Sensor Implementation

```python
from weather_station.sensors import BaseSensor, SensorError

class BME280Sensor(BaseSensor):
    def __init__(self, i2c_bus=1, address=0x76):
        super().__init__(sensor_id=f"bme280-{address}")
        self.i2c_bus = i2c_bus
        self.address = address
        self._device = None

    def initialize(self) -> None:
        try:
            import board
            import adafruit_bme280.basic as adafruit_bme280
            
            i2c = board.I2C()
            self._device = adafruit_bme280.Adafruit_BME280_I2C(
                i2c, address=self.address
            )
            self.logger.info(f"BME280 sensor initialized on bus {self.i2c_bus}")
        except Exception as e:
            raise SensorError(f"Sensor initialization failed: {e}")

    def cleanup(self) -> None:
        if self._device:
            # Perform any necessary cleanup
            self._device = None

    def read_temperature(self) -> float:
        if not self._device:
            raise SensorError("Sensor not initialized")
        return self._device.temperature

    def read_humidity(self) -> float:
        if not self._device:
            raise SensorError("Sensor not initialized")
        return self._device.relative_humidity

    def read_pressure(self) -> float:
        if not self._device:
            raise SensorError("Sensor not initialized")
        return self._device.pressure
```

## Advanced Configuration

### Logging Setup

```python
import logging
from pathlib import Path

def configure_logging(log_dir: Path, level=logging.INFO):
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "weather_station.log"),
            logging.StreamHandler()
        ]
    )
```

### Multiple Alert Handlers

```python
def email_alert(alert):
    # Implement email sending logic
    send_email(
        to="admin@example.com",
        subject=f"Weather Alert: {alert.alert_type}",
        body=str(alert)
    )

def sms_alert(alert):
    # Implement SMS sending logic
    send_sms(
        to="+1234567890",
        message=str(alert)
    )

# Add multiple alert handlers
controller.add_alert_callback(print_alert)
controller.add_alert_callback(email_alert)
controller.add_alert_callback(sms_alert)
```

## Deployment Strategies

### Docker Deployment

Create a `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Install the package
RUN pip install .

# Run the weather station
CMD ["python", "-m", "weather_station.main"]
```

### Systemd Service

Create `/etc/systemd/system/weather-station.service`:
```ini
[Unit]
Description=Weather Station Monitoring Service
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/weather-station
ExecStart=/home/pi/weather-station/.venv/bin/python -m weather_station.main
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

## Troubleshooting

### Common Issues

1. **Sensor Not Initializing**
   - Check hardware connections
   - Verify I2C/SPI settings
   - Ensure proper power supply

2. **Data Not Saving**
   - Check directory permissions
   - Verify disk space
   - Ensure data directory exists

3. **Network Connectivity**
   - Check WiFi/Ethernet settings
   - Verify firewall rules
   - Test network connectivity

### Diagnostic Commands

```bash
# Check I2C devices
i2cdetect -y 1

# Check system logs
journalctl -u weather-station.service

# Verify Python environment
python -m weather_station.diagnostics
```

## Next Steps

1. Implement custom sensors
2. Set up advanced alert mechanisms
3. Create data visualization tools
4. Implement remote configuration
5. Add machine learning for predictive analysis

## Resources

- [Configuration Guide](configuration.md)
- [API Reference](api/index.md)
- [Examples](examples.md)
