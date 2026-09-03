"""Deterministic, non-authoritative viability frontier evaluation."""

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Tuple


class ViabilityStatus(str, Enum):
    VIABLE = "VIABLE"
    VIABLE_CON_CONDICIONES = "VIABLE_CON_CONDICIONES"
    NOT_VIABLE = "NOT_VIABLE"
    NOT_EVALUABLE = "NOT_EVALUABLE"


class FrontierClass(str, Enum):
    H = "H"
    K = "K"
    U = "U"
    S = "S"


class FrontierInputError(ValueError):
    """Raised for malformed or context-incompatible frontier input."""


@dataclass(frozen=True)
class FrontierAssessment:
    assessment_id: str
    decision_id: str
    scenario_id: str
    frontier_class: FrontierClass
    evaluated: bool
    satisfied: bool | None
    solvable: bool | None
    rule_id: str
    trace_reference: str


@dataclass(frozen=True)
class ViabilityResult:
    decision_id: str
    scenario_id: str
    status: ViabilityStatus
    assessment_ids: Tuple[str, ...]
    rule_ids: Tuple[str, ...]
    trace_references: Tuple[str, ...]
    limitation: str | None = None


def _validate(item: FrontierAssessment, decision_id: str, scenario_id: str) -> None:
    if not item.assessment_id or not item.rule_id or not item.trace_reference:
        raise FrontierInputError("frontier assessment identifiers/references are required")
    if item.decision_id != decision_id or item.scenario_id != scenario_id:
        raise FrontierInputError("assessment context is incompatible with frontier context")
    if not item.evaluated and item.frontier_class in (FrontierClass.H, FrontierClass.K):
        return
    if item.frontier_class == FrontierClass.H and item.satisfied is None:
        raise FrontierInputError("H consequence requires explicit satisfaction state")
    if item.frontier_class == FrontierClass.K and (item.satisfied is None or item.solvable is None):
        raise FrontierInputError("K consequence requires satisfaction and solvability")


def evaluate_viability(
    decision_id: str,
    scenario_id: str,
    assessments: Iterable[FrontierAssessment],
) -> ViabilityResult:
    """Apply only the authorized H -> U -> K -> VIABLE precedence."""
    items = tuple(assessments)
    seen: set[str] = set()
    for item in items:
        _validate(item, decision_id, scenario_id)
        if item.assessment_id in seen:
            raise FrontierInputError("duplicate assessment_id")
        seen.add(item.assessment_id)

    ordered = tuple(sorted(items, key=lambda x: (x.assessment_id, x.rule_id, x.trace_reference)))
    assessment_ids = tuple(x.assessment_id for x in ordered)
    rule_ids = tuple(x.rule_id for x in ordered)
    traces = tuple(x.trace_reference for x in ordered)

    hard = tuple(x for x in ordered if x.frontier_class == FrontierClass.H and x.evaluated and x.satisfied is False)
    if hard:
        return ViabilityResult(decision_id, scenario_id, ViabilityStatus.NOT_VIABLE, assessment_ids, rule_ids, traces)

    insufficient = tuple(x for x in ordered if x.frontier_class == FrontierClass.U)
    if insufficient:
        return ViabilityResult(
            decision_id, scenario_id, ViabilityStatus.NOT_EVALUABLE,
            assessment_ids, rule_ids, traces, "material insufficiency in frontier evaluation"
        )

    conditional = tuple(
        x for x in ordered
        if x.frontier_class == FrontierClass.K and x.evaluated and x.satisfied is False and x.solvable is True
    )
    if conditional:
        return ViabilityResult(decision_id, scenario_id, ViabilityStatus.VIABLE_CON_CONDICIONES, assessment_ids, rule_ids, traces)

    return ViabilityResult(decision_id, scenario_id, ViabilityStatus.VIABLE, assessment_ids, rule_ids, traces)
