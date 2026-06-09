"""Data coordinator for Decent ReaPrime."""

from __future__ import annotations

import asyncio
from collections.abc import Callable, Coroutine
from datetime import timedelta
from logging import Logger
from typing import Any

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import CannotConnect, ReaPrimeApiError, ReaPrimeClient
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

PayloadHandler = Callable[[dict[str, Any], dict[str, Any]], None]


class ReaPrimeDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinate REST polling and WebSocket push updates."""

    def __init__(
        self,
        hass: HomeAssistant,
        logger: Logger,
        client: ReaPrimeClient,
        *,
        update_interval_seconds: int = DEFAULT_SCAN_INTERVAL,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            logger,
            name=DOMAIN,
            update_interval=timedelta(seconds=update_interval_seconds),
        )
        self.client = client
        self._tasks: list[asyncio.Task[None]] = []

    async def _async_update_data(self) -> dict[str, Any]:
        """Poll a stable baseline from the REST API."""
        data = dict(self.data or {})
        data["app_online"] = True

        try:
            devices = await self.client.async_get_devices()
        except CannotConnect as err:
            raise UpdateFailed(f"Cannot connect to ReaPrime: {err}") from err
        except ReaPrimeApiError as err:
            raise UpdateFailed(f"ReaPrime devices request failed: {err}") from err

        data["devices"] = devices
        data["display"] = await self._optional(self.client.async_get_display)
        data["machine"] = await self._optional(self.client.async_get_machine_state)
        data["machine_info"] = await self._optional(self.client.async_get_machine_info)
        data["capabilities"] = await self._optional(self.client.async_get_capabilities) or []
        data["cup_warmer"] = await self._optional(self.client.async_get_cup_warmer)

        return data

    async def _optional(
        self,
        call: Callable[[], Coroutine[Any, Any, Any]],
    ) -> Any:
        """Run an optional API call without failing setup on missing hardware."""
        try:
            return await call()
        except (CannotConnect, ReaPrimeApiError) as err:
            self.logger.debug("Optional ReaPrime request failed: %s", err)
            return None

    def start_websockets(self) -> None:
        """Start WebSocket listeners."""
        if self._tasks:
            return
        watches: tuple[tuple[str, PayloadHandler], ...] = (
            ("/ws/v1/machine/snapshot", self._handle_machine_snapshot),
            ("/ws/v1/scale/snapshot", self._handle_scale_snapshot),
            ("/ws/v1/devices", self._handle_devices_state),
            ("/ws/v1/display", self._handle_display_state),
        )
        for path, handler in watches:
            self._tasks.append(self.hass.async_create_task(self._watch(path, handler)))

    async def async_shutdown(self) -> None:
        """Stop WebSocket listeners."""
        tasks = list(self._tasks)
        self._tasks.clear()
        for task in tasks:
            task.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _watch(self, path: str, handler: PayloadHandler) -> None:
        """Run a reconnecting WebSocket listener."""
        while True:
            try:
                async for payload in self.client.async_ws_messages(path):
                    self._merge_payload(payload, handler)
            except asyncio.CancelledError:
                raise
            except CannotConnect as err:
                self.logger.debug("ReaPrime WebSocket %s disconnected: %s", path, err)
            except Exception as err:  # noqa: BLE001 - keep listener alive
                self.logger.debug("ReaPrime WebSocket %s failed: %s", path, err)
            await asyncio.sleep(5)

    @callback
    def _merge_payload(self, payload: dict[str, Any], handler: PayloadHandler) -> None:
        """Merge a pushed payload into coordinator data."""
        data = dict(self.data or {})
        data["app_online"] = True
        handler(data, payload)
        self.async_set_updated_data(data)

    @staticmethod
    def _handle_machine_snapshot(
        data: dict[str, Any],
        payload: dict[str, Any],
    ) -> None:
        if "error" in payload:
            data["machine"] = None
            data["machine_error"] = payload["error"]
            return
        data["machine"] = payload
        data.pop("machine_error", None)

    @staticmethod
    def _handle_scale_snapshot(
        data: dict[str, Any],
        payload: dict[str, Any],
    ) -> None:
        status = payload.get("status")
        if status in ("connected", "disconnected"):
            data["scale_status"] = status
            if status == "disconnected":
                data["scale"] = None
            return
        data["scale"] = payload
        data["scale_status"] = "connected"

    @staticmethod
    def _handle_devices_state(
        data: dict[str, Any],
        payload: dict[str, Any],
    ) -> None:
        devices = payload.get("devices")
        if isinstance(devices, list):
            data["devices"] = devices
        data["scanning"] = bool(payload.get("scanning", False))
        if isinstance(payload.get("connectionStatus"), dict):
            data["connection_status"] = payload["connectionStatus"]
        if isinstance(payload.get("charging"), dict):
            data["charging"] = payload["charging"]

    @staticmethod
    def _handle_display_state(
        data: dict[str, Any],
        payload: dict[str, Any],
    ) -> None:
        data["display"] = payload
