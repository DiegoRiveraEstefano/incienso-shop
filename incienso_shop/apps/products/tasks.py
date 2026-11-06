from celery import shared_task

from .models import Product


@shared_task
def sync_product_inventory_alerts():
    """Alerta de stock bajo para productos con menos de 3 unidades."""

    low_stock = Product.objects.filter(stock__lte=3, is_active=True).count()
    return f"Stock bajo verificado: {low_stock} productos en nivel crítico"
