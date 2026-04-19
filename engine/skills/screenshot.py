"""Capture a screenshot."""
from __future__ import annotations

import datetime
import os

from engine.skills import SkillContext, skill

try:
    import pyautogui
except Exception:  # pragma: no cover
    pyautogui = None  # type: ignore[assignment]


@skill(
    name="screenshot.take",
    triggers=("screenshot", "take a screenshot"),
    description="Save a screenshot to the Desktop",
)
def take_screenshot(text: str, ctx: SkillContext) -> bool:
    if pyautogui is None:
        ctx.speak("Screenshot support isn't available on this machine.")
        return False
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    os.makedirs(desktop, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(desktop, f"tars_screenshot_{stamp}.png")
    try:
        pyautogui.screenshot().save(path)
    except Exception:
        ctx.speak("I couldn't capture the screen.")
        return False
    ctx.speak("Screenshot saved to your Desktop, sir.")
    return True
