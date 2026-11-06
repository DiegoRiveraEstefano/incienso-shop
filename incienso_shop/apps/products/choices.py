from django.db import models
from django.utils.translation import gettext_lazy as _


class AromaFamilyChoices(models.TextChoices):
    RESINS = "RESINAS", _("Resinas Naturales (Copil, Mirra, Incienso)")
    WOODS = "MADERAS", _("Maderas Sagradas (Sándalo, Palo Santo, Cedro)")
    FLORAL = "FLORALES", _("Florales & Dulces (Jazmín, Rosa, Lavanda)")
    HERBAL = "HERBALES", _("Hierbas & Limpieza (Salvia Blanca, Romero, Ruda)")
    SPICY = "ESPECIADOS", _("Especiados & Cálidos (Canela, Clavo, Vainilla)")
    CITRUS = "CITRICOS", _("Cítricos & Revitalizantes (Naranja, Bergamota, Lemongrass)")


class ProductFormatChoices(models.TextChoices):
    STICKS = "STICKS", _("Varillas Tradicionales")
    CONES = "CONES", _("Conos de Humo / Cascada")
    RESIN_GRAINS = "RESIN_GRAINS", _("Granos y Lágrimas de Resina")
    ROPE = "ROPE", _("Incienso de Cuerda Nepalí")
    SMUDGE = "SMUDGE", _("Sahumerio Atado / Smudge Stick")
