"""Data update coordinator for Mannito Farming."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.const import CONF_SENSORS

from .const import API_BASE_URL, API_DEVICE_STATUS, API_SENSOR_UPDATE

_LOGGER = logging.getLogger(__name__)

class MannitoFarmingDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the Mannito Farming controller."""

    def __init__(
        self,
        hass: HomeAssistant,
        host: str,
        username: str,
        password: str,
        sensors: list[str] | None = None,
    ) -> None:
        """Initialize the data updater."""
        self.host = host
        self.username = username
        self.password = password
        self.sensors = sensors or []
        self.session = async_get_clientsession(hass)
        self.hass = hass

        super().__init__(
            hass,
            _LOGGER,
            name="Mannito Farming",
            update_interval=timedelta(seconds=30),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from Mannito Farming controller."""
        try:
            # Update external sensors if configured
            if self.sensors:
                await self._update_external_sensors()
            return {}
        except Exception as err:
            _LOGGER.error("Error fetching Mannito Farming data: %s", err)
            raise

    async def _update_external_sensors(self) -> None:
        """Update external sensors on the controller."""
        sensor_data = {}
        for sensor_id in self.sensors:
            try:
                state = self.hass.states.get(sensor_id)
                if state is not None and state.state != "unknown":
                    sensor_data[sensor_id] = {
                        "state": state.state,
                        "attributes": state.attributes,
                    }
            except Exception as err:
                _LOGGER.error("Error getting sensor state for %s: %s", sensor_id, err)

        if sensor_data:
            try:
                url = API_SENSOR_UPDATE.format(host=self.host)
                async with self.session.post(
                    url,
                    json=sensor_data,
                    auth=BasicAuth(self.username, self.password),
                ) as response:
                    if response.status != 200:
                        _LOGGER.error(
                            "Error updating external sensors: %s",
                            await response.text(),
                        )
            except Exception as err:
                _LOGGER.error("Error sending sensor data: %s", err)

    async def async_set_device_state(self, device_id: str, command: str) -> bool:
        """Set device state."""
        url = API_DEVICE_STATUS.format(host=self.host, device_id=device_id)
        try:
            async with self.session.post(
                url,
                json={"state": command},
                auth=BasicAuth(self.username, self.password),
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
                auth=BasicAuth(self.username, self.password),
            ) as response:
                if response.status == 200:
                    return await response.json()
                return {}
        except Exception as err:
            _LOGGER.error("Error getting device state: %s", err)
            return {}