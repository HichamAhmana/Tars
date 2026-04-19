"""Conversational Q&A — forwarded to the LLM brain when configured.

This is a catch-all with very low priority so every other intent wins
first. If the user is clearly asking a question (``who``/``what``/``why``
/…) and an LLM provider is enabled, TARS will answer conversationally.
"""
from __future__ import annotations

from engine import config
from engine.skills import SkillContext, skill

_QA_PREFIXES = (
    "who ", "what ", "why ", "when ", "where ", "how ",
    "tell me ", "explain ", "define ", "ask ",
)


@skill(
    name="qa.answer",
    triggers=_QA_PREFIXES,
    description="Answer a free-form question via the LLM",
    priority=-100,
)
def answer(text: str, ctx: SkillContext) -> bool:
    # Skip skill routing to the brain if rule-only mode is active (no LLM).
    if config.BRAIN_PROVIDER == "rules":
        return False
    try:
        from engine.brain import llm_answer
    except Exception:
        return False
    reply = llm_answer(text, ctx.memory)
    if not reply:
        return False
    ctx.speak(reply)
    return True
