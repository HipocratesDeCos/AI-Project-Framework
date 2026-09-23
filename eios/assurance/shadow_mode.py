"""Assurance Shadow Mode observation boundary.

Shadow Mode preserves the EIOS consolidated result and an observed human business
decision as distinct facts. Literal comparison is descriptive only and never
feeds back into Rules, Parameters, CRC, or O1 execution.
"""
from __future__ import annotations

from datetime import datetime
from hashlib import sha256
import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from eios.core.crc_mvp import CRCResult, ConsolidatedResult
from eios.core.models import DecisionContext, Evidence
from eios.core.validation import validate_evidence


HumanDecisionSourceState = Literal[
    "OBSERVED",
    "NOT_OBSERVED",
    "NOT_DETERMINABLE",
    "CONFLICTING",
]
SystemVisibilityState = Literal["WITHHELD_DECLARED", "EXPOSED", "UNKNOWN"]
ShadowComparisonState = Literal[
    "MATCH",
    "DIFFERENT",
    "SYSTEM_INSUFFICIENT",
    "HUMAN_NOT_OBSERVED",
    "NOT_COMPARABLE",
]
ShadowEligibility = Literal[
    "SHADOW_ELIGIBLE",
    "NOT_SHADOW_ELIGIBLE",
    "NOT_DETERMINABLE",
]


class _Frozen(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)


class ObservedHumanDecision(_Frozen):
    decision_id: str = Field(min_length=1, max_length=64)
    scenario_id: str = Field(min_length=1, max_length=64)
    observed_result: ConsolidatedResult | None = None
    decision_ref: str | None = Field(default=None, min_length=1, max_length=256)
    decided_at: datetime | None = None
    decision_authority_ref: str | None = Field(default=None, min_length=1, max_length=256)
    evidence_refs: tuple[str, ...] = ()
    trace_refs: tuple[str, ...] = ()
    source_state: HumanDecisionSourceState

    @model_validator(mode="after")
    def validate_state(self) -> "ObservedHumanDecision":
        if len(self.evidence_refs) != len(set(self.evidence_refs)):
            raise ValueError("evidence_refs no puede contener duplicados")
        if len(self.trace_refs) != len(set(self.trace_refs)):
            raise ValueError("trace_refs no puede contener duplicados")
        if self.source_state == "OBSERVED":
            required = (
                self.observed_result,
                self.decision_ref,
                self.decided_at,
                self.decision_authority_ref,
            )
            if any(value is None for value in required):
                raise ValueError("OBSERVED requiere resultado, referencia, fecha y autoridad")
            if not self.evidence_refs:
                raise ValueError("OBSERVED requiere evidence_refs")
            if not self.trace_refs:
                raise ValueError("OBSERVED requiere trace_refs")
        return self


class ShadowObservation(_Frozen):
    decision_id: str = Field(min_length=1, max_length=64)
    scenario_id: str = Field(min_length=1, max_length=64)
    rules_version: str = Field(min_length=1, max_length=64)
    parameters_version: str = Field(min_length=1, max_length=64)
    data_snapshot_id: str = Field(min_length=1, max_length=64)
    system_result: ConsolidatedResult
    human_result: ConsolidatedResult | None = None
    comparison_state: ShadowComparisonState
    execution_ref: str = Field(min_length=1, max_length=256)
    decision_ref: str | None = Field(default=None, max_length=256)
    system_trace_refs: tuple[str, ...] = ()
    human_trace_refs: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()


class ShadowModeResult(_Frozen):
    observation_id: str = Field(min_length=1, max_length=320)
    observation: ShadowObservation
    eligibility: ShadowEligibility
    comparison_state: ShadowComparisonState
    limitations: tuple[str, ...] = ()
    trace_refs: tuple[str, ...] = ()


