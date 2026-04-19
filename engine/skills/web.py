"""Browser and search skills."""
from __future__ import annotations

from engine.skills import SkillContext, skill


@skill(
    name="web.search",
    triggers=("search for ", "google ", "search "),
    description="Google search for a phrase",
    priority=10,
)
def search(text: str, ctx: SkillContext) -> bool:
    for prefix in ("search for ", "google ", "search "):
        if text.startswith(prefix):
            query = text[len(prefix):].strip()
            break
    else:
        return False
    if not query:
        return False
    ctx.speak(f"Searching for {query}.")
    return ctx.platform.open_url(f"https://www.google.com/search?q={query.replace(' ', '+')}")


@skill(
    name="web.youtube",
    triggers=("open youtube", "go to youtube"),
    description="Open YouTube (optionally to a search)",
    priority=10,
)
def youtube(text: str, ctx: SkillContext) -> bool:
    base = "https://www.youtube.com"
    query = text.replace("open youtube", "").replace("go to youtube", "").strip()
    if query:
        ctx.speak(f"Searching YouTube for {query}.")
        return ctx.platform.open_url(f"{base}/results?search_query={query.replace(' ', '+')}")
    ctx.speak("Opening YouTube.")
    return ctx.platform.open_url(base)


@skill(
    name="web.goto",
    triggers=("go to ", "open website "),
    description="Open an arbitrary website",
    priority=8,
)
def goto(text: str, ctx: SkillContext) -> bool:
    for prefix in ("go to ", "open website "):
        if text.startswith(prefix):
            site = text[len(prefix):].strip()
            break
    else:
        return False
    if not site or site == "youtube":
        return False
    if "." not in site:
        site = site + ".com"
    ctx.speak(f"Opening {site}.")
    return ctx.platform.open_url(f"https://{site}")
