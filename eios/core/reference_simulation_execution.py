"""Causal execution facade for EIOS reference operational simulations.

A reference operational simulation is a product-validation scenario built from
synthetic material. This facade validates the exact CaseProvenance, synthetic
QTG receipt/consumption, bundle, PurchaseOperation and DecisionContext before
delegating exactly once to the closed MVP execution service.

It never converts synthetic material into PRESENTED_OPERATIONAL, never calls
the operational admission path, and never grants operational or decision
authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json

from .case_provenance import (
    CaseProvenance,
    classify_reference_operational_simulation,
)
from .execution_boundary import ExecutionOutcome
from .models import DecisionContext, PurchaseOperation
from .mvp_execution import CapabilityInvoker, run_mvp_execution
from .projection_quality_consumer import (
    ProjectionQualityConsumption,
    validate_projection_quality_consumption,
)
from .projection_quality_producer import (
    ProjectionQualityReceipt,
    validate_projection_quality_receipt,
)
from .projection_synthetic_adapter import ProjectionOnlySyntheticMaterialBundle


SCHEMA_VERSION = "EIOS-REFERENCE-SIMULATION-EXECUTION-01/v0.1"


def _canonical(value: object) -> bytes:
    if hasattr(value, "model_dump"):
        value = value.model_dump(mode="json")
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _fingerprint(value: object) -> str:
    return sha256(_canonical(value)).hexdigest()


def _policy(value: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise ValueError("policy_version must be an explicit nonempty identifier")
    if len(value) > 64:
        raise ValueError("policy_version exceeds MVP contract length")
    return value


def _extract_runtime(
    bundle: ProjectionOnlySyntheticMaterialBundle,
) -> tuple[PurchaseOperation, DecisionContext]:
    payload = bundle.envelope.to_payload()
    try:
        dip = payload["preparation"]["payload"]["capture"]["finance_package"][
            "decision_input_package"
        ]
        purchase = PurchaseOperation.model_validate(dip["purchase"])
        context = DecisionContext.model_validate(dip["context"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(
            "Reference bundle does not contain a valid bound DIP runtime"
        ) from exc
    return purchase, context


def _validate_reference_provenance(
    *,
    provenance: CaseProvenance,
    bundle: ProjectionOnlySyntheticMaterialBundle,
) -> dict:
    if not isinstance(provenance, CaseProvenance):
        raise TypeError("Expected CaseProvenance")
    if not isinstance(bundle, ProjectionOnlySyntheticMaterialBundle):
        raise TypeError("Expected ProjectionOnlySyntheticMaterialBundle")

    payload = provenance.to_payload()
    if payload.get("case_kind") != "REFERENCE_OPERATIONAL_SIMULATION":
        raise ValueError("Reference execution requires REFERENCE_OPERATIONAL_SIMULATION")
    reference_case_id = payload.get("reference_case_id")
    if not isinstance(reference_case_id, str) or not reference_case_id:
        raise ValueError("Reference provenance lacks reference_case_id")

    recomputed = classify_reference_operational_simulation(
        bundle=bundle,
        reference_case_id=reference_case_id,
    )
    if provenance.to_payload() != recomputed.to_payload() \
            or provenance.fingerprint != recomputed.fingerprint:
        raise ValueError("Reference CaseProvenance is not reproducible from exact bundle")

    expected = {
        "material_nature": "SYNTHETIC",
        "qtg_mode_policy": "SYNTHETIC_TEST_ONLY",
        "operational_path": "FORBIDDEN",
        "effect_scope": "NO_OPERATIONAL_EFFECT",
        "validation_scope": "PRODUCT_REFERENCE_E2E",
        "requires_operational_preflight": False,
        "decision_authority": False,
    }
    mismatches = tuple(
        field for field, value in expected.items()
        if payload.get(field) != value
    )
    if mismatches:
        raise ValueError(
            "Reference provenance violates nonoperational invariants: "
            + ", ".join(mismatches)
        )
    return payload


@dataclass(frozen=True, init=False)
class ReferenceSimulationExecution:
    """Immutable terminal artifact for one product reference execution."""

    _material: bytes

    def __init__(self) -> None:
        raise TypeError("Use run_reference_operational_simulation")

    def to_payload(self) -> dict:
        return json.loads(self._material)

    @property
    def fingerprint(self) -> str:
        return sha256(self._material).hexdigest()


def run_reference_operational_simulation(
    *,
    provenance: CaseProvenance,
    bundle: ProjectionOnlySyntheticMaterialBundle,
    receipt: ProjectionQualityReceipt,
    consumption: ProjectionQualityConsumption,
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
) -> ReferenceSimulationExecution:
    """Validate synthetic provenance -> one MVP execution -> immutable closure."""
    provenance_payload = _validate_reference_provenance(
        provenance=provenance,
        bundle=bundle,
    )
    policy_version = _policy(policy_version)

    validate_projection_quality_receipt(
        receipt=receipt,
        envelope=bundle.envelope,
        execution_mode="SYNTHETIC_TEST",
    )
    validate_projection_quality_consumption(
        consumption=consumption,
        receipt=receipt,
        envelope=bundle.envelope,
        execution_mode="SYNTHETIC_TEST",
        consumption_scope="TEST_ONLY",
    )

    receipt_payload = receipt.to_payload()
    consumption_payload = consumption.to_payload()
    if receipt_payload.get("operational_effect") is not False:
        raise ValueError("Reference QTG receipt must have no operational effect")
    if consumption_payload.get("execution_mode") != "SYNTHETIC_TEST" \
            or consumption_payload.get("consumption_scope") != "TEST_ONLY" \
            or consumption_payload.get("operational_effect") is not False \
            or consumption_payload.get("decision_authority") is not False:
        raise ValueError("Reference QTG consumption violates synthetic invariants")
    if consumption_payload.get("receipt_fingerprint") != receipt.fingerprint:
        raise ValueError("Reference consumption/receipt fingerprint mismatch")
    if consumption_payload.get("envelope_fingerprint") != bundle.envelope.fingerprint:
        raise ValueError("Reference consumption/envelope fingerprint mismatch")

    bound_purchase, bound_context = _extract_runtime(bundle)
    if not isinstance(purchase, PurchaseOperation):
        raise TypeError("Expected PurchaseOperation")
    if not isinstance(context, DecisionContext):
        raise TypeError("Expected DecisionContext")
    runtime_purchase = purchase.model_copy(deep=True)
    runtime_context = context.model_copy(deep=True)
    if bound_purchase != runtime_purchase:
        raise ValueError("Runtime PurchaseOperation differs from reference bundle")
    if bound_context != runtime_context:
        raise ValueError("Runtime DecisionContext differs from reference bundle")
    if runtime_purchase.decision_id != runtime_context.decision_id \
            or runtime_purchase.scenario_id != runtime_context.scenario_id:
        raise ValueError("Runtime purchase/context identity mismatch")

    outcome = run_mvp_execution(
        purchase=runtime_purchase.model_copy(deep=True),
        context=runtime_context.model_copy(deep=True),
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

    purchase_payload = runtime_purchase.model_dump(mode="json")
    context_payload = runtime_context.model_dump(mode="json")
    outcome_payload = outcome.model_dump(mode="json")
    capability_sequence = (
        "QTG",
        *(item.capability for item in outcome.capability_results),
    )

    payload = {
        "schema_version": SCHEMA_VERSION,
        "execution_kind": "REFERENCE_OPERATIONAL_SIMULATION",
        "reference_case_id": provenance_payload["reference_case_id"],
        "runtime_scope": "PRODUCT_REFERENCE_VALIDATION_ONLY",
        "operational_effect": False,
        "decision_authority": False,
        "operational_path": "FORBIDDEN",
        "qtg_execution_mode": "SYNTHETIC_TEST",
        "qtg_consumption_scope": "TEST_ONLY",
        "policy_version": policy_version,
        "case_provenance": provenance_payload,
        "case_provenance_fingerprint": provenance.fingerprint,
        "dataset_fingerprint": bundle.dataset_fingerprint,
        "bundle_fingerprint": bundle.fingerprint,
        "envelope_fingerprint": bundle.envelope.fingerprint,
        "qtg_receipt_fingerprint": receipt.fingerprint,
        "qtg_consumption_fingerprint": consumption.fingerprint,
        "qtg_quality_result": consumption_payload["functional_quality_result"],
        "purchase": purchase_payload,
        "purchase_fingerprint": _fingerprint(purchase_payload),
        "context": context_payload,
        "context_fingerprint": _fingerprint(context_payload),
        "capability_sequence": list(capability_sequence),
        "execution_outcome": outcome_payload,
        "execution_outcome_fingerprint": _fingerprint(outcome_payload),
    }
    payload["terminal_fingerprint"] = _fingerprint(payload)

    result = object.__new__(ReferenceSimulationExecution)
    object.__setattr__(result, "_material", _canonical(payload))
    return result


__all__ = [
    "ReferenceSimulationExecution",
    "SCHEMA_VERSION",
    "run_reference_operational_simulation",
]
