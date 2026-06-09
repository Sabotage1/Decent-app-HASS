"""Constants for the Decent Espresso integration."""

from __future__ import annotations

from homeassistant.const import Platform

DOMAIN = "decent_reaprime"

DEFAULT_NAME = "Decent Espresso"
DEFAULT_PORT = 8080
DEFAULT_SCAN_INTERVAL = 30
DEFAULT_TIMEOUT = 10

DATA_CLIENT = "client"
DATA_COORDINATOR = "coordinator"

PLATFORMS: tuple[Platform, ...] = (
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.NUMBER,
    Platform.SELECT,
)

CONF_TIMEOUT = "timeout"

MANUFACTURER = "Decent Espresso / ReaPrime"
MODEL = "Decent.app bridge"

MACHINE_STATE_OPTIONS: list[str] = [
    "idle",
    "sleeping",
    "espresso",
    "steam",
    "hotWater",
    "flush",
    "steamRinse",
    "skipStep",
    "cleaning",
    "descaling",
]
