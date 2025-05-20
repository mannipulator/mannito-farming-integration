"""Light platform for Grow Controller."""
from __future__ import annotations

from typing import Any

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ColorMode,
    LightEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import MannitoFarmingDataUpdateCoordinator

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Grow Controller light platform."""
    coordinator: MannitoFarmingDataUpdateCoordinator = hass.data[entry.domain][entry.entry_id]

    async_add_entities(
        [
            GrowControllerLight(
                coordinator,
                entry,
                "DIMMER",
                "Grow Light",
            )
        ]
    )

class GrowControllerLight(LightEntity):
    """Representation of a Grow Controller light."""

    _attr_color_mode = ColorMode.BRIGHTNESS
    _attr_supported_color_modes = {ColorMode.BRIGHTNESS}

    def __init__(
        self,
        coordinator: MannitoFarmingDataUpdateCoordinator,
        entry: ConfigEntry,
        device_id: str,
        name: str,
    ) -> None:
        """Initialize the light."""
        self.coordinator = coordinator
        self._device_id = device_id
        self._attr_name = name
        self._attr_unique_id = f"{entry.entry_id}_{device_id}"
        self._attr_is_on = False
        self._attr_brightness = 0    @property
    def available(self) -> bool:
        """Return if entity is available."""
        device = self.coordinator._devices.get(self._device_id)
        # Check both coordinator update success and device-specific availability
        return self.coordinator.last_update_success and (device and device.available)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the light on."""
        brightness = kwargs.get(ATTR_BRIGHTNESS, 255)
        if await self.coordinator.async_control_device(self._device_id, True):
            self._attr_is_on = True
            self._attr_brightness = brightness

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the light off."""
        if await self.coordinator.async_control_device(self._device_id, False):
            self._attr_is_on = False
            self._attr_brightness = 0

    async def async_update(self) -> None:
        """Update the light state."""
        state = await self.coordinator.async_fetch_device_state(self._device_id)
        self._attr_is_on = state.get("state", False)
        self._attr_brightness = state.get("brightness", 0)