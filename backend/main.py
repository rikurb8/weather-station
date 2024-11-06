"""
Main entry point for the Weather Station Monitoring System.

Provides CLI and programmatic interfaces for running the weather station.
"""

import asyncio
import argparse
import logging
from pathlib import Path
import sys

from . import (
    WeatherStation,
    MockSensor,
    WeatherStationController,
    configure as configure_package,
    get_config,
)


def setup_logging(verbose: bool = False):
    """
    Configure logging based on verbosity.

    Args:
        verbose: Enable debug logging if True
    """
    log_level = logging.DEBUG if verbose else logging.INFO
    configure_package(log_level=logging.getLevelName(log_level))

    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured at {logging.getLevelName(log_level)} level")
    return logger


def create_default_station(station_id: str = "default-station") -> WeatherStation:
    """
    Create a default weather station configuration.

    Args:
        station_id: Unique identifier for the station

    Returns:
        Configured WeatherStation instance
    """
    return WeatherStation(
        station_id=station_id,
        name=f"{station_id.replace('-', ' ').title()} Weather Monitor",
        latitude=0.0,  # Default to equator
        longitude=0.0,
        altitude_meters=0.0,
    )


def create_default_controller(
    station: WeatherStation, data_dir: Path, reading_interval: float = 60.0
) -> WeatherStationController:
    """
    Create a default weather station controller.

    Args:
        station: WeatherStation configuration
        data_dir: Directory for storing sensor readings
        reading_interval: Interval between sensor readings in seconds

    Returns:
        Configured WeatherStationController instance
    """
    # Use MockSensor by default, can be replaced with real sensor
    sensor = MockSensor(sensor_id=f"{station.station_id}-sensor")

    return WeatherStationController(
        station=station,
        sensor=sensor,
        reading_interval=reading_interval,
        data_dir=data_dir,
        alert_thresholds={
            "high_temperature": 35.0,
            "low_temperature": 0.0,
            "high_wind_speed": 20.0,
        },
    )


def setup_alert_handlers(controller: WeatherStationController):
    """
    Set up default alert handling mechanisms.

    Args:
        controller: WeatherStationController instance
    """

    def print_alert(alert):
        """Simple console alert handler."""
        print(f"🚨 ALERT: {alert.message}")

    # Optional: Add more sophisticated alert handlers here
    # e.g., email_alert, sms_alert, logging_alert

    controller.add_alert_callback(print_alert)


async def run_weather_station(
    station_id: str = "default-station",
    data_dir: Path = Path("weather_data"),
    reading_interval: float = 60.0,
    verbose: bool = False,
):
    """
    Async function to run the weather station.

    Args:
        station_id: Unique identifier for the station
        data_dir: Directory for storing sensor readings
        reading_interval: Interval between sensor readings
        verbose: Enable verbose logging
    """
    # Setup logging
    logger = setup_logging(verbose)

    # Ensure data directory exists
    data_dir.mkdir(parents=True, exist_ok=True)

    # Create station and controller
    station = create_default_station(station_id)
    controller = create_default_controller(station, data_dir, reading_interval)

    # Setup alert handlers
    setup_alert_handlers(controller)

    logger.info(f"Starting weather station: {station.name}")

    try:
        await controller.start()
    except KeyboardInterrupt:
        logger.info("Weather station monitoring interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error in weather station: {e}")
    finally:
        controller.stop()
        logger.info("Weather station monitoring stopped")


def main():
    """
    CLI entry point for the weather station.
    Parses command-line arguments and runs the station.
    """
    parser = argparse.ArgumentParser(description="Weather Station Monitoring System")

    parser.add_argument(
        "--station-id",
        default="default-station",
        help="Unique identifier for the weather station",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("weather_data"),
        help="Directory for storing sensor readings",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=60.0,
        help="Interval between sensor readings in seconds",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Run the async main function
    asyncio.run(
        run_weather_station(
            station_id=args.station_id,
            data_dir=args.data_dir,
            reading_interval=args.interval,
            verbose=args.verbose,
        )
    )


if __name__ == "__main__":
    main()
