"""Short-term conversation memory for TARS.

Remembers the last N user turns and a small key-value store the skills
can use ("last_app", "last_query", etc). This is explicitly *not*
persistent — it lives for one engine run, which is fine for now.
"""
from __future__ import annotations

import collections
from typing import Any


class Memory:
    def __init__(self, max_turns: int = 8) -> None:
        self._turns: collections.deque[tuple[str, str]] = collections.deque(maxlen=max_turns)
        self._kv: dict[str, Any] = {}

    # ── Conversation turns ──────────────────────────────────────────────────
    def add_turn(self, role: str, content: str) -> None:
        self._turns.append((role, content))

    def recent_turns(self) -> list[tuple[str, str]]:
        return list(self._turns)

    # ── Key/value ───────────────────────────────────────────────────────────
    def remember(self, key: str, value: Any) -> None:
        self._kv[key] = value

    def recall(self, key: str, default: Any = None) -> Any:
        return self._kv.get(key, default)

    def forget(self, key: str) -> None:
        self._kv.pop(key, None)

    def snapshot(self) -> dict[str, Any]:
        return {"turns": list(self._turns), "kv": dict(self._kv)}
