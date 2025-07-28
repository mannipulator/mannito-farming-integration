"""API for the Mannito Farming integration."""
import logging
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from aiohttp import BasicAuth, ClientSession

_LOGGER = logging.getLogger(__name__)


class SlotSensorType(StrEnum):
    """Slot parameter sensor types."""

    @classmethod
    def parse(cls, value: str) -> "SlotSensorType":
        """
        Parse a string into a SlotSensorType enum.

        Args:
            value: The string to parse

        Returns:
            The corresponding SlotSensorType enum value

        Raises:
            ValueError: If the string doesn't match any SlotSensorType

        """
        try:
            return cls(value.upper())
        except ValueError:
            raise ValueError(f"'{value}' is not a valid SlotSensorType")

    AIR_TEMPERATURE = "AIR_TEMPERATURE"
    AIR_HUMIDITY = "AIR_HUMIDITY" 
    LEAF_TEMPERATURE = "LEAF_TEMPERATURE"
    OTHER = "OTHER"


class DeviceType(StrEnum):
    """Device types."""

    @classmethod
    def parse(cls, value: str) -> "DeviceType":
        """
        Parse a string into a DeviceType enum.

        Args:
            value: The string to parse

        Returns:
            The corresponding DeviceType enum value

        Raises:
            ValueError: If the string doesn't match any DeviceType

        """
        try:
            return cls(value.upper())
        except ValueError:
            raise ValueError(f"'{value}' is not a valid DeviceType")

    # Fan types
    EC_FAN = "EC_FAN"
    DC_FAN = "DC_FAN"
    AC_FAN = "AC_FAN"

    # Switch device types
    RELAY = "RELAY"
    HUMIDIFIER = "HUMIDIFIER"
    DEHUMIDIFIER = "DEHUMIDIFIER"
    PUMP = "PUMP"
    SOLENOID = "SOLENOID"
    AIR_PUMP = "AIR_PUMP"
    HEATER = "HEATER"
    COOLER = "COOLER"
    CO2_VALVE = "CO2_VALVE"
    HEAT_MAT = "HEAT_MAT"
    PERISTALTIC_PUMP = "PERISTALTIC_PUMP"
    MISTING_SYSTEM = "MISTING_SYSTEM"
    GENERIC_SOCKET = "GENERIC_SOCKET"
    
    # Light type
    LIGHT = "LIGHT"

    OTHER = "OTHER"

class SensorType(StrEnum):
    """Device types."""

    @classmethod
    def parse(cls, value: str) -> "SensorType":
        """
        Parse a string into a DeviceType enum.

        Args:
            value: The string to parse

        Returns:
            The corresponding DeviceType enum value

        Raises:
            ValueError: If the string doesn't match any DeviceType

        """
        try:
            return cls(value.upper())
        except ValueError:
            raise ValueError(f"'{value}' is not a valid DeviceType")

    HUMIDITY = "HUMIDITY"
    TEMPERATURE = "TEMPERATURE"
    CO2 = "CO2"
    WATERLEVEL = "WATERLEVEL"
    WATERFLOW = "WATERFLOW"
    LEAF_TEMPERATURE = "LEAF_TEMPERATURE"
    PH = "PH"
    EC = "EC"
    UPTIME = "UPTIME"
    OTHER = "OTHER"

class PluginType(StrEnum):
    """Plugin types."""

    @classmethod
    def parse(cls, value: str) -> "PluginType":
        """
        Parse a string into a PluginType enum.
        
        Args:
            value: The string to parse
            
        Returns:
            The corresponding PluginType enum value
            
        Raises:
            ValueError: If the string doesn't match any PluginType

        """
        try:
            return cls(value.upper())
        except ValueError:
            raise ValueError(f"'{value}' is not a valid PluginType")

    LIGHT_SCHEDULER = "LIGHT_SCHEDULER"
    DEVICE_SCHEDULER = "DEVICE_SCHEDULER"
    TEMPERATURE_CONTROLLER = "TEMPERATURE_CONTROLLER"
    WIND_SIMULATOR = "WIND_SIMULATOR"
    WATER_CONTROLLER = "WATER_CONTROLLER"
    OTHER = "OTHER"

