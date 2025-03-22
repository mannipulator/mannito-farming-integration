"""Fan platform for Grow Controller."""
from __future__ import annotations

from typing import Any

from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util.percentage import ordered_list_item_to_percentage, percentage_to_ordered_list_item

from .coordinator import MannitoFarmingDataUpdateCoordinator

SPEED_LIST = ["off", "low", "medium", "high"]

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Grow Controller fan platform."""
    coordinator: MannitoFarmingDataUpdateCoordinator = hass.data[entry.domain][entry.entry_id]

    # Add fans
    for i in range(10):
        async_add_entities(
            [
                GrowControllerFan(
                    coordinator,
                    entry,
                    f"FAN{i+1}",
                    f"Fan {i+1}",
                )
            ]
        )

class GrowControllerFan(FanEntity):
    """Representation of a Grow Controller fan."""

    _attr_supported_features = FanEntityFeature.SET_SPEED
    _attr_speed_list = SPEED_LIST

    def __init__(
        self,
        coordinator: GrowControllerDataUpdateCoordinator,
        entry: ConfigEntry,
        device_id: str,
        name: str,
    ) -> None:
        """Initialize the fan."""
        self.coordinator = coordinator
        self._device_id = device_id
        self._attr_name = name
        self._attr_unique_id = f"{entry.entry_id}_{device_id}"
        self._attr_is_on = False
        self._attr_percentage = 0

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success

    async def async_turn_on(
        self,
        speed: str | None = None,
        percentage: int | None = None,
        preset_mode: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Turn the fan on."""
        if percentage is not None:
            speed = percentage_to_ordered_list_item(SPEED_LIST, percentage)
        elif speed is None:
            speed = "medium"

        if await self.coordinator.async_set_device_state(self._device_id, speed):
            self._attr_is_on = True
            self._attr_percentage = ordered_list_item_to_percentage(SPEED_LIST, speed)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the fan off."""
        if await self.coordinator.async_set_device_state(self._device_id, "off"):
            self._attr_is_on = False
            self._attr_percentage = 0

    async def async_set_percentage(self, percentage: int) -> None:
        """Set the speed percentage of the fan."""
        speed = percentage_to_ordered_list_item(SPEED_LIST, percentage)
        if await self.coordinator.async_set_device_state(self._device_id, speed):
            self._attr_percentage = percentage

    async def async_update(self) -> None:
        """Update the fan state."""
        state = await self.coordinator.async_get_device_state(self._device_id)
        current_speed = state.get("speed", "off")
        self._attr_is_on = current_speed != "off"
        self._attr_percentage = ordered_list_item_to_percentage(SPEED_LIST, current_speed) 