#!/usr/bin/env python3
"""Update Home Assistant YAML config for the Decent Espresso connector."""

from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path
from typing import Any


DOMAIN_BLOCK = """\
decent_reaprime:
  host: {host}
  port: 8080

lovelace:
  dashboards:
    decent-espresso:
      mode: yaml
      title: Decent Espresso
      icon: mdi:coffee-maker
      show_in_sidebar: true
      filename: dashboards/decent_espresso_dashboard.yaml
"""


def _has_top_level_key(text: str, key: str) -> bool:
    return re.search(rf"(?m)^{re.escape(key)}:\s*(?:#.*)?$", text) is not None


def _append_simple_config(config_path: Path, host: str) -> None:
    text = config_path.read_text() if config_path.exists() else ""
    suffix = "\n" if text and not text.endswith("\n") else ""
    config_path.write_text(f"{text}{suffix}\n{DOMAIN_BLOCK.format(host=host)}")


def _merge_with_pyyaml(config_path: Path, host: str) -> None:
    try:
        import yaml
    except ImportError as err:
        raise RuntimeError(
            "PyYAML is required to merge with an existing lovelace or "
            "decent_reaprime block. Install PyYAML or add the dashboard and "
            "integration YAML manually."
        ) from err

    if config_path.exists():
        current = yaml.safe_load(config_path.read_text()) or {}
        if not isinstance(current, dict):
            raise RuntimeError("configuration.yaml root must be a mapping")
    else:
        current = {}

    current["decent_reaprime"] = {
        "host": host,
        "port": 8080,
    }

    lovelace = current.setdefault("lovelace", {})
    if not isinstance(lovelace, dict):
        raise RuntimeError("configuration.yaml lovelace block must be a mapping")
    dashboards = lovelace.setdefault("dashboards", {})
    if not isinstance(dashboards, dict):
        raise RuntimeError("configuration.yaml lovelace.dashboards block must be a mapping")
    dashboards["decent-espresso"] = {
        "mode": "yaml",
        "title": "Decent Espresso",
        "icon": "mdi:coffee-maker",
        "show_in_sidebar": True,
        "filename": "dashboards/decent_espresso_dashboard.yaml",
    }

    if config_path.exists():
        backup_path = config_path.with_suffix(".yaml.decent-espresso.bak")
        shutil.copy2(config_path, backup_path)
        print(f"Backed up existing configuration to {backup_path}")

    config_path.write_text(yaml.safe_dump(current, sort_keys=False))


def update_config(config_dir: Path, host: str) -> None:
    """Install or update Decent Espresso YAML configuration."""
    config_path = config_dir / "configuration.yaml"
    text = config_path.read_text() if config_path.exists() else ""

    if not _has_top_level_key(text, "lovelace") and not _has_top_level_key(
        text,
        "decent_reaprime",
    ):
        _append_simple_config(config_path, host)
        return

    _merge_with_pyyaml(config_path, host)


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("Usage: install_config.py <ha-config-dir> <reaprime-host>", file=sys.stderr)
        return 2

    config_dir = Path(argv[1]).expanduser().resolve()
    host = argv[2].strip()
    if not host:
        print("ReaPrime host/IP cannot be empty", file=sys.stderr)
        return 2
    if not config_dir.exists():
        print(f"Home Assistant config directory does not exist: {config_dir}", file=sys.stderr)
        return 2

    update_config(config_dir, host)
    print("Updated Home Assistant YAML configuration")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
