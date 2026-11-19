# -*- coding: utf-8 -*-
"""Tray icon and context menu."""

import os
import sys

import pystray
from PIL import Image, ImageDraw

from . import APP_TITLE, VERSION

PRESET_LIMITS = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]


def _asset_path(name):
    """Load from assets/ in source mode, from the bundle when frozen."""
    base = getattr(sys, "_MEIPASS", None) or os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, "assets", name)


def make_icon_image():
    """Load assets/icon.png, falling back to a drawn icon if it is missing."""
    try:
        img = Image.open(_asset_path("icon.png")).convert("RGBA")
        return img.resize((64, 64), Image.LANCZOS)
    except Exception:
        pass
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse((2, 2, 62, 62), fill=(41, 128, 185, 255))
    d.rectangle((16, 26, 26, 38), fill=(255, 255, 255, 255))
    d.polygon([(26, 26), (38, 16), (38, 48), (26, 38)],
              fill=(255, 255, 255, 255))
    d.arc((34, 22, 48, 42), start=-60, end=60,
          fill=(255, 255, 255, 255), width=3)
    return img


def status_text(app):
    state = "Locked" if app.locked else "Unlocked"
    count = max(app.device_count, 0)
    return "Limit: %d%%  |  %s  |  %d output device%s" % (
        app.limit, state, count, "" if count == 1 else "s")


def build_menu(app):
    """Bind menu items to callbacks on the VolumeLimiter instance."""
    preset_items = [
        pystray.MenuItem("%d%%" % v, app.preset_handler(v),
                         checked=app.is_limit(v), radio=True)
        for v in PRESET_LIMITS
    ]
    preset_items.append(pystray.Menu.SEPARATOR)
    preset_items.append(pystray.MenuItem("Fine -5%", app.adjust_limit(-5)))
    preset_items.append(pystray.MenuItem("Fine -1%", app.adjust_limit(-1)))
    preset_items.append(pystray.MenuItem("Fine +1%", app.adjust_limit(1)))
    preset_items.append(pystray.MenuItem("Fine +5%", app.adjust_limit(5)))
    return pystray.Menu(
        pystray.MenuItem(lambda item: status_text(app), None, enabled=False),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Volume limit", pystray.Menu(*preset_items)),
        pystray.MenuItem("Lock volume", app.toggle_lock,
                         checked=lambda item: app.locked),
        pystray.MenuItem("Start with Windows", app.toggle_autostart,
                         checked=lambda item: app.autostart),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("About %s %s" % (APP_TITLE, VERSION), app.show_about),
        pystray.MenuItem("Quit", app.quit),
    )
