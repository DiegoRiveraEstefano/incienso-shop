from django.urls import path

from .views import StoreSettingsDetailView
from .views import StoreSettingsListView
from .views import StoreSettingsUpdateView

app_name = "core"

urlpatterns = [
    path("settings/", StoreSettingsListView.as_view(), name="settings_list"),
    path(
        "settings/<int:pk>/",
        StoreSettingsDetailView.as_view(),
        name="settings_detail",
    ),
    path(
        "settings/<int:pk>/edit/",
        StoreSettingsUpdateView.as_view(),
        name="settings_update",
    ),
]
