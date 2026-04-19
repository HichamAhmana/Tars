"""Helper for publishing events over Django Channels.

All live-updates from the API flow through :func:`publish` so the
dashboard sees a single stream with a predictable envelope::

    {"type": "command.new", "data": {...}}

Channels is optional — if it isn't installed or no layer is configured
the call is a silent no-op and REST still works.
"""
from __future__ import annotations

from typing import Any

try:
    from asgiref.sync import async_to_sync
    from channels.layers import get_channel_layer
except Exception:  # pragma: no cover - channels not installed
    async_to_sync = None  # type: ignore[assignment]
    get_channel_layer = None  # type: ignore[assignment]

GROUP = "tars_events"


def publish(kind: str, data: dict[str, Any]) -> None:
    if get_channel_layer is None or async_to_sync is None:
        return
    layer = get_channel_layer()
    if layer is None:
        return
    try:
        async_to_sync(layer.group_send)(GROUP, {
            "type": "tars.event",
            "event": {"type": kind, "data": data},
        })
    except Exception:
        # Never let an event failure break a REST request.
        pass
