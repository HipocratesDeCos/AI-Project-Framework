"""Rule-specific provenance carriers for R-STK-002.

These carriers do not replace M04/M07/M08 domain models. They represent two
business facts that must already be produced and evidenced upstream before the
rule can evaluate.
"""
from __future__ import annotations

import hashlib
import json
from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from eios.core.models import PurchaseOperation


ProjectedCoverageState = Literal[
    "FINITE",
    "UNBOUNDED",
    "NOT_EVIDENCED",
    "CONFLICTING_DATA",
    "NOT_DETERMINABLE",
]

JustifiedNeedStatus = Literal[
    "PRESENT",
    "ABSENT",
    "NOT_EVIDENCED",
    "CONFLICTING_DATA",
    "NOT_DETERMINABLE",
]

PROJECTED_COVERAGE_EVIDENCE_SOURCE_TYPE = "ProjectedCoverageAfterPurchaseEvidence"
JUSTIFIED_NEED_EVIDENCE_SOURCE_TYPE = "JustifiedNeedStateEvidence"


def stock_purchase_operation_ref(purchase: PurchaseOperation) -> str:
    if not isinstance(purchase, PurchaseOperation):
        raise TypeError("purchase debe ser PurchaseOperation")
    payload = json.dumps(
        purchase.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return f"stock_purchase_operation:{hashlib.sha256(payload).hexdigest()}"


class _STK002CarrierBase(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    decision_id: str = Field(min_length=1, max_length=64)
    scenario_id: str = Field(min_length=1, max_length=64)
    data_snapshot_id: str = Field(min_length=1, max_length=64)
    company_scope: str = Field(min_length=1, max_length=128)
    article_id: str = Field(min_length=1, max_length=128)
    evaluation_date: date
    purchase_operation_ref: str = Field(min_length=1, max_length=128)
    source_ref: str = Field(min_length=1, max_length=256)
    authority_ref: str = Field(min_length=1, max_length=256)
    trace_refs: tuple[str, ...] = ()

    @field_validator("trace_refs")
    @classmethod
    def validate_traces(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if len(value) != len(set(value)):
            raise ValueError("trace_refs no puede contener duplicados")
        if any(not item.strip() for item in value):
            raise ValueError("trace_refs no puede contener referencias vacías")
        return value


class ProjectedCoverageAfterPurchase(_STK002CarrierBase):
    state: ProjectedCoverageState
    coverage_days: Decimal | None = None

    @model_validator(mode="after")
    def validate_state(self) -> "ProjectedCoverageAfterPurchase":
        if self.state == "FINITE":
            if self.coverage_days is None:
                raise ValueError("FINITE requiere coverage_days")
            if not self.coverage_days.is_finite():
                raise ValueError("coverage_days debe ser finito")
            if self.coverage_days < 0:
                raise ValueError("coverage_days no puede ser negativo")
        elif self.coverage_days is not None:
            raise ValueError("Solo FINITE puede publicar coverage_days")
        return self


class JustifiedNeedState(_STK002CarrierBase):
    state: JustifiedNeedStatus


def _carrier_ref(prefix: str, carrier: BaseModel) -> str:
    payload = json.dumps(
        carrier.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return f"{prefix}:{hashlib.sha256(payload).hexdigest()}"


def projected_coverage_ref(carrier: ProjectedCoverageAfterPurchase) -> str:
    if not isinstance(carrier, ProjectedCoverageAfterPurchase):
        raise TypeError("carrier debe ser ProjectedCoverageAfterPurchase")
    return _carrier_ref("projected_coverage_after_purchase", carrier)


def justified_need_ref(carrier: JustifiedNeedState) -> str:
    if not isinstance(carrier, JustifiedNeedState):
        raise TypeError("carrier debe ser JustifiedNeedState")
    return _carrier_ref("justified_need_state", carrier)


__all__ = [
    "JUSTIFIED_NEED_EVIDENCE_SOURCE_TYPE",
    "PROJECTED_COVERAGE_EVIDENCE_SOURCE_TYPE",
    "JustifiedNeedState",
    "JustifiedNeedStatus",
    "ProjectedCoverageAfterPurchase",
    "ProjectedCoverageState",
    "justified_need_ref",
    "projected_coverage_ref",
    "stock_purchase_operation_ref",
]
