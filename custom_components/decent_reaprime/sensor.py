"""Sensor entities for Decent ReaPrime."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfMass,
    UnitOfPressure,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from .const import DATA_COORDINATOR, DOMAIN
from .coordinator import ReaPrimeDataUpdateCoordinator
from .entity import ReaPrimeEntity
from .helpers import (
    device_list,
    display_state,
    is_machine_connected,
    is_scale_connected,
    machine_snapshot,
    nested_value,
    scale_snapshot,
)


@dataclass(frozen=True, kw_only=True)
class ReaPrimeSensorDescription(SensorEntityDescription):
    """Describe a ReaPrime sensor."""

    value_fn: Callable[[dict[str, Any] | None], StateType]
    available_fn: Callable[[dict[str, Any] | None], bool] = lambda _: True
    attr_fn: Callable[[dict[str, Any] | None], dict[str, Any]] | None = None


def _machine_state(data: dict[str, Any] | None) -> StateType:
    return nested_value(machine_snapshot(data), "state", "state")


def _scale_timer_seconds(data: dict[str, Any] | None) -> StateType:
    timer_value = nested_value(scale_snapshot(data), "timerValue")
    if timer_value is None:
        return None
    return round(float(timer_value) / 1000, 1)


def _machine_attrs(data: dict[str, Any] | None) -> dict[str, Any]:
    snapshot = machine_snapshot(data) or {}
    attrs: dict[str, Any] = {}
    substate = nested_value(snapshot, "state", "substate")
    if substate is not None:
        attrs["substate"] = substate
    timestamp = snapshot.get("timestamp")
    if timestamp is not None:
        attrs["timestamp"] = timestamp
    error = (data or {}).get("machine_error")
    if error is not None:
        attrs["error"] = error
    return attrs


def _device_count(data: dict[str, Any] | None) -> StateType:
    return sum(1 for device in device_list(data) if device.get("state") == "connected")


def _device_attrs(data: dict[str, Any] | None) -> dict[str, Any]:
    return {"devices": device_list(data)}


SENSORS: tuple[ReaPrimeSensorDescription, ...] = (
    ReaPrimeSensorDescription(
        key="machine_state",
        name="Machine state",
        icon="mdi:coffee-maker",
        value_fn=_machine_state,
        available_fn=is_machine_connected,
        attr_fn=_machine_attrs,
    ),
    ReaPrimeSensorDescription(
        key="pressure",
        name="Pressure",
        native_unit_of_measurement=UnitOfPressure.BAR,
        device_class=SensorDeviceClass.PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        value_fn=lambda data: nested_value(machine_snapshot(data), "pressure"),
        available_fn=is_machine_connected,
    ),
    ReaPrimeSensorDescription(
        key="target_pressure",
        name="Target pressure",
        native_unit_of_measurement=UnitOfPressure.BAR,
        device_class=SensorDeviceClass.PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        value_fn=lambda data: nested_value(machine_snapshot(data), "targetPressure"),
        available_fn=is_machine_connected,
    ),
    ReaPrimeSensorDescription(
        key="flow",
        name="Flow",
        icon="mdi:waves-arrow-right",
        native_unit_of_measurement="mL/s",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        value_fn=lambda data: nested_value(machine_snapshot(data), "flow"),
        available_fn=is_machine_connected,
    ),
    ReaPrimeSensorDescription(
        key="target_flow",
        name="Target flow",
        icon="mdi:waves-arrow-right",
        native_unit_of_measurement="mL/s",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        value_fn=lambda data: nested_value(machine_snapshot(data), "targetFlow"),
        available_fn=is_machine_connected,
    ),
    ReaPrimeSensorDescription(
        key="mix_temperature",
        name="Mix temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda data: nested_value(machine_snapshot(data), "mixTemperature"),
        available_fn=is_machine_connected,
    ),
    ReaPrimeSensorDescription(
        key="group_temperature",
        name="Group temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda data: nested_value(machine_snapshot(data), "groupTemperature"),
        available_fn=is_machine_connected,
    ),
    ReaPrimeSensorDescription(
        key="target_mix_temperature",
        name="Target mix temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda data: nested_value(machine_snapshot(data), "targetMixTemperature"),
        available_fn=is_machine_connected,
    ),
    ReaPrimeSensorDescription(
        key="target_group_temperature",
        name="Target group temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda data: nested_value(machine_snapshot(data), "targetGroupTemperature"),
        available_fn=is_machine_connected,
    ),
    ReaPrimeSensorDescription(
        key="steam_temperature",
        name="Steam temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda data: nested_value(machine_snapshot(data), "steamTemperature"),
        available_fn=is_machine_connected,
    ),
    ReaPrimeSensorDescription(
        key="profile_frame",
        name="Profile frame",
        icon="mdi:timeline-clock",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: nested_value(machine_snapshot(data), "profileFrame"),
        available_fn=is_machine_connected,
    ),
    ReaPrimeSensorDescription(
        key="scale_weight",
        name="Scale weight",
        native_unit_of_measurement=UnitOfMass.GRAMS,
        device_class=SensorDeviceClass.WEIGHT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda data: nested_value(scale_snapshot(data), "weight"),
        available_fn=is_scale_connected,
    ),
    ReaPrimeSensorDescription(
        key="scale_flow",
        name="Scale flow",
        icon="mdi:scale-balance",
        native_unit_of_measurement="g/s",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        value_fn=lambda data: nested_value(scale_snapshot(data), "weightFlow"),
        available_fn=is_scale_connected,
    ),
    ReaPrimeSensorDescription(
        key="scale_battery",
        name="Scale battery",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: nested_value(scale_snapshot(data), "battery"),
        available_fn=is_scale_connected,
    ),
    ReaPrimeSensorDescription(
        key="scale_timer",
        name="Scale timer",
        icon="mdi:timer-outline",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=_scale_timer_seconds,
        available_fn=is_scale_connected,
    ),
    ReaPrimeSensorDescription(
        key="display_brightness",
        name="Display brightness",
        icon="mdi:brightness-6",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: nested_value(display_state(data), "brightness"),
        available_fn=lambda data: display_state(data) is not None,
    ),
    ReaPrimeSensorDescription(
        key="connected_devices",
        name="Connected devices",
        icon="mdi:devices",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=_device_count,
        attr_fn=_device_attrs,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Decent ReaPrime sensors."""
    coordinator: ReaPrimeDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][
        DATA_COORDINATOR
    ]
    async_add_entities(
        ReaPrimeSensor(coordinator, entry.entry_id, description)
        for description in SENSORS
    )


class ReaPrimeSensor(ReaPrimeEntity, SensorEntity):
    """A Decent ReaPrime sensor."""

    entity_description: ReaPrimeSensorDescription

    def __init__(
        self,
        coordinator: ReaPrimeDataUpdateCoordinator,
        entry_id: str,
        description: ReaPrimeSensorDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry_id, description.key, description.name or "")
        self.entity_description = description

    @property
    def native_value(self) -> StateType:
        """Return the sensor value."""
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def available(self) -> bool:
        """Return whether the entity is available."""
        return super().available and self.entity_description.available_fn(
            self.coordinator.data
        )

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return extra state attributes."""
        if self.entity_description.attr_fn is None:
            return None
        attrs = self.entity_description.attr_fn(self.coordinator.data)
        return attrs or None
