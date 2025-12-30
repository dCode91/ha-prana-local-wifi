"""Number platform for Prana Recuperator brightness and speed control."""
from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Any, Callable

from homeassistant.components.number import NumberEntity, NumberEntityDescription, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import PranaState
from .const import (
    BRIGHTNESS_LEVELS,
    BRIGHTNESS_VALUES,
    DOMAIN,
    FAN_TYPE_BOUNDED,
    FAN_TYPE_EXTRACT,
    FAN_TYPE_SUPPLY,
    SPEED_STEP,
)
from .coordinator import PranaCoordinator
from .entity import PranaEntity

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class PranaSpeedNumberEntityDescription(NumberEntityDescription):
    """Describes a Prana speed number entity."""

    fan_type: str
    value_fn: Callable[[PranaState], int]


SPEED_DESCRIPTIONS: tuple[PranaSpeedNumberEntityDescription, ...] = (
    PranaSpeedNumberEntityDescription(
        key="supply_speed_control",
        translation_key="supply_speed_control",
        name="Supply Fan Speed",
        icon="mdi:fan",
        native_min_value=0,
        native_max_value=6,
        native_step=1,
        mode=NumberMode.SLIDER,
        fan_type=FAN_TYPE_SUPPLY,
        value_fn=lambda state: state.supply_speed // SPEED_STEP if state.supply_speed else 0,
    ),
    PranaSpeedNumberEntityDescription(
        key="extract_speed_control",
        translation_key="extract_speed_control",
        name="Extract Fan Speed",
        icon="mdi:fan",
        native_min_value=0,
        native_max_value=6,
        native_step=1,
        mode=NumberMode.SLIDER,
        fan_type=FAN_TYPE_EXTRACT,
        value_fn=lambda state: state.extract_speed // SPEED_STEP if state.extract_speed else 0,
    ),
    PranaSpeedNumberEntityDescription(
        key="bounded_speed_control",
        translation_key="bounded_speed_control",
        name="Recuperator Speed",
        icon="mdi:fan",
        native_min_value=0,
        native_max_value=6,
        native_step=1,
        mode=NumberMode.SLIDER,
        fan_type=FAN_TYPE_BOUNDED,
        value_fn=lambda state: state.bounded_speed // SPEED_STEP if state.bounded_speed else 0,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Prana number entities from config entry."""
    coordinator: PranaCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[NumberEntity] = [
        PranaBrightnessNumber(coordinator, entry.entry_id),
    ]

    # Add speed control entities
    for description in SPEED_DESCRIPTIONS:
        entities.append(PranaSpeedNumber(coordinator, entry.entry_id, description))

    async_add_entities(entities)


class PranaBrightnessNumber(PranaEntity, NumberEntity):
    """Representation of a Prana brightness control."""

    _attr_native_min_value = 0
    _attr_native_max_value = 6
    _attr_native_step = 1
    _attr_mode = NumberMode.SLIDER
    _attr_icon = "mdi:brightness-6"
    _attr_name = "Display Brightness"
    _attr_translation_key = "brightness"

    def __init__(
        self,
        coordinator: PranaCoordinator,
        entry_id: str,
    ) -> None:
        """Initialize the brightness control."""
        super().__init__(coordinator, entry_id)
        self._attr_unique_id = f"{coordinator.api.host}_brightness"

    @property
    def native_value(self) -> float | None:
        """Return the current brightness level (0-6)."""
        if self.coordinator.data is None:
            return None

        raw_brightness = self.coordinator.data.brightness
        # Convert raw value to level (0-6)
        return BRIGHTNESS_VALUES.get(raw_brightness, 6)

    async def async_set_native_value(self, value: float) -> None:
        """Set the brightness level."""
        level = int(value)
        # Convert level (0-6) to raw value
        raw_brightness = BRIGHTNESS_LEVELS.get(level, 32)
        
        # Skip if value hasn't changed
        if self.coordinator.data and self.coordinator.data.brightness == raw_brightness:
            _LOGGER.debug("Brightness already at %d, skipping update", raw_brightness)
            return
        
        await self.coordinator.async_set_brightness(raw_brightness)


class PranaSpeedNumber(PranaEntity, NumberEntity):
    """Representation of a Prana fan speed control."""

    entity_description: PranaSpeedNumberEntityDescription

    def __init__(
        self,
        coordinator: PranaCoordinator,
        entry_id: str,
        description: PranaSpeedNumberEntityDescription,
    ) -> None:
        """Initialize the speed control."""
        super().__init__(coordinator, entry_id)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.api.host}_{description.key}"
        self._attr_mode = NumberMode.SLIDER

    @property
    def native_value(self) -> float | None:
        """Return the current speed (0-6)."""
        if self.coordinator.data is None:
            return None
        return self.entity_description.value_fn(self.coordinator.data)

    async def async_set_native_value(self, value: float) -> None:
        """Set the fan speed (0-6)."""
        speed_level = int(value)
        fan_type = self.entity_description.fan_type
        
        # Get current state
        current_speed_level = 0
        current_is_on = False
        if self.coordinator.data:
            current_speed_level = self.entity_description.value_fn(self.coordinator.data)
            current_is_on = self.coordinator.data.is_fan_on(fan_type)
        
        # Skip if value hasn't changed
        if speed_level == current_speed_level:
            _LOGGER.debug(
                "%s speed already at %d, skipping update",
                fan_type,
                speed_level,
            )
            return
        
        if speed_level == 0:
            # Turn off the fan (only if it's currently on)
            if current_is_on:
                await self.coordinator.async_set_fan_on(False, fan_type)
            else:
                _LOGGER.debug("%s fan already off, skipping update", fan_type)
        else:
            # Convert level (1-6) to API speed (10-60)
            api_speed = speed_level * SPEED_STEP
            
            # Set speed first
            await self.coordinator.async_set_speed(api_speed, fan_type)
            
            # Then ensure fan is on (if it wasn't already)
            if not current_is_on:
                await self.coordinator.async_set_fan_on(True, fan_type)
