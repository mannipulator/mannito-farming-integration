"""Config flow for Mannito Farming integration."""
import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import API, APIAuthError, APIConnectionError
from .const import DOMAIN, MDNS_SERVICE_TYPE

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_USERNAME): str,
        vol.Optional(CONF_PASSWORD): str,
    }
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Mannito Farming."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._host: str | None = None
        self._username: str | None = None
        self._password: str | None = None
        self._discovered_devices: dict[str, dict[str, Any]] = {}

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._host = user_input[CONF_HOST]
            self._username = user_input.get(CONF_USERNAME)
            self._password = user_input.get(CONF_PASSWORD)

            try:
                return await self._test_connection()
            except APIConnectionError:
                errors["base"] = "cannot_connect"
            except APIAuthError:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_zeroconf(self, discovery_info: dict[str, Any]) -> FlowResult:
        """Handle zeroconf discovery."""
        if not discovery_info.get("type") == MDNS_SERVICE_TYPE:
            return self.async_abort(reason="not_mannito_device")

        # Get the host from the discovery info
        self._host = discovery_info.get("host")

        # Check if device is already configured
        await self.async_set_unique_id(f"mannito_{self._host}")
        self._abort_if_unique_id_configured({CONF_HOST: self._host})

        # Set the default title that will be shown in the UI
        self.context["title_placeholders"] = {
            "name": discovery_info.get("name", "Mannito Farming"),
            "host": self._host,
        }

        return await self.async_step_confirm()

    async def async_step_confirm(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Confirm the zeroconf discovery."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._username = user_input.get(CONF_USERNAME)
            self._password = user_input.get(CONF_PASSWORD)

            try:
                return await self._test_connection()
            except APIConnectionError:
                errors["base"] = "cannot_connect"
            except APIAuthError:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="confirm",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_USERNAME): str,
                    vol.Optional(CONF_PASSWORD): str,
                }
            ),
            description_placeholders={"host": self._host},
            errors=errors,
        )

    async def _test_connection(self) -> FlowResult:
        """Test the connection to the device."""
        session = async_get_clientsession(self.hass)
        api = API(self._host, self._username, self._password, session)

        device_config = await api.fetch_device_config()

        # Use serial number or host for unique ID if available
        serial_number = device_config.get("serial_number")
        unique_id = f"mannito_{serial_number}" if serial_number else f"mannito_{self._host}"

        await self.async_set_unique_id(unique_id)
        self._abort_if_unique_id_configured({CONF_HOST: self._host})

        # Create a title for the device
        if serial_number:
            title = f"Mannito Farming {serial_number}"
        else:
            title = f"Mannito Farming {self._host}"

        return self.async_create_entry(
            title=title,
            data={
                CONF_HOST: self._host,
                CONF_USERNAME: self._username,
                CONF_PASSWORD: self._password,
                "device_info": device_config,
            },
        )
