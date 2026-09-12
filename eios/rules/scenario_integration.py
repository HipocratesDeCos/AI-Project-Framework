"""Provenance-safe bridge from C0 Assessments into scenario analytics.

The bridge validates already-produced Assessment+Trace bindings against the
actual O2 child scenario and delegates the independently produced typed
ViabilityResult to the closed VF->Scenario Analytics boundary. It never
executes rules, Viability Frontier, O2 or O3.
"""
from __future__ import annotations

from collections.abc import Sequence
from copy import deepcopy
from typing import Any

from eios.core.models import Assessment, DecisionContext, PurchaseOperation
from eios.core.o4_o2_o3_orchestration import (
    AuthorizedScenarioAnalytics,
    O4O2O3Preparation,
)
from eios.core.scenario_engine import ScenarioStatus, ScenarioVersion
from eios.core.scenario_evaluation import ScenarioEvaluationStatus
from eios.core.viability_frontier import ViabilityResult
from eios.core.viability_scenario_integration import (
    build_authorized_analytics_from_viability,
)

from .provenance import AssessmentTraceBinding, validate_assessment_trace_binding


def _target_scenario_context(
    preparation: O4O2O3Preparation,
    scenario_id: str,
) -> tuple[ScenarioVersion, DecisionContext]:
    matches = tuple(
        scenario
        for scenario in preparation.materialization.scenarios
        if scenario.scenario_id == scenario_id
    )
    if not matches:
        raise ValueError("scenario_id no pertenece a la preparación O4→O2")
    if len(matches) != 1:
        raise ValueError("scenario_id duplicado en la preparación O4→O2")

    scenario = matches[0]
    if scenario.status != ScenarioStatus.VALID:
        raise ValueError("Assessment→Scenario Analytics requiere un ScenarioVersion VALID")

    base = preparation.context
    context = DecisionContext(
        decision_id=base.decision_id,
        scenario_id=scenario.scenario_id,
        rules_version=base.rules_version,
        parameters_version=base.parameters_version,
        data_snapshot_id=base.data_snapshot_id,
    )
    return scenario, context


def _canonical_assessment_payload(assessment: Assessment) -> dict[str, Any]:
    """Transport only the closed Assessment contract after typed validation."""
    return {
        "rule_id": assessment.rule_id,
        "status": assessment.status,
        "outcome": assessment.outcome,
        "evidence_ids": list(assessment.evidence_ids),
        "reason": assessment.reason,
    }


def build_authorized_scenario_analytics_from_provenanced_assessments(
    *,
    preparation: O4O2O3Preparation,
    scenario_id: str,
    purchase: PurchaseOperation,
    assessment_bindings: Sequence[AssessmentTraceBinding],
    viability_result: ViabilityResult,
    status: ScenarioEvaluationStatus = ScenarioEvaluationStatus.COMPLETED,
    limitations: tuple[str, ...] = (),
    failure_reason: str | None = None,
) -> AuthorizedScenarioAnalytics:
    """Build one analytical package from independently provenanced C0 and VF data.

    The supplied PurchaseOperation is used only to verify C0 Trace provenance for
    the target O2 child scenario. This function does not claim that it generically
    materializes every ``ScenarioVersion.changes`` entry.
    """
    preparation_snapshot = preparation.model_copy(deep=True)
    purchase_snapshot = purchase.model_copy(deep=True)
    binding_snapshots = tuple(
        binding.model_copy(deep=True) for binding in assessment_bindings
    )
    viability_snapshot = deepcopy(viability_result)
    limitations_snapshot = tuple(limitations)

    if not binding_snapshots:
        raise ValueError("Assessment→Scenario Analytics requiere bindings no vacíos")

    scenario, scenario_context = _target_scenario_context(
        preparation_snapshot,
        scenario_id,
    )

    if purchase_snapshot.decision_id != scenario_context.decision_id:
        raise ValueError("PurchaseOperation.decision_id incoherente con el escenario")
    if purchase_snapshot.scenario_id != scenario_context.scenario_id:
        raise ValueError("PurchaseOperation.scenario_id incoherente con el escenario")

    rule_ids = tuple(binding.assessment.rule_id for binding in binding_snapshots)
    if len(rule_ids) != len(set(rule_ids)):
        raise ValueError("No se permiten rule_id duplicados en Scenario Analytics")

    validated_bindings = tuple(
        validate_assessment_trace_binding(
            purchase=purchase_snapshot.model_copy(deep=True),
            context=scenario_context.model_copy(deep=True),
            binding=binding,
        )
        for binding in binding_snapshots
    )

    assessment_payloads = tuple(
        _canonical_assessment_payload(binding.assessment)
        for binding in validated_bindings
    )
    trace_references = tuple(binding.trace.trace_id for binding in validated_bindings)

    return build_authorized_analytics_from_viability(
        preparation=preparation_snapshot,
        scenario_id=scenario.scenario_id,
        assessments=deepcopy(assessment_payloads),
        viability_result=viability_snapshot,
        status=status,
        limitations=limitations_snapshot,
        trace_references=trace_references,
        failure_reason=failure_reason,
    )


__all__ = ["build_authorized_scenario_analytics_from_provenanced_assessments"]
