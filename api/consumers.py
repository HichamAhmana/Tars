"""WebSocket consumer that fans out TARS events to the dashboard."""
from __future__ import annotations

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.conf import settings

from .events import GROUP
from .models import APIToken


class EventConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self) -> None:
        if getattr(settings, "TARS_REQUIRE_AUTH", False):
            token = self._extract_token()
            if not token:
                await self.close(code=4401)
                return
            if not await self._token_exists(token):
                await self.close(code=4403)
                return
        await self.channel_layer.group_add(GROUP, self.channel_name)
        await self.accept()
        await self.send_json({"type": "hello", "data": {"message": "TARS stream connected"}})

    async def disconnect(self, code: int) -> None:  # pragma: no cover
        await self.channel_layer.group_discard(GROUP, self.channel_name)

    # fan-out from events.publish → {"type": "tars.event", "event": {...}}
    async def tars_event(self, message) -> None:
        await self.send_json(message["event"])

    # ── Helpers ─────────────────────────────────────────────────────────────
    def _extract_token(self) -> str:
        query_string = self.scope.get("query_string", b"").decode()
        for part in query_string.split("&"):
            if part.startswith("token="):
                return part[len("token="):]
        headers = dict(self.scope.get("headers", []))
        raw = headers.get(b"authorization", b"").decode()
        if raw.startswith("Token "):
            return raw[len("Token "):].strip()
        return ""

    @staticmethod
    async def _token_exists(key: str) -> bool:
        from asgiref.sync import sync_to_async
        return await sync_to_async(APIToken.objects.filter(key=key).exists)()
