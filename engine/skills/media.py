"""Media playback and volume controls."""
from __future__ import annotations

from engine.skills import SkillContext, skill


@skill(name="media.play", triggers=("play",), description="Start playback")
def play(text: str, ctx: SkillContext) -> bool:
    if "pause" in text or "playlist" in text:
        return False

    lower = text.lower()
    if len(lower) >= 5 and "play " in lower:
        # Extract everything after "play"
        query_start = lower.find("play ") + 5
        query = text[query_start:].strip()
        
        if query.lower().endswith("on youtube"):
            query = query[:-10].strip()
        
        if query:
            ctx.speak(f"Playing {query}")
            try:
                import pywhatkit
                pywhatkit.playonyt(query)
            except Exception as e:
                ctx.speak("I'm sorry, I couldn't reach YouTube.")
            return True

    ctx.speak("Resuming playback.")
    return ctx.platform.media_key("playpause")


@skill(name="media.pause", triggers=("pause", "stop music"), description="Pause playback")
def pause(text: str, ctx: SkillContext) -> bool:
    ctx.speak("Pausing.")
    return ctx.platform.media_key("playpause")


@skill(name="media.next", triggers=("next track", "next song", "skip"), description="Next track")
def next_track(text: str, ctx: SkillContext) -> bool:
    ctx.speak("Next track.")
    return ctx.platform.media_key("next")


@skill(name="media.prev", triggers=("previous track", "previous song"), description="Previous track")
def prev_track(text: str, ctx: SkillContext) -> bool:
    ctx.speak("Previous track.")
    return ctx.platform.media_key("prev")


@skill(name="media.volume_up", triggers=("volume up", "turn it up", "louder"), description="Raise volume")
def volume_up(text: str, ctx: SkillContext) -> bool:
    ctx.speak("Turning up the volume.")
    ok = True
    for _ in range(5):
        ok = ctx.platform.media_key("volumeup") and ok
    return ok


@skill(name="media.volume_down", triggers=("volume down", "turn it down", "quieter"), description="Lower volume")
def volume_down(text: str, ctx: SkillContext) -> bool:
    ctx.speak("Turning down the volume.")
    ok = True
    for _ in range(5):
        ok = ctx.platform.media_key("volumedown") and ok
    return ok


@skill(name="media.mute", triggers=("mute", "unmute"), description="Toggle mute")
def mute(text: str, ctx: SkillContext) -> bool:
    ctx.speak("Muting." if "unmute" not in text else "Unmuting.")
    return ctx.platform.media_key("mute")
