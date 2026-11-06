from django.urls import path

from .views import AuditEventCreateView
from .views import AuditEventDeleteView
from .views import AuditEventDetailView
from .views import AuditEventListView
from .views import AuditEventUpdateView

app_name = "audit"

urlpatterns = [
    path("", AuditEventListView.as_view(), name="audit_list"),
    path("create/", AuditEventCreateView.as_view(), name="audit_create"),
    path("<int:pk>/", AuditEventDetailView.as_view(), name="audit_detail"),
    path("<int:pk>/edit/", AuditEventUpdateView.as_view(), name="audit_update"),
    path("<int:pk>/delete/", AuditEventDeleteView.as_view(), name="audit_delete"),
]
