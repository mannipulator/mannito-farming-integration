"""Switch platform for Grow Controller."""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DEVICE_TYPE_VALVE,
    DEVICE_TYPE_PUMP,
)
from .coordinator import GrowControllerDataUpdateCoordinator

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Grow Controller switch platform."""
    coordinator: GrowControllerDataUpdateCoordinator = hass.data[entry.domain][entry.entry_id]

    # Add valves
    for i in range(5):
        async_add_entities(
            [
                GrowControllerSwitch(
                    coordinator,
                    entry,
                    f"valve_{i+1}",
                    f"Valve {i+1}",
                    DEVICE_TYPE_VALVE,
                )
            ]
        )

    # Add pumps
    for i in range(4):
        async_add_entities(
            [
                GrowControllerSwitch(
                    coordinator,
                    entry,
                    f"pump_{i+1}",
                    f"Pump {i+1}",
                    DEVICE_TYPE_PUMP,
                )
            ]
        )

class GrowControllerSwitch(SwitchEntity):
    """Representation of a Grow Controller switch."""

    def __init__(
        self,
        coordinator: GrowControllerDataUpdateCoordinator,
        entry: ConfigEntry,
        device_id: str,
        name: str,
        device_type: str,
    ) -> None:
        """Initialize the switch."""
        self.coordinator = coordinator
        self._device_id = device_id
        self._attr_name = name
        self._attr_unique_id = f"{entry.entry_id}_{device_id}"
        self._device_type = device_type
        self._attr_is_on = False

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        if await self.coordinator.async_set_device_state(self._device_id, "on"):
            self._attr_is_on = True

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        if await self.coordinator.async_set_device_state(self._device_id, "off"):
            self._attr_is_on = False

    async def async_update(self) -> None:
        """Update the switch state."""
        state = await self.coordinator.async_get_device_state(self._device_id)
        self._attr_is_on = state.get("state") == "on" 