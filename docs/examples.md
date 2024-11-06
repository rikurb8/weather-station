# Examples

This page provides practical examples and common patterns for using the weather station system.

## Basic Station Setup

### Simple Monitoring

Basic setup with default configuration:

```python
import asyncio
from weather_station.models import WeatherStation
from weather_station.sensors import MockSensor
from weather_station.station import WeatherStationController

async def main():
    station = WeatherStation(
        station_id="basic-001",
        name="Basic Station",
        latitude=51.5074,
        longitude=-0.1278,
        altitude_meters=100.0
    )
    
    sensor = MockSensor()
    controller = WeatherStationController(
        station=station,
        sensor=sensor
    )
    
    try:
        await controller.start()
    except KeyboardInterrupt:
        controller.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

## Advanced Sensor Implementation

### Custom BME280 Sensor

Implementation for the popular BME280 sensor:

```python
from typing import Optional
import board
import adafruit_bme280.advanced as adafruit_bme280
from weather_station.sensors import BaseSensor, SensorError

class BME280Sensor(BaseSensor):
    def __init__(self, i2c_address: int = 0x76):
        self.i2c_address = i2c_address
        self.device = None
        self.i2c = None
        
    def initialize(self) -> None:
        try:
            self.i2c = board.I2C()
            self.device = adafruit_bme280.Adafruit_BME280_I2C(
                self.i2c,
                address=self.i2c_address
            )
            # Configure for weather monitoring
            self.device.mode = adafruit_bme280.MODE_NORMAL
            self.device.standby_period = adafruit_bme280.STANDBY_TC_500
            self.device.pressure_oversampling = adafruit_bme280.OVERSCAN_X16
            self.device.temperature_oversampling = adafruit_bme280.OVERSCAN_X2
            self.device.humidity_oversampling = adafruit_bme280.OVERSCAN_X1
            self.device.filter_coefficient = adafruit_bme280.IIR_FILTER_X16
        except Exception as e:
            raise SensorError(f"Failed to initialize BME280: {e}")
    
    def cleanup(self) -> None:
        if self.device:
            self.device.mode = adafruit_bme280.MODE_SLEEP
            self.device = None
        if self.i2c:
            self.i2c.deinit()
            self.i2c = None
    
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
        return None  # BME280 doesn't measure wind
    
    def read_wind_direction(self) -> Optional[float]:
        return None  # BME280 doesn't measure wind
    
    def read_rainfall(self) -> Optional[float]:
        return None  # BME280 doesn't measure rainfall
```

## Alert Handling Examples

### Email Alerts

```python
import smtplib
from email.message import EmailMessage
from typing import Optional
from weather_station.models import WeatherAlert

class EmailAlertHandler:
    def __init__(
        self,
        smtp_server: str,
        smtp_port: int,
        username: str,
        password: str,
        from_addr: str,
        to_addrs: list[str],
        use_tls: bool = True
    ):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_addr = from_addr
        self.to_addrs = to_addrs
        self.use_tls = use_tls
    
    def __call__(self, alert: WeatherAlert) -> None:
        msg = EmailMessage()
        msg.set_content(self._format_alert(alert))
        msg["Subject"] = f"Weather Alert: {alert.alert_type}"
        msg["From"] = self.from_addr
        msg["To"] = ", ".join(self.to_addrs)
        
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            if self.use_tls:
                server.starttls()
            server.login(self.username, self.password)
            server.send_message(msg)
    
    def _format_alert(self, alert: WeatherAlert) -> str:
        return f"""
Weather Alert from {alert.station_id}
Type: {alert.alert_type}
Severity: {alert.severity}
Time: {alert.timestamp}

{alert.message}

Current Readings:
- Temperature: {alert.reading.temperature_celsius}°C
- Humidity: {alert.reading.humidity_percent}%
- Pressure: {alert.reading.pressure_hpa} hPa
"""

# Usage
email_handler = EmailAlertHandler(
    smtp_server="smtp.gmail.com",
    smtp_port=587,
    username="weather@example.com",
    password="your-password",
    from_addr="weather@example.com",
    to_addrs=["admin@example.com"]
)

controller.add_alert_callback(email_handler)
```

### SMS Alerts using Twilio

```python
from twilio.rest import Client
from weather_station.models import WeatherAlert

class SMSAlertHandler:
    def __init__(
        self,
        account_sid: str,
        auth_token: str,
        from_number: str,
        to_numbers: list[str]
    ):
        self.client = Client(account_sid, auth_token)
        self.from_number = from_number
        self.to_numbers = to_numbers
    
    def __call__(self, alert: WeatherAlert) -> None:
        message = f"Weather Alert: {alert.alert_type}\n{alert.message}"
        
        for number in self.to_numbers:
            self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=number
            )

# Usage
sms_handler = SMSAlertHandler(
    account_sid="your-sid",
    auth_token="your-token",
    from_number="+1234567890",
    to_numbers=["+1987654321"]
)

