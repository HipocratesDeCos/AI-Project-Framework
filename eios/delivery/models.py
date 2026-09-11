"""Physical contracts for the EIOS delivery/stockout factual analyzer.

This module materializes the closed ENT analyzer contract v0.3.2. It owns
factual inputs and analytical results only. Rules, Assessment, CRC,
persistence and final purchase authority remain outside ENT.
"""
from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from eios.stock.models import StockProjectionResult


BaselineQualificationState = Literal["KNOWN", "CONFLICTING_DATA", "NOT_DETERMINABLE"]
DeliveryTimingEvidenceState = Literal["KNOWN", "NOT_EVIDENCED", "CONFLICTING_DATA", "NOT_DETERMINABLE"]
DeliveryAnalysisState = Literal[
    "LATE_DELIVERY_DEMONSTRATED",
    "NOT_LATE_DEMONSTRATED",
    "NOT_LATE_WITHIN_EVIDENCED_HORIZON",
    "NOT_EVIDENCED",
    "CONFLICTING_DATA",
    "NOT_DETERMINABLE",
]
DeliveryLimitationCode = Literal[
    "SAME_DAY_ORDER_NOT_DEMONSTRATED",
    "DELIVERY_BEYOND_STK_HORIZON",
    "PAST_DELIVERY_DATE_APPLICABILITY_UNPROVEN",
]


def _validate_refs(values: tuple[str, ...], field: str) -> None:
    if any(not value.strip() for value in values):
        raise ValueError(f"{field} no puede contener referencias vacías")
    if len(values) != len(set(values)):
        raise ValueError(f"{field} no puede contener duplicados")


class FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, frozen=True)


class BaselineStockoutQualification(FrozenModel):
    """Traceable qualification that a stock projection is the baseline without the evaluated purchase."""

    decision_id: str = Field(min_length=1, max_length=64)
    article_id: str = Field(min_length=1, max_length=128)
    evaluation_date: date
    evaluated_purchase_ref: str = Field(min_length=1, max_length=256)
    baseline_projection_ref: str = Field(min_length=1, max_length=256)
    projection: StockProjectionResult
    state: BaselineQualificationState
    baseline_relation_ref: str | None = Field(default=None, min_length=1, max_length=256)
    projection_provenance_ref: str | None = Field(default=None, min_length=1, max_length=256)
    purchase_exclusion_ref: str | None = Field(default=None, min_length=1, max_length=256)
    evidence_refs: tuple[str, ...] = ()
    unresolved_refs: tuple[str, ...] = ()
    issue_refs: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()
    trace_refs: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_qualification(self) -> "BaselineStockoutQualification":
        for field in ("evidence_refs", "unresolved_refs", "issue_refs", "limitations", "trace_refs"):
            _validate_refs(getattr(self, field), field)

        identity = self.projection.identity
        if self.decision_id != identity.decision_id:
            raise ValueError("Baseline decision_id incompatible con StockProjectionResult")
        if self.article_id != identity.article_id:
            raise ValueError("Baseline article_id incompatible con StockProjectionResult")
        if self.evaluation_date != identity.evaluation_date:
            raise ValueError("Baseline evaluation_date incompatible con StockProjectionResult")

        if self.state == "KNOWN":
            if not all((self.baseline_relation_ref, self.projection_provenance_ref, self.purchase_exclusion_ref)):
                raise ValueError("Baseline KNOWN requiere relation/provenance/exclusion refs")
            if not (self.evidence_refs or self.trace_refs):
                raise ValueError("Baseline KNOWN requiere evidencia o traza")
            if self.unresolved_refs:
                raise ValueError("Baseline KNOWN no admite unresolved_refs")
        elif self.state == "CONFLICTING_DATA" and not (self.issue_refs or self.unresolved_refs):
            raise ValueError("Baseline CONFLICTING_DATA requiere issue_ref o unresolved_ref")
        return self


