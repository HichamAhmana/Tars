"""Text-to-speech abstraction.

Two back-ends:
  * ``pyttsx3`` — offline, installed by default, works everywhere.
  * ``edge`` — Microsoft Edge voices (``edge-tts`` package, optional).

Never crashes the engine — if TTS fails, it just prints the text.
"""
from __future__ import annotations

import asyncio
import logging

from engine import config

log = logging.getLogger(__name__)


class Speaker:
    def __init__(self) -> None:
        self.provider = config.TTS_PROVIDER
        self._pyttsx = None
        if self.provider == "pyttsx3":
            self._pyttsx = self._init_pyttsx()

    # ── Init ────────────────────────────────────────────────────────────────
    def _init_pyttsx(self):
        try:
            import pyttsx3  # type: ignore
        except Exception as e:
            log.warning("pyttsx3 unavailable (%s); TTS will print to console only.", e)
            return None
        engine = pyttsx3.init()
        engine.setProperty("rate", config.TTS_RATE)
        engine.setProperty("volume", config.TTS_VOLUME)
        try:
            for voice in engine.getProperty("voices"):
                if "david" in voice.name.lower() or "male" in voice.name.lower():
                    engine.setProperty("voice", voice.id)
                    break
        except Exception:
            pass
        return engine

    # ── Public ──────────────────────────────────────────────────────────────
    def speak(self, text: str) -> None:
        print(f"\n[TARS] >>> {text}")
        if not text:
            return
        if self.provider == "edge":
            self._speak_edge(text)
            return
        if self._pyttsx is None:
            return
        try:
            self._pyttsx.say(text)
            self._pyttsx.runAndWait()
        except Exception as e:  # noqa: BLE001
            log.warning("pyttsx3 speak failed: %s", e)

    # ── Edge-TTS backend ────────────────────────────────────────────────────
    def _speak_edge(self, text: str) -> None:
        try:
            import edge_tts  # type: ignore
            import tempfile
            from playsound import playsound  # type: ignore
        except Exception as e:
            log.warning("edge-tts unavailable (%s); falling back to silent TTS.", e)
            return

        async def _synth(path: str) -> None:
            communicate = edge_tts.Communicate(text, config.TTS_EDGE_VOICE)
            await communicate.save(path)

        try:
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
                path = tmp.name
            asyncio.run(_synth(path))
            playsound(path)
        except Exception as e:  # noqa: BLE001
            log.warning("edge-tts playback failed: %s", e)
