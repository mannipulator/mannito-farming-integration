"""Light platform for Grow Controller."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ColorMode,
    LightEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import MannitoFarmingDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Grow Controller light platform."""
    coordinator: MannitoFarmingDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []

    discovered_devices = await coordinator.get_all_devices()
    _LOGGER.debug("Discovered light devices: %s", discovered_devices)
    for device in discovered_devices:
        if device.device_type == "LIGHT":
            entities.append(
                MannitoFarmingLight(
                    coordinator=coordinator,
                    entry=entry,
                    device_id=device.device_id,
                    name=device.name,
                )
            )
    async_add_entities(entities)


class MannitoFarmingLight(
    CoordinatorEntity[MannitoFarmingDataUpdateCoordinator], LightEntity
):
    """Representation of a Mannito Farming light."""

    _attr_color_mode = ColorMode.BRIGHTNESS
    _attr_supported_color_modes = {ColorMode.BRIGHTNESS}
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: MannitoFarmingDataUpdateCoordinator,
        entry: ConfigEntry,
        device_id: str,
        name: str,
    ) -> None:
        """Initialize the light."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._attr_name = name
        self._attr_unique_id = f"{entry.entry_id}_{device_id}_light"

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        device = self.coordinator._devices.get(self._device_id)
        return self.coordinator.last_update_success and (device and device.available)

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return self.coordinator.get_device_info()

    @property
    def is_on(self) -> bool:
        """Return true if light is on."""
        device = self.coordinator._devices.get(self._device_id)
        if device:
            return device.state
        return False

    @property
    def brightness(self) -> int | None:
        """Return the brightness of this light between 0..255."""
        device = self.coordinator._devices.get(self._device_id)
        if device and device.powerlevel is not None and device.powerlevel_supported:
            # Convert from device powerlevel range to Home Assistant brightness range (0-255)
            max_powerlevel = device.max_powerlevel or 255
            return int((device.powerlevel / max_powerlevel) * 255)
        return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the light on."""
        brightness = kwargs.get(ATTR_BRIGHTNESS)
        
        if brightness is not None:
            device = self.coordinator._devices.get(self._device_id)
            if device and device.powerlevel_supported:
                # Convert brightness (0-255) to device powerlevel range
                max_powerlevel = device.max_powerlevel or 255
                powerlevel = int((brightness / 255) * max_powerlevel)
                await self.coordinator.api.set_fan_speed(self._device_id, powerlevel)
            else:
                # Device doesn't support brightness, just turn on
                await self.coordinator.api.set_device_state(self._device_id, True)
        else:
            # No brightness specified, just turn on
            await self.coordinator.api.set_device_state(self._device_id, True)
        
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the light off."""
        await self.coordinator.api.set_device_state(self._device_id, False)
        await self.coordinator.async_request_refresh()
