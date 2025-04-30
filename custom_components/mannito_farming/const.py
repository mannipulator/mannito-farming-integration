"""Constants for the Mannito Farming integration."""
from typing import Final

from homeassistant.const import Platform

# Domain
DOMAIN: Final = "mannito_farming"

# Platforms
PLATFORMS: Final = [Platform.SWITCH, Platform.FAN]

# Configuration
CONF_DEVICE_ID: Final = "device_id"
CONF_DEVICE_INFO: Final = "device_info"

# Default values
DEFAULT_NAME: Final = "Mannito Farming"
DEFAULT_UPDATE_INTERVAL: Final = 30

# Discovery
MDNS_SERVICE_TYPE: Final = "_mannito-farming._tcp.local."

# Device types
DEVICE_TYPE_VALVE: Final = "valve"
DEVICE_TYPE_FAN: Final = "fan"
DEVICE_TYPE_RELAY: Final = "relay"
DEVICE_TYPE_PUMP: Final = "pump"

# Component count
VALVE_COUNT: Final = 5
FAN_COUNT: Final = 10
RELAY_COUNT: Final = 8
PUMP_COUNT: Final = 4