"""Windows implementation of the platform driver."""
from __future__ import annotations

import os

from .base import PlatformDriver

try:  # optional — only needed on the physical machine
    import pyautogui
except Exception:  # pragma: no cover - import may fail on headless CI
    pyautogui = None  # type: ignore[assignment]


_FOLDERS = {
    "downloads": r"%USERPROFILE%\Downloads",
    "documents": r"%USERPROFILE%\Documents",
    "desktop":   r"%USERPROFILE%\Desktop",
    "pictures":  r"%USERPROFILE%\Pictures",
    "music":     r"%USERPROFILE%\Music",
    "videos":    r"%USERPROFILE%\Videos",
}

_MEDIA_KEYS = {
    "playpause":  "playpause",
    "next":       "nexttrack",
    "prev":       "prevtrack",
    "volumeup":   "volumeup",
    "volumedown": "volumedown",
    "mute":       "volumemute",
}


class WindowsDriver(PlatformDriver):
    name = "windows"

    # ── App control ─────────────────────────────────────────────────────────
    def open_app(self, app: str) -> bool:
        return self._run(f'start "" "{app}"', shell=True)

    def close_app(self, app: str) -> bool:
        exe = os.path.basename(app).replace(".exe", "")
        return self._run(f'taskkill /F /IM {exe}.exe /T', shell=True)

    # ── Power ───────────────────────────────────────────────────────────────
    def shutdown(self) -> bool: return self._run("shutdown /s /t 5", shell=True)
    def restart(self)  -> bool: return self._run("shutdown /r /t 5", shell=True)
    def sleep(self)    -> bool: return self._run("rundll32.exe powrprof.dll,SetSuspendState 0,1,0", shell=True)
    def lock(self)     -> bool: return self._run("rundll32.exe user32.dll,LockWorkStation", shell=True)

    def empty_trash(self) -> bool:
        return self._run(
            ["powershell", "-Command", "Clear-RecycleBin -Confirm:$false"],
        )

    def battery_level(self) -> int | None:
        rc, out = self._run_sync(
            ["powershell", "-Command",
             "(Get-WmiObject -Class Win32_Battery).EstimatedChargeRemaining"],
        )
        if rc != 0:
            return None
        try:
            return int(out.strip())
        except ValueError:
            return None

    # ── Folders ─────────────────────────────────────────────────────────────
    def open_folder(self, kind: str) -> bool:
        path = _FOLDERS.get(kind.lower())
        if not path:
            return False
        return self._run(f'start "" "{path}"', shell=True)

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
        key = _MEDIA_KEYS.get(action)
        return self.press_key(key) if key else False
