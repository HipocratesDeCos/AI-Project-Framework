"""Authorized commercial factual carriers for COM001/COM002."""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


DiscountOpportunityState = Literal[
    "AVAILABLE",
    "NOT_AVAILABLE",
    "NOT_DETERMINABLE",
    "CONFLICTING",
]
DiscountApplicabilityState = Literal[
    "CONFIRMED",
    "CONDITIONAL",
    "NOT_CONFIRMED",
    "NOT_DETERMINABLE",
    "CONFLICTING",
]
RappelApplicabilityState = Literal[
    "CONFIRMED",
    "CONDITIONAL",
    "NOT_APPLICABLE",
    "NOT_DETERMINABLE",
    "CONFLICTING",
]


class DiscountOpportunityEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    article_id: str = Field(min_length=1, max_length=128)
    supplier_id: str = Field(min_length=1, max_length=128)
    evaluation_date: date
    opportunity_ref: str = Field(min_length=1, max_length=256)
    applicability_ref: str = Field(min_length=1, max_length=256)
    opportunity_state: DiscountOpportunityState
    applicability_state: DiscountApplicabilityState
    evidence_refs: tuple[str, ...] = ()
    trace_refs: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_refs(self) -> "DiscountOpportunityEvidence":
        if len(self.evidence_refs) != len(set(self.evidence_refs)):
            raise ValueError("evidence_refs no puede contener duplicados")
        if len(self.trace_refs) != len(set(self.trace_refs)):
            raise ValueError("trace_refs no puede contener duplicados")
        return self


class RappelApplicabilityEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    article_id: str = Field(min_length=1, max_length=128)
    supplier_id: str = Field(min_length=1, max_length=128)
    evaluation_date: date
    agreement_ref: str = Field(min_length=1, max_length=256)
    applicability_ref: str = Field(min_length=1, max_length=256)
    economic_basis_ref: str = Field(min_length=1, max_length=256)
    applicability_state: RappelApplicabilityState
    eligible_base_amount: Decimal = Field(ge=0)
    rebate_rate_pct: Decimal = Field(gt=0, le=100)
    currency: str = Field(min_length=3, max_length=3)
    evidence_refs: tuple[str, ...] = ()
    trace_refs: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_rappel(self) -> "RappelApplicabilityEvidence":
        for field_name in ("eligible_base_amount", "rebate_rate_pct"):
            value = getattr(self, field_name)
            if not value.is_finite():
                raise ValueError(f"{field_name} debe ser finito")
        if len(self.evidence_refs) != len(set(self.evidence_refs)):
            raise ValueError("evidence_refs no puede contener duplicados")
        if len(self.trace_refs) != len(set(self.trace_refs)):
            raise ValueError("trace_refs no puede contener duplicados")
        return self


class RappelEffectiveCostEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    article_id: str = Field(min_length=1, max_length=128)
    supplier_id: str = Field(min_length=1, max_length=128)
    evaluation_date: date
    agreement_ref: str = Field(min_length=1, max_length=256)
    purchase_gross_amount: Decimal = Field(ge=0)
    eligible_base_amount: Decimal = Field(ge=0)
    rebate_rate_pct: Decimal = Field(gt=0, le=100)
    rebate_amount: Decimal = Field(ge=0)
    effective_cost_after_rappel: Decimal = Field(ge=0)
    currency: str = Field(min_length=3, max_length=3)
    evidence_refs: tuple[str, ...] = ()
    trace_refs: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_cost(self) -> "RappelEffectiveCostEvidence":
        for field_name in (
            "purchase_gross_amount",
            "eligible_base_amount",
            "rebate_rate_pct",
            "rebate_amount",
            "effective_cost_after_rappel",
        ):
            value = getattr(self, field_name)
            if not value.is_finite():
                raise ValueError(f"{field_name} debe ser finito")
        if self.rebate_amount > self.purchase_gross_amount:
            raise ValueError("rebate_amount no puede superar purchase_gross_amount")
        return self


__all__ = [
    "DiscountApplicabilityState",
    "DiscountOpportunityEvidence",
    "DiscountOpportunityState",
    "RappelApplicabilityEvidence",
    "RappelApplicabilityState",
    "RappelEffectiveCostEvidence",
]
