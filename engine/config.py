"""Central configuration for the TARS engine.

Every knob reads from an environment variable with a sensible default,
so nothing in this file needs to be edited to try v2 — just set the
matching env var (see ``.env.example``) and restart the engine.
"""
from __future__ import annotations

import os
from typing import Any

# ── Helpers ──────────────────────────────────────────────────────────────────

def _env(name: str, default: Any) -> str:
    return os.environ.get(name, str(default))


def _env_bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes", "on")


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


# ── Wake word / voice ────────────────────────────────────────────────────────
WAKE_WORD: str = _env("TARS_WAKE_WORD", "tars").lower()
WAKE_WORD_SENSITIVITY: float = _env_float("TARS_WAKE_SENSITIVITY", 0.5)
PORCUPINE_ACCESS_KEY: str = _env("TARS_PORCUPINE_ACCESS_KEY", "")

TTS_RATE: int = _env_int("TARS_TTS_RATE", 190)
TTS_VOLUME: float = _env_float("TARS_TTS_VOLUME", 1.0)
TTS_PROVIDER: str = _env("TARS_TTS_PROVIDER", "pyttsx3").lower()  # pyttsx3 | edge
TTS_EDGE_VOICE: str = _env("TARS_TTS_EDGE_VOICE", "en-US-GuyNeural")

STT_PROVIDER: str = _env("TARS_STT_PROVIDER", "google").lower()  # google | whisper
WHISPER_MODEL: str = _env("TARS_WHISPER_MODEL", "base.en")
WHISPER_DEVICE: str = _env("TARS_WHISPER_DEVICE", "cpu")

# ── Brain (LLM intent parser) ────────────────────────────────────────────────
# ``rules`` is the original keyword router. Anything else plugs in an LLM.
BRAIN_PROVIDER: str = _env("TARS_BRAIN_PROVIDER", "rules").lower()  # rules | openai | groq | ollama
BRAIN_MODEL: str = _env("TARS_BRAIN_MODEL", "gpt-4o-mini")
BRAIN_API_KEY: str = _env("TARS_BRAIN_API_KEY", "")
BRAIN_BASE_URL: str = _env("TARS_BRAIN_BASE_URL", "")
BRAIN_MEMORY_TURNS: int = _env_int("TARS_BRAIN_MEMORY_TURNS", 6)

# ── Backend API ──────────────────────────────────────────────────────────────
API_BASE: str = _env("TARS_API_BASE", "http://localhost:8000/api")
API_TOKEN: str = _env("TARS_API_TOKEN", "")
STREAM_TO_API: bool = _env_bool("TARS_STREAM_TO_API", True)

# ── Custom app shortcuts (spoken name → executable) ──────────────────────────
# Kept for backward compatibility; the platform layer has its own defaults too.
CUSTOM_APPS: dict[str, str] = {
    "spotify":            "spotify",
    "discord":            "discord",
    "steam":              "steam",
    "vs code":            "code",
    "visual studio code": "code",
    "task manager":       "taskmgr",
    "file explorer":      "explorer",
    "control panel":      "control",
    "settings":           "ms-settings:",
    "calculator":         "calc",
    "notepad":            "notepad",
    "paint":              "mspaint",
    "word":               "winword",
    "excel":              "excel",
    "powerpoint":         "powerpnt",
    "chrome":             "chrome",
    "firefox":            "firefox",
    "edge":               "msedge",
    "vlc":                "vlc",
}

# ── Debug / telemetry ────────────────────────────────────────────────────────
DEBUG: bool = _env_bool("TARS_DEBUG", False)
