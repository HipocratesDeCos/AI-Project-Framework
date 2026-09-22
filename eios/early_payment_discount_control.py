"""PAG001 P-PAG-005 early-payment discount context control."""
from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from eios.core.models import DecisionContext, Evidence
from eios.core.validation import validate_evidence
from eios.parameters import ResolvedConfiguration

P_PAG_005 = "P-PAG-005"
PARAMETER_CONFIGURATION_EVIDENCE_SOURCE_TYPE = "ParameterConfigurationEvidence"

EarlyPaymentDiscountControlState = Literal["ENABLED", "DISABLED", "NOT_EVALUABLE"]
EarlyPaymentDiscountControlReasonCode = Literal[
    "EARLY_PAYMENT_DISCOUNT_CONTEXT_ENABLED",
    "EARLY_PAYMENT_DISCOUNT_CONTEXT_DISABLED",
    "MISSING_DISCOUNT_CONTROL_CONFIGURATION",
    "INVALID_DISCOUNT_CONTROL_CONFIGURATION",
    "INVALID_DISCOUNT_CONTROL_EVIDENCE",
]


class EarlyPaymentDiscountControlResolution(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    decision_id: str = Field(min_length=1, max_length=64)
    scenario_id: str = Field(min_length=1, max_length=64)
    parameters_version: str = Field(min_length=1, max_length=64)
    company_scope: str = Field(min_length=1, max_length=128)
    evaluation_date: date
    state: EarlyPaymentDiscountControlState
    reason_code: EarlyPaymentDiscountControlReasonCode
    configuration_ref: str | None = Field(default=None, max_length=256)
    evidence_id: str | None = Field(default=None, max_length=64)

    @model_validator(mode="after")
    def validate_payload(self) -> "EarlyPaymentDiscountControlResolution":
        if self.state == "ENABLED" and self.reason_code != "EARLY_PAYMENT_DISCOUNT_CONTEXT_ENABLED":
            raise ValueError("ENABLED requiere EARLY_PAYMENT_DISCOUNT_CONTEXT_ENABLED")
        if self.state == "DISABLED" and self.reason_code != "EARLY_PAYMENT_DISCOUNT_CONTEXT_DISABLED":
            raise ValueError("DISABLED requiere EARLY_PAYMENT_DISCOUNT_CONTEXT_DISABLED")
        if self.state in {"ENABLED", "DISABLED"} and (
            self.configuration_ref is None or self.evidence_id is None
        ):
            raise ValueError("ENABLED/DISABLED requieren configuración y evidencia")
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
    state: EarlyPaymentDiscountControlState,
    reason_code: EarlyPaymentDiscountControlReasonCode,
    resolved: ResolvedConfiguration | None,
    evidence: Evidence | None,
) -> EarlyPaymentDiscountControlResolution:
    return EarlyPaymentDiscountControlResolution(
        decision_id=context.decision_id,
        scenario_id=context.scenario_id,
        parameters_version=context.parameters_version,
        company_scope=company_scope,
        evaluation_date=evaluation_date,
        state=state,
        reason_code=reason_code,
        configuration_ref=resolved.configuration_ref if resolved else None,
        evidence_id=evidence.evidence_id if evidence else None,
    )


def resolve_early_payment_discount_control(
    *,
    context: DecisionContext,
    company_scope: str,
    evaluation_date: date,
    control_resolution: ResolvedConfiguration | None,
    control_evidence: Evidence | None,
) -> EarlyPaymentDiscountControlResolution:
    """Resolve P-PAG-005 independently from the R-PAG-001 core comparator."""

    if control_resolution is None or control_evidence is None:
        return _build(
            context=context,
            company_scope=company_scope,
            evaluation_date=evaluation_date,
            state="NOT_EVALUABLE",
            reason_code="MISSING_DISCOUNT_CONTROL_CONFIGURATION",
            resolved=control_resolution,
            evidence=control_evidence,
        )

    coherent = (
        control_resolution.parameter_id == P_PAG_005
        and control_resolution.company_id == company_scope
        and control_resolution.parameters_version == context.parameters_version
        and control_resolution.effective_at.date() == evaluation_date
        and _active(control_resolution)
    )
    if not coherent:
        return _build(
            context=context,
            company_scope=company_scope,
            evaluation_date=evaluation_date,
            state="NOT_EVALUABLE",
            reason_code="INVALID_DISCOUNT_CONTROL_CONFIGURATION",
            resolved=control_resolution,
            evidence=control_evidence,
        )

    valid_evidence = (
        control_evidence.source_type == PARAMETER_CONFIGURATION_EVIDENCE_SOURCE_TYPE
        and control_evidence.captured_at == evaluation_date
        and validate_evidence(control_evidence).status == "VALID"
        and control_evidence.demonstration_ref == control_resolution.configuration_ref
    )
    if not valid_evidence:
        return _build(
            context=context,
            company_scope=company_scope,
            evaluation_date=evaluation_date,
            state="NOT_EVALUABLE",
            reason_code="INVALID_DISCOUNT_CONTROL_EVIDENCE",
            resolved=control_resolution,
            evidence=control_evidence,
        )

    if control_resolution.value == "Sí":
        return _build(
            context=context,
            company_scope=company_scope,
            evaluation_date=evaluation_date,
            state="ENABLED",
            reason_code="EARLY_PAYMENT_DISCOUNT_CONTEXT_ENABLED",
            resolved=control_resolution,
            evidence=control_evidence,
        )
    if control_resolution.value == "No":
        return _build(
            context=context,
            company_scope=company_scope,
            evaluation_date=evaluation_date,
            state="DISABLED",
            reason_code="EARLY_PAYMENT_DISCOUNT_CONTEXT_DISABLED",
            resolved=control_resolution,
            evidence=control_evidence,
        )

    return _build(
        context=context,
        company_scope=company_scope,
        evaluation_date=evaluation_date,
        state="NOT_EVALUABLE",
        reason_code="INVALID_DISCOUNT_CONTROL_CONFIGURATION",
        resolved=control_resolution,
        evidence=control_evidence,
    )


__all__ = [
    "P_PAG_005",
    "EarlyPaymentDiscountControlReasonCode",
    "EarlyPaymentDiscountControlResolution",
    "EarlyPaymentDiscountControlState",
    "resolve_early_payment_discount_control",
]
