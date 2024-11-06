import pytest
from datetime import datetime
from pathlib import Path
import json

from backend.models import WeatherStation, SensorReading, WeatherAlert
from backend.sensors import MockSensor
from backend.station import WeatherStationController


@pytest.fixture
def mock_sensor():
    sensor = MockSensor()
    return sensor


@pytest.fixture
def test_station():
    return WeatherStation(
        station_id="TEST001",
        name="Test Station",
        latitude=51.5074,
        longitude=-0.1278,
        altitude_meters=11.0,
    )


@pytest.fixture
def temp_data_dir(tmp_path):
    data_dir = tmp_path / "weather_data"
    data_dir.mkdir()
    return data_dir


async def test_weather_station_controller(mock_sensor, test_station, temp_data_dir):
    # Initialize controller with short interval for testing
    controller = WeatherStationController(
        station=test_station,
        sensor=mock_sensor,
        reading_interval=0.1,
        data_dir=temp_data_dir,
    )

    # Test alert callback
    alerts = []

    def alert_callback(alert: WeatherAlert):
        alerts.append(alert)

    controller.add_alert_callback(alert_callback)

    # Run controller briefly
    import asyncio

    task = asyncio.create_task(controller.start())
    await asyncio.sleep(0.3)  # Allow for a few readings
    controller.stop()
    await task

    # Check that readings were saved
    data_files = list(temp_data_dir.glob("readings_*.jsonl"))
    assert len(data_files) > 0

    # Verify reading format
    with open(data_files[0]) as f:
        reading_json = f.readline().strip()
        reading = SensorReading.model_validate_json(reading_json)

        assert isinstance(reading.timestamp, datetime)
        assert isinstance(reading.temperature_celsius, float)
        assert isinstance(reading.humidity_percent, float)
        assert isinstance(reading.pressure_hpa, float)


def test_sensor_reading_model():
    reading = SensorReading(
        temperature_celsius=20.5,
        humidity_percent=65.0,
        pressure_hpa=1013.25,
        wind_speed_ms=5.0,
        wind_direction_degrees=180.0,
        rain_mm=0.0,
    )

    assert reading.temperature_celsius == 20.5
    assert reading.humidity_percent == 65.0
    assert reading.pressure_hpa == 1013.25
    assert reading.wind_speed_ms == 5.0
    assert reading.wind_direction_degrees == 180.0
    assert reading.rain_mm == 0.0


def test_weather_station_model():
    station = WeatherStation(
        station_id="TEST001",
        name="Test Station",
        latitude=51.5074,
        longitude=-0.1278,
        altitude_meters=11.0,
    )

    assert station.station_id == "TEST001"
    assert station.name == "Test Station"
    assert station.latitude == 51.5074
    assert station.longitude == -0.1278
    assert station.altitude_meters == 11.0
