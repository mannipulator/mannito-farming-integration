"""Data update coordinator for Mannito Farming."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any
from aiohttp import BasicAuth
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    CONF_USERNAME,
    CONF_SENSORS
)

from .const import API_BASE_URL, API_DEVICE_STATUS, API_SENSOR_UPDATE, API_DEVICE_SET_STATE

_LOGGER = logging.getLogger(__name__)

class MannitoFarmingDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the Mannito Farming controller."""

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry
    ) -> None:
        """Initialize the data updater."""

        self.host = config_entry.data[CONF_HOST]
        self.username = config_entry.data[CONF_USERNAME]
        self.password = config_entry.data[CONF_PASSWORD]

        self.sensors = sensors or []
        self.session = async_get_clientsession(hass)
        self.hass = hass
        _LOGGER.debug("Coordinator initialized with host: %s", self.host)

        super().__init__(
            hass,
            _LOGGER,
            name="Mannito Farming",
            update_method=self.async_update_data,
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
                    json=sensor_data
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

        """ Create API here """
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