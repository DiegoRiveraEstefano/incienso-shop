from decimal import Decimal

from auditlog.registry import auditlog
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords

from incienso_shop.apps.core.base_models import BaseModel
from incienso_shop.apps.crm.choices import CampaignStatusChoices
from incienso_shop.apps.crm.choices import DealPriorityChoices
from incienso_shop.apps.crm.choices import LoyaltyTierChoices
from incienso_shop.apps.crm.choices import PointTransactionTypeChoices
from incienso_shop.apps.orders.models import Order


@auditlog.register()
class LoyaltyTier(BaseModel):
    """Nivel de fidelización y privilegios para clientes."""

    code = models.CharField(
        _("Código de Nivel"),
        max_length=20,
        choices=LoyaltyTierChoices.choices,
        unique=True,
    )
    name = models.CharField(_("Nombre Público"), max_length=100)
    min_spent = models.DecimalField(
        _("Gasto Mínimo Acumulado"), max_digits=10, decimal_places=2, default=Decimal("0.00"),
    )
    points_multiplier = models.DecimalField(
        _("Multiplicador de Puntos"), max_digits=4, decimal_places=2, default=Decimal("1.00"),
    )
    badge_color = models.CharField(_("Color Badge (Hex / CSS)"), max_length=20, default="#d4af37")

    class Meta:
        verbose_name = _("Nivel de Fidelización")
        verbose_name_plural = _("Niveles de Fidelización")
        ordering = ["min_spent"]

    def __str__(self) -> str:
        return f"{self.name} (x{self.points_multiplier})"


