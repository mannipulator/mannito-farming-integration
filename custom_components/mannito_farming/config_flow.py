"""Config flow for Grow Controller integration."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import entity_registry as er

from .const import DOMAIN, CONF_SENSORS

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
    }
)

STEP_SENSOR_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_SENSORS): vol.All(
            cv.multi_select,
            vol.Length(min=1),
        ),
    }
)

class GrowControllerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Grow Controller."""

    VERSION = 1

    def __init__(self):
        """Initialize the config flow."""
        self._host = None
        self._username = None
        self._password = None
        self._sensors = None

    async def async_step_user(
        self, user_input: dict[str, str] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=STEP_USER_DATA_SCHEMA,
            )

        self._host = user_input[CONF_HOST]
        self._username = user_input[CONF_USERNAME]
        self._password = user_input[CONF_PASSWORD]

        return await self.async_step_sensor()

    async def async_step_sensor(
        self, user_input: dict[str, list[str]] | None = None
    ) -> FlowResult:
        """Handle the sensor selection step."""
        if user_input is None:
            # Get all available sensors
            entity_registry = er.async_get(self.hass)
            sensors = [
                entity.entity_id
                for entity in entity_registry.entities.values()
                if entity.domain == "sensor"
            ]

            return self.async_show_form(
                step_id="sensor",
                data_schema=STEP_SENSOR_DATA_SCHEMA.extend(
                    {
                        vol.Required(CONF_SENSORS): vol.All(
                            cv.multi_select,
                            vol.Length(min=1),
                        ),
                    }
                ),
            )

        self._sensors = user_input[CONF_SENSORS]

        return self.async_create_entry(
            title=f"Grow Controller {self._host}",
            data={
                CONF_HOST: self._host,
                CONF_USERNAME: self._username,
                CONF_PASSWORD: self._password,
                CONF_SENSORS: self._sensors,
            },
        ) 