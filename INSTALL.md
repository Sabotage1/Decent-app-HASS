# Decent Espresso Home Assistant Install Guide

This guide explains how to install the **Decent Espresso Home Assistant Connector** and what entities you will see in Home Assistant.

The connector does not connect directly to the coffee machine over BLE or USB. The ReaPrime/Decent Espresso app stays connected to the machine, and Home Assistant connects to the app over your local network.

```text
Home Assistant -> http://<tablet-or-app-ip>:8080 -> ReaPrime/Decent Espresso app -> Decent machine / scale
```

## Requirements

- ReaPrime/Decent Espresso app `v0.7.6` or newer.
- The app must be running on the same network as Home Assistant.
- Home Assistant must be able to reach the app on port `8080`.
- Home Assistant Core `2024.12.0` or newer.

Do not expose port `8080` to the internet. Keep it on your trusted local network.

## Step 1: Prepare the ReaPrime App

There is nothing extra to install inside the ReaPrime app.

1. Install and open ReaPrime/Decent Espresso on the tablet or computer that talks to the coffee machine.
2. Connect your Decent machine in the app as usual.
3. Connect your scale in the app if you use one.
4. Find the IP address of the tablet or computer running the app.

You can test the app API from another device on the same network:

```bash
curl http://192.168.1.50:8080/api/v1/devices
```

Replace `192.168.1.50` with the IP address of your tablet or computer. If the API is reachable, you should get a JSON response.

## One-Command Automated Install

If you have Terminal/SSH access to Home Assistant, this is the easiest path.
It installs the integration, registers the dashboard, and asks for the
ReaPrime/Decent Espresso app IP address at the end.

Run this from the Home Assistant terminal:

```bash
curl -fsSL https://raw.githubusercontent.com/Sabotage1/Decent-app-HASS/main/scripts/install.sh | bash
```

The script prompts for the ReaPrime/Decent Espresso app IP address even when it
is installed with `curl | bash`.

If your Home Assistant config directory is not `/config`, set it explicitly:

```bash
curl -fsSL https://raw.githubusercontent.com/Sabotage1/Decent-app-HASS/main/scripts/install.sh | HA_CONFIG_DIR=/path/to/config bash
```

For a fully non-interactive install, pass the IP address with `REAPRIME_HOST`:

```bash
curl -fsSL https://raw.githubusercontent.com/Sabotage1/Decent-app-HASS/main/scripts/install.sh | REAPRIME_HOST=192.168.1.50 bash
```

When the script asks:

```text
Enter the ReaPrime/Decent Espresso app IP or hostname:
```

enter the IP address of the tablet or computer running the app, for example:

```text
192.168.1.50
```

Then restart Home Assistant. After restart, Home Assistant imports the Decent
Espresso integration from YAML and shows the dashboard in the sidebar.

For fresh/default configs, the installer separates the appended YAML with blank
lines and sets `lovelace: mode: storage` so existing UI-controlled dashboards
continue to load normally.

The Home Assistant SSH add-on does not always include Python. The installer
does not require Python for a normal install. If your `configuration.yaml`
already has a `lovelace:` or `decent_reaprime:` block, the script installs the
files and prints a YAML snippet for you to merge manually instead of changing
your existing YAML automatically.

## Manual Install in Home Assistant

### Option A: HACS Custom Repository

1. Open **HACS** in Home Assistant.
2. Open the three-dot menu.
3. Choose **Custom repositories**.
4. Paste the GitHub repository URL for this connector.
5. Set the category to **Integration**.
6. Click **Add**.
7. Search HACS for **Decent Espresso Home Assistant Connector**.
8. Install it.
9. Restart Home Assistant.

### Option B: Manual Install

Copy this folder from the repository:

```text
custom_components/decent_reaprime
```

Into your Home Assistant config folder:

```text
/config/custom_components/decent_reaprime
```

Then restart Home Assistant.

## Add the Integration Manually

1. Go to **Settings -> Devices & services**.
2. Click **Add integration**.
3. Search for **Decent Espresso**.
4. Enter the IP address or hostname of the tablet/computer running ReaPrime.
5. Use port `8080` unless you changed it.
6. Click **Submit**.

If setup succeeds, Home Assistant will create a **Decent Espresso** device with sensors and controls.

If you used the one-command automated installer, you can skip this manual add
step. The integration is imported from `configuration.yaml` after restart.

## Optional Dashboard

This repository includes a ready-to-paste dashboard:

```text
dashboards/decent_espresso_dashboard.yaml
```

To install it:

1. Go to **Settings -> Dashboards**.
2. Click **Add dashboard**.
3. Choose **New dashboard from scratch**.
4. Open the raw YAML editor.
5. Paste the contents of `dashboards/decent_espresso_dashboard.yaml`.
6. Save.

The dashboard assumes Home Assistant creates entity IDs like `sensor.decent_espresso_pressure`. If your entity IDs are different, edit the YAML to match your actual entity IDs.

## Available Sensor Entities

These are the normal Home Assistant `sensor` entities created by the integration.

