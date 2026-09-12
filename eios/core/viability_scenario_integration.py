"""Typed provenance bridge from Viability Frontier into scenario analytics.

The bridge consumes an already-produced ViabilityResult. It never executes
Viability Frontier or O3 and does not map viability semantics to O3 status.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any

from .o4_o2_o3_orchestration import AuthorizedScenarioAnalytics, O4O2O3Preparation
from .scenario_engine import ScenarioStatus
from .scenario_evaluation import ScenarioEvaluationStatus
from .viability_frontier import ViabilityResult


def _canonical_viability_payload(result: ViabilityResult) -> dict[str, Any]:
    """Return the exhaustive transport representation of a validated VF result."""
    return {
        "decision_id": result.decision_id,
        "scenario_id": result.scenario_id,
        "status": result.status.value,
        "assessment_ids": tuple(result.assessment_ids),
        "rule_ids": tuple(result.rule_ids),
        "trace_references": tuple(result.trace_references),
        "rules_version": result.rules_version,
        "parameters_version": result.parameters_version,
        "data_snapshot_id": result.data_snapshot_id,
        "limitation": result.limitation,
    }


def build_authorized_analytics_from_viability(
    *,
    preparation: O4O2O3Preparation,
    scenario_id: str,
    assessments: tuple[Any, ...],
    viability_result: ViabilityResult,
    status: ScenarioEvaluationStatus = ScenarioEvaluationStatus.COMPLETED,
    limitations: tuple[str, ...] = (),
    trace_references: tuple[str, ...] = (),
    failure_reason: str | None = None,
) -> AuthorizedScenarioAnalytics:
    """Bind one typed VF result to one VALID scenario from the preparation.

    Context identity is derived only from ``preparation``. A detached context is
    intentionally not accepted.
    """
    preparation_snapshot = preparation.model_copy(deep=True)
    assessments_snapshot = deepcopy(tuple(assessments))
    viability_snapshot = deepcopy(viability_result)
    limitations_snapshot = tuple(limitations)
    trace_snapshot = tuple(trace_references)

    if not isinstance(viability_snapshot, ViabilityResult):
        raise TypeError("viability_result debe ser un ViabilityResult")

    matches = tuple(
        scenario
        for scenario in preparation_snapshot.materialization.scenarios
        if scenario.scenario_id == scenario_id
    )
    if not matches:
        raise ValueError("scenario_id no pertenece a la preparación O4→O2")
    if len(matches) != 1:
        raise ValueError("scenario_id duplicado en la preparación O4→O2")

    scenario = matches[0]
    if scenario.status != ScenarioStatus.VALID:
        raise ValueError("VF→Scenario Analytics requiere un ScenarioVersion VALID")

    context = preparation_snapshot.context
    if viability_snapshot.decision_id != context.decision_id:
        raise ValueError("ViabilityResult.decision_id incoherente con la preparación")
    if viability_snapshot.scenario_id != scenario.scenario_id:
        raise ValueError("ViabilityResult.scenario_id incoherente con el escenario")

    version_bindings = (
        ("rules_version", viability_snapshot.rules_version, context.rules_version),
        (
            "parameters_version",
            viability_snapshot.parameters_version,
            context.parameters_version,
        ),
        (
            "data_snapshot_id",
            viability_snapshot.data_snapshot_id,
            context.data_snapshot_id,
        ),
    )
    for field, actual, expected in version_bindings:
        if actual is None:
            raise ValueError(f"ViabilityResult.{field} es obligatorio para esta integración")
        if actual != expected:
            raise ValueError(f"ViabilityResult.{field} incoherente con la preparación")

    payload = _canonical_viability_payload(viability_snapshot)

    return AuthorizedScenarioAnalytics(
        scenario_id=scenario.scenario_id,
        assessments=assessments_snapshot,
        viability_result=payload,
        limitations=limitations_snapshot,
        trace_references=trace_snapshot,
        status=status,
        failure_reason=failure_reason,
    )


__all__ = ["build_authorized_analytics_from_viability"]
