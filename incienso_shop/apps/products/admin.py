from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import Category
from .models import Product
from .models import ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Category)
class CategoryAdmin(SimpleHistoryAdmin):
    list_display = ("name", "slug", "is_active", "sort_order", "created_at")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(SimpleHistoryAdmin):
    list_display = (
        "name",
        "sku",
        "category",
        "aroma_family",
        "price",
        "stock",
        "is_featured",
        "is_active",
    )
    list_filter = (
        "category",
        "aroma_family",
        "product_format",
        "is_featured",
        "is_active",
    )
    search_fields = ("name", "sku", "description")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductImageInline]
