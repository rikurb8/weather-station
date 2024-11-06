import asyncio
from datetime import datetime, UTC
from typing import Optional, List, Callable
import logging
from pathlib import Path
import json

from .models import WeatherStation, SensorReading, WeatherAlert
from .sensors import SensorInterface, SensorError

logger = logging.getLogger(__name__)


class WeatherStationController:
    """Main weather station controller."""

    def __init__(
        self,
        station: WeatherStation,
        sensor: SensorInterface,
        reading_interval: float = 60.0,
        data_dir: Optional[Path] = None,
    ) -> None:
        """
        Initialize the weather station controller.

        Args:
            station: WeatherStation configuration
            sensor: Sensor interface implementation
            reading_interval: Interval between readings in seconds
            data_dir: Directory for storing readings
        """
        self.station = station
        self.sensor = sensor
        self.reading_interval = reading_interval
        self.data_dir = data_dir or Path("data")
        self.alert_callbacks: List[Callable[[WeatherAlert], None]] = []
        self._running = False

        # Ensure data directory exists
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def add_alert_callback(self, callback: Callable[[WeatherAlert], None]) -> None:
        """Add a callback for weather alerts."""
        self.alert_callbacks.append(callback)

    def _check_alerts(self, reading: SensorReading) -> None:
        """Check for alert conditions and trigger callbacks."""
        alerts = []

        # Example alert conditions
        if reading.temperature_celsius > 35:
            alerts.append(
                WeatherAlert(
                    alert_id=f"high_temp_{datetime.now(UTC).isoformat()}",
                    station_id=self.station.station_id,
                    alert_type="high_temperature",
                    severity="warning",
                    message=f"High temperature detected: {reading.temperature_celsius}°C",
                    reading=reading,
                )
            )

        # Trigger callbacks for any alerts
        for alert in alerts:
            for callback in self.alert_callbacks:
                try:
                    callback(alert)
                except Exception as e:
                    logger.error(f"Alert callback failed: {str(e)}")

    def _save_reading(self, reading: SensorReading) -> None:
        """Save the reading to a file."""
        timestamp = reading.timestamp.strftime("%Y%m%d")
        filepath = self.data_dir / f"readings_{timestamp}.jsonl"

        try:
            with open(filepath, "a") as f:
                f.write(reading.model_dump_json() + "\n")
        except Exception as e:
            logger.error(f"Failed to save reading: {str(e)}")

    async def start(self) -> None:
        """Start the weather station monitoring."""
        self._running = True

        try:
            while self._running:
                try:
                    reading = self.sensor.get_reading()
                    self.station.last_reading = reading
                    self._save_reading(reading)
                    self._check_alerts(reading)

                    logger.info(
                        f"Reading: {reading.temperature_celsius}°C, "
                        f"{reading.humidity_percent}%, "
                        f"{reading.pressure_hpa}hPa"
                    )

                except SensorError as e:
                    logger.error(f"Sensor reading failed: {str(e)}")

                await asyncio.sleep(self.reading_interval)

        finally:
            self._running = False

    def stop(self) -> None:
        """Stop the weather station monitoring."""
        self._running = False
