from django.urls import path

from .views import PaymentFailureView
from .views import PaymentSuccessView
from .views import StartPaymentView
from .views import TrialBalanceView

app_name = "shop_payments"

urlpatterns = [
    path("pay/<uuid:order_number>/", StartPaymentView.as_view(), name="start_payment"),
    path(
        "success/<uuid:order_number>/",
        PaymentSuccessView.as_view(),
        name="payment_success",
    ),
    path(
        "failure/<uuid:order_number>/",
        PaymentFailureView.as_view(),
        name="payment_failure",
    ),
    path(
        "ledger/trial-balance/",
        TrialBalanceView.as_view(),
        name="trial_balance",
    ),
]
