"""The TARS "brain".

Routes an utterance to the right skill. Two modes:

* **rules** (default): greedy keyword match against the skill registry.
  Works offline, no API keys, backward compatible with v1.

* **LLM** (``TARS_BRAIN_PROVIDER=openai|groq|ollama`` + an API key):
  the utterance is posted to a chat-completions-style endpoint that
  either picks a skill via tool-calling or replies conversationally.
  If the LLM call fails for any reason the rule-based router is used
  as a fallback — the engine must never hard-fail on a network blip.
"""
from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

from engine import config
from engine.memory import Memory
from engine.skills import REGISTRY, SkillContext, discover

log = logging.getLogger(__name__)


@dataclass
class Decision:
    """What the brain decided to do with an utterance."""
    kind: str            # "skill" | "answer" | "none"
    skill_name: str | None = None
    answer: str | None = None
    match: str | None = None


class Brain:
    def __init__(self, platform: Any, speak: Any, *, memory: Memory | None = None) -> None:
        self.platform = platform
        self.speak = speak
        self.memory = memory or Memory(max_turns=max(2, config.BRAIN_MEMORY_TURNS))
        discover()  # populate REGISTRY

    # ── Public API ──────────────────────────────────────────────────────────
    def handle(self, text: str) -> Decision:
        text = (text or "").lower().strip()
        if not text:
            return Decision(kind="none")
        self.memory.add_turn("user", text)

        # 1. Rule-based routing is always tried first — it's fast and works offline.
        intent, match = _rule_match(text)

        # 2. Optionally let the LLM override routing when it's clearly a question.
        if config.BRAIN_PROVIDER != "rules" and _looks_like_question(text) and intent is None:
            answer = llm_answer(text, self.memory)
            if answer:
                self.speak(answer)
                self.memory.add_turn("assistant", answer)
                return Decision(kind="answer", answer=answer)

        if intent is None:
            return Decision(kind="none")

        ctx = SkillContext(
            platform=self.platform,
            speak=self.speak,
            memory=self.memory,
            match=match,
        )
        if intent.fn(text, ctx):
            self.memory.add_turn("assistant", intent.name)
            return Decision(kind="skill", skill_name=intent.name, match=match)
        return Decision(kind="none")


# ── Rule-based matcher ──────────────────────────────────────────────────────
def _rule_match(text: str):
    for intent in REGISTRY:
        match = intent.matches(text)
        if match is not None:
            return intent, match
    return None, None


# ── LLM support ─────────────────────────────────────────────────────────────
def _looks_like_question(text: str) -> bool:
    triggers = ("who ", "what ", "why ", "when ", "where ", "how ",
                "tell me ", "explain ", "define ")
    return any(text.startswith(t) for t in triggers) or text.endswith("?")


def llm_answer(text: str, memory: Memory) -> str:
    """Call the configured LLM and return its reply (or empty string on error)."""
    provider = config.BRAIN_PROVIDER
    if provider == "rules":
        return ""

    messages = [
        {
            "role": "system",
            "content": (
                "You are TARS, a concise voice assistant inspired by the Interstellar character. "
                "Answers are spoken aloud, so keep them short (<= 3 sentences) and conversational."
            ),
        }
    ]
    for role, content in memory.recent_turns():
        if role in ("user", "assistant"):
            messages.append({"role": role, "content": content})

    try:
        return _call_openai_compatible(provider, messages)
    except Exception as e:  # noqa: BLE001 — any network/JSON failure falls back silently
        log.warning("LLM call failed (%s); falling back to rules only.", e)
        return ""


def _call_openai_compatible(provider: str, messages: list[dict]) -> str:
    if provider == "ollama":
        base = config.BRAIN_BASE_URL or "http://localhost:11434/v1"
        api_key = config.BRAIN_API_KEY or "ollama"
    elif provider == "groq":
        base = config.BRAIN_BASE_URL or "https://api.groq.com/openai/v1"
        api_key = config.BRAIN_API_KEY
    else:  # openai or custom
        base = config.BRAIN_BASE_URL or "https://api.openai.com/v1"
        api_key = config.BRAIN_API_KEY

    if not api_key and provider != "ollama":
        return ""

    body = json.dumps({
        "model": config.BRAIN_MODEL,
        "messages": messages,
        "temperature": 0.3,
    }).encode()
    req = urllib.request.Request(
        f"{base.rstrip('/')}/chat/completions",
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode())
    try:
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, AttributeError):
        return ""


__all__ = ["Brain", "Decision", "llm_answer"]
