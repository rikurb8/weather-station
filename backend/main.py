from typing import NoReturn
from backend.station import WeatherStation


def main() -> NoReturn:
    """Main entry point for the weather station"""
    station = WeatherStation()
    station.start()


if __name__ == "__main__":
    main()
