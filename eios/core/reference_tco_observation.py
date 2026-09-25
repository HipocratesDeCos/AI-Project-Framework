"""Read-only TCO observation bound to one synthetic reference execution."""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json

from eios.tco.models import TCOInput, TCOResult

from .orchestration import CapabilityExecution
from .reference_price_observation import _canonical
from .reference_simulation_execution import ReferenceSimulationExecution
from .tco_integration import ObservedTCOInvoker


_SCOPE = {
    "material_nature": "SYNTHETIC",
    "qtg_mode_policy": "SYNTHETIC_TEST_ONLY",
    "operational_path": "FORBIDDEN",
    "effect_scope": "NO_OPERATIONAL_EFFECT",
    "decision_authority": False,
}


def _digest(value: object) -> str:
    return sha256(_canonical(value)).hexdigest()


def validate_reference_tco_observation_payload(observation: dict,
                                               terminal: dict) -> None:
    """Validate a detached sidecar against its exact synthetic terminal."""
    if not isinstance(observation, dict) or not isinstance(terminal, dict):
        raise ValueError("TCO observation and terminal must be objects")
    provenance = terminal.get("case_provenance")
    if not isinstance(provenance, dict) or provenance.get("case_kind") != \
            "REFERENCE_OPERATIONAL_SIMULATION" or any(
                provenance.get(k) != v for k, v in _SCOPE.items()
            ) or terminal.get("operational_path") != "FORBIDDEN" or \
            terminal.get("operational_effect") is not False or \
            terminal.get("decision_authority") is not False:
        raise ValueError("TCO observation requires synthetic reference terminal")
    if observation.get("observation_fingerprint") != _digest({
        k: v for k, v in observation.items() if k != "observation_fingerprint"
    }):
        raise ValueError("TCO observation fingerprint mismatch")
    expected = {
        "schema_version": "EIOS-REFERENCE-TCO-OBSERVATION-01/v0.1",
        "reference_case_id": terminal.get("reference_case_id"),
        "terminal_fingerprint": terminal.get("terminal_fingerprint"),
        "purchase_fingerprint": terminal.get("purchase_fingerprint"),
        "context_fingerprint": terminal.get("context_fingerprint"),
        **_SCOPE,
    }
    if any(observation.get(k) != v for k, v in expected.items()):
        raise ValueError("TCO observation identity or synthetic scope mismatch")
    source = TCOInput.model_validate(observation.get("tco_input"))
    result = TCOResult.model_validate(observation.get("tco_result"))
    capability = CapabilityExecution.model_validate(observation.get("tco_execution"))
    matches = [item for item in terminal["execution_outcome"]["capability_results"]
               if item.get("capability") == "TCO"]
    if capability.capability != "TCO" or len(matches) != 1 or \
            matches[0] != observation["tco_execution"]:
        raise ValueError("TCO observation execution differs from terminal")
    purchase, context = terminal["purchase"], terminal["context"]
    if source.purchase_operation.model_dump(mode="json") != purchase or \
            (result.decision_id, result.scenario_id, result.currency) != (
                context["decision_id"], context["scenario_id"], purchase["currency"]
            ) or observation.get("trace_references") != [] or \
            tuple(capability.trace_references) != ():
        raise ValueError("TCO observation input, result or traces differ from terminal")
    if observation.get("tco_input_fingerprint") != _digest(observation["tco_input"]) or \
            observation.get("tco_result_fingerprint") != _digest(observation["tco_result"]):
        raise ValueError("TCO input or result fingerprint mismatch")
    if observation.get("additional_attributable_costs_provided") is not (
        bool(source.attributable_costs)
    ) or observation.get("contributing_components") != list(result.contributing_components) \
            or observation.get("unresolved_components") != list(result.unresolved_components) \
            or observation.get("limitations") != list(result.limitations) \
            or observation.get("complete_for_supplied_components") is not result.complete:
        raise ValueError("TCO observation components or scope mismatch")
    from .capability_adapters import adapt_tco
    if adapt_tco(result) != capability:
        raise ValueError("TCO observation result does not explain execution")


@dataclass(frozen=True, init=False)
class ReferenceTCOObservation:
    _material: bytes

    def __init__(self) -> None:
        raise TypeError("Use a reference execution with observed TCO")

    def to_payload(self) -> dict:
        return json.loads(self._material)

    @property
    def fingerprint(self) -> str:
        return sha256(self._material).hexdigest()


def _close_reference_tco_observation(*, execution: ReferenceSimulationExecution,
                                     tco_invoker: ObservedTCOInvoker) -> ReferenceTCOObservation:
    if not isinstance(execution, ReferenceSimulationExecution):
        raise TypeError("Expected ReferenceSimulationExecution")
    if not isinstance(tco_invoker, ObservedTCOInvoker):
        raise TypeError("Expected ObservedTCOInvoker")
    terminal = execution.to_payload()
    if tco_invoker.reference_case_id != terminal["reference_case_id"]:
        raise ValueError("Observed TCO case identity differs from terminal")
    capture = tco_invoker.capture()
    source = tco_invoker.input_payload().model_dump(mode="json")
    result = capture.result.model_dump(mode="json")
    capability = capture.capability.model_dump(mode="json")
    body = {
        "schema_version": "EIOS-REFERENCE-TCO-OBSERVATION-01/v0.1",
        "reference_case_id": terminal["reference_case_id"],
        "terminal_fingerprint": terminal["terminal_fingerprint"],
        "purchase_fingerprint": terminal["purchase_fingerprint"],
        "context_fingerprint": terminal["context_fingerprint"],
        **_SCOPE,
        "tco_input": source,
        "tco_input_fingerprint": _digest(source),
        "additional_attributable_costs_provided": bool(source["attributable_costs"]),
        "tco_result": result,
        "tco_result_fingerprint": _digest(result),
        "tco_execution": capability,
        "contributing_components": result["contributing_components"],
        "unresolved_components": result["unresolved_components"],
        "limitations": result["limitations"],
        "complete_for_supplied_components": capture.result.complete,
        "trace_references": [],
    }
    body["observation_fingerprint"] = _digest(body)
    validate_reference_tco_observation_payload(body, terminal)
    observation = object.__new__(ReferenceTCOObservation)
    object.__setattr__(observation, "_material", _canonical(body))
    return observation


__all__ = ["ReferenceTCOObservation", "validate_reference_tco_observation_payload"]
