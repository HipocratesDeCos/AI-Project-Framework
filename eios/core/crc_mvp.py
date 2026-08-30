"""Minimal CRC implementation for the EIOS Vertical MVP.

This module consolidates already-produced Assessment results. It does not
implement quality, evidence, viability, scenario generation, negotiation,
exceptions, overrides, scoring, ranking, or business execution.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Mapping, Sequence

from pydantic import BaseModel, ConfigDict, Field, model_validator

from eios.core.models import Assessment, DecisionContext


Effect = Literal["R0", "R1", "R2", "R3"]
Severity = Literal["CRÍTICA", "ALTA", "MEDIA", "BAJA", "INFORMATIVA"]
ConsolidatedResult = Literal[
    "COMPRAR",
    "NEGOCIAR",
    "COMPRAR CONDICIONADO",
    "NO COMPRAR",
    "INFORMACIÓN INSUFICIENTE",
]


@dataclass(frozen=True)
class RuleMetadata:
    """Normative rule metadata supplied by the rule registry/runtime."""

    rule_id: str
    version: str
    effect: Effect
    severity: Severity


@dataclass(frozen=True)
class CRCTraceability:
    """Minimal traceability view; source Assessment objects are not mutated."""

    decision_id: str
    scenario_id: str
    rules_version: str
    assessment_rule_ids: tuple[str, ...]


class CRCInput(BaseModel):
    """Logical input contract for CRC-MVP."""

    model_config = ConfigDict(extra="forbid")

    assessments: list[Assessment] = Field(default_factory=list)
    decision_context: DecisionContext
    base_result: ConsolidatedResult


class CRCResult(BaseModel):
    """Consolidated EIOS result, not a business decision or execution command."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    consolidated_result: ConsolidatedResult
    dominant_reason: str
    relevant_factors: tuple[str, ...] = ()
    conflicts: tuple[str, ...] = ()
    traceability: CRCTraceability

    @model_validator(mode="after")
    def require_dominant_reason(self) -> "CRCResult":
        if not self.dominant_reason.strip():
            raise ValueError("dominant_reason no puede estar vacío")
        return self


_EFFECT_PRIORITY = {"R0": 0, "R1": 1, "R2": 2, "R3": 3}
_EFFECT_RESULT: dict[Effect, ConsolidatedResult | None] = {
    "R0": "NO COMPRAR",
    "R1": "COMPRAR CONDICIONADO",
    "R2": "NEGOCIAR",
    "R3": None,
}


def resolve_crc(
    crc_input: CRCInput,
    rule_metadata: Mapping[str, RuleMetadata],
) -> CRCResult:
    """Consolidate Assessment results using authorized rule effects.

    The function is intentionally deterministic and conservative: missing or
    incompatible rule metadata is an integrity error, and non-evaluable
    assessments are never converted to FALSE.
    """

    assessments: Sequence[Assessment] = crc_input.assessments
    context = crc_input.decision_context

    for item in assessments:
        metadata = rule_metadata.get(item.rule_id)
        if metadata is None:
            raise ValueError(f"rule_id no resoluble: {item.rule_id}")
        if metadata.version != context.rules_version:
            raise ValueError(
                f"rules_version incompatible con rule_id {item.rule_id}: "
                f"{metadata.version} != {context.rules_version}"
            )

    if not assessments:
        return CRCResult(
            consolidated_result=crc_input.base_result,
            dominant_reason="Sin evaluaciones individuales adicionales; se conserva el resultado base autorizado.",
            traceability=CRCTraceability(
                decision_id=context.decision_id,
                scenario_id=context.scenario_id,
                rules_version=context.rules_version,
                assessment_rule_ids=(),
            ),
        )

    evaluated = [a for a in assessments if a.status == "EVALUABLE"]
    not_evaluable = [a for a in assessments if a.status == "NOT_EVALUABLE"]

    active: list[tuple[Assessment, RuleMetadata]] = []
    for item in evaluated:
        # In C0, TRUE represents the rule condition/result being satisfied.
        if item.outcome == "TRUE":
            active.append((item, rule_metadata[item.rule_id]))

    # A known R0 remains dominant even when other information is incomplete.
    if active:
        active.sort(key=lambda pair: _EFFECT_PRIORITY[pair[1].effect])
        dominant_assessment, dominant_rule = active[0]
        dominant_effect = dominant_rule.effect
        consolidated = _EFFECT_RESULT[dominant_effect] or crc_input.base_result

        lower_reasons = tuple(
            item.reason
            for item, metadata in active[1:]
            if metadata.effect != dominant_effect
        )
        informative_reasons = tuple(
            item.reason for item, metadata in active if metadata.effect == "R3" and item is not dominant_assessment
        )
        relevant = lower_reasons + informative_reasons

        conflicts = tuple(
            f"{item.rule_id}:{metadata.effect}"
            for item, metadata in active
            if metadata.effect != dominant_effect
        )

        return CRCResult(
            consolidated_result=consolidated,
            dominant_reason=dominant_assessment.reason,
            relevant_factors=relevant,
            conflicts=conflicts,
            traceability=CRCTraceability(
                decision_id=context.decision_id,
                scenario_id=context.scenario_id,
                rules_version=context.rules_version,
                assessment_rule_ids=tuple(a.rule_id for a in assessments),
            ),
        )

    if not_evaluable:
        return CRCResult(
            consolidated_result="INFORMACIÓN INSUFICIENTE",
            dominant_reason=not_evaluable[0].reason,
            relevant_factors=tuple(a.reason for a in not_evaluable[1:]),
            traceability=CRCTraceability(
                decision_id=context.decision_id,
                scenario_id=context.scenario_id,
                rules_version=context.rules_version,
                assessment_rule_ids=tuple(a.rule_id for a in assessments),
            ),
        )

    # Only inactive/false rules remain; no restriction is invented.
    reasons = tuple(a.reason for a in assessments)
    return CRCResult(
        consolidated_result=crc_input.base_result,
        dominant_reason=reasons[0],
        relevant_factors=reasons[1:],
        traceability=CRCTraceability(
            decision_id=context.decision_id,
            scenario_id=context.scenario_id,
            rules_version=context.rules_version,
            assessment_rule_ids=tuple(a.rule_id for a in assessments),
        ),
    )


__all__ = ["CRCInput", "CRCResult", "CRCTraceability", "RuleMetadata", "resolve_crc"]
