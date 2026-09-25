"""Synthetic supplier external assessment captured in the same O1 invocation."""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json

from eios.supplier.models import SupplierEvidenceResult
from eios.supplier.risk_value import (
    ObservedSupplierRiskValueInvoker, SupplierRiskValueResult,
    SupplierRiskDimensionAssessment, SupplierValueDimensionAssessment, _adapt_result,
)

from .models import PurchaseOperation
from .orchestration import CapabilityExecution
from .reference_price_observation import _canonical
from .reference_simulation_execution import ReferenceSimulationExecution


_SCOPE = {
    "material_nature": "SYNTHETIC",
    "qtg_mode_policy": "SYNTHETIC_TEST_ONLY",
    "operational_path": "FORBIDDEN",
    "effect_scope": "NO_OPERATIONAL_EFFECT",
    "decision_authority": False,
}
_SCHEMA = "EIOS-REFERENCE-SUPPLIER-RISK-OBSERVATION-01/v0.1"


def _digest(value: object) -> str:
    return sha256(_canonical(value)).hexdigest()


def validate_reference_supplier_risk_observation_payload(observation: dict,
                                                         terminal: dict) -> None:
    if not isinstance(observation, dict) or not isinstance(terminal, dict):
        raise ValueError("Supplier observation and terminal must be objects")
    provenance = terminal.get("case_provenance")
    if not isinstance(provenance, dict) or provenance.get("case_kind") != \
            "REFERENCE_OPERATIONAL_SIMULATION" or any(
                provenance.get(k) != v for k, v in _SCOPE.items()
            ) or terminal.get("operational_path") != "FORBIDDEN" or \
            terminal.get("operational_effect") is not False or \
            terminal.get("decision_authority") is not False:
        raise ValueError("Supplier observation requires synthetic terminal")
    if observation.get("observation_fingerprint") != _digest({
        k: v for k, v in observation.items() if k != "observation_fingerprint"
    }):
        raise ValueError("Supplier observation fingerprint mismatch")
    expected = {
        "schema_version": _SCHEMA,
        "reference_case_id": terminal.get("reference_case_id"),
        "terminal_fingerprint": terminal.get("terminal_fingerprint"),
        "purchase_fingerprint": terminal.get("purchase_fingerprint"),
        "context_fingerprint": terminal.get("context_fingerprint"),
        "assessment_origin": "DECLARED_SYNTHETIC_EXTERNAL_ASSESSMENT",
        **_SCOPE,
    }
    if any(observation.get(k) != v for k, v in expected.items()):
        raise ValueError("Supplier observation identity or scope mismatch")
    source = observation.get("source")
    if not isinstance(source, dict) or observation.get("source_fingerprint") != _digest(source):
        raise ValueError("Supplier observation source fingerprint mismatch")
    purchase = PurchaseOperation.model_validate(source.get("purchase"))
    supplier = SupplierEvidenceResult.model_validate(source.get("supplier_result"))
    result = SupplierRiskValueResult.model_validate(observation.get("supplier_result"))
    capability = CapabilityExecution.model_validate(observation.get("supplier_execution"))
    if purchase.model_dump(mode="json") != terminal["purchase"] or (
        supplier.identity.decision_id, supplier.identity.scenario_id,
        supplier.identity.data_snapshot_id, supplier.current_supplier_id,
    ) != (
        terminal["context"]["decision_id"], terminal["context"]["scenario_id"],
        terminal["context"]["data_snapshot_id"], terminal["purchase"]["supplier_id"],
    ) or (result.decision_id, result.scenario_id, result.article_id,
          result.current_supplier_id) != (
        terminal["context"]["decision_id"], terminal["context"]["scenario_id"],
        purchase.article_id, purchase.supplier_id,
    ):
        raise ValueError("Supplier observation source/result identity mismatch")
    matches = [item for item in terminal["execution_outcome"]["capability_results"]
               if item.get("capability") == "SUPPLIER_RISK_VALUE"]
    if len(matches) != 1 or matches[0] != observation["supplier_execution"] or \
            _adapt_result(result) != capability:
        raise ValueError("Supplier observation execution differs from terminal")
    if observation.get("supplier_result_fingerprint") != _digest(observation["supplier_result"]):
        raise ValueError("Supplier observation result fingerprint mismatch")
    inventory = {
        "candidates": len(supplier.candidates),
        "observations": len(supplier.observations),
        "historical_facts": len(supplier.historical_facts),
        "external_metrics": len(supplier.external_metrics),
        "signals": len(supplier.signals),
        "structural_comparisons": len(supplier.structural_comparisons),
    }
    if observation.get("source_inventory") != inventory or \
            observation.get("trace_references") != list(result.trace_refs) or \
            observation.get("value_comparison_available") is not bool(result.value_dimensions):
        raise ValueError("Supplier observation sources or traces mismatch")
    risks = tuple(sorted(
        (SupplierRiskDimensionAssessment.model_validate(x)
         for x in source.get("risk_assessments", [])),
        key=lambda x: (x.supplier_id, x.dimension, x.assessment_ref),
    ))
    values = tuple(sorted(
        (SupplierValueDimensionAssessment.model_validate(x)
         for x in source.get("value_assessments", [])),
        key=lambda x: (x.supplier_id, x.comparison_supplier_id or "", x.dimension,
                       x.assessment_ref),
    ))
    if result.risk_dimensions != risks:
        raise ValueError("Supplier observation risk declarations mismatch")
    if result.value_dimensions != values:
        raise ValueError("Supplier observation value declarations mismatch")
    if tuple(sorted({ref for item in (*risks, *values)
                     for ref in item.evidence_refs})) != result.evidence_refs or \
            tuple(sorted({ref for item in (*risks, *values)
                          for ref in item.trace_refs})) != result.trace_refs:
        raise ValueError("Supplier observation references mismatch")


