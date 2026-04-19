"""Launch or kill applications by spoken name."""
from __future__ import annotations

from engine import config
from engine.skills import SkillContext, skill


def _resolve(app: str) -> str:
    return config.CUSTOM_APPS.get(app.strip().lower(), app.strip())


@skill(
    name="app.open",
    triggers=("open ", "launch ", "start "),
    description="Open an application by name",
    priority=5,  # must beat 'open youtube' etc → the web skill has higher priority
)
def open_app(text: str, ctx: SkillContext) -> bool:
    trigger = ctx.match or ""
    app = text[len(trigger):].strip()
    # Guard: never try to handle 'open youtube'/'open website' — those belong to web skill.
    if not app or app.startswith(("youtube", "website")) or app.endswith((".com", ".org", ".net")):
        return False
    exe = _resolve(app)
    ctx.speak(f"Opening {app}.")
    ctx.memory.remember("last_app", app)
    return ctx.platform.open_app(exe)


@skill(
    name="app.close",
    triggers=("close ", "kill ", "quit "),
    description="Close an application by name",
    priority=5,
)
def close_app(text: str, ctx: SkillContext) -> bool:
    trigger = ctx.match or ""
    target = text[len(trigger):].strip()
    if not target or target in ("window", "this", "tab"):
        return False
    exe = _resolve(target)
    ctx.speak(f"Closing {target}.")
    return ctx.platform.close_app(exe)
