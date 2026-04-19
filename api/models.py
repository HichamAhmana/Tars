"""Database models for the TARS backend."""
from __future__ import annotations

import secrets

from django.db import models


class CommandHistory(models.Model):
    """Every utterance spoken to TARS and whether it was executed."""

    command   = models.TextField()
    success   = models.BooleanField(default=False)
    skill     = models.CharField(max_length=100, blank=True, default="")
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self) -> str:
        return f"[{self.timestamp:%Y-%m-%d %H:%M:%S}] {self.command}"


class CustomCommand(models.Model):
    """User-defined trigger → shell action mapping."""

    trigger     = models.CharField(max_length=200, unique=True)
    action      = models.TextField(help_text="Shell command or executable path")
    description = models.CharField(max_length=300, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f'"{self.trigger}" → {self.action}'


class EngineSettings(models.Model):
    """Singleton-style settings row for the voice engine."""

    wake_word       = models.CharField(max_length=50, default="tars")
    tts_rate        = models.IntegerField(default=190)
    tts_volume      = models.FloatField(default=1.0)
    engine_running  = models.BooleanField(default=False)
    # New in v2 — user-configurable providers.
    brain_provider  = models.CharField(max_length=20, default="rules")
    stt_provider    = models.CharField(max_length=20, default="google")
    tts_provider    = models.CharField(max_length=20, default="pyttsx3")
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Engine Settings"

    def save(self, *args, **kwargs):
        self.pk = 1  # enforce singleton
        super().save(*args, **kwargs)

    @classmethod
    def get(cls) -> "EngineSettings":
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class APIToken(models.Model):
    """Shared-secret token — lets the engine + dashboard authenticate to the API."""

    key         = models.CharField(max_length=64, unique=True)
    name        = models.CharField(max_length=100, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    @classmethod
    def create(cls, name: str = "") -> "APIToken":
        return cls.objects.create(key=secrets.token_hex(24), name=name or "default")

    @classmethod
    def default(cls) -> "APIToken":
        """Return the first token, creating one on demand."""
        tok = cls.objects.first()
        if tok is None:
            tok = cls.create(name="default")
        return tok

    def __str__(self) -> str:
        return self.name or self.key[:8]
