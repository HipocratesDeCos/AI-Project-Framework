"""Provenance-safe TCO integration for the EIOS Vertical MVP."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from eios.tco.engine import calculate_tco
from eios.tco.models import TCOInput, TCOResult

from .capability_adapters import adapt_tco
from .models import DecisionContext, PurchaseOperation
from .observed_invocation import SingleUseObservedInvoker
from .orchestration import CapabilityExecution


TCOInvoker = Callable[[PurchaseOperation, DecisionContext], CapabilityExecution]


@dataclass(frozen=True)
class TCOInvocationCapture:
    result: TCOResult
    capability: CapabilityExecution


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


def _frozen_source(payload: TCOInput) -> TCOInput:
    if not isinstance(payload, TCOInput):
        raise TypeError("payload debe ser TCOInput")
    return payload.model_copy(deep=True)


def _produce_bound_tco(payload: TCOInput, purchase: PurchaseOperation,
                       context: DecisionContext) -> TCOResult:
    _validate_execution_identity(payload, purchase, context)
    return calculate_tco(payload.model_copy(deep=True))


class ObservedTCOInvoker(SingleUseObservedInvoker[TCOResult, TCOInvocationCapture]):
    """Capture the result from the exact TCO call admitted to O1."""

    def __init__(self, payload: TCOInput, reference_case_id: str) -> None:
        self._payload = _frozen_source(payload)
        super().__init__(
            label="TCO", reference_case_id=reference_case_id,
            producer=lambda purchase, context: _produce_bound_tco(
                self._payload, purchase, context,
            ),
            adapter=adapt_tco, capture_factory=TCOInvocationCapture,
        )

    def input_payload(self) -> TCOInput:
        return self._payload.model_copy(deep=True)


def build_reference_observed_tco_invoker(*, payload: TCOInput,
                                         reference_case_id: str) -> ObservedTCOInvoker:
    return ObservedTCOInvoker(payload, reference_case_id)


def build_provenanced_tco_invoker(*, payload: TCOInput) -> TCOInvoker:
    """Freeze complete TCO input and expose the Vertical capability contract."""

    payload_snapshot = _frozen_source(payload)

    def invoke(
        purchase: PurchaseOperation,
        context: DecisionContext,
    ) -> CapabilityExecution:
        purchase_snapshot = purchase.model_copy(deep=True)
        context_snapshot = context.model_copy(deep=True)
        result = _produce_bound_tco(payload_snapshot, purchase_snapshot, context_snapshot)
        return adapt_tco(result)

    return invoke


__all__ = ["TCOInvoker", "TCOInvocationCapture", "ObservedTCOInvoker",
           "build_provenanced_tco_invoker", "build_reference_observed_tco_invoker"]
