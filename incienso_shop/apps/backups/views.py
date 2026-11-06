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

from .filters import DatabaseBackupFilter
from .forms import DatabaseBackupForm
from .models import DatabaseBackup
from .selectors import DatabaseBackupSelector
from .services import DatabaseBackupService
from .tables import DatabaseBackupTable


class DatabaseBackupListView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    SingleTableMixin,
    FilterView,
):
    model = DatabaseBackup
    permission_required = "backups.view_databasebackup"
    table_class = DatabaseBackupTable
    filterset_class = DatabaseBackupFilter
    template_name = "backups/backup_list.html"
    paginate_by = 25
    page_title = "Copias de Seguridad"
    create_url_name = "backups:backup_create"

    def get_queryset(self):
        return DatabaseBackupSelector.get_queryset()


class DatabaseBackupDetailView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    DetailView,
):
    model = DatabaseBackup
    permission_required = "backups.view_databasebackup"
    template_name = "backups/backup_detail.html"
    page_title = "Detalle de Copia de Seguridad"
    list_url_name = "backups:backup_list"
    update_url_name = "backups:backup_update"
    delete_url_name = "backups:backup_delete"


class DatabaseBackupCreateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    CreateView,
):
    model = DatabaseBackup
    permission_required = "backups.add_databasebackup"
    form_class = DatabaseBackupForm
    template_name = "backups/backup_form.html"
    success_url = reverse_lazy("backups:backup_list")
    page_title = "Crear Copia de Seguridad"
    list_url_name = "backups:backup_list"

    def form_valid(self, form):
        self.object = DatabaseBackupService.save_record(**form.cleaned_data)
        messages.success(self.request, "Registro guardado exitosamente.")
        return redirect(self.success_url)


class DatabaseBackupUpdateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    UpdateView,
):
    model = DatabaseBackup
    permission_required = "backups.change_databasebackup"
    form_class = DatabaseBackupForm
    template_name = "backups/backup_form.html"
    success_url = reverse_lazy("backups:backup_list")
    page_title = "Editar Copia de Seguridad"
    list_url_name = "backups:backup_list"

    def form_valid(self, form):
        self.object = DatabaseBackupService.save_record(
            instance=self.get_object(),
            **form.cleaned_data,
        )
        messages.success(self.request, "Registro actualizado exitosamente.")
        return redirect(self.success_url)


class DatabaseBackupDeleteView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    DeleteView,
):
    model = DatabaseBackup
    permission_required = "backups.delete_databasebackup"
    template_name = "backups/backup_confirm_delete.html"
    success_url = reverse_lazy("backups:backup_list")
    list_url_name = "backups:backup_list"

    def form_valid(self, form):
        DatabaseBackupService.delete_record(instance=self.get_object())
        messages.success(self.request, "Registro eliminado.")
        return redirect(self.success_url)