@dataclass(frozen=True, init=False)
class ReferenceSupplierRiskObservation:
    _material: bytes

    def __init__(self) -> None:
        raise TypeError("Use a reference execution with observed supplier risk")

    def to_payload(self) -> dict:
        return json.loads(self._material)

    @property
    def fingerprint(self) -> str:
        return sha256(self._material).hexdigest()


def _close_reference_supplier_risk_observation(
    *, execution: ReferenceSimulationExecution,
    supplier_invoker: ObservedSupplierRiskValueInvoker,
) -> ReferenceSupplierRiskObservation:
    if not isinstance(execution, ReferenceSimulationExecution):
        raise TypeError("Expected ReferenceSimulationExecution")
    if not isinstance(supplier_invoker, ObservedSupplierRiskValueInvoker):
        raise TypeError("Expected ObservedSupplierRiskValueInvoker")
    terminal = execution.to_payload()
    if supplier_invoker.reference_case_id != terminal["reference_case_id"]:
        raise ValueError("Observed supplier case identity differs from terminal")
    capture = supplier_invoker.capture()
    source = supplier_invoker.source_payload()
    result = capture.result.model_dump(mode="json")
    supplier = source["supplier_result"]
    body = {
        "schema_version": _SCHEMA,
        "reference_case_id": terminal["reference_case_id"],
        "terminal_fingerprint": terminal["terminal_fingerprint"],
        "purchase_fingerprint": terminal["purchase_fingerprint"],
        "context_fingerprint": terminal["context_fingerprint"],
        "assessment_origin": "DECLARED_SYNTHETIC_EXTERNAL_ASSESSMENT",
        **_SCOPE,
        "source": source,
        "source_fingerprint": _digest(source),
        "source_inventory": {key: len(supplier[key]) for key in (
            "candidates", "observations", "historical_facts", "external_metrics",
            "signals", "structural_comparisons",
        )},
        "supplier_result": result,
        "supplier_result_fingerprint": _digest(result),
        "supplier_execution": capture.capability.model_dump(mode="json"),
        "trace_references": result["trace_refs"],
        "value_comparison_available": bool(result["value_dimensions"]),
    }
    body["observation_fingerprint"] = _digest(body)
    validate_reference_supplier_risk_observation_payload(body, terminal)
    observation = object.__new__(ReferenceSupplierRiskObservation)
    object.__setattr__(observation, "_material", _canonical(body))
    return observation


__all__ = ["ReferenceSupplierRiskObservation",
           "validate_reference_supplier_risk_observation_payload"]
