from decimal import Decimal
from http import HTTPStatus

import pytest
from django.urls import reverse

from incienso_shop.apps.audit.models import AuditEvent
from incienso_shop.apps.core.models import StoreSettings
from incienso_shop.apps.products.choices import AromaFamilyChoices
from incienso_shop.apps.products.models import Category
from incienso_shop.apps.products.models import Product
from incienso_shop.apps.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


def test_auditlog_records_creation_and_update():
    settings = StoreSettings.objects.create(
        store_name="Audit Store",
        tagline="Aromas sagrados",
        currency="USD",
    )
    entries = AuditEvent.objects.filter(object_pk=str(settings.pk))
    assert entries.count() == 1
    create_entry = entries.first()
    assert create_entry is not None
    assert create_entry.action == 0

    settings.tagline = "Aromas botánicos actualizados"
    settings.save()

    entries = AuditEvent.objects.filter(object_pk=str(settings.pk))
    expected_entry_count = 2
    assert entries.count() == expected_entry_count
    update_entry = entries.order_by("-timestamp").first()
    assert update_entry is not None
    assert update_entry.action == 1
    assert "Aromas sagrados" in str(update_entry.changes_display_dict)
    assert "Aromas botánicos actualizados" in str(update_entry.changes_display_dict)


def test_auditlog_views_display_events_and_diff(client):
    admin = UserFactory(is_superuser=True, is_staff=True)
    client.force_login(admin)

    cat = Category.objects.create(name="Resinas Test", slug="resinas-test")
    product = Product.objects.create(
        name="Audited Incense",
        slug="audited-incense",
        sku="AUD-001",
        category=cat,
        aroma_family=AromaFamilyChoices.RESINS,
        price=Decimal("15.00"),
    )
    product.name = "Audited Incense Updated"
    product.save()

    entry = AuditEvent.objects.filter(object_pk=str(product.pk)).first()
    assert entry is not None

    res_list = client.get(reverse("audit:audit_list"))
    assert res_list.status_code == HTTPStatus.OK
    assert "Audited Incense" in res_list.rendered_content

    res_detail = client.get(entry.get_absolute_url())
    assert res_detail.status_code == HTTPStatus.OK
    assert "Detalle de Cambios" in res_detail.rendered_content
