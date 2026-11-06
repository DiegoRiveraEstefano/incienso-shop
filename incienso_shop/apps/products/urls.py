from django.urls import path

from .views import CategoryDetailView
from .views import ProductDetailView
from .views import ProductListView

app_name = "products"

urlpatterns = [
    path("", ProductListView.as_view(), name="product_list"),
    path("<slug:slug>/", ProductDetailView.as_view(), name="product_detail"),
    path("category/<slug:slug>/", CategoryDetailView.as_view(), name="category_detail"),
]
