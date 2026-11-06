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

from .filters import ApplicationLogEntryFilter
from .forms import ApplicationLogEntryForm
from .models import ApplicationLogEntry
from .selectors import ApplicationLogEntrySelector
from .services import ApplicationLogEntryService
from .tables import ApplicationLogEntryTable


class ApplicationLogEntryListView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    SingleTableMixin,
    FilterView,
):
    model = ApplicationLogEntry
    permission_required = "logs.view_applicationlogentry"
    table_class = ApplicationLogEntryTable
    filterset_class = ApplicationLogEntryFilter
    template_name = "logs/log_list.html"
    paginate_by = 25
    page_title = "Entradas de Log"
    create_url_name = "logs:log_create"

    def get_queryset(self):
        return ApplicationLogEntrySelector.get_queryset()


class ApplicationLogEntryDetailView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    DetailView,
):
    model = ApplicationLogEntry
    permission_required = "logs.view_applicationlogentry"
    template_name = "logs/log_detail.html"
    page_title = "Detalle de Entrada de Log"
    list_url_name = "logs:log_list"
    update_url_name = "logs:log_update"
    delete_url_name = "logs:log_delete"


class ApplicationLogEntryCreateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    CreateView,
):
    model = ApplicationLogEntry
    permission_required = "logs.add_applicationlogentry"
    form_class = ApplicationLogEntryForm
    template_name = "logs/log_form.html"
    success_url = reverse_lazy("logs:log_list")
    page_title = "Crear Entrada de Log"
    list_url_name = "logs:log_list"

    def form_valid(self, form):
        self.object = ApplicationLogEntryService.save_record(**form.cleaned_data)
        messages.success(self.request, "Registro guardado exitosamente.")
        return redirect(self.success_url)


class ApplicationLogEntryUpdateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    UpdateView,
):
    model = ApplicationLogEntry
    permission_required = "logs.change_applicationlogentry"
    form_class = ApplicationLogEntryForm
    template_name = "logs/log_form.html"
    success_url = reverse_lazy("logs:log_list")
    page_title = "Editar Entrada de Log"
    list_url_name = "logs:log_list"

    def form_valid(self, form):
        self.object = ApplicationLogEntryService.save_record(
            instance=self.get_object(),
            **form.cleaned_data,
        )
        messages.success(self.request, "Registro actualizado exitosamente.")
        return redirect(self.success_url)


class ApplicationLogEntryDeleteView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    DeleteView,
):
    model = ApplicationLogEntry
    permission_required = "logs.delete_applicationlogentry"
    template_name = "logs/log_confirm_delete.html"
    success_url = reverse_lazy("logs:log_list")
    list_url_name = "logs:log_list"

    def form_valid(self, form):
        ApplicationLogEntryService.delete_record(instance=self.get_object())
        messages.success(self.request, "Registro eliminado.")
        return redirect(self.success_url)
