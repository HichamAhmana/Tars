"""TARS v2 engine entry point.

Wires together:
  * wake-word listener (Porcupine or STT fallback)
  * STT transcriber (Google or local Whisper)
  * TTS speaker (pyttsx3 or Edge-TTS)
  * skill registry (auto-discovered plugins)
  * brain (rule-based routing + optional LLM Q&A)
  * API client that streams every command to the Django backend
"""
from __future__ import annotations

import datetime
import json
import logging
import os
import sys

# Make ``engine.*`` imports work regardless of cwd.
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from engine import api_client, config, platform as platform_module
from engine.audio import AudioEngine
from engine.brain import Brain
from engine.memory import Memory
from engine.wake import WakeWordListener

# Force UTF-8 output on Windows terminals.
if getattr(sys.stdout, "encoding", "").lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logging.basicConfig(
    level=logging.DEBUG if config.DEBUG else logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s | %(message)s",
)

HISTORY_FILE = os.path.join(_ROOT, "command_history.json")


def log_command(text: str, success: bool, skill: str | None = None) -> None:
    """Append one command record to the local history file."""
    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "command":   text,
        "success":   success,
        "skill":     skill or "",
    }
    history: list = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                history = json.load(f)
        except (OSError, json.JSONDecodeError):
            history = []
    history.append(entry)
    history = history[-500:]
    try:
        with open(HISTORY_FILE, "w") as f:
            json.dump(history, f, indent=2)
    except OSError:
        pass


def print_banner() -> None:
    driver = platform_module.get()
    print("=" * 52)
    print("         T  A  R  S  v2  -  Voice Assistant")
    print("=" * 52)
    print(f"  Wake word : {config.WAKE_WORD.upper()}")
    print(f"  Platform  : {driver.name}")
    print(f"  STT       : {config.STT_PROVIDER}")
    print(f"  TTS       : {config.TTS_PROVIDER}")
    print(f"  Brain     : {config.BRAIN_PROVIDER}")
    print("  Say 'exit' or Ctrl+C to shut down.")
    print("=" * 52)
    print()


def main() -> None:
    print_banner()

    audio = AudioEngine()
    driver = platform_module.get()
    memory = Memory(max_turns=max(2, config.BRAIN_MEMORY_TURNS))
    brain = Brain(platform=driver, speak=audio.speak, memory=memory)

    audio.speak("Tars online. Awaiting your command.")

    wake = WakeWordListener(
        transcribe=lambda: audio.listen(timeout=None, phrase_time_limit=4),
    )

    consecutive_failures = 0

    try:
        while True:
            # ── Wait for wake word ─────────────────────────────────────────
            try:
                should_continue = wake.wait_for_wake()
            except KeyboardInterrupt:
                raise
            if not should_continue:
                audio.speak("Going offline. Goodbye, sir.")
                break

            audio.speak("Yes sir?")
            print("[TARS] Activated — listening for command...")

            # ── Capture the actual command ────────────────────────────────
            command_text = audio.listen(timeout=6, phrase_time_limit=8)

            if command_text in ("exit", "quit", f"{config.WAKE_WORD} exit"):
                audio.speak("Going offline. Goodbye, sir.")
                break
            if not command_text:
                audio.speak("I didn't catch that.")
                continue

            # ── Route to a skill or the brain ─────────────────────────────
            decision = brain.handle(command_text)
            success = decision.kind != "none"
            skill_name = decision.skill_name or ("answer" if decision.kind == "answer" else None)

            log_command(command_text, success, skill_name)
            api_client.push_command(command_text, success, skill=skill_name)

            if not success:
                consecutive_failures += 1
                if consecutive_failures >= 3:
                    audio.speak(
                        "I've been unable to recognize several commands in a row. "
                        "Try saying 'open', 'search for', 'play', or 'type' followed by what you want."
                    )
                    consecutive_failures = 0
                else:
                    audio.speak(f"Sorry, I didn't understand: {command_text}")
            else:
                consecutive_failures = 0
    finally:
        wake.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[TARS] Interrupted. Goodbye.")
        sys.exit(0)
