"""
Comprehensive example demonstrating advanced usage of the Weather Station Monitoring System.

This example showcases:
- Custom sensor implementation
- Multiple alert mechanisms
- Logging configuration
- Advanced station setup
"""

import asyncio
import logging
from pathlib import Path
from typing import Optional

from .models import WeatherStation, SensorReading
from .sensors import BaseSensor, SensorError
from .station import WeatherStationController


class AdvancedMockSensor(BaseSensor):
    """
    Advanced mock sensor with configurable and dynamic behavior.
    Simulates more complex sensor interactions and potential failures.
    """

    def __init__(
        self,
        sensor_id: Optional[str] = None,
        temperature_range: tuple[float, float] = (15.0, 35.0),
        humidity_range: tuple[float, float] = (30.0, 70.0),
        failure_probability: float = 0.05,
    ):
        """
        Initialize the advanced mock sensor.

        Args:
            sensor_id: Unique identifier for the sensor
            temperature_range: (min, max) temperature range
            humidity_range: (min, max) humidity range
            failure_probability: Probability of simulating a sensor failure
        """
        super().__init__(sensor_id)
        self._temperature_range = temperature_range
        self._humidity_range = humidity_range
        self._failure_probability = failure_probability

        # Simulation state
        import random

        self._random = random.Random()
        self._consecutive_failures = 0
        self._max_consecutive_failures = 3

    def initialize(self) -> None:
        """Simulate sensor initialization with potential failure."""
        self.logger.info(f"Initializing sensor {self.sensor_id}")

        # Simulate occasional initialization failure
        if self._random.random() < 0.1:
            raise SensorError("Simulated initialization failure")

    def cleanup(self) -> None:
        """Simulate sensor cleanup."""
        self.logger.info(f"Cleaning up sensor {self.sensor_id}")

    def _simulate_reading_failure(self) -> bool:
        """
        Determine if a reading should fail based on failure probability.

        Returns:
            Boolean indicating whether a reading should fail
        """
        if self._consecutive_failures >= self._max_consecutive_failures:
            return False

        if self._random.random() < self._failure_probability:
            self._consecutive_failures += 1
            return True

        self._consecutive_failures = 0
        return False

    def read_temperature(self) -> float:
        """
        Simulate temperature reading with dynamic variation.

        Returns:
            Simulated temperature reading

        Raises:
            SensorError: If simulated reading failure occurs
        """
        if self._simulate_reading_failure():
            raise SensorError("Simulated temperature reading failure")

        min_temp, max_temp = self._temperature_range
        return self._random.uniform(min_temp, max_temp)

    def read_humidity(self) -> float:
        """
        Simulate humidity reading with dynamic variation.

        Returns:
            Simulated humidity reading

        Raises:
            SensorError: If simulated reading failure occurs
        """
        if self._simulate_reading_failure():
            raise SensorError("Simulated humidity reading failure")

        min_humid, max_humid = self._humidity_range
        return self._random.uniform(min_humid, max_humid)

    def read_pressure(self) -> float:
        """
        Simulate atmospheric pressure reading.

        Returns:
            Simulated pressure reading
        """
        return 1013.25 + self._random.uniform(-10.0, 10.0)

    def read_wind_speed(self) -> Optional[float]:
        """
        Simulate wind speed reading.

        Returns:
            Optional simulated wind speed
        """
        return self._random.uniform(0.0, 15.0)

    def read_wind_direction(self) -> Optional[float]:
        """
        Simulate wind direction reading.

        Returns:
            Optional simulated wind direction in degrees
        """
        return self._random.uniform(0.0, 360.0)

    def read_rainfall(self) -> Optional[float]:
        """
        Simulate rainfall reading.

        Returns:
            Optional simulated rainfall amount
        """
        return self._random.uniform(0.0, 5.0) if self._random.random() < 0.3 else 0.0


def setup_logging(log_dir: Path, log_level: int = logging.INFO):
    """
    Configure comprehensive logging for the weather station.

    Args:
        log_dir: Directory to store log files
        log_level: Logging level
    """
    log_dir.mkdir(parents=True, exist_ok=True)

    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_dir / "weather_station.log"),
            logging.StreamHandler(),
        ],
    )


def create_email_alert_handler(email: str):
    """
    Create an email alert handler.

    Args:
        email: Email address to send alerts to

    Returns:
        Callable alert handler
    """

    def email_alert(alert):
        """
        Send email alert.

        Args:
            alert: WeatherAlert instance
        """
        try:
            # Placeholder for email sending logic
            # In a real implementation, use an email library like smtplib
            logging.getLogger(__name__).info(
                f"EMAIL ALERT sent to {email}: {alert.message}"
            )
        except Exception as e:
            logging.getLogger(__name__).error(f"Failed to send email alert: {e}")

    return email_alert


def create_sms_alert_handler(phone_number: str):
    """
    Create an SMS alert handler.

    Args:
        phone_number: Phone number to send SMS alerts to

    Returns:
        Callable alert handler
    """

    def sms_alert(alert):
        """
        Send SMS alert.

        Args:
            alert: WeatherAlert instance
        """
        try:
            # Placeholder for SMS sending logic
            # In a real implementation, use a SMS gateway or service
            logging.getLogger(__name__).info(
                f"SMS ALERT sent to {phone_number}: {alert.message}"
            )
        except Exception as e:
            logging.getLogger(__name__).error(f"Failed to send SMS alert: {e}")

    return sms_alert


async def run_advanced_weather_station():
    """
    Run an advanced weather station with multiple features.
    """
    # Setup logging
    log_dir = Path("logs")
    setup_logging(log_dir, logging.DEBUG)
    logger = logging.getLogger(__name__)

    # Create station
    station = WeatherStation(
        station_id="advanced-mock-station",
        name="Advanced Mock Weather Station",
        latitude=51.5074,
        longitude=-0.1278,
        altitude_meters=100.0,
    )

    # Create advanced mock sensor
    sensor = AdvancedMockSensor(
        sensor_id="advanced-mock-sensor",
        temperature_range=(10.0, 40.0),
        humidity_range=(20.0, 80.0),
        failure_probability=0.1,
    )

    # Create controller
    controller = WeatherStationController(
        station=station,
        sensor=sensor,
        reading_interval=30.0,  # Read every 30 seconds
        data_dir=Path("weather_data"),
        alert_thresholds={
            "high_temperature": 35.0,
            "low_temperature": 10.0,
            "high_wind_speed": 15.0,
            "high_humidity": 75.0,
            "low_humidity": 25.0,
        },
        max_consecutive_errors=3,
    )

    # Add multiple alert handlers
    controller.add_alert_callback(create_email_alert_handler("admin@example.com"))
    controller.add_alert_callback(create_sms_alert_handler("+1234567890"))
    controller.add_alert_callback(
        lambda alert: logger.warning(f"ALERT: {alert.message}")
    )

    # Run the station
    try:
        logger.info("Starting advanced weather station")
        await controller.start()
    except KeyboardInterrupt:
        logger.info("Weather station monitoring interrupted")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        controller.stop()
        logger.info("Weather station monitoring stopped")


def main():
    """
    Main entry point for the example script.
    """
    asyncio.run(run_advanced_weather_station())


if __name__ == "__main__":
    main()
