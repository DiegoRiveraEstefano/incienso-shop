from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import ListView

from incienso_shop.apps.suppliers.models import PurchaseOrder
from incienso_shop.apps.suppliers.models import Supplier
from incienso_shop.apps.suppliers.selectors import get_all_purchase_orders
from incienso_shop.apps.suppliers.selectors import get_all_suppliers


class SupplierListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Supplier
    template_name = "suppliers/supplier_list.html"
    context_object_name = "suppliers"
    permission_required = "suppliers.view_supplier"

    def get_queryset(self):
        return get_all_suppliers()


class PurchaseOrderListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = PurchaseOrder
    template_name = "suppliers/purchase_order_list.html"
    context_object_name = "purchase_orders"
    permission_required = "suppliers.view_purchaseorder"

    def get_queryset(self):
        return get_all_purchase_orders()
