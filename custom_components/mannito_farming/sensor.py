"""Sensor platform for Grow Controller."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
    UnitOfTemperature
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import MannitoFarmingDataUpdateCoordinator

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Grow Controller sensor platform."""
    coordinator: MannitoFarmingDataUpdateCoordinator = hass.data[entry.domain][entry.entry_id]

    # Add temperature and humidity sensors
    for i in range(2):
        async_add_entities(
            [
                GrowControllerTemperatureSensor(
                    coordinator,
                    entry,
                    f"sensor_{i+1}",
                    f"Temperature Sensor {i+1}",
                ),
                GrowControllerHumiditySensor(
                    coordinator,
                    entry,
                    f"sensor_{i+1}",
                    f"Humidity Sensor {i+1}",
                ),
            ]
        )

class GrowControllerTemperatureSensor(SensorEntity):
    """Representation of a Grow Controller temperature sensor."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: GrowControllerDataUpdateCoordinator,
        entry: ConfigEntry,
        device_id: str,
        name: str,
    ) -> None:
        """Initialize the temperature sensor."""
        self.coordinator = coordinator
        self._device_id = device_id
        self._attr_name = name
        self._attr_unique_id = f"{entry.entry_id}_{device_id}_temperature"
        self._attr_native_value = None
        self._attr_last_updated = None

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success

    async def async_update(self) -> None:
        """Update the sensor state."""
        state = await self.coordinator.async_get_device_state(self._device_id)
        try:
            self._attr_native_value = float(state.get("temperature", 0))
            self._attr_last_updated = datetime.now()
        except (ValueError, TypeError):
            self._attr_native_value = None

class GrowControllerHumiditySensor(SensorEntity):
    """Representation of a Grow Controller humidity sensor."""

    _attr_device_class = SensorDeviceClass.HUMIDITY
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: GrowControllerDataUpdateCoordinator,
        entry: ConfigEntry,
        device_id: str,
        name: str,
    ) -> None:
        """Initialize the humidity sensor."""
        self.coordinator = coordinator
        self._device_id = device_id
        self._attr_name = name
        self._attr_unique_id = f"{entry.entry_id}_{device_id}_humidity"
        self._attr_native_value = None
        self._attr_last_updated = None

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success

    async def async_update(self) -> None:
        """Update the sensor state."""
        state = await self.coordinator.async_get_device_state(self._device_id)
        try:
            self._attr_native_value = float(state.get("humidity", 0))
            self._attr_last_updated = datetime.now()
        except (ValueError, TypeError):
            self._attr_native_value = None 