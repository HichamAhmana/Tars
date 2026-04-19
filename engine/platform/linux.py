"""Linux implementation of the platform driver."""
from __future__ import annotations

import os
import shutil

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
    "videos":    "~/Videos",
}


def _has(binary: str) -> bool:
    return shutil.which(binary) is not None


class LinuxDriver(PlatformDriver):
    name = "linux"

    # ── App control ─────────────────────────────────────────────────────────
    def open_app(self, app: str) -> bool:
        if _has("gtk-launch"):
            # Try desktop file first (strip .desktop if the user said it).
            desktop = app.replace(".desktop", "")
            if self._run(["gtk-launch", desktop]):
                return True
        return self._run([app])

    def close_app(self, app: str) -> bool:
        if _has("pkill"):
            return self._run(["pkill", "-f", app])
        return self._run(["killall", app])

    # ── Power ───────────────────────────────────────────────────────────────
    def shutdown(self) -> bool:
        if _has("systemctl"):
            return self._run(["systemctl", "poweroff"])
        return self._run(["shutdown", "-h", "now"])

    def restart(self) -> bool:
        if _has("systemctl"):
            return self._run(["systemctl", "reboot"])
        return self._run(["shutdown", "-r", "now"])

    def sleep(self) -> bool:
        if _has("systemctl"):
            return self._run(["systemctl", "suspend"])
        return False

    def lock(self) -> bool:
        for candidate in ("loginctl", "xdg-screensaver", "gnome-screensaver-command"):
            if _has(candidate):
                if candidate == "loginctl":
                    return self._run(["loginctl", "lock-session"])
                if candidate == "xdg-screensaver":
                    return self._run(["xdg-screensaver", "lock"])
                return self._run(["gnome-screensaver-command", "--lock"])
        return False

    def empty_trash(self) -> bool:
        trash = os.path.expanduser("~/.local/share/Trash")
        if not os.path.isdir(trash):
            return False
        return self._run(["rm", "-rf", f"{trash}/files", f"{trash}/info"])

    def battery_level(self) -> int | None:
        # Read the first battery in /sys (works on most distros without deps).
        for i in range(3):
            path = f"/sys/class/power_supply/BAT{i}/capacity"
            try:
                with open(path) as fp:
                    return int(fp.read().strip())
            except OSError:
                continue
        return None

    # ── Folders ─────────────────────────────────────────────────────────────
    def open_folder(self, kind: str) -> bool:
        path = _FOLDERS.get(kind.lower())
        if not path or not _has("xdg-open"):
            return False
        return self._run(["xdg-open", os.path.expanduser(path)])

    # ── Keys ────────────────────────────────────────────────────────────────
    def press_key(self, *keys: str) -> bool:
        if pyautogui is None or not keys:
            return False
        try:
            if len(keys) == 1:
                pyautogui.press(keys[0])
            else:
                pyautogui.hotkey(*keys)
            return True
        except Exception:
            return False

    def media_key(self, action: str) -> bool:
        mapping = {
            "playpause":  "playpause",
            "next":       "nexttrack",
            "prev":       "prevtrack",
            "volumeup":   "volumeup",
            "volumedown": "volumedown",
            "mute":       "volumemute",
        }
        return self.press_key(mapping.get(action, ""))
