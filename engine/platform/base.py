"""Abstract platform driver.

Each concrete subclass maps a small set of high-level actions onto the
commands, shortcuts, and APIs of a specific operating system. Keeping
this interface narrow is intentional — if a skill needs something that
isn't here, add it to the base class and implement it for every OS.
"""
from __future__ import annotations

import os
import shlex
import subprocess
import webbrowser
from abc import ABC, abstractmethod


class PlatformDriver(ABC):
    """Thin adapter around OS-specific shell invocations."""

    name: str = "base"

    # ── App control ─────────────────────────────────────────────────────────
    @abstractmethod
    def open_app(self, app: str) -> bool:
        """Launch ``app`` (either a known alias or a raw executable)."""

    @abstractmethod
    def close_app(self, app: str) -> bool:
        """Kill the process backing ``app``."""

    # ── System power ────────────────────────────────────────────────────────
    @abstractmethod
    def shutdown(self) -> bool: ...

    @abstractmethod
    def restart(self) -> bool: ...

    @abstractmethod
    def sleep(self) -> bool: ...

    @abstractmethod
    def lock(self) -> bool: ...

    @abstractmethod
    def empty_trash(self) -> bool: ...

    @abstractmethod
    def battery_level(self) -> int | None:
        """Return remaining battery percentage (0-100) or ``None`` on AC/desktop."""

    # ── File browsing ───────────────────────────────────────────────────────
    @abstractmethod
    def open_folder(self, kind: str) -> bool:
        """Open one of: downloads, documents, desktop, pictures, music, videos."""

    # ── Media keys / window management ──────────────────────────────────────
    @abstractmethod
    def press_key(self, *keys: str) -> bool:
        """Press a single key or hotkey combination."""

    @abstractmethod
    def media_key(self, action: str) -> bool:
        """action ∈ {'playpause', 'next', 'prev', 'volumeup', 'volumedown', 'mute'}."""

    # ── Shared helpers ──────────────────────────────────────────────────────
    def open_url(self, url: str) -> bool:
        """Open a URL in the default browser — identical on every OS."""
        return webbrowser.open(url)

    @staticmethod
    def _run(cmd: list[str] | str, *, shell: bool = False) -> bool:
        """Run ``cmd`` non-blocking. Returns True if it was dispatched cleanly."""
        try:
            if isinstance(cmd, str) and not shell:
                cmd = shlex.split(cmd)
            subprocess.Popen(
                cmd,
                shell=shell,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                env=os.environ.copy(),
            )
            return True
        except (OSError, ValueError):
            return False

    @staticmethod
    def _run_sync(cmd: list[str] | str, *, shell: bool = False, timeout: float = 5) -> tuple[int, str]:
        """Run ``cmd`` synchronously and return (returncode, stdout)."""
        try:
            result = subprocess.run(
                cmd if not isinstance(cmd, str) or shell else shlex.split(cmd),
                shell=shell,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
            return result.returncode, (result.stdout or "")
        except (OSError, subprocess.TimeoutExpired):
            return -1, ""
