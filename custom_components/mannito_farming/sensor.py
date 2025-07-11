"""Sensor platform for Grow Controller."""
from __future__ import annotations

import logging
from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
    UnitOfTemperature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import MannitoFarmingDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

@dataclass
class MannitoFarmingSensorEntityDescription(SensorEntityDescription):
    """Entity description for Mannito Farming switches."""

    device_class: str = "",
    native_unit_of_measurement: str | None=None,
    state_class : str ="",


SENSOR_DESCRIPTIONS_MAP = {
    "CO2": MannitoFarmingSensorEntityDescription(
        key= "CO2",
        translation_key="co2",
        device_class=SensorDeviceClass.CO2
    ),
    "TEMPERATURE": MannitoFarmingSensorEntityDescription(
        key= "TEMPERATURE",
        translation_key="temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT
    ),
    "HUMIDITY": MannitoFarmingSensorEntityDescription(
        key= "HUMIDITY",
        translation_key="humidity",
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT
    ),
    "PH": MannitoFarmingSensorEntityDescription(
        key= "PH",
        translation_key="ph",
        device_class=SensorDeviceClass.PH,
        native_unit_of_measurement=None,
        state_class=SensorStateClass.MEASUREMENT
    ),
    "EC": MannitoFarmingSensorEntityDescription(
        key= "CONDUCTIVITY",
        translation_key="conductivity",
        device_class=SensorDeviceClass.CONDUCTIVITY,
        native_unit_of_measurement=None,
        state_class=SensorStateClass.MEASUREMENT
    ),
    "WATERFLOW": MannitoFarmingSensorEntityDescription(
        key= "WATERFLOW",
        translation_key="waterflow",
        device_class=SensorDeviceClass.VOLUME_FLOW_RATE,
        native_unit_of_measurement=None,
        state_class=SensorStateClass.MEASUREMENT
    ),
    "WATERLEVEL": MannitoFarmingSensorEntityDescription(
        key= "WATERLEVEL",
        translation_key="waterlevel",
        device_class=SensorDeviceClass.VOLUME_STORAGE,
        native_unit_of_measurement=None,
        state_class=SensorStateClass.MEASUREMENT
    )
}

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Grow Controller sensor platform."""
    coordinator: MannitoFarmingDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []

    discovered_sensor = await coordinator.get_all_sensors()
    _LOGGER.debug("Discovered sensors: %s", discovered_sensor)
    for sensor in discovered_sensor:
        descriptor: MannitoFarmingSensorEntityDescription = (
            SENSOR_DESCRIPTIONS_MAP.get(sensor.sensor_type)
        )

        if descriptor:
            entities.append(
                MannitoFarmingSensor(
                    coordinator=coordinator,
                    entry=entry,
                    device_id=sensor.sensor_id,
                    description=descriptor,
                    name=sensor.name,
                )
            )

    async_add_entities(entities)


class MannitoFarmingSensor(
    CoordinatorEntity[MannitoFarmingDataUpdateCoordinator], SensorEntity
):
    """Representation of a Grow Controller temperature sensor."""

    entity_description: MannitoFarmingSensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: MannitoFarmingDataUpdateCoordinator,
        entry: ConfigEntry,
        device_id: str,
        description: MannitoFarmingSensorEntityDescription,
        name: str,
    ) -> None:
        """Initialize the generic sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._device_id = device_id
        self._attr_name = name
        self._attr_unique_id = f"{entry.entry_id}_{device_id}_sensor"

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        sensor = self.coordinator._sensors.get(self._device_id)
        # Check both coordinator update success and sensor-specific availability
        return self.coordinator.last_update_success and (sensor and sensor.available)

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return self.coordinator.get_device_info()

    @property
    def native_value(self) -> str | None:
        """Return the sensor's current value."""
        sensor = self.coordinator._sensors.get(self._device_id)
        if sensor:
            _LOGGER.debug(
                "Fetching sensor value for %s: %s", self._device_id, sensor.state_value
            )
            value = sensor.state_value

            # If sensor has state_class="measurement", ensure value is numeric
            if (
                hasattr(self.entity_description, "state_class")
                and self.entity_description.state_class == SensorStateClass.MEASUREMENT
            ):
                # For measurement sensors, validate that the value is numeric
                if value is None or value == "":
                    return None
                try:
                    # Try to convert to float to validate it's numeric
                    float(value)
                    return value
                except (ValueError, TypeError):
                    _LOGGER.warning(
                        "Sensor %s has state_class 'measurement' but returned "
                        "non-numeric value: %s (%s). Returning None.",
                        self._device_id,
                        value,
                        type(value).__name__,
                    )
                    return None

            return value
        return None

