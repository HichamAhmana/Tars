"""Shared fixtures for the engine test suite."""
from __future__ import annotations

import os
import sys
import types

# Keep pyautogui from trying to connect to a real display at import time.
os.environ.setdefault("DISPLAY", ":0")
_fake_pyautogui = types.ModuleType("pyautogui")


def _noop(*args, **kwargs):
    return None


_fake_pyautogui.press = _noop
_fake_pyautogui.hotkey = _noop
_fake_pyautogui.write = _noop


class _Screen:
    def save(self, _): return None


_fake_pyautogui.screenshot = lambda *a, **k: _Screen()
sys.modules.setdefault("pyautogui", _fake_pyautogui)
