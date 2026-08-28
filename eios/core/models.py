"""Canonical C0 domain contracts for the EIOS procurement MVP.

C0 scope is deliberately limited to:
Input Contract -> DecisionContext -> Evidence -> Evidence Validation
-> Rule -> Assessment -> Trace.

No decision, scenario engine, negotiation, ladder, CRC, persistence, API,
LLM or external execution dependency is defined here.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


Currency = Literal["EUR"]
EvidenceState = Literal["DEMONSTRATED", "GAP"]
EvidenceValidationStatus = Literal["VALID", "INVALID"]
AssessmentStatus = Literal["EVALUABLE", "NOT_EVALUABLE"]
AssessmentOutcome = Literal["TRUE", "FALSE"]


class PurchaseOperation(BaseModel):
    """Existing purchase input contract retained as the C0 input payload."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    decision_id: str = Field(min_length=1, max_length=64)
    scenario_id: str = Field(min_length=1, max_length=64)
    article_id: str = Field(min_length=1, max_length=64)
    supplier_id: str = Field(min_length=1, max_length=64)
    quantity: Decimal = Field(gt=0)
    unit_price: Decimal = Field(ge=0, decimal_places=4)
    currency: Currency = "EUR"
    operation_date: date

    @field_validator("quantity", "unit_price")
    @classmethod
    def reject_non_finite_decimals(cls, value: Decimal) -> Decimal:
        if not value.is_finite():
            raise ValueError("El valor decimal debe ser finito")
        return value


InputContract = PurchaseOperation


class DecisionContext(BaseModel):
    """Execution identity required to reproduce a C0 evaluation."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    decision_id: str = Field(min_length=1, max_length=64)
    scenario_id: str = Field(min_length=1, max_length=64)
    rules_version: str = Field(min_length=1, max_length=64)
    parameters_version: str = Field(min_length=1, max_length=64)
    data_snapshot_id: str = Field(min_length=1, max_length=64)

    @model_validator(mode="after")
    def context_ids_are_present(self) -> "DecisionContext":
        return self


# Backward-compatible name for the pre-C0 Sprint 1 model.
EvaluationContext = DecisionContext


class Evidence(BaseModel):
    """Evidence item presented to a rule evaluation."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    evidence_id: str = Field(min_length=1, max_length=64)
    source_type: str = Field(min_length=1, max_length=64)
    source_ref: str = Field(min_length=1, max_length=256)
    captured_at: date
    state: EvidenceState
    demonstration_ref: str | None = Field(default=None, max_length=256)

    @model_validator(mode="after")
    def validate_demonstration_state(self) -> "Evidence":
        if self.state == "DEMONSTRATED" and not self.demonstration_ref:
            raise ValueError("La evidencia DEMONSTRATED requiere demonstration_ref")
        return self


# Compatibility alias for the pre-C0 reference-only model.
EvidenceRef = Evidence


class EvidenceValidation(BaseModel):
    """Deterministic validation result for one evidence item."""

    model_config = ConfigDict(extra="forbid")

    evidence_id: str = Field(min_length=1, max_length=64)
    status: EvidenceValidationStatus
    reason: str = Field(min_length=1, max_length=256)


class Rule(BaseModel):
    """Minimal C0 rule contract.

    The executable predicate is deliberately supplied by the rule engine,
    not embedded in this data contract. This keeps the contract declarative
    and prevents C0 from introducing a rule DSL or persistence dependency.
    """

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    rule_id: str = Field(min_length=1, max_length=64)
    version: str = Field(min_length=1, max_length=64)
    requires_evidence: bool = True


class Assessment(BaseModel):
    """Result of applying one rule after evidence validation."""

    model_config = ConfigDict(extra="forbid")

    rule_id: str = Field(min_length=1, max_length=64)
    status: AssessmentStatus
    outcome: AssessmentOutcome | None = None
    evidence_ids: list[str] = Field(default_factory=list)
    reason: str = Field(min_length=1, max_length=256)

    @model_validator(mode="after")
    def enforce_status_outcome_invariant(self) -> "Assessment":
        if self.status == "NOT_EVALUABLE" and self.outcome is not None:
            raise ValueError("NOT_EVALUABLE no puede tener outcome")
        if self.status == "EVALUABLE" and self.outcome is None:
            raise ValueError("EVALUABLE requiere outcome")
        return self


class Trace(BaseModel):
    """Immutable-in-practice C0 trace record linking the evaluation chain."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    trace_id: str = Field(min_length=1, max_length=128)
    decision_id: str = Field(min_length=1, max_length=64)
    scenario_id: str = Field(min_length=1, max_length=64)
    rule_id: str = Field(min_length=1, max_length=64)
    assessment_status: AssessmentStatus
    assessment_outcome: AssessmentOutcome | None = None
    evidence_ids: tuple[str, ...] = ()
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class QualityStatus(BaseModel):
    """Legacy Sprint 1 quality result retained for compatibility."""

    model_config = ConfigDict(extra="forbid")

    status: Literal["PASS", "FAIL", "INSUFFICIENT"]
    score: Decimal | None = Field(default=None, ge=0, le=1, decimal_places=4)
    reasons: list[str] = Field(default_factory=list)


class PurchaseEvaluation(BaseModel):
    """Legacy Sprint 1 envelope retained for compatibility."""

    model_config = ConfigDict(extra="forbid")

    context: DecisionContext
    purchase: PurchaseOperation
    quality: QualityStatus
    evidence: list[Evidence] = Field(default_factory=list)


__all__ = [
    "Assessment",
    "AssessmentOutcome",
    "AssessmentStatus",
    "Currency",
    "DecisionContext",
    "Evidence",
    "EvidenceRef",
    "EvidenceState",
    "EvidenceValidation",
    "EvidenceValidationStatus",
    "EvaluationContext",
    "InputContract",
    "PurchaseEvaluation",
    "PurchaseOperation",
    "QualityStatus",
    "Rule",
    "Trace",
]
