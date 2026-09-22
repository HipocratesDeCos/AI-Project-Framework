"""PAG002 P-PAG-001 minimum payment-term resolution."""
from __future__ import annotations

from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from eios.core.models import DecisionContext, Evidence
from eios.core.validation import validate_evidence
from eios.parameters import ResolvedConfiguration

P_PAG_001 = "P-PAG-001"
PARAMETER_CONFIGURATION_EVIDENCE_SOURCE_TYPE = "ParameterConfigurationEvidence"

MinimumPaymentTermState = Literal["AVAILABLE", "NOT_EVALUABLE"]
MinimumPaymentTermReasonCode = Literal[
    "AVAILABLE",
    "MISSING_CONFIGURATION",
    "INVALID_CONFIGURATION",
    "INVALID_EVIDENCE",
]


class MinimumPaymentTermResolution(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    decision_id: str = Field(min_length=1, max_length=64)
    scenario_id: str = Field(min_length=1, max_length=64)
    parameters_version: str = Field(min_length=1, max_length=64)
    company_scope: str = Field(min_length=1, max_length=128)
    evaluation_date: date
    state: MinimumPaymentTermState
    reason_code: MinimumPaymentTermReasonCode
    configuration_ref: str | None = Field(default=None, max_length=256)
    minimum_payment_term_days: Decimal | None = None
    evidence_id: str | None = Field(default=None, max_length=64)

    @field_validator("minimum_payment_term_days")
    @classmethod
    def validate_days(cls, value: Decimal | None) -> Decimal | None:
        if value is not None and not value.is_finite():
            raise ValueError("minimum_payment_term_days debe ser finito")
        return value

    @model_validator(mode="after")
    def validate_payload(self) -> "MinimumPaymentTermResolution":
        if self.state == "AVAILABLE":
            if self.reason_code != "AVAILABLE":
                raise ValueError("AVAILABLE requiere reason_code AVAILABLE")
            if (
                self.configuration_ref is None
                or self.minimum_payment_term_days is None
                or self.evidence_id is None
            ):
                raise ValueError("AVAILABLE requiere configuración, valor y evidencia")
        elif self.reason_code == "AVAILABLE":
            raise ValueError("NOT_EVALUABLE no puede usar reason_code AVAILABLE")
        return self


def _active(resolved: ResolvedConfiguration) -> bool:
    configuration = resolved.configuration
    try:
        return configuration.valid_from <= resolved.effective_at and (
            configuration.valid_to is None or resolved.effective_at < configuration.valid_to
        )
    except TypeError:
        return False


def _build(
    *,
    context: DecisionContext,
    company_scope: str,
    evaluation_date: date,
    state: MinimumPaymentTermState,
    reason_code: MinimumPaymentTermReasonCode,
    resolved: ResolvedConfiguration | None,
    evidence: Evidence | None,
    value: Decimal | None = None,
) -> MinimumPaymentTermResolution:
    return MinimumPaymentTermResolution(
        decision_id=context.decision_id,
        scenario_id=context.scenario_id,
        parameters_version=context.parameters_version,
        company_scope=company_scope,
        evaluation_date=evaluation_date,
        state=state,
        reason_code=reason_code,
        configuration_ref=resolved.configuration_ref if resolved else None,
        minimum_payment_term_days=value,
        evidence_id=evidence.evidence_id if evidence else None,
    )


def resolve_minimum_payment_term(
    *,
    context: DecisionContext,
    company_scope: str,
    evaluation_date: date,
    minimum_resolution: ResolvedConfiguration | None,
    minimum_evidence: Evidence | None,
) -> MinimumPaymentTermResolution:
    if minimum_resolution is None or minimum_evidence is None:
        return _build(
            context=context,
            company_scope=company_scope,
            evaluation_date=evaluation_date,
            state="NOT_EVALUABLE",
            reason_code="MISSING_CONFIGURATION",
            resolved=minimum_resolution,
            evidence=minimum_evidence,
        )

    coherent = (
        minimum_resolution.parameter_id == P_PAG_001
        and minimum_resolution.company_id == company_scope
        and minimum_resolution.parameters_version == context.parameters_version
        and minimum_resolution.effective_at.date() == evaluation_date
        and _active(minimum_resolution)
        and minimum_resolution.unit == "días"
    )
    if not coherent:
        return _build(
            context=context,
            company_scope=company_scope,
            evaluation_date=evaluation_date,
            state="NOT_EVALUABLE",
            reason_code="INVALID_CONFIGURATION",
            resolved=minimum_resolution,
            evidence=minimum_evidence,
        )

    if (
        minimum_evidence.source_type != PARAMETER_CONFIGURATION_EVIDENCE_SOURCE_TYPE
        or minimum_evidence.captured_at != evaluation_date
        or validate_evidence(minimum_evidence).status != "VALID"
        or minimum_evidence.demonstration_ref != minimum_resolution.configuration_ref
    ):
        return _build(
            context=context,
            company_scope=company_scope,
            evaluation_date=evaluation_date,
            state="NOT_EVALUABLE",
            reason_code="INVALID_EVIDENCE",
            resolved=minimum_resolution,
            evidence=minimum_evidence,
        )

    try:
        value = Decimal(minimum_resolution.value)
    except (InvalidOperation, ValueError, TypeError):
        value = None

    if value is None or not value.is_finite() or value < 0:
        return _build(
            context=context,
            company_scope=company_scope,
            evaluation_date=evaluation_date,
            state="NOT_EVALUABLE",
            reason_code="INVALID_CONFIGURATION",
            resolved=minimum_resolution,
            evidence=minimum_evidence,
            value=value,
        )

    return _build(
        context=context,
        company_scope=company_scope,
        evaluation_date=evaluation_date,
        state="AVAILABLE",
        reason_code="AVAILABLE",
        resolved=minimum_resolution,
        evidence=minimum_evidence,
        value=value,
    )


__all__ = [
    "MinimumPaymentTermReasonCode",
    "MinimumPaymentTermResolution",
    "MinimumPaymentTermState",
    "P_PAG_001",
    "resolve_minimum_payment_term",
]