class PurchaseSpecificDeliveryTimingEvidence(FrozenModel):
    """Expected delivery timing evidence explicitly scoped to the evaluated purchase."""

    decision_id: str = Field(min_length=1, max_length=64)
    article_id: str = Field(min_length=1, max_length=128)
    supplier_id: str = Field(min_length=1, max_length=128)
    evaluation_date: date
    evaluated_purchase_ref: str = Field(min_length=1, max_length=256)
    state: DeliveryTimingEvidenceState
    expected_delivery_date: date | None = None
    delivery_semantic_ref: str | None = Field(default=None, min_length=1, max_length=256)
    purchase_applicability_ref: str | None = Field(default=None, min_length=1, max_length=256)
    source_ref: str | None = Field(default=None, min_length=1, max_length=256)
    evidence_refs: tuple[str, ...] = ()
    captured_at: date | None = None
    valid_from: date | None = None
    valid_to: date | None = None
    issue_refs: tuple[str, ...] = ()
    trace_refs: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_evidence(self) -> "PurchaseSpecificDeliveryTimingEvidence":
        for field in ("evidence_refs", "issue_refs", "trace_refs"):
            _validate_refs(getattr(self, field), field)
        if self.valid_from and self.valid_to and self.valid_to < self.valid_from:
            raise ValueError("valid_to no puede ser anterior a valid_from")

        if self.state == "KNOWN":
            if self.expected_delivery_date is None:
                raise ValueError("Delivery KNOWN requiere expected_delivery_date")
            if not all((self.delivery_semantic_ref, self.purchase_applicability_ref, self.source_ref, self.captured_at)):
                raise ValueError("Delivery KNOWN requiere semantic/applicability/source/captured_at")
            if not self.evidence_refs:
                raise ValueError("Delivery KNOWN requiere evidence_refs")
        elif self.state == "NOT_EVIDENCED":
            if self.expected_delivery_date is not None and not self.source_ref:
                raise ValueError("Delivery NOT_EVIDENCED con fecha declarada requiere source_ref")
        elif self.state == "CONFLICTING_DATA":
            if self.expected_delivery_date is not None:
                raise ValueError("Delivery CONFLICTING_DATA no publica fecha única")
            if not self.issue_refs:
                raise ValueError("Delivery CONFLICTING_DATA requiere issue_refs")
        elif self.state == "NOT_DETERMINABLE" and self.expected_delivery_date is not None:
            if not all((self.delivery_semantic_ref, self.source_ref, self.captured_at)) or not self.evidence_refs:
                raise ValueError("Delivery NOT_DETERMINABLE con fecha requiere semantic/source/evidence/captured_at")
            if self.purchase_applicability_ref is not None:
                raise ValueError("Delivery NOT_DETERMINABLE con fecha representa aplicabilidad no demostrada")
        return self


class DeliveryStockoutAnalysisInput(FrozenModel):
    """Target context plus the two factual dependencies required by ENT."""

    decision_id: str = Field(min_length=1, max_length=64)
    article_id: str = Field(min_length=1, max_length=128)
    evaluation_date: date
    evaluated_purchase_ref: str = Field(min_length=1, max_length=256)
    baseline: BaselineStockoutQualification
    delivery: PurchaseSpecificDeliveryTimingEvidence


