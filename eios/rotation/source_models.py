"""Authorized factual carriers for ROT002 completion package v0.1."""
from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


CoverageState = Literal["COMPLETE", "PARTIAL", "NOT_DEMONSTRATED", "CONFLICTING"]
RotationExceptionType = Literal[
    "CONFIRMED_ORDER",
    "PLANNED_CAMPAIGN",
    "STRATEGIC_OPERATION",
    "EXPLICIT_BUSINESS_DECISION",
]
RotationExceptionState = Literal[
    "PRESENT",
    "NOT_PRESENT",
    "NOT_DETERMINABLE",
    "CONFLICTING",
]


class SalesActivitySourceEvidence(BaseModel):
    """Upstream factual support from an already-qualified sales source."""

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
    def validate_source(self) -> "SalesActivitySourceEvidence":
        if self.window_start > self.window_end:
            raise ValueError("window_start no puede ser posterior a window_end")
        for name, values in (
            ("valid_sale_evidence_refs", self.valid_sale_evidence_refs),
            ("trace_refs", self.trace_refs),
        ):
            if len(values) != len(set(values)):
                raise ValueError(f"{name} no puede contener duplicados")
            if any(not value.strip() for value in values):
                raise ValueError(f"{name} no puede contener referencias vacías")
        return self


class RotationExceptionDetermination(BaseModel):
    """One explicit determination in the exhaustive ROT002 MVP exception universe."""

    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    exception_type: RotationExceptionType
    state: RotationExceptionState
    evidence_refs: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_refs(self) -> "RotationExceptionDetermination":
        if len(self.evidence_refs) != len(set(self.evidence_refs)):
            raise ValueError("evidence_refs no puede contener duplicados")
        if any(not value.strip() for value in self.evidence_refs):
            raise ValueError("evidence_refs no puede contener referencias vacías")
        return self


class RotationExceptionEvidence(BaseModel):
    """Factual exception carrier for R-ROT-002."""

    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    article_id: str = Field(min_length=1, max_length=128)
    evaluation_date: date
    exception_scope_ref: str = Field(min_length=1, max_length=256)
    determinations: tuple[RotationExceptionDetermination, ...]
    evidence_refs: tuple[str, ...] = ()
    trace_refs: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_exception_carrier(self) -> "RotationExceptionEvidence":
        types = tuple(item.exception_type for item in self.determinations)
        if len(types) != len(set(types)):
            raise ValueError("determinations no puede duplicar exception_type")
        for name, values in (
            ("evidence_refs", self.evidence_refs),
            ("trace_refs", self.trace_refs),
        ):
            if len(values) != len(set(values)):
                raise ValueError(f"{name} no puede contener duplicados")
            if any(not value.strip() for value in values):
                raise ValueError(f"{name} no puede contener referencias vacías")
        return self


ROT002_MVP_EXCEPTION_TYPES: tuple[RotationExceptionType, ...] = (
    "CONFIRMED_ORDER",
    "PLANNED_CAMPAIGN",
    "STRATEGIC_OPERATION",
    "EXPLICIT_BUSINESS_DECISION",
)


__all__ = [
    "CoverageState",
    "ROT002_MVP_EXCEPTION_TYPES",
    "RotationExceptionDetermination",
    "RotationExceptionEvidence",
    "RotationExceptionState",
    "RotationExceptionType",
    "SalesActivitySourceEvidence",
]
