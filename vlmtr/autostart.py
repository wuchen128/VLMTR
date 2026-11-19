# -*- coding: utf-8 -*-
"""Start with Windows: per-user HKCU Run key (no admin rights required)."""

import os
import sys
import winreg

from . import APP_NAME

REG_RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"


def exe_command():
    """Command written to the registry."""
    if getattr(sys, "frozen", False):
        return '"%s"' % sys.executable
    # Run through pythonw.exe from source to avoid a console window.
    return '"%s" "%s"' % (sys.executable.replace("python.exe", "pythonw.exe"),
                          os.path.abspath(sys.argv[0]))


def apply(enable):
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_RUN_KEY, 0,
                             winreg.KEY_SET_VALUE)
        if enable:
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, exe_command())
        else:
            try:
                winreg.DeleteValue(key, APP_NAME)
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
    except Exception:
        pass
