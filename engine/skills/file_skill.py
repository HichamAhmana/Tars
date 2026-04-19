"""Open standard user folders."""
from __future__ import annotations

from engine.skills import SkillContext, skill

_FOLDERS = {
    "open downloads": "downloads",
    "open documents": "documents",
    "open desktop":   "desktop",
    "open pictures":  "pictures",
    "open music":     "music",
    "open videos":    "videos",
}


@skill(
    name="file.open_folder",
    triggers=tuple(_FOLDERS.keys()),
    description="Open a common user folder",
    priority=15,  # beats generic app.open "open X"
)
def open_folder(text: str, ctx: SkillContext) -> bool:
    kind = _FOLDERS.get(ctx.match or "")
    if not kind:
        return False
    ctx.speak(f"Opening your {kind} folder.")
    return ctx.platform.open_folder(kind)