controller.add_alert_callback(sms_handler)
```

## Data Analysis Examples

### Reading and Analyzing Data

```python
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta

def load_data(data_dir: Path, start_date: datetime, end_date: datetime) -> pd.DataFrame:
    """Load weather data into a pandas DataFrame."""
    data = []
    current_date = start_date
    
    while current_date <= end_date:
        filename = f"readings_{current_date.strftime('%Y%m%d')}.jsonl"
        filepath = data_dir / filename
        
        if filepath.exists():
            # Read JSONL file
            df = pd.read_json(filepath, lines=True)
            data.append(df)
            
        current_date += timedelta(days=1)
    
    return pd.concat(data) if data else pd.DataFrame()

# Usage
data_dir = Path("weather_data")
start = datetime(2024, 1, 1)
end = datetime(2024, 1, 31)

df = load_data(data_dir, start, end)

# Basic statistics
daily_stats = df.groupby(df['timestamp'].dt.date).agg({
    'temperature_celsius': ['mean', 'min', 'max'],
    'humidity_percent': 'mean',
    'pressure_hpa': 'mean'
})

# Plot temperature trends
import matplotlib.pyplot as plt

plt.figure(figsize=(12, 6))
plt.plot(df['timestamp'], df['temperature_celsius'])
plt.title('Temperature Over Time')
plt.xlabel('Time')
plt.ylabel('Temperature (°C)')
plt.grid(True)
plt.show()
```

## Multiple Station Management

### Station Network

```python
import asyncio
from typing import Dict
from weather_station.models import WeatherStation
from weather_station.station import WeatherStationController

class StationNetwork:
    def __init__(self):
        self.stations: Dict[str, WeatherStationController] = {}
    
    def add_station(self, controller: WeatherStationController) -> None:
        """Add a station to the network."""
        station_id = controller.station.station_id
        if station_id in self.stations:
            raise ValueError(f"Station {station_id} already exists")
        self.stations[station_id] = controller
    
    async def start_all(self) -> None:
        """Start all stations."""
        await asyncio.gather(
            *(controller.start() for controller in self.stations.values())
        )
    
    def stop_all(self) -> None:
        """Stop all stations."""
        for controller in self.stations.values():
            controller.stop()

# Usage
async def main():
    network = StationNetwork()
    
    # Add multiple stations
    stations = [
        ("rooftop", 51.5074, -0.1278, 100.0),
        ("garden", 51.5075, -0.1279, 95.0),
        ("parking", 51.5076, -0.1280, 97.0)
    ]
    
    for location, lat, lon, alt in stations:
        station = WeatherStation(
            station_id=f"{location}-001",
            name=f"{location.title()} Station",
            latitude=lat,
            longitude=lon,
            altitude_meters=alt
        )
        
        controller = WeatherStationController(
            station=station,
            sensor=MockSensor(),
            data_dir=Path(f"data/{location}")
        )
        
        network.add_station(controller)
    
    try:
        await network.start_all()
    except KeyboardInterrupt:
        network.stop_all()

if __name__ == "__main__":
    asyncio.run(main())
```

## Testing Examples

### Mocking Sensors

```python
import pytest
from weather_station.sensors import BaseSensor
from typing import Optional

class TestSensor(BaseSensor):
    """Configurable sensor for testing."""
    
    def __init__(
        self,
        temperature: float = 20.0,
        humidity: float = 65.0,
        pressure: float = 1013.25
    ):
        self.temperature = temperature
        self.humidity = humidity
        self.pressure = pressure
    
    def initialize(self) -> None:
        pass
    
    def cleanup(self) -> None:
        pass
    
    def read_temperature(self) -> float:
        return self.temperature
    
    def read_humidity(self) -> float:
        return self.humidity
    
    def read_pressure(self) -> float:
        return self.pressure
    
    def read_wind_speed(self) -> Optional[float]:
        return None
    
    def read_wind_direction(self) -> Optional[float]:
        return None
    
    def read_rainfall(self) -> Optional[float]:
        return None

@pytest.fixture
def test_sensor():
    return TestSensor(
        temperature=25.0,
        humidity=60.0,
        pressure=1015.0
    )

def test_high_temperature_alert(test_sensor):
    station = WeatherStation(
        station_id="test-001",
        name="Test Station",
        latitude=0.0,
        longitude=0.0,
        altitude_meters=0.0
    )
    
    alerts = []
    def alert_handler(alert):
        alerts.append(alert)
    
    controller = WeatherStationController(
        station=station,
        sensor=test_sensor
    )
    controller.add_alert_callback(alert_handler)
    
    # Simulate a reading
    reading = test_sensor.get_reading()
    controller._check_alerts(reading)
    
    assert len(alerts) == 0  # No alert for normal temperature
    
    # Simulate high temperature
    test_sensor.temperature = 36.0
    reading = test_sensor.get_reading()
    controller._check_alerts(reading)
    
    assert len(alerts) == 1
    assert alerts[0].alert_type == "high_temperature"
