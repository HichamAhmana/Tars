"""
sounddevice-based microphone listening, used as a drop-in replacement
for PyAudio (which fails to build on Python 3.14 without MSVC).
"""
import io
import queue
import threading
import numpy as np
import sounddevice as sd
import soundfile as sf
import speech_recognition as sr


SAMPLE_RATE  = 16000   # Hz - matches Google STT expectation
CHANNELS     = 1
DTYPE        = 'int16'


class SoundDeviceMicrophone:
    """Mimics the sr.Microphone context manager using sounddevice."""

    def __init__(self, sample_rate=SAMPLE_RATE):
        self.sample_rate = sample_rate
        self._q: queue.Queue = queue.Queue()
        self._frames: list   = []
        self._stream         = None

    def __enter__(self):
        self._frames = []
        self._stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=CHANNELS,
            dtype=DTYPE,
            callback=self._callback,
        )
        self._stream.start()
        return self

    def __exit__(self, *_):
        if self._stream:
            self._stream.stop()
            self._stream.close()

    def _callback(self, indata, frames, time_info, status):
        self._frames.append(indata.copy())

    def record(self, duration: float) -> sr.AudioData:
        """Record for `duration` seconds and return sr.AudioData."""
        sd.sleep(int(duration * 1000))
        if not self._frames:
            return sr.AudioData(b'', self.sample_rate, 2)
        audio_np = np.concatenate(self._frames, axis=0)
        buf = io.BytesIO()
        sf.write(buf, audio_np, self.sample_rate, format='WAV')
        buf.seek(0)
        wav_bytes = buf.read()
        # sr.AudioData wants raw PCM, skip 44-byte WAV header
        return sr.AudioData(wav_bytes[44:], self.sample_rate, 2)
