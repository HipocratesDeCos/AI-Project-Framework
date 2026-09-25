"""Same-invocation synthetic Negotiation Ladder observation."""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json

from eios.rules.negotiation_provenance import (
    NegotiationContentEvidence, ObservedC0BoundLadderInvoker,
    _produce_c0_bound_ladder, _produce_c0_bound_ni,
)
from eios.rules.provenance import AssessmentTraceBinding

from .capability_adapters import adapt_nl
from .models import DecisionContext, Evidence, PurchaseOperation
from .negotiation_ladder import NegotiationLadderResult
from .orchestration import CapabilityExecution
from .reference_price_observation import _canonical
from .reference_simulation_execution import ReferenceSimulationExecution


_SCHEMA = "EIOS-REFERENCE-LADDER-OBSERVATION-01/v0.1"
_SCOPE = {
    "material_nature": "SYNTHETIC",
    "qtg_mode_policy": "SYNTHETIC_TEST_ONLY",
    "operational_path": "FORBIDDEN",
    "effect_scope": "NO_OPERATIONAL_EFFECT",
    "decision_authority": False,
}


def _digest(value: object) -> str:
    return sha256(_canonical(value)).hexdigest()


def validate_reference_ladder_observation_payload(observation: dict,
                                                  terminal: dict) -> None:
    if not isinstance(observation, dict) or not isinstance(terminal, dict):
        raise ValueError("Ladder observation and terminal must be objects")
    provenance = terminal.get("case_provenance")
    if not isinstance(provenance, dict) or provenance.get("case_kind") != \
            "REFERENCE_OPERATIONAL_SIMULATION" or any(
                provenance.get(key) != value for key, value in _SCOPE.items()
            ) or terminal.get("operational_path") != "FORBIDDEN" or \
            terminal.get("operational_effect") is not False or \
            terminal.get("decision_authority") is not False:
        raise ValueError("Ladder observation requires synthetic terminal")
    if observation.get("observation_fingerprint") != _digest({
        key: value for key, value in observation.items() if key != "observation_fingerprint"
    }):
        raise ValueError("Ladder observation fingerprint mismatch")
    expected = {
        "schema_version": _SCHEMA,
        "reference_case_id": terminal.get("reference_case_id"),
        "terminal_fingerprint": terminal.get("terminal_fingerprint"),
        "purchase_fingerprint": terminal.get("purchase_fingerprint"),
        "context_fingerprint": terminal.get("context_fingerprint"),
        "structure_scope": "SYNTHETIC_CONTENT_REPRESENTATION_ONLY",
        "authority_origin": "DECLARED_SYNTHETIC_TEST_EVIDENCE",
        "separate_ni_invocation_binding_proven": False,
        "c0_content_derivation_proven": False,
        **_SCOPE,
    }
    if any(observation.get(key) != value for key, value in expected.items()):
        raise ValueError("Ladder observation identity or scope mismatch")
    source = observation.get("source")
    if not isinstance(source, dict) or observation.get("source_fingerprint") != _digest(source):
        raise ValueError("Ladder observation source fingerprint mismatch")
    purchase = PurchaseOperation.model_validate(source.get("purchase"))
    context = DecisionContext.model_validate(terminal["context"])
    if purchase.model_dump(mode="json") != terminal["purchase"]:
        raise ValueError("Ladder observation purchase differs from terminal")
    content = NegotiationContentEvidence.model_validate(source.get("content_evidence"))
    evidences = tuple(Evidence.model_validate(item) for item in source.get("evidences", []))
    bindings = tuple(AssessmentTraceBinding.model_validate(item)
                     for item in source.get("bindings", []))
    result = NegotiationLadderResult.model_validate(observation.get("ladder_result"))
    capability = CapabilityExecution.model_validate(observation.get("ladder_execution"))
    matches = [item for item in terminal["execution_outcome"]["capability_results"]
               if item.get("capability") == "NEGOTIATION_LADDER"]
    if len(matches) != 1 or matches[0] != observation["ladder_execution"] or \
            capability.capability != "NEGOTIATION_LADDER" or \
            adapt_nl(result) != capability or \
            observation.get("trace_references") != list(result.traceability_references) or \
            observation.get("ladder_result_fingerprint") != _digest(observation["ladder_result"]):
        raise ValueError("Ladder observation execution differs from terminal")
    ni = _produce_c0_bound_ni(
        purchase=purchase, context=context, content_evidence=content,
        evidences=evidences, bindings=bindings,
    )
    replayed = _produce_c0_bound_ladder(
        purchase=purchase, context=context, content_evidence=content,
        evidences=evidences, bindings=bindings,
    )
    if replayed.model_dump(mode="json") != observation["ladder_result"] or \
            result.context_references.negotiation_result_id != ni.negotiation_result_id:
        raise ValueError("Ladder observation differs from C0-bound NI replay")


@dataclass(frozen=True, init=False)
class ReferenceLadderObservation:
    _material: bytes

    def __init__(self) -> None:
        raise TypeError("Use a reference execution with observed Ladder")

    def to_payload(self) -> dict:
        return json.loads(self._material)

    @property
    def fingerprint(self) -> str:
        return sha256(self._material).hexdigest()


def _close_reference_ladder_observation(
    *, execution: ReferenceSimulationExecution,
    ladder_invoker: ObservedC0BoundLadderInvoker,
) -> ReferenceLadderObservation:
    if not isinstance(execution, ReferenceSimulationExecution) or \
            not isinstance(ladder_invoker, ObservedC0BoundLadderInvoker):
        raise TypeError("Expected reference execution and observed Ladder invoker")
    terminal = execution.to_payload()
    if ladder_invoker.reference_case_id != terminal["reference_case_id"]:
        raise ValueError("Observed Ladder case identity differs from terminal")
    capture = ladder_invoker.capture()
    source = ladder_invoker.source_payload()
    result = capture.result.model_dump(mode="json")
    body = {
        "schema_version": _SCHEMA,
        "reference_case_id": terminal["reference_case_id"],
        "terminal_fingerprint": terminal["terminal_fingerprint"],
        "purchase_fingerprint": terminal["purchase_fingerprint"],
        "context_fingerprint": terminal["context_fingerprint"],
        "structure_scope": "SYNTHETIC_CONTENT_REPRESENTATION_ONLY",
        "authority_origin": "DECLARED_SYNTHETIC_TEST_EVIDENCE",
        "separate_ni_invocation_binding_proven": False,
        "c0_content_derivation_proven": False,
        **_SCOPE,
        "source": source,
        "source_fingerprint": _digest(source),
        "ladder_result": result,
        "ladder_result_fingerprint": _digest(result),
        "ladder_execution": capture.capability.model_dump(mode="json"),
        "trace_references": list(capture.result.traceability_references),
    }
    body["observation_fingerprint"] = _digest(body)
    validate_reference_ladder_observation_payload(body, terminal)
    observation = object.__new__(ReferenceLadderObservation)
    object.__setattr__(observation, "_material", _canonical(body))
    return observation
