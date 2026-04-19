"""Plugin-based skill system for TARS.

Every skill is a small module that registers one or more *intents* via the
``@skill`` decorator. At startup ``discover()`` imports every module in this
package and the ``@skill`` decorator records each intent in ``REGISTRY``.

A skill function takes ``(text, ctx)`` where ``ctx`` has:
    - ``platform``:  the :class:`engine.platform.PlatformDriver` for this OS
    - ``speak(msg)``:  say something back to the user
    - ``memory``:    :class:`engine.memory.Memory` for short-term state
    - ``match``:     the keyword that triggered the intent (when routed by rule)

It must return ``True`` if it handled the utterance and ``False`` otherwise.
"""
from __future__ import annotations

import dataclasses
import importlib
import pkgutil
from collections.abc import Callable, Iterable
from typing import Any

SkillFn = Callable[[str, "SkillContext"], bool]


@dataclasses.dataclass
class SkillContext:
    platform: Any
    speak: Callable[[str], None]
    memory: Any = None
    match: str | None = None


@dataclasses.dataclass
class Intent:
    name: str
    description: str
    triggers: tuple[str, ...]
    fn: SkillFn
    priority: int = 0

    def matches(self, text: str) -> str | None:
        """Return the first trigger found in ``text`` or ``None``."""
        for t in self.triggers:
            if t in text:
                return t
        return None


REGISTRY: list[Intent] = []
_DISCOVERED = False


def skill(
    *,
    name: str,
    triggers: Iterable[str],
    description: str = "",
    priority: int = 0,
) -> Callable[[SkillFn], SkillFn]:
    """Decorator that registers a function as a TARS intent."""
    def decorator(fn: SkillFn) -> SkillFn:
        REGISTRY.append(Intent(
            name=name,
            description=description or (fn.__doc__ or "").strip().split("\n", 1)[0],
            triggers=tuple(t.lower() for t in triggers),
            fn=fn,
            priority=priority,
        ))
        return fn
    return decorator


def discover() -> list[Intent]:
    """Import every skill module so the registry is populated. Idempotent."""
    global _DISCOVERED
    if _DISCOVERED:
        return REGISTRY
    pkg_path = __path__  # type: ignore[name-defined]
    for module_info in pkgutil.iter_modules(pkg_path):
        if module_info.name.startswith("_"):
            continue
        importlib.import_module(f"{__name__}.{module_info.name}")
    REGISTRY.sort(key=lambda i: -i.priority)
    _DISCOVERED = True
    return REGISTRY


def reset_for_tests() -> None:
    """Clear the registry — used by test suites that reload skills."""
    global _DISCOVERED
    REGISTRY.clear()
    _DISCOVERED = False


__all__ = ["Intent", "SkillContext", "SkillFn", "REGISTRY", "skill", "discover", "reset_for_tests"]
