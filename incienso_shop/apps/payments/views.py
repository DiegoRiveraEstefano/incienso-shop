from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView

from incienso_shop.apps.orders.models import Order
from incienso_shop.apps.orders.selectors import OrderSelector
from incienso_shop.apps.payments.selectors import PaymentSelector
from incienso_shop.apps.payments.services import PaymentService


class StartPaymentView(View):
    """Inicializa la pasarela de pago para una orden utilizando django-payments."""

    template_name = "payments/payment_form.html"

    def get(self, request, order_number):
        order = get_object_or_404(Order, order_number=order_number)
        payment = PaymentSelector.get_latest_for_order(order)
        if not payment or payment.status in ["confirmed", "rejected"]:
            payment = PaymentService.create_payment_for_order(order, variant="dummy")

        try:
            form = payment.get_form(data=request.POST or None)
        except AttributeError, KeyError, ValueError, TypeError:
            form = None

        return render(
            request,
            self.template_name,
            {
                "order": order,
                "payment": payment,
                "form": form,
            },
        )

    def post(self, request, order_number):
        order = get_object_or_404(Order, order_number=order_number)
        payment = PaymentSelector.get_latest_for_order(order)
        if not payment:
            payment = PaymentService.create_payment_for_order(order, variant="dummy")

        form = payment.get_form(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect(payment.get_success_url())

        return render(
            request,
            self.template_name,
            {
                "order": order,
                "payment": payment,
                "form": form,
            },
        )


class PaymentSuccessView(TemplateView):
    """Confirmación de pago exitoso."""

    template_name = "payments/payment_success.html"

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_number = self.kwargs["order_number"]
        order = OrderSelector.get_by_number(order_number)
        if order:
            payment = PaymentSelector.get_latest_for_order(order)
            if payment and payment.status != "confirmed":
                PaymentService.complete_payment(payment)
        context["order"] = order
        return context


class PaymentFailureView(TemplateView):
    """Pantalla ante fallos o rechazos en el pago."""

    template_name = "payments/payment_failure.html"

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_number = self.kwargs["order_number"]
        context["order"] = OrderSelector.get_by_number(order_number)
        return context


class TrialBalanceView(LoginRequiredMixin, TemplateView):
    """Libro Mayor y Balance de Comprobación de Partida Doble."""

    template_name = "payments/trial_balance.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["trial_balance"] = PaymentSelector.get_trial_balance()
        return context
