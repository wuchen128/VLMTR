# -*- coding: utf-8 -*-
"""Application core: state, watcher thread and menu callbacks."""

import threading
import time

import pystray

from . import APP_NAME, APP_TITLE, VERSION, audio, config, tray
from .autostart import apply as apply_autostart

POLL_INTERVAL = 0.2    # volume enforcement interval (seconds)
ENUM_INTERVAL = 1.0    # device enumeration interval (seconds)


class VolumeLimiter:
    def __init__(self):
        cfg = config.load_config()
        self.limit = max(0, min(100, int(cfg.get("limit", 50))))
        self.locked = cfg.get("locked", True)
        self.autostart = cfg.get("autostart", False)
        self.device_count = 0
        self._stop = threading.Event()
        self._icon = None
        self._devices = []          # [(friendly_name, IAudioEndpointVolume), ...]
        self._device_lock = threading.Lock()
        self._refresh_devices()
        if self.autostart:
            apply_autostart(True)

    # ---------- configuration ----------
    def save_config(self):
        config.save_config(self.limit, self.locked, self.autostart)

    # ---------- devices and volume ----------
    def _refresh_devices(self):
        """Enumerate active endpoints; newly plugged devices join automatically."""
        devices, ok = audio.list_output_devices()
        if not ok:
            # Keep the old list on enumeration failure to avoid losing control.
            return
        with self._device_lock:
            self._devices = devices
            count = len(devices)
        if count != self.device_count:
            self.device_count = count
            self._update_menu()

    def _enforce_all(self):
        """Push every device back to the limit."""
        with self._device_lock:
            devices = list(self._devices)
        audio.enforce(devices, self.limit)

    def _watch_loop(self):
        audio.com_init()
        last_enum = 0.0
        while not self._stop.is_set():
            now = time.time()
            if now - last_enum >= ENUM_INTERVAL:
                self._refresh_devices()
                last_enum = now
            if self.locked:
                self._enforce_all()
            time.sleep(POLL_INTERVAL)

    # ---------- menu callbacks (bound by tray.build_menu) ----------
    def set_limit(self, value):
        self.limit = max(0, min(100, int(value)))
        self.save_config()
        if self.locked:
            self._enforce_all()
        self._update_menu()

    def adjust_limit(self, delta):
        """Fine-tune the limit by delta (any integer in 0-100 is reachable)."""
        def handler(icon, item):
            self.set_limit(self.limit + delta)
        return handler

    def preset_handler(self, value):
        return lambda icon, item: self.set_limit(value)

    def is_limit(self, value):
        return lambda item: self.limit == value

    def toggle_lock(self, icon, item):
        self.locked = not self.locked
        self.save_config()
        if self.locked:
            self._refresh_devices()
            self._enforce_all()
        icon.update_menu()

    def toggle_autostart(self, icon, item):
        self.autostart = not self.autostart
        apply_autostart(self.autostart)
        self.save_config()
        icon.update_menu()

    def show_about(self, icon, item):
        icon.notify("%s %s\nLimit: %d%%\nOutput devices: %d" % (
            APP_TITLE, VERSION, self.limit, max(self.device_count, 0)),
            APP_TITLE)

    def quit(self, icon, item):
        self._stop.set()
        icon.stop()

    # ---------- tray ----------
    def _update_menu(self):
        if self._icon is None:
            return
        try:
            self._icon.update_menu()
        except Exception:
            pass

    def run(self):
        watcher = threading.Thread(target=self._watch_loop, daemon=True)
        watcher.start()
        self._icon = pystray.Icon(APP_NAME, tray.make_icon_image(),
                                  "%s %s" % (APP_TITLE, VERSION),
                                  tray.build_menu(self))
        self._icon.run()
