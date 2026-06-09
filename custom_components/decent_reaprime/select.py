"""Select entities for Decent ReaPrime."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DATA_COORDINATOR, DOMAIN, MACHINE_STATE_OPTIONS
from .coordinator import ReaPrimeDataUpdateCoordinator
from .entity import ReaPrimeEntity
from .helpers import is_machine_connected, machine_snapshot, nested_value


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Decent ReaPrime select entities."""
    coordinator: ReaPrimeDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][
        DATA_COORDINATOR
    ]
    async_add_entities([ReaPrimeMachineStateSelect(coordinator, entry.entry_id)])


class ReaPrimeMachineStateSelect(ReaPrimeEntity, SelectEntity):
    """Machine state selector."""

    _attr_icon = "mdi:coffee-maker"
    _attr_options = MACHINE_STATE_OPTIONS

    def __init__(
        self,
        coordinator: ReaPrimeDataUpdateCoordinator,
        entry_id: str,
    ) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator, entry_id, "machine_state_select", "Machine mode")

    @property
    def current_option(self) -> str | None:
        """Return the current machine state."""
        current = nested_value(machine_snapshot(self.coordinator.data), "state", "state")
        return current if current in self.options else None

    @property
    def available(self) -> bool:
        """Return whether the machine state can be changed."""
        return super().available and is_machine_connected(self.coordinator.data)

    async def async_select_option(self, option: str) -> None:
        """Request a machine state change."""
        if option not in self.options:
            raise ValueError(f"Unsupported machine state: {option}")
        await self.coordinator.client.async_set_machine_state(option)
        await self.coordinator.async_request_refresh()
