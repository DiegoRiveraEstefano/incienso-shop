from django.urls import path

from incienso_shop.apps.inventory import views

app_name = "inventory"

urlpatterns = [
    path("", views.InventoryDashboardView.as_view(), name="dashboard"),
    path("batches/", views.BatchListView.as_view(), name="batch_list"),
]
