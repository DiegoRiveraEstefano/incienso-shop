from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from django.views.generic import DetailView
from django.views.generic import FormView
from django.views.generic import TemplateView
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from incienso_shop.apps.core.exceptions import BusinessLogicError
from incienso_shop.apps.core.selectors import StoreSettingsSelector
from incienso_shop.apps.orders.filters import OrderFilter
from incienso_shop.apps.orders.forms import AddToCartForm
from incienso_shop.apps.orders.forms import CheckoutForm
from incienso_shop.apps.orders.models import Order
from incienso_shop.apps.orders.selectors import CartSelector
from incienso_shop.apps.orders.selectors import OrderSelector
from incienso_shop.apps.orders.services import CartService
from incienso_shop.apps.orders.services import OrderService
from incienso_shop.apps.orders.tables import OrderTable
from incienso_shop.apps.products.models import Product


class CartDetailView(TemplateView):
    """Vista del carrito de compras (compatible con modal/offcanvas y página completa con Unpoly)."""

    template_name = "orders/cart_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = CartSelector.get_or_create_cart(self.request)
        context["cart"] = cart
        context["settings"] = StoreSettingsSelector.get_settings()
        return context


class AddToCartView(View):
    """Agrega un producto al carrito."""

    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id, is_active=True)
        form = AddToCartForm(request.POST)
        qty = form.cleaned_data["quantity"] if form.is_valid() else 1

        cart = CartSelector.get_or_create_cart(request)
        try:
            CartService.add_product(cart, product, quantity=qty)
            messages.success(request, f"{product.name} fue agregado a tu carrito.")
        except BusinessLogicError as exc:
            messages.error(request, str(exc))

        # Redirigir de vuelta a la página o al carrito
        next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or reverse("orders:cart_detail")
        return HttpResponseRedirect(next_url)


class RemoveFromCartView(View):
    """Elimina un ítem del carrito."""

    def post(self, request, product_id):
        cart = CartSelector.get_or_create_cart(request)
        CartService.remove_item(cart, product_id=product_id)
        messages.info(request, "Producto eliminado del carrito.")
        return redirect("orders:cart_detail")


class CheckoutView(FormView):
    """Proceso de checkout e ingreso de datos de envío."""

    template_name = "orders/checkout.html"
    form_class = CheckoutForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = CartSelector.get_or_create_cart(self.request)
        context["cart"] = cart
        context["settings"] = StoreSettingsSelector.get_settings()
        return context

    def form_valid(self, form):
        cart = CartSelector.get_or_create_cart(self.request)
        try:
            order = OrderService.create_order_from_cart(
                cart=cart,
                customer_data=form.cleaned_data,
                user=self.request.user,
            )
            messages.success(
                self.request,
                "Pedido generado exitosamente. Procede al pago seguro.",
            )
            # Redirigir a la vista de pago
            return redirect(
                "shop_payments:start_payment",
                order_number=order.order_number,
            )
        except BusinessLogicError as exc:
            messages.error(self.request, str(exc))
            return self.form_invalid(form)


class OrderDetailView(DetailView):
    """Detalle del pedido y estado."""

    model = Order
    template_name = "orders/order_detail.html"
    context_object_name = "order"
    slug_field = "order_number"
    slug_url_kwarg = "order_number"

    def get_queryset(self):
        return OrderSelector.list_all()


class OrderListView(LoginRequiredMixin, SingleTableMixin, FilterView):
    """Listado de pedidos del usuario autenticado."""

    model = Order
    table_class = OrderTable
    filterset_class = OrderFilter
    template_name = "orders/order_list.html"
    context_object_name = "orders"

    def get_queryset(self):
        if self.request.user.is_staff:
            return OrderSelector.list_all()
        return OrderSelector.list_for_user(self.request.user)
