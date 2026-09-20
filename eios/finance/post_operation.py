"""Explicit post-operation working-capital evidence carrier for R-FIN-002.

This module does not calculate accounting consequences of a purchase. It only
carries amounts supplied by an authorized source and binds them to the exact
PurchaseOperation that the source declares it has incorporated.
"""
from __future__ import annotations

import hashlib
import json
from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from eios.core.models import PurchaseOperation


POST_OPERATION_WORKING_CAPITAL_EVIDENCE_SOURCE_TYPE = (
    "PostOperationWorkingCapitalEvidence"
)


def _finite_optional(value: Decimal | None) -> Decimal | None:
    if value is not None and not value.is_finite():
        raise ValueError("Las magnitudes post-operación deben ser finitas")
    return value


class PostOperationWorkingCapitalPosition(BaseModel):
    """Accounting totals supplied for the evaluated purchase scenario."""

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
    current_assets_after_operation: Decimal | None = None
    current_liabilities_after_operation: Decimal | None = None
    post_operation_snapshot_ref: str = Field(min_length=1, max_length=256)
    source_ref: str = Field(min_length=1, max_length=256)
    authority_ref: str = Field(min_length=1, max_length=256)
    trace_refs: tuple[str, ...] = ()

    _finite_assets = field_validator("current_assets_after_operation")(
        _finite_optional
    )
    _finite_liabilities = field_validator("current_liabilities_after_operation")(
        _finite_optional
    )

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


def purchase_operation_ref(purchase: PurchaseOperation) -> str:
    """Canonical SHA-256 binding to one exact PurchaseOperation."""
    if not isinstance(purchase, PurchaseOperation):
        raise TypeError("purchase debe ser PurchaseOperation")
    payload = json.dumps(
        purchase.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return f"purchase_operation:{hashlib.sha256(payload).hexdigest()}"


def post_operation_working_capital_position_ref(
    position: PostOperationWorkingCapitalPosition,
) -> str:
    """Canonical SHA-256 binding to one exact post-operation position."""
    if not isinstance(position, PostOperationWorkingCapitalPosition):
        raise TypeError("position debe ser PostOperationWorkingCapitalPosition")
    payload = json.dumps(
        position.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return f"post_operation_working_capital:{hashlib.sha256(payload).hexdigest()}"


__all__ = [
    "POST_OPERATION_WORKING_CAPITAL_EVIDENCE_SOURCE_TYPE",
    "PostOperationWorkingCapitalPosition",
    "post_operation_working_capital_position_ref",
    "purchase_operation_ref",
]
