import pyttsx3
import speech_recognition as sr
import sys

# Try PyAudio first; fall back to our sounddevice shim (works on Python 3.14)
try:
    import pyaudio as _  # noqa: F401
    from speech_recognition import Microphone
    _USE_SDMIC = False
except (ImportError, OSError):
    from mic import SoundDeviceMicrophone as Microphone  # type: ignore
    _USE_SDMIC = True


class AudioEngine:
    def __init__(self):
        # TTS engine
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 190)
        self.engine.setProperty('volume', 1.0)

        # Pick a deeper / more robotic voice if present
        voices = self.engine.getProperty('voices')
        for voice in voices:
            if 'david' in voice.name.lower() or 'male' in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break

        # STT recognizer
        self.recognizer = sr.Recognizer()
        self.recognizer.pause_threshold = 0.8
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True

        if _USE_SDMIC:
            print("[TARS] Using sounddevice microphone backend (PyAudio not available).")

    def speak(self, text: str):
        print(f"\n[TARS] >>> {text}")
        self.engine.say(text)
        self.engine.runAndWait()

    def listen(self, timeout: float | None = 5, phrase_time_limit: float = 6) -> str:
        """Listen from microphone and return lower-case transcript."""
        if _USE_SDMIC:
            return self._listen_sounddevice(phrase_time_limit)
        return self._listen_pyaudio(timeout, phrase_time_limit)

    def _listen_pyaudio(self, timeout, phrase_time_limit) -> str:
        with Microphone() as source:
            print("[TARS] Listening...", end="\r")
            try:
                audio = self.recognizer.listen(source, timeout=timeout,
                                               phrase_time_limit=phrase_time_limit)
                print("[TARS] Recognizing...", end="\r")
                text = self.recognizer.recognize_google(audio)
                print(f"[You]  {text}                      ")
                return text.lower().strip()
            except sr.WaitTimeoutError:
                return ""
            except sr.UnknownValueError:
                return ""
            except sr.RequestError as e:
                print(f"[TARS] STT service error: {e}")
                return ""

    def _listen_sounddevice(self, duration: float) -> str:
        with Microphone() as mic:
            print("[TARS] Listening ...", end="\r")
            audio = mic.record(duration)
        try:
            text = self.recognizer.recognize_google(audio)
            print(f"[You]  {text}                      ")
            return text.lower().strip()
        except sr.UnknownValueError:
            return ""
        except sr.RequestError as e:
            print(f"[TARS] STT service error: {e}")
            return ""

