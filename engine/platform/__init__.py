"""Platform-specific actions for TARS.

``platform.get()`` returns the concrete driver for the running OS. All
skills use this interface instead of calling ``os.system`` directly, so
commands work identically on Windows, macOS, and Linux.
"""
from __future__ import annotations

import sys

from .base import PlatformDriver


def get() -> PlatformDriver:
    """Return a driver for the current operating system."""
    if sys.platform.startswith("win"):
        from .windows import WindowsDriver
        return WindowsDriver()
    if sys.platform == "darwin":
        from .macos import MacOSDriver
        return MacOSDriver()
    from .linux import LinuxDriver
    return LinuxDriver()


__all__ = ["PlatformDriver", "get"]
