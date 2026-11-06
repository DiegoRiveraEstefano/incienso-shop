from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.core import mail

from incienso_shop.apps.crm.choices import CampaignStatusChoices
from incienso_shop.apps.crm.choices import LoyaltyTierChoices
from incienso_shop.apps.crm.choices import PointTransactionTypeChoices
from incienso_shop.apps.crm.models import CustomerSegment
from incienso_shop.apps.crm.models import CustomerSegmentMembership
from incienso_shop.apps.crm.models import Deal
from incienso_shop.apps.crm.models import EmailCampaign
from incienso_shop.apps.crm.models import FunnelStage
from incienso_shop.apps.crm.models import LoyaltyTier
from incienso_shop.apps.crm.models import SalesFunnel
from incienso_shop.apps.crm.selectors import get_funnel_stages_with_deals
from incienso_shop.apps.crm.services import award_points_for_order
from incienso_shop.apps.crm.services import move_deal_stage
from incienso_shop.apps.crm.services import redeem_points
from incienso_shop.apps.crm.services import send_email_campaign
from incienso_shop.apps.orders.models import Order

User = get_user_model()
pytestmark = pytest.mark.django_db


@pytest.fixture
def user():
    return User.objects.create_user(
        username="leal_customer",
        email="leal@cliente.example",
        password="ValidPassword123!",
    )


@pytest.fixture
def tiers():
    bronze = LoyaltyTier.objects.create(
        code=LoyaltyTierChoices.BRONZE,
        name="Bronce",
        min_spent=Decimal("0.00"),
        points_multiplier=Decimal("1.00"),
    )
    gold = LoyaltyTier.objects.create(
        code=LoyaltyTierChoices.GOLD,
        name="Oro",
        min_spent=Decimal("500.00"),
        points_multiplier=Decimal("1.50"),
    )
    return bronze, gold


def test_loyalty_award_points_and_tier_upgrade(user, tiers):
    """Comprueba que una orden otorga puntos y promueve al cliente de tier si supera el gasto."""
    _bronze, gold = tiers
    order = Order.objects.create(
        user=user,
        customer_name="Cliente Fiel",
        customer_email=user.email,
        subtotal=Decimal("600.00"),
        total_amount=Decimal("600.00"),
    )

    tx = award_points_for_order(order)
    assert tx is not None
    assert tx.points == 60  # 600 / 10 = 60
    assert tx.transaction_type == PointTransactionTypeChoices.PURCHASE_EARNED

    account = user.loyalty_account
    assert account.points_balance == 60
    assert account.total_spent == Decimal("600.00")
    # Verificamos que ascendió a nivel Oro (min_spent=500)
    assert account.current_tier == gold


def test_redeem_loyalty_points(user, tiers):
    """Verifica el canje de puntos con validación de saldo."""
    order = Order.objects.create(
        user=user,
        customer_name="Cliente Fiel",
        customer_email=user.email,
        subtotal=Decimal("200.00"),
        total_amount=Decimal("200.00"),
    )
    award_points_for_order(order)  # 20 puntos ganados

    account = user.loyalty_account
    assert account.points_balance == 20

    # Canje exitoso de 15 puntos
    tx_redeem = redeem_points(user=user, points=15, reason="Descuento en vela artesanal")
    assert tx_redeem.points == -15
    account.refresh_from_db()
    assert account.points_balance == 5


def test_sales_funnel_canvas_and_deal_movement():
    """Comprueba el tablero Canvas del embudo y el cambio de etapas de las oportunidades."""
    funnel = SalesFunnel.objects.create(name="Pipeline Mayorista Inciensos")
    stage_prospect = FunnelStage.objects.create(funnel=funnel, name="Prospecto", order=1, color_hex="#3b82f6")
    stage_negotiation = FunnelStage.objects.create(funnel=funnel, name="En Negociación", order=2, color_hex="#f59e0b")
    stage_won = FunnelStage.objects.create(funnel=funnel, name="Ganado", order=3, color_hex="#10b981")

    deal = Deal.objects.create(
        stage=stage_prospect,
        title="Distribución Spa Mandala 500 cajas",
        customer_name="Mandala Spa Resort",
        estimated_value=Decimal("1500.00"),
    )

    # Visualización en Canvas
    stages_qs = get_funnel_stages_with_deals(funnel.id)
    assert len(stages_qs) == 3
    assert stages_qs[0].deals.first() == deal

    # Mover a En Negociación
    move_deal_stage(deal_id=deal.id, new_stage_id=stage_negotiation.id)
    deal.refresh_from_db()
    assert deal.stage == stage_negotiation

    # Mover a Ganado
    move_deal_stage(deal_id=deal.id, new_stage_id=stage_won.id)
    deal.refresh_from_db()
    assert deal.stage == stage_won


def test_customer_segment_and_email_campaign(user):
    """Comprueba la segmentación de clientes y el envío masivo de correos."""
    segment = CustomerSegment.objects.create(name="Amantes del Copal Sagrado")
    CustomerSegmentMembership.objects.create(segment=segment, user=user)

    campaign = EmailCampaign.objects.create(
        title="Lanzamiento Nueva Cosecha de Copal",
        subject="¡Ha llegado el nuevo Copal Blanco!",
        body_html="<p>Disfruta de un 20% en tu próxima compra de copal.</p>",
        segment=segment,
    )

    delivered_count = send_email_campaign(campaign)
    assert delivered_count == 1
    campaign.refresh_from_db()
    assert campaign.status == CampaignStatusChoices.SENT
    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == [user.email]
