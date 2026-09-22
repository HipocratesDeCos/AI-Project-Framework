"""PAG002 financial-state classifier over provenance-safe Finance Basic."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from eios.core.models import DecisionContext, Evidence
from eios.core.validation import validate_evidence
from eios.finance.provenance import (
    ProvenancedFinanceBasicExecution,
    validate_provenanced_finance_basic_execution,
)
from eios.parameters import ResolvedConfiguration
from eios.payment_term_counterfactual import (
    PAG002CounterfactualFinanceExecution,
    validate_pag002_counterfactual_finance_execution,
)

from .finance import (
    FINANCE_BASIC_EVIDENCE_SOURCE_TYPE,
    P_FIN_002,
    _treasury_minimum,
    _validate_finance_evidence,
)

PAG002FinancialState = Literal[
    "PAG002_FINANCIALLY_VIABLE",
    "PAG002_FINANCIALLY_NON_VIABLE",
    "PAG002_FINANCIAL_STATE_NOT_DETERMINABLE",
]
PAG002FinancialReasonCode = Literal[
    "CAPACITY_MEETS_TREASURY_MINIMUM",
    "CAPACITY_BELOW_TREASURY_MINIMUM",
    "FINANCE_EXECUTION_NOT_DETERMINED",
    "FINANCE_EVIDENCE_INVALID",
    "TREASURY_MINIMUM_NOT_AVAILABLE",
]


class PAG002FinancialStateResolution(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    decision_id: str = Field(min_length=1, max_length=64)
    scenario_id: str = Field(min_length=1, max_length=64)
    data_snapshot_id: str = Field(min_length=1, max_length=64)
    parameters_version: str = Field(min_length=1, max_length=64)
    company_scope: str = Field(min_length=1, max_length=128)
    state: PAG002FinancialState
    reason_code: PAG002FinancialReasonCode
    financial_capacity_forecast: str | None = None
    treasury_minimum: str | None = None
    mode: Literal["FACTUAL", "SCENARIO_ONLY"] = "FACTUAL"
    scenario_fingerprint: str | None = Field(default=None, min_length=64, max_length=64)
    evidence_ids: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_state(self) -> "PAG002FinancialStateResolution":
        determined = {
            "PAG002_FINANCIALLY_VIABLE",
            "PAG002_FINANCIALLY_NON_VIABLE",
        }
        if self.mode == "FACTUAL" and self.scenario_fingerprint is not None:
            raise ValueError("FACTUAL no puede publicar scenario_fingerprint")
        if self.mode == "SCENARIO_ONLY" and self.scenario_fingerprint is None:
            raise ValueError("SCENARIO_ONLY requiere scenario_fingerprint")
        if self.state in determined:
            if self.financial_capacity_forecast is None or self.treasury_minimum is None:
                raise ValueError("estado financiero determinado requiere capacidad y mínimo")
            if self.mode == "FACTUAL" and len(self.evidence_ids) != 2:
                raise ValueError("estado FACTUAL determinado requiere dos evidencias")
            if self.mode == "SCENARIO_ONLY" and len(self.evidence_ids) != 1:
                raise ValueError("estado SCENARIO_ONLY determinado requiere evidencia de P-FIN-002")
        else:
            if (
                self.financial_capacity_forecast is not None
                or self.treasury_minimum is not None
            ):
                raise ValueError("NOT_DETERMINABLE no publica magnitudes parciales")
        return self


def classify_pag002_financial_state(
    *,
    context: DecisionContext,
    finance_execution: ProvenancedFinanceBasicExecution,
    finance_evidence: Evidence,
    treasury_minimum_resolution: ResolvedConfiguration | None,
    treasury_minimum_evidence: Evidence | None,
) -> PAG002FinancialStateResolution:
    validate_provenanced_finance_basic_execution(finance_execution)
    finance_input = finance_execution.finance_input
    finance_result = finance_execution.finance_result

    if finance_input.context != context:
        raise ValueError("Finance Basic execution pertenece a otro DecisionContext")

    _validate_finance_evidence(finance_input, finance_result, finance_evidence)

    base = dict(
        decision_id=context.decision_id,
        scenario_id=context.scenario_id,
        data_snapshot_id=context.data_snapshot_id,
        parameters_version=context.parameters_version,
        company_scope=finance_input.snapshot.company_scope,
    )

    if validate_evidence(finance_evidence).status != "VALID":
        return PAG002FinancialStateResolution(
            **base,
            state="PAG002_FINANCIAL_STATE_NOT_DETERMINABLE",
            reason_code="FINANCE_EVIDENCE_INVALID",
            evidence_ids=(finance_evidence.evidence_id,),
        )

    projection = finance_result.projection
    if projection.status != "DETERMINED" or projection.financial_capacity_forecast is None:
        return PAG002FinancialStateResolution(
            **base,
            state="PAG002_FINANCIAL_STATE_NOT_DETERMINABLE",
            reason_code="FINANCE_EXECUTION_NOT_DETERMINED",
            evidence_ids=(finance_evidence.evidence_id,),
        )

    if treasury_minimum_resolution is None or treasury_minimum_evidence is None:
        return PAG002FinancialStateResolution(
            **base,
            state="PAG002_FINANCIAL_STATE_NOT_DETERMINABLE",
            reason_code="TREASURY_MINIMUM_NOT_AVAILABLE",
            evidence_ids=(finance_evidence.evidence_id,),
        )

    if treasury_minimum_evidence.evidence_id == finance_evidence.evidence_id:
        return PAG002FinancialStateResolution(
            **base,
            state="PAG002_FINANCIAL_STATE_NOT_DETERMINABLE",
            reason_code="TREASURY_MINIMUM_NOT_AVAILABLE",
            evidence_ids=(finance_evidence.evidence_id,),
        )

    threshold = _treasury_minimum(
        finance_input,
        context,
        treasury_minimum_resolution,
        treasury_minimum_evidence,
    )
    if (
        validate_evidence(treasury_minimum_evidence).status != "VALID"
        or threshold is None
    ):
        return PAG002FinancialStateResolution(
            **base,
            state="PAG002_FINANCIAL_STATE_NOT_DETERMINABLE",
            reason_code="TREASURY_MINIMUM_NOT_AVAILABLE",
            evidence_ids=(
                finance_evidence.evidence_id,
                treasury_minimum_evidence.evidence_id,
            ),
        )

    capacity = projection.financial_capacity_forecast
    assert capacity is not None
    state = (
        "PAG002_FINANCIALLY_VIABLE"
        if capacity >= threshold
        else "PAG002_FINANCIALLY_NON_VIABLE"
    )
    reason = (
        "CAPACITY_MEETS_TREASURY_MINIMUM"
        if capacity >= threshold
        else "CAPACITY_BELOW_TREASURY_MINIMUM"
    )
    return PAG002FinancialStateResolution(
        **base,
        state=state,
        reason_code=reason,
        financial_capacity_forecast=str(capacity),
        treasury_minimum=str(threshold),
        evidence_ids=(
            finance_evidence.evidence_id,
            treasury_minimum_evidence.evidence_id,
        ),
    )


def classify_pag002_counterfactual_financial_state(
    *,
    execution: PAG002CounterfactualFinanceExecution,
    treasury_minimum_resolution: ResolvedConfiguration | None,
    treasury_minimum_evidence: Evidence | None,
) -> PAG002FinancialStateResolution:
    """Classify an authorized SCENARIO_ONLY finance execution for PAG002."""

    validate_pag002_counterfactual_finance_execution(execution)
    finance_input = execution.scenario_finance_input
    finance_result = execution.finance_result
    context = finance_input.context

    base = dict(
        decision_id=context.decision_id,
        scenario_id=context.scenario_id,
        data_snapshot_id=context.data_snapshot_id,
        parameters_version=context.parameters_version,
        company_scope=finance_input.snapshot.company_scope,
        mode="SCENARIO_ONLY",
        scenario_fingerprint=execution.scenario.fingerprint,
    )

    projection = finance_result.projection
    if projection.status != "DETERMINED" or projection.financial_capacity_forecast is None:
        return PAG002FinancialStateResolution(
            **base,
            state="PAG002_FINANCIAL_STATE_NOT_DETERMINABLE",
            reason_code="FINANCE_EXECUTION_NOT_DETERMINED",
            evidence_ids=(),
        )

    if treasury_minimum_resolution is None or treasury_minimum_evidence is None:
        return PAG002FinancialStateResolution(
            **base,
            state="PAG002_FINANCIAL_STATE_NOT_DETERMINABLE",
            reason_code="TREASURY_MINIMUM_NOT_AVAILABLE",
            evidence_ids=(),
        )

    threshold = _treasury_minimum(
        finance_input,
        context,
        treasury_minimum_resolution,
        treasury_minimum_evidence,
    )
    if (
        validate_evidence(treasury_minimum_evidence).status != "VALID"
        or threshold is None
    ):
        return PAG002FinancialStateResolution(
            **base,
            state="PAG002_FINANCIAL_STATE_NOT_DETERMINABLE",
            reason_code="TREASURY_MINIMUM_NOT_AVAILABLE",
            evidence_ids=(treasury_minimum_evidence.evidence_id,),
        )

    capacity = projection.financial_capacity_forecast
    state = (
        "PAG002_FINANCIALLY_VIABLE"
        if capacity >= threshold
        else "PAG002_FINANCIALLY_NON_VIABLE"
    )
    reason = (
        "CAPACITY_MEETS_TREASURY_MINIMUM"
        if capacity >= threshold
        else "CAPACITY_BELOW_TREASURY_MINIMUM"
    )
    return PAG002FinancialStateResolution(
        **base,
        state=state,
        reason_code=reason,
        financial_capacity_forecast=str(capacity),
        treasury_minimum=str(threshold),
        evidence_ids=(treasury_minimum_evidence.evidence_id,),
    )


__all__ = [
    "PAG002FinancialReasonCode",
    "PAG002FinancialState",
    "PAG002FinancialStateResolution",
    "classify_pag002_financial_state",
    "classify_pag002_counterfactual_financial_state",
]
