"""Voice dictation — type a phrase into the active window."""
from __future__ import annotations

from engine.skills import SkillContext, skill

try:
    import pyautogui
except Exception:  # pragma: no cover
    pyautogui = None  # type: ignore[assignment]


@skill(name="dictation.type", triggers=("type ",), description="Type text via voice", priority=20)
def type_text(text: str, ctx: SkillContext) -> bool:
    content = text[len("type "):].strip()
    if not content:
        return False
    ctx.speak("Typing.")
    if pyautogui is None:
        return False
    try:
        pyautogui.write(content, interval=0.03)
        return True
    except Exception:
        return False
