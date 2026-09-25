"""Same-invocation synthetic Negotiation Intelligence observation."""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json

from eios.rules.negotiation_provenance import (
    NegotiationContentEvidence, ObservedC0BoundNIInvoker, _produce_c0_bound_ni,
)
from eios.rules.provenance import AssessmentTraceBinding

from .capability_adapters import adapt_ni
from .models import DecisionContext, Evidence, PurchaseOperation
from .negotiation_intelligence import NegotiationIntelligenceResult
from .orchestration import CapabilityExecution
from .reference_price_observation import _canonical
from .reference_simulation_execution import ReferenceSimulationExecution


_SCHEMA = "EIOS-REFERENCE-NI-OBSERVATION-01/v0.1"
_SCOPE = {
    "material_nature": "SYNTHETIC",
    "qtg_mode_policy": "SYNTHETIC_TEST_ONLY",
    "operational_path": "FORBIDDEN",
    "effect_scope": "NO_OPERATIONAL_EFFECT",
    "decision_authority": False,
}


def _digest(value: object) -> str:
    return sha256(_canonical(value)).hexdigest()


def validate_reference_ni_observation_payload(observation: dict,
                                              terminal: dict) -> None:
    if not isinstance(observation, dict) or not isinstance(terminal, dict):
        raise ValueError("NI observation and terminal must be objects")
    provenance = terminal.get("case_provenance")
    if not isinstance(provenance, dict) or provenance.get("case_kind") != \
            "REFERENCE_OPERATIONAL_SIMULATION" or any(
                provenance.get(key) != value for key, value in _SCOPE.items()
            ) or terminal.get("operational_path") != "FORBIDDEN" or \
            terminal.get("operational_effect") is not False or \
            terminal.get("decision_authority") is not False:
        raise ValueError("NI observation requires synthetic terminal")
    if observation.get("observation_fingerprint") != _digest({
        key: value for key, value in observation.items() if key != "observation_fingerprint"
    }):
        raise ValueError("NI observation fingerprint mismatch")
    expected = {
        "schema_version": _SCHEMA,
        "reference_case_id": terminal.get("reference_case_id"),
        "terminal_fingerprint": terminal.get("terminal_fingerprint"),
        "purchase_fingerprint": terminal.get("purchase_fingerprint"),
        "context_fingerprint": terminal.get("context_fingerprint"),
        "authority_origin": "DECLARED_SYNTHETIC_TEST_EVIDENCE",
        "c0_content_derivation_proven": False,
        "separate_c0_invocation_binding_proven": False,
        **_SCOPE,
    }
    if any(observation.get(key) != value for key, value in expected.items()):
        raise ValueError("NI observation identity or scope mismatch")
    source = observation.get("source")
    if not isinstance(source, dict) or observation.get("source_fingerprint") != _digest(source):
        raise ValueError("NI observation source fingerprint mismatch")
    purchase = PurchaseOperation.model_validate(source.get("purchase"))
    context = DecisionContext.model_validate(terminal["context"])
    if purchase.model_dump(mode="json") != terminal["purchase"]:
        raise ValueError("NI observation purchase differs from terminal")
    content = NegotiationContentEvidence.model_validate(source.get("content_evidence"))
    evidences = tuple(Evidence.model_validate(item) for item in source.get("evidences", []))
    bindings = tuple(AssessmentTraceBinding.model_validate(item)
                     for item in source.get("bindings", []))
    result = NegotiationIntelligenceResult.model_validate(observation.get("ni_result"))
    capability = CapabilityExecution.model_validate(observation.get("ni_execution"))
    matches = [item for item in terminal["execution_outcome"]["capability_results"]
               if item.get("capability") == "NEGOTIATION_INTELLIGENCE"]
    if len(matches) != 1 or matches[0] != observation["ni_execution"] or \
            capability.capability != "NEGOTIATION_INTELLIGENCE" or \
            adapt_ni(result) != capability or \
            observation.get("trace_references") != list(result.traceability_references) or \
            observation.get("ni_result_fingerprint") != _digest(observation["ni_result"]):
        raise ValueError("NI observation execution differs from terminal")
    replayed = _produce_c0_bound_ni(
        purchase=purchase, context=context, content_evidence=content,
        evidences=evidences, bindings=bindings,
    )
    if replayed.model_dump(mode="json") != observation["ni_result"]:
        raise ValueError("NI observation differs from C0-bound replay")


@dataclass(frozen=True, init=False)
class ReferenceNIObservation:
    _material: bytes

    def __init__(self) -> None:
        raise TypeError("Use a reference execution with observed NI")

    def to_payload(self) -> dict:
        return json.loads(self._material)

    @property
    def fingerprint(self) -> str:
        return sha256(self._material).hexdigest()


def _close_reference_ni_observation(
    *, execution: ReferenceSimulationExecution,
    ni_invoker: ObservedC0BoundNIInvoker,
) -> ReferenceNIObservation:
    if not isinstance(execution, ReferenceSimulationExecution) or \
            not isinstance(ni_invoker, ObservedC0BoundNIInvoker):
        raise TypeError("Expected reference execution and observed NI invoker")
    terminal = execution.to_payload()
    if ni_invoker.reference_case_id != terminal["reference_case_id"]:
        raise ValueError("Observed NI case identity differs from terminal")
    capture = ni_invoker.capture()
    source = ni_invoker.source_payload()
    result = capture.result.model_dump(mode="json")
    body = {
        "schema_version": _SCHEMA,
        "reference_case_id": terminal["reference_case_id"],
        "terminal_fingerprint": terminal["terminal_fingerprint"],
        "purchase_fingerprint": terminal["purchase_fingerprint"],
        "context_fingerprint": terminal["context_fingerprint"],
        "authority_origin": "DECLARED_SYNTHETIC_TEST_EVIDENCE",
        "c0_content_derivation_proven": False,
        "separate_c0_invocation_binding_proven": False,
        **_SCOPE,
        "source": source,
        "source_fingerprint": _digest(source),
        "ni_result": result,
        "ni_result_fingerprint": _digest(result),
        "ni_execution": capture.capability.model_dump(mode="json"),
        "trace_references": list(capture.result.traceability_references),
    }
    body["observation_fingerprint"] = _digest(body)
    validate_reference_ni_observation_payload(body, terminal)
    observation = object.__new__(ReferenceNIObservation)
    object.__setattr__(observation, "_material", _canonical(body))
    return observation
