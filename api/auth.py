"""Token authentication for the TARS API.

Tokens are stored in :class:`api.models.APIToken` and supplied via the
``Authorization: Token <key>`` header. When ``settings.TARS_REQUIRE_AUTH``
is ``False`` (the default in dev), auth is skipped and every request is
allowed through — this keeps ``./start.*`` "just works" for fresh clones.
"""
from __future__ import annotations

from django.conf import settings
from rest_framework import authentication, exceptions, permissions

from .models import APIToken


class TokenUser:
    """Minimal stand-in for ``request.user`` when we authenticate via token."""

    def __init__(self, token: APIToken) -> None:
        self.token = token
        self.is_authenticated = True
        self.is_anonymous = False

    def __str__(self) -> str:
        return f"TokenUser({self.token.name or 'default'})"


class APITokenAuthentication(authentication.BaseAuthentication):
    keyword = "Token"

    def authenticate(self, request):
        header = authentication.get_authorization_header(request).decode("latin1")
        if not header:
            return None
        try:
            scheme, key = header.split(" ", 1)
        except ValueError:
            return None
        if scheme.lower() != self.keyword.lower():
            return None
        try:
            token = APIToken.objects.get(key=key.strip())
        except APIToken.DoesNotExist as exc:
            raise exceptions.AuthenticationFailed("Invalid TARS API token.") from exc
        return TokenUser(token), token


class TarsPermission(permissions.BasePermission):
    """Allow everyone in dev, require a valid token when auth is turned on."""

    def has_permission(self, request, view) -> bool:
        if not getattr(settings, "TARS_REQUIRE_AUTH", False):
            return True
        return bool(getattr(request, "user", None) and request.user.is_authenticated)
