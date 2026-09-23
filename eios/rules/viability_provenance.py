"""Provenance-safe Viability Frontier producer for the authorized minimal MVP catalog."""
from __future__ import annotations

from copy import deepcopy
from collections.abc import Sequence

from eios.core.fingerprint import assessment_fingerprint
from eios.core.models import DecisionContext, PurchaseOperation
from eios.core.viability_frontier import (
    FrontierAssessment,
    FrontierClass,
    ViabilityResult,
    evaluate_viability,
)

from .provenance import AssessmentTraceBinding, validate_assessment_trace_binding


VF_MINIMAL_CATALOG: dict[str, FrontierClass] = {
    "R-FIN-001": FrontierClass.H,
    "R-PAG-002": FrontierClass.K,
    "R-DAT-003": FrontierClass.U,
}


def _frontier_from_binding(
    binding: AssessmentTraceBinding,
    *,
    purchase: PurchaseOperation,
    context: DecisionContext,
) -> FrontierAssessment | None:
    validated = validate_assessment_trace_binding(
        purchase=purchase,
        context=context,
        binding=binding,
    )
    assessment = validated.assessment
    trace = validated.trace
    frontier_class = VF_MINIMAL_CATALOG.get(assessment.rule_id)
    if frontier_class is None:
        return None

    if assessment.status == "EVALUABLE":
        if assessment.outcome not in {"TRUE", "FALSE"}:
            raise ValueError("Assessment EVALUABLE requiere outcome TRUE/FALSE")
        active = assessment.outcome == "TRUE"

        if frontier_class == FrontierClass.H:
            evaluated = True
            satisfied = not active
            solvable = False
            materially_insufficient = False
        elif frontier_class == FrontierClass.K:
            evaluated = True
            satisfied = not active
            solvable = True
            materially_insufficient = False
        else:
            if not active:
                return None
            evaluated = True
            satisfied = None
            solvable = None
            materially_insufficient = True
    elif assessment.status == "NOT_EVALUABLE":
        if frontier_class in {FrontierClass.H, FrontierClass.K}:
            evaluated = False
            satisfied = None
            solvable = None
            materially_insufficient = True
        else:
            evaluated = True
            satisfied = None
            solvable = None
            materially_insufficient = True
    else:
        raise ValueError("Assessment.status no soportado por VF minimal")

    return FrontierAssessment(
        assessment_id=f"vf:{assessment.rule_id}:{assessment_fingerprint(assessment)}",
        decision_id=context.decision_id,
        scenario_id=context.scenario_id,
        frontier_class=frontier_class,
        evaluated=evaluated,
        satisfied=satisfied,
        solvable=solvable,
        rule_id=assessment.rule_id,
        trace_reference=trace.trace_id,
        materially_insufficient=materially_insufficient,
        authority_conflict=False,
    )


def produce_frontier_assessments(
    *,
    purchase: PurchaseOperation,
    context: DecisionContext,
    bindings: Sequence[AssessmentTraceBinding],
) -> tuple[FrontierAssessment, ...]:
    """Produce only explicitly authorized H/K/U consequences from provenanced C0 material."""
    purchase_snapshot = purchase.model_copy(deep=True)
    context_snapshot = context.model_copy(deep=True)
    binding_snapshots = tuple(item.model_copy(deep=True) for item in bindings)

    if purchase_snapshot.decision_id != context_snapshot.decision_id:
        raise ValueError("PurchaseOperation y DecisionContext tienen decision_id distintos")
    if purchase_snapshot.scenario_id != context_snapshot.scenario_id:
        raise ValueError("PurchaseOperation y DecisionContext tienen scenario_id distintos")

    rule_ids = tuple(item.assessment.rule_id for item in binding_snapshots)
    if len(rule_ids) != len(set(rule_ids)):
        raise ValueError("No se permiten rule_id duplicados para Viability Frontier")

    produced: list[FrontierAssessment] = []
    for binding in binding_snapshots:
        consequence = _frontier_from_binding(
            binding,
            purchase=purchase_snapshot,
            context=context_snapshot,
        )
        if consequence is not None:
            produced.append(consequence)

    return tuple(
        sorted(
            produced,
            key=lambda item: (item.assessment_id, item.rule_id, item.trace_reference),
        )
    )


def evaluate_provenanced_viability(
    *,
    purchase: PurchaseOperation,
    context: DecisionContext,
    bindings: Sequence[AssessmentTraceBinding],
) -> ViabilityResult:
    """Evaluate VF only from consequences reconstructed from provenanced bindings."""
    purchase_snapshot = purchase.model_copy(deep=True)
    context_snapshot = context.model_copy(deep=True)
    binding_snapshots = tuple(item.model_copy(deep=True) for item in bindings)

    consequences = produce_frontier_assessments(
        purchase=purchase_snapshot,
        context=context_snapshot,
        bindings=binding_snapshots,
    )
    return evaluate_viability(
        context_snapshot.decision_id,
        context_snapshot.scenario_id,
        consequences,
        rules_version=context_snapshot.rules_version,
        parameters_version=context_snapshot.parameters_version,
        data_snapshot_id=context_snapshot.data_snapshot_id,
    )


__all__ = [
    "VF_MINIMAL_CATALOG",
    "evaluate_provenanced_viability",
    "produce_frontier_assessments",
]
