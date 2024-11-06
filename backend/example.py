import asyncio
import logging
from pathlib import Path

from .models import WeatherStation, WeatherAlert
from .sensors import MockSensor
from .station import WeatherStationController

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    # Create a test weather station
    station = WeatherStation(
        station_id="WS001",
        name="Backyard Weather Station",
        latitude=37.7749,
        longitude=-122.4194,
        altitude_meters=80.0,
    )

    # Initialize sensor
    sensor = MockSensor()

    # Setup alert callback
    def alert_handler(alert: WeatherAlert):
        logger.warning(f"Weather Alert: {alert.message}")

    # Initialize controller
    controller = WeatherStationController(
        station=station,
        sensor=sensor,
        reading_interval=5.0,  # Read every 5 seconds
        data_dir=Path("weather_data"),
    )

    # Add alert handler
    controller.add_alert_callback(alert_handler)

    # Run the station
    try:
        logger.info("Starting weather station monitoring...")
        await controller.start()
    except KeyboardInterrupt:
        logger.info("Stopping weather station monitoring...")
        controller.stop()


if __name__ == "__main__":
    asyncio.run(main())
