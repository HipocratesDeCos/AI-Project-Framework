"""Independent temporal-reference carrier for R-HIS-001.

This module binds one already-identified historical reference to the exact
PurchaseOperation. It does not select references or consume detached Price
Intelligence temporal statuses.
"""
from __future__ import annotations

import hashlib
import json
from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from eios.core.models import PurchaseOperation


HistoricalTemporalState = Literal[
    "AVAILABLE",
    "NOT_EVIDENCED",
    "CONFLICTING_DATA",
    "NOT_DETERMINABLE",
]

HISTORICAL_REFERENCE_TEMPORAL_EVIDENCE_SOURCE_TYPE = "HistoricalReferenceTemporalEvidence"


def historical_reference_purchase_ref(purchase: PurchaseOperation) -> str:
    if not isinstance(purchase, PurchaseOperation):
        raise TypeError("purchase debe ser PurchaseOperation")
    payload = json.dumps(
        purchase.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return f"historical_reference_purchase:{hashlib.sha256(payload).hexdigest()}"


class HistoricalReferenceTemporalObservation(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    decision_id: str = Field(min_length=1, max_length=64)
    scenario_id: str = Field(min_length=1, max_length=64)
    data_snapshot_id: str = Field(min_length=1, max_length=64)
    company_scope: str = Field(min_length=1, max_length=128)
    purchase_operation_ref: str = Field(min_length=1, max_length=128)
    reference_id: str = Field(min_length=1, max_length=128)
    reference_operation_date: date | None = None
    evaluation_date: date
    state: HistoricalTemporalState
    source_ref: str = Field(min_length=1, max_length=256)
    authority_ref: str = Field(min_length=1, max_length=256)
    methodology_ref: str = Field(min_length=1, max_length=256)
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
    def available_requires_date(self) -> "HistoricalReferenceTemporalObservation":
        if self.state == "AVAILABLE" and self.reference_operation_date is None:
            raise ValueError("AVAILABLE requiere reference_operation_date")
        return self


def historical_reference_temporal_ref(
    carrier: HistoricalReferenceTemporalObservation,
) -> str:
    if not isinstance(carrier, HistoricalReferenceTemporalObservation):
        raise TypeError("carrier debe ser HistoricalReferenceTemporalObservation")
    payload = json.dumps(
        carrier.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return f"historical_reference_temporal:{hashlib.sha256(payload).hexdigest()}"


__all__ = [
    "HISTORICAL_REFERENCE_TEMPORAL_EVIDENCE_SOURCE_TYPE",
    "HistoricalReferenceTemporalObservation",
    "HistoricalTemporalState",
    "historical_reference_purchase_ref",
    "historical_reference_temporal_ref",
]
