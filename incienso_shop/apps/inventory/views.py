from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import ListView
from django.views.generic import TemplateView

from incienso_shop.apps.inventory.models import ProductBatch
from incienso_shop.apps.inventory.selectors import get_inventory_valuation
from incienso_shop.apps.inventory.selectors import get_low_stock_alerts
from incienso_shop.apps.suppliers.models import PurchaseOrder


class InventoryDashboardView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = "inventory/dashboard.html"
    permission_required = "inventory.view_productbatch"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["valuation"] = get_inventory_valuation()
        context["low_stock_products"] = get_low_stock_alerts()
        context["recent_batches"] = ProductBatch.objects.select_related("product", "supplier").order_by(
            "-received_date",
        )[:10]
        context["pending_purchase_orders"] = PurchaseOrder.objects.select_related("supplier").exclude(
            status="RECEIVED",
        )[:5]
        return context


class BatchListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = ProductBatch
    template_name = "inventory/batch_list.html"
    context_object_name = "batches"
    paginate_by = 25
    permission_required = "inventory.view_productbatch"

    def get_queryset(self):
        return ProductBatch.objects.select_related("product", "supplier").order_by("-received_date", "-id")
