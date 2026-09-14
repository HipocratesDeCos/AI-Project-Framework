"""U1 application boundary.

This module adapts UI input to canonical EIOS contracts and exposes existing
backend results for presentation. It never invokes analytical capabilities or
creates decision authority.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Mapping

from eios.core.models import DecisionContext, PurchaseOperation
from eios.frontend.visual.configuration_center_workflow import (
    ConfigurationWorkflowSnapshot,
)
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


def present_configuration_center_snapshot(
    snapshot: ConfigurationWorkflowSnapshot,
) -> Mapping[str, Any]:
    """Serialize one Configuration Center workflow snapshot for presentation.

    This function verifies only the public snapshot type. It does not certify
    provenance, reconstruct authorization, or revalidate Slice 1–3 invariants.
    """
    if not isinstance(snapshot, ConfigurationWorkflowSnapshot):
        raise FrontendBoundaryError("snapshot de Configuration Center no válido")

    screen = snapshot.screen
    detail = screen.detail.detail if screen.detail is not None else None
    history = screen.history.items if screen.history is not None else None
    form = screen.form
    confirmation = screen.confirmation

    return {
        "data_ready": snapshot.data_ready,
        "history_stale": snapshot.history_stale,
        "status": {
            "state": screen.status.state,
            "error_code": screen.status.error_code,
        },
        "detail": _present_configuration_detail(detail) if detail is not None else None,
        "history": (
            [_present_configuration_history_item(item) for item in history]
            if history is not None
            else None
        ),
        "form": _present_configuration_form(form) if form is not None else None,
        "confirmation": (
            {
                "detail": _present_configuration_detail(confirmation.detail),
                "proposal": _present_change_proposal(confirmation.proposal),
            }
            if confirmation is not None
            else None
        ),
    }


def _present_configuration_detail(detail: Any) -> Mapping[str, Any]:
    return {
        "company_id": detail.company_id,
        "parameter_id": detail.parameter_id,
        "actor": detail.actor,
        "value_type": detail.value_type,
        "unit": detail.unit,
        "restricted": detail.restricted,
        "configuration": (
            _present_configuration(detail.configuration)
            if detail.configuration is not None
            else None
        ),
    }


def _present_configuration(configuration: Any) -> Mapping[str, Any]:
    return {
        "configuration_id": configuration.configuration_id,
        "parameter_id": configuration.parameter_id,
        "company_id": configuration.company_id,
        "value": configuration.value,
        "value_type": configuration.value_type,
        "unit": configuration.unit,
        "valid_from": _present_datetime(configuration.valid_from),
        "valid_to": _present_optional_datetime(configuration.valid_to),
        "created_at": _present_datetime(configuration.created_at),
        "updated_at": _present_datetime(configuration.updated_at),
    }


def _present_configuration_history_item(item: Any) -> Mapping[str, Any]:
    return {
        "configuration_id": item.configuration_id,
        "parameter_id": item.parameter_id,
        "company_id": item.company_id,
        "previous_value": item.previous_value,
        "new_value": item.new_value,
        "changed_by": item.changed_by,
        "changed_at": _present_datetime(item.changed_at),
        "change_reason": item.change_reason,
    }


def _present_configuration_form(form: Any) -> Mapping[str, Any]:
    return {
        "value": form.value,
        "valid_from": _present_datetime(form.valid_from),
        "valid_to": _present_optional_datetime(form.valid_to),
        "reason": form.reason,
    }


def _present_change_proposal(proposal: Any) -> Mapping[str, Any]:
    return {
        "value": proposal.value,
        "valid_from": _present_datetime(proposal.valid_from),
        "valid_to": _present_optional_datetime(proposal.valid_to),
        "reason": proposal.reason,
    }


def _present_datetime(value: datetime) -> str:
    return value.isoformat()


def _present_optional_datetime(value: datetime | None) -> str | None:
    return value.isoformat() if value is not None else None
