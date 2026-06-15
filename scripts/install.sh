#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://github.com/Sabotage1/Decent-app-HASS"
ARCHIVE_URL="${REPO_URL}/archive/refs/heads/main.tar.gz"

CONFIG_DIR="${HA_CONFIG_DIR:-/config}"
if [[ ! -d "$CONFIG_DIR" && -f "configuration.yaml" ]]; then
  CONFIG_DIR="$PWD"
fi

if [[ ! -d "$CONFIG_DIR" ]]; then
  echo "Could not find the Home Assistant config directory."
  echo "Run this from Home Assistant, or set HA_CONFIG_DIR=/path/to/config."
  exit 1
fi

SCRIPT_PATH="${BASH_SOURCE[0]:-}"
if [[ -n "$SCRIPT_PATH" && -f "$SCRIPT_PATH" ]]; then
  SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_PATH")" && pwd)"
  REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
else
  REPO_ROOT=""
fi

TMP_DIR=""
cleanup() {
  if [[ -n "$TMP_DIR" && -d "$TMP_DIR" ]]; then
    rm -rf "$TMP_DIR"
  fi
}
trap cleanup EXIT

if [[ -z "$REPO_ROOT" || ! -f "$REPO_ROOT/custom_components/decent_reaprime/manifest.json" ]]; then
  TMP_DIR="$(mktemp -d)"
  echo "Downloading Decent Espresso connector..."
  curl -fsSL "$ARCHIVE_URL" | tar -xz -C "$TMP_DIR"
  REPO_ROOT="$(find "$TMP_DIR" -maxdepth 1 -type d -name "Decent-app-HASS-*" | head -n 1)"
fi

if [[ -z "$REPO_ROOT" || ! -f "$REPO_ROOT/custom_components/decent_reaprime/manifest.json" ]]; then
  echo "Could not locate connector files."
  exit 1
fi

echo "Installing custom integration into $CONFIG_DIR/custom_components/decent_reaprime"
mkdir -p "$CONFIG_DIR/custom_components"
rm -rf "$CONFIG_DIR/custom_components/decent_reaprime"
cp -R "$REPO_ROOT/custom_components/decent_reaprime" "$CONFIG_DIR/custom_components/decent_reaprime"

echo "Installing dashboard YAML into $CONFIG_DIR/dashboards/decent_espresso_dashboard.yaml"
mkdir -p "$CONFIG_DIR/dashboards"
cp "$REPO_ROOT/dashboards/decent_espresso_dashboard.yaml" "$CONFIG_DIR/dashboards/decent_espresso_dashboard.yaml"

echo
read -r -p "Enter the ReaPrime/Decent Espresso app IP or hostname: " REAPRIME_HOST
if [[ -z "$REAPRIME_HOST" ]]; then
  echo "IP/hostname cannot be empty."
  exit 1
fi

python3 "$REPO_ROOT/scripts/install_config.py" "$CONFIG_DIR" "$REAPRIME_HOST"

echo
echo "Install complete."
echo "Restart Home Assistant."
echo "After restart, Home Assistant will import Decent Espresso from YAML."
echo "The dashboard will appear in the sidebar as Decent Espresso."