@auditlog.register()
class LoyaltyAccount(BaseModel):
    """Cuenta de fidelización personal de un cliente."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="loyalty_account",
        verbose_name=_("Cliente"),
    )
    current_tier = models.ForeignKey(
        LoyaltyTier,
        on_delete=models.PROTECT,
        related_name="members",
        verbose_name=_("Nivel Actual"),
        null=True,
        blank=True,
    )
    points_balance = models.PositiveIntegerField(_("Puntos Disponibles"), default=0)
    lifetime_points = models.PositiveIntegerField(_("Puntos Históricos Totales"), default=0)
    total_spent = models.DecimalField(
        _("Total Gastado Histórico"), max_digits=12, decimal_places=2, default=Decimal("0.00"),
    )

    history = HistoricalRecords()

    class Meta:
        verbose_name = _("Cuenta de Fidelización")
        verbose_name_plural = _("Cuentas de Fidelización")

    def __str__(self) -> str:
        return f"Fidelización {self.user.username}: {self.points_balance} pts"


@auditlog.register()
class PointTransaction(BaseModel):
    """Bitácora inmutable de acumulación y canje de puntos."""

    account = models.ForeignKey(
        LoyaltyAccount,
        on_delete=models.CASCADE,
        related_name="transactions",
        verbose_name=_("Cuenta"),
    )
    transaction_type = models.CharField(
        _("Tipo"),
        max_length=20,
        choices=PointTransactionTypeChoices.choices,
    )
    points = models.IntegerField(_("Puntos (+/-)"))
    order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="loyalty_transactions",
        verbose_name=_("Pedido Origen"),
    )
    description = models.CharField(_("Descripción / Motivo"), max_length=255)

    class Meta:
        verbose_name = _("Transacción de Puntos")
        verbose_name_plural = _("Transacciones de Puntos")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.get_transaction_type_display()}: {self.points:+d} pts ({self.account.user.username})"


@auditlog.register()
class CustomerSegment(BaseModel):
    """Grupo o segmento de clientes para campañas y descuentos."""

    name = models.CharField(_("Nombre del Grupo"), max_length=150, unique=True)
    description = models.TextField(_("Descripción del Segmento"), blank=True)
    is_active = models.BooleanField(_("Activo"), default=True)

    class Meta:
        verbose_name = _("Segmento de Clientes")
        verbose_name_plural = _("Segmentos de Clientes")
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class CustomerSegmentMembership(BaseModel):
    """Asociación de un cliente a un segmento."""

    segment = models.ForeignKey(
        CustomerSegment,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="segment_memberships",
    )

    class Meta:
        verbose_name = _("Membresía de Segmento")
        verbose_name_plural = _("Membresías de Segmentos")
        unique_together = ("segment", "user")

    def __str__(self) -> str:
        return f"{self.user.username} en {self.segment.name}"


@auditlog.register()
class SalesFunnel(BaseModel):
    """Embudo de ventas o proceso comercial."""

    name = models.CharField(_("Nombre del Embudo"), max_length=150)
    description = models.TextField(_("Descripción"), blank=True)
    is_active = models.BooleanField(_("Activo"), default=True)

    class Meta:
        verbose_name = _("Embudo de Ventas")
        verbose_name_plural = _("Embudos de Ventas")

    def __str__(self) -> str:
        return self.name


class FunnelStage(BaseModel):
    """Etapa o columna en el tablero Canvas / Kanban del embudo."""

    funnel = models.ForeignKey(
        SalesFunnel,
        on_delete=models.CASCADE,
        related_name="stages",
        verbose_name=_("Embudo"),
    )
    name = models.CharField(_("Nombre de la Etapa"), max_length=100)
    order = models.PositiveIntegerField(_("Orden de Columna"), default=0)
    color_hex = models.CharField(_("Color de Columna (Hex)"), max_length=7, default="#4a5568")

    class Meta:
        verbose_name = _("Etapa de Embudo")
        verbose_name_plural = _("Etapas de Embudo")
        ordering = ["funnel", "order"]

    def __str__(self) -> str:
        return f"{self.funnel.name} - {self.name}"


@auditlog.register()
class Deal(BaseModel):
    """Trato u oportunidad comercial representada como tarjeta en el Canvas."""

    stage = models.ForeignKey(
        FunnelStage,
        on_delete=models.PROTECT,
        related_name="deals",
        verbose_name=_("Etapa Actual"),
    )
    title = models.CharField(_("Título del Trato"), max_length=200)
    customer_name = models.CharField(_("Cliente / Empresa"), max_length=200)
    customer_email = models.EmailField(_("Correo Electrónico"), blank=True)
    customer_phone = models.CharField(_("Teléfono"), max_length=50, blank=True)
    estimated_value = models.DecimalField(
        _("Valor Estimado"),
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    priority = models.CharField(
        _("Prioridad"),
        max_length=20,
        choices=DealPriorityChoices.choices,
        default=DealPriorityChoices.MEDIUM,
    )
    expected_close_date = models.DateField(_("Fecha Estimada de Cierre"), null=True, blank=True)
    notes = models.TextField(_("Notas y Bitácora"), blank=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = _("Oportunidad Comercial (Deal)")
        verbose_name_plural = _("Oportunidades Comerciales (Deals)")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.title} (${self.estimated_value}) [{self.stage.name}]"


@auditlog.register()
class EmailCampaign(BaseModel):
    """Campaña de correo electrónico dirigida a todos o a un segmento de clientes."""

    title = models.CharField(_("Nombre Interno"), max_length=200)
    subject = models.CharField(_("Asunto del Email"), max_length=255)
    body_html = models.TextField(_("Cuerpo del Correo (HTML / Texto)"))
    segment = models.ForeignKey(
        CustomerSegment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="campaigns",
        verbose_name=_("Segmento Destinatario (Dejar vacío para Todos)"),
    )
    status = models.CharField(
        _("Estado"),
        max_length=20,
        choices=CampaignStatusChoices.choices,
        default=CampaignStatusChoices.DRAFT,
    )
    sent_at = models.DateTimeField(_("Fecha de Envío"), null=True, blank=True)
    recipients_count = models.PositiveIntegerField(_("Destinatarios"), default=0)

    class Meta:
        verbose_name = _("Campaña de Email")
        verbose_name_plural = _("Campañas de Email")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.title} ({self.get_status_display()})"


class CampaignRecipient(BaseModel):
    """Registro individual de envío a un destinatario."""

    campaign = models.ForeignKey(
        EmailCampaign,
        on_delete=models.CASCADE,
        related_name="recipients",
    )
    email = models.EmailField(_("Email"))
    is_delivered = models.BooleanField(_("Entregado"), default=False)
    delivered_at = models.DateTimeField(_("Hora de Entrega"), default=timezone.now)

    class Meta:
        verbose_name = _("Destinatario de Campaña")
        verbose_name_plural = _("Destinatarios de Campañas")
