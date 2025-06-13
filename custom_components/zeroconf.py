"""Zeroconf discovery for Mannito Farming integration."""
from homeassistant.components.zeroconf import ZeroconfServiceInfo
from homeassistant.config_entries import ConfigFlow
from homeassistant.const import CONF_HOST, CONF_NAME

from .const import DOMAIN


async def async_setup_zeroconf(hass):
    """Set up Zeroconf discovery."""

class MannitoFarmingConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle Zeroconf discovery for Mannito Farming."""

    async def async_step_zeroconf(
        self, discovery_info: ZeroconfServiceInfo
    ) -> dict:
        """Handle Zeroconf discovery."""
        if discovery_info.type != "_mannitofarming._tcp.local.":
            return self.async_abort(reason="invalid_service_type")

        host = discovery_info.host
        name = discovery_info.properties.get("name", discovery_info.hostname)
        model = discovery_info.properties.get("model", "Mannito Farming Controller")
        version = discovery_info.properties.get("version", "Unknown")

        await self.async_set_unique_id(discovery_info.hostname)
        self._abort_if_unique_id_configured()

        self.context["title_placeholders"] = {"name": name}
        return await self.async_step_user(
            user_input={
                CONF_HOST: host,
                CONF_NAME: name,
                "model": model,
                "version": version,
            }
        )

    async def async_step_user(self, user_input=None):
        """Handle user configuration step."""
        if user_input is not None:
            return self.async_create_entry(
                title=user_input[CONF_NAME],
                data={
                    CONF_HOST: user_input[CONF_HOST],
                    CONF_NAME: user_input[CONF_NAME],
                },
            )
        return self.async_show_form(step_id="user")
