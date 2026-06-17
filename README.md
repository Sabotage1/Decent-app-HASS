# Decent Espresso Home Assistant Connector

Custom Home Assistant integration for the ReaPrime/Decent Espresso app local API.

For shareable setup instructions and a full entity list, see [INSTALL.md](INSTALL.md).

This does not talk BLE or USB to the coffee machine directly. ReaPrime keeps owning the machine and scale connection, and Home Assistant connects to ReaPrime over your LAN:

```text
Home Assistant -> http://<tablet-or-app-ip>:8080 -> ReaPrime/Decent Espresso app -> Decent machine / scale
```

The connector is based on ReaPrime `v0.7.6`, which exposes REST endpoints under `/api/v1/...` and WebSocket streams under `/ws/v1/...`.

## Requirements

- ReaPrime/Decent Espresso app `v0.7.6` or newer running on the same network as Home Assistant.
- The tablet or computer running ReaPrime must be reachable from Home Assistant on port `8080`.
- Home Assistant Core `2024.12.0` or newer.

## Installation

### One-command automated install

From the Home Assistant terminal:

```bash
curl -fsSL https://raw.githubusercontent.com/Sabotage1/Decent-app-HASS/main/scripts/install.sh | bash
```

The script installs the custom integration, installs the dashboard, then asks for the ReaPrime/Decent Espresso app IP address at the end. Restart Home Assistant when it finishes.

For non-interactive installs:

```bash
curl -fsSL https://raw.githubusercontent.com/Sabotage1/Decent-app-HASS/main/scripts/install.sh | REAPRIME_HOST=192.168.1.50 bash
```

### HACS custom repository

1. In HACS, add this repository as a custom integration repository.
2. Install **Decent Espresso Home Assistant Connector**.
3. Restart Home Assistant.
4. Go to **Settings -> Devices & services -> Add integration**.
5. Search for **Decent Espresso**.
6. Enter the tablet/app host and port, usually `8080`.

### Manual

Copy `custom_components/decent_reaprime` into your Home Assistant config directory:

```text
<home-assistant-config>/custom_components/decent_reaprime
```

Restart Home Assistant, then add **Decent Espresso** from **Settings -> Devices & services**.

## Entities

The integration creates sensors for:

- Machine state, pressure, target pressure, flow, target flow, temperatures, and profile frame.
- Scale weight, scale flow, scale battery, and scale timer.
- Tablet display brightness.
- Connected Decent Espresso device count.

It creates binary sensors for:

- App online.
- Machine connected.
- Scale connected.
- Device scan in progress.
- Cup warmer support.
- Wake-lock and low-battery brightness state.

It creates controls for:

- Scanning and auto-connecting Decent Espresso devices.
- Taring the scale and controlling the scale timer.
- Display brightness.
- Requesting and releasing tablet wake-lock.
- Setting machine mode.
- Bengle cup warmer temperature when the connected machine supports it.

## Services

The integration also registers services under `decent_reaprime`:

- `scan_devices`
- `connect_device`
- `disconnect_device`
- `set_machine_state`
- `tare_scale`
- `scale_timer_start`
- `scale_timer_stop`
- `scale_timer_reset`
- `set_cup_warmer`

Use the `Connected devices` sensor attributes or ReaPrime's `/api/v1/devices` endpoint to find device IDs when using `connect_device` or `disconnect_device`.

## Dashboard

I included a ready-to-paste Lovelace dashboard at:

```text
dashboards/decent_espresso_dashboard.yaml
```

In Home Assistant, go to **Settings -> Dashboards -> Add dashboard -> New dashboard from scratch**, open the raw configuration editor, and paste the YAML. The dashboard assumes a fresh install where Home Assistant creates entity IDs like `sensor.decent_espresso_pressure`. If HA keeps older entity IDs, use **Settings -> Devices & services -> Entities** to confirm the names and adjust the YAML.

## Notes

- If ReaPrime is reachable but no machine is connected, machine entities stay unavailable until the app connects to the machine.
- If no scale is connected, scale entities and scale buttons stay unavailable.
- Setting machine mode can start machine actions such as espresso, steam, rinse, cleaning, or descaling. Use HA automations carefully.
