"""Provenance-safe Price Intelligence integration for the Vertical MVP.

The public reuse boundary freezes the complete Price Intelligence inputs and
re-executes the closed C1 engine only after proving that the current purchase
and DecisionContext are exactly the ones from which those inputs were built.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from threading import Lock

from eios.pricing.engine import run_price_intelligence
from eios.pricing.models import (
    PriceIntelligenceAssessmentContext, PriceIntelligenceInput,
    PriceIntelligenceResult,
)

from .capability_adapters import adapt_price
from .models import DecisionContext, PurchaseOperation
from .orchestration import CapabilityExecution


PriceInvoker = Callable[[PurchaseOperation, DecisionContext], CapabilityExecution]


@dataclass(frozen=True)
class PriceInvocationCapture:
    result: PriceIntelligenceResult
    capability: CapabilityExecution


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


def _produce_bound_price(
    payload: PriceIntelligenceInput,
    assessment_context: PriceIntelligenceAssessmentContext,
    purchase: PurchaseOperation,
    context: DecisionContext,
) -> PriceIntelligenceResult:
    _validate_execution_identity(payload, purchase, context)
    return run_price_intelligence(
        payload.model_copy(deep=True), assessment_context.model_copy(deep=True),
    )


def _frozen_sources(
    payload: PriceIntelligenceInput,
    assessment_context: PriceIntelligenceAssessmentContext,
) -> tuple[PriceIntelligenceInput, PriceIntelligenceAssessmentContext]:
    if not isinstance(payload, PriceIntelligenceInput):
        raise TypeError("payload debe ser PriceIntelligenceInput")
    if not isinstance(assessment_context, PriceIntelligenceAssessmentContext):
        raise TypeError("assessment_context debe ser PriceIntelligenceAssessmentContext")
    return payload.model_copy(deep=True), assessment_context.model_copy(deep=True)


class ObservedPriceInvoker:
    """One-shot O1-compatible PRICE invoker with a private same-call capture."""

    def __init__(self, payload: PriceIntelligenceInput,
                 assessment_context: PriceIntelligenceAssessmentContext,
                 reference_case_id: str) -> None:
        if not isinstance(reference_case_id, str) or not reference_case_id.strip() \
                or reference_case_id != reference_case_id.strip():
            raise ValueError("reference_case_id is required")
        self.reference_case_id = reference_case_id
        self._payload, self._assessment = _frozen_sources(payload, assessment_context)
        self._lock = Lock()
        self._used = False
        self._capture: PriceInvocationCapture | None = None

    def __call__(self, purchase: PurchaseOperation,
                 context: DecisionContext) -> CapabilityExecution:
        with self._lock:
            if self._used:
                raise ValueError("Observed PRICE invoker is single-use")
            self._used = True
            result = _produce_bound_price(
                self._payload, self._assessment,
                purchase.model_copy(deep=True), context.model_copy(deep=True),
            )
            capability = adapt_price(result)
            self._capture = PriceInvocationCapture(
                result.model_copy(deep=True), capability.model_copy(deep=True),
            )
            return capability

    def capture(self) -> PriceInvocationCapture:
        with self._lock:
            if self._capture is None:
                raise ValueError("PRICE observation is unavailable before successful invocation")
            return PriceInvocationCapture(
                self._capture.result.model_copy(deep=True),
                self._capture.capability.model_copy(deep=True),
            )


def build_reference_observed_price_invoker(
    *, payload: PriceIntelligenceInput,
    assessment_context: PriceIntelligenceAssessmentContext,
    reference_case_id: str,
) -> ObservedPriceInvoker:
    return ObservedPriceInvoker(payload, assessment_context, reference_case_id)


def build_provenanced_price_invoker(
    *,
    payload: PriceIntelligenceInput,
    assessment_context: PriceIntelligenceAssessmentContext,
) -> PriceInvoker:
    """Freeze complete C1 inputs and expose the Vertical capability contract."""
    payload_snapshot, assessment_snapshot = _frozen_sources(payload, assessment_context)

    def invoke(
        purchase: PurchaseOperation,
        context: DecisionContext,
    ) -> CapabilityExecution:
        purchase_snapshot = purchase.model_copy(deep=True)
        context_snapshot = context.model_copy(deep=True)
        result = _produce_bound_price(
            payload_snapshot, assessment_snapshot,
            purchase_snapshot, context_snapshot,
        )
        return adapt_price(result)

    return invoke


__all__ = [
    "PriceInvoker", "PriceInvocationCapture", "ObservedPriceInvoker",
    "build_provenanced_price_invoker", "build_reference_observed_price_invoker",
]
