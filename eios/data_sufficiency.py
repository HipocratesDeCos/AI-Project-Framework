"""Provenance-safe factual contracts for R-DAT-003 data sufficiency."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from eios.core.models import DecisionContext, Evidence, PurchaseOperation
from eios.core.validation import validate_evidence


RequirementClassification = Literal["SATISFIED", "FAILED", "UNDETERMINED"]
DataSufficiencyState = Literal[
    "AVAILABLE",
    "NOT_EVIDENCED",
    "CONFLICTING_DATA",
    "NOT_DETERMINABLE",
]

DECISION_EVIDENCE_SUFFICIENCY_EVIDENCE_SOURCE_TYPE = "DecisionEvidenceSufficiencyEvidence"


def _fingerprint(prefix: str, payload: dict) -> str:
    raw = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return f"{prefix}:{hashlib.sha256(raw).hexdigest()}"


def decision_evidence_purchase_ref(purchase: PurchaseOperation) -> str:
    if not isinstance(purchase, PurchaseOperation):
        raise TypeError("purchase debe ser PurchaseOperation")
    return _fingerprint("decision_evidence_purchase", purchase.model_dump(mode="json"))


class DecisionEvidenceRequirementSet(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    decision_id: str = Field(min_length=1, max_length=64)
    scenario_id: str = Field(min_length=1, max_length=64)
    data_snapshot_id: str = Field(min_length=1, max_length=64)
    company_scope: str = Field(min_length=1, max_length=128)
    purchase_operation_ref: str = Field(min_length=1, max_length=128)
    effective_date: date
    requirement_set_id: str = Field(min_length=1, max_length=128)
    requirement_set_version: str = Field(min_length=1, max_length=64)
    requirement_ids: tuple[str, ...]
    authority_ref: str = Field(min_length=1, max_length=256)
    methodology_ref: str = Field(min_length=1, max_length=256)
    trace_refs: tuple[str, ...] = ()

    @field_validator("requirement_ids", "trace_refs")
    @classmethod
    def unique_nonempty_refs(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if len(value) != len(set(value)):
            raise ValueError("las referencias no pueden contener duplicados")
        if any(not item.strip() for item in value):
            raise ValueError("las referencias no pueden contener valores vacíos")
        return value


def decision_evidence_requirement_set_ref(
    requirement_set: DecisionEvidenceRequirementSet,
) -> str:
    if not isinstance(requirement_set, DecisionEvidenceRequirementSet):
        raise TypeError("requirement_set debe ser DecisionEvidenceRequirementSet")
    return _fingerprint(
        "decision_evidence_requirement_set",
        requirement_set.model_dump(mode="json"),
    )


class RequirementEvidenceBinding(BaseModel):
    """Explicit upstream classification of one required evidence requirement."""

    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    requirement_id: str = Field(min_length=1, max_length=128)
    classification: RequirementClassification
    evidence: tuple[Evidence, ...] = ()
    classification_ref: str | None = Field(default=None, max_length=256)
    authority_ref: str = Field(min_length=1, max_length=256)
    trace_refs: tuple[str, ...] = ()

    @field_validator("trace_refs")
    @classmethod
    def unique_trace_refs(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if len(value) != len(set(value)):
            raise ValueError("trace_refs no puede contener duplicados")
        if any(not item.strip() for item in value):
            raise ValueError("trace_refs no puede contener referencias vacías")
        return value

    @model_validator(mode="after")
    def validate_classification_support(self) -> "RequirementEvidenceBinding":
        evidence_ids = [item.evidence_id for item in self.evidence]
        if len(evidence_ids) != len(set(evidence_ids)):
            raise ValueError("evidence no puede contener evidence_id duplicados")

        if self.classification in {"SATISFIED", "FAILED"}:
            if not self.classification_ref:
                raise ValueError(
                    "SATISFIED/FAILED requieren classification_ref explícito"
                )
            if not self.evidence:
                raise ValueError("SATISFIED/FAILED requieren Evidence demostrada")
            if any(validate_evidence(item).status != "VALID" for item in self.evidence):
                raise ValueError(
                    "SATISFIED/FAILED solo admiten Evidence válida/demostrada"
                )
        return self


class DecisionEvidenceSufficiencyObservation(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    decision_id: str = Field(min_length=1, max_length=64)
    scenario_id: str = Field(min_length=1, max_length=64)
    data_snapshot_id: str = Field(min_length=1, max_length=64)
    company_scope: str = Field(min_length=1, max_length=128)
    purchase_operation_ref: str = Field(min_length=1, max_length=128)
    evaluation_date: date
    requirement_set_ref: str | None = Field(default=None, max_length=256)
    required_requirement_ids: tuple[str, ...] = ()
    satisfied_requirement_ids: tuple[str, ...] = ()
    failed_requirement_ids: tuple[str, ...] = ()
    undetermined_requirement_ids: tuple[str, ...] = ()
    state: DataSufficiencyState
    source_ref: str = Field(min_length=1, max_length=256)
    authority_ref: str = Field(min_length=1, max_length=256)
    methodology_ref: str = Field(min_length=1, max_length=256)
    trace_refs: tuple[str, ...] = ()

    @field_validator(
        "required_requirement_ids",
        "satisfied_requirement_ids",
        "failed_requirement_ids",
        "undetermined_requirement_ids",
        "trace_refs",
    )
    @classmethod
    def unique_nonempty_refs(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if len(value) != len(set(value)):
            raise ValueError("las referencias no pueden contener duplicados")
        if any(not item.strip() for item in value):
            raise ValueError("las referencias no pueden contener valores vacíos")
        return value

    @model_validator(mode="after")
    def validate_partition(self) -> "DecisionEvidenceSufficiencyObservation":
        required = set(self.required_requirement_ids)
        satisfied = set(self.satisfied_requirement_ids)
        failed = set(self.failed_requirement_ids)
        undetermined = set(self.undetermined_requirement_ids)

        if self.state == "AVAILABLE":
            if not self.requirement_set_ref:
                raise ValueError("AVAILABLE requiere requirement_set_ref")
            if not required:
                raise ValueError("AVAILABLE requiere RequirementSet no vacío")
            if satisfied & failed or satisfied & undetermined or failed & undetermined:
                raise ValueError("las clasificaciones deben ser disjuntas")
            if satisfied | failed | undetermined != required:
                raise ValueError(
                    "la clasificación debe cubrir exactamente todos los requirements"
                )
        else:
            if satisfied or failed or undetermined:
                raise ValueError(
                    "un estado no AVAILABLE no puede publicar clasificación parcial"
                )
        return self


def decision_evidence_sufficiency_ref(
    observation: DecisionEvidenceSufficiencyObservation,
) -> str:
    if not isinstance(observation, DecisionEvidenceSufficiencyObservation):
        raise TypeError(
            "observation debe ser DecisionEvidenceSufficiencyObservation"
        )
    return _fingerprint(
        "decision_evidence_sufficiency",
        observation.model_dump(mode="json"),
    )


@dataclass(frozen=True)
class DecisionEvidenceSufficiencyProducer:
    """Build sufficiency observations only from explicit requirement bindings."""

    authority_ref: str
    methodology_ref: str

    def __post_init__(self) -> None:
        if not self.authority_ref.strip():
            raise ValueError("authority_ref no puede estar vacío")
        if not self.methodology_ref.strip():
            raise ValueError("methodology_ref no puede estar vacío")

    def produce(
        self,
        *,
        purchase: PurchaseOperation,
        context: DecisionContext,
        company_scope: str,
        state: DataSufficiencyState,
        requirement_set: DecisionEvidenceRequirementSet | None,
        bindings: tuple[RequirementEvidenceBinding, ...] = (),
        source_ref: str,
        trace_refs: tuple[str, ...] = (),
    ) -> DecisionEvidenceSufficiencyObservation:
        if purchase.decision_id != context.decision_id:
            raise ValueError(
                "PurchaseOperation y DecisionContext tienen decision_id distintos"
            )
        if purchase.scenario_id != context.scenario_id:
            raise ValueError(
                "PurchaseOperation y DecisionContext tienen scenario_id distintos"
            )
        if not company_scope.strip():
            raise ValueError("company_scope no puede estar vacío")
        if not source_ref.strip():
            raise ValueError("source_ref no puede estar vacío")

        purchase_ref = decision_evidence_purchase_ref(purchase)

        if state != "AVAILABLE":
            if bindings:
                raise ValueError(
                    "un estado no AVAILABLE no admite clasificación parcial"
                )
            if requirement_set is not None:
                self._validate_requirement_set(
                    purchase, context, company_scope, purchase_ref, requirement_set
                )
            return DecisionEvidenceSufficiencyObservation(
                decision_id=context.decision_id,
                scenario_id=context.scenario_id,
                data_snapshot_id=context.data_snapshot_id,
                company_scope=company_scope,
                purchase_operation_ref=purchase_ref,
                evaluation_date=purchase.operation_date,
                requirement_set_ref=(
                    decision_evidence_requirement_set_ref(requirement_set)
                    if requirement_set is not None
                    else None
                ),
                required_requirement_ids=(
                    requirement_set.requirement_ids
                    if requirement_set is not None
                    else ()
                ),
                state=state,
                source_ref=source_ref,
                authority_ref=self.authority_ref,
                methodology_ref=self.methodology_ref,
                trace_refs=trace_refs,
            )

        if requirement_set is None:
            raise ValueError("AVAILABLE requiere RequirementSet explícito")
        self._validate_requirement_set(
            purchase, context, company_scope, purchase_ref, requirement_set
        )
        if not requirement_set.requirement_ids:
            return DecisionEvidenceSufficiencyObservation(
                decision_id=context.decision_id,
                scenario_id=context.scenario_id,
                data_snapshot_id=context.data_snapshot_id,
                company_scope=company_scope,
                purchase_operation_ref=purchase_ref,
                evaluation_date=purchase.operation_date,
                requirement_set_ref=decision_evidence_requirement_set_ref(
                    requirement_set
                ),
                required_requirement_ids=(),
                state="NOT_DETERMINABLE",
                source_ref=source_ref,
                authority_ref=self.authority_ref,
                methodology_ref=self.methodology_ref,
                trace_refs=trace_refs,
            )

        ids = [item.requirement_id for item in bindings]
        if len(ids) != len(set(ids)):
            raise ValueError("bindings contiene requirement_id duplicados")
        if set(ids) != set(requirement_set.requirement_ids):
            raise ValueError(
                "bindings debe cubrir exactamente requirement_ids del RequirementSet"
            )

        satisfied = tuple(
            item.requirement_id
            for item in bindings
            if item.classification == "SATISFIED"
        )
        failed = tuple(
            item.requirement_id
            for item in bindings
            if item.classification == "FAILED"
        )
        undetermined = tuple(
            item.requirement_id
            for item in bindings
            if item.classification == "UNDETERMINED"
        )

        return DecisionEvidenceSufficiencyObservation(
            decision_id=context.decision_id,
            scenario_id=context.scenario_id,
            data_snapshot_id=context.data_snapshot_id,
            company_scope=company_scope,
            purchase_operation_ref=purchase_ref,
            evaluation_date=purchase.operation_date,
            requirement_set_ref=decision_evidence_requirement_set_ref(
                requirement_set
            ),
            required_requirement_ids=requirement_set.requirement_ids,
            satisfied_requirement_ids=satisfied,
            failed_requirement_ids=failed,
            undetermined_requirement_ids=undetermined,
            state="AVAILABLE",
            source_ref=source_ref,
            authority_ref=self.authority_ref,
            methodology_ref=self.methodology_ref,
            trace_refs=trace_refs,
        )

    @staticmethod
    def _validate_requirement_set(
        purchase: PurchaseOperation,
        context: DecisionContext,
        company_scope: str,
        purchase_ref: str,
        requirement_set: DecisionEvidenceRequirementSet,
    ) -> None:
        if requirement_set.decision_id != context.decision_id:
            raise ValueError("RequirementSet pertenece a otra decisión")
        if requirement_set.scenario_id != context.scenario_id:
            raise ValueError("RequirementSet pertenece a otro escenario")
        if requirement_set.data_snapshot_id != context.data_snapshot_id:
            raise ValueError("RequirementSet pertenece a otro data_snapshot_id")
        if requirement_set.company_scope != company_scope:
            raise ValueError("RequirementSet pertenece a otro company_scope")
        if requirement_set.purchase_operation_ref != purchase_ref:
            raise ValueError(
                "RequirementSet no está vinculado a la PurchaseOperation exacta"
            )
        if requirement_set.effective_date != purchase.operation_date:
            raise ValueError("RequirementSet usa otra effective_date")


__all__ = [
    "DECISION_EVIDENCE_SUFFICIENCY_EVIDENCE_SOURCE_TYPE",
    "DataSufficiencyState",
    "DecisionEvidenceRequirementSet",
    "DecisionEvidenceSufficiencyObservation",
    "DecisionEvidenceSufficiencyProducer",
    "RequirementClassification",
    "RequirementEvidenceBinding",
    "decision_evidence_purchase_ref",
    "decision_evidence_requirement_set_ref",
    "decision_evidence_sufficiency_ref",
]
