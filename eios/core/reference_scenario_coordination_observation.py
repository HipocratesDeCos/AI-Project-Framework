"""Same-call, synthetic O2 coordination observation for the reference case."""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json

from eios.rules.scenario_integration import (
    ObservedScenarioCoordinationInvoker, ProvenancedScenarioAnalyticsInput,
    _produce_provenanced_scenario_support,
)

from .models import DecisionContext, PurchaseOperation
from .o2 import O2SupportPackage
from .o4_o2_o3_orchestration import O4O2O3Preparation
from .orchestration import CapabilityExecution
from .scenario_coordination_adapter import adapt_scenario_coordination
from .reference_price_observation import _canonical
from .reference_simulation_execution import ReferenceSimulationExecution


_SCHEMA = "EIOS-REFERENCE-SCENARIO-COORDINATION-OBSERVATION-01/v0.1"
_SCOPE = {
    "material_nature": "SYNTHETIC",
    "qtg_mode_policy": "SYNTHETIC_TEST_ONLY",
    "operational_path": "FORBIDDEN",
    "effect_scope": "NO_OPERATIONAL_EFFECT",
    "decision_authority": False,
}


def _digest(value: object) -> str:
    return sha256(_canonical(value)).hexdigest()


def validate_reference_scenario_coordination_observation_payload(
    observation: dict, terminal: dict,
) -> None:
    if not isinstance(observation, dict) or not isinstance(terminal, dict):
        raise ValueError("Scenario observation and terminal must be objects")
    provenance = terminal.get("case_provenance")
    if not isinstance(provenance, dict) or provenance.get("case_kind") != \
            "REFERENCE_OPERATIONAL_SIMULATION" or any(
                provenance.get(key) != value for key, value in _SCOPE.items()
            ) or terminal.get("operational_path") != "FORBIDDEN" or \
            terminal.get("operational_effect") is not False or \
            terminal.get("decision_authority") is not False:
        raise ValueError("Scenario observation requires synthetic terminal")
    if observation.get("observation_fingerprint") != _digest({
        key: value for key, value in observation.items() if key != "observation_fingerprint"
    }):
        raise ValueError("Scenario observation fingerprint mismatch")
    expected = {
        "schema_version": _SCHEMA,
        "reference_case_id": terminal.get("reference_case_id"),
        "terminal_fingerprint": terminal.get("terminal_fingerprint"),
        "purchase_fingerprint": terminal.get("purchase_fingerprint"),
        "context_fingerprint": terminal.get("context_fingerprint"),
        "coordination_scope": "DESCRIPTIVE_SUPPORT_ONLY",
        "selected_scenario": None,
        **_SCOPE,
    }
    if any(observation.get(key) != value for key, value in expected.items()):
        raise ValueError("Scenario observation identity or scope mismatch")
    source = observation.get("source")
    if not isinstance(source, dict) or observation.get("source_fingerprint") != _digest(source):
        raise ValueError("Scenario observation source fingerprint mismatch")
    purchase = PurchaseOperation.model_validate(source.get("purchase"))
    preparation = O4O2O3Preparation.model_validate(source.get("preparation"))
    inputs = tuple(ProvenancedScenarioAnalyticsInput.model_validate(item)
                   for item in source.get("inputs", []))
    context = DecisionContext.model_validate(terminal["context"])
    if purchase.model_dump(mode="json") != terminal["purchase"] or \
            preparation.context != context or len(inputs) < 2:
        raise ValueError("Scenario observation root source mismatch")
    support = O2SupportPackage.model_validate(observation.get("support"))
    capability = CapabilityExecution.model_validate(observation.get("scenario_execution"))
    matches = [item for item in terminal["execution_outcome"]["capability_results"]
               if item.get("capability") == "SCENARIO_COORDINATION"]
    if len(matches) != 1 or matches[0] != observation["scenario_execution"] or \
            capability.capability != "SCENARIO_COORDINATION" or \
            adapt_scenario_coordination(support) != capability:
        raise ValueError("Scenario observation execution differs from terminal")
    if support.execution_context.decision_id != context.decision_id or \
            tuple(item.scenario_id for item in support.scenarios) != \
            tuple(observation.get("scenario_ids", [])) or \
            tuple(capability.trace_references) != tuple(observation.get("trace_references", [])) or \
            observation.get("support_fingerprint") != _digest(observation["support"]):
        raise ValueError("Scenario observation support binding mismatch")
    # Source replay prevents a rehashed but detached or invented O2 result.
    replayed = _produce_provenanced_scenario_support(
        purchase=purchase, context=context, preparation=preparation, inputs=inputs,
    )
    if replayed.model_dump(mode="json") != observation["support"]:
        raise ValueError("Scenario observation differs from provenanced replay")


@dataclass(frozen=True, init=False)
class ReferenceScenarioCoordinationObservation:
    _material: bytes

    def __init__(self) -> None:
        raise TypeError("Use a reference execution with observed Scenario Coordination")

    def to_payload(self) -> dict:
        return json.loads(self._material)

    @property
    def fingerprint(self) -> str:
        return sha256(self._material).hexdigest()


def _close_reference_scenario_coordination_observation(
    *, execution: ReferenceSimulationExecution,
    scenario_invoker: ObservedScenarioCoordinationInvoker,
) -> ReferenceScenarioCoordinationObservation:
    if not isinstance(execution, ReferenceSimulationExecution) or \
            not isinstance(scenario_invoker, ObservedScenarioCoordinationInvoker):
        raise TypeError("Expected reference execution and observed scenario invoker")
    terminal = execution.to_payload()
    if scenario_invoker.reference_case_id != terminal["reference_case_id"]:
        raise ValueError("Observed scenario case identity differs from terminal")
    capture = scenario_invoker.capture()
    source = scenario_invoker.source_payload()
    support = capture.result.model_dump(mode="json")
    body = {
        "schema_version": _SCHEMA,
        "reference_case_id": terminal["reference_case_id"],
        "terminal_fingerprint": terminal["terminal_fingerprint"],
        "purchase_fingerprint": terminal["purchase_fingerprint"],
        "context_fingerprint": terminal["context_fingerprint"],
        "coordination_scope": "DESCRIPTIVE_SUPPORT_ONLY",
        "selected_scenario": None,
        **_SCOPE,
        "source": source,
        "source_fingerprint": _digest(source),
        "support": support,
        "support_fingerprint": _digest(support),
        "scenario_execution": capture.capability.model_dump(mode="json"),
        "scenario_ids": [item["scenario_id"] for item in support["scenarios"]],
        "trace_references": list(capture.capability.trace_references),
    }
    body["observation_fingerprint"] = _digest(body)
    validate_reference_scenario_coordination_observation_payload(body, terminal)
    observation = object.__new__(ReferenceScenarioCoordinationObservation)
    object.__setattr__(observation, "_material", _canonical(body))
    return observation
