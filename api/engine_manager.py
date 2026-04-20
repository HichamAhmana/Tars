"""
TARS Voice Engine process manager.

The engine runs as a subprocess so it never blocks the Django thread.
Django communicates status through the EngineSettings model (engine_running flag).
"""
import subprocess
import sys
import os
import threading

_process: subprocess.Popen | None = None
_lock = threading.Lock()

ENGINE_SCRIPT = os.path.join(os.path.dirname(__file__), '..', 'engine', 'main.py')


def start_engine() -> bool:
    """Spawn the voice engine subprocess. Returns True if started."""
    global _process
    with _lock:
        if _process and _process.poll() is None:
            return False  # Already running
        _process = subprocess.Popen(
            [sys.executable, "-m", "engine.main"],
            cwd=os.path.abspath(os.path.join(os.path.dirname(__file__), '..')),
            # Allow logs to flow straight to the console; omitting PIPE prevents deadlocks
        )
        return True


def stop_engine() -> bool:
    """Terminate the voice engine subprocess. Returns True if stopped."""
    global _process
    with _lock:
        if _process and _process.poll() is None:
            _process.terminate()
            _process = None
            return True
        return False


def is_running() -> bool:
    """Check whether the engine subprocess is alive."""
    with _lock:
        return _process is not None and _process.poll() is None
