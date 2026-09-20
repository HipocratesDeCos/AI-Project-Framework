"""Deterministic EIOS Profitability Core v0.1."""
from __future__ import annotations

from decimal import Decimal

from .models import (
    ProfitabilityCalculationState,
    ProfitabilityInput,
    ProfitabilityResult,
)


def _dedupe(values: tuple[str, ...] | list[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(values))


def _non_known_state(payload: ProfitabilityInput) -> ProfitabilityCalculationState | None:
    states = (payload.sale_basis.state, payload.cost_basis.state)
    if "CONFLICTING_DATA" in states:
        return "CONFLICTING_DATA"
    if "NOT_EVIDENCED" in states:
        return "NOT_EVIDENCED"
    if "NOT_DETERMINABLE" in states:
        return "NOT_DETERMINABLE"
    return None


def _result(
    payload: ProfitabilityInput,
    *,
    state: ProfitabilityCalculationState,
    currency: str | None = None,
    economic_basis_ref: str | None = None,
    margin_amount: Decimal | None = None,
    margin_percentage: Decimal | None = None,
    limitations: tuple[str, ...] = (),
) -> ProfitabilityResult:
    traces = _dedupe(payload.sale_basis.trace_refs + payload.cost_basis.trace_refs)
    return ProfitabilityResult(
        decision_id=payload.context.decision_id,
        scenario_id=payload.context.scenario_id,
        data_snapshot_id=payload.context.data_snapshot_id,
        parameters_version=payload.context.parameters_version,
        company_scope=payload.company_scope,
        article_id=payload.purchase_operation.article_id,
        evaluation_date=payload.evaluation_date,
        methodology_version=payload.methodology_version,
        sale_basis=payload.sale_basis,
        cost_basis=payload.cost_basis,
        calculation_state=state,
        currency=currency,
        economic_basis_ref=economic_basis_ref,
        margin_amount=margin_amount,
        margin_percentage=margin_percentage,
        limitations=limitations,
        trace_refs=traces,
    )


def calculate_profitability(payload: ProfitabilityInput) -> ProfitabilityResult:
    """Calculate profitability only from pre-authorized compatible bases."""
    if not isinstance(payload, ProfitabilityInput):
        raise TypeError("payload debe ser ProfitabilityInput")

    blocked_state = _non_known_state(payload)
    if blocked_state is not None:
        return _result(payload, state=blocked_state)

    sale = payload.sale_basis
    cost = payload.cost_basis

    # Model invariants guarantee KNOWN bases expose these values.
    assert sale.value is not None
    assert cost.value is not None
    assert sale.currency is not None
    assert cost.currency is not None
    assert sale.economic_basis_ref is not None
    assert cost.economic_basis_ref is not None

    limitations: list[str] = []
    if sale.currency != cost.currency:
        limitations.append("CURRENCY_INCOMPATIBLE")
    if sale.economic_basis_ref != cost.economic_basis_ref:
        limitations.append("ECONOMIC_BASIS_INCOMPATIBLE")
    if limitations:
        return _result(
            payload,
            state="NOT_DETERMINABLE",
            limitations=_dedupe(limitations),
        )

    margin_amount = sale.value - cost.value

    if sale.value == 0:
        return _result(
            payload,
            state="NOT_DETERMINABLE",
            currency=sale.currency,
            economic_basis_ref=sale.economic_basis_ref,
            margin_amount=margin_amount,
            margin_percentage=None,
            limitations=("SALE_BASIS_ZERO",),
        )

    margin_percentage = margin_amount / sale.value * Decimal("100")
    return _result(
        payload,
        state="DETERMINED",
        currency=sale.currency,
        economic_basis_ref=sale.economic_basis_ref,
        margin_amount=margin_amount,
        margin_percentage=margin_percentage,
        limitations=(),
    )


__all__ = ["calculate_profitability"]
