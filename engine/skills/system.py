"""Power and system-level skills."""
from __future__ import annotations

from engine.skills import SkillContext, skill


@skill(name="system.shutdown", triggers=("shut down", "shutdown"), description="Shut the computer down")
def shutdown(text: str, ctx: SkillContext) -> bool:
    ctx.speak("Shutting down. Goodbye, sir.")
    return ctx.platform.shutdown()


@skill(name="system.restart", triggers=("restart", "reboot"), description="Restart the computer")
def restart(text: str, ctx: SkillContext) -> bool:
    ctx.speak("Restarting the system.")
    return ctx.platform.restart()


@skill(name="system.sleep", triggers=("sleep", "hibernate"), description="Put the computer to sleep")
def sleep(text: str, ctx: SkillContext) -> bool:
    ctx.speak("Going to sleep.")
    return ctx.platform.sleep()


@skill(name="system.lock", triggers=("lock",), description="Lock the workstation")
def lock(text: str, ctx: SkillContext) -> bool:
    ctx.speak("Locking your PC, sir.")
    return ctx.platform.lock()


@skill(name="system.empty_trash", triggers=("empty recycle bin", "empty trash"), description="Empty the trash")
def empty_trash(text: str, ctx: SkillContext) -> bool:
    ctx.speak("Emptying the recycle bin.")
    return ctx.platform.empty_trash()


@skill(name="system.battery", triggers=("check battery", "battery level"), description="Report battery percentage")
def battery(text: str, ctx: SkillContext) -> bool:
    level = ctx.platform.battery_level()
    if level is None:
        ctx.speak("I couldn't determine the battery level. You may be on AC power.")
    else:
        ctx.speak(f"Battery is at {level} percent.")
    return True
