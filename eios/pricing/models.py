"""Physical C1 contracts for EIOS Price Intelligence."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from eios.core.models import DecisionContext, PurchaseOperation

ComparabilityStatus = Literal["COMPARABLE", "NO_COMPARABLE", "PENDING"]
RepresentativenessStatus = Literal["REPRESENTATIVE", "NON_REPRESENTATIVE", "INDETERMINATE"]
SufficiencyStatus = Literal["SUFFICIENT", "LIMITED", "NOT_JUSTIFIABLE"]
PRStatus = Literal["PR_AVAILABLE", "PR_LIMITED", "PR_NOT_JUSTIFIABLE"]
AggregationMethod = Literal["MEDIAN_UNWEIGHTED"]


class PriceReference(BaseModel):
    """Economic price observation supplied to C1."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    source_transaction_id: str = Field(min_length=1, max_length=128)
    article_identity: str = Field(min_length=1, max_length=128)
    supplier_identity: str | None = Field(default=None, max_length=128)
    quantity: Decimal = Field(gt=0)
    unit: str = Field(min_length=1, max_length=32)
    unit_price: Decimal = Field(ge=0, decimal_places=4)
    currency: str = Field(min_length=3, max_length=3)
    operation_date: date
    commercial_conditions: str | None = Field(default=None, max_length=512)
    evidence_refs: tuple[str, ...] = ()

    @model_validator(mode="after")
    def finite_values(self) -> "PriceReference":
        if not self.unit_price.is_finite() or not self.quantity.is_finite():
            raise ValueError("Los valores de precio y cantidad deben ser finitos")
        return self


class NormalizationRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    field: str = Field(min_length=1, max_length=64)
    original_value: str
    normalized_value: str
    rule_reference: str = Field(min_length=1, max_length=128)
    trace_reference: str = Field(min_length=1, max_length=128)


class PriceReferenceAssessment(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reference_id: str = Field(min_length=1, max_length=128)
    comparability: ComparabilityStatus
    representativeness: RepresentativenessStatus
    normalized_unit_price: Decimal | None = Field(default=None, ge=0, decimal_places=4)
    normalization: tuple[NormalizationRecord, ...] = ()
    limitation_refs: tuple[str, ...] = ()


class PriceIntelligenceInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decision_context: DecisionContext
    purchase_operation: PurchaseOperation
    references: tuple[PriceReference, ...] = ()
    methodology_version: str = Field(min_length=1, max_length=64)

    @model_validator(mode="after")
    def context_matches_purchase(self) -> "PriceIntelligenceInput":
        if self.decision_context.decision_id != self.purchase_operation.decision_id:
            raise ValueError("decision_id no coincide entre contexto y operación")
        if self.decision_context.scenario_id != self.purchase_operation.scenario_id:
            raise ValueError("scenario_id no coincide entre contexto y operación")
        return self


class PriceCounts(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    n_raw: int = Field(ge=0)
    n_unique: int = Field(ge=0)
    n_comparable: int = Field(ge=0)
    n_representative: int = Field(ge=0)
    n_selected: int = Field(ge=0)

    @model_validator(mode="after")
    def monotonic_counts(self) -> "PriceCounts":
        values = (self.n_raw, self.n_unique, self.n_comparable, self.n_representative, self.n_selected)
        if any(a < b for a, b in zip(values, values[1:])):
            raise ValueError("Los conteos C1 deben ser monótonos no crecientes")
        return self


class PriceIntelligenceResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    decision_id: str
    scenario_id: str
    data_snapshot_id: str
    methodology_version: str
    pr_value: Decimal | None = Field(default=None, ge=0, decimal_places=4)
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    pr_status: PRStatus
    pr_limitations: tuple[str, ...] = ()
    reference_set: tuple[str, ...] = ()
    counts: PriceCounts
    aggregation_method: AggregationMethod
    trace_references: tuple[str, ...] = ()

    @model_validator(mode="after")
    def enforce_result_invariants(self) -> "PriceIntelligenceResult":
        if self.pr_status == "PR_NOT_JUSTIFIABLE" and self.pr_value is not None:
            raise ValueError("PR_NOT_JUSTIFIABLE requiere pr_value=null")
        if self.pr_value is not None and self.currency is None:
            raise ValueError("Un PR disponible requiere moneda")
        if self.counts.n_selected == 0 and self.pr_status != "PR_NOT_JUSTIFIABLE":
            raise ValueError("N_SELECTED=0 requiere PR_NOT_JUSTIFIABLE")
        if self.counts.n_selected == 1 and self.pr_status == "PR_AVAILABLE":
            raise ValueError("N_SELECTED=1 no puede producir PR_AVAILABLE")
        return self


__all__ = [
    "AggregationMethod", "ComparabilityStatus", "NormalizationRecord",
    "PRStatus", "PriceCounts", "PriceIntelligenceInput", "PriceIntelligenceResult",
    "PriceReference", "PriceReferenceAssessment", "RepresentativenessStatus",
    "SufficiencyStatus",
]
