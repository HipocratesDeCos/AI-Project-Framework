"""PAG001 payment-term tolerance transformation.

This module materializes the authorized P-PAG-002/P-PAG-003 transformation
without executing R-PAG-001. It is intentionally provenance-safe and fail-closed.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from eios.core.models import DecisionContext, Evidence
from eios.core.validation import validate_evidence
from eios.parameters import ResolvedConfiguration


P_PAG_002 = "P-PAG-002"
P_PAG_003 = "P-PAG-003"
PARAMETER_CONFIGURATION_EVIDENCE_SOURCE_TYPE = "ParameterConfigurationEvidence"

PaymentTermToleranceState = Literal["AVAILABLE", "NOT_EVALUABLE"]
PaymentTermToleranceReasonCode = Literal[
    "AVAILABLE",
    "MISSING_CONFIGURATION",
    "INVALID_CONFIGURATION",
    "INCOHERENT_CONFIGURATION",
    "INVALID_EVIDENCE",
]


class PaymentTermToleranceResolution(BaseModel):
    """Traceable result of resolving the authorized target-tolerance threshold."""

    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    decision_id: str = Field(min_length=1, max_length=64)
    scenario_id: str = Field(min_length=1, max_length=64)
    parameters_version: str = Field(min_length=1, max_length=64)
    company_scope: str = Field(min_length=1, max_length=128)
    evaluation_date: date
    state: PaymentTermToleranceState
    reason_code: PaymentTermToleranceReasonCode
    target_configuration_ref: str | None = Field(default=None, max_length=256)
    tolerance_configuration_ref: str | None = Field(default=None, max_length=256)
    target_days: Decimal | None = None
    tolerance_days: Decimal | None = None
    effective_threshold_days: Decimal | None = None
    evidence_ids: tuple[str, ...] = ()

    @field_validator("target_days", "tolerance_days", "effective_threshold_days")
    @classmethod
    def validate_decimal(cls, value: Decimal | None) -> Decimal | None:
        if value is not None and not value.is_finite():
            raise ValueError("los valores de plazo deben ser finitos")
        return value

    @field_validator("evidence_ids")
    @classmethod
    def unique_evidence_ids(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if len(value) != len(set(value)):
            raise ValueError("evidence_ids no puede contener duplicados")
        return value

    @model_validator(mode="after")
    def validate_state_payload(self) -> "PaymentTermToleranceResolution":
        if self.state == "AVAILABLE":
            if self.reason_code != "AVAILABLE":
                raise ValueError("AVAILABLE requiere reason_code AVAILABLE")
            required = (
                self.target_configuration_ref,
                self.tolerance_configuration_ref,
                self.target_days,
                self.tolerance_days,
                self.effective_threshold_days,
            )
            if any(item is None for item in required):
                raise ValueError("AVAILABLE requiere transformación completa")
            if len(self.evidence_ids) != 2:
                raise ValueError("AVAILABLE requiere dos evidencias de configuración")
        else:
            if self.reason_code == "AVAILABLE":
                raise ValueError("NOT_EVALUABLE no puede usar reason_code AVAILABLE")
            if self.effective_threshold_days is not None:
                raise ValueError("NOT_EVALUABLE no puede publicar umbral efectivo")
        return self


def _base(
    *,
    context: DecisionContext,
    company_scope: str,
    evaluation_date: date,
    state: PaymentTermToleranceState,
    reason_code: PaymentTermToleranceReasonCode,
    target: ResolvedConfiguration | None,
    tolerance: ResolvedConfiguration | None,
    target_days: Decimal | None = None,
    tolerance_days: Decimal | None = None,
    threshold: Decimal | None = None,
    evidence_ids: tuple[str, ...] = (),
) -> PaymentTermToleranceResolution:
    return PaymentTermToleranceResolution(
        decision_id=context.decision_id,
        scenario_id=context.scenario_id,
        parameters_version=context.parameters_version,
        company_scope=company_scope,
        evaluation_date=evaluation_date,
        state=state,
        reason_code=reason_code,
        target_configuration_ref=target.configuration_ref if target else None,
        tolerance_configuration_ref=tolerance.configuration_ref if tolerance else None,
        target_days=target_days,
        tolerance_days=tolerance_days,
        effective_threshold_days=threshold,
        evidence_ids=evidence_ids,
    )


def _parse_days(resolved: ResolvedConfiguration) -> Decimal | None:
    if resolved.unit != "días":
        return None
    try:
        value = Decimal(resolved.value)
    except (InvalidOperation, ValueError, TypeError):
        return None
    if not value.is_finite():
        return None
    return value


def _evidence_matches(
    *,
    resolved: ResolvedConfiguration,
    evidence: Evidence,
    evaluation_date: date,
) -> bool:
    if evidence.source_type != PARAMETER_CONFIGURATION_EVIDENCE_SOURCE_TYPE:
        return False
    if evidence.captured_at != evaluation_date:
        return False
    if validate_evidence(evidence).status != "VALID":
        return False
    if evidence.demonstration_ref != resolved.configuration_ref:
        return False
    return True


def resolve_payment_term_tolerance(
    *,
    context: DecisionContext,
    company_scope: str,
    evaluation_date: date,
    target_resolution: ResolvedConfiguration | None,
    target_evidence: Evidence | None,
    tolerance_resolution: ResolvedConfiguration | None,
    tolerance_evidence: Evidence | None,
) -> PaymentTermToleranceResolution:
    """Resolve the authorized effective threshold P-PAG-002 - P-PAG-003."""

    if (
        target_resolution is None
        or tolerance_resolution is None
        or target_evidence is None
        or tolerance_evidence is None
    ):
        evidence_ids = tuple(
            item.evidence_id
            for item in (target_evidence, tolerance_evidence)
            if item is not None
        )
        return _base(
            context=context,
            company_scope=company_scope,
            evaluation_date=evaluation_date,
            state="NOT_EVALUABLE",
            reason_code="MISSING_CONFIGURATION",
            target=target_resolution,
            tolerance=tolerance_resolution,
            evidence_ids=evidence_ids,
        )

    evidence_ids = (target_evidence.evidence_id, tolerance_evidence.evidence_id)

    if (
        target_resolution.parameter_id != P_PAG_002
        or tolerance_resolution.parameter_id != P_PAG_003
    ):
        return _base(
            context=context,
            company_scope=company_scope,
            evaluation_date=evaluation_date,
            state="NOT_EVALUABLE",
            reason_code="INVALID_CONFIGURATION",
            target=target_resolution,
            tolerance=tolerance_resolution,
            evidence_ids=evidence_ids,
        )

    coherent = (
        target_resolution.company_id == tolerance_resolution.company_id == company_scope
        and target_resolution.parameters_version
        == tolerance_resolution.parameters_version
        == context.parameters_version
        and target_resolution.effective_at == tolerance_resolution.effective_at
        and target_resolution.effective_at.date() == evaluation_date
    )
    if not coherent:
        return _base(
            context=context,
            company_scope=company_scope,
            evaluation_date=evaluation_date,
            state="NOT_EVALUABLE",
            reason_code="INCOHERENT_CONFIGURATION",
            target=target_resolution,
            tolerance=tolerance_resolution,
            evidence_ids=evidence_ids,
        )

    if not _evidence_matches(
        resolved=target_resolution,
        evidence=target_evidence,
        evaluation_date=evaluation_date,
    ) or not _evidence_matches(
        resolved=tolerance_resolution,
        evidence=tolerance_evidence,
        evaluation_date=evaluation_date,
    ):
        return _base(
            context=context,
            company_scope=company_scope,
            evaluation_date=evaluation_date,
            state="NOT_EVALUABLE",
            reason_code="INVALID_EVIDENCE",
            target=target_resolution,
            tolerance=tolerance_resolution,
            evidence_ids=evidence_ids,
        )

    target_days = _parse_days(target_resolution)
    tolerance_days = _parse_days(tolerance_resolution)
    if (
        target_days is None
        or tolerance_days is None
        or target_days < 0
        or tolerance_days < 0
        or tolerance_days > target_days
    ):
        return _base(
            context=context,
            company_scope=company_scope,
            evaluation_date=evaluation_date,
            state="NOT_EVALUABLE",
            reason_code="INVALID_CONFIGURATION",
            target=target_resolution,
            tolerance=tolerance_resolution,
            target_days=target_days,
            tolerance_days=tolerance_days,
            evidence_ids=evidence_ids,
        )

    threshold = target_days - tolerance_days
    return _base(
        context=context,
        company_scope=company_scope,
        evaluation_date=evaluation_date,
        state="AVAILABLE",
        reason_code="AVAILABLE",
        target=target_resolution,
        tolerance=tolerance_resolution,
        target_days=target_days,
        tolerance_days=tolerance_days,
        threshold=threshold,
        evidence_ids=evidence_ids,
    )


__all__ = [
    "P_PAG_002",
    "P_PAG_003",
    "PaymentTermToleranceReasonCode",
    "PaymentTermToleranceResolution",
    "PaymentTermToleranceState",
    "resolve_payment_term_tolerance",
]
