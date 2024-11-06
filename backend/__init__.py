"""
Weather Station Monitoring System

A robust, type-safe, and extensible weather monitoring solution.

Key Components:
- Flexible sensor management
- Advanced data collection
- Intelligent alert system
- Type-safe data models

Modules:
- models: Data models and type definitions
- sensors: Sensor interfaces and implementations
- station: Weather station controller
"""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("weather-station")
except PackageNotFoundError:
    __version__ = "0.1.0-dev"

# Core models
from .models import SensorReading, WeatherStation, WeatherAlert

# Sensor interfaces and base classes
from .sensors import SensorInterface, BaseSensor, SensorError, MockSensor

# Station controller
from .station import WeatherStationController

# Type hints and protocols
from typing import Optional, List, Callable, Dict, Any

# Expose key components
__all__ = [
    # Models
    "SensorReading",
    "WeatherStation",
    "WeatherAlert",
    # Sensors
    "SensorInterface",
    "BaseSensor",
    "SensorError",
    "MockSensor",
    # Station
    "WeatherStationController",
    # Metadata
    "__version__",
]

# Package-level configuration
__package_name__ = "weather-station"
__author__ = "Weather Station Development Team"
__email__ = "support@weatherstation.dev"
__license__ = "MIT"

# Runtime configuration
_runtime_config: Dict[str, Any] = {
    "log_level": "INFO",
    "data_storage_path": None,
    "max_log_retention_days": 30,
}


def configure(
    log_level: Optional[str] = None,
    data_storage_path: Optional[str] = None,
    max_log_retention_days: Optional[int] = None,
) -> None:
    """
    Configure package-level settings.

    Args:
        log_level: Logging level (e.g., 'INFO', 'DEBUG')
        data_storage_path: Default path for data storage
        max_log_retention_days: Maximum days to retain log files
    """
    import logging

    if log_level:
        _runtime_config["log_level"] = log_level.upper()
        logging.getLogger().setLevel(getattr(logging, _runtime_config["log_level"]))

    if data_storage_path:
        _runtime_config["data_storage_path"] = data_storage_path

    if max_log_retention_days is not None:
        _runtime_config["max_log_retention_days"] = max(1, max_log_retention_days)


def get_config(key: str) -> Any:
    """
    Retrieve a runtime configuration value.

    Args:
        key: Configuration key to retrieve

    Returns:
        Configuration value or None if not set
    """
    return _runtime_config.get(key)


# Setup basic logging
def _setup_default_logging():
    import logging
    import sys

    logging.basicConfig(
        level=getattr(logging, _runtime_config["log_level"]),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            # Optional: Add file handler if needed
        ],
    )


# Initialize default logging
_setup_default_logging()
