import asyncio
from datetime import datetime, UTC
from typing import Optional, List, Callable, Dict, Any
import logging
from pathlib import Path
import json
from contextlib import asynccontextmanager

from .models import WeatherStation, SensorReading, WeatherAlert
from .sensors import SensorInterface, SensorError, BaseSensor


class WeatherStationController:
    """
    Advanced weather station controller with comprehensive monitoring and error handling.

    Provides async monitoring, configurable alert thresholds, and robust data logging.
    """

    def __init__(
        self,
        station: WeatherStation,
        sensor: SensorInterface,
        reading_interval: float = 60.0,
        data_dir: Optional[Path] = None,
        alert_thresholds: Optional[Dict[str, Any]] = None,
        max_consecutive_errors: int = 5,
    ) -> None:
        """
        Initialize the weather station controller.

        Args:
            station: WeatherStation configuration
            sensor: Sensor interface implementation
            reading_interval: Interval between readings in seconds
            data_dir: Directory for storing readings
            alert_thresholds: Custom alert threshold configuration
            max_consecutive_errors: Maximum number of consecutive sensor errors before stopping
        """
        self.station = station
        self.sensor = sensor
        self.reading_interval = reading_interval
        self.data_dir = data_dir or Path("data") / station.station_id
        self.alert_callbacks: List[Callable[[WeatherAlert], None]] = []
        self._running = False
        self._consecutive_errors = 0
        self.max_consecutive_errors = max_consecutive_errors

        # Default alert thresholds
        self.alert_thresholds = {
            "high_temperature": 35.0,
            "low_temperature": 0.0,
            "high_wind_speed": 20.0,
            "high_humidity": 90.0,
            "low_humidity": 20.0,
            "high_pressure": 1030.0,
            "low_pressure": 980.0,
        }

        # Update with custom thresholds if provided
        if alert_thresholds:
            self.alert_thresholds.update(alert_thresholds)

        # Ensure data directory exists
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Configure logging
        self.logger = logging.getLogger(f"station.{station.station_id}")

    def add_alert_callback(self, callback: Callable[[WeatherAlert], None]) -> None:
        """
        Add a callback function for weather alerts.

        Args:
            callback: Function to be called when an alert is triggered
        """
        self.alert_callbacks.append(callback)

    def _generate_alert(
        self, reading: SensorReading, alert_type: str, severity: str, message: str
    ) -> WeatherAlert:
        """
        Generate a weather alert with a unique ID.

        Args:
            reading: Sensor reading that triggered the alert
            alert_type: Type of alert
            severity: Alert severity
            message: Alert description

        Returns:
            A WeatherAlert instance
        """
        return WeatherAlert(
            alert_id=f"{alert_type}_{datetime.now(UTC).isoformat()}",
            station_id=self.station.station_id,
            alert_type=alert_type,
            severity=severity,
            message=message,
            reading=reading,
        )

    def _check_alerts(self, reading: SensorReading) -> List[WeatherAlert]:
        """
        Check sensor readings against predefined alert thresholds.

        Args:
            reading: Current sensor reading

        Returns:
            List of triggered alerts
        """
        alerts = []

        # Temperature alerts
        if reading.temperature_celsius > self.alert_thresholds["high_temperature"]:
            alerts.append(
                self._generate_alert(
                    reading,
                    "high_temperature",
                    "warning",
                    f"High temperature: {reading.temperature_celsius}°C",
                )
            )
        elif reading.temperature_celsius < self.alert_thresholds["low_temperature"]:
            alerts.append(
                self._generate_alert(
                    reading,
                    "low_temperature",
                    "warning",
                    f"Low temperature: {reading.temperature_celsius}°C",
                )
            )

        # Wind speed alert
        if (
            reading.wind_speed_ms is not None
            and reading.wind_speed_ms > self.alert_thresholds["high_wind_speed"]
        ):
            alerts.append(
                self._generate_alert(
                    reading,
                    "high_wind",
                    "warning",
                    f"High wind speed: {reading.wind_speed_ms} m/s",
                )
            )

        # Humidity alerts
        if reading.humidity_percent > self.alert_thresholds["high_humidity"]:
            alerts.append(
                self._generate_alert(
                    reading,
                    "high_humidity",
                    "info",
                    f"High humidity: {reading.humidity_percent}%",
                )
            )
        elif reading.humidity_percent < self.alert_thresholds["low_humidity"]:
            alerts.append(
                self._generate_alert(
                    reading,
                    "low_humidity",
                    "info",
                    f"Low humidity: {reading.humidity_percent}%",
                )
            )

        # Pressure alerts
        if reading.pressure_hpa > self.alert_thresholds["high_pressure"]:
            alerts.append(
                self._generate_alert(
                    reading,
                    "high_pressure",
                    "info",
                    f"High pressure: {reading.pressure_hpa} hPa",
                )
            )
        elif reading.pressure_hpa < self.alert_thresholds["low_pressure"]:
            alerts.append(
                self._generate_alert(
                    reading,
                    "low_pressure",
                    "info",
                    f"Low pressure: {reading.pressure_hpa} hPa",
                )
            )

        return alerts

    def _trigger_alerts(self, alerts: List[WeatherAlert]) -> None:
        """
        Trigger alert callbacks for generated alerts.

        Args:
            alerts: List of alerts to trigger
        """
        for alert in alerts:
            for callback in self.alert_callbacks:
                try:
                    callback(alert)
                except Exception as e:
                    self.logger.error(f"Alert callback failed: {e}")

    def _save_reading(self, reading: SensorReading) -> None:
        """
        Save sensor reading to a daily JSONL file.

        Args:
            reading: Sensor reading to save
        """
        timestamp = reading.timestamp.strftime("%Y%m%d")
        filepath = self.data_dir / f"readings_{timestamp}.jsonl"

        try:
            with open(filepath, "a") as f:
                f.write(reading.model_dump_json() + "\n")
        except Exception as e:
            self.logger.error(f"Failed to save reading: {e}")

    @asynccontextmanager
    async def _sensor_monitoring(self):
        """
        Async context manager for sensor monitoring with error handling.

        Manages sensor state and handles consecutive errors.
        """
        try:
            yield
        except Exception as e:
            self._consecutive_errors += 1
            self.logger.error(f"Sensor monitoring error: {e}")

            if self._consecutive_errors >= self.max_consecutive_errors:
                self.logger.critical(
                    f"Max consecutive errors reached. Stopping station."
                )
                self.stop()

    async def start(self) -> None:
        """
        Start the weather station monitoring asynchronously.

        Continuously reads sensor data, saves readings, and checks for alerts.
        """
        self._running = True
        self._consecutive_errors = 0

        try:
            while self._running:
                async with self._sensor_monitoring():
                    reading = self.sensor.get_reading()
                    self.station.last_reading = reading

                    self._save_reading(reading)
                    alerts = self._check_alerts(reading)
                    self._trigger_alerts(alerts)

                    self.logger.info(
                        f"Reading: {reading.temperature_celsius}°C, "
                        f"{reading.humidity_percent}%, "
                        f"{reading.pressure_hpa}hPa"
                    )

                    await asyncio.sleep(self.reading_interval)

        except asyncio.CancelledError:
            self.logger.info("Weather station monitoring cancelled")
        finally:
            self._running = False

    def stop(self) -> None:
        """
        Stop the weather station monitoring.

        Gracefully terminates the monitoring process.
        """
        self._running = False
        self.logger.info("Weather station monitoring stopped")
