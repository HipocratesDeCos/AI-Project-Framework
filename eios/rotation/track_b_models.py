"""Authorized ROT001 Track B factual carriers."""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field, model_validator

from .source_models import CoverageState


ROTATION_METRIC_UNIT = "eventos/día"


class RotationMetricSourceEvidence(BaseModel):
    """Complete upstream source for the authorized Track B frequency metric."""

    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    article_id: str = Field(min_length=1, max_length=128)
    window_start: date
    window_end: date
    source_ref: str = Field(min_length=1, max_length=256)
    source_semantics_ref: str = Field(min_length=1, max_length=256)
    completeness_ref: str = Field(min_length=1, max_length=256)
    valid_sale_evidence_refs: tuple[str, ...] = ()
    trace_refs: tuple[str, ...] = ()
    coverage_state: CoverageState

    @model_validator(mode="after")
    def validate_source(self) -> "RotationMetricSourceEvidence":
        if self.window_start > self.window_end:
            raise ValueError("window_start no puede ser posterior a window_end")
        if len(self.valid_sale_evidence_refs) != len(set(self.valid_sale_evidence_refs)):
            raise ValueError("valid_sale_evidence_refs no puede contener duplicados")
        if len(self.trace_refs) != len(set(self.trace_refs)):
            raise ValueError("trace_refs no puede contener duplicados")
        return self


class RotationMetricEvidence(BaseModel):
    """Derived, immutable Track B metric carrier."""

    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    article_id: str = Field(min_length=1, max_length=128)
    evaluation_date: date
    window_start: date
    window_end: date
    window_authority_ref: str = Field(min_length=1, max_length=256)
    threshold_authority_ref: str = Field(min_length=1, max_length=256)
    source_ref: str = Field(min_length=1, max_length=256)
    source_semantics_ref: str = Field(min_length=1, max_length=256)
    completeness_ref: str = Field(min_length=1, max_length=256)
    valid_sale_event_count: int = Field(ge=0)
    rotation_metric: Decimal = Field(ge=0)
    metric_unit: str = ROTATION_METRIC_UNIT
    evidence_refs: tuple[str, ...] = ()
    trace_refs: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_metric(self) -> "RotationMetricEvidence":
        if self.metric_unit != ROTATION_METRIC_UNIT:
            raise ValueError("metric_unit no canónica")
        if self.window_start > self.window_end:
            raise ValueError("window_start no puede ser posterior a window_end")
        if self.window_end > self.evaluation_date:
            raise ValueError("window_end no puede ser posterior a evaluation_date")
        if not self.rotation_metric.is_finite():
            raise ValueError("rotation_metric debe ser finita")
        if len(self.evidence_refs) != len(set(self.evidence_refs)):
            raise ValueError("evidence_refs no puede contener duplicados")
        if len(self.trace_refs) != len(set(self.trace_refs)):
            raise ValueError("trace_refs no puede contener duplicados")
        return self


__all__ = [
    "ROTATION_METRIC_UNIT",
    "RotationMetricEvidence",
    "RotationMetricSourceEvidence",
]
