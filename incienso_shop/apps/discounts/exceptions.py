from incienso_shop.apps.core.exceptions import BusinessLogicError


class InvalidCouponError(BusinessLogicError):
    """Lanzada cuando un cupón de descuento no es válido, ha expirado o superó su límite de usos."""
