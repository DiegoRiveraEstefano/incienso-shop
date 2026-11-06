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

from .filters import InstanceHealthCheckFilter
from .forms import InstanceHealthCheckForm
from .models import InstanceHealthCheck
from .selectors import InstanceHealthCheckSelector
from .services import InstanceHealthCheckService
from .tables import InstanceHealthCheckTable


class InstanceHealthCheckListView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    SingleTableMixin,
    FilterView,
):
    model = InstanceHealthCheck
    permission_required = "monitor.view_instancehealthcheck"
    table_class = InstanceHealthCheckTable
    filterset_class = InstanceHealthCheckFilter
    template_name = "monitor/health_list.html"
    paginate_by = 25
    page_title = "Chequeos de Salud de Instancia"
    create_url_name = "monitor:health_create"

    def get_queryset(self):
        return InstanceHealthCheckSelector.get_queryset()


class InstanceHealthCheckDetailView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    DetailView,
):
    model = InstanceHealthCheck
    permission_required = "monitor.view_instancehealthcheck"
    template_name = "monitor/health_detail.html"
    page_title = "Detalle de Chequeo de Salud de Instancia"
    list_url_name = "monitor:health_list"
    update_url_name = "monitor:health_update"
    delete_url_name = "monitor:health_delete"


class InstanceHealthCheckCreateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    CreateView,
):
    model = InstanceHealthCheck
    permission_required = "monitor.add_instancehealthcheck"
    form_class = InstanceHealthCheckForm
    template_name = "monitor/health_form.html"
    success_url = reverse_lazy("monitor:health_list")
    page_title = "Crear Chequeo de Salud de Instancia"
    list_url_name = "monitor:health_list"

    def form_valid(self, form):
        self.object = InstanceHealthCheckService.save_record(**form.cleaned_data)
        messages.success(self.request, "Registro guardado exitosamente.")
        return redirect(self.success_url)


class InstanceHealthCheckUpdateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    UpdateView,
):
    model = InstanceHealthCheck
    permission_required = "monitor.change_instancehealthcheck"
    form_class = InstanceHealthCheckForm
    template_name = "monitor/health_form.html"
    success_url = reverse_lazy("monitor:health_list")
    page_title = "Editar Chequeo de Salud de Instancia"
    list_url_name = "monitor:health_list"

    def form_valid(self, form):
        self.object = InstanceHealthCheckService.save_record(
            instance=self.get_object(),
            **form.cleaned_data,
        )
        messages.success(self.request, "Registro actualizado exitosamente.")
        return redirect(self.success_url)


class InstanceHealthCheckDeleteView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    DeleteView,
):
    model = InstanceHealthCheck
    permission_required = "monitor.delete_instancehealthcheck"
    template_name = "monitor/health_confirm_delete.html"
    success_url = reverse_lazy("monitor:health_list")
    list_url_name = "monitor:health_list"

    def form_valid(self, form):
        InstanceHealthCheckService.delete_record(instance=self.get_object())
        messages.success(self.request, "Registro eliminado.")
        return redirect(self.success_url)
