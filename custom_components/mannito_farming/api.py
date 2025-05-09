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
            return cls(value.capitalize())
        except ValueError:
            raise ValueError(f"'{value}' is not a valid DeviceType")
    FAN = "FAN"
    RELAY = "RELAY"
    SOLENOID = "SOLENOID"
    PUMP = "PUMP"
    OTHER = "ÔTHER"

class SensorType(StrEnum):
    """Device types."""
    HUMIDITY = "humidity"
    TEMPERATURE = "temperature"
    CO2 = "co2"
    WATERLEVEL = "waterlevel"
    WATERFLOW = "waterflow"
    LEAF_TEMPERATURE="leaf_temperature"
    PH = "ph"
    EC = "ec"
    OTHER = "other"



@dataclass
class Device:
    """Device information."""
    device_id: str
    device_unique_id: str
    device_type: DeviceType
    name: str
    state: bool = False
    speed: Optional[int] = None

@dataclass
class Sensor:
    """Sensor information."""
    sensor_id: str
    sensor_unique_id: str
    sensor_type: SensorType
    name: str
    state_value: str = ""

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
        url = f"http://{self.host}/api/device/{component_name}/speed/{speed}"
        try:
            async with self.session.post(url, auth=self.auth) as response:
                return response.status == 200
        except Exception as err:
            _LOGGER.error("Error setting speed for %s: %s", component_name, err)
            return False


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
            return {}

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
            return {}

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
        try:
            config = await self.fetch_device_config()
            deviceList=config.get("devices"),
            
            for device in deviceList:
                deviceid=device.get("device_id")
                devices.append(Device(
                    device_id=deviceid,
                    device_unique_id=f"{self.host}_{deviceid}",
                    device_type=DeviceType.SOLENOID,
                    name=device.get("device_name"),
                ))

            # Process valves (5x)
            # for i in range(1, 6):
                
            #     devices.append(Device(
            #         device_id=device_id,
            #         device_unique_id=f"{self.host}_{device_id}",
            #         device_type=DeviceType.SOLENOID,
            #         name=f"Valve {i}"
            #     ))
            
            # # Process fans (10x)
            # for i in range(1, 11):
            #     device_id = f"FAN{i}"
            #     devices.append(Device(
            #         device_id=device_id,
            #         device_unique_id=f"{self.host}_{device_id}",
            #         device_type=DeviceType.FAN,
            #         name=f"Fan {i}",
            #         speed=0
            #     ))
            
            # # Process relays (8x)
            # for i in range(1, 9):
            #     device_id = f"RELAY{i}"
            #     devices.append(Device(
            #         device_id=device_id,
            #         device_unique_id=f"{self.host}_{device_id}",
            #         device_type=DeviceType.RELAY,
            #         name=f"Relay {i}"
            #     ))
            
            # # Process pumps (4x)
            # for i in range(1, 5):
            #     device_id = f"PUMP{i}"
            #     devices.append(Device(
            #         device_id=device_id,
            #         device_unique_id=f"{self.host}_{device_id}",
            #         device_type=DeviceType.PUMP,
            #         name=f"Pump {i}"
            #     ))
                
            return devices
        except Exception as err:
            _LOGGER.error("Error discovering devices: %s", err)
            return []



    async def discover_sensors(self) -> List[Sensor]:
        """Discover available sensors.
        
        Returns:
            List of discovered sensors
        """
    
        sensors = []
        try:
            config = await self.fetch_device_config()
            
            # Process temp sensors (4x)
            for i in range(1, 2):
                sensor_id = f"TEMP{i}"
                sensors.append(Sensor(
                    sensor_id=sensor_id,
                    sensor_unique_id=f"{self.host}_{sensor_id}",
                    sensor_type=SensorType.HUMIDITY,
                    name=f"Temperatur Sensor {i}"
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

# Example of what the `device_info` object might contain:
# {
#     "model": "Farming Controller v1.0",
#     "firmware_version": "1.2.3",
#     "serial_number": "12345-ABCDE",
#     "manufacturer": "Mannito",
#     "uptime": "72 hours",
#     "ip_address": "192.168.1.100"
# }
