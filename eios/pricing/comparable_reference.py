"""Independent comparable-price reference carrier for R-PRE-001.

Rules consumes one already-selected comparable reference. This module does not
select the latest purchase, aggregate Price Intelligence outputs, or normalize
economic terms implicitly.
"""
from __future__ import annotations

import hashlib
import json
from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from eios.core.models import PurchaseOperation


ComparabilityState = Literal[
    "COMPARABLE",
    "NOT_COMPARABLE",
    "NOT_EVIDENCED",
    "CONFLICTING_DATA",
    "NOT_DETERMINABLE",
]

COMPARABLE_PRICE_REFERENCE_EVIDENCE_SOURCE_TYPE = "ComparablePriceReferenceEvidence"


def comparable_price_purchase_ref(purchase: PurchaseOperation) -> str:
    if not isinstance(purchase, PurchaseOperation):
        raise TypeError("purchase debe ser PurchaseOperation")
    payload = json.dumps(
        purchase.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return f"comparable_price_purchase:{hashlib.sha256(payload).hexdigest()}"


class ComparablePriceReference(BaseModel):
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
    currency: str = Field(min_length=3, max_length=3)
    purchase_operation_ref: str = Field(min_length=1, max_length=128)
    reference_operation_ref: str = Field(min_length=1, max_length=256)
    reference_date: date
    reference_price: Decimal | None = None
    comparability_state: ComparabilityState
    source_ref: str = Field(min_length=1, max_length=256)
    authority_ref: str = Field(min_length=1, max_length=256)
    methodology_ref: str = Field(min_length=1, max_length=256)
    trace_refs: tuple[str, ...] = ()

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value: str) -> str:
        return value.upper()

    @field_validator("trace_refs")
    @classmethod
    def unique_trace_refs(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if len(value) != len(set(value)):
            raise ValueError("trace_refs no puede contener duplicados")
        if any(not item.strip() for item in value):
            raise ValueError("trace_refs no puede contener referencias vacías")
        return value

    @model_validator(mode="after")
    def validate_reference_price(self) -> "ComparablePriceReference":
        if self.comparability_state == "COMPARABLE" and self.reference_price is None:
            raise ValueError("COMPARABLE requiere reference_price")
        if self.reference_price is not None:
            if not self.reference_price.is_finite():
                raise ValueError("reference_price debe ser finito")
            if self.reference_price <= 0:
                raise ValueError("reference_price debe ser mayor que cero")
        return self


def comparable_price_reference_ref(carrier: ComparablePriceReference) -> str:
    if not isinstance(carrier, ComparablePriceReference):
        raise TypeError("carrier debe ser ComparablePriceReference")
    payload = json.dumps(
        carrier.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return f"comparable_price_reference:{hashlib.sha256(payload).hexdigest()}"


__all__ = [
    "COMPARABLE_PRICE_REFERENCE_EVIDENCE_SOURCE_TYPE",
    "ComparablePriceReference",
    "ComparabilityState",
    "comparable_price_purchase_ref",
    "comparable_price_reference_ref",
]
