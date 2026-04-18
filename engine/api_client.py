"""
Lightweight HTTP client used by the voice engine to push command history
into the Django API. Falls back silently if Django is not running.
"""
import json
import urllib.request
import urllib.error

API_BASE = "http://localhost:8000/api"


def push_command(command: str, success: bool) -> bool:
    """POST a command record to the Django API. Returns True on success."""
    payload = json.dumps({"command": command, "success": success}).encode()
    req = urllib.request.Request(
        f"{API_BASE}/history/log/",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=1):
            return True
    except (urllib.error.URLError, urllib.error.HTTPError):
        return False  # Django offline – silently ignore


def get_custom_commands() -> dict:
    """Fetch custom trigger→action pairs from the Django API."""
    try:
        with urllib.request.urlopen(f"{API_BASE}/commands/", timeout=1) as r:
            data = json.loads(r.read())
            return {item["trigger"]: item["action"] for item in data}
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError):
        return {}
