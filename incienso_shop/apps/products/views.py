from django.views.generic import DetailView
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from .filters import ProductFilter
from .models import Category
from .models import Product
from .selectors import ProductSelector
from .tables import ProductTable


class ProductListView(SingleTableMixin, FilterView):
    model = Product
    table_class = ProductTable
    filterset_class = ProductFilter
    template_name = "products/product_list.html"
    context_object_name = "products"
    paginate_by = 12

    def get_queryset(self):
        return ProductSelector.get_active_products()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = ProductSelector.list_categories()
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = "products/product_detail.html"
    context_object_name = "product"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return ProductSelector.get_active_products()


class CategoryDetailView(DetailView):
    model = Category
    template_name = "products/category_detail.html"
    context_object_name = "category"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["products"] = ProductSelector.get_active_products().filter(
            category=self.object,
        )
        return context
