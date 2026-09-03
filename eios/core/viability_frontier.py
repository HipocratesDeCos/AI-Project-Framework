"""Deterministic, non-authoritative viability frontier evaluation.

FrontierAssessment is a technical representation of an already-authorized
frontier consequence. It does not create normative authority.
"""

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
    """Technical representation of an externally authorized consequence."""

    assessment_id: str
    decision_id: str
    scenario_id: str
    frontier_class: FrontierClass
    evaluated: bool
    satisfied: bool | None
    solvable: bool | None
    rule_id: str
    trace_reference: str
    materially_insufficient: bool = False
    authority_conflict: bool = False


@dataclass(frozen=True)
class ViabilityResult:
    decision_id: str
    scenario_id: str
    status: ViabilityStatus
    assessment_ids: Tuple[str, ...]
    rule_ids: Tuple[str, ...]
    trace_references: Tuple[str, ...]
    rules_version: str | None = None
    parameters_version: str | None = None
    data_snapshot_id: str | None = None
    limitation: str | None = None


def _validate(item: FrontierAssessment, decision_id: str, scenario_id: str) -> None:
    if not item.assessment_id or not item.rule_id or not item.trace_reference:
        raise FrontierInputError("frontier assessment identifiers/references are required")
    if item.decision_id != decision_id or item.scenario_id != scenario_id:
        raise FrontierInputError("assessment context is incompatible with frontier context")
    if item.authority_conflict:
        return
    if item.frontier_class == FrontierClass.H and item.evaluated and item.satisfied is None:
        raise FrontierInputError("evaluated H consequence requires explicit satisfaction state")
    if item.frontier_class == FrontierClass.K and item.evaluated and (
        item.satisfied is None or item.solvable is None
    ):
        raise FrontierInputError("evaluated K consequence requires satisfaction and solvability")
    if item.frontier_class == FrontierClass.U and item.evaluated and not item.materially_insufficient:
        raise FrontierInputError("evaluated U consequence requires explicit material insufficiency")


def evaluate_viability(
    decision_id: str,
    scenario_id: str,
    assessments: Iterable[FrontierAssessment],
    *,
    rules_version: str | None = None,
    parameters_version: str | None = None,
    data_snapshot_id: str | None = None,
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

    base = dict(
        decision_id=decision_id,
        scenario_id=scenario_id,
        assessment_ids=assessment_ids,
        rule_ids=rule_ids,
        trace_references=traces,
        rules_version=rules_version,
        parameters_version=parameters_version,
        data_snapshot_id=data_snapshot_id,
    )

    conflicts = tuple(x for x in ordered if x.authority_conflict)
    if conflicts:
        return ViabilityResult(
            status=ViabilityStatus.NOT_EVALUABLE,
            limitation="UNRESOLVED_AUTHORITY_CONFLICT",
            **base,
        )

    hard = tuple(
        x for x in ordered
        if x.frontier_class == FrontierClass.H and x.evaluated and x.satisfied is False
    )
    if hard:
        return ViabilityResult(status=ViabilityStatus.NOT_VIABLE, **base)

    insufficient = tuple(
        x for x in ordered
        if x.frontier_class == FrontierClass.U and x.materially_insufficient
    )
    if insufficient:
        return ViabilityResult(
            status=ViabilityStatus.NOT_EVALUABLE,
            limitation="MATERIAL_INSUFFICIENCY",
            **base,
        )

    unresolved = tuple(
        x for x in ordered
        if x.frontier_class in (FrontierClass.H, FrontierClass.K)
        and not x.evaluated
        and x.materially_insufficient
    )
    if unresolved:
        return ViabilityResult(
            status=ViabilityStatus.NOT_EVALUABLE,
            limitation="MATERIAL_UNEVALUATED_FRONTIER_CONSEQUENCE",
            **base,
        )

    conditional = tuple(
        x for x in ordered
        if x.frontier_class == FrontierClass.K
        and x.evaluated
        and x.satisfied is False
        and x.solvable is True
    )
    if conditional:
        return ViabilityResult(status=ViabilityStatus.VIABLE_CON_CONDICIONES, **base)

    return ViabilityResult(status=ViabilityStatus.VIABLE, **base)
