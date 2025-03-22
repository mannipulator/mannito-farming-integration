"""Config flow for Mannito Farming integration."""
from __future__ import annotations
import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers import config_validation as cv
from homeassistant.components.sensor import SensorDeviceClass

from .const import DOMAIN, CONF_SENSORS

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
    }
)

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Mannito Farming."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

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
        _LOGGER.debug("async_step_user called with user_input: %s", user_input)
        if user_input is None:
            _LOGGER.debug("Showing form for step 'user'")
            return self.async_show_form(
                step_id="user",
                data_schema=STEP_USER_DATA_SCHEMA,
            )

        self._host = user_input[CONF_HOST]
        self._username = user_input[CONF_USERNAME]
        self._password = user_input[CONF_PASSWORD]
        _LOGGER.debug("User input received: host=%s, username=%s", self._host, self._username)

        _LOGGER.debug("Proceeding to sensor selection step")
        return await self.async_step_sensor()

    async def async_step_sensor(
        self, user_input: dict[str, list[str]] | None = None
    ) -> FlowResult:
        """Handle the sensor selection step."""
        _LOGGER.debug("async_step_sensor called with user_input: %s", user_input)
        if user_input is None:
            # Get all available sensors
            entity_registry = er.async_get(self.hass)
            sensors = [
                entity.entity_id
                for entity in entity_registry.entities.values()
                if entity.domain == "sensor" and entity.device_class in [SensorDeviceClass.HUMIDITY, SensorDeviceClass.TEMPERATURE]
            ]
            _LOGGER.debug("Available sensors: %s", sensors)
            if not sensors:
                _LOGGER.warning("Keine passenden Sensoren gefunden, überspringe Sensorauswahl")
                return self.async_create_entry(
                    title=f"Mannito Farming {self._host}",
                    data={
                        CONF_HOST: self._host,
                        CONF_USERNAME: self._username,
                        CONF_PASSWORD: self._password,
                        CONF_SENSORS: [],
                    },
                )           
            try:
                # Erstellen eines neuen Schemas mit der Sensorliste
                schema = vol.Schema({
                    vol.Optional(CONF_SENSORS, default=[]): cv.multi_select(sensors)
                })
                _LOGGER.debug("Schema for sensor selection created successfully")
            except Exception as e:
                _LOGGER.error("Error creating schema for sensor selection: %s", e)
                raise

            return self.async_show_form(
                step_id="sensor",
                data_schema=schema,
            )

        self._sensors = user_input[CONF_SENSORS]
        _LOGGER.debug("Selected sensors: %s", self._sensors)

        _LOGGER.debug("Creating config entry for host: %s", self._host)
        return self.async_create_entry(
            title=f"Mannito Farming {self._host}",
            data={
                CONF_HOST: self._host,
                CONF_USERNAME: self._username,
                CONF_PASSWORD: self._password,
                CONF_SENSORS: self._sensors,
            },
        )