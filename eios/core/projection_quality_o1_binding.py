"""Causal binding between validated operational Projection Quality and O1.

QTG remains outside the O1 capability catalog. This module binds an already
validated operational QTG consumption to the exact PurchaseOperation,
DecisionContext and policy used by one synchronous run_mvp_execution call.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json

from .execution_boundary import ExecutionOutcome
from .models import DecisionContext, PurchaseOperation
from .mvp_execution import CapabilityInvoker, run_mvp_execution
from .orchestration import O1ExecutionContext
from .projection_material_envelope import ProjectionMaterialEnvelope
from .projection_quality_consumer import (
    ProjectionQualityConsumption,
    validate_projection_quality_consumption,
)
from .projection_quality_producer import ProjectionQualityReceipt


def _canonical(value) -> bytes:
    if hasattr(value, "model_dump"):
        value = value.model_dump(mode="json")
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _fingerprint(value) -> str:
    return sha256(_canonical(value)).hexdigest()


def _policy(value: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise ValueError("policy_version must be an explicit nonempty identifier")
    if len(value) > 64:
        raise ValueError("policy_version exceeds O1 contract length")
    return value


@dataclass(frozen=True, init=False)
class ProjectionQualityO1InputBinding:
    _material: bytes

    def __init__(self):
        raise TypeError("Use build_projection_quality_o1_input_binding")

    def to_payload(self) -> dict:
        return json.loads(self._material)

    @property
    def fingerprint(self) -> str:
        return sha256(self._material).hexdigest()


@dataclass(frozen=True, init=False)
class ProjectionQualityO1BoundExecution:
    _material: bytes

    def __init__(self):
        raise TypeError("Use run_mvp_execution_with_projection_quality_binding")

    def to_payload(self) -> dict:
        return json.loads(self._material)

    @property
    def fingerprint(self) -> str:
        return sha256(self._material).hexdigest()


def _extract_bound_runtime(
    envelope: ProjectionMaterialEnvelope,
) -> tuple[PurchaseOperation, DecisionContext]:
    payload = envelope.to_payload()
    try:
        dip = payload["preparation"]["payload"]["capture"]["finance_package"][
            "decision_input_package"
        ]
        purchase = PurchaseOperation.model_validate(dip["purchase"])
        context = DecisionContext.model_validate(dip["context"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("Envelope does not contain a valid bound DIP runtime") from exc
    return purchase, context


def build_projection_quality_o1_input_binding(
    *,
    consumption: ProjectionQualityConsumption,
    receipt: ProjectionQualityReceipt,
    envelope: ProjectionMaterialEnvelope,
    purchase: PurchaseOperation,
    context: DecisionContext,
    policy_version: str,
) -> ProjectionQualityO1InputBinding:
    """Create BOUND_INPUT after exact operational provenance validation."""
    if not isinstance(purchase, PurchaseOperation):
        raise TypeError("Expected PurchaseOperation")
    if not isinstance(context, DecisionContext):
        raise TypeError("Expected DecisionContext")
    policy_version = _policy(policy_version)

    validate_projection_quality_consumption(
        consumption=consumption,
        receipt=receipt,
        envelope=envelope,
        execution_mode="OPERATIONAL",
        consumption_scope="OPERATIONAL",
    )
    consumption_payload = consumption.to_payload()
    if consumption_payload.get("execution_mode") != "OPERATIONAL" \
            or consumption_payload.get("consumption_scope") != "OPERATIONAL" \
            or consumption_payload.get("operational_effect") is not True:
        raise ValueError("Binding requires operational QTG consumption")
    if consumption_payload.get("receipt_fingerprint") != receipt.fingerprint:
        raise ValueError("Consumption/receipt fingerprint mismatch")
    if consumption_payload.get("envelope_fingerprint") != envelope.fingerprint:
        raise ValueError("Consumption/envelope fingerprint mismatch")

    bound_purchase, bound_context = _extract_bound_runtime(envelope)
    runtime_purchase = purchase.model_copy(deep=True)
    runtime_context = context.model_copy(deep=True)

    if bound_purchase != runtime_purchase:
        raise ValueError("Runtime PurchaseOperation differs from bound DIP purchase")
    if bound_context != runtime_context:
        raise ValueError("Runtime DecisionContext differs from bound DIP context")
    if runtime_purchase.decision_id != runtime_context.decision_id \
            or runtime_purchase.scenario_id != runtime_context.scenario_id:
        raise ValueError("Runtime purchase/context identity mismatch")

    purchase_payload = runtime_purchase.model_dump(mode="json")
    context_payload = runtime_context.model_dump(mode="json")
    o1_context = O1ExecutionContext.from_context(runtime_context)

    payload = dict(
        schema_version="QTG-O1-CAUSAL-BINDING-01/v0.1",
        binding_version="0.1",
        binding_status="BOUND_INPUT",
        profile="PROJECTION_ONLY",
        purchase=purchase_payload,
        purchase_fingerprint=_fingerprint(purchase_payload),
        context=context_payload,
        context_fingerprint=_fingerprint(context_payload),
        o1_execution_context=o1_context.model_dump(mode="json"),
        o1_execution_context_semantics=(
            "DERIVED_CONTEXT_IDENTITY_NOT_EXECUTION_OCCURRENCE_ID"
        ),
        policy_version=policy_version,
        envelope_fingerprint=envelope.fingerprint,
        receipt_fingerprint=receipt.fingerprint,
        consumption_fingerprint=consumption.fingerprint,
        consumption=consumption_payload,
        functional_quality_result=consumption_payload["functional_quality_result"],
        decision_authority=False,
    )
    result = object.__new__(ProjectionQualityO1InputBinding)
    object.__setattr__(result, "_material", _canonical(payload))
    return result


def run_mvp_execution_with_projection_quality_binding(
    *,
    consumption: ProjectionQualityConsumption,
    receipt: ProjectionQualityReceipt,
    envelope: ProjectionMaterialEnvelope,
    purchase: PurchaseOperation,
    context: DecisionContext,
    policy_version: str,
    price_invoker: CapabilityInvoker | None = None,
    tco_invoker: CapabilityInvoker | None = None,
    supplier_risk_value_invoker: CapabilityInvoker | None = None,
    rules_invoker: CapabilityInvoker | None = None,
    decision_twin_invoker: CapabilityInvoker | None = None,
    scenario_coordination_invoker: CapabilityInvoker | None = None,
    negotiation_intelligence_invoker: CapabilityInvoker | None = None,
    negotiation_ladder_invoker: CapabilityInvoker | None = None,
) -> ProjectionQualityO1BoundExecution:
    """Own validation -> one O1 execution -> terminal causal closure."""
    input_binding = build_projection_quality_o1_input_binding(
        consumption=consumption,
        receipt=receipt,
        envelope=envelope,
        purchase=purchase,
        context=context,
        policy_version=policy_version,
    )
    purchase_snapshot = purchase.model_copy(deep=True)
    context_snapshot = context.model_copy(deep=True)

    outcome = run_mvp_execution(
        purchase=purchase_snapshot,
        context=context_snapshot,
        policy_version=policy_version,
        price_invoker=price_invoker,
        tco_invoker=tco_invoker,
        supplier_risk_value_invoker=supplier_risk_value_invoker,
        rules_invoker=rules_invoker,
        decision_twin_invoker=decision_twin_invoker,
        scenario_coordination_invoker=scenario_coordination_invoker,
        negotiation_intelligence_invoker=negotiation_intelligence_invoker,
        negotiation_ladder_invoker=negotiation_ladder_invoker,
    )
    if not isinstance(outcome, ExecutionOutcome):
        raise TypeError("run_mvp_execution returned foreign outcome")
    outcome = ExecutionOutcome.model_validate(outcome.model_dump(mode="python"))
    if outcome.policy_version != policy_version:
        raise ValueError("ExecutionOutcome policy_version mismatch")

    input_payload = input_binding.to_payload()
    outcome_payload = outcome.model_dump(mode="json")
    payload = dict(
        schema_version="QTG-O1-CAUSAL-BOUND-EXECUTION-01/v0.1",
        binding_version="0.1",
        binding_status="BOUND_TERMINAL_OUTCOME",
        input_binding=input_payload,
        input_binding_fingerprint=input_binding.fingerprint,
        consumption=input_payload["consumption"],
        consumption_fingerprint=input_payload["consumption_fingerprint"],
        receipt_fingerprint=input_payload["receipt_fingerprint"],
        envelope_fingerprint=input_payload["envelope_fingerprint"],
        purchase=input_payload["purchase"],
        purchase_fingerprint=input_payload["purchase_fingerprint"],
        context=input_payload["context"],
        context_fingerprint=input_payload["context_fingerprint"],
        policy_version=policy_version,
        o1_execution_context=input_payload["o1_execution_context"],
        o1_execution_context_semantics=input_payload[
            "o1_execution_context_semantics"
        ],
        execution_outcome=outcome_payload,
        execution_outcome_fingerprint=_fingerprint(outcome_payload),
        functional_quality_result=input_payload["functional_quality_result"],
        decision_authority=False,
    )
    payload["terminal_fingerprint"] = _fingerprint(payload)
    result = object.__new__(ProjectionQualityO1BoundExecution)
    object.__setattr__(result, "_material", _canonical(payload))
    return result


__all__ = [
    "ProjectionQualityO1BoundExecution",
    "ProjectionQualityO1InputBinding",
    "build_projection_quality_o1_input_binding",
    "run_mvp_execution_with_projection_quality_binding",
]
