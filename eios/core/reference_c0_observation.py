"""Same-invocation C0/CRC result of a synthetic reference execution."""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json

from eios.rules.provenance import (
    AssessmentTraceBinding, ObservedRulesC0Invoker,
    validate_assessment_trace_binding,
)
from eios.rules.runtime import RuleSetVerticalResult

from .models import DecisionContext, PurchaseOperation
from .orchestration import CapabilityExecution
from .reference_price_observation import _canonical
from .reference_simulation_execution import ReferenceSimulationExecution


_SCHEMA = "EIOS-REFERENCE-C0-OBSERVATION-01/v0.1"
_SCOPE = {
    "material_nature": "SYNTHETIC",
    "qtg_mode_policy": "SYNTHETIC_TEST_ONLY",
    "operational_path": "FORBIDDEN",
    "effect_scope": "NO_OPERATIONAL_EFFECT",
    "decision_authority": False,
}


def _digest(value: object) -> str:
    return sha256(_canonical(value)).hexdigest()


def validate_reference_c0_observation_payload(observation: dict,
                                              terminal: dict) -> None:
    if not isinstance(observation, dict) or not isinstance(terminal, dict):
        raise ValueError("C0 observation and terminal must be objects")
    provenance = terminal.get("case_provenance")
    if not isinstance(provenance, dict) or provenance.get("case_kind") != \
            "REFERENCE_OPERATIONAL_SIMULATION" or any(
                provenance.get(k) != v for k, v in _SCOPE.items()
            ) or terminal.get("operational_path") != "FORBIDDEN" or \
            terminal.get("operational_effect") is not False or \
            terminal.get("decision_authority") is not False:
        raise ValueError("C0 observation requires synthetic terminal")
    if observation.get("observation_fingerprint") != _digest({
        key: value for key, value in observation.items()
        if key != "observation_fingerprint"
    }):
        raise ValueError("C0 observation fingerprint mismatch")
    expected = {
        "schema_version": _SCHEMA,
        "reference_case_id": terminal.get("reference_case_id"),
        "terminal_fingerprint": terminal.get("terminal_fingerprint"),
        "purchase_fingerprint": terminal.get("purchase_fingerprint"),
        "context_fingerprint": terminal.get("context_fingerprint"),
        "qtg_status": terminal["qtg_quality_result"]["status"],
        "qtg_c0_derivation_proven": False,
        "crc_base_origin": "SUPPLIED_SYNTHETIC_BASE_RESULT",
        **_SCOPE,
    }
    if any(observation.get(key) != value for key, value in expected.items()):
        raise ValueError("C0 observation identity or synthetic scope mismatch")
    source = observation.get("source")
    if not isinstance(source, dict) or observation.get("source_fingerprint") != _digest(source):
        raise ValueError("C0 observation source fingerprint mismatch")
    bindings = tuple(AssessmentTraceBinding.model_validate(item)
                     for item in source.get("bindings", []))
    purchase = PurchaseOperation.model_validate(terminal["purchase"])
    context = DecisionContext.model_validate(terminal["context"])
    for binding in bindings:
        validate_assessment_trace_binding(
            purchase=purchase, context=context, binding=binding,
        )
    result = RuleSetVerticalResult.model_validate(observation.get("vertical_result"))
    capability = CapabilityExecution.model_validate(observation.get("c0_execution"))
    if len(bindings) != len(result.assessments) or \
            tuple(item.assessment for item in bindings) != result.assessments or \
            tuple(item.trace for item in bindings) != result.traces or \
            result.c0_capability != capability or capability.capability != "C0" or \
            tuple(capability.trace_references) != tuple(item.trace_id for item in result.traces):
        raise ValueError("C0 observation bindings or result mismatch")
    matches = [item for item in terminal["execution_outcome"]["capability_results"]
               if item.get("capability") == "C0"]
    if len(matches) != 1 or matches[0] != observation["c0_execution"]:
        raise ValueError("C0 observation execution differs from terminal")
    crc = result.crc_result
    if (crc.traceability.decision_id, crc.traceability.scenario_id,
        crc.traceability.rules_version) != (
        context.decision_id, context.scenario_id, context.rules_version,
    ) or tuple(crc.traceability.assessment_rule_ids) != tuple(
        item.rule_id for item in result.assessments
    ) or observation.get("base_result") != source.get("base_result") or \
            observation.get("crc_result") != crc.model_dump(mode="json"):
        raise ValueError("C0 observation CRC identity or base mismatch")
    if observation.get("vertical_result_fingerprint") != _digest(observation["vertical_result"]):
        raise ValueError("C0 observation result fingerprint mismatch")


@dataclass(frozen=True, init=False)
class ReferenceC0Observation:
    _material: bytes

    def __init__(self) -> None:
        raise TypeError("Use a reference execution with observed C0")

    def to_payload(self) -> dict:
        return json.loads(self._material)

    @property
    def fingerprint(self) -> str:
        return sha256(self._material).hexdigest()


def _close_reference_c0_observation(*, execution: ReferenceSimulationExecution,
                                    c0_invoker: ObservedRulesC0Invoker) -> ReferenceC0Observation:
    if not isinstance(execution, ReferenceSimulationExecution):
        raise TypeError("Expected ReferenceSimulationExecution")
    if not isinstance(c0_invoker, ObservedRulesC0Invoker):
        raise TypeError("Expected ObservedRulesC0Invoker")
    terminal = execution.to_payload()
    if c0_invoker.reference_case_id != terminal["reference_case_id"]:
        raise ValueError("Observed C0 case identity differs from terminal")
    capture = c0_invoker.capture()
    source = c0_invoker.source_payload()
    result = capture.result.model_dump(mode="json")
    body = {
        "schema_version": _SCHEMA,
        "reference_case_id": terminal["reference_case_id"],
        "terminal_fingerprint": terminal["terminal_fingerprint"],
        "purchase_fingerprint": terminal["purchase_fingerprint"],
        "context_fingerprint": terminal["context_fingerprint"],
        "qtg_status": terminal["qtg_quality_result"]["status"],
        "qtg_c0_derivation_proven": False,
        "crc_base_origin": "SUPPLIED_SYNTHETIC_BASE_RESULT",
        **_SCOPE,
        "source": source,
        "source_fingerprint": _digest(source),
        "base_result": source["base_result"],
        "vertical_result": result,
        "vertical_result_fingerprint": _digest(result),
        "crc_result": result["crc_result"],
        "c0_execution": capture.capability.model_dump(mode="json"),
    }
    body["observation_fingerprint"] = _digest(body)
    validate_reference_c0_observation_payload(body, terminal)
    observation = object.__new__(ReferenceC0Observation)
    object.__setattr__(observation, "_material", _canonical(body))
    return observation


__all__ = ["ReferenceC0Observation", "validate_reference_c0_observation_payload"]
