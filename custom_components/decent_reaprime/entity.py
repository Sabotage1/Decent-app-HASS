"""Base entities for Decent Espresso."""

from __future__ import annotations

from typing import Any

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL
from .coordinator import ReaPrimeDataUpdateCoordinator


class ReaPrimeEntity(CoordinatorEntity[ReaPrimeDataUpdateCoordinator]):
    """Base class for ReaPrime entities."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: ReaPrimeDataUpdateCoordinator,
        entry_id: str,
        key: str,
        name: str,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._attr_unique_id = f"{entry_id}_{key}"
        self._attr_name = name

    @property
    def device_info(self) -> DeviceInfo:
        """Return the ReaPrime app as the Home Assistant device."""
        info: dict[str, Any] = {
            "identifiers": {(DOMAIN, self._entry_id)},
            "manufacturer": MANUFACTURER,
            "model": MODEL,
            "name": "Decent Espresso",
            "configuration_url": self.coordinator.client.base_url,
        }
        machine_info = (self.coordinator.data or {}).get("machine_info")
        if isinstance(machine_info, dict):
            serial = machine_info.get("serial") or machine_info.get("id")
            firmware = machine_info.get("firmware") or machine_info.get("version")
            if serial is not None:
                info["serial_number"] = str(serial)
            if firmware is not None:
                info["sw_version"] = str(firmware)
        return info
