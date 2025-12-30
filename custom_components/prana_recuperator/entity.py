"""Base entity for Prana Recuperator."""
from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import PranaCoordinator


class PranaEntity(CoordinatorEntity[PranaCoordinator]):
    """Base entity for Prana Recuperator."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: PranaCoordinator,
        entry_id: str,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.api.host)},
            name=coordinator.device_name,
            manufacturer="Prana",
            model="Recuperator",
            configuration_url=f"http://{coordinator.api.host}",
        )
