"""Provenance-safe Price Intelligence integration for the Vertical MVP.

The public reuse boundary freezes the complete Price Intelligence inputs and
re-executes the closed C1 engine only after proving that the current purchase
and DecisionContext are exactly the ones from which those inputs were built.
"""
from __future__ import annotations

from collections.abc import Callable

from eios.pricing.engine import run_price_intelligence
from eios.pricing.models import PriceIntelligenceAssessmentContext, PriceIntelligenceInput

from .capability_adapters import adapt_price
from .models import DecisionContext, PurchaseOperation
from .orchestration import CapabilityExecution


PriceInvoker = Callable[[PurchaseOperation, DecisionContext], CapabilityExecution]


def _validate_execution_identity(
    payload: PriceIntelligenceInput,
    purchase: PurchaseOperation,
    context: DecisionContext,
) -> None:
    context_mismatches = tuple(
        field
        for field in (
            "decision_id",
            "scenario_id",
            "rules_version",
            "parameters_version",
            "data_snapshot_id",
        )
        if getattr(payload.decision_context, field) != getattr(context, field)
    )
    if context_mismatches:
        raise ValueError(
            "PriceIntelligenceInput no coincide con DecisionContext: "
            + ", ".join(context_mismatches)
        )

    purchase_mismatches = tuple(
        field
        for field in PurchaseOperation.model_fields
        if getattr(payload.purchase_operation, field) != getattr(purchase, field)
    )
    if purchase_mismatches:
        raise ValueError(
            "PriceIntelligenceInput no coincide con PurchaseOperation: "
            + ", ".join(purchase_mismatches)
        )


def build_provenanced_price_invoker(
    *,
    payload: PriceIntelligenceInput,
    assessment_context: PriceIntelligenceAssessmentContext,
) -> PriceInvoker:
    """Freeze complete C1 inputs and expose the Vertical capability contract."""
    if not isinstance(payload, PriceIntelligenceInput):
        raise TypeError("payload debe ser PriceIntelligenceInput")
    if not isinstance(assessment_context, PriceIntelligenceAssessmentContext):
        raise TypeError("assessment_context debe ser PriceIntelligenceAssessmentContext")

    payload_snapshot = payload.model_copy(deep=True)
    assessment_snapshot = assessment_context.model_copy(deep=True)

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
        result = run_price_intelligence(
            payload_snapshot.model_copy(deep=True),
            assessment_snapshot.model_copy(deep=True),
        )
        return adapt_price(result)

    return invoke


__all__ = ["PriceInvoker", "build_provenanced_price_invoker"]
