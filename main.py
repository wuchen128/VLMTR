# -*- coding: utf-8 -*-
"""VLMTR entry point, used for source runs and PyInstaller builds.

Usage: python main.py
"""

from vlmtr.app import VolumeLimiter


if __name__ == "__main__":
    VolumeLimiter().run()
