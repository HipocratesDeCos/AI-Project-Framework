from dataclasses import replace
from datetime import timedelta
from decimal import Decimal

import pytest

from test_finance_decision_input_package import capture

from eios.core.documentary_payment_capture import (
    DocumentaryLocator,
    DocumentaryMaterial,
    DocumentaryPaymentBinding,
    build_documentary_payment_capture,
)
from eios.core.finance_decision_input_package import build_finance_decision_input_package
from eios.core.models import Evidence
from eios.finance import CashFlow, run_provenanced_finance_basic
from eios.parameters.center import Configuration
from eios.parameters.resolution import ResolvedConfiguration
from eios.payment_term_counterfactual import (
    PAG002_CF_ORIGIN,
    build_pag002_counterfactual_finance_execution,
    build_pag002_counterfactual_payment_schedule,
    validate_pag002_counterfactual_finance_execution,
)
from eios.payment_terms import PaymentTermSemanticAuthority
from eios.supplier.models import (
    SupplierEvidenceResult,
    SupplierObservation,
    SupplierResultIdentity,
)


def _minimum_resolution(kwargs, value="60"):
    effective = kwargs["effective_at"]
    cfg = Configuration(
        configuration_id=901,
        parameter_id="P-PAG-001",
        company_id=kwargs["company_id"],
        value=value,
        value_type="numeric",
        unit="días",
        valid_from=effective - timedelta(days=1),
        valid_to=None,
        created_at=effective - timedelta(days=2),
        updated_at=effective - timedelta(days=1),
    )
    return ResolvedConfiguration(
        configuration=cfg,
        parameters_version=kwargs["context"].parameters_version,
        effective_at=effective,
    )


def _minimum_evidence(resolved, evaluation_date):
    return Evidence(
        evidence_id="EV-PAG001",
        source_type="ParameterConfigurationEvidence",
        source_ref="parameter:P-PAG-001",
        captured_at=evaluation_date,
        state="DEMONSTRATED",
        demonstration_ref=resolved.configuration_ref,
    )


def _supplier_result(kwargs, offered=30, *, decimal=False):
    context = kwargs["context"]
    purchase = kwargs["purchase"]
    identity = SupplierResultIdentity(
        decision_id=context.decision_id,
        scenario_id=context.scenario_id,
        rules_version=context.rules_version,
        parameters_version=context.parameters_version,
        data_snapshot_id=context.data_snapshot_id,
        company_scope=kwargs["company_id"],
        article_id=purchase.article_id,
        evaluation_date=purchase.operation_date,
    )
    data = dict(
        observation_id="OBS-PAY",
        supplier_id=purchase.supplier_id,
        candidate_id=None,
        object_id=purchase.article_id,
        dimension="PAYMENT_TERM",
        state="KNOWN",
        value_kind="DECIMAL" if decimal else "INTEGER",
        unit="days",
        semantic_ref="SEM-OFFERED-PAYMENT-DAYS",
        source_ref="supplier:terms",
        evidence_id="EV-OFFERED",
        captured_at=purchase.operation_date,
        trace_refs=("trace:offered-term",),
    )
    if decimal:
        data["value_decimal"] = Decimal(str(offered))
    else:
        data["value_integer"] = int(offered)
    observation = SupplierObservation(**data)
    return SupplierEvidenceResult(
        identity=identity,
        current_supplier_id=purchase.supplier_id,
        observations=(observation,),
    )


def _semantic_authority():
    return PaymentTermSemanticAuthority(
        semantic_ref="SEM-OFFERED-PAYMENT-DAYS",
        meaning="OFFERED_PAYMENT_TERM_DAYS",
        authority_ref="authority:pag001-offered-term",
        methodology_ref="methodology:pag001-offered-term",
        version="0.1",
    )


def _prepared(capture, *, extra_payment=False):
    kwargs, _, _ = capture
    kwargs = dict(kwargs)
    first = kwargs["finance_input"].cash_flows[0].model_copy(
        update={"due_date_evidenced": True}
    )
    flows = [first]
    bindings = [
        DocumentaryPaymentBinding(
            installment_ref="installment-1",
            flow_id=first.flow_id,
            locators=(DocumentaryLocator(document_ref="doc", page=1, section="Terms"),),
        )
    ]
    if extra_payment:
        second = CashFlow(
            flow_id="payment-2",
            flow_type="PAYMENT",
            amount=Decimal("50"),
            currency="EUR",
            due_date=first.due_date + timedelta(days=1),
            due_date_evidenced=True,
            source_ref="erp:payment-2",
            evidence_state="DEMONSTRATED",
        )
        flows.append(second)
        bindings.append(
            DocumentaryPaymentBinding(
                installment_ref="installment-2",
                flow_id=second.flow_id,
                locators=(DocumentaryLocator(document_ref="doc", page=1, section="Terms"),),
            )
        )
    kwargs["finance_input"] = kwargs["finance_input"].model_copy(
        update={"cash_flows": tuple(flows)}
    )
    package = build_finance_decision_input_package(**kwargs)
    doc_capture = build_documentary_payment_capture(
        package=package,
        documents=(DocumentaryMaterial(document_ref="doc", content=b"synthetic terms"),),
        bindings=tuple(bindings),
        case_kind="SYNTHETIC",
        operation_ref="operation:test",
    )
    baseline = run_provenanced_finance_basic(
        package.finance_input,
        package.horizon_resolution,
    )
    return kwargs, package, doc_capture, baseline