| Entity | What it shows | Unit |
| --- | --- | --- |
| `sensor.decent_espresso_machine_state` | Current machine state, such as idle, sleeping, espresso, steam, or hotWater | text |
| `sensor.decent_espresso_pressure` | Current brew pressure | bar |
| `sensor.decent_espresso_target_pressure` | Current target pressure | bar |
| `sensor.decent_espresso_flow` | Current machine flow | mL/s |
| `sensor.decent_espresso_target_flow` | Current target flow | mL/s |
| `sensor.decent_espresso_mix_temperature` | Current mix temperature | C |
| `sensor.decent_espresso_group_temperature` | Current group temperature | C |
| `sensor.decent_espresso_target_mix_temperature` | Target mix temperature | C |
| `sensor.decent_espresso_target_group_temperature` | Target group temperature | C |
| `sensor.decent_espresso_steam_temperature` | Steam temperature | C |
| `sensor.decent_espresso_profile_frame` | Current profile frame | count |
| `sensor.decent_espresso_scale_weight` | Connected scale weight | g |
| `sensor.decent_espresso_scale_flow` | Scale-derived flow | g/s |
| `sensor.decent_espresso_scale_battery` | Scale battery level when reported by the scale | % |
| `sensor.decent_espresso_scale_timer` | Scale timer value | s |
| `sensor.decent_espresso_display_brightness` | Tablet/app display brightness | % |
| `sensor.decent_espresso_connected_devices` | Number of connected ReaPrime devices; attributes include the device list | count |

Machine sensors are unavailable until a machine is connected in ReaPrime. Scale sensors are unavailable until a scale is connected.

## Available Binary Sensors

These show yes/no states.

| Entity | What it shows |
| --- | --- |
| `binary_sensor.decent_espresso_app_online` | Whether Home Assistant can reach the app |
| `binary_sensor.decent_espresso_machine_connected` | Whether a machine is connected |
| `binary_sensor.decent_espresso_scale_connected` | Whether a scale is connected |
| `binary_sensor.decent_espresso_scanning` | Whether ReaPrime is currently scanning for devices |
| `binary_sensor.decent_espresso_cup_warmer_supported` | Whether the connected machine supports the Bengle cup warmer endpoint |
| `binary_sensor.decent_espresso_wake_lock` | Whether wake lock is active |
| `binary_sensor.decent_espresso_wake_lock_override` | Whether a wake-lock override is active |
| `binary_sensor.decent_espresso_low_battery_brightness_limit` | Whether low-battery brightness limiting is active |

## Available Controls

The integration also creates Home Assistant controls.

| Entity | What it does |
| --- | --- |
| `select.decent_espresso_machine_mode` | Request machine states such as idle, sleeping, espresso, steam, hotWater, flush, cleaning, or descaling |
| `number.decent_espresso_display_brightness` | Set tablet/app display brightness from 0 to 100 |
| `number.decent_espresso_cup_warmer` | Set Bengle cup warmer temperature from 0 to 80 C; 0 turns it off |
| `button.decent_espresso_scan_devices` | Start a device scan |
| `button.decent_espresso_auto_connect` | Scan and auto-connect preferred or single discovered devices |
| `button.decent_espresso_tare_scale` | Tare the connected scale |
| `button.decent_espresso_start_scale_timer` | Start the connected scale timer |
| `button.decent_espresso_stop_scale_timer` | Stop the connected scale timer |
| `button.decent_espresso_reset_scale_timer` | Reset the connected scale timer |
| `button.decent_espresso_request_wake_lock` | Request a tablet wake-lock override |
| `button.decent_espresso_release_wake_lock` | Release the tablet wake-lock override |
| `button.decent_espresso_stop_machine` | Request machine idle state |
| `button.decent_espresso_sleep_machine` | Request machine sleeping state |

Be careful with automations that start machine states like espresso, steam, cleaning, or descaling.

## Available Services

Services are registered under the `decent_reaprime` domain:

| Service | Purpose |
| --- | --- |
| `decent_reaprime.scan_devices` | Ask the app to scan for devices |
| `decent_reaprime.connect_device` | Connect a discovered device by device ID |
| `decent_reaprime.disconnect_device` | Disconnect a device by device ID |
| `decent_reaprime.set_machine_state` | Request a machine state change |
| `decent_reaprime.tare_scale` | Tare the connected scale |
| `decent_reaprime.scale_timer_start` | Start the scale timer |
| `decent_reaprime.scale_timer_stop` | Stop the scale timer |
| `decent_reaprime.scale_timer_reset` | Reset the scale timer |
| `decent_reaprime.set_cup_warmer` | Set Bengle cup warmer temperature |

Use the attributes on `sensor.decent_espresso_connected_devices` or call the ReaPrime API endpoint `/api/v1/devices` to find device IDs.

## Troubleshooting

### Home Assistant cannot connect

Check that the app is running and reachable:

```bash
curl http://<tablet-or-app-ip>:8080/api/v1/devices
```

If this fails, check the tablet/computer IP address, firewall, VPN, and whether Home Assistant is on the same network.

### Machine sensors are unavailable

The app is reachable, but no machine is connected in ReaPrime. Connect the machine in the app first.

### Scale sensors are unavailable

No scale is connected in ReaPrime, or the scale does not report that value. Some scales do not report battery or timer data.

### Dashboard cards show missing entities

Home Assistant may have created different entity IDs. Go to **Settings -> Devices & services -> Entities**, search for **Decent Espresso**, and update the dashboard YAML with the actual entity IDs.
