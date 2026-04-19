"""Tests for the TARS Brain router."""
from __future__ import annotations

from unittest.mock import MagicMock

from engine.brain import Brain


def _make_brain():
    driver = MagicMock()
    driver.open_app.return_value = True
    driver.open_url.return_value = True
    driver.press_key.return_value = True
    driver.media_key.return_value = True
    driver.open_folder.return_value = True
    speak = MagicMock()
    return Brain(platform=driver, speak=speak), driver, speak


def test_brain_routes_open_app():
    brain, driver, _ = _make_brain()
    decision = brain.handle("open chrome")
    assert decision.kind == "skill"
    assert decision.skill_name == "app.open"
    driver.open_app.assert_called_once()


def test_brain_routes_folder_over_open_app():
    """'open downloads' should hit file.open_folder, not app.open."""
    brain, driver, _ = _make_brain()
    decision = brain.handle("open downloads")
    assert decision.skill_name == "file.open_folder"
    driver.open_folder.assert_called_once()


def test_brain_unrecognised_returns_none():
    brain, _, _ = _make_brain()
    decision = brain.handle("asdfkjhalksjdfh")
    assert decision.kind == "none"


def test_brain_records_memory_turn():
    brain, _, _ = _make_brain()
    brain.handle("what time is it")
    turns = brain.memory.recent_turns()
    assert turns[0] == ("user", "what time is it")
    assert turns[1][0] == "assistant"


def test_brain_llm_fallback_failure_does_not_crash(monkeypatch):
    """If an LLM answer is needed and the provider throws, we just return 'none'."""
    from engine import config
    monkeypatch.setattr(config, "BRAIN_PROVIDER", "openai")
    monkeypatch.setattr(config, "BRAIN_API_KEY", "fake")

    def boom(*_a, **_kw):
        raise RuntimeError("network down")

    monkeypatch.setattr("engine.brain._call_openai_compatible", boom)

    brain, _, _ = _make_brain()
    decision = brain.handle("who painted the mona lisa")
    assert decision.kind in ("none", "skill")  # no crash, any routing is fine
