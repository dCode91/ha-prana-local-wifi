"""Constants for the Prana Recuperator integration."""
from typing import Final

DOMAIN: Final = "prana_recuperator"

# Configuration
CONF_HOST: Final = "host"
CONF_NAME: Final = "name"

# API Constants
DEFAULT_PORT: Final = 80
DEFAULT_TIMEOUT: Final = 10

# Device attributes
ATTR_EXTRACT_SPEED: Final = "extract_speed"
ATTR_SUPPLY_SPEED: Final = "supply_speed"
ATTR_BOUNDED_SPEED: Final = "bounded_speed"
ATTR_EXTRACT_IS_ON: Final = "extract_is_on"
ATTR_SUPPLY_IS_ON: Final = "supply_is_on"
ATTR_BOUNDED_IS_ON: Final = "bounded_is_on"
ATTR_MAX_SPEED: Final = "max_speed"
ATTR_BOUND: Final = "bound"
ATTR_HEATER: Final = "heater"
ATTR_AUTO: Final = "auto"
ATTR_AUTO_PLUS: Final = "auto_plus"
ATTR_WINTER: Final = "winter"
ATTR_NIGHT: Final = "night"
ATTR_BOOST: Final = "boost"
ATTR_BRIGHTNESS: Final = "brightness"

# Sensor attributes
ATTR_INSIDE_TEMPERATURE: Final = "inside_temperature"
ATTR_INSIDE_TEMPERATURE_2: Final = "inside_temperature_2"
ATTR_OUTSIDE_TEMPERATURE: Final = "outside_temperature"
ATTR_OUTSIDE_TEMPERATURE_2: Final = "outside_temperature_2"
ATTR_HUMIDITY: Final = "humidity"
ATTR_CO2: Final = "co2"
ATTR_VOC: Final = "voc"
ATTR_AIR_PRESSURE: Final = "air_pressure"

# Fan types
FAN_TYPE_SUPPLY: Final = "supply"
FAN_TYPE_EXTRACT: Final = "extract"
FAN_TYPE_BOUNDED: Final = "bounded"

# Switch types
SWITCH_TYPE_BOUND: Final = "bound"
SWITCH_TYPE_HEATER: Final = "heater"
SWITCH_TYPE_NIGHT: Final = "night"
SWITCH_TYPE_BOOST: Final = "boost"
SWITCH_TYPE_AUTO: Final = "auto"
SWITCH_TYPE_AUTO_PLUS: Final = "auto_plus"
SWITCH_TYPE_WINTER: Final = "winter"

# Brightness levels mapping
BRIGHTNESS_LEVELS: Final = {
    0: 0,    # Screen off
    1: 1,    # Level 1 (minimum)
    2: 2,    # Level 2
    3: 4,    # Level 3
    4: 8,    # Level 4
    5: 16,   # Level 5
    6: 32,   # Level 6 (maximum)
}

BRIGHTNESS_VALUES: Final = {v: k for k, v in BRIGHTNESS_LEVELS.items()}

# Speed constants
SPEED_STEP: Final = 10
MIN_SPEED: Final = 10
MAX_SPEED: Final = 60
SPEED_COUNT: Final = 6

# Service names
SERVICE_SET_BRIGHTNESS: Final = "set_brightness"
