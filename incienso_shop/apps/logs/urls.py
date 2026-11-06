from django.urls import path

from .views import ApplicationLogEntryCreateView
from .views import ApplicationLogEntryDeleteView
from .views import ApplicationLogEntryDetailView
from .views import ApplicationLogEntryListView
from .views import ApplicationLogEntryUpdateView

app_name = "logs"

urlpatterns = [
    path("", ApplicationLogEntryListView.as_view(), name="log_list"),
    path("create/", ApplicationLogEntryCreateView.as_view(), name="log_create"),
    path("<int:pk>/", ApplicationLogEntryDetailView.as_view(), name="log_detail"),
    path("<int:pk>/edit/", ApplicationLogEntryUpdateView.as_view(), name="log_update"),
    path(
        "<int:pk>/delete/",
        ApplicationLogEntryDeleteView.as_view(),
        name="log_delete",
    ),
]