def _schedule(capture, *, offered=30, minimum="60", decimal=False, extra_payment=False):
    kwargs, package, doc_capture, baseline = _prepared(
        capture,
        extra_payment=extra_payment,
    )
    resolved = _minimum_resolution(kwargs, minimum)
    result = build_pag002_counterfactual_payment_schedule(
        capture=doc_capture,
        baseline_execution=baseline,
        supplier_result=_supplier_result(kwargs, offered, decimal=decimal),
        semantic_authority=_semantic_authority(),
        minimum_resolution=resolved,
        minimum_evidence=_minimum_evidence(
            resolved,
            kwargs["purchase"].operation_date,
        ),
    )
    return result, baseline, kwargs


def test_single_payment_schedule_uses_baseline_due_date_plus_term_delta(capture):
    schedule, baseline, _ = _schedule(capture)
    flow = baseline.finance_input.cash_flows[0]
    assert schedule.state == "AVAILABLE"
    assert schedule.mode == "SCENARIO_ONLY"
    assert schedule.delta_days == 30
    assert schedule.baseline_due_date == flow.due_date
    assert schedule.counterfactual_due_date == flow.due_date + timedelta(days=30)
    assert schedule.scenario_change.variable == f"payment_due_date:{flow.flow_id}"
    assert schedule.scenario_change.origin == PAG002_CF_ORIGIN
    assert flow.due_date_evidenced is True
    assert flow.evidence_state == "DEMONSTRATED"


def test_counterfactual_execution_preserves_factual_cashflow(capture):
    schedule, baseline, _ = _schedule(capture)
    before = baseline.finance_input.model_dump(mode="python")
    execution = build_pag002_counterfactual_finance_execution(
        baseline_execution=baseline,
        schedule=schedule,
    )
    assert baseline.finance_input.model_dump(mode="python") == before
    assert execution.scenario.parent_scenario_id == baseline.finance_input.context.scenario_id
    assert execution.scenario_finance_input.cash_flows == baseline.finance_input.cash_flows
    assert execution.finance_result.scenario_id == execution.scenario.scenario_id
    validate_pag002_counterfactual_finance_execution(execution)


def test_counterfactual_outside_horizon_does_not_extend_finance_horizon(capture):
    schedule, baseline, _ = _schedule(capture)
    execution = build_pag002_counterfactual_finance_execution(
        baseline_execution=baseline,
        schedule=schedule,
    )
    assert execution.finance_result.projection.horizon_end == baseline.finance_result.projection.horizon_end
    assert schedule.counterfactual_due_date > execution.finance_result.projection.horizon_end
    assert execution.finance_result.projection.financial_capacity_forecast == Decimal("1000")


def test_multi_installment_is_not_evaluable(capture):
    schedule, _, _ = _schedule(capture, extra_payment=True)
    assert schedule.state == "NOT_EVALUABLE"
    assert schedule.reason_code == "PAYMENT_BINDING_NOT_SINGLE"


def test_fractional_payment_term_is_not_rounded(capture):
    schedule, _, _ = _schedule(capture, offered=Decimal("30.5"), decimal=True)
    assert schedule.state == "NOT_EVALUABLE"
    assert schedule.reason_code == "NON_INTEGER_PAYMENT_TERM_FOR_DATE_TRANSFORMATION"


def test_minimum_not_extension_does_not_materialize_scenario(capture):
    schedule, _, _ = _schedule(capture, offered=30, minimum="30")
    assert schedule.state == "NOT_EVALUABLE"
    assert schedule.reason_code == "MINIMUM_TERM_NOT_EXTENSION"
    assert schedule.scenario_change is None


def test_missing_supplier_term_fails_closed(capture):
    kwargs, package, doc_capture, baseline = _prepared(capture)
    supplier = _supplier_result(kwargs)
    supplier = supplier.model_copy(update={"observations": ()})
    minimum = _minimum_resolution(kwargs)
    schedule = build_pag002_counterfactual_payment_schedule(
        capture=doc_capture,
        baseline_execution=baseline,
        supplier_result=supplier,
        semantic_authority=_semantic_authority(),
        minimum_resolution=minimum,
        minimum_evidence=_minimum_evidence(minimum, kwargs["purchase"].operation_date),
    )
    assert schedule.state == "NOT_EVALUABLE"
    assert schedule.reason_code == "TERM_INPUT_NOT_AVAILABLE"


def test_detached_finance_execution_is_rejected_on_revalidation(capture):
    schedule, baseline, _ = _schedule(capture)
    execution = build_pag002_counterfactual_finance_execution(
        baseline_execution=baseline,
        schedule=schedule,
    )
    forged = replace(execution, finance_result=baseline.finance_result)
    with pytest.raises(ValueError, match="recomputación"):
        validate_pag002_counterfactual_finance_execution(forged)
