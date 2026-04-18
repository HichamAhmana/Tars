from django.db import models


class CommandHistory(models.Model):
    """Stores every command spoken to TARS."""
    command   = models.TextField()
    success   = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"[{self.timestamp:%Y-%m-%d %H:%M:%S}] {self.command}"


class CustomCommand(models.Model):
    """User-defined trigger → shell action mapping."""
    trigger     = models.CharField(max_length=200, unique=True)
    action      = models.TextField(help_text="Shell command or executable path")
    description = models.CharField(max_length=300, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'"{self.trigger}" → {self.action}'


class EngineSettings(models.Model):
    """Singleton-style settings table for the voice engine."""
    wake_word        = models.CharField(max_length=50, default='tars')
    tts_rate         = models.IntegerField(default=190)
    tts_volume       = models.FloatField(default=1.0)
    engine_running   = models.BooleanField(default=False)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Engine Settings'

    def save(self, *args, **kwargs):
        # Enforce singleton: always use pk=1
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
