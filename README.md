# VLMTR

A minimal Windows tray app that caps your system volume. No matter which app,
hotkey or system slider is used, the volume stays at or below the limit you set.

## Features

- **All output devices** — speakers, headphones, Bluetooth and HDMI are limited
  together; devices plugged in later are picked up within a second.
- **Hard limit** — the volume is checked every 0.2 s and pushed back down.
- **Adjustable** — presets from 10% to 100%, plus ±1% / ±5% fine-tuning for any
  value between 0 and 100.
- **Tray only** — no main window, no console window.
- **Persistent** — limit, lock state and autostart setting survive restarts.

## Download

Get `VLMTR.exe` from [Releases](https://github.com/wuchen128/VLMTR/releases).
It is a single portable executable; no installation needed. If SmartScreen
warns you, choose "More info" → "Run anyway".

## Usage

Right-click the tray icon:

| Menu item | Description |
|---|---|
| Volume limit | Pick a preset; the volume is lowered immediately. |
| Fine tune | Adjust the limit by ±1% or ±5%. |
| Lock volume | Enforce the limit. Turn off to leave the volume alone. |
| Start with Windows | Adds a per-user registry Run entry. |
| Quit | Stop enforcing and exit. |

Settings are stored in `%APPDATA%\VLMTR\config.json`.

## Build from source

Requires Python 3.13 on Windows.

```bash
pip install pycaw pystray pillow comtypes pyinstaller
python main.py
```

Build the executable:

```bash
pyinstaller VLMTR.spec
```

Output: `dist/VLMTR.exe`. Build artifacts (`build/`, `dist/`, `.venv/`) are
ignored by git.

## How it works

Windows stores master volume per device, so limiting only the default device
breaks as soon as you switch to headphones. VLMTR enumerates every active
output endpoint once a second and, while the lock is on, rewinds any device
above the limit every 0.2 s.

## Limitations

- Polling leaves a window of under 200 ms in which the volume can exceed the limit.
- Master volume only; per-app volume is not controlled.
- No password protection — anyone with tray access can raise the limit.

## License

[MIT](LICENSE) — free to use, modify and distribute, as long as the copyright
notice and this license are kept in copies or substantial portions of the software.
