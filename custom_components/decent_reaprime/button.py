"""Button entities for Decent ReaPrime."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DATA_COORDINATOR, DOMAIN
from .coordinator import ReaPrimeDataUpdateCoordinator
from .entity import ReaPrimeEntity
from .helpers import display_state, is_machine_connected, is_scale_connected, nested_value


@dataclass(frozen=True, kw_only=True)
class ReaPrimeButtonDescription(ButtonEntityDescription):
    """Describe a ReaPrime button."""

    press_fn: Callable[[ReaPrimeDataUpdateCoordinator], Any]
    available_fn: Callable[[dict[str, Any] | None], bool] = lambda _: True


async def _scan_devices(coordinator: ReaPrimeDataUpdateCoordinator) -> None:
    await coordinator.client.async_scan_devices(connect=False, quick=True)


async def _auto_connect(coordinator: ReaPrimeDataUpdateCoordinator) -> None:
    await coordinator.client.async_scan_devices(connect=True, quick=True)


async def _tare_scale(coordinator: ReaPrimeDataUpdateCoordinator) -> None:
    await coordinator.client.async_tare_scale()


async def _timer_start(coordinator: ReaPrimeDataUpdateCoordinator) -> None:
    await coordinator.client.async_scale_timer_start()


async def _timer_stop(coordinator: ReaPrimeDataUpdateCoordinator) -> None:
    await coordinator.client.async_scale_timer_stop()


async def _timer_reset(coordinator: ReaPrimeDataUpdateCoordinator) -> None:
    await coordinator.client.async_scale_timer_reset()


async def _request_wakelock(coordinator: ReaPrimeDataUpdateCoordinator) -> None:
    await coordinator.client.async_request_wakelock()


async def _release_wakelock(coordinator: ReaPrimeDataUpdateCoordinator) -> None:
    await coordinator.client.async_release_wakelock()


async def _machine_idle(coordinator: ReaPrimeDataUpdateCoordinator) -> None:
    await coordinator.client.async_set_machine_state("idle")


async def _machine_sleep(coordinator: ReaPrimeDataUpdateCoordinator) -> None:
    await coordinator.client.async_set_machine_state("sleeping")


def _wake_lock_supported(data: dict[str, Any] | None) -> bool:
    return bool(nested_value(display_state(data), "platformSupported", "wakeLock"))


BUTTONS: tuple[ReaPrimeButtonDescription, ...] = (
    ReaPrimeButtonDescription(
        key="scan_devices",
        name="Scan devices",
        icon="mdi:radar",
        press_fn=_scan_devices,
    ),
    ReaPrimeButtonDescription(
        key="auto_connect",
        name="Auto-connect",
        icon="mdi:connection",
        press_fn=_auto_connect,
    ),
    ReaPrimeButtonDescription(
        key="tare_scale",
        name="Tare scale",
        icon="mdi:scale-balance",
        press_fn=_tare_scale,
        available_fn=is_scale_connected,
    ),
    ReaPrimeButtonDescription(
        key="scale_timer_start",
        name="Start scale timer",
        icon="mdi:timer-play-outline",
        press_fn=_timer_start,
        available_fn=is_scale_connected,
    ),
    ReaPrimeButtonDescription(
        key="scale_timer_stop",
        name="Stop scale timer",
        icon="mdi:timer-stop-outline",
        press_fn=_timer_stop,
        available_fn=is_scale_connected,
    ),
    ReaPrimeButtonDescription(
        key="scale_timer_reset",
        name="Reset scale timer",
        icon="mdi:timer-refresh-outline",
        press_fn=_timer_reset,
        available_fn=is_scale_connected,
    ),
    ReaPrimeButtonDescription(
        key="request_wake_lock",
        name="Request wake lock",
        icon="mdi:cellphone-lock",
        press_fn=_request_wakelock,
        available_fn=_wake_lock_supported,
    ),
    ReaPrimeButtonDescription(
        key="release_wake_lock",
        name="Release wake lock",
        icon="mdi:cellphone-key",
        press_fn=_release_wakelock,
        available_fn=_wake_lock_supported,
    ),
    ReaPrimeButtonDescription(
        key="machine_idle",
        name="Stop machine",
        icon="mdi:stop-circle-outline",
        press_fn=_machine_idle,
        available_fn=is_machine_connected,
    ),
    ReaPrimeButtonDescription(
        key="machine_sleep",
        name="Sleep machine",
        icon="mdi:power-sleep",
        press_fn=_machine_sleep,
        available_fn=is_machine_connected,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Decent ReaPrime buttons."""
    coordinator: ReaPrimeDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][
        DATA_COORDINATOR
    ]
    async_add_entities(
        ReaPrimeButton(coordinator, entry.entry_id, description)
        for description in BUTTONS
    )


class ReaPrimeButton(ReaPrimeEntity, ButtonEntity):
    """A Decent ReaPrime button."""

    entity_description: ReaPrimeButtonDescription

    def __init__(
        self,
        coordinator: ReaPrimeDataUpdateCoordinator,
        entry_id: str,
        description: ReaPrimeButtonDescription,
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator, entry_id, description.key, description.name or "")
        self.entity_description = description

    @property
    def available(self) -> bool:
        """Return whether the entity is available."""
        return super().available and self.entity_description.available_fn(
            self.coordinator.data
        )

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.entity_description.press_fn(self.coordinator)
        await self.coordinator.async_request_refresh()
