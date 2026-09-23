"""Factual Rotation Track A carrier for the R-ROT-002 sales-activity window.

This module materializes only the closed SalesActivityWindowEvidence contract.
It does not calculate a rotation metric, evaluate R-ROT-002, apply exceptions,
produce an Assessment or call CRC.
"""
from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


SalesActivityState = Literal[
    "SALES_ACTIVITY_PRESENT",
    "ZERO_VALID_SALES_DEMONSTRATED",
    "NOT_EVIDENCED",
    "CONFLICTING_DATA",
    "NOT_DETERMINABLE",
]


class SalesActivityWindowEvidence(BaseModel):
    """Immutable factual carrier defined by Rotation methodology v0.3."""

    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    article_id: str = Field(min_length=1, max_length=128)
    evaluation_date: date
    window_start: date
    window_end: date
    window_authority_ref: str = Field(min_length=1, max_length=256)
    source_ref: str = Field(min_length=1, max_length=256)
    source_semantics_ref: str = Field(min_length=1, max_length=256)
    completeness_ref: str = Field(min_length=1, max_length=256)
    activity_state: SalesActivityState
    evidence_refs: tuple[str, ...] = ()
    trace_refs: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_window_and_refs(self) -> "SalesActivityWindowEvidence":
        if self.window_start > self.window_end:
            raise ValueError("window_start no puede ser posterior a window_end")
        if self.window_end > self.evaluation_date:
            raise ValueError("window_end no puede ser posterior a evaluation_date")
        if len(self.evidence_refs) != len(set(self.evidence_refs)):
            raise ValueError("evidence_refs no puede contener duplicados")
        if len(self.trace_refs) != len(set(self.trace_refs)):
            raise ValueError("trace_refs no puede contener duplicados")
        if any(not value.strip() for value in self.evidence_refs):
            raise ValueError("evidence_refs no puede contener referencias vacías")
        if any(not value.strip() for value in self.trace_refs):
            raise ValueError("trace_refs no puede contener referencias vacías")
        return self


__all__ = ["SalesActivityState", "SalesActivityWindowEvidence"]
