"""Read-only same-call structural Decision Twin comparison for reference EIOS."""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json

from eios.rules.decision_twin_integration import (
    ObservedDecisionTwinInvoker, ProvenancedDecisionTwinAlternativeInput,
)

from .capability_adapters import adapt_twin
from .decision_twin import DecisionTwinComparison
from .models import DecisionContext, PurchaseOperation
from .o4_o2_o3_orchestration import O4O2O3Preparation
from .orchestration import CapabilityExecution
from .reference_price_observation import _canonical
from .reference_simulation_execution import ReferenceSimulationExecution


_SCHEMA = "EIOS-REFERENCE-DECISION-TWIN-OBSERVATION-01/v0.1"
_SCOPE = {
    "material_nature": "SYNTHETIC",
    "qtg_mode_policy": "SYNTHETIC_TEST_ONLY",
    "operational_path": "FORBIDDEN",
    "effect_scope": "NO_OPERATIONAL_EFFECT",
    "decision_authority": False,
}


def _digest(value: object) -> str:
    return sha256(_canonical(value)).hexdigest()


def validate_reference_decision_twin_observation_payload(observation: dict,
                                                         terminal: dict) -> None:
    if not isinstance(observation, dict) or not isinstance(terminal, dict):
        raise ValueError("Decision Twin observation and terminal must be objects")
    provenance = terminal.get("case_provenance")
    if not isinstance(provenance, dict) or provenance.get("case_kind") != \
            "REFERENCE_OPERATIONAL_SIMULATION" or any(
                provenance.get(key) != value for key, value in _SCOPE.items()
            ) or terminal.get("operational_path") != "FORBIDDEN" or \
            terminal.get("operational_effect") is not False or \
            terminal.get("decision_authority") is not False:
        raise ValueError("Decision Twin observation requires synthetic terminal")
    if observation.get("observation_fingerprint") != _digest({
        key: value for key, value in observation.items() if key != "observation_fingerprint"
    }):
        raise ValueError("Decision Twin observation fingerprint mismatch")
    expected = {
        "schema_version": _SCHEMA,
        "reference_case_id": terminal.get("reference_case_id"),
        "terminal_fingerprint": terminal.get("terminal_fingerprint"),
        "purchase_fingerprint": terminal.get("purchase_fingerprint"),
        "context_fingerprint": terminal.get("context_fingerprint"),
        "comparison_scope": "STRUCTURAL_DESCRIPTIVE_ONLY",
        "selected_alternative": None,
        **_SCOPE,
    }
    if any(observation.get(key) != value for key, value in expected.items()):
        raise ValueError("Decision Twin observation identity or scope mismatch")
    source = observation.get("source")
    if not isinstance(source, dict) or observation.get("source_fingerprint") != _digest(source):
        raise ValueError("Decision Twin observation source fingerprint mismatch")
    purchase = PurchaseOperation.model_validate(source.get("purchase"))
    preparation = O4O2O3Preparation.model_validate(source.get("preparation"))
    alternatives = tuple(ProvenancedDecisionTwinAlternativeInput.model_validate(item)
                         for item in source.get("alternatives", []))
    context = DecisionContext.model_validate(terminal["context"])
    if purchase.model_dump(mode="json") != terminal["purchase"] or \
            preparation.context != context or len(alternatives) < 2:
        raise ValueError("Decision Twin observation root source mismatch")
    refs = tuple(item.representation_ref for item in alternatives)
    scenario_ids = tuple(item.scenario_input.scenario_id for item in alternatives)
    if len(set(refs)) != len(refs) or len(set(scenario_ids)) != len(scenario_ids):
        raise ValueError("Decision Twin observation alternative identities mismatch")
    comparison = DecisionTwinComparison.model_validate(observation.get("comparison"))
    capability = CapabilityExecution.model_validate(observation.get("twin_execution"))
    matches = [item for item in terminal["execution_outcome"]["capability_results"]
               if item.get("capability") == "DECISION_TWIN"]
    if len(matches) != 1 or matches[0] != observation["twin_execution"] or \
            capability.capability != "DECISION_TWIN" or adapt_twin(comparison) != capability:
        raise ValueError("Decision Twin observation execution differs from terminal")
    if comparison.alternatives != tuple(sorted(refs)) or \
            observation.get("alternative_refs") != list(comparison.alternatives) or \
            observation.get("trace_references") != list(comparison.trace_refs) or \
            observation.get("differences") != list(comparison.differences) or \
            observation.get("missing_attributes") != list(comparison.missing_attributes):
        raise ValueError("Decision Twin observation comparison or traces mismatch")
    if observation.get("comparison_fingerprint") != _digest(observation["comparison"]):
        raise ValueError("Decision Twin comparison fingerprint mismatch")


@dataclass(frozen=True, init=False)
class ReferenceDecisionTwinObservation:
    _material: bytes

    def __init__(self) -> None:
        raise TypeError("Use a reference execution with observed Decision Twin")

    def to_payload(self) -> dict:
        return json.loads(self._material)

    @property
    def fingerprint(self) -> str:
        return sha256(self._material).hexdigest()


def _close_reference_decision_twin_observation(
    *, execution: ReferenceSimulationExecution,
    twin_invoker: ObservedDecisionTwinInvoker,
) -> ReferenceDecisionTwinObservation:
    if not isinstance(execution, ReferenceSimulationExecution):
        raise TypeError("Expected ReferenceSimulationExecution")
    if not isinstance(twin_invoker, ObservedDecisionTwinInvoker):
        raise TypeError("Expected ObservedDecisionTwinInvoker")
    terminal = execution.to_payload()
    if twin_invoker.reference_case_id != terminal["reference_case_id"]:
        raise ValueError("Observed Decision Twin case identity differs from terminal")
    capture = twin_invoker.capture()
    source = twin_invoker.source_payload()
    comparison = capture.result.model_dump(mode="json")
    body = {
        "schema_version": _SCHEMA,
        "reference_case_id": terminal["reference_case_id"],
        "terminal_fingerprint": terminal["terminal_fingerprint"],
        "purchase_fingerprint": terminal["purchase_fingerprint"],
        "context_fingerprint": terminal["context_fingerprint"],
        "comparison_scope": "STRUCTURAL_DESCRIPTIVE_ONLY",
        "selected_alternative": None,
        **_SCOPE,
        "source": source,
        "source_fingerprint": _digest(source),
        "comparison": comparison,
        "comparison_fingerprint": _digest(comparison),
        "twin_execution": capture.capability.model_dump(mode="json"),
        "alternative_refs": comparison["alternatives"],
        "trace_references": comparison["trace_refs"],
        "differences": comparison["differences"],
        "missing_attributes": comparison["missing_attributes"],
    }
    body["observation_fingerprint"] = _digest(body)
    validate_reference_decision_twin_observation_payload(body, terminal)
    observation = object.__new__(ReferenceDecisionTwinObservation)
    object.__setattr__(observation, "_material", _canonical(body))
    return observation


__all__ = ["ReferenceDecisionTwinObservation",
           "validate_reference_decision_twin_observation_payload"]
