"""Number entities for Decent ReaPrime."""

from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DATA_COORDINATOR, DOMAIN
from .coordinator import ReaPrimeDataUpdateCoordinator
from .entity import ReaPrimeEntity
from .helpers import (
    cup_warmer_state,
    display_state,
    is_cup_warmer_supported,
    nested_value,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Decent ReaPrime numbers."""
    coordinator: ReaPrimeDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][
        DATA_COORDINATOR
    ]
    async_add_entities(
        [
            ReaPrimeBrightnessNumber(coordinator, entry.entry_id),
            ReaPrimeCupWarmerNumber(coordinator, entry.entry_id),
        ]
    )


class ReaPrimeBrightnessNumber(ReaPrimeEntity, NumberEntity):
    """Tablet brightness control."""

    _attr_icon = "mdi:brightness-6"
    _attr_native_min_value = 0
    _attr_native_max_value = 100
    _attr_native_step = 1
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_mode = NumberMode.SLIDER

    def __init__(
        self,
        coordinator: ReaPrimeDataUpdateCoordinator,
        entry_id: str,
    ) -> None:
        """Initialize the brightness number."""
        super().__init__(coordinator, entry_id, "display_brightness_control", "Display brightness")

    @property
    def native_value(self) -> float | None:
        """Return the current brightness target."""
        display = display_state(self.coordinator.data)
        requested = nested_value(display, "requestedBrightness")
        return requested if requested is not None else nested_value(display, "brightness")

    @property
    def available(self) -> bool:
        """Return whether brightness control is available."""
        return super().available and bool(
            nested_value(
                display_state(self.coordinator.data),
                "platformSupported",
                "brightness",
            )
        )

    async def async_set_native_value(self, value: float) -> None:
        """Set display brightness."""
        display = await self.coordinator.client.async_set_brightness(round(value))
        if display is not None:
            data = dict(self.coordinator.data or {})
            data["display"] = display
            self.coordinator.async_set_updated_data(data)
        await self.coordinator.async_request_refresh()


class ReaPrimeCupWarmerNumber(ReaPrimeEntity, NumberEntity):
    """Bengle cup warmer setpoint."""

    _attr_icon = "mdi:heat-wave"
    _attr_native_min_value = 0
    _attr_native_max_value = 80
    _attr_native_step = 1
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_mode = NumberMode.SLIDER

    def __init__(
        self,
        coordinator: ReaPrimeDataUpdateCoordinator,
        entry_id: str,
    ) -> None:
        """Initialize the cup warmer number."""
        super().__init__(coordinator, entry_id, "cup_warmer_temperature", "Cup warmer")

    @property
    def native_value(self) -> float | None:
        """Return the current cup warmer temperature."""
        return nested_value(cup_warmer_state(self.coordinator.data), "temperature")

    @property
    def available(self) -> bool:
        """Return whether the cup warmer is available."""
        return (
            super().available
            and is_cup_warmer_supported(self.coordinator.data)
            and cup_warmer_state(self.coordinator.data) is not None
        )

    async def async_set_native_value(self, value: float) -> None:
        """Set cup warmer temperature."""
        await self.coordinator.client.async_set_cup_warmer_temperature(float(value))
        await self.coordinator.async_request_refresh()