@dataclass
class Plugin:
    """Plugin information."""

    plugin_id: str
    plugin_unique_id: str
    plugin_type: PluginType
    name: str
    state: bool = False
    available: bool = True

@dataclass
class Device:
    """Device information."""

    device_id: str
    device_unique_id: str
    device_type: DeviceType
    name: str
    state: bool = False
    powerlevel: int | None = None
    powerlevel_supported: bool = False
    max_powerlevel: int = 255
    is_enabled: bool = True
    is_initialized: bool = True
    available: bool = True

@dataclass
class Sensor:
    """Sensor information."""

    sensor_id: str
    sensor_unique_id: str
    sensor_type: SensorType
    name: str
    sensor_value: str | float | int = ""
    unit: str = ""
    is_valid: bool = True
    is_enabled: bool = True
    is_initialized: bool = True
    available: bool = True

@dataclass
class SlotParameter:
    """Slot parameter information."""

    slot_name: str
    parameter: SlotSensorType
    parameter_id: str  # Unique ID like "slot_default_air_temperature"
    parameter_unique_id: str
    name: str  # Display name like "Default Slot - Air Temperature"
    value: float | int = 0
    available: bool = True

class APIAuthError(Exception):
    """Exception for authentication errors."""


class APIConnectionError(Exception):
    """Exception for connection errors."""


