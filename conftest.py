"""Top-level pytest configuration for TARS."""
import os
import sys
import types

# Stub pyautogui before any engine module imports it — CI runs headless.
if "pyautogui" not in sys.modules:
    fake = types.ModuleType("pyautogui")
    fake.press = lambda *a, **k: None
    fake.hotkey = lambda *a, **k: None
    fake.write = lambda *a, **k: None

    class _Img:
        def save(self, *_a, **_kw): return None

    fake.screenshot = lambda *a, **k: _Img()
    sys.modules["pyautogui"] = fake

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
