from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Configura los grupos de usuario y roles de acceso estándar para Incienso Shop."

    def handle(self, *args, **options):
        roles = {
            "Administradores": {
                "all": True,
            },
            "Gestores de Inventario & Proveedores": {
                "apps": ["inventory", "suppliers", "products"],
            },
            "Agentes CRM & Ventas": {
                "apps": ["crm", "discounts"],
            },
            "Operadores Logísticos": {
                "apps": ["shipping"],
            },
            "Clientes": {
                "apps": [],
            },
        }

        for role_name, config in roles.items():
            group, created = Group.objects.get_or_create(name=role_name)
            action_text = "Creado" if created else "Actualizado"

            if config.get("all"):
                all_perms = Permission.objects.all()
                group.permissions.set(all_perms)
            elif config.get("apps"):
                content_types = ContentType.objects.filter(app_label__in=config["apps"])
                perms = Permission.objects.filter(content_type__in=content_types)
                group.permissions.set(perms)

            self.stdout.write(
                self.style.SUCCESS(f"{action_text} grupo: {role_name} ({group.permissions.count()} permisos)"),
            )

        self.stdout.write(self.style.SUCCESS("Roles y grupos del sistema configurados exitosamente."))
