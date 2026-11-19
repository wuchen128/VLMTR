# -*- coding: utf-8 -*-
"""Configuration storage: %APPDATA%\\VLMTR\\config.json"""

import json
import os

from . import APP_NAME, VERSION


def config_path():
    appdata = os.environ.get("APPDATA") or os.path.expanduser("~")
    folder = os.path.join(appdata, APP_NAME)
    os.makedirs(folder, exist_ok=True)
    return os.path.join(folder, "config.json")


def load_config():
    try:
        with open(config_path(), "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_config(limit, locked, autostart):
    data = {
        "limit": limit,
        "locked": locked,
        "autostart": autostart,
        "version": VERSION,
    }
    try:
        with open(config_path(), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass
