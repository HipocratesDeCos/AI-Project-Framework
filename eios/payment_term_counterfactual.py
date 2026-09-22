"""PAG002 single-payment counterfactual due-date materialization."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from eios.core.documentary_payment_capture import DocumentaryPaymentCapture
from eios.core.models import DecisionContext, PurchaseOperation
from eios.core.scenario_engine import (
    AuthorizedScenarioChange,
    ScenarioStatus,
    ScenarioVersion,
    create_scenario,
)
from eios.finance.engine import calculate_finance_basic_scenario_due_dates
from eios.finance.models import FinanceBasicInput, FinanceBasicResult
from eios.finance.provenance import (
    ProvenancedFinanceBasicExecution,
    validate_provenanced_finance_basic_execution,
)
from eios.payment_term_minimum import MinimumPaymentTermResolution
from eios.payment_terms import OfferedPaymentTermObservation

PAG002_CF_AUTHORITY_REF = "01_Modelo/PAG002_Counterfactual_Due_Date_Authority_v0.1.md"
PAG002_CF_METHODOLOGY_REF = (
    "08_Implementacion/PAG002_Counterfactual_Due_Date_Technical_Contract_v0.1.md"
)
PAG002_CF_ORIGIN = "PAG002-CF-DUE-DATE-v0.1"

CounterfactualScheduleState = Literal["AVAILABLE", "NOT_EVALUABLE"]
CounterfactualScheduleReasonCode = Literal[
    "AVAILABLE",
    "CAPTURE_BASELINE_MISMATCH",
    "PAYMENT_BINDING_NOT_SINGLE",
    "PAYMENT_FLOW_NOT_USABLE",
    "TERM_INPUT_NOT_AVAILABLE",
    "TERM_IDENTITY_MISMATCH",
    "NON_INTEGER_PAYMENT_TERM_FOR_DATE_TRANSFORMATION",
    "MINIMUM_TERM_NOT_EXTENSION",
    "COUNTERFACTUAL_DATE_OVERFLOW",
]


class CounterfactualPaymentSchedule(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    state: CounterfactualScheduleState
    reason_code: CounterfactualScheduleReasonCode
    mode: Literal["SCENARIO_ONLY"] = "SCENARIO_ONLY"

    decision_id: str = Field(min_length=1, max_length=64)
    baseline_scenario_id: str = Field(min_length=1, max_length=64)
    data_snapshot_id: str = Field(min_length=1, max_length=64)
    parameters_version: str = Field(min_length=1, max_length=64)
    company_scope: str = Field(min_length=1, max_length=128)
    article_id: str = Field(min_length=1, max_length=128)
    supplier_id: str = Field(min_length=1, max_length=128)
    evaluation_date: date
    operation_ref: str = Field(min_length=1, max_length=256)

    flow_id: str | None = Field(default=None, max_length=128)
    installment_ref: str | None = Field(default=None, max_length=256)
    baseline_due_date: date | None = None
    counterfactual_due_date: date | None = None
    offered_payment_term_days: Decimal | None = None
    minimum_payment_term_days: Decimal | None = None
    delta_days: int | None = None
    baseline_source_ref: str | None = Field(default=None, max_length=256)
    capture_fingerprint: str = Field(min_length=64, max_length=64)
    case_kind: Literal["SYNTHETIC", "PRESENTED_OPERATIONAL"]
    transformation_authority_ref: str = Field(min_length=1, max_length=256)
    methodology_ref: str = Field(min_length=1, max_length=256)
    scenario_change: AuthorizedScenarioChange | None = None

    @field_validator("offered_payment_term_days", "minimum_payment_term_days")
    @classmethod
    def validate_terms(cls, value: Decimal | None) -> Decimal | None:
        if value is not None and not value.is_finite():
            raise ValueError("payment term debe ser finito")
        return value

    @model_validator(mode="after")
    def validate_payload(self) -> "CounterfactualPaymentSchedule":
        if self.state == "AVAILABLE":
            required = (
                self.flow_id,
                self.installment_ref,
                self.baseline_due_date,
                self.counterfactual_due_date,
                self.offered_payment_term_days,
                self.minimum_payment_term_days,
                self.delta_days,
                self.baseline_source_ref,
                self.scenario_change,
            )
            if any(item is None for item in required):
                raise ValueError("AVAILABLE requiere schedule contrafactual completo")
            if self.reason_code != "AVAILABLE":
                raise ValueError("AVAILABLE requiere reason_code AVAILABLE")
            if self.mode != "SCENARIO_ONLY":
                raise ValueError("counterfactual schedule debe ser SCENARIO_ONLY")
        elif self.reason_code == "AVAILABLE":
            raise ValueError("NOT_EVALUABLE no puede usar reason_code AVAILABLE")
        return self


@dataclass(frozen=True)
class PAG002CounterfactualFinanceExecution:
    baseline_execution: ProvenancedFinanceBasicExecution
    schedule: CounterfactualPaymentSchedule
    scenario: ScenarioVersion
    scenario_finance_input: FinanceBasicInput
    finance_result: FinanceBasicResult


def _base_identity(
    *,
    context: DecisionContext,
    purchase: PurchaseOperation,
    company_scope: str,
    operation_ref: str,
    capture: DocumentaryPaymentCapture,
    case_kind: str,
) -> dict:
    return dict(
        decision_id=context.decision_id,
        baseline_scenario_id=context.scenario_id,
        data_snapshot_id=context.data_snapshot_id,
        parameters_version=context.parameters_version,
        company_scope=company_scope,
        article_id=purchase.article_id,
        supplier_id=purchase.supplier_id,
        evaluation_date=purchase.operation_date,
        operation_ref=operation_ref,
        capture_fingerprint=capture.fingerprint,
        case_kind=case_kind,
        transformation_authority_ref=PAG002_CF_AUTHORITY_REF,
        methodology_ref=PAG002_CF_METHODOLOGY_REF,
    )


def _not_evaluable(identity: dict, reason: CounterfactualScheduleReasonCode) -> CounterfactualPaymentSchedule:
    return CounterfactualPaymentSchedule(
        **identity,
        state="NOT_EVALUABLE",
        reason_code=reason,
    )


def build_pag002_counterfactual_payment_schedule(
    *,
    capture: DocumentaryPaymentCapture,
    baseline_execution: ProvenancedFinanceBasicExecution,
    offered_term: OfferedPaymentTermObservation,
    minimum_term: MinimumPaymentTermResolution,
) -> CounterfactualPaymentSchedule:
    """Build one authorized SCENARIO_ONLY payment due-date change."""

    if not isinstance(capture, DocumentaryPaymentCapture):
        raise TypeError("capture debe ser DocumentaryPaymentCapture")
    validate_provenanced_finance_basic_execution(baseline_execution)

    payload = capture.to_payload()
    finance_payload = payload["finance_package"]
    base_payload = finance_payload["decision_input_package"]
    captured_context = DecisionContext.model_validate(base_payload["context"])
    purchase = PurchaseOperation.model_validate(base_payload["purchase"])
    captured_finance = FinanceBasicInput.model_validate(finance_payload["finance_input"])

    identity = _base_identity(
        context=captured_context,
        purchase=purchase,
        company_scope=captured_finance.snapshot.company_scope,
        operation_ref=payload["operation_ref"],
        capture=capture,
        case_kind=payload["case_kind"],
    )

    if captured_finance != baseline_execution.finance_input:
        return _not_evaluable(identity, "CAPTURE_BASELINE_MISMATCH")

    if len(payload["bindings"]) != 1:
        return _not_evaluable(identity, "PAYMENT_BINDING_NOT_SINGLE")

    binding = payload["bindings"][0]
    flow_id = binding["flow_id"]
    flows = {flow.flow_id: flow for flow in baseline_execution.finance_input.cash_flows}
    flow = flows.get(flow_id)
    if (
        flow is None
        or flow.flow_type != "PAYMENT"
        or flow.evidence_state != "DEMONSTRATED"
        or not flow.due_date_evidenced
        or flow.due_date is None
        or flow.amount is None
        or flow.currency is None
        or flow.source_ref is None
    ):
        return _not_evaluable(identity, "PAYMENT_FLOW_NOT_USABLE")

    if offered_term.state != "AVAILABLE" or minimum_term.state != "AVAILABLE":
        return _not_evaluable(identity, "TERM_INPUT_NOT_AVAILABLE")
    if (
        offered_term.offered_payment_term_days is None
        or minimum_term.minimum_payment_term_days is None
    ):
        return _not_evaluable(identity, "TERM_INPUT_NOT_AVAILABLE")

    coherent = (
        offered_term.decision_id == captured_context.decision_id
        and offered_term.scenario_id == captured_context.scenario_id
        and offered_term.data_snapshot_id == captured_context.data_snapshot_id
        and offered_term.company_scope == captured_finance.snapshot.company_scope
        and offered_term.article_id == purchase.article_id
        and offered_term.supplier_id == purchase.supplier_id
        and offered_term.evaluation_date == purchase.operation_date
        and minimum_term.decision_id == captured_context.decision_id
        and minimum_term.scenario_id == captured_context.scenario_id
        and minimum_term.parameters_version == captured_context.parameters_version
        and minimum_term.company_scope == captured_finance.snapshot.company_scope
        and minimum_term.evaluation_date == purchase.operation_date
    )
    if not coherent:
        return _not_evaluable(identity, "TERM_IDENTITY_MISMATCH")

    offered = offered_term.offered_payment_term_days
    minimum = minimum_term.minimum_payment_term_days
    if (
        offered != offered.to_integral_value()
        or minimum != minimum.to_integral_value()
    ):
        return _not_evaluable(
            identity,
            "NON_INTEGER_PAYMENT_TERM_FOR_DATE_TRANSFORMATION",
        )
    if minimum <= offered:
        return _not_evaluable(identity, "MINIMUM_TERM_NOT_EXTENSION")

    delta_days = int(minimum - offered)
    try:
        counterfactual_due = flow.due_date + timedelta(days=delta_days)
    except OverflowError:
        return _not_evaluable(identity, "COUNTERFACTUAL_DATE_OVERFLOW")

    change = AuthorizedScenarioChange(
        variable=f"payment_due_date:{flow.flow_id}",
        base_value=flow.due_date,
        simulated_value=counterfactual_due,
        unit="calendar_date",
        authorization=True,
        origin=PAG002_CF_ORIGIN,
    )

    return CounterfactualPaymentSchedule(
        **identity,
        state="AVAILABLE",
        reason_code="AVAILABLE",
        flow_id=flow.flow_id,
        installment_ref=binding["installment_ref"],
        baseline_due_date=flow.due_date,
        counterfactual_due_date=counterfactual_due,
        offered_payment_term_days=offered,
        minimum_payment_term_days=minimum,
        delta_days=delta_days,
        baseline_source_ref=flow.source_ref,
        scenario_change=change,
    )


def build_pag002_counterfactual_finance_execution(
    *,
    baseline_execution: ProvenancedFinanceBasicExecution,
    schedule: CounterfactualPaymentSchedule,
) -> PAG002CounterfactualFinanceExecution:
    """Execute Finance Basic under the authorized due-date hypothesis only."""

    validate_provenanced_finance_basic_execution(baseline_execution)
    if schedule.state != "AVAILABLE" or schedule.scenario_change is None:
        raise ValueError("schedule AVAILABLE requerida")

    baseline_input = baseline_execution.finance_input
    context = baseline_input.context
    if (
        schedule.decision_id != context.decision_id
        or schedule.baseline_scenario_id != context.scenario_id
        or schedule.data_snapshot_id != context.data_snapshot_id
        or schedule.parameters_version != context.parameters_version
        or schedule.company_scope != baseline_input.snapshot.company_scope
    ):
        raise ValueError("schedule pertenece a otro contexto financiero")

    change = schedule.scenario_change
    if (
        change.variable != f"payment_due_date:{schedule.flow_id}"
        or change.base_value != schedule.baseline_due_date
        or change.simulated_value != schedule.counterfactual_due_date
        or change.unit != "calendar_date"
        or not change.authorization
        or change.origin != PAG002_CF_ORIGIN
    ):
        raise ValueError("AuthorizedScenarioChange incompatible con la autoridad PAG002")

    scenario = create_scenario(
        context,
        changes=(change,),
        parent_scenario_id=context.scenario_id,
    )
    if scenario.status != ScenarioStatus.VALID or len(scenario.changes) != 1:
        raise ValueError("O2 no materializó un escenario válido de cambio único")

    scenario_context = context.model_copy(update={"scenario_id": scenario.scenario_id})
    scenario_input = baseline_input.model_copy(
        update={"context": scenario_context},
        deep=True,
    )
    result = calculate_finance_basic_scenario_due_dates(
        scenario_input,
        scenario_due_dates={
            schedule.flow_id: schedule.counterfactual_due_date,
        },
    )

    return PAG002CounterfactualFinanceExecution(
        baseline_execution=baseline_execution,
        schedule=schedule,
        scenario=scenario,
        scenario_finance_input=scenario_input,
        finance_result=result,
    )


def validate_pag002_counterfactual_finance_execution(
    execution: PAG002CounterfactualFinanceExecution,
) -> None:
    if not isinstance(execution, PAG002CounterfactualFinanceExecution):
        raise TypeError("execution debe ser PAG002CounterfactualFinanceExecution")

    rebuilt = build_pag002_counterfactual_finance_execution(
        baseline_execution=execution.baseline_execution,
        schedule=execution.schedule,
    )
    if rebuilt.scenario != execution.scenario:
        raise ValueError("ScenarioVersion contrafactual no coincide con O2")
    if rebuilt.scenario_finance_input != execution.scenario_finance_input:
        raise ValueError("scenario_finance_input no preserva el baseline")
    if rebuilt.finance_result != execution.finance_result:
        raise ValueError("finance_result contrafactual no coincide con recomputación")


__all__ = [
    "CounterfactualPaymentSchedule",
    "CounterfactualScheduleReasonCode",
    "CounterfactualScheduleState",
    "PAG002CounterfactualFinanceExecution",
    "PAG002_CF_AUTHORITY_REF",
    "PAG002_CF_METHODOLOGY_REF",
    "PAG002_CF_ORIGIN",
    "build_pag002_counterfactual_finance_execution",
    "build_pag002_counterfactual_payment_schedule",
    "validate_pag002_counterfactual_finance_execution",
]
