from django.urls import path

from . import views

urlpatterns = [
    # Meta
    path("health/",              views.HealthView.as_view(),            name="health"),
    # Engine
    path("engine/status/",       views.EngineStatusView.as_view(),      name="engine-status"),
    path("engine/speak/",        views.SpeakView.as_view(),             name="engine-speak"),
    # History
    path("history/",             views.CommandHistoryView.as_view(),    name="command-history"),
    path("history/log/",         views.CommandHistoryView.as_view(),    name="command-history-log"),  # legacy
    # Custom commands
    path("commands/",            views.CustomCommandListView.as_view(),  name="custom-commands"),
    path("commands/<int:pk>/",   views.CustomCommandDetailView.as_view(), name="custom-command-detail"),
    # Engine settings
    path("settings/",            views.EngineSettingsView.as_view(),    name="engine-settings"),
    # Skills
    path("skills/",              views.SkillListView.as_view(),         name="skill-list"),
    # Tokens
    path("tokens/",              views.APITokenView.as_view(),          name="api-tokens"),
]
