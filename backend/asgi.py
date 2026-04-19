"""ASGI config for the TARS backend.

Routes HTTP through Django's normal stack and WebSockets through the
Channels router defined in :mod:`api.routing`.
"""
from __future__ import annotations

import os

import django
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

# Import after django.setup() so the apps are ready.
from api.routing import websocket_urlpatterns  # noqa: E402

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http":      django_asgi_app,
    "websocket": URLRouter(websocket_urlpatterns),
})
