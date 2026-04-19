"""Tests for the plugin-based skill registry and individual skills."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from engine.memory import Memory
from engine.skills import SkillContext, discover


@pytest.fixture
def ctx():
    driver = MagicMock()
    driver.open_app.return_value = True
    driver.close_app.return_value = True
    driver.open_url.return_value = True
    driver.press_key.return_value = True
    driver.media_key.return_value = True
    driver.open_folder.return_value = True
    driver.shutdown.return_value = True
    driver.restart.return_value = True
    driver.sleep.return_value = True
    driver.lock.return_value = True
    driver.empty_trash.return_value = True
    driver.battery_level.return_value = 85
    speak = MagicMock()
    return SkillContext(platform=driver, speak=speak, memory=Memory(), match=None)


def test_registry_populated():
    intents = discover()
    assert len(intents) > 10
    names = {i.name for i in intents}
    for expected in (
        "app.open", "app.close", "web.search", "web.youtube",
        "media.play", "window.minimize", "system.shutdown",
        "file.open_folder", "time.current", "screenshot.take",
    ):
        assert expected in names


def _get(name):
    discover()
    from engine.skills import REGISTRY
    return next(i for i in REGISTRY if i.name == name)


def test_open_app_speaks_and_dispatches(ctx):
    intent = _get("app.open")
    ctx.match = "open "
    ok = intent.fn("open chrome", ctx)
    assert ok is True
    ctx.platform.open_app.assert_called_once()
    ctx.speak.assert_called_once()
    assert ctx.memory.recall("last_app") == "chrome"


def test_open_app_refuses_urls(ctx):
    """Open app must NOT swallow 'open youtube' — the web skill handles that."""
    intent = _get("app.open")
    ctx.match = "open "
    assert intent.fn("open youtube", ctx) is False
    assert intent.fn("open website github.com", ctx) is False


def test_search_builds_google_url(ctx):
    intent = _get("web.search")
    ctx.match = "search for "
    intent.fn("search for einstein", ctx)
    url = ctx.platform.open_url.call_args[0][0]
    assert "google.com/search" in url
    assert "einstein" in url


def test_youtube_search_query(ctx):
    intent = _get("web.youtube")
    ctx.match = "open youtube"
    intent.fn("open youtube lofi beats", ctx)
    url = ctx.platform.open_url.call_args[0][0]
    assert "search_query=lofi" in url


def test_media_volume_up_hits_media_key_multiple_times(ctx):
    intent = _get("media.volume_up")
    ctx.match = "volume up"
    intent.fn("volume up", ctx)
    assert ctx.platform.media_key.call_count == 5


def test_battery_reports_percentage(ctx):
    intent = _get("system.battery")
    ctx.match = "check battery"
    intent.fn("check battery", ctx)
    spoken = ctx.speak.call_args[0][0]
    assert "85" in spoken


def test_current_time_speaks(ctx):
    intent = _get("time.current")
    ctx.match = "what time"
    assert intent.fn("what time is it", ctx) is True
    ctx.speak.assert_called_once()
