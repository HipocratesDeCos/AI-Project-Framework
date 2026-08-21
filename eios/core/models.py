"""Core domain models for the EIOS purchase-operation MVP.

Sprint 1 scope:
- Represent a purchase operation with an explicit, validated contract.
- Keep the model independent from rule implementation and persistence.
- Preserve identifiers required later for reproducibility and evidence.

This module deliberately does not resolve the open F3 parameter-dependency GAPs.
Those decisions belong to the rule/dependency layer and must not be inferred here.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


Currency = Literal["EUR"]


class PurchaseOperation(BaseModel):
    """Canonical input contract for one purchase operation."""

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


class EvaluationContext(BaseModel):
    """Execution metadata used to make an evaluation reproducible."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    decision_id: str = Field(min_length=1, max_length=64)
    scenario_id: str = Field(min_length=1, max_length=64)
    rules_version: str = Field(min_length=1, max_length=64)
    parameters_version: str = Field(min_length=1, max_length=64)
    data_snapshot_id: str = Field(min_length=1, max_length=64)


class QualityStatus(BaseModel):
    """Minimal Quality & Trust Gate result for Sprint 1."""

    model_config = ConfigDict(extra="forbid")

    status: Literal["PASS", "FAIL", "INSUFFICIENT"]
    score: Decimal | None = Field(default=None, ge=0, le=1, decimal_places=4)
    reasons: list[str] = Field(default_factory=list)


class EvidenceRef(BaseModel):
    """Reference to evidence supporting an evaluated result."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    evidence_id: str = Field(min_length=1, max_length=64)
    source_type: str = Field(min_length=1, max_length=64)
    source_ref: str = Field(min_length=1, max_length=256)
    captured_at: date


class PurchaseEvaluation(BaseModel):
    """Stable result envelope returned by the MVP evaluation pipeline."""

    model_config = ConfigDict(extra="forbid")

    context: EvaluationContext
    purchase: PurchaseOperation
    quality: QualityStatus
    evidence: list[EvidenceRef] = Field(default_factory=list)


__all__ = [
    "Currency",
    "EvidenceRef",
    "EvaluationContext",
    "PurchaseEvaluation",
    "PurchaseOperation",
    "QualityStatus",
]
