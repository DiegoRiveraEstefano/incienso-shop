from typing import TYPE_CHECKING

from django.core.cache import cache

from .models import Category
from .models import Product

if TYPE_CHECKING:
    from django.db.models import QuerySet

CACHE_KEY_FEATURED_PRODUCTS = "featured_products_list"
CACHE_TTL = 300


class ProductSelector:
    """Consultas optimizadas para catálogo de productos."""

    @staticmethod
    def get_active_products() -> QuerySet[Product]:
        return Product.objects.filter(is_active=True).select_related("category").prefetch_related("images", "tags")

    @staticmethod
    def get_featured_products(limit: int = 8) -> list[Product]:
        cached = cache.get(CACHE_KEY_FEATURED_PRODUCTS)
        if cached is None:
            qs = list(
                ProductSelector.get_active_products().filter(is_featured=True)[:limit],
            )
            cache.set(CACHE_KEY_FEATURED_PRODUCTS, qs, CACHE_TTL)
            return qs
        return cached

    @staticmethod
    def get_by_slug(slug: str) -> Product | None:
        return ProductSelector.get_active_products().filter(slug=slug).first()

    @staticmethod
    def list_categories() -> QuerySet[Category]:
        return Category.objects.filter(is_active=True).order_by("sort_order", "name")

    @staticmethod
    def get_category_by_slug(slug: str) -> Category | None:
        return Category.objects.filter(slug=slug, is_active=True).first()
