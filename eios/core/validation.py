"""Quality & Trust validation for the EIOS purchase-operation MVP."""

from __future__ import annotations

from datetime import date

from .models import PurchaseOperation, QualityStatus


def validate_purchase_operation(
    purchase: PurchaseOperation,
    *,
    as_of: date | None = None,
) -> QualityStatus:
    """Apply the Sprint 1 input-quality gate to a validated purchase model.

    This gate checks only structural/business-input quality that is already
    represented by the domain model. It deliberately does not infer open F3
    parameter dependencies or evaluate purchase rules.
    """
    reference_date = as_of or date.today()
    reasons: list[str] = []

    if purchase.operation_date > reference_date:
        reasons.append("La fecha de operación no puede ser futura")

    if purchase.quantity <= 0:
        reasons.append("La cantidad debe ser mayor que cero")

    if purchase.unit_price < 0:
        reasons.append("El precio unitario no puede ser negativo")

    if reasons:
        return QualityStatus(status="FAIL", reasons=reasons)

    return QualityStatus(status="PASS", score=1)


__all__ = ["validate_purchase_operation"]
