# -*- coding: utf-8 -*-
"""Windows Core Audio helpers: enumerate output devices and enforce the limit."""

from comtypes import CLSCTX_ALL
from pycaw.constants import DEVICE_STATE, EDataFlow
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


def com_init():
    """COM must be initialized per thread (idempotent, errors ignored)."""
    try:
        import comtypes
        comtypes.CoInitialize()
    except Exception:
        pass


def _device_names():
    """Map device id -> friendly name (used for status display)."""
    names = {}
    try:
        for d in AudioUtilities.GetAllDevices():
            if getattr(d, "FriendlyName", None) and getattr(d, "id", None):
                names[d.id] = d.FriendlyName
    except Exception:
        pass
    return names


def list_output_devices():
    """Enumerate all active audio render endpoints.

    Returns (devices, ok). ok is False when enumeration fails (e.g. a
    transient COM error); callers should keep the previous device list
    instead of treating it as "no devices".
    """
    com_init()
    found = []
    try:
        names = _device_names()
        enumerator = AudioUtilities.GetDeviceEnumerator()
        coll = enumerator.EnumAudioEndpoints(
            EDataFlow.eRender.value, DEVICE_STATE.ACTIVE.value)
        for i in range(coll.GetCount()):
            dev = coll.Item(i)
            try:
                ep = dev.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                vol = ep.QueryInterface(IAudioEndpointVolume)
                found.append((names.get(dev.GetId(), "Output device"), vol))
            except Exception:
                continue
        return found, True
    except Exception:
        return [], False


def enforce(devices, limit):
    """Push every device's volume back to the limit."""
    com_init()
    for _, vol in devices:
        try:
            cur = vol.GetMasterVolumeLevelScalar()
            if cur > limit / 100.0 + 1e-6:
                vol.SetMasterVolumeLevelScalar(limit / 100.0, None)
        except Exception:
            # Device may have just been unplugged; next enumeration drops it.
            continue