class API:
    """API class to handle communication with the Mannito Farming controller."""

    def __init__(self, host: str, username: str, password: str, session: ClientSession) -> None:
        """
        Initialize the API client.
        
        Args:
            host: IP address or hostname of the controller
            username: Authentication username
            password: Authentication password
            session: aiohttp ClientSession

        """
        self.host = host
        self.auth = BasicAuth(username, password) if username and password else None
        self.session = session
        self.connected = False
        self.device_info = None

    async def async_test_connection(self) -> bool:
        """
        Test the connection to the controller.
        
        Returns:
            True if connection is successful, False otherwise

        """
        try:
            _LOGGER.info("Testing mannito connection")
            device_info = await self.fetch_device_config()
            self.connected = bool(device_info)
            self.device_info = device_info
            return self.connected
        except Exception as err:
            _LOGGER.error("Error testing connection: %s", err)
            self.connected = False
            return False

    async def set_device_state(self, component_name: str, state: bool) -> bool:
        """
        Set the state of a device.
        
        Args:
            component_name: The name/ID of the component
            state: The state to set (True=on, False=off)
            
        Returns:
            True if successful, False otherwise

        """
        stateAsString = "on" if state else "off"

        url = f"http://{self.host}/api/device/{component_name}/{stateAsString}"
        try:
            async with self.session.post(url, auth=self.auth) as response:
                return response.status == 200
        except Exception as err:
            _LOGGER.error("Error setting state for %s: %s", component_name, err)
            return False

    async def set_fan_speed(self, component_name: str, speed: int) -> bool:
        """
        Set the speed of a fan.
        
        Args:
            component_name: The name/ID of the fan
            speed: Speed value (0-100)
            
        Returns:
            True if successful, False otherwise

        """
        _LOGGER.debug("Setting fan speed for %s to %d", component_name, speed)

        url = f"http://{self.host}/api/device/{component_name}/value/{int(speed)}"
        _LOGGER.debug("Setting fan speed URL: %s", url)
        try:
            async with self.session.post(url, auth=self.auth) as response:
                return response.status == 200
        except Exception as err:
            _LOGGER.error("Error setting speed for %s: %s", component_name, err)
            return False


    async def get_plugin_state(self, plugin_name: str) -> dict[str, Any]:
        """
        Get the state of a device.
        
        Args:
            plugin_name: The name/ID of the plugin
            
        Returns:
            Dictionary with plugin state information

        """
        url = f"http://{self.host}/api/plugin/{plugin_name}"
        try:
            async with self.session.get(url, auth=self.auth) as response:
                if response.status == 200:
                    return await response.json()
                return {}
        except Exception as err:
            _LOGGER.error("Error getting state for %s: %s", plugin_name, err)
            raise APIConnectionError(f"Error getting state for {plugin_name}: {err}")


    async def get_sensor_state(self, component_name: str) -> dict[str, Any]:
        """
        Get the state of a device.
        
        Args:
            component_name: The name/ID of the component
            
        Returns:
            Dictionary with device state information

        """
        url = f"http://{self.host}/api/sensor/{component_name}"
        try:
            async with self.session.get(url, auth=self.auth) as response:
                if response.status == 200:
                    return await response.json()
                return {}
        except Exception as err:
            _LOGGER.error("Error getting state for %s: %s", component_name, err)
            raise APIConnectionError(f"Error getting state for {component_name}: {err}")

    async def get_all_device_states(self) -> dict[str, Any]:
        """
        Get the states of all devices using the bulk endpoint.
        
        Returns:
            Dictionary with all device states from /api/components/summary

        """
        url = f"http://{self.host}/api/components/summary"
        try:
            async with self.session.get(url, auth=self.auth) as response:
                if response.status == 200:
                    return await response.json()
                return {}
        except Exception as err:
            _LOGGER.error("Error getting all device states: %s", err)
            raise APIConnectionError(f"Error getting all device states: {err}")

    async def get_system_status(self) -> dict[str, Any]:
        """
        Get system status including uptime.
        
        Returns:
            Dictionary with system status information from /api/system/status

        """
        url = f"http://{self.host}/api/system/status"
        try:
            async with self.session.get(url, auth=self.auth) as response:
                if response.status == 200:
                    return await response.json()
                return {}
        except Exception as err:
            _LOGGER.error("Error getting system status: %s", err)
            raise APIConnectionError(f"Error getting system status: {err}")

    async def get_device_state(self, component_name: str) -> dict[str, Any]:
        """
        Get the state of a device.
        
        Args:
            component_name: The name/ID of the component
            
        Returns:
            Dictionary with device state information

        """
        url = f"http://{self.host}/api/device/{component_name}"
        try:
            async with self.session.get(url, auth=self.auth) as response:
                if response.status == 200:
                    return await response.json()
                return {}
        except Exception as err:
            _LOGGER.error("Error getting state for %s: %s", component_name, err)
            raise APIConnectionError(f"Error getting state for {component_name}: {err}")

    async def fetch_device_config(self) -> dict[str, Any]:
        """
        Fetch the device configuration from the API.
        
        Returns:
            Dictionary with device configuration
            
        Raises:
            APIConnectionError: If connection fails

        """
        url = f"http://{self.host}/api/components/summary"
        try:
            async with self.session.get(url, auth=self.auth) as response:
                if response.status != 200:
                    raise APIConnectionError(f"Failed to fetch device config, status code: {response.status}")
                return await response.json()
        except Exception as err:
            _LOGGER.error("Error fetching device configuration: %s", err)
            raise APIConnectionError("Failed to fetch device configuration")

    async def discover_devices(self) -> list[Device]:
        """
        Discover available devices.
        
        Returns:
            List of discovered devices

        """
        devices = []
        try:
            config = await self.fetch_device_config()
            deviceList = config.get("devices", [])

            for device in deviceList:
                deviceid = device.get("id")
                device_type_str = device.get("device_type", "OTHER")
                try:
                    device_type = DeviceType.parse(device_type_str)
                except ValueError:
                    _LOGGER.warning("Unknown device type: %s, using OTHER", device_type_str)
                    device_type = DeviceType.OTHER

                devices.append(Device(
                    device_id=deviceid,
                    device_unique_id=f"{self.host}_{deviceid}",
                    device_type=device_type,
                    name=device.get("name"),
                    state=device.get("state", False),
                    powerlevel=device.get("powerlevel"),
                    powerlevel_supported=device.get("powerlevel_supported", False),
                    max_powerlevel=device.get("max_powerlevel", 255),
                    is_enabled=device.get("is_enabled", True),
                    is_initialized=device.get("is_initialized", True),
                    available=device.get("is_enabled", True) and device.get("is_initialized", True),
                ))

            return devices
        except Exception as err:
            _LOGGER.error("Error discovering devices: %s", err)
            raise APIConnectionError("Error discovering devices")


    async def discover_sensors(self) -> list[Sensor]:
        """
        Discover available sensors.
        
        Returns:
            List of discovered sensors

        """
        sensors = []
        try:
            config = await self.fetch_device_config()
            sensorList = config.get("sensors", [])

            for sensor in sensorList:
                sensorid = sensor.get("id")
                sensor_type_str = sensor.get("sensor_type", "OTHER")
                try:
                    sensor_type = SensorType.parse(sensor_type_str)
                except ValueError:
                    _LOGGER.warning("Unknown sensor type: %s, using OTHER", sensor_type_str)
                    sensor_type = SensorType.OTHER

                sensors.append(Sensor(
                    sensor_id=sensorid,
                    sensor_unique_id=f"{self.host}_{sensorid}",
                    sensor_type=sensor_type,
                    name=sensor.get("name"),
                    sensor_value=sensor.get("sensor_value", ""),
                    unit=sensor.get("unit", ""),
                    is_valid=sensor.get("is_valid", True),
                    is_enabled=sensor.get("is_enabled", True),
                    is_initialized=sensor.get("is_initialized", True),
                    available=sensor.get("is_enabled", True) and sensor.get("is_initialized", True),
                ))

            # Add system uptime sensor
            sensors.append(Sensor(
                sensor_id="system_uptime",
                sensor_unique_id=f"{self.host}_system_uptime",
                sensor_type=SensorType.UPTIME,
                name="System Uptime",
                sensor_value=config.get("uptime", 0),
                unit="s",
            ))

            return sensors
        except Exception as err:
            _LOGGER.error("Error discovering sensors: %s", err)
            return []

    async def discover_slot_parameters(self) -> list[SlotParameter]:
        """
        Discover available slot parameters from the /api/components/summary endpoint.
        
        Returns:
            List of discovered slot parameters

        """
        slot_parameters = []
        try:
            # Use the bulk endpoint to get slot data
            bulk_data = await self.get_all_device_states()
            slots_data = bulk_data.get("slots", [])

            for slot_index, slot in enumerate(slots_data):
                slot_name = slot.get("name", "Unknown Slot")
                parameters = slot.get("parameters", [])
                
                for param in parameters:
                    parameter_name = param.get("parameter", "OTHER")
                    parameter_value = param.get("value", 0)
                    
                    try:
                        slot_sensor_type = SlotSensorType.parse(parameter_name)
                    except ValueError:
                        _LOGGER.warning("Unknown slot parameter type: %s, using OTHER", parameter_name)
                        slot_sensor_type = SlotSensorType.OTHER
                    
                    # Create unique IDs - include slot index to handle duplicate slot names
                    slot_clean = slot_name.lower().replace(" ", "_")
                    param_clean = parameter_name.lower()
                    parameter_id = f"slot_{slot_clean}_{slot_index}_{param_clean}"
                    
                    slot_parameters.append(SlotParameter(
                        slot_name=slot_name,
                        parameter=slot_sensor_type,
                        parameter_id=parameter_id,
                        parameter_unique_id=f"{self.host}_{parameter_id}",
                        name=f"{slot_name} {slot_index + 1} - {parameter_name.replace('_', ' ').title()}",
                        value=parameter_value,
                    ))

            return slot_parameters
        except Exception as err:
            _LOGGER.error("Error discovering slot parameters: %s", err)
            return []


    async def get_device_info(self) -> dict[str, Any]:
        """Return device information from the cached configuration data."""
        if not self.device_info:
            _LOGGER.info("Device configuration not loaded. Call fetch_device_config first.")
            self.device_info = await self.fetch_device_config()
            # return {}

        _LOGGER.info("Found device-info: %s", self.device_info)

        return {
            "model": "Mannito Farming Controller",
            "sw_version": self.device_info.get("version", "Unknown Version"),
            "hw_version": self.device_info.get("hardware_version", "Unknown Version"),
            "serial_number": self.device_info.get("serialnumber", "Unknown Serial"),
            "manufacturer": "Mannito",
            "uptime": self.device_info.get("uptime", "Unknown Uptime"),
            "ip_address": self.device_info.get("ip_address", self.host),
            "configuration_url": f"http://{self.host}",
            "name": f"Mannito Farming {self.host}",
        }
