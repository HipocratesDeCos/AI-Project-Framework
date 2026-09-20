"""Independent recommended-price-ceiling carrier for R-PRE-003.

This module deliberately does not derive the ceiling from Price Intelligence.
PR and PMR remain separate concepts unless a future authority explicitly
defines a transformation between them.
"""
from __future__ import annotations

import hashlib
import json
from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from eios.core.models import PurchaseOperation


RecommendedPriceCeilingState = Literal[
    "AVAILABLE",
    "NOT_EVIDENCED",
    "CONFLICTING_DATA",
    "NOT_DETERMINABLE",
]

RECOMMENDED_PRICE_CEILING_EVIDENCE_SOURCE_TYPE = "RecommendedPriceCeilingEvidence"


def recommended_price_purchase_ref(purchase: PurchaseOperation) -> str:
    if not isinstance(purchase, PurchaseOperation):
        raise TypeError("purchase debe ser PurchaseOperation")
    payload = json.dumps(
        purchase.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return f"recommended_price_purchase:{hashlib.sha256(payload).hexdigest()}"


class RecommendedPriceCeiling(BaseModel):
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
    state: RecommendedPriceCeilingState
    ceiling_price: Decimal | None = None
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
    def validate_state(self) -> "RecommendedPriceCeiling":
        if self.state == "AVAILABLE":
            if self.ceiling_price is None:
                raise ValueError("AVAILABLE requiere ceiling_price")
            if not self.ceiling_price.is_finite():
                raise ValueError("ceiling_price debe ser finito")
            if self.ceiling_price < 0:
                raise ValueError("ceiling_price no puede ser negativo")
        elif self.ceiling_price is not None:
            raise ValueError("Solo AVAILABLE puede publicar ceiling_price")
        return self


def recommended_price_ceiling_ref(carrier: RecommendedPriceCeiling) -> str:
    if not isinstance(carrier, RecommendedPriceCeiling):
        raise TypeError("carrier debe ser RecommendedPriceCeiling")
    payload = json.dumps(
        carrier.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return f"recommended_price_ceiling:{hashlib.sha256(payload).hexdigest()}"


__all__ = [
    "RECOMMENDED_PRICE_CEILING_EVIDENCE_SOURCE_TYPE",
    "RecommendedPriceCeiling",
    "RecommendedPriceCeilingState",
    "recommended_price_ceiling_ref",
    "recommended_price_purchase_ref",
]
