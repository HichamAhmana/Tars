"""Window-management skills."""
from __future__ import annotations

import sys

from engine.skills import SkillContext, skill


_IS_MAC = sys.platform == "darwin"
_MOD = "command" if _IS_MAC else "ctrl"
_SUPER = "command" if _IS_MAC else "win"


@skill(name="window.show_desktop", triggers=("minimize all", "show desktop"), description="Minimize every window")
def show_desktop(text: str, ctx: SkillContext) -> bool:
    ctx.speak("Showing desktop.")
    if _IS_MAC:
        return ctx.platform.press_key("fn", "f11")
    return ctx.platform.press_key(_SUPER, "d")


@skill(name="window.minimize", triggers=("minimize",), description="Minimize current window")
def minimize(text: str, ctx: SkillContext) -> bool:
    if "all" in text:
        return False  # handled by show_desktop
    ctx.speak("Minimizing window.")
    return ctx.platform.press_key(_SUPER, "down")


@skill(name="window.maximize", triggers=("maximize",), description="Maximize current window")
def maximize(text: str, ctx: SkillContext) -> bool:
    ctx.speak("Maximizing window.")
    return ctx.platform.press_key(_SUPER, "up")


@skill(name="window.switch", triggers=("switch window", "alt tab"), description="Switch between windows")
def switch_window(text: str, ctx: SkillContext) -> bool:
    ctx.speak("Switching window.")
    return ctx.platform.press_key("alt", "tab")


@skill(name="window.snap_left", triggers=("snap left",), description="Snap window left")
def snap_left(text: str, ctx: SkillContext) -> bool:
    ctx.speak("Snapping left.")
    return ctx.platform.press_key(_SUPER, "left")


@skill(name="window.snap_right", triggers=("snap right",), description="Snap window right")
def snap_right(text: str, ctx: SkillContext) -> bool:
    ctx.speak("Snapping right.")
    return ctx.platform.press_key(_SUPER, "right")


@skill(name="window.close", triggers=("close window", "close this"), description="Close active window")
def close_window(text: str, ctx: SkillContext) -> bool:
    ctx.speak("Closing window.")
    return ctx.platform.press_key("alt", "f4")


@skill(name="window.new_tab", triggers=("new tab",), description="Open a new browser/editor tab")
def new_tab(text: str, ctx: SkillContext) -> bool:
    ctx.speak("Opening new tab.")
    return ctx.platform.press_key(_MOD, "t")


@skill(name="window.close_tab", triggers=("close tab",), description="Close the active tab")
def close_tab(text: str, ctx: SkillContext) -> bool:
    ctx.speak("Closing tab.")
    return ctx.platform.press_key(_MOD, "w")
