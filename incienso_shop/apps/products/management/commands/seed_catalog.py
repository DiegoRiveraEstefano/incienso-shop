# ruff: noqa: E501
from decimal import Decimal

from django.core.management.base import BaseCommand

from incienso_shop.apps.core.models import StoreSettings
from incienso_shop.apps.products.choices import AromaFamilyChoices
from incienso_shop.apps.products.choices import ProductFormatChoices
from incienso_shop.apps.products.models import Category
from incienso_shop.apps.products.models import Product


class Command(BaseCommand):
    help = "Puebla el catálogo de inciensos con productos iniciales artesanales para demo/portafolio."

    def handle(self, *args, **options):
        self.stdout.write("Inicializando StoreSettings...")
        StoreSettings.objects.get_or_create(
            id=1,
            defaults={
                "store_name": "Incienso Shop Artesanal",
                "tagline": "Aromas sagrados y resinas naturales para tu espacio",
                "free_shipping_threshold": Decimal("50.00"),
                "standard_shipping_cost": Decimal("4.99"),
                "tax_rate_pct": Decimal("19.00"),
            },
        )

        self.stdout.write("Creando Categorías...")
        cat_resinas, _ = Category.objects.get_or_create(
            slug="resinas-naturales",
            defaults={
                "name": "Resinas Naturales",
                "description": "Copal, mirra e incienso puro en lágrimas y varillas.",
                "icon": "bi-gem",
                "sort_order": 1,
            },
        )

        cat_maderas, _ = Category.objects.get_or_create(
            slug="maderas-sagradas",
            defaults={
                "name": "Maderas Sagradas",
                "description": "Palo santo de recolección ética, sándalo y cedro.",
                "icon": "bi-tree",
                "sort_order": 2,
            },
        )

        cat_florales, _ = Category.objects.get_or_create(
            slug="florales-y-calma",
            defaults={
                "name": "Florales & Calma",
                "description": "Lavanda, rosa y jazmín para serenidad y meditación.",
                "icon": "bi-flower1",
                "sort_order": 3,
            },
        )

        self.stdout.write("Creando Productos de Incienso...")
        products_data = [
            {
                "name": "Copal Blanco Sagrado de México",
                "slug": "copal-blanco-sagrado",
                "sku": "COP-001",
                "category": cat_resinas,
                "aroma_family": AromaFamilyChoices.RESINS,
                "product_format": ProductFormatChoices.STICKS,
                "origin_country": "México",
                "burn_time_minutes": 55,
                "pieces_count": 15,
                "price": Decimal("14.50"),
                "compare_at_price": Decimal("18.00"),
                "stock": 25,
                "is_featured": True,
                "description": "Incienso de copal blanco silvestre de recolección sustentable. Humo blanco denso con notas cítricas resinosas ideal para purificar hogares y consagrar espacios de meditación.",
            },
            {
                "name": "Palo Santo de Piura Seleccionado",
                "slug": "palo-santo-piura",
                "sku": "PLS-002",
                "category": cat_maderas,
                "aroma_family": AromaFamilyChoices.WOODS,
                "product_format": ProductFormatChoices.STICKS,
                "origin_country": "Perú",
                "burn_time_minutes": 45,
                "pieces_count": 20,
                "price": Decimal("12.90"),
                "compare_at_price": None,
                "stock": 30,
                "is_featured": True,
                "description": "Varillas artesanales moldeadas con serrín puro de Palo Santo caído de forma natural y añejado durante más de 4 años en el bosque seco del norte peruano.",
            },
            {
                "name": "Sándalo de Mysore Puro",
                "slug": "sandalo-mysore-puro",
                "sku": "SAN-003",
                "category": cat_maderas,
                "aroma_family": AromaFamilyChoices.WOODS,
                "product_format": ProductFormatChoices.STICKS,
                "origin_country": "India",
                "burn_time_minutes": 60,
                "pieces_count": 12,
                "price": Decimal("19.90"),
                "compare_at_price": Decimal("24.00"),
                "stock": 18,
                "is_featured": True,
                "description": "El clásico aroma amaderado, cálido y aterciopelado del sándalo tradicional indio. Fomenta el enfoque mental, la contemplación y el sosiego.",
            },
            {
                "name": "Mirra Sagrada & Incienso Olibano",
                "slug": "mirra-sagrada-olibano",
                "sku": "MYR-004",
                "category": cat_resinas,
                "aroma_family": AromaFamilyChoices.RESINS,
                "product_format": ProductFormatChoices.CONES,
                "origin_country": "Somalia",
                "burn_time_minutes": 35,
                "pieces_count": 10,
                "price": Decimal("11.50"),
                "compare_at_price": None,
                "stock": 14,
                "is_featured": False,
                "description": "Conos aromáticos elaborados con resina pura de Commiphora myrrha y Boswellia carterii. Fragancia profunda, balsámica y terrosa.",
            },
            {
                "name": "Lavanda de la Provenza Relajante",
                "slug": "lavanda-provenza-relajante",
                "sku": "LAV-005",
                "category": cat_florales,
                "aroma_family": AromaFamilyChoices.FLORAL,
                "product_format": ProductFormatChoices.STICKS,
                "origin_country": "Francia",
                "burn_time_minutes": 50,
                "pieces_count": 20,
                "price": Decimal("10.90"),
                "compare_at_price": Decimal("13.00"),
                "stock": 40,
                "is_featured": True,
                "description": "Flores secas de lavanda francesa maceradas con aceite esencial puro. Perfecto para disipar el estrés y acompañar rituales nocturnos de descanso.",
            },
        ]

        for p_data in products_data:
            p, created = Product.objects.get_or_create(
                slug=p_data["slug"],
                defaults=p_data,
            )
            if created:
                self.stdout.write(f"  + Creado: {p.name}")

        self.stdout.write(self.style.SUCCESS("Catálogo inicial sembrado exitosamente."))
