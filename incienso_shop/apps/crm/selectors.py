from django.contrib.auth import get_user_model
from django.db.models import Prefetch
from django.db.models import QuerySet

from incienso_shop.apps.crm.models import CustomerSegment
from incienso_shop.apps.crm.models import Deal
from incienso_shop.apps.crm.models import FunnelStage
from incienso_shop.apps.crm.models import LoyaltyAccount
from incienso_shop.apps.crm.models import LoyaltyTier
from incienso_shop.apps.crm.models import SalesFunnel

User = get_user_model()


def get_default_sales_funnel() -> SalesFunnel | None:
    """Obtiene el embudo de ventas activo por defecto."""
    return SalesFunnel.objects.filter(is_active=True).first()


def get_funnel_stages_with_deals(funnel_id: int) -> QuerySet[FunnelStage]:
    """Carga todas las etapas del embudo con sus deals para el tablero Canvas/Kanban."""
    deals_prefetch = Prefetch(
        "deals",
        queryset=Deal.objects.order_by("-priority", "-created_at"),
    )
    return FunnelStage.objects.filter(funnel_id=funnel_id).prefetch_related(deals_prefetch).order_by("order")


def get_or_create_loyalty_account(user) -> LoyaltyAccount:
    """Obtiene o inicializa la cuenta de fidelización del cliente."""
    base_tier = LoyaltyTier.objects.order_by("min_spent").first()
    account, _ = LoyaltyAccount.objects.get_or_create(
        user=user,
        defaults={"current_tier": base_tier},
    )
    return account


def get_all_segments() -> QuerySet[CustomerSegment]:
    return CustomerSegment.objects.filter(is_active=True).prefetch_related("memberships__user").order_by("name")


def get_campaign_recipient_emails(segment: CustomerSegment | None = None) -> list[str]:
    """Retorna la lista de correos de clientes suscritos a un segmento o a toda la tienda."""
    if segment:
        emails = list(
            User.objects.filter(segment_memberships__segment=segment, is_active=True)
            .exclude(email="")
            .values_list("email", flat=True)
            .distinct(),
        )
    else:
        emails = list(User.objects.filter(is_active=True).exclude(email="").values_list("email", flat=True).distinct())
    return emails
