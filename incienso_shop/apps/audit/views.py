from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import UpdateView
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from incienso_shop.apps.core.mixins import CrudContextMixin

from .filters import AuditEventFilter
from .forms import AuditEventForm
from .models import AuditEvent
from .selectors import AuditEventSelector
from .services import AuditEventService
from .tables import AuditEventTable


class AuditEventListView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    SingleTableMixin,
    FilterView,
):
    model = AuditEvent
    permission_required = "audit.view_auditevent"
    table_class = AuditEventTable
    filterset_class = AuditEventFilter
    template_name = "audit/audit_list.html"
    paginate_by = 25
    page_title = "Eventos de Auditoría"
    create_url_name = "audit:audit_create"

    def get_queryset(self):
        return AuditEventSelector.get_queryset()


class AuditEventDetailView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    DetailView,
):
    model = AuditEvent
    permission_required = "audit.view_auditevent"
    template_name = "audit/audit_detail.html"
    page_title = "Detalle de Evento de Auditoría"
    list_url_name = "audit:audit_list"
    update_url_name = "audit:audit_update"
    delete_url_name = "audit:audit_delete"


class AuditEventCreateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    CreateView,
):
    model = AuditEvent
    permission_required = "audit.add_auditevent"
    form_class = AuditEventForm
    template_name = "audit/audit_form.html"
    success_url = reverse_lazy("audit:audit_list")
    page_title = "Crear Evento de Auditoría"
    list_url_name = "audit:audit_list"

    def form_valid(self, form):
        self.object = AuditEventService.save_record(**form.cleaned_data)
        messages.success(self.request, "Registro guardado exitosamente.")
        return redirect(self.success_url)


class AuditEventUpdateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    UpdateView,
):
    model = AuditEvent
    permission_required = "audit.change_auditevent"
    form_class = AuditEventForm
    template_name = "audit/audit_form.html"
    success_url = reverse_lazy("audit:audit_list")
    page_title = "Editar Evento de Auditoría"
    list_url_name = "audit:audit_list"

    def form_valid(self, form):
        self.object = AuditEventService.save_record(
            instance=self.get_object(),
            **form.cleaned_data,
        )
        messages.success(self.request, "Registro actualizado exitosamente.")
        return redirect(self.success_url)


class AuditEventDeleteView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    DeleteView,
):
    model = AuditEvent
    permission_required = "audit.delete_auditevent"
    template_name = "audit/audit_confirm_delete.html"
    success_url = reverse_lazy("audit:audit_list")
    list_url_name = "audit:audit_list"

    def form_valid(self, form):
        AuditEventService.delete_record(instance=self.get_object())
        messages.success(self.request, "Registro eliminado.")
        return redirect(self.success_url)
