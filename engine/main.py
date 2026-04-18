import sys
import os
import datetime
import json

# Force UTF-8 output on Windows terminals
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Make sure engine/ is importable regardless of cwd
sys.path.insert(0, os.path.dirname(__file__))

from audio import AudioEngine
from commands import CommandParser
from config import WAKE_WORD

HISTORY_FILE = os.path.join(os.path.dirname(__file__), '..', 'command_history.json')

def log_command(text, success):
    """Append a command entry to the history file."""
    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "command": text,
        "success": success,
    }
    history = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r') as f:
                history = json.load(f)
        except json.JSONDecodeError:
            history = []
    history.append(entry)
    # Keep last 500 entries
    history = history[-500:]
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)

def print_banner():
    print("=" * 48)
    print("         T  A  R  S  -  Voice Assistant")
    print("=" * 48)
    print(f"  Wake word : {WAKE_WORD.upper()}")
    print("  Say 'exit' or Ctrl+C to shut down")
    print("=" * 48)
    print()

def main():
    print_banner()

    audio   = AudioEngine()
    parser  = CommandParser(audio)
    
    audio.speak("Tars online. Awaiting your command.")

    consecutive_failures = 0

    while True:
        # ── Wait for wake word ────────────────────────────────────────────────
        text = audio.listen(timeout=None, phrase_time_limit=4)

        if not text:
            continue

        # Graceful exit via keyboard or voice
        if text in ("exit", "quit", "tars exit", "tars quit", "shut down tars"):
            audio.speak("Going offline. Goodbye, sir.")
            break

        # ── Wake word detected? ───────────────────────────────────────────────
        if WAKE_WORD not in text:
            continue

        audio.speak("Yes sir?")
        print(f"[TARS] Activated — listening for command...")

        # ── Listen for the actual command ─────────────────────────────────────
        command_text = audio.listen(timeout=6, phrase_time_limit=8)

        if not command_text or command_text in ("exit", "quit"):
            if command_text in ("exit", "quit"):
                audio.speak("Going offline. Goodbye, sir.")
                break
            audio.speak("I didn't catch that.")
            continue

        # ── Execute command ───────────────────────────────────────────────────
        success = parser.execute(command_text)
        log_command(command_text, success)

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

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[TARS] Interrupted. Goodbye.")
        sys.exit(0)
