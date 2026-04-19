"""Tests for the platform abstraction layer."""
from __future__ import annotations

import sys
from unittest.mock import patch

from engine import platform as platform_module
from engine.platform.linux import LinuxDriver
from engine.platform.macos import MacOSDriver
from engine.platform.windows import WindowsDriver


def test_get_returns_driver_for_current_os():
    driver = platform_module.get()
    assert driver.name in ("windows", "macos", "linux")


def test_each_driver_exposes_full_interface():
    required = [
        "open_app", "close_app", "shutdown", "restart", "sleep", "lock",
        "empty_trash", "battery_level", "open_folder", "press_key",
        "media_key", "open_url",
    ]
    for cls in (WindowsDriver, MacOSDriver, LinuxDriver):
        for method in required:
            assert callable(getattr(cls, method)), f"{cls.__name__} missing {method}"


def test_linux_driver_dispatches_commands():
    driver = LinuxDriver()
    with patch.object(LinuxDriver, "_run", return_value=True) as m:
        assert driver.open_app("firefox") is True
        # Call may have used gtk-launch or the raw binary — either is fine.
        assert m.called


def test_open_url_goes_through_webbrowser():
    driver = LinuxDriver()
    with patch("engine.platform.base.webbrowser.open", return_value=True) as m:
        assert driver.open_url("https://example.com") is True
        m.assert_called_once_with("https://example.com")


def test_macos_press_key_translates_ctrl_to_command():
    driver = MacOSDriver()
    with patch("engine.platform.macos.pyautogui") as fake:
        fake.hotkey.return_value = None
        driver.press_key("ctrl", "c")
        assert fake.hotkey.call_args[0] == ("command", "c")
