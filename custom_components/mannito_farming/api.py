"""API Placeholder.

You should create your api seperately and have it hosted on PYPI.  This is included here for the sole purpose
of making this example code executable.
"""

import asyncio
from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
import logging
from random import choice, randrange

from .const import API_BASE_URL, API_DEVICE_STATUS, API_SENSOR_UPDATE, API_DEVICE_SET_STATE



_LOGGER = logging.getLogger(__name__)


class DeviceType(StrEnum):
    """Device types."""

    TEMP_SENSOR = "temp_sensor"
    DOOR_SENSOR = "door_sensor"
    OTHER = "other"


DEVICES = [
    {"id": 1, "type": DeviceType.TEMP_SENSOR},
    {"id": 2, "type": DeviceType.TEMP_SENSOR},
    {"id": 3, "type": DeviceType.TEMP_SENSOR},
    {"id": 4, "type": DeviceType.TEMP_SENSOR},
    {"id": 1, "type": DeviceType.DOOR_SENSOR},
    {"id": 2, "type": DeviceType.DOOR_SENSOR},
    {"id": 3, "type": DeviceType.DOOR_SENSOR},
    {"id": 4, "type": DeviceType.DOOR_SENSOR},
]


@dataclass
class Device:
    """API device."""

    device_id: int
    device_unique_id: str
    device_type: DeviceType
    name: str
    state: int | bool



class DeviceApi():
    """API for devices."""

    def __init__(self, host: str, user: str, pwd: str) -> None:
        """Initialise."""
        self.host = host
        self.user = user
        self.password = pwd
        self.connected: bool = False

    async def get_device(self, device_id: int) -> Device:
        """Get a device."""
        """ Load all relevant stuff from the API """
        
        return next((device for device in self.devices if device.device_id == device_id), None)


    async def async_set_device_state(self, device_id: str, command: str) -> bool:
        """Set device state."""
        url = API_DEVICE_SET_STATE.format(host=self.host, device_id=device_id, command=command)
        try:
            async with self.session.post(
                url
            ) as response:
                return response.status == 200
        except Exception as err:
            _LOGGER.error("Error setting device state: %s", err)
            return False


    async def async_get_device_state(self, device_id: str) -> dict[str, Any]:
        """Get device state."""
        url = API_DEVICE_STATUS.format(host=self.host, device_id=device_id)
        try:
            async with self.session.get(
                url,
            ) as response:
                if response.status == 200:
                    return await response.json()
                return {}
        except Exception as err:
            _LOGGER.error("Error getting device state: %s", err)
            return {}


    async def update_device(self, device_id: int) -> Device:
        """Update a device."""
        await asyncio.sleep(1)
        device = await self.get_device(device_id)
        if device:
            device.state = choice([True, False]) if device.device_type == DeviceType.DOOR_SENSOR else randrange(0, 30)
            return device
        return None


class APIAuthError(Exception):
    """Exception class for auth error."""


class APIConnectionError(Exception):
    """Exception class for connection error."""
