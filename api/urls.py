from django.urls import path
from . import views

urlpatterns = [
    # Engine
    path('engine/status/',          views.EngineStatusView.as_view(),        name='engine-status'),
    # History
    path('history/',                views.CommandHistoryView.as_view(),       name='command-history'),
    # Custom commands
    path('commands/',               views.CustomCommandListView.as_view(),    name='custom-commands'),
    path('commands/<int:pk>/',      views.CustomCommandDetailView.as_view(),  name='custom-command-detail'),
    # Settings
    path('settings/',               views.EngineSettingsView.as_view(),       name='engine-settings'),
]
