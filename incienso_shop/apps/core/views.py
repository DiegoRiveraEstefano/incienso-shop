from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import DetailView
from django.views.generic import TemplateView
from django.views.generic import UpdateView
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from .filters import StoreSettingsFilter
from .forms import StoreSettingsForm
from .models import StoreSettings
from .selectors import StoreSettingsSelector
from .services import StoreSettingsService


class HomeDashboardView(TemplateView):
    """Página principal de la tienda de inciensos."""

    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["settings"] = StoreSettingsSelector.get_settings()
        return context


class AboutView(TemplateView):
    """Página Acerca De."""

    template_name = "pages/about.html"


class StoreSettingsListView(LoginRequiredMixin, SingleTableMixin, FilterView):
    model = StoreSettings
    table_class = StoreSettingsFilter
    filterset_class = StoreSettingsFilter
    template_name = "core/settings_list.html"
    context_object_name = "settings_list"

    def get_queryset(self):
        return StoreSettingsSelector.list_settings()


class StoreSettingsDetailView(LoginRequiredMixin, DetailView):
    model = StoreSettings
    template_name = "core/settings_detail.html"
    context_object_name = "store_settings"


class StoreSettingsUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = StoreSettings
    form_class = StoreSettingsForm
    template_name = "core/settings_form.html"
    permission_required = "core.change_storesettings"
    success_url = reverse_lazy("core:settings_list")

    def form_valid(self, form):
        StoreSettingsService.update_settings(self.object, **form.cleaned_data)
        messages.success(self.request, "Configuración guardada correctamente.")
        return super().form_valid(form)
