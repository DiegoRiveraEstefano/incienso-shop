from django.urls import path

from .views import DatabaseBackupCreateView
from .views import DatabaseBackupDeleteView
from .views import DatabaseBackupDetailView
from .views import DatabaseBackupListView
from .views import DatabaseBackupUpdateView

app_name = "backups"

urlpatterns = [
    path("", DatabaseBackupListView.as_view(), name="backup_list"),
    path("create/", DatabaseBackupCreateView.as_view(), name="backup_create"),
    path("<int:pk>/", DatabaseBackupDetailView.as_view(), name="backup_detail"),
    path("<int:pk>/edit/", DatabaseBackupUpdateView.as_view(), name="backup_update"),
    path("<int:pk>/delete/", DatabaseBackupDeleteView.as_view(), name="backup_delete"),
]
