"""Generic keyboard shortcut skills."""
from __future__ import annotations

from engine.skills import SkillContext, skill

# Phrase → hotkey. Modifier ``ctrl`` is remapped to ``command`` on macOS inside the platform layer.
SHORTCUTS: dict[str, tuple[str, ...]] = {
    "copy":       ("ctrl", "c"),
    "paste":      ("ctrl", "v"),
    "cut":        ("ctrl", "x"),
    "undo":       ("ctrl", "z"),
    "redo":       ("ctrl", "y"),
    "select all": ("ctrl", "a"),
    "save as":    ("ctrl", "shift", "s"),
    "save":       ("ctrl", "s"),
    "find":       ("ctrl", "f"),
    "zoom in":    ("ctrl", "="),
    "zoom out":   ("ctrl", "-"),
    "refresh":    ("f5",),
    "full screen": ("f11",),
    "escape":     ("esc",),
    "enter":      ("enter",),
    "print":      ("ctrl", "p"),
}


@skill(
    name="keyboard.shortcut",
    triggers=tuple(SHORTCUTS.keys()),
    description="Press common keyboard shortcuts",
)
def shortcut(text: str, ctx: SkillContext) -> bool:
    keys = SHORTCUTS.get(ctx.match or "")
    if not keys:
        return False
    ctx.speak(f"{(ctx.match or '').capitalize()}.")
    return ctx.platform.press_key(*keys)
