"""Tell the current time or date."""
from __future__ import annotations

import datetime

from engine.skills import SkillContext, skill


@skill(name="time.current", triggers=("what time", "current time"), description="Report the current time")
def current_time(text: str, ctx: SkillContext) -> bool:
    now = datetime.datetime.now().strftime("%I:%M %p")
    ctx.speak(f"The current time is {now}.")
    return True


@skill(
    name="time.today",
    triggers=("what day", "today's date", "what date", "todays date"),
    description="Report today's date",
)
def today(text: str, ctx: SkillContext) -> bool:
    now = datetime.datetime.now().strftime("%A, %B %d, %Y")
    ctx.speak(f"Today is {now}.")
    return True
