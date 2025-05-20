"""Fan platform for Mannito Farming integration."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from homeassistant.components.fan import (
    FanEntity,
    FanEntityDescription,
    FanEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util.percentage import (
    int_states_in_range,
    percentage_to_ranged_value,
    ranged_value_to_percentage,
)

from .api import DeviceType
from .const import (
    DOMAIN,
    DEVICE_TYPE_FAN,
)
from .coordinator import MannitoFarmingDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

# Fan speed range
SPEED_RANGE = (1, 100)  # Min speed, Max speed


@dataclass
class MannitoFarmingFanEntityDescription(FanEntityDescription):
    """Entity description for Mannito Farming fans."""

    device_type: str = DEVICE_TYPE_FAN
    icon_on: str | None = None
    icon_off: str | None = None


# Fan descriptions for the 10 fans
FAN_DESCRIPTIONS_MAP = {
    f"FAN": MannitoFarmingFanEntityDescription(
        key=f"FAN",
        translation_key="fan",
        device_type=DEVICE_TYPE_FAN,
        icon_on="mdi:fan",
        icon_off="mdi:fan-off",
    )
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Mannito Farming fan platform."""
    coordinator: MannitoFarmingDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    discovered_devices = await coordinator.get_all_devices()
    _LOGGER.debug("Discovered devices: %s", discovered_devices)
    # Add fans
    for device in discovered_devices:
        descriptor: MannitoFarmingFanEntityDescription = FAN_DESCRIPTIONS_MAP.get(device.device_type)
        if descriptor:
            entities.append(
                MannitoFarmingFan(
                    coordinator=coordinator,
                    entry=entry,
                    device_id=device.device_id,
                    description=descriptor,
                    name=device.name,
                )
            )

    async_add_entities(entities)


class MannitoFarmingFan(CoordinatorEntity[MannitoFarmingDataUpdateCoordinator], FanEntity):
    """Representation of a Mannito Farming fan."""

    entity_description: MannitoFarmingFanEntityDescription
    _attr_has_entity_name = True
    _attr_supported_features = (
        FanEntityFeature.SET_SPEED | FanEntityFeature.TURN_OFF | FanEntityFeature.TURN_ON
    )

    def __init__(
        self,
        coordinator: MannitoFarmingDataUpdateCoordinator,
        entry: ConfigEntry,
        device_id: str,
        description: MannitoFarmingFanEntityDescription,
        name: str | None = None
    ) -> None:
        """Initialize the fan."""
        super().__init__(coordinator)
        self.entity_description = description
        self._device_id = device_id
        self._attr_unique_id = f"{entry.entry_id}_{self._device_id}"
        self._attr_name = name


    @property
    def is_on(self) -> bool:
        """Return true if the fan is on."""
        device = self.coordinator._devices.get(self._device_id)
        if device:
            return device.state
        return False    @property
    def available(self) -> bool:
        """Return if entity is available."""
        device = self.coordinator._devices.get(self._device_id)
        # Check both coordinator update success and device-specific availability
        return self.coordinator.last_update_success and (device and device.available)

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        api_device_info = self.coordinator.get_device_info()
        _LOGGER.debug("Device info: %s", api_device_info)
        return api_device_info


    @property
    def percentage(self) -> Optional[int]:
        """Return the current speed percentage."""
        device = self.coordinator._devices.get(self._device_id)
        if device and device.speed is not None:
            # Convert the device speed to percentage
            return ranged_value_to_percentage(SPEED_RANGE, device.speed)
        return None

    @property
    def speed_count(self) -> int:
        """Return the number of speeds the fan supports."""
        return int_states_in_range(SPEED_RANGE)

    async def async_turn_on(
        self, percentage: Optional[int] = None, preset_mode: Optional[str] = None, **kwargs: Any
    ) -> None:
        """Turn the fan on."""
        if percentage is None:
            # If no percentage provided, use 50%
            speed = percentage_to_ranged_value(SPEED_RANGE, 50)
        else:
            # Convert percentage to device speed
            speed = percentage_to_ranged_value(SPEED_RANGE, percentage)
        
        # First turn on the fan
        await self.coordinator.async_set_device_state(self._device_id, True)
        
        # Then set the speed if applicable
        if speed > 0:
            await self.coordinator.async_set_fan_speed(self._device_id, speed)
        
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the fan off."""
        await self.coordinator.async_set_device_state(self._device_id, False)
        self.async_write_ha_state()
    
    async def async_set_percentage(self, percentage: int) -> None:
        """Set the speed percentage of the fan."""
        # Convert percentage to device speed
        speed = percentage_to_ranged_value(SPEED_RANGE, percentage)
        
        # If setting to 0, turn off the fan
        if speed == 0:
            await self.async_turn_off()
            return
        
        # If the fan is off, turn it on first
        if not self.is_on:
            await self.coordinator.async_set_device_state(self._device_id, True)
        
        # Set the speed
        await self.coordinator.async_set_fan_speed(self._device_id, speed)
        self.async_write_ha_state()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()