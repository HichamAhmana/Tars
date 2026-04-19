"""Speech-to-text abstraction.

``Transcriber.listen(...)`` captures one utterance from the microphone
and returns a lower-cased transcript. Two back-ends are supported:

* ``google`` — free Google Web Speech endpoint via ``speech_recognition``.
  Requires internet, no API key.
* ``whisper`` — local inference via ``faster-whisper``. Fully offline
  once the model is downloaded.
"""
from __future__ import annotations

import logging

import speech_recognition as sr

from engine import config

log = logging.getLogger(__name__)

try:
    import pyaudio as _  # noqa: F401
    from speech_recognition import Microphone
    _USE_SDMIC = False
except (ImportError, OSError):
    from engine.mic import SoundDeviceMicrophone as Microphone  # type: ignore
    _USE_SDMIC = True


class Transcriber:
    def __init__(self) -> None:
        self.provider = config.STT_PROVIDER
        self.recognizer = sr.Recognizer()
        self.recognizer.pause_threshold = 0.8
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self._whisper = None
        if self.provider == "whisper":
            self._whisper = self._init_whisper()

    # ── Init ────────────────────────────────────────────────────────────────
    def _init_whisper(self):
        try:
            from faster_whisper import WhisperModel  # type: ignore
        except Exception as e:
            log.warning("faster-whisper unavailable (%s); falling back to Google STT.", e)
            self.provider = "google"
            return None
        return WhisperModel(config.WHISPER_MODEL, device=config.WHISPER_DEVICE, compute_type="int8")

    # ── Public ──────────────────────────────────────────────────────────────
    def listen(self, *, timeout: float | None = 5, phrase_time_limit: float = 6) -> str:
        audio = self._record(timeout=timeout, phrase_time_limit=phrase_time_limit)
        if audio is None:
            return ""
        return self._transcribe(audio)

    # ── Capture ─────────────────────────────────────────────────────────────
    def _record(self, *, timeout, phrase_time_limit):
        try:
            if _USE_SDMIC:
                with Microphone() as mic:
                    return mic.record(phrase_time_limit)
            with Microphone() as source:
                return self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit,
                )
        except sr.WaitTimeoutError:
            return None
        except Exception as e:  # noqa: BLE001
            log.warning("mic capture failed: %s", e)
            return None

    # ── Decode ──────────────────────────────────────────────────────────────
    def _transcribe(self, audio) -> str:
        if self.provider == "whisper" and self._whisper is not None:
            return self._transcribe_whisper(audio)
        return self._transcribe_google(audio)

    def _transcribe_google(self, audio) -> str:
        try:
            text = self.recognizer.recognize_google(audio)
            return text.lower().strip()
        except sr.UnknownValueError:
            return ""
        except sr.RequestError as e:
            log.warning("Google STT error: %s", e)
            return ""

    def _transcribe_whisper(self, audio) -> str:
        try:
            import io
            import tempfile
            wav_bytes = audio.get_wav_data()
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp.write(wav_bytes)
                path = tmp.name
            segments, _ = self._whisper.transcribe(path, language="en", vad_filter=True)
            text = " ".join(seg.text for seg in segments).strip().lower()
            return text
        except Exception as e:  # noqa: BLE001
            log.warning("Whisper STT failed (%s); falling back to Google.", e)
            return self._transcribe_google(audio)
