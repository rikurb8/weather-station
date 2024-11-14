"""
Weather Station Monitoring System with Randy Marsh interface

A fun and interactive weather monitoring solution featuring South Park's Randy Marsh.
"""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("weather-station")
except PackageNotFoundError:
    __version__ = "0.1.0-dev"

from .station import WeatherStation

__all__ = [
    "WeatherStation",
    "__version__",
]

# Package-level configuration
__package_name__ = "weather-station"
__author__ = "Weather Station Development Team"
__license__ = "MIT"
