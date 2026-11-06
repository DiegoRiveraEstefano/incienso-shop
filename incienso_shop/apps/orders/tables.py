import django_tables2 as tables

from .models import Order


class OrderTable(tables.Table):
    order_number = tables.TemplateColumn(
        template_code="""
        <a href="{% url 'orders:order_detail' record.order_number %}">#{{ record.order_number|stringformat:'.8s' }}</a>
        """,
        verbose_name="Pedido",
    )
    total_amount = tables.TemplateColumn(
        template_code="<strong>${{ record.total_amount }}</strong>",
        verbose_name="Total",
    )
    status = tables.TemplateColumn(
        template_code="""
        <span class="badge bg-secondary">{{ record.get_status_display }}</span>
        """,
        verbose_name="Estado",
    )

    class Meta:
        model = Order
        template_name = "django_tables2/bootstrap5.html"
        fields = (
            "order_number",
            "customer_name",
            "status",
            "total_amount",
            "created_at",
        )
