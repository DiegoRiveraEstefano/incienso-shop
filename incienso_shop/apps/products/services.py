from typing import TYPE_CHECKING

from django.core.cache import cache
from django.db import transaction

from incienso_shop.apps.core.exceptions import BusinessLogicError
from incienso_shop.apps.products.selectors import CACHE_KEY_FEATURED_PRODUCTS

if TYPE_CHECKING:
    from incienso_shop.apps.products.models import Product


class ProductService:
    """Servicios de mutación y lógica transaccional de productos."""

    @staticmethod
    @transaction.atomic
    def adjust_stock(product: Product, quantity_delta: int) -> Product:
        """Aumenta o descuenta stock validando disponibilidad."""
        new_stock = product.stock + quantity_delta
        if new_stock < 0:
            msg = f"Stock insuficiente para {product.name}. Disponible: {product.stock}, Solicitado: {-quantity_delta}"
            raise BusinessLogicError(msg)
        product.stock = new_stock
        product.save(update_fields=["stock", "updated_at"])
        cache.delete(CACHE_KEY_FEATURED_PRODUCTS)
        return product

    @staticmethod
    @transaction.atomic
    def toggle_featured(product: Product) -> Product:
        product.is_featured = not product.is_featured
        product.save(update_fields=["is_featured", "updated_at"])
        cache.delete(CACHE_KEY_FEATURED_PRODUCTS)
        return product
