"""macOS implementation of the platform driver."""
from __future__ import annotations

import os

from .base import PlatformDriver

try:
    import pyautogui
except Exception:  # pragma: no cover
    pyautogui = None  # type: ignore[assignment]


_FOLDERS = {
    "downloads": "~/Downloads",
    "documents": "~/Documents",
    "desktop":   "~/Desktop",
    "pictures":  "~/Pictures",
    "music":     "~/Music",
    "videos":    "~/Movies",
}


class MacOSDriver(PlatformDriver):
    name = "macos"

    # ── App control ─────────────────────────────────────────────────────────
    def open_app(self, app: str) -> bool:
        # `open -a` handles friendly names like "Spotify", "Visual Studio Code"
        return self._run(["open", "-a", app])

    def close_app(self, app: str) -> bool:
        script = f'tell application "{app}" to quit'
        return self._run(["osascript", "-e", script])

    # ── Power ───────────────────────────────────────────────────────────────
    def shutdown(self) -> bool:
        return self._run(["osascript", "-e", 'tell app "System Events" to shut down'])

    def restart(self) -> bool:
        return self._run(["osascript", "-e", 'tell app "System Events" to restart'])

    def sleep(self) -> bool:
        return self._run(["pmset", "sleepnow"])

    def lock(self) -> bool:
        return self._run("pmset displaysleepnow", shell=True)

    def empty_trash(self) -> bool:
        return self._run(["osascript", "-e", 'tell app "Finder" to empty trash'])

    def battery_level(self) -> int | None:
        rc, out = self._run_sync(["pmset", "-g", "batt"])
        if rc != 0:
            return None
        for token in out.replace("\n", " ").split():
            if token.endswith("%;"):
                try:
                    return int(token.rstrip("%;"))
                except ValueError:
                    return None
        return None

    # ── Folders ─────────────────────────────────────────────────────────────
    def open_folder(self, kind: str) -> bool:
        path = _FOLDERS.get(kind.lower())
        if not path:
            return False
        return self._run(["open", os.path.expanduser(path)])

    # ── Keys ────────────────────────────────────────────────────────────────
    def press_key(self, *keys: str) -> bool:
        if pyautogui is None or not keys:
            return False
        try:
            # On macOS `ctrl` in the keyword map should map to the `command` key.
            translated = tuple("command" if k == "ctrl" else k for k in keys)
            if len(translated) == 1:
                pyautogui.press(translated[0])
            else:
                pyautogui.hotkey(*translated)
            return True
        except Exception:
            return False

    def media_key(self, action: str) -> bool:
        # Use AppleScript key codes for the media keys that don't map well through pyautogui.
        codes = {
            "playpause":  100,
            "next":       101,
            "prev":       98,
            "volumeup":   "volume up",
            "volumedown": "volume down",
            "mute":       "mute",
        }
        mapped = codes.get(action)
        if isinstance(mapped, int):
            script = f'tell application "System Events" to key code {mapped}'
            return self._run(["osascript", "-e", script])
        if isinstance(mapped, str) and mapped.startswith("volume"):
            direction = "+10" if mapped.endswith("up") else "-10"
            script = f'set volume output volume (output volume of (get volume settings) {direction})'
            return self._run(["osascript", "-e", script])
        if mapped == "mute":
            return self._run(["osascript", "-e", "set volume output muted true"])
        return False
