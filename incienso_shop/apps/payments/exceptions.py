from incienso_shop.apps.core.exceptions import BusinessLogicError


class UnbalancedTransactionError(BusinessLogicError):
    """Lanzada cuando un asiento contable no cumple con la regla de partida doble (Débitos != Créditos)."""
