from django.urls import path

from incienso_shop.apps.suppliers import views

app_name = "suppliers"

urlpatterns = [
    path("", views.SupplierListView.as_view(), name="supplier_list"),
    path("purchase-orders/", views.PurchaseOrderListView.as_view(), name="purchase_order_list"),
]
