"""Binary sensor entities for Decent ReaPrime."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DATA_COORDINATOR, DOMAIN
from .coordinator import ReaPrimeDataUpdateCoordinator
from .entity import ReaPrimeEntity
from .helpers import (
    display_state,
    is_cup_warmer_supported,
    is_machine_connected,
    is_scale_connected,
    nested_value,
)


@dataclass(frozen=True, kw_only=True)
class ReaPrimeBinarySensorDescription(BinarySensorEntityDescription):
    """Describe a ReaPrime binary sensor."""

    value_fn: Callable[[dict[str, Any] | None], bool | None]
    available_fn: Callable[[dict[str, Any] | None], bool] = lambda _: True


BINARY_SENSORS: tuple[ReaPrimeBinarySensorDescription, ...] = (
    ReaPrimeBinarySensorDescription(
        key="app_online",
        name="App online",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        value_fn=lambda data: bool((data or {}).get("app_online")),
        available_fn=lambda _: True,
    ),
    ReaPrimeBinarySensorDescription(
        key="machine_connected",
        name="Machine connected",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        value_fn=is_machine_connected,
    ),
    ReaPrimeBinarySensorDescription(
        key="scale_connected",
        name="Scale connected",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        value_fn=is_scale_connected,
    ),
    ReaPrimeBinarySensorDescription(
        key="scanning",
        name="Scanning",
        icon="mdi:radar",
        value_fn=lambda data: bool((data or {}).get("scanning", False)),
    ),
    ReaPrimeBinarySensorDescription(
        key="cup_warmer_supported",
        name="Cup warmer supported",
        icon="mdi:heat-wave",
        value_fn=is_cup_warmer_supported,
    ),
    ReaPrimeBinarySensorDescription(
        key="wake_lock",
        name="Wake lock",
        icon="mdi:cellphone-lock",
        value_fn=lambda data: nested_value(display_state(data), "wakeLockEnabled"),
        available_fn=lambda data: display_state(data) is not None,
    ),
    ReaPrimeBinarySensorDescription(
        key="wake_lock_override",
        name="Wake lock override",
        icon="mdi:cellphone-key",
        value_fn=lambda data: nested_value(display_state(data), "wakeLockOverride"),
        available_fn=lambda data: display_state(data) is not None,
    ),
    ReaPrimeBinarySensorDescription(
        key="low_battery_brightness_active",
        name="Low battery brightness limit",
        icon="mdi:battery-alert",
        value_fn=lambda data: nested_value(
            display_state(data),
            "lowBatteryBrightnessActive",
        ),
        available_fn=lambda data: display_state(data) is not None,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Decent ReaPrime binary sensors."""
    coordinator: ReaPrimeDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][
        DATA_COORDINATOR
    ]
    async_add_entities(
        ReaPrimeBinarySensor(coordinator, entry.entry_id, description)
        for description in BINARY_SENSORS
    )


class ReaPrimeBinarySensor(ReaPrimeEntity, BinarySensorEntity):
    """A Decent ReaPrime binary sensor."""

    entity_description: ReaPrimeBinarySensorDescription

    def __init__(
        self,
        coordinator: ReaPrimeDataUpdateCoordinator,
        entry_id: str,
        description: ReaPrimeBinarySensorDescription,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, entry_id, description.key, description.name or "")
        self.entity_description = description

    @property
    def is_on(self) -> bool | None:
        """Return whether the binary sensor is on."""
        if self.entity_description.key == "app_online":
            return self.coordinator.last_update_success
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def available(self) -> bool:
        """Return whether the entity is available."""
        if self.entity_description.key == "app_online":
            return True
        return super().available and self.entity_description.available_fn(
            self.coordinator.data
        )
