"""Client for the Decent ReaPrime local API."""

from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator
from typing import Any

import aiohttp
from homeassistant.const import CONF_HOST, CONF_PORT

from .const import DEFAULT_PORT, DEFAULT_TIMEOUT


class ReaPrimeError(Exception):
    """Base error for ReaPrime API problems."""


class CannotConnect(ReaPrimeError):
    """Raised when the ReaPrime app cannot be reached."""


class ReaPrimeApiError(ReaPrimeError):
    """Raised when the ReaPrime app returns an unexpected response."""

    def __init__(self, status: int, message: str) -> None:
        """Initialize the API error."""
        super().__init__(f"ReaPrime API returned HTTP {status}: {message}")
        self.status = status
        self.message = message


class ReaPrimeClient:
    """Small async client for the local ReaPrime REST and WebSocket API."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        host: str,
        port: int = DEFAULT_PORT,
        *,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        """Initialize the client."""
        self._session = session
        self._host = host.strip()
        self._port = port
        self._timeout = timeout

    @classmethod
    def from_config_entry(
        cls,
        session: aiohttp.ClientSession,
        data: dict[str, Any],
    ) -> "ReaPrimeClient":
        """Build a client from a Home Assistant config entry data dict."""
        return cls(
            session,
            data[CONF_HOST],
            data.get(CONF_PORT, DEFAULT_PORT),
        )

    @property
    def host(self) -> str:
        """Return the configured host."""
        return self._host

    @property
    def port(self) -> int:
        """Return the configured port."""
        return self._port

    @property
    def base_url(self) -> str:
        """Return the base HTTP URL."""
        return f"http://{self._host}:{self._port}"

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def _ws_url(self, path: str) -> str:
        return f"ws://{self._host}:{self._port}{path}"

    async def _request(
        self,
        method: str,
        path: str,
        *,
        json_payload: Any | None = None,
        params: dict[str, Any] | None = None,
        expected_statuses: tuple[int, ...] = (200, 202),
    ) -> Any:
        """Make a REST request and decode JSON."""
        try:
            async with asyncio.timeout(self._timeout):
                async with self._session.request(
                    method,
                    self._url(path),
                    json=json_payload,
                    params=params,
                ) as response:
                    text = await response.text()
                    if response.status not in expected_statuses:
                        raise ReaPrimeApiError(response.status, text)
                    if not text:
                        return None
                    try:
                        return json.loads(text)
                    except json.JSONDecodeError as err:
                        raise ReaPrimeApiError(response.status, text) from err
        except (TimeoutError, aiohttp.ClientError) as err:
            raise CannotConnect(str(err)) from err

    async def async_ping(self) -> None:
        """Check that the ReaPrime app is reachable."""
        await self.async_get_devices()

    async def async_get_devices(self) -> list[dict[str, Any]]:
        """Return known devices."""
        data = await self._request("GET", "/api/v1/devices")
        return data if isinstance(data, list) else []

    async def async_scan_devices(
        self,
        *,
        connect: bool = True,
        quick: bool = False,
    ) -> list[dict[str, Any]]:
        """Start a scan, optionally asking ReaPrime to auto-connect."""
        data = await self._request(
            "GET",
            "/api/v1/devices/scan",
            params={
                "connect": "true" if connect else "false",
                "quick": "true" if quick else "false",
            },
        )
        return data if isinstance(data, list) else []

    async def async_connect_device(self, device_id: str) -> None:
        """Connect a discovered machine, scale, or sensor by ReaPrime device ID."""
        await self._request(
            "PUT",
            "/api/v1/devices/connect",
            json_payload={"deviceId": device_id},
        )

    async def async_disconnect_device(self, device_id: str) -> None:
        """Disconnect a machine, scale, or sensor by ReaPrime device ID."""
        await self._request(
            "PUT",
            "/api/v1/devices/disconnect",
            json_payload={"deviceId": device_id},
        )

    async def async_get_machine_state(self) -> dict[str, Any] | None:
        """Return the current machine snapshot, or None when no machine is connected."""
        try:
            data = await self._request("GET", "/api/v1/machine/state")
        except ReaPrimeApiError as err:
            if err.status in (404, 500):
                return None
            raise
        return data if isinstance(data, dict) else None

    async def async_get_machine_info(self) -> dict[str, Any] | None:
        """Return machine information, or None when no machine is connected."""
        try:
            data = await self._request("GET", "/api/v1/machine/info")
        except ReaPrimeApiError as err:
            if err.status in (404, 500):
                return None
            raise
        return data if isinstance(data, dict) else None

    async def async_set_machine_state(self, state: str) -> None:
        """Request a machine state change."""
        await self._request("PUT", f"/api/v1/machine/state/{state}")

    async def async_get_capabilities(self) -> list[str]:
        """Return optional machine capabilities."""
        try:
            data = await self._request("GET", "/api/v1/machine/capabilities")
        except ReaPrimeApiError as err:
            if err.status in (404, 500):
                return []
            raise
        if isinstance(data, dict) and isinstance(data.get("capabilities"), list):
            return [str(capability) for capability in data["capabilities"]]
        return []

    async def async_get_cup_warmer(self) -> dict[str, Any] | None:
        """Return Bengle cup warmer state when supported."""
        try:
            data = await self._request("GET", "/api/v1/machine/cupWarmer")
        except ReaPrimeApiError as err:
            if err.status in (404, 500):
                return None
            raise
        return data if isinstance(data, dict) else None

    async def async_set_cup_warmer_temperature(self, temperature: float) -> None:
        """Set Bengle cup warmer temperature in degrees Celsius."""
        await self._request(
            "PUT",
            "/api/v1/machine/cupWarmer",
            json_payload={"temperature": temperature},
        )

    async def async_tare_scale(self) -> None:
        """Tare the connected scale."""
        await self._request("PUT", "/api/v1/scale/tare")

    async def async_scale_timer_start(self) -> None:
        """Start the connected scale timer."""
        await self._request("PUT", "/api/v1/scale/timer/start")

    async def async_scale_timer_stop(self) -> None:
        """Stop the connected scale timer."""
        await self._request("PUT", "/api/v1/scale/timer/stop")

    async def async_scale_timer_reset(self) -> None:
        """Reset the connected scale timer."""
        await self._request("PUT", "/api/v1/scale/timer/reset")

    async def async_get_display(self) -> dict[str, Any] | None:
        """Return tablet display state."""
        try:
            data = await self._request("GET", "/api/v1/display")
        except ReaPrimeApiError as err:
            if err.status in (404, 500):
                return None
            raise
        return data if isinstance(data, dict) else None

    async def async_set_brightness(self, brightness: int) -> dict[str, Any] | None:
        """Set tablet brightness to a value from 0 to 100."""
        data = await self._request(
            "PUT",
            "/api/v1/display/brightness",
            json_payload={"brightness": brightness},
        )
        return data if isinstance(data, dict) else None

    async def async_request_wakelock(self) -> dict[str, Any] | None:
        """Request a tablet wake-lock override."""
        data = await self._request("POST", "/api/v1/display/wakelock")
        return data if isinstance(data, dict) else None

    async def async_release_wakelock(self) -> dict[str, Any] | None:
        """Release a tablet wake-lock override."""
        data = await self._request("DELETE", "/api/v1/display/wakelock")
        return data if isinstance(data, dict) else None

    async def async_ws_messages(self, path: str) -> AsyncIterator[dict[str, Any]]:
        """Yield JSON messages from a ReaPrime WebSocket path."""
        try:
            async with self._session.ws_connect(
                self._ws_url(path),
                heartbeat=20,
            ) as websocket:
                async for message in websocket:
                    if message.type is aiohttp.WSMsgType.TEXT:
                        try:
                            payload = json.loads(message.data)
                        except json.JSONDecodeError:
                            continue
                        if isinstance(payload, dict):
                            yield payload
                    elif message.type in (
                        aiohttp.WSMsgType.CLOSED,
                        aiohttp.WSMsgType.CLOSE,
                        aiohttp.WSMsgType.CLOSING,
                    ):
                        break
                    elif message.type is aiohttp.WSMsgType.ERROR:
                        raise CannotConnect(str(websocket.exception()))
        except (TimeoutError, aiohttp.ClientError) as err:
            raise CannotConnect(str(err)) from err
