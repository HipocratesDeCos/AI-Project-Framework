"""Provenance-safe TCO integration for the EIOS Vertical MVP."""
from __future__ import annotations

from collections.abc import Callable

from eios.tco.engine import calculate_tco
from eios.tco.models import TCOInput

from .capability_adapters import adapt_tco
from .models import DecisionContext, PurchaseOperation
from .orchestration import CapabilityExecution


TCOInvoker = Callable[[PurchaseOperation, DecisionContext], CapabilityExecution]


def _validate_execution_identity(
    payload: TCOInput,
    purchase: PurchaseOperation,
    context: DecisionContext,
) -> None:
    purchase_mismatches = tuple(
        field
        for field in PurchaseOperation.model_fields
        if getattr(payload.purchase_operation, field) != getattr(purchase, field)
    )
    if purchase_mismatches:
        raise ValueError(
            "TCOInput no coincide con PurchaseOperation: "
            + ", ".join(purchase_mismatches)
        )

    context_mismatches = tuple(
        field
        for field in ("decision_id", "scenario_id")
        if getattr(purchase, field) != getattr(context, field)
    )
    if context_mismatches:
        raise ValueError(
            "PurchaseOperation no coincide con DecisionContext para TCO: "
            + ", ".join(context_mismatches)
        )


def build_provenanced_tco_invoker(*, payload: TCOInput) -> TCOInvoker:
    """Freeze complete TCO input and expose the Vertical capability contract."""
    if not isinstance(payload, TCOInput):
        raise TypeError("payload debe ser TCOInput")

    payload_snapshot = payload.model_copy(deep=True)

    def invoke(
        purchase: PurchaseOperation,
        context: DecisionContext,
    ) -> CapabilityExecution:
        purchase_snapshot = purchase.model_copy(deep=True)
        context_snapshot = context.model_copy(deep=True)
        _validate_execution_identity(
            payload_snapshot,
            purchase_snapshot,
            context_snapshot,
        )
        result = calculate_tco(payload_snapshot.model_copy(deep=True))
        return adapt_tco(result)

    return invoke


__all__ = ["TCOInvoker", "build_provenanced_tco_invoker"]
