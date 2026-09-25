"""Read-only PRICE observation for one completed synthetic reference execution."""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json

from .price_integration import ObservedPriceInvoker
from .orchestration import CapabilityExecution
from .reference_simulation_execution import ReferenceSimulationExecution
from eios.pricing.models import PriceIntelligenceResult


def _canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def validate_reference_price_observation_payload(
    observation: dict, terminal: dict,
) -> None:
    """Check a detached JSON sidecar against one validated reference terminal."""
    if not isinstance(observation, dict) or not isinstance(terminal, dict):
        raise ValueError("PRICE observation and terminal must be objects")
    digest = lambda value: sha256(_canonical(value)).hexdigest()
    provenance = terminal.get("case_provenance")
    if not isinstance(provenance, dict) or any(provenance.get(k) != v for k, v in {
        "case_kind": "REFERENCE_OPERATIONAL_SIMULATION",
        "material_nature": "SYNTHETIC",
        "qtg_mode_policy": "SYNTHETIC_TEST_ONLY",
        "operational_path": "FORBIDDEN",
        "effect_scope": "NO_OPERATIONAL_EFFECT",
        "decision_authority": False,
    }.items()) or terminal.get("operational_path") != "FORBIDDEN" \
            or terminal.get("operational_effect") is not False \
            or terminal.get("decision_authority") is not False:
        raise ValueError("PRICE observation requires synthetic reference terminal")
    if observation.get("observation_fingerprint") != digest({
        k: v for k, v in observation.items() if k != "observation_fingerprint"
    }):
        raise ValueError("PRICE observation fingerprint mismatch")
    expected = {
        "schema_version": "EIOS-REFERENCE-PRICE-OBSERVATION-01/v0.1",
        "reference_case_id": terminal.get("reference_case_id"),
        "terminal_fingerprint": terminal.get("terminal_fingerprint"),
        "purchase_fingerprint": terminal.get("purchase_fingerprint"),
        "context_fingerprint": terminal.get("context_fingerprint"),
        "material_nature": "SYNTHETIC",
        "qtg_mode_policy": "SYNTHETIC_TEST_ONLY",
        "operational_path": "FORBIDDEN",
        "effect_scope": "NO_OPERATIONAL_EFFECT",
        "decision_authority": False,
    }
    if any(observation.get(k) != v for k, v in expected.items()):
        raise ValueError("PRICE observation identity or synthetic scope mismatch")
    result = PriceIntelligenceResult.model_validate(observation.get("price_result"))
    capability = CapabilityExecution.model_validate(observation.get("price_execution"))
    if capability.capability != "PRICE":
        raise ValueError("PRICE observation contains another capability")
    matches = [item for item in terminal["execution_outcome"]["capability_results"]
               if item.get("capability") == "PRICE"]
    if len(matches) != 1 or matches[0] != observation["price_execution"]:
        raise ValueError("PRICE observation execution differs from terminal")
    if (result.decision_id, result.scenario_id, result.data_snapshot_id) != (
        terminal["context"]["decision_id"], terminal["context"]["scenario_id"],
        terminal["context"]["data_snapshot_id"],
    ) or tuple(result.trace_references) != tuple(capability.trace_references):
        raise ValueError("PRICE observation result differs from terminal identity")
    if observation.get("price_result_fingerprint") != digest(observation["price_result"]):
        raise ValueError("PRICE result fingerprint mismatch")


@dataclass(frozen=True, init=False)
class ReferencePriceObservation:
    _material: bytes

    def __init__(self) -> None:
        raise TypeError("Use a reference execution with observed PRICE")

    def to_payload(self) -> dict:
        return json.loads(self._material)

    @property
    def fingerprint(self) -> str:
        return sha256(self._material).hexdigest()


def _close_reference_price_observation(
    *, execution: ReferenceSimulationExecution,
    price_invoker: ObservedPriceInvoker,
) -> ReferencePriceObservation:
    """Bind a same-call capture to the exact terminal's PRICE state."""
    if not isinstance(execution, ReferenceSimulationExecution):
        raise TypeError("Expected ReferenceSimulationExecution")
    if not isinstance(price_invoker, ObservedPriceInvoker):
        raise TypeError("Expected ObservedPriceInvoker")
    terminal = execution.to_payload()
    if price_invoker.reference_case_id != terminal["reference_case_id"]:
        raise ValueError("Observed PRICE case identity differs from terminal")
    provenance = terminal["case_provenance"]
    expected = {
        "case_kind": "REFERENCE_OPERATIONAL_SIMULATION",
        "material_nature": "SYNTHETIC",
        "qtg_mode_policy": "SYNTHETIC_TEST_ONLY",
        "operational_path": "FORBIDDEN",
        "effect_scope": "NO_OPERATIONAL_EFFECT",
        "decision_authority": False,
    }
    if any(provenance.get(k) != v for k, v in expected.items()) or (
        terminal["operational_path"] != "FORBIDDEN"
        or terminal["operational_effect"] is not False
        or terminal["decision_authority"] is not False
    ):
        raise ValueError("PRICE observation requires synthetic reference closure")
    matches = [item for item in terminal["execution_outcome"]["capability_results"]
               if item["capability"] == "PRICE"]
    if len(matches) != 1:
        raise ValueError("Terminal requires exactly one PRICE execution")
    capture = price_invoker.capture()
    capability = capture.capability.model_dump(mode="json")
    if matches[0] != capability:
        raise ValueError("Captured PRICE execution differs from terminal")
    result = capture.result.model_dump(mode="json")
    context = terminal["context"]
    if (result["decision_id"], result["scenario_id"], result["data_snapshot_id"]) != (
        context["decision_id"], context["scenario_id"], context["data_snapshot_id"],
    ) or result["trace_references"] != capability["trace_references"]:
        raise ValueError("Captured PRICE result identity or traces differ from terminal")
    body = {
        "schema_version": "EIOS-REFERENCE-PRICE-OBSERVATION-01/v0.1",
        "reference_case_id": terminal["reference_case_id"],
        "terminal_fingerprint": terminal["terminal_fingerprint"],
        "purchase_fingerprint": terminal["purchase_fingerprint"],
        "context_fingerprint": terminal["context_fingerprint"],
        "material_nature": "SYNTHETIC",
        "qtg_mode_policy": "SYNTHETIC_TEST_ONLY",
        "operational_path": "FORBIDDEN",
        "effect_scope": "NO_OPERATIONAL_EFFECT",
        "decision_authority": False,
        "price_result": result,
        "price_result_fingerprint": sha256(_canonical(result)).hexdigest(),
        "price_execution": capability,
    }
    body["observation_fingerprint"] = sha256(_canonical(body)).hexdigest()
    observation = object.__new__(ReferencePriceObservation)
    object.__setattr__(observation, "_material", _canonical(body))
    return observation


__all__ = [
    "ReferencePriceObservation", "validate_reference_price_observation_payload",
]
