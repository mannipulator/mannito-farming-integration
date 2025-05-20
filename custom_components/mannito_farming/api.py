"""API for the Mannito Farming integration."""
import asyncio
import logging
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Dict, List, Optional

from aiohttp import ClientSession, BasicAuth

_LOGGER = logging.getLogger(__name__)




class DeviceType(StrEnum):
    """Device types."""
    
    @classmethod
    def parse(cls, value: str) -> "DeviceType":
        """Parse a string into a DeviceType enum.
        
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
    FAN = "FAN"
    RELAY = "RELAY"
    SOLENOID = "SOLENOID"
    PUMP = "PUMP"
    OTHER = "OTHER"

class SensorType(StrEnum):
    """Device types."""

    @classmethod
    def parse(cls, value: str) -> "SensorType":
        """Parse a string into a DeviceType enum.
        
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
    LEAF_TEMPERATURE="LEAF_TEMPERATURE"
    PH = "PH"
    EC = "EC"
    OTHER = "OTHER"

class PluginType(StrEnum):
    """Plugin types."""
    
    @classmethod
    def parse(cls, value: str) -> "PluginType":
        """Parse a string into a PluginType enum.
        
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
    speed: Optional[int] = None
    available: bool = True

@dataclass
class Sensor:
    """Sensor information."""
    sensor_id: str
    sensor_unique_id: str
    sensor_type: SensorType
    name: str
    state_value: str = ""
    available: bool = True

class APIAuthError(Exception):
    """Exception for authentication errors."""


class APIConnectionError(Exception):
    """Exception for connection errors."""


class API:
    """API class to handle communication with the Mannito Farming controller."""

    def __init__(self, host: str, username: str, password: str, session: ClientSession) -> None:
        """Initialize the API client.
        
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
        """Test the connection to the controller.
        
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
        """Set the state of a device.
        
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
        """Set the speed of a fan.
        
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


    async def get_plugin_state(self, plugin_name: str) -> Dict[str, Any]:
        """Get the state of a device.
        
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


    async def get_sensor_state(self, component_name: str) -> Dict[str, Any]:
        """Get the state of a device.
        
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

    async def get_device_state(self, component_name: str) -> Dict[str, Any]:
        """Get the state of a device.
        
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

    async def fetch_device_config(self) -> Dict[str, Any]:
        """Fetch the device configuration from the API.
        
        Returns:
            Dictionary with device configuration
            
        Raises:
            APIConnectionError: If connection fails
        """
        url = f"http://{self.host}/api/config"
        try:
            async with self.session.get(url, auth=self.auth) as response:
                if response.status != 200:
                    raise APIConnectionError(f"Failed to fetch device config, status code: {response.status}")
                return await response.json()
        except Exception as err:
            _LOGGER.error("Error fetching device configuration: %s", err)
            raise APIConnectionError("Failed to fetch device configuration")

    async def discover_devices(self) -> List[Device]:
        """Discover available devices.
        
        Returns:
            List of discovered devices
        """
        devices = []
        sensors = []
        plugins = []
        try:
            config = await self.fetch_device_config()
            deviceList = config.get("devices", [])
            
            for device in deviceList:
                deviceid = device.get("device_id")
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
                    name=device.get("device_name"),
                ))
                
            return devices
        except Exception as err:
            _LOGGER.error("Error discovering devices: %s", err)
            raise APIConnectionError("Error discovering devices")


    async def discover_sensors(self) -> List[Sensor]:
        """Discover available sensors.
        
        Returns:
            List of discovered sensors
        """
    
        sensors = []
        try:
            config = await self.fetch_device_config()            
            sensorList = config.get("sensors", [])
            
            for sensor in sensorList:
                sensorid = sensor.get("sensor_id")
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
                    name=sensor.get("sensor_name"),
                ))
                
            return sensors
        except Exception as err:
            _LOGGER.error("Error discovering devices: %s", err)
            return []



    async def get_device_info(self) -> Dict[str, Any]:
        """Return device information from the cached configuration data."""
        if not self.device_info:
            _LOGGER.info("Device configuration not loaded. Call fetch_device_config first.")
            self.device_info = await self.fetch_device_config()
            # return {}

        _LOGGER.info("Found device-info: %s", self.device_info)

        return {
            "model": self.device_info.get("model", "Unknown Model"),
            "sw_version": self.device_info.get("firmware_version", "Unknown Version"),
            "hw_version": self.device_info.get("hardware_version", "Unknown Version"),
            "serial_number": self.device_info.get("serial_number", "Unknown Serial"),
            "manufacturer": self.device_info.get("manufacturer", "Mannito"),
            "uptime": self.device_info.get("uptime", "Unknown Uptime"),
            "ip_address": self.device_info.get("ip_address", self.host),
            "configuration_url": f"http://{self.host}",
            "name": self.device_info.get("name", f"Mannito Farming {self.host}"),
        }
