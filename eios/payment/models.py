"""Factual payment-term evidence contracts for the EIOS procurement MVP.

This package records purchase-specific offered payment terms and their evidence
state. It does not apply P-PAG parameters, evaluate R-PAG rules, negotiate,
consolidate CRC results, or create purchase authority.
"""
from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


PaymentTermEvidenceState = Literal[
    "KNOWN",
    "NOT_EVIDENCED",
    "CONFLICTING_DATA",
    "NOT_DETERMINABLE",
]


class FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, frozen=True)


def _validate_refs(values: tuple[str, ...], field: str) -> None:
    if any(not value.strip() for value in values):
        raise ValueError(f"{field} no puede contener referencias vacías")
    if len(values) != len(set(values)):
        raise ValueError(f"{field} no puede contener duplicados")


class PurchasePaymentTermEvidence(FrozenModel):
    """Evidence for the payment term offered for one evaluated purchase."""

    decision_id: str = Field(min_length=1, max_length=64)
    scenario_id: str = Field(min_length=1, max_length=64)
    article_id: str = Field(min_length=1, max_length=128)
    supplier_id: str = Field(min_length=1, max_length=128)
    evaluated_purchase_ref: str = Field(min_length=1, max_length=256)
    state: PaymentTermEvidenceState
    offered_payment_term_days: int | None = Field(default=None, ge=0)
    semantic_ref: str | None = Field(default=None, min_length=1, max_length=256)
    purchase_applicability_ref: str | None = Field(default=None, min_length=1, max_length=256)
    source_ref: str | None = Field(default=None, min_length=1, max_length=256)
    captured_at: date | None = None
    evidence_refs: tuple[str, ...] = ()
    issue_refs: tuple[str, ...] = ()
    trace_refs: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()

    @field_validator("offered_payment_term_days", mode="before")
    @classmethod
    def reject_bool_as_days(cls, value):
        if isinstance(value, bool):
            raise ValueError("offered_payment_term_days requiere un entero de días")
        return value

    @model_validator(mode="after")
    def validate_evidence_state(self) -> "PurchasePaymentTermEvidence":
        for field in ("evidence_refs", "issue_refs", "trace_refs", "limitations"):
            _validate_refs(getattr(self, field), field)

        if self.state == "KNOWN":
            if self.offered_payment_term_days is None:
                raise ValueError("Payment term KNOWN requiere offered_payment_term_days")
            if not all(
                (
                    self.semantic_ref,
                    self.purchase_applicability_ref,
                    self.source_ref,
                    self.captured_at,
                )
            ):
                raise ValueError(
                    "Payment term KNOWN requiere semantic/applicability/source/captured_at"
                )
            if not self.evidence_refs:
                raise ValueError("Payment term KNOWN requiere evidence_refs")
            if self.issue_refs:
                raise ValueError("Payment term KNOWN no admite issue_refs no resueltas")
        elif self.state == "NOT_EVIDENCED":
            if self.offered_payment_term_days is not None:
                raise ValueError("NOT_EVIDENCED no puede publicar un plazo como conocido")
        elif self.state == "CONFLICTING_DATA":
            if self.offered_payment_term_days is not None:
                raise ValueError("CONFLICTING_DATA no puede publicar un plazo único")
            if not self.issue_refs:
                raise ValueError("CONFLICTING_DATA requiere issue_refs")
        elif self.state == "NOT_DETERMINABLE":
            if self.offered_payment_term_days is not None:
                raise ValueError("NOT_DETERMINABLE no puede publicar un plazo determinado")
            if not (self.issue_refs or self.limitations):
                raise ValueError("NOT_DETERMINABLE requiere issue_refs o limitations")
        return self


class PaymentTermResult(FrozenModel):
    """Traceable factual payment-term result; never a rule Assessment."""

    decision_id: str = Field(min_length=1, max_length=64)
    scenario_id: str = Field(min_length=1, max_length=64)
    article_id: str = Field(min_length=1, max_length=128)
    supplier_id: str = Field(min_length=1, max_length=128)
    rules_version: str = Field(min_length=1, max_length=64)
    parameters_version: str = Field(min_length=1, max_length=64)
    data_snapshot_id: str = Field(min_length=1, max_length=64)
    evaluated_purchase_ref: str = Field(min_length=1, max_length=256)
    state: PaymentTermEvidenceState
    offered_payment_term_days: int | None = Field(default=None, ge=0)
    evidence_refs: tuple[str, ...] = ()
    issue_refs: tuple[str, ...] = ()
    trace_refs: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()

    @field_validator("offered_payment_term_days", mode="before")
    @classmethod
    def reject_bool_as_days(cls, value):
        if isinstance(value, bool):
            raise ValueError("offered_payment_term_days requiere un entero de días")
        return value

    @model_validator(mode="after")
    def validate_result_state(self) -> "PaymentTermResult":
        for field in ("evidence_refs", "issue_refs", "trace_refs", "limitations"):
            _validate_refs(getattr(self, field), field)
        if self.state == "KNOWN" and self.offered_payment_term_days is None:
            raise ValueError("PaymentTermResult KNOWN requiere plazo")
        if self.state != "KNOWN" and self.offered_payment_term_days is not None:
            raise ValueError("Solo KNOWN puede publicar offered_payment_term_days")
        if self.state == "CONFLICTING_DATA" and not self.issue_refs:
            raise ValueError("PaymentTermResult CONFLICTING_DATA requiere issue_refs")
        if self.state == "NOT_DETERMINABLE" and not (self.issue_refs or self.limitations):
            raise ValueError("PaymentTermResult NOT_DETERMINABLE requiere contexto explícito")
        return self


__all__ = [
    "PaymentTermEvidenceState",
    "PaymentTermResult",
    "PurchasePaymentTermEvidence",
]
