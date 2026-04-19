from rest_framework import serializers

from .models import APIToken, CommandHistory, CustomCommand, EngineSettings


class CommandHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CommandHistory
        fields = ["id", "command", "success", "skill", "timestamp"]
        read_only_fields = ["id", "timestamp"]


class CustomCommandSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomCommand
        fields = ["id", "trigger", "action", "description", "created_at"]
        read_only_fields = ["id", "created_at"]


class EngineSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EngineSettings
        fields = [
            "wake_word", "tts_rate", "tts_volume", "engine_running",
            "brain_provider", "stt_provider", "tts_provider", "updated_at",
        ]
        read_only_fields = ["updated_at"]


class APITokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = APIToken
        fields = ["id", "key", "name", "created_at"]
        read_only_fields = ["id", "key", "created_at"]
