"""Provenance-safe factual carrier and producer for R-DAT-001.

The producer only binds explicit source metadata to the selected data snapshot.
It does not evaluate freshness, resolve parameters, inspect Evidence.captured_at,
or derive timestamps from identifiers.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from eios.core.models import DecisionContext, PurchaseOperation


DataFreshnessState = Literal[
    "AVAILABLE",
    "NOT_EVIDENCED",
    "CONFLICTING_DATA",
    "NOT_DETERMINABLE",
]

DATA_SNAPSHOT_FRESHNESS_EVIDENCE_SOURCE_TYPE = "DataSnapshotFreshnessEvidence"


def data_snapshot_purchase_ref(purchase: PurchaseOperation) -> str:
    if not isinstance(purchase, PurchaseOperation):
        raise TypeError("purchase debe ser PurchaseOperation")
    payload = json.dumps(
        purchase.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return f"data_snapshot_purchase:{hashlib.sha256(payload).hexdigest()}"


class DataSnapshotFreshnessObservation(BaseModel):
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
    evaluation_date: date
    source_updated_date: date | None = None
    state: DataFreshnessState
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
    def validate_state_date(self) -> "DataSnapshotFreshnessObservation":
        if self.state == "AVAILABLE":
            if self.source_updated_date is None:
                raise ValueError("AVAILABLE requiere source_updated_date")
        elif self.source_updated_date is not None:
            raise ValueError("Solo AVAILABLE puede publicar source_updated_date")
        return self


def data_snapshot_freshness_ref(observation: DataSnapshotFreshnessObservation) -> str:
    if not isinstance(observation, DataSnapshotFreshnessObservation):
        raise TypeError("observation debe ser DataSnapshotFreshnessObservation")
    payload = json.dumps(
        observation.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return f"data_snapshot_freshness:{hashlib.sha256(payload).hexdigest()}"


@dataclass(frozen=True)
class DataSnapshotFreshnessProducer:
    """Build factual observations only from explicit caller-supplied metadata."""

    authority_ref: str
    methodology_ref: str

    def __post_init__(self) -> None:
        if not isinstance(self.authority_ref, str) or not self.authority_ref.strip():
            raise ValueError("authority_ref no puede estar vacío")
        if not isinstance(self.methodology_ref, str) or not self.methodology_ref.strip():
            raise ValueError("methodology_ref no puede estar vacío")

    def produce(
        self,
        *,
        purchase: PurchaseOperation,
        context: DecisionContext,
        company_scope: str,
        state: DataFreshnessState,
        source_updated_date: date | None,
        source_ref: str,
        trace_refs: tuple[str, ...] = (),
    ) -> DataSnapshotFreshnessObservation:
        if not isinstance(purchase, PurchaseOperation):
            raise TypeError("purchase debe ser PurchaseOperation")
        if not isinstance(context, DecisionContext):
            raise TypeError("context debe ser DecisionContext")
        if purchase.decision_id != context.decision_id:
            raise ValueError("PurchaseOperation y DecisionContext tienen decision_id distintos")
        if purchase.scenario_id != context.scenario_id:
            raise ValueError("PurchaseOperation y DecisionContext tienen scenario_id distintos")
        if not isinstance(company_scope, str) or not company_scope.strip():
            raise ValueError("company_scope no puede estar vacío")
        if not isinstance(source_ref, str) or not source_ref.strip():
            raise ValueError("source_ref no puede estar vacío")
        if type(trace_refs) is not tuple:
            raise TypeError("trace_refs debe ser tuple")

        return DataSnapshotFreshnessObservation(
            decision_id=context.decision_id,
            scenario_id=context.scenario_id,
            data_snapshot_id=context.data_snapshot_id,
            company_scope=company_scope,
            purchase_operation_ref=data_snapshot_purchase_ref(purchase),
            evaluation_date=purchase.operation_date,
            source_updated_date=source_updated_date,
            state=state,
            source_ref=source_ref,
            authority_ref=self.authority_ref,
            methodology_ref=self.methodology_ref,
            trace_refs=trace_refs,
        )


__all__ = [
    "DATA_SNAPSHOT_FRESHNESS_EVIDENCE_SOURCE_TYPE",
    "DataFreshnessState",
    "DataSnapshotFreshnessObservation",
    "DataSnapshotFreshnessProducer",
    "data_snapshot_freshness_ref",
    "data_snapshot_purchase_ref",
]
