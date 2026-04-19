"""Thin backward-compatible wrapper around :mod:`engine.stt` and :mod:`engine.tts`.

v1 code imported ``AudioEngine`` directly; v2 splits capture and playback
into two focused modules but keeps this class around so nothing outside
the engine breaks.
"""
from __future__ import annotations

from engine.stt import Transcriber
from engine.tts import Speaker


class AudioEngine:
    def __init__(self) -> None:
        self._speaker = Speaker()
        self._transcriber = Transcriber()

    # Speech synthesis
    def speak(self, text: str) -> None:
        self._speaker.speak(text)

    # Speech recognition
    def listen(self, timeout: float | None = 5, phrase_time_limit: float = 6) -> str:
        return self._transcriber.listen(timeout=timeout, phrase_time_limit=phrase_time_limit)
