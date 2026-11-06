from django.urls import path

from .views import InstanceHealthCheckCreateView
from .views import InstanceHealthCheckDeleteView
from .views import InstanceHealthCheckDetailView
from .views import InstanceHealthCheckListView
from .views import InstanceHealthCheckUpdateView

app_name = "monitor"

urlpatterns = [
    path("", InstanceHealthCheckListView.as_view(), name="health_list"),
    path("create/", InstanceHealthCheckCreateView.as_view(), name="health_create"),
    path("<int:pk>/", InstanceHealthCheckDetailView.as_view(), name="health_detail"),
    path(
        "<int:pk>/edit/",
        InstanceHealthCheckUpdateView.as_view(),
        name="health_update",
    ),
    path(
        "<int:pk>/delete/",
        InstanceHealthCheckDeleteView.as_view(),
        name="health_delete",
    ),
]
