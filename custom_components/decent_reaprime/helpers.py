"""Shared helpers for Decent ReaPrime entities."""

from __future__ import annotations

from typing import Any


def machine_snapshot(data: dict[str, Any] | None) -> dict[str, Any] | None:
    """Return the latest machine snapshot."""
    if not data:
        return None
    snapshot = data.get("machine")
    return snapshot if isinstance(snapshot, dict) else None


def scale_snapshot(data: dict[str, Any] | None) -> dict[str, Any] | None:
    """Return the latest scale snapshot."""
    if not data:
        return None
    snapshot = data.get("scale")
    return snapshot if isinstance(snapshot, dict) else None


def display_state(data: dict[str, Any] | None) -> dict[str, Any] | None:
    """Return the latest display state."""
    if not data:
        return None
    display = data.get("display")
    return display if isinstance(display, dict) else None


def capabilities(data: dict[str, Any] | None) -> list[str]:
    """Return machine capabilities."""
    if not data:
        return []
    value = data.get("capabilities")
    return value if isinstance(value, list) else []


def cup_warmer_state(data: dict[str, Any] | None) -> dict[str, Any] | None:
    """Return the Bengle cup warmer state."""
    if not data:
        return None
    state = data.get("cup_warmer")
    return state if isinstance(state, dict) else None


def device_list(data: dict[str, Any] | None) -> list[dict[str, Any]]:
    """Return known ReaPrime devices."""
    if not data:
        return []
    devices = data.get("devices")
    return devices if isinstance(devices, list) else []


def connected_device(data: dict[str, Any] | None, device_type: str) -> dict[str, Any] | None:
    """Return the first connected device of a given type."""
    for device in device_list(data):
        if device.get("type") == device_type and device.get("state") == "connected":
            return device
    return None


def is_machine_connected(data: dict[str, Any] | None) -> bool:
    """Return whether a machine is connected."""
    devices = device_list(data)
    if devices:
        return connected_device(data, "machine") is not None
    snapshot = machine_snapshot(data)
    return snapshot is not None and "state" in snapshot


def is_scale_connected(data: dict[str, Any] | None) -> bool:
    """Return whether a scale is connected."""
    if not data:
        return False
    status = data.get("scale_status")
    if status in ("connected", "disconnected"):
        return status == "connected"
    devices = device_list(data)
    if devices:
        return connected_device(data, "scale") is not None
    return scale_snapshot(data) is not None


def is_cup_warmer_supported(data: dict[str, Any] | None) -> bool:
    """Return whether the connected machine supports the cup warmer endpoint."""
    return "cupWarmer" in capabilities(data)


def nested_value(data: dict[str, Any] | None, *path: str) -> Any:
    """Return a nested value from a mapping."""
    current: Any = data
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current
