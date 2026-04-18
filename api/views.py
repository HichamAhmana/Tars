from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import CommandHistory, CustomCommand, EngineSettings
from .serializers import (
    CommandHistorySerializer,
    CustomCommandSerializer,
    EngineSettingsSerializer,
)
from . import engine_manager


# ── Engine control ─────────────────────────────────────────────────────────────

class EngineStatusView(APIView):
    """GET  → current status + settings
       POST → start or stop the engine  (body: {"action": "start"|"stop"})
    """

    def get(self, request):
        settings = EngineSettings.get()
        settings.engine_running = engine_manager.is_running()
        settings.save()
        return Response({
            "engine_running": settings.engine_running,
            "wake_word":      settings.wake_word,
            "tts_rate":       settings.tts_rate,
            "tts_volume":     settings.tts_volume,
        })

    def post(self, request):
        action = request.data.get("action", "").lower()
        settings = EngineSettings.get()

        if action == "start":
            started = engine_manager.start_engine()
            settings.engine_running = True
            settings.save()
            return Response({
                "message": "Engine started." if started else "Engine already running.",
                "engine_running": True,
            })
        elif action == "stop":
            stopped = engine_manager.stop_engine()
            settings.engine_running = False
            settings.save()
            return Response({
                "message": "Engine stopped." if stopped else "Engine was not running.",
                "engine_running": False,
            })
        else:
            return Response(
                {"error": "Invalid action. Use 'start' or 'stop'."},
                status=status.HTTP_400_BAD_REQUEST,
            )


# ── Command history ────────────────────────────────────────────────────────────

class CommandHistoryView(APIView):
    """GET → last N commands (default 50) | DELETE → clear all history"""

    def get(self, request):
        limit = int(request.query_params.get("limit", 50))
        qs = CommandHistory.objects.all()[:limit]
        return Response(CommandHistorySerializer(qs, many=True).data)

    def delete(self, request):
        CommandHistory.objects.all().delete()
        return Response({"message": "History cleared."}, status=status.HTTP_204_NO_CONTENT)


# ── Custom commands ────────────────────────────────────────────────────────────

class CustomCommandListView(APIView):
    """GET → list all | POST → create new"""

    def get(self, request):
        qs = CustomCommand.objects.all()
        return Response(CustomCommandSerializer(qs, many=True).data)

    def post(self, request):
        serializer = CustomCommandSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomCommandDetailView(APIView):
    """GET | PUT | DELETE  for a single custom command"""

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
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        obj = self._get_obj(pk)
        if not obj:
            return Response({"error": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ── Engine settings ────────────────────────────────────────────────────────────

class EngineSettingsView(APIView):
    """GET → current settings | PATCH → update settings"""

    def get(self, request):
        settings = EngineSettings.get()
        return Response(EngineSettingsSerializer(settings).data)

    def patch(self, request):
        settings = EngineSettings.get()
        serializer = EngineSettingsSerializer(settings, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
