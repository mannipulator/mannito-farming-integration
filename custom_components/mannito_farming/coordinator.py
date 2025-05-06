"""Data update coordinator for Mannito Farming."""
from datetime import timedelta
import logging
from typing import Any, Dict, List, Optional

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import API, Device
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
            if not self._devices:
                # First run, discover all devices
                devices = await self.api.discover_devices()
                for device in devices:
                    self._devices[device.device_id] = device
            
            # Update all device states
            data = {}
            for device_id, device in self._devices.items():
                state_data = await self.api.get_device_state(device_id)
                data[device_id] = state_data
                
                # Update stored device state
                if "state" in state_data:
                    device.state = state_data["state"]
                if "speed" in state_data and device.speed is not None:
                    device.speed = state_data["speed"]
                
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
        success = await self.api.set_fan_speed(device_id, speed)
        if success and device_id in self._devices:
            device = self._devices[device_id]
            if device.speed is not None:  # Only update if it's a fan
                device.speed = speed
        return success

    async def get_device_info(self) -> Dict[str, Any]:
        """Fetch device information from the API.

        Returns:
            Dictionary containing device information.
        """
        try:
            return await self.api.get_device_info()
        except Exception as err:
            _LOGGER.error("Error fetching device info: %s", err)
            return {}

    async def discover_and_update_devices(self) -> None:
        """Discover devices and update the internal device list."""
        try:
            devices = await self.api.discover_devices()
            for device in devices:
                self._devices[device.device_id] = device
        except Exception as err:
            _LOGGER.error("Error discovering devices: %s", err)