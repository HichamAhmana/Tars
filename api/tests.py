"""Backend integration tests for the TARS REST + auth layers."""
from __future__ import annotations

from django.test import Client, TestCase, override_settings

from .models import APIToken, CommandHistory, CustomCommand, EngineSettings


class HealthTests(TestCase):
    def test_health_is_open(self):
        resp = self.client.get("/api/health/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["status"], "ok")


class CommandHistoryTests(TestCase):
    def test_post_and_get_roundtrip(self):
        resp = self.client.post(
            "/api/history/",
            data={"command": "open chrome", "success": True, "skill": "app.open"},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 201, resp.content)

        resp = self.client.get("/api/history/")
        self.assertEqual(resp.status_code, 200)
        items = resp.json()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["command"], "open chrome")
        self.assertEqual(items[0]["skill"], "app.open")

    def test_delete_clears_history(self):
        CommandHistory.objects.create(command="x", success=True)
        resp = self.client.delete("/api/history/")
        self.assertEqual(resp.status_code, 204)
        self.assertEqual(CommandHistory.objects.count(), 0)


class CustomCommandTests(TestCase):
    def test_crud(self):
        resp = self.client.post(
            "/api/commands/",
            data={"trigger": "hello", "action": "echo hi", "description": "test"},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 201)
        cid = resp.json()["id"]

        resp = self.client.get(f"/api/commands/{cid}/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["trigger"], "hello")

        resp = self.client.put(
            f"/api/commands/{cid}/",
            data={"description": "updated"},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["description"], "updated")

        resp = self.client.delete(f"/api/commands/{cid}/")
        self.assertEqual(resp.status_code, 204)


class EngineSettingsTests(TestCase):
    def test_default_values(self):
        resp = self.client.get("/api/settings/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["wake_word"], "tars")
        self.assertEqual(data["brain_provider"], "rules")

    def test_patch_updates(self):
        resp = self.client.patch(
            "/api/settings/",
            data={"wake_word": "jarvis", "brain_provider": "openai"},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        settings = EngineSettings.get()
        self.assertEqual(settings.wake_word, "jarvis")
        self.assertEqual(settings.brain_provider, "openai")


class SpeakTests(TestCase):
    def test_speak_requires_text(self):
        resp = self.client.post("/api/engine/speak/", data={}, content_type="application/json")
        self.assertEqual(resp.status_code, 400)

    def test_speak_accepts_text(self):
        resp = self.client.post(
            "/api/engine/speak/",
            data={"text": "hello sir"},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["text"], "hello sir")


class SkillsEndpointTests(TestCase):
    def test_skills_lists_at_least_one(self):
        resp = self.client.get("/api/skills/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(len(data) >= 5)
        names = {s["name"] for s in data}
        self.assertIn("app.open", names)


@override_settings(TARS_REQUIRE_AUTH=True)
class TokenAuthTests(TestCase):
    def setUp(self):
        self.token = APIToken.create(name="test")
        self.client = Client()

    def test_unauthenticated_is_rejected(self):
        resp = self.client.get("/api/history/")
        self.assertIn(resp.status_code, (401, 403))

    def test_token_lets_you_in(self):
        resp = self.client.get(
            "/api/history/",
            HTTP_AUTHORIZATION=f"Token {self.token.key}",
        )
        self.assertEqual(resp.status_code, 200)

    def test_wrong_token_is_rejected(self):
        resp = self.client.get(
            "/api/history/",
            HTTP_AUTHORIZATION="Token definitelynotreal",
        )
        self.assertIn(resp.status_code, (401, 403))
