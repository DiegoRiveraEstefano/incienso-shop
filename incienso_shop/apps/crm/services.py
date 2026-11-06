from decimal import Decimal
from typing import TYPE_CHECKING

from django.core.mail import send_mass_mail
from django.db import transaction
from django.utils import timezone

from incienso_shop.apps.core.exceptions import BusinessLogicError
from incienso_shop.apps.crm.choices import CampaignStatusChoices
from incienso_shop.apps.crm.choices import PointTransactionTypeChoices
from incienso_shop.apps.crm.models import CampaignRecipient
from incienso_shop.apps.crm.models import Deal
from incienso_shop.apps.crm.models import EmailCampaign
from incienso_shop.apps.crm.models import FunnelStage
from incienso_shop.apps.crm.models import LoyaltyTier
from incienso_shop.apps.crm.models import PointTransaction
from incienso_shop.apps.crm.selectors import get_campaign_recipient_emails
from incienso_shop.apps.crm.selectors import get_or_create_loyalty_account

if TYPE_CHECKING:
    from incienso_shop.apps.orders.models import Order


@transaction.atomic
def award_points_for_order(order: Order) -> PointTransaction | None:
    """Calcula y otorga puntos de fidelización tras una compra exitosa."""
    if not order.user:
        return None

    account = get_or_create_loyalty_account(order.user)
    multiplier = account.current_tier.points_multiplier if account.current_tier else Decimal("1.00")

    # 1 punto base por cada $10 gastados en total_amount
    base_points = int(order.total_amount / Decimal("10.00"))
    earned_points = int(base_points * float(multiplier))

    if earned_points <= 0:
        return None

    account.points_balance += earned_points
    account.lifetime_points += earned_points
    account.total_spent += order.total_amount

    # Evaluar si califica para subir de nivel (tier)
    eligible_tier = LoyaltyTier.objects.filter(min_spent__lte=account.total_spent).order_by("-min_spent").first()
    if eligible_tier:
        account.current_tier = eligible_tier

    account.save()

    return PointTransaction.objects.create(
        account=account,
        transaction_type=PointTransactionTypeChoices.PURCHASE_EARNED,
        points=earned_points,
        order=order,
        description=f"Puntos acreditados por Pedido #{str(order.order_number)[:8]}",
    )


@transaction.atomic
def redeem_points(*, user, points: int, reason: str = "Canje de recompensa") -> PointTransaction:
    """Canjea puntos de la cuenta de un cliente si tiene saldo suficiente."""
    if points <= 0:
        msg = "La cantidad de puntos a canjear debe ser positiva."
        raise BusinessLogicError(msg)

    account = get_or_create_loyalty_account(user)
    if account.points_balance < points:
        msg = f"Saldo insuficiente. Disponibles: {account.points_balance}, Solicitados: {points}"
        raise BusinessLogicError(msg)

    account.points_balance -= points
    account.save(update_fields=["points_balance"])

    return PointTransaction.objects.create(
        account=account,
        transaction_type=PointTransactionTypeChoices.REDEMPTION,
        points=-points,
        description=reason,
    )


@transaction.atomic
def move_deal_stage(*, deal_id: int, new_stage_id: int) -> Deal:
    """Mueve una tarjeta de oportunidad comercial (deal) a otra etapa del tablero."""
    deal = Deal.objects.select_related("stage").get(id=deal_id)
    new_stage = FunnelStage.objects.get(id=new_stage_id)
    deal.stage = new_stage
    deal.save(update_fields=["stage"])
    return deal


@transaction.atomic
def send_email_campaign(campaign: EmailCampaign) -> int:
    """Envía la campaña de correo a los destinatarios y registra las entregas."""
    recipient_emails = get_campaign_recipient_emails(campaign.segment)
    if not recipient_emails:
        campaign.status = CampaignStatusChoices.SENT
        campaign.sent_at = timezone.now()
        campaign.recipients_count = 0
        campaign.save(update_fields=["status", "sent_at", "recipients_count"])
        return 0

    messages = [(campaign.subject, campaign.body_html, None, [email]) for email in recipient_emails]

    try:
        send_mass_mail(messages, fail_silently=False)
        campaign.status = CampaignStatusChoices.SENT
    except Exception:
        campaign.status = CampaignStatusChoices.FAILED
        campaign.save(update_fields=["status"])
        raise

    campaign.sent_at = timezone.now()
    campaign.recipients_count = len(recipient_emails)
    campaign.save(update_fields=["status", "sent_at", "recipients_count"])

    # Registrar historial de destinatarios
    recipients_objs = [
        CampaignRecipient(campaign=campaign, email=email, is_delivered=True) for email in recipient_emails
    ]
    CampaignRecipient.objects.bulk_create(recipients_objs)
    return len(recipient_emails)
