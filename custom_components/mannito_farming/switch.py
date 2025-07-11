"""Switch platform for Mannito Farming integration."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DEVICE_TYPE_PUMP,
    DEVICE_TYPE_RELAY,
    DEVICE_TYPE_VALVE,
    DOMAIN,
    PUMP_COUNT,
    RELAY_COUNT,
    VALVE_COUNT,
)
from .coordinator import MannitoFarmingDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


@dataclass
class MannitoFarmingSwitchEntityDescription(SwitchEntityDescription):
    """Entity description for Mannito Farming switches."""

    device_type: str = ""
    icon_on: str | None = None
    icon_off: str | None = None



SWITCH_DESCRIPTIONS_MAP = {
    "SOLENOID": MannitoFarmingSwitchEntityDescription(
        translation_key="valve",
        key="SOLENOID",
        device_type=DEVICE_TYPE_VALVE,
        icon_on="mdi:water",
        icon_off="mdi:water-off",
    ),
    "RELAY": MannitoFarmingSwitchEntityDescription(
        translation_key="relay",
        key="RELAY",
        device_type=DEVICE_TYPE_RELAY,
        icon_on="mdi:power-plug",
        icon_off="mdi:power-plug-off",
    ),
    "PUMP": MannitoFarmingSwitchEntityDescription(
        translation_key="pump",
        key="PUMP",
        device_type=DEVICE_TYPE_PUMP,
        icon_on="mdi:pump",
        icon_off="mdi:pump-off",
    ),
    "HUMIDIFIER": MannitoFarmingSwitchEntityDescription(
        translation_key="humidifier",
        key="HUMIDIFIER",
        device_type="humidifier",
        icon_on="mdi:air-humidifier",
        icon_off="mdi:air-humidifier-off",
    ),
    "DEHUMIDIFIER": MannitoFarmingSwitchEntityDescription(
        translation_key="dehumidifier",
        key="DEHUMIDIFIER",
        device_type="dehumidifier",
        icon_on="mdi:water-minus",
        icon_off="mdi:water-minus-outline",
    ),
    "AIR_PUMP": MannitoFarmingSwitchEntityDescription(
        translation_key="air_pump",
        key="AIR_PUMP",
        device_type="air_pump",
        icon_on="mdi:pump",
        icon_off="mdi:pump-off",
    ),
    "HEATER": MannitoFarmingSwitchEntityDescription(
        translation_key="heater",
        key="HEATER",
        device_type="heater",
        icon_on="mdi:radiator",
        icon_off="mdi:radiator-off",
    ),
    "COOLER": MannitoFarmingSwitchEntityDescription(
        translation_key="cooler",
        key="COOLER",
        device_type="cooler",
        icon_on="mdi:snowflake",
        icon_off="mdi:snowflake-off",
    ),
    "CO2_VALVE": MannitoFarmingSwitchEntityDescription(
        translation_key="co2_valve",
        key="CO2_VALVE",
        device_type="co2_valve",
        icon_on="mdi:valve-open",
        icon_off="mdi:valve-closed",
    ),
    "HEAT_MAT": MannitoFarmingSwitchEntityDescription(
        translation_key="heat_mat",
        key="HEAT_MAT",
        device_type="heat_mat",
        icon_on="mdi:heating-coil",
        icon_off="mdi:heating-coil",
    ),
    "PERISTALTIC_PUMP": MannitoFarmingSwitchEntityDescription(
        translation_key="peristaltic_pump",
        key="PERISTALTIC_PUMP",
        device_type="peristaltic_pump",
        icon_on="mdi:pump",
        icon_off="mdi:pump-off",
    ),
    "MISTING_SYSTEM": MannitoFarmingSwitchEntityDescription(
        translation_key="misting_system",
        key="MISTING_SYSTEM",
        device_type="misting_system",
        icon_on="mdi:sprinkler",
        icon_off="mdi:sprinkler-off",
    ),
    "GENERIC_SOCKET": MannitoFarmingSwitchEntityDescription(
        translation_key="relay",
        key="GENERIC_SOCKET",
        device_type=DEVICE_TYPE_RELAY,
        icon_on="mdi:power-plug",
        icon_off="mdi:power-plug-off",
    ),
}


# Switch descriptions for valves
VALVE_ENTITY_DESCRIPTIONS = [
    MannitoFarmingSwitchEntityDescription(
        key=f"SOLENOID{i}",
        translation_key="valve",
        name=f"Valve {i}",
        device_type=DEVICE_TYPE_VALVE,
        icon_on="mdi:water",
        icon_off="mdi:water-off",
    )
    for i in range(1, VALVE_COUNT + 1)
]

# Switch descriptions for relays
RELAY_ENTITY_DESCRIPTIONS = [
    MannitoFarmingSwitchEntityDescription(
        key=f"RELAY{i}",
        translation_key="relay",
        name=f"Relay {i}",
        device_type=DEVICE_TYPE_RELAY,
        icon_on="mdi:power-plug",
        icon_off="mdi:power-plug-off",
    )
    for i in range(1, RELAY_COUNT + 1)
]

# Switch descriptions for pumps
PUMP_ENTITY_DESCRIPTIONS = [
    MannitoFarmingSwitchEntityDescription(
        key=f"PUMP{i}",
        translation_key="pump",
        name=f"Pump {i}",
        device_type=DEVICE_TYPE_PUMP,
        icon_on="mdi:pump",
        icon_off="mdi:pump-off",
    )
    for i in range(1, PUMP_COUNT + 1)
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Mannito Farming switch platform."""
    coordinator: MannitoFarmingDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []

    discovered_devices = await coordinator.get_all_devices()
    _LOGGER.debug("Discovered switch-devices: %s", discovered_devices)
    for device in discovered_devices:
        descriptor: MannitoFarmingSwitchEntityDescription = SWITCH_DESCRIPTIONS_MAP.get(device.device_type)
        if descriptor:
            entities.append(
                MannitoFarmingSwitch(
                    coordinator=coordinator,
                    entry=entry,
                    device_id=device.device_id,
                    description=descriptor,
                    name=device.name,
                )
            )
    async_add_entities(entities)



class MannitoFarmingSwitch(CoordinatorEntity[MannitoFarmingDataUpdateCoordinator], SwitchEntity):
    """Representation of a Mannito Farming switch."""

    entity_description: MannitoFarmingSwitchEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: MannitoFarmingDataUpdateCoordinator,
        entry: ConfigEntry,
        device_id: str,
        description: MannitoFarmingSwitchEntityDescription,
        name: str | None = None
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self.entity_description = description
        self._device_id = device_id
        self._attr_unique_id = f"{entry.entry_id}_{self._device_id}"
        self._attr_name = name

    @property
    def icon(self) -> str | None:
        """Return the icon to use in the frontend."""
        if self.is_on:
            return self.entity_description.icon_on
        return self.entity_description.icon_off

    @property
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
    def is_on(self) -> bool:
        """Return true if the switch is on."""
        device = self.coordinator._devices.get(self._device_id)
        if device:
            return device.state
        return False

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        await self.coordinator.async_set_device_state(self._device_id, True)
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        await self.coordinator.async_set_device_state(self._device_id, False)
        self.async_write_ha_state()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()
