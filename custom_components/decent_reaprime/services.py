"""Services for Decent ReaPrime."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.const import ATTR_DEVICE_ID
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from .api import ReaPrimeClient
from .const import DATA_CLIENT, DATA_COORDINATOR, DOMAIN, MACHINE_STATE_OPTIONS
from .coordinator import ReaPrimeDataUpdateCoordinator

SERVICE_SCAN_DEVICES = "scan_devices"
SERVICE_CONNECT_DEVICE = "connect_device"
SERVICE_DISCONNECT_DEVICE = "disconnect_device"
SERVICE_SET_MACHINE_STATE = "set_machine_state"
SERVICE_TARE_SCALE = "tare_scale"
SERVICE_SCALE_TIMER_START = "scale_timer_start"
SERVICE_SCALE_TIMER_STOP = "scale_timer_stop"
SERVICE_SCALE_TIMER_RESET = "scale_timer_reset"
SERVICE_SET_CUP_WARMER = "set_cup_warmer"

ATTR_CONNECT = "connect"
ATTR_ENTRY_ID = "entry_id"
ATTR_QUICK = "quick"
ATTR_STATE = "state"
ATTR_TEMPERATURE = "temperature"

SCAN_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_ENTRY_ID): cv.string,
        vol.Optional(ATTR_CONNECT, default=True): cv.boolean,
        vol.Optional(ATTR_QUICK, default=True): cv.boolean,
    }
)
DEVICE_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_ENTRY_ID): cv.string,
        vol.Required(ATTR_DEVICE_ID): cv.string,
    }
)
STATE_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_ENTRY_ID): cv.string,
        vol.Required(ATTR_STATE): vol.In(MACHINE_STATE_OPTIONS),
    }
)
ENTRY_SCHEMA = vol.Schema({vol.Optional(ATTR_ENTRY_ID): cv.string})
CUP_WARMER_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_ENTRY_ID): cv.string,
        vol.Required(ATTR_TEMPERATURE): vol.All(
            vol.Coerce(float),
            vol.Range(min=0, max=80),
        ),
    }
)


def _integration_data(hass: HomeAssistant, entry_id: str | None) -> dict[str, Any]:
    entries = hass.data.get(DOMAIN, {})
    if entry_id is not None:
        return entries[entry_id]
    if not entries:
        raise ValueError("No Decent Espresso entries are loaded")
    return next(iter(entries.values()))


def _client(hass: HomeAssistant, call: ServiceCall) -> ReaPrimeClient:
    return _integration_data(hass, call.data.get(ATTR_ENTRY_ID))[DATA_CLIENT]


def _coordinator(
    hass: HomeAssistant,
    call: ServiceCall,
) -> ReaPrimeDataUpdateCoordinator:
    return _integration_data(hass, call.data.get(ATTR_ENTRY_ID))[DATA_COORDINATOR]


async def async_register_services(hass: HomeAssistant) -> None:
    """Register Decent ReaPrime services once."""
    if hass.services.has_service(DOMAIN, SERVICE_SCAN_DEVICES):
        return

    async def scan_devices(call: ServiceCall) -> None:
        client = _client(hass, call)
        coordinator = _coordinator(hass, call)
        await client.async_scan_devices(
            connect=call.data[ATTR_CONNECT],
            quick=call.data[ATTR_QUICK],
        )
        await coordinator.async_request_refresh()

    async def connect_device(call: ServiceCall) -> None:
        client = _client(hass, call)
        coordinator = _coordinator(hass, call)
        await client.async_connect_device(call.data[ATTR_DEVICE_ID])
        await coordinator.async_request_refresh()

    async def disconnect_device(call: ServiceCall) -> None:
        client = _client(hass, call)
        coordinator = _coordinator(hass, call)
        await client.async_disconnect_device(call.data[ATTR_DEVICE_ID])
        await coordinator.async_request_refresh()

    async def set_machine_state(call: ServiceCall) -> None:
        client = _client(hass, call)
        coordinator = _coordinator(hass, call)
        await client.async_set_machine_state(call.data[ATTR_STATE])
        await coordinator.async_request_refresh()

    async def tare_scale(call: ServiceCall) -> None:
        client = _client(hass, call)
        coordinator = _coordinator(hass, call)
        await client.async_tare_scale()
        await coordinator.async_request_refresh()

    async def scale_timer_start(call: ServiceCall) -> None:
        client = _client(hass, call)
        coordinator = _coordinator(hass, call)
        await client.async_scale_timer_start()
        await coordinator.async_request_refresh()

    async def scale_timer_stop(call: ServiceCall) -> None:
        client = _client(hass, call)
        coordinator = _coordinator(hass, call)
        await client.async_scale_timer_stop()
        await coordinator.async_request_refresh()

    async def scale_timer_reset(call: ServiceCall) -> None:
        client = _client(hass, call)
        coordinator = _coordinator(hass, call)
        await client.async_scale_timer_reset()
        await coordinator.async_request_refresh()

    async def set_cup_warmer(call: ServiceCall) -> None:
        client = _client(hass, call)
        coordinator = _coordinator(hass, call)
        await client.async_set_cup_warmer_temperature(call.data[ATTR_TEMPERATURE])
        await coordinator.async_request_refresh()

    hass.services.async_register(
        DOMAIN,
        SERVICE_SCAN_DEVICES,
        scan_devices,
        schema=SCAN_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_CONNECT_DEVICE,
        connect_device,
        schema=DEVICE_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_DISCONNECT_DEVICE,
        disconnect_device,
        schema=DEVICE_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_MACHINE_STATE,
        set_machine_state,
        schema=STATE_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_TARE_SCALE,
        tare_scale,
        schema=ENTRY_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SCALE_TIMER_START,
        scale_timer_start,
        schema=ENTRY_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SCALE_TIMER_STOP,
        scale_timer_stop,
        schema=ENTRY_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SCALE_TIMER_RESET,
        scale_timer_reset,
        schema=ENTRY_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_CUP_WARMER,
        set_cup_warmer,
        schema=CUP_WARMER_SCHEMA,
    )


async def async_unregister_services(hass: HomeAssistant) -> None:
    """Unregister Decent ReaPrime services."""
    for service in (
        SERVICE_SCAN_DEVICES,
        SERVICE_CONNECT_DEVICE,
        SERVICE_DISCONNECT_DEVICE,
        SERVICE_SET_MACHINE_STATE,
        SERVICE_TARE_SCALE,
        SERVICE_SCALE_TIMER_START,
        SERVICE_SCALE_TIMER_STOP,
        SERVICE_SCALE_TIMER_RESET,
        SERVICE_SET_CUP_WARMER,
    ):
        if hass.services.has_service(DOMAIN, service):
            hass.services.async_remove(DOMAIN, service)
