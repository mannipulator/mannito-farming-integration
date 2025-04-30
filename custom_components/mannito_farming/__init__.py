"""The Mannito Farming integration."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

from homeassistant.components import zeroconf
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, PLATFORMS
from .coordinator import MannitoFarmingDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the Mannito Farming integration from a config entry."""
    _LOGGER.debug("Setting up Mannito Farming integration for %s", entry.data[CONF_HOST])

    # Initialize the coordinator, which handles API communication and data updates
    coordinator = MannitoFarmingDataUpdateCoordinator(hass, entry)
    
    # First refresh to get initial data
    await coordinator.async_config_entry_first_refresh()
    
    # Store the coordinator in hass.data for the platforms to access
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    # Forward the setup to all platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register to config entry updates
    entry.async_on_unload(entry.add_update_listener(async_update_options))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug("Unloading Mannito Farming integration for %s", entry.data[CONF_HOST])
    
    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    # Remove the coordinator from hass.data
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        
        # Remove entire domain data if this was the last entry
        if not hass.data[DOMAIN]:
            hass.data.pop(DOMAIN)

    return unload_ok


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update options when entry options are changed."""
    await hass.config_entries.async_reload(entry.entry_id)