"""Constants for the Mannito Farming integration."""
from homeassistant.const import Platform

DOMAIN = "mannito_farming"
PLATFORMS = [Platform.SWITCH, Platform.LIGHT, Platform.SENSOR, Platform.FAN]

CONF_DEVICE_ID = "device_id"
CONF_SENSORS = "sensors"

# API endpoints
API_BASE_URL = "http://{host}:80/api"
API_DEVICE_STATUS = API_BASE_URL + "/device/{device_id}"
API_DEVICE_CONTROL = API_BASE_URL + "/device/{device_id}/{command}"
API_SENSOR_UPDATE = API_BASE_URL + "/sensor"

# Device types
DEVICE_TYPE_VALVE = "valve"
DEVICE_TYPE_PUMP = "pump"
DEVICE_TYPE_FAN = "fan"
DEVICE_TYPE_LIGHT = "light"
DEVICE_TYPE_SOCKET = "socket"
DEVICE_TYPE_SENSOR = "sensor"

# Default names
DEFAULT_NAME = "Mannito Farming" 