class DeliveryStockoutAnalysisResult(FrozenModel):
    """Factual temporal relation result. This is not an Assessment."""

    decision_id: str = Field(min_length=1, max_length=64)
    article_id: str = Field(min_length=1, max_length=128)
    evaluation_date: date
    evaluated_purchase_ref: str = Field(min_length=1, max_length=256)
    supplier_id: str = Field(min_length=1, max_length=128)
    baseline_projection_ref: str = Field(min_length=1, max_length=256)
    state: DeliveryAnalysisState
    depletion_date: date | None = None
    expected_delivery_date: date | None = None
    horizon_end: date | None = None
    limitation_codes: tuple[DeliveryLimitationCode, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    unresolved_refs: tuple[str, ...] = ()
    issue_refs: tuple[str, ...] = ()
    trace_refs: tuple[str, ...] = ()
    upstream_limitations: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_result(self) -> "DeliveryStockoutAnalysisResult":
        for field in ("evidence_refs", "unresolved_refs", "issue_refs", "trace_refs", "upstream_limitations"):
            _validate_refs(getattr(self, field), field)
        if len(self.limitation_codes) != len(set(self.limitation_codes)):
            raise ValueError("limitation_codes no puede contener duplicados")

        has_same_day = "SAME_DAY_ORDER_NOT_DEMONSTRATED" in self.limitation_codes
        if has_same_day:
            if self.state != "NOT_LATE_DEMONSTRATED":
                raise ValueError("SAME_DAY_ORDER_NOT_DEMONSTRATED solo admite NOT_LATE_DEMONSTRATED")
            if self.depletion_date is None or self.expected_delivery_date != self.depletion_date:
                raise ValueError("SAME_DAY_ORDER_NOT_DEMONSTRATED requiere igualdad de fechas")

        if self.state == "LATE_DELIVERY_DEMONSTRATED":
            if self.depletion_date is None or self.expected_delivery_date is None:
                raise ValueError("LATE_DELIVERY_DEMONSTRATED requiere ambas fechas")
            if self.expected_delivery_date <= self.depletion_date:
                raise ValueError("LATE_DELIVERY_DEMONSTRATED requiere delivery > depletion")
        elif self.state == "NOT_LATE_DEMONSTRATED":
            if self.depletion_date is None or self.expected_delivery_date is None:
                raise ValueError("NOT_LATE_DEMONSTRATED requiere ambas fechas")
            if self.expected_delivery_date > self.depletion_date:
                raise ValueError("NOT_LATE_DEMONSTRATED requiere delivery <= depletion")
            same_day = self.expected_delivery_date == self.depletion_date
            if same_day != has_same_day:
                raise ValueError("SAME_DAY_ORDER_NOT_DEMONSTRATED debe coincidir exactamente con igualdad de fechas")
        elif self.state == "NOT_LATE_WITHIN_EVIDENCED_HORIZON":
            if self.expected_delivery_date is None or self.horizon_end is None:
                raise ValueError("NOT_LATE_WITHIN_EVIDENCED_HORIZON requiere delivery y horizon_end")
            if self.expected_delivery_date > self.horizon_end:
                raise ValueError("NOT_LATE_WITHIN_EVIDENCED_HORIZON exige delivery <= horizon_end")

        if "DELIVERY_BEYOND_STK_HORIZON" in self.limitation_codes:
            if self.state != "NOT_DETERMINABLE" or self.expected_delivery_date is None or self.horizon_end is None:
                raise ValueError("DELIVERY_BEYOND_STK_HORIZON requiere resultado NOT_DETERMINABLE con fechas")
            if self.expected_delivery_date <= self.horizon_end:
                raise ValueError("DELIVERY_BEYOND_STK_HORIZON requiere delivery > horizon_end")
        if "PAST_DELIVERY_DATE_APPLICABILITY_UNPROVEN" in self.limitation_codes:
            if self.state != "NOT_DETERMINABLE" or self.expected_delivery_date is None:
                raise ValueError("PAST_DELIVERY_DATE_APPLICABILITY_UNPROVEN requiere NOT_DETERMINABLE con fecha")
            if self.expected_delivery_date >= self.evaluation_date:
                raise ValueError("PAST_DELIVERY_DATE_APPLICABILITY_UNPROVEN requiere fecha anterior a evaluation_date")
        return self


__all__ = [
    "BaselineQualificationState",
    "BaselineStockoutQualification",
    "DeliveryAnalysisState",
    "DeliveryLimitationCode",
    "DeliveryStockoutAnalysisInput",
    "DeliveryStockoutAnalysisResult",
    "DeliveryTimingEvidenceState",
    "PurchaseSpecificDeliveryTimingEvidence",
]
