"""U1 application boundary.

This module adapts UI input to canonical EIOS contracts and exposes existing
backend results for presentation. It never invokes analytical capabilities or
creates decision authority.
"""
from __future__ import annotations

from typing import Any, Mapping

from eios.core.models import DecisionContext, PurchaseOperation
from eios.mvp import VerticalMVPSupportResult


FORBIDDEN_FIELDS = frozenset({"decision_version", "decision_fingerprint"})


class FrontendBoundaryError(ValueError):
    """Raised when UI input violates the U1 boundary."""


def build_purchase_operation(payload: Mapping[str, Any]) -> PurchaseOperation:
    """Build a canonical PurchaseOperation from authorized UI fields only."""
    forbidden = FORBIDDEN_FIELDS.intersection(payload.keys())
    if forbidden:
        raise FrontendBoundaryError(
            f"campos no autorizados: {', '.join(sorted(forbidden))}"
        )
    try:
        return PurchaseOperation.model_validate(dict(payload))
    except Exception as exc:
        raise FrontendBoundaryError("entrada de operación no válida") from exc


def build_decision_context(payload: Mapping[str, Any]) -> DecisionContext:
    """Build the canonical DecisionContext without introducing versioning."""
    forbidden = FORBIDDEN_FIELDS.intersection(payload.keys())
    if forbidden:
        raise FrontendBoundaryError(
            f"campos no autorizados: {', '.join(sorted(forbidden))}"
        )
    try:
        return DecisionContext.model_validate(dict(payload))
    except Exception as exc:
        raise FrontendBoundaryError("contexto de decisión no válido") from exc


def present_support_package(package: Any) -> Mapping[str, Any]:
    """Expose an existing O1 package without recalculating or mutating it."""
    if not hasattr(package, "model_dump"):
        raise FrontendBoundaryError("paquete O1 no válido")
    return package.model_dump(mode="json")


def present_vertical_mvp_result(result: VerticalMVPSupportResult) -> Mapping[str, Any]:
    """Expose Vertical MVP execution, Rules/CRC and scenario support for UI use."""
    if not isinstance(result, VerticalMVPSupportResult):
        raise FrontendBoundaryError("resultado Vertical MVP no válido")

    execution = result.execution
    payload: dict[str, Any] = {
        "execution": {
            "status": execution.status.value,
            "policy_version": execution.policy_version,
            "unresolved_items": list(execution.unresolved_items),
            "failure_reason": execution.failure_reason,
            "capabilities": [
                {
                    "capability": item.capability,
                    "status": item.status.value,
                    "result_available": item.result_available,
                    "trace_references": list(item.trace_references),
                    "unresolved_items": list(item.unresolved_items),
                }
                for item in execution.capability_results
            ],
        },
        "rules": None,
        "scenario_support": None,
    }

    if result.rules is not None:
        crc = result.rules.crc_result
        payload["rules"] = {
            "executed_rule_ids": list(result.rules.executed_rule_ids),
            "omitted_rule_ids": list(result.rules.omitted_rule_ids),
            "consolidated_result": crc.consolidated_result,
            "dominant_reason": crc.dominant_reason,
            "relevant_factors": list(crc.relevant_factors),
            "conflicts": list(crc.conflicts),
            "assessments": [
                {
                    "rule_id": item.rule_id,
                    "status": item.status,
                    "outcome": item.outcome,
                    "reason": item.reason,
                    "evidence_ids": list(item.evidence_ids),
                }
                for item in result.rules.assessments
            ],
            "trace_references": [trace.trace_id for trace in result.rules.traces],
        }

    if result.scenario_support is not None:
        payload["scenario_support"] = result.scenario_support.model_dump(mode="json")

    return payload
