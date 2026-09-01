"""Deterministic TCO Core calculation."""
from __future__ import annotations

from decimal import Decimal
from .models import TCOInput, TCOResult


def calculate_tco(payload: TCOInput) -> TCOResult:
    """Calculate acquisition cost plus valid directly attributable costs.

    No FX conversion, financial cost, storage, obsolescence, returns or other
    GAP-TCO-01 extensions are performed here.
    """
    operation = payload.purchase_operation
    base = operation.quantity * operation.unit_price
    total = base
    contributing = ["ACQUISITION"]
    unresolved: list[str] = []
    limitations: list[str] = []

    for component in payload.attributable_costs:
        if component.applicability == "NOT_APPLICABLE":
            continue
        if component.currency != operation.currency:
            unresolved.append(component.component)
            limitations.append(f"CURRENCY_INCOMPATIBLE:{component.component}")
            continue
        assert component.amount is not None
        total += component.amount
        contributing.append(component.component)

    value = total if not unresolved else None
    return TCOResult(
        decision_id=operation.decision_id,
        scenario_id=operation.scenario_id,
        currency=operation.currency,
        value=value,
        contributing_components=tuple(contributing),
        unresolved_components=tuple(unresolved),
        limitations=tuple(dict.fromkeys(limitations)),
    )


__all__ = ["calculate_tco"]
