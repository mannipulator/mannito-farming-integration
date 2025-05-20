"""Data update coordinator for Mannito Farming."""
from datetime import timedelta
import logging
from typing import Any, Dict, List, Optional

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.entity import DeviceInfo
from .api import API, Device, Sensor
from .const import DEFAULT_UPDATE_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class MannitoFarmingDataUpdateCoordinator(DataUpdateCoordinator[Dict[str, Any]]):
    """Class to manage fetching data from the Mannito Farming controller."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize the coordinator.
        
        Args:
            hass: Home Assistant instance
            config_entry: Config entry containing configuration data
        """
        self.hass = hass
        self.config_entry = config_entry
        self.host = config_entry.data[CONF_HOST]
        self.username = config_entry.data.get(CONF_USERNAME)
        self.password = config_entry.data.get(CONF_PASSWORD)
        self.session = async_get_clientsession(hass)
        self.api = API(self.host, self.username, self.password, self.session)
        self._devices: Dict[str, Device] = {}
        self._sensors: Dict[str, Sensor] = {}
        self.device_info: Dict[str, Any] = {}
        
        _LOGGER.debug("Initializing coordinator for host: %s", self.host)
        
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{self.host}",
            update_interval=timedelta(seconds=DEFAULT_UPDATE_INTERVAL),
        )

    async def _async_update_data(self) -> Dict[str, Any]:
        """Fetch data from the API.
        
        Returns:
            Dictionary with device states
        
        Raises:
            UpdateFailed: If the update fails
        """
        try:
            _LOGGER.info("Starting _async_update_data")
            # Load device info if not already loaded
            if not self.device_info:
                
                self.device_info = await self.api.get_device_info()
                _LOGGER.debug("Loaded Device info from api: %s", self.device_info)
                
            if not self._devices:
                # First run, discover all devices
                devices = await self.api.discover_devices()
                for device in devices:
                    self._devices[device.device_id] = device

            if not self._sensors:
                # First run, discover all devices
                sensors = await self.api.discover_sensors()
                for sensor in sensors:
                    self._sensors[sensor.sensor_id] = sensor            # Update all device states
            data = {}
            for device_id, device in self._devices.items():
                try:
                    state_data = await self.api.get_device_state(device_id)
                    data[device_id] = state_data
                    
                    # If we got a response with data, the device is available
                    if state_data:
                        device.available = True
                        # Update stored device state
                        if "state" in state_data:
                            device.state = state_data["state"]
                        if "speed" in state_data and device.speed is not None:
                            device.speed = state_data["speed"]
                    else:
                        # Empty response means the device is not available
                        device.available = False
                        _LOGGER.warning("Device %s is not responding, marking as unavailable", device_id)
                except Exception as err:
                    # If an error occurred, the device is not available
                    device.available = False
                    _LOGGER.error("Error updating device %s: %s", device_id, err)
                    raise UpdateFailed(f"Error updating data: {err}")
                
            for sensor_id, sensor in self._sensors.items():
                try:
                    sensor_data = await self.api.get_sensor_state(sensor_id)
                    data[sensor_id] = sensor_data
                    
                    _LOGGER.debug("Mannito-Sensor data: %s", sensor_data)
                    
                    # If we got a valid response, the sensor is available
                    if sensor_data:
                        sensor.available = True
                        # Update stored sensor value
                        if "value" in sensor_data:
                            if "is_valid" in sensor_data and sensor_data["is_valid"]:
                                sensor.state_value = sensor_data["value"]
                    else:
                        # Empty response means the sensor is not available
                        sensor.available = False
                        _LOGGER.warning("Sensor %s is not responding, marking as unavailable", sensor_id)
                except Exception as err:
                    # If an error occurred, the sensor is not available
                    sensor.available = False
                    _LOGGER.error("Error updating sensor %s: %s", sensor_id, err)
                    raise UpdateFailed(f"Error updating data: {err}")

            return data
        except Exception as err:
            raise UpdateFailed(f"Error updating data: {err}")

    async def get_device(self, device_id: str) -> Optional[Device]:
        """Get device information.
        
        Args:
            device_id: Device ID to get
            
        Returns:
            Device object if found, None otherwise
        """
        return self._devices.get(device_id)

    async def get_all_devices(self) -> List[Device]:
        """Get all devices.
        
        Returns:
            List of all devices
        """
        return list(self._devices.values())
    
    async def get_sensor(self, sensor_id: str) -> Optional[Sensor]:
        """Get sensor information.
        
        Args:
            sensor_id: Sensor ID to get
            
        Returns:
            Sensor object if found, None otherwise
        """
        return self._sensors.get(sensor_id)

    async def get_all_sensors(self) -> List[Sensor]:
        """Get all sensors.
        
        Returns:
            List of all sensors
        """
        return list(self._sensors.values())
    
    async def async_set_device_state(self, device_id: str, state: bool) -> bool:
        """Set the state of a device.
        
        Args:
            device_id: Device ID to control
            state: State to set (True=on, False=off)
            
        Returns:
            True if successful, False otherwise
        """
        success = await self.api.set_device_state(device_id, state)
        if success and device_id in self._devices:
            self._devices[device_id].state = state
        return success

    async def async_set_fan_speed(self, device_id: str, speed: int) -> bool:
        """Set the speed of a fan.
        
        Args:
            device_id: Fan ID to control
            speed: Speed to set (0-100)
            
        Returns:
            True if successful, False otherwise
        """

        _LOGGER.debug("Setting fan speed for device %s to %d", device_id, speed)

        success = await self.api.set_fan_speed(device_id, speed)
        if success and device_id in self._devices:
            device = self._devices[device_id]
            if device.speed is not None:  # Only update if it's a fan
                device.speed = speed
        return success

    def get_device_info(self) -> DeviceInfo:
        """Fetch device information from the API.

        Returns:
            Dictionary containing device information.
        """
        api_device_info = self.device_info or {}
        if not self.device_info:
            # If device_info is not already loaded, fetch it
            api_device_info = self.api.fetch_device_config()
            _LOGGER.debug("Fetched Device info from api: %s", api_device_info)

        return DeviceInfo(
            identifiers={(DOMAIN, self.host)},
            name=api_device_info.get("name", f"Mannito Farming {self.host}"),
            manufacturer=api_device_info.get("manufacturer", "Mannito Farming"),
            model=api_device_info.get("model", "Mannito Device"),
            sw_version=api_device_info.get("sw_version", "Unknown"),
            hw_version=api_device_info.get("hw_version", "Unknown"),
            serial_number=api_device_info.get("serial_number", "Unknown"),
            configuration_url=api_device_info.get("configuration_url", f"http://{self.host}"),
        )


    async def discover_and_update_devices(self) -> None:
        """Discover devices and update the internal device list."""
        try:
            devices = await self.api.discover_devices()
            for device in devices:
                self._devices[device.device_id] = device

            sensors = await self.api.discover_sensors()
            for sensor in sensors:
                self._sensors[sensor.sensor_id] = sensor

        except Exception as err:
            _LOGGER.error("Error discovering devices and sensors: %s", err)