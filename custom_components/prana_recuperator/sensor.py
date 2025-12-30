"""Sensor platform for Prana Recuperator."""
from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Callable

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONCENTRATION_PARTS_PER_MILLION,
    PERCENTAGE,
    UnitOfPressure,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import PranaState
from .const import DOMAIN
from .coordinator import PranaCoordinator
from .entity import PranaEntity

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class PranaSensorEntityDescription(SensorEntityDescription):
    """Describes a Prana sensor entity."""

    value_fn: Callable[[PranaState], float | int | None]
    exists_fn: Callable[[PranaState], bool] = lambda _: True


SENSOR_DESCRIPTIONS: tuple[PranaSensorEntityDescription, ...] = (
    PranaSensorEntityDescription(
        key="inside_temperature",
        translation_key="inside_temperature",
        name="Inside Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda state: state.inside_temperature,
        exists_fn=lambda state: state.inside_temperature is not None,
    ),
    PranaSensorEntityDescription(
        key="inside_temperature_2",
        translation_key="inside_temperature_2",
        name="Inside Temperature 2",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda state: state.inside_temperature_2,
        exists_fn=lambda state: state.inside_temperature_2 is not None,
    ),
    PranaSensorEntityDescription(
        key="outside_temperature",
        translation_key="outside_temperature",
        name="Outside Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda state: state.outside_temperature,
        exists_fn=lambda state: state.outside_temperature is not None,
    ),
    PranaSensorEntityDescription(
        key="outside_temperature_2",
        translation_key="outside_temperature_2",
        name="Outside Temperature 2",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda state: state.outside_temperature_2,
        exists_fn=lambda state: state.outside_temperature_2 is not None,
    ),
    PranaSensorEntityDescription(
        key="humidity",
        translation_key="humidity",
        name="Humidity",
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        value_fn=lambda state: state.humidity,
        exists_fn=lambda state: state.humidity is not None,
    ),
    PranaSensorEntityDescription(
        key="co2",
        translation_key="co2",
        name="CO2",
        device_class=SensorDeviceClass.CO2,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=CONCENTRATION_PARTS_PER_MILLION,
        value_fn=lambda state: state.co2,
        exists_fn=lambda state: state.co2 is not None,
    ),
    PranaSensorEntityDescription(
        key="voc",
        translation_key="voc",
        name="VOC",
        device_class=SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS_PARTS,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=CONCENTRATION_PARTS_PER_MILLION,
        value_fn=lambda state: state.voc,
        exists_fn=lambda state: state.voc is not None,
    ),
    PranaSensorEntityDescription(
        key="air_pressure",
        translation_key="air_pressure",
        name="Air Pressure",
        device_class=SensorDeviceClass.ATMOSPHERIC_PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPressure.HPA,
        value_fn=lambda state: state.air_pressure,
        exists_fn=lambda state: state.air_pressure is not None,
    ),
    # Speed sensors
    PranaSensorEntityDescription(
        key="extract_speed",
        translation_key="extract_speed",
        name="Extract Speed",
        icon="mdi:fan",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda state: state.extract_speed // 10 if state.extract_speed else 0,
        exists_fn=lambda _: True,
    ),
    PranaSensorEntityDescription(
        key="supply_speed",
        translation_key="supply_speed",
        name="Supply Speed",
        icon="mdi:fan",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda state: state.supply_speed // 10 if state.supply_speed else 0,
        exists_fn=lambda _: True,
    ),
    PranaSensorEntityDescription(
        key="bounded_speed",
        translation_key="bounded_speed",
        name="Bounded Speed",
        icon="mdi:fan",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda state: state.bounded_speed // 10 if state.bounded_speed else 0,
        exists_fn=lambda _: True,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Prana sensors from config entry."""
    coordinator: PranaCoordinator = hass.data[DOMAIN][entry.entry_id]

    # Only add sensors that exist (have data)
    entities = []
    for description in SENSOR_DESCRIPTIONS:
        if coordinator.data and description.exists_fn(coordinator.data):
            entities.append(PranaSensor(coordinator, entry.entry_id, description))

    async_add_entities(entities)


class PranaSensor(PranaEntity, SensorEntity):
    """Representation of a Prana sensor."""

    entity_description: PranaSensorEntityDescription

    def __init__(
        self,
        coordinator: PranaCoordinator,
        entry_id: str,
        description: PranaSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry_id)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.api.host}_{description.key}"

    @property
    def native_value(self) -> float | int | None:
        """Return the sensor value."""
        if self.coordinator.data is None:
            return None
        return self.entity_description.value_fn(self.coordinator.data)
