import django_tables2 as tables

from .models import Product


class ProductTable(tables.Table):
    name = tables.Column(linkify=True, verbose_name="Incienso")
    price = tables.TemplateColumn(
        template_code="<strong>${{ record.price }}</strong>",
        verbose_name="Precio",
    )
    stock = tables.TemplateColumn(
        template_code="""
        {% if record.stock > 5 %}
          <span class="badge bg-success">{{ record.stock }} disp.</span>
        {% elif record.stock > 0 %}
          <span class="badge bg-warning text-dark">{{ record.stock }} últimas</span>
        {% else %}
          <span class="badge bg-danger">Agotado</span>
        {% endif %}
        """,
        verbose_name="Disponibilidad",
    )

    class Meta:
        model = Product
        template_name = "django_tables2/bootstrap5.html"
        fields = ("name", "sku", "category", "aroma_family", "price", "stock")
