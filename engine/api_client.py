"""HTTP client the engine uses to push events to the Django backend.

Every call is best-effort and non-fatal. If the backend is down the
engine just logs the command locally and keeps running.
"""
from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request

from engine import config

log = logging.getLogger(__name__)


def _headers() -> dict[str, str]:
    headers = {"Content-Type": "application/json"}
    if config.API_TOKEN:
        headers["Authorization"] = f"Token {config.API_TOKEN}"
    return headers


def push_command(command: str, success: bool, *, skill: str | None = None) -> bool:
    """POST a command record. Returns True on success."""
    if not config.STREAM_TO_API:
        return False
    payload = json.dumps({
        "command": command,
        "success": success,
        "skill":   skill or "",
    }).encode()
    req = urllib.request.Request(
        f"{config.API_BASE}/history/",
        data=payload,
        headers=_headers(),
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=1):
            return True
    except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
        log.debug("history push failed: %s", e)
        return False


def get_custom_commands() -> dict[str, str]:
    """Fetch user-defined trigger→action pairs from the backend."""
    req = urllib.request.Request(f"{config.API_BASE}/commands/", headers=_headers())
    try:
        with urllib.request.urlopen(req, timeout=1) as r:
            data = json.loads(r.read().decode())
            return {item["trigger"]: item["action"] for item in data}
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, OSError):
        return {}