def _canonical(value):
    if hasattr(value, "model_dump"):
        value = value.model_dump(mode="python")
    if isinstance(value, dict):
        return {key: _canonical(value[key]) for key in sorted(value)}
    if isinstance(value, (tuple, list)):
        return [_canonical(item) for item in value]
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def _fingerprint(payload: dict) -> str:
    raw = json.dumps(
        _canonical(payload),
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return sha256(raw).hexdigest()


def _validate_crc(context: DecisionContext, crc_result: CRCResult) -> None:
    trace = crc_result.traceability
    if trace.decision_id != context.decision_id:
        raise ValueError("CRCResult.decision_id incompatible")
    if trace.scenario_id != context.scenario_id:
        raise ValueError("CRCResult.scenario_id incompatible")
    if trace.rules_version != context.rules_version:
        raise ValueError("CRCResult.rules_version incompatible")


def _validate_human(
    *,
    context: DecisionContext,
    human_decision: ObservedHumanDecision,
    evidences: tuple[Evidence, ...],
) -> None:
    if human_decision.decision_id != context.decision_id:
        raise ValueError("ObservedHumanDecision.decision_id incompatible")
    if human_decision.scenario_id != context.scenario_id:
        raise ValueError("ObservedHumanDecision.scenario_id incompatible")

    if human_decision.source_state != "OBSERVED":
        return

    by_id = {item.evidence_id: item for item in evidences}
    if len(by_id) != len(evidences):
        raise ValueError("evidence_id duplicado")

    authority_ok = any(
        item.state == "DEMONSTRATED"
        and item.demonstration_ref == human_decision.decision_authority_ref
        and validate_evidence(item).status == "VALID"
        for item in evidences
    )
    if not authority_ok:
        raise ValueError("decision_authority_ref no demostrada")

    for evidence_id in human_decision.evidence_refs:
        item = by_id.get(evidence_id)
        if (
            item is None
            or item.state != "DEMONSTRATED"
            or validate_evidence(item).status != "VALID"
        ):
            raise ValueError("evidence_ref de decisión humana no demostrada")


def produce_shadow_mode_result(
    *,
    context: DecisionContext,
    crc_result: CRCResult,
    execution_ref: str,
    shadow_evaluation_recorded_at: datetime,
    human_decision: ObservedHumanDecision,
    system_visibility_state: SystemVisibilityState,
    evidences: tuple[Evidence, ...],
) -> ShadowModeResult:
    """Create one descriptive Shadow Mode observation without feedback effects."""
    if not execution_ref.strip():
        raise ValueError("execution_ref no puede estar vacío")

    context_snapshot = context.model_copy(deep=True)
    crc_snapshot = crc_result.model_copy(deep=True)
    human_snapshot = human_decision.model_copy(deep=True)
    evidence_snapshot = tuple(item.model_copy(deep=True) for item in evidences)

    _validate_crc(context_snapshot, crc_snapshot)
    _validate_human(
        context=context_snapshot,
        human_decision=human_snapshot,
        evidences=evidence_snapshot,
    )

    if (
        human_snapshot.source_state == "OBSERVED"
        and human_snapshot.decided_at is not None
        and human_snapshot.decided_at < shadow_evaluation_recorded_at
    ):
        raise ValueError("decided_at no puede ser anterior a shadow_evaluation_recorded_at")

    system_result = crc_snapshot.consolidated_result
    human_result = (
        human_snapshot.observed_result
        if human_snapshot.source_state == "OBSERVED"
        else None
    )

    limitations: list[str] = [
        "MATCH/DIFFERENT son comparación literal, no juicio de corrección.",
        "Shadow Mode no verifica identidad personal, firma, IAM ni mandato empresarial.",
    ]

    if human_snapshot.source_state != "OBSERVED":
        comparison: ShadowComparisonState = "HUMAN_NOT_OBSERVED"
    elif system_result == "INFORMACIÓN INSUFICIENTE":
        comparison = "SYSTEM_INSUFFICIENT"
    elif human_result == system_result:
        comparison = "MATCH"
    else:
        comparison = "DIFFERENT"

    if human_snapshot.source_state != "OBSERVED":
        eligibility: ShadowEligibility = "NOT_SHADOW_ELIGIBLE"
        limitations.append("No existe decisión humana OBSERVED para comparación Shadow.")
    elif system_visibility_state == "WITHHELD_DECLARED":
        eligibility = "SHADOW_ELIGIBLE"
        limitations.append(
            "WITHHELD_DECLARED es una declaración de proceso, no una prueba técnica de ocultación."
        )
    elif system_visibility_state == "EXPOSED":
        eligibility = "NOT_SHADOW_ELIGIBLE"
        limitations.append("La evaluación EIOS fue declarada EXPOSED antes de la decisión.")
    else:
        eligibility = "NOT_DETERMINABLE"
        limitations.append("La visibilidad de la evaluación EIOS es UNKNOWN.")

    system_trace_refs = (execution_ref,)
    human_trace_refs = human_snapshot.trace_refs
    trace_refs = tuple(sorted(set((*system_trace_refs, *human_trace_refs))))

    observation = ShadowObservation(
        decision_id=context_snapshot.decision_id,
        scenario_id=context_snapshot.scenario_id,
        rules_version=context_snapshot.rules_version,
        parameters_version=context_snapshot.parameters_version,
        data_snapshot_id=context_snapshot.data_snapshot_id,
        system_result=system_result,
        human_result=human_result,
        comparison_state=comparison,
        execution_ref=execution_ref,
        decision_ref=human_snapshot.decision_ref,
        system_trace_refs=system_trace_refs,
        human_trace_refs=human_trace_refs,
        limitations=tuple(limitations),
    )

    fp = _fingerprint(
        {
            "context": context_snapshot,
            "crc_result": crc_snapshot,
            "execution_ref": execution_ref,
            "shadow_evaluation_recorded_at": shadow_evaluation_recorded_at,
            "human_decision": human_snapshot,
            "system_visibility_state": system_visibility_state,
            "evidence_ids": tuple(item.evidence_id for item in evidence_snapshot),
        }
    )

    return ShadowModeResult(
        observation_id=(
            f"shadow:{context_snapshot.decision_id}:{context_snapshot.scenario_id}:{fp}"
        ),
        observation=observation,
        eligibility=eligibility,
        comparison_state=comparison,
        limitations=tuple(limitations),
        trace_refs=trace_refs,
    )


__all__ = [
    "HumanDecisionSourceState",
    "ObservedHumanDecision",
    "ShadowComparisonState",
    "ShadowEligibility",
    "ShadowModeResult",
    "ShadowObservation",
    "SystemVisibilityState",
    "produce_shadow_mode_result",
]
