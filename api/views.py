"""REST API for the TARS dashboard and engine."""
from __future__ import annotations

from django.conf import settings as django_settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from . import engine_manager
from .auth import APITokenAuthentication, TarsPermission
from .events import publish
from .models import APIToken, CommandHistory, CustomCommand, EngineSettings
from .serializers import (
    APITokenSerializer,
    CommandHistorySerializer,
    CustomCommandSerializer,
    EngineSettingsSerializer,
)


class TarsAPIView(APIView):
    """Base class that applies TARS auth to every endpoint at once."""
    authentication_classes = [APITokenAuthentication]
    permission_classes = [TarsPermission]


# ── Engine control ─────────────────────────────────────────────────────────────

class EngineStatusView(TarsAPIView):
    """GET  → current status + settings
       POST → start or stop the engine  (body: {"action": "start"|"stop"})"""

    def get(self, request):
        settings = EngineSettings.get()
        settings.engine_running = engine_manager.is_running()
        settings.save()
        return Response({
            "engine_running": settings.engine_running,
            "wake_word":      settings.wake_word,
            "tts_rate":       settings.tts_rate,
            "tts_volume":     settings.tts_volume,
            "brain_provider": settings.brain_provider,
            "stt_provider":   settings.stt_provider,
            "tts_provider":   settings.tts_provider,
        })

    def post(self, request):
        action = (request.data.get("action") or "").lower()
        settings_row = EngineSettings.get()

        if action == "start":
            started = engine_manager.start_engine()
            settings_row.engine_running = True
            settings_row.save()
            publish("engine.state", {"running": True})
            return Response({
                "message": "Engine started." if started else "Engine already running.",
                "engine_running": True,
            })
        if action == "stop":
            stopped = engine_manager.stop_engine()
            settings_row.engine_running = False
            settings_row.save()
            publish("engine.state", {"running": False})
            return Response({
                "message": "Engine stopped." if stopped else "Engine was not running.",
                "engine_running": False,
            })
        return Response(
            {"error": "Invalid action. Use 'start' or 'stop'."},
            status=status.HTTP_400_BAD_REQUEST,
        )


# ── Command history ────────────────────────────────────────────────────────────

class CommandHistoryView(TarsAPIView):
    """GET → last N commands | POST → log one (engine uses this) | DELETE → clear all"""

    def get(self, request):
        limit = min(int(request.query_params.get("limit", 100)), 500)
        qs = CommandHistory.objects.all()[:limit]
        return Response(CommandHistorySerializer(qs, many=True).data)

    def post(self, request):
        serializer = CommandHistorySerializer(data=request.data)
        if serializer.is_valid():
            record = serializer.save()
            publish("command.new", CommandHistorySerializer(record).data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        CommandHistory.objects.all().delete()
        publish("history.cleared", {})
        return Response({"message": "History cleared."}, status=status.HTTP_204_NO_CONTENT)


# ── Custom commands ────────────────────────────────────────────────────────────

class CustomCommandListView(TarsAPIView):
    def get(self, request):
        qs = CustomCommand.objects.all()
        return Response(CustomCommandSerializer(qs, many=True).data)

    def post(self, request):
        serializer = CustomCommandSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            publish("command.custom.new", serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomCommandDetailView(TarsAPIView):
    def _get_obj(self, pk):
        try:
            return CustomCommand.objects.get(pk=pk)
        except CustomCommand.DoesNotExist:
            return None

    def get(self, request, pk):
        obj = self._get_obj(pk)
        if not obj:
            return Response({"error": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(CustomCommandSerializer(obj).data)

    def put(self, request, pk):
        obj = self._get_obj(pk)
        if not obj:
            return Response({"error": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = CustomCommandSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            publish("command.custom.updated", serializer.data)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        obj = self._get_obj(pk)
        if not obj:
            return Response({"error": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        pk = obj.pk
        obj.delete()
        publish("command.custom.deleted", {"id": pk})
        return Response(status=status.HTTP_204_NO_CONTENT)


# ── Engine settings ────────────────────────────────────────────────────────────

class EngineSettingsView(TarsAPIView):
    def get(self, request):
        return Response(EngineSettingsSerializer(EngineSettings.get()).data)

    def patch(self, request):
        settings_row = EngineSettings.get()
        serializer = EngineSettingsSerializer(settings_row, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            publish("settings.updated", serializer.data)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ── Skills introspection ──────────────────────────────────────────────────────

class SkillListView(TarsAPIView):
    """Expose the registered engine skills to the dashboard."""

    def get(self, request):
        try:
            from engine.skills import discover
        except Exception:  # pragma: no cover - engine package missing on minimal deployments
            return Response([])
        intents = discover()
        return Response([
            {
                "name":        intent.name,
                "description": intent.description,
                "triggers":    list(intent.triggers),
                "priority":    intent.priority,
            }
            for intent in intents
        ])


# ── Speak (dashboard → engine) ─────────────────────────────────────────────────

class SpeakView(TarsAPIView):
    """POST {"text": "..."} — broadcast a "speak" event so the running
    engine (or any listener) can say it aloud. This is a fire-and-forget
    relay; it doesn't actually synthesise speech server-side.
    """

    def post(self, request):
        text = (request.data.get("text") or "").strip()
        if not text:
            return Response({"error": "Missing 'text'."}, status=status.HTTP_400_BAD_REQUEST)
        publish("engine.speak", {"text": text})
        return Response({"ok": True, "text": text})


class ExecuteCommandView(TarsAPIView):
    """POST {"text": "..."} — actively execute a command via PTT."""

    def post(self, request):
        text = (request.data.get("text") or "").strip()
        if not text:
            return Response({"error": "Missing 'text'."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            from engine.brain import Brain
            from engine.memory import Memory
            from engine import platform as platform_module
            from engine import api_client
            
            driver = platform_module.get()
            memory = Memory(max_turns=2)
            
            def dashboard_speak(out_text: str):
                publish("engine.speak", {"text": out_text})
                
            brain = Brain(platform=driver, speak=dashboard_speak, memory=memory)
            decision = brain.handle(text)
            
            success = decision.kind != "none"
            skill_name = decision.skill_name or ("answer" if decision.kind == "answer" else None)
            
            api_client.push_command(text, success, skill=skill_name)
            
            return Response({"ok": True, "success": success, "skill": skill_name})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ── Tokens ────────────────────────────────────────────────────────────────────

class APITokenView(TarsAPIView):
    """GET → list tokens | POST → create a new one."""
    # Token management is only ever meaningful when auth is on; still require it.

    def get(self, request):
        return Response(APITokenSerializer(APIToken.objects.all(), many=True).data)

    def post(self, request):
        name = (request.data.get("name") or "").strip()
        token = APIToken.create(name=name)
        return Response(APITokenSerializer(token).data, status=status.HTTP_201_CREATED)


# ── Meta / healthcheck (unauthenticated) ───────────────────────────────────────

class HealthView(APIView):
    authentication_classes: list = []
    permission_classes: list = []

    def get(self, request):
        return Response({
            "status": "ok",
            "version": "2.0.0",
            "auth_required": getattr(django_settings, "TARS_REQUIRE_AUTH", False),
        })
