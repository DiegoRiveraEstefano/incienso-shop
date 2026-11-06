from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from incienso_shop.apps.analytics.selectors import get_business_intelligence_kpis
from incienso_shop.apps.analytics.selectors import get_top_selling_products
from incienso_shop.apps.inventory.selectors import get_low_stock_alerts


class AnalyticsDashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard de Inteligencia de Negocio y Analíticas de E-commerce."""

    template_name = "analytics/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["kpis"] = get_business_intelligence_kpis()
        context["top_products"] = get_top_selling_products(limit=5)
        context["low_stock"] = get_low_stock_alerts()
        return context
