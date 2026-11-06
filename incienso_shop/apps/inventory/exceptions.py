from incienso_shop.apps.core.exceptions import BusinessLogicError


class InsufficientStockError(BusinessLogicError):
    """Lanzada cuando no hay suficiente stock en los lotes FIFO para satisfacer la demanda."""


class InvalidBatchOperationError(BusinessLogicError):
    """Lanzada cuando una operación sobre un lote es inválida o no permitida."""
