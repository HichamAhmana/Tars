from rest_framework import serializers
from .models import CommandHistory, CustomCommand, EngineSettings


class CommandHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model  = CommandHistory
        fields = ['id', 'command', 'success', 'timestamp']
        read_only_fields = fields


class CustomCommandSerializer(serializers.ModelSerializer):
    class Meta:
        model  = CustomCommand
        fields = ['id', 'trigger', 'action', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']


class EngineSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model  = EngineSettings
        fields = ['wake_word', 'tts_rate', 'tts_volume', 'engine_running', 'updated_at']
        read_only_fields = ['updated_at']
