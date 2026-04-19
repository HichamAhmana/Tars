"""Wake-word detection.

If ``TARS_PORCUPINE_ACCESS_KEY`` is set *and* the ``pvporcupine`` and
``pvrecorder`` packages are installed, TARS uses Picovoice's Porcupine
for always-on, offline wake-word detection. Otherwise it falls back to
the v1 behaviour: transcribe every buffer via STT and look for the
wake word in the text.
"""
from __future__ import annotations

import logging
from typing import Callable

from engine import config

log = logging.getLogger(__name__)


class WakeWordListener:
    """Blocking ``wait_for_wake()`` that returns when the wake word fires."""

    def __init__(self, *, transcribe: Callable[[], str]):
        self.transcribe = transcribe
        self._porcupine = None
        self._recorder = None
        if config.PORCUPINE_ACCESS_KEY:
            self._init_porcupine()

    def _init_porcupine(self) -> None:
        try:
            import pvporcupine  # type: ignore
            from pvrecorder import PvRecorder  # type: ignore
        except Exception as e:
            log.warning("Porcupine unavailable (%s); falling back to STT wake detection.", e)
            return

        keyword = config.WAKE_WORD
        try:
            self._porcupine = pvporcupine.create(
                access_key=config.PORCUPINE_ACCESS_KEY,
                keywords=[keyword if keyword in pvporcupine.KEYWORDS else "computer"],
                sensitivities=[config.WAKE_WORD_SENSITIVITY],
            )
            self._recorder = PvRecorder(device_index=-1, frame_length=self._porcupine.frame_length)
            self._recorder.start()
            log.info("Porcupine initialised (keyword=%s).", keyword)
        except Exception as e:
            log.warning("Failed to start Porcupine (%s); falling back to STT wake detection.", e)
            self._porcupine = None
            self._recorder = None

    # ── Public ──────────────────────────────────────────────────────────────
    def wait_for_wake(self) -> bool:
        if self._porcupine is not None and self._recorder is not None:
            return self._wait_porcupine()
        return self._wait_stt()

    # ── Strategies ──────────────────────────────────────────────────────────
    def _wait_porcupine(self) -> bool:
        try:
            while True:
                pcm = self._recorder.read()
                if self._porcupine.process(pcm) >= 0:
                    return True
        except KeyboardInterrupt:
            raise
        except Exception as e:  # noqa: BLE001
            log.warning("Porcupine loop crashed (%s); falling back to STT.", e)
            return self._wait_stt()

    def _wait_stt(self) -> bool:
        wake = config.WAKE_WORD
        while True:
            text = self.transcribe()
            if not text:
                continue
            if text in ("exit", "quit", f"{wake} exit", f"{wake} quit", f"shut down {wake}"):
                return False
            if wake in text:
                return True

    def close(self) -> None:
        if self._recorder is not None:
            try: self._recorder.stop()
            except Exception: pass
            try: self._recorder.delete()
            except Exception: pass
        if self._porcupine is not None:
            try: self._porcupine.delete()
            except Exception: pass
