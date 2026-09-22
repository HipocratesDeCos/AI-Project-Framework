from datetime import timedelta
from decimal import Decimal

from test_finance_decision_input_package import capture
from test_pag002_counterfactual_due_date import (
    _minimum_evidence,
    _minimum_resolution,
    _semantic_authority,
    _supplier_result,
)

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
from eios.rules.catalog import authorized_rule, authorized_rule_metadata
from eios.rules.finance import finance_basic_result_ref
from eios.rules.payment_risk import (
    PAG002FinanceInputs,
    PAG002ParameterBundle,
    evaluate_r_pag_002,
)


def _control_resolution(kwargs, value="Sí"):
    effective = kwargs["effective_at"]
    cfg = Configuration(
        configuration_id=904,
        parameter_id="P-PAG-004",
        company_id=kwargs["company_id"],
        value=value,
        value_type="BOOLEAN",
        unit="Sí/No",
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


def _parameter_evidence(resolved, evidence_id, evaluation_date):
    return Evidence(
        evidence_id=evidence_id,
        source_type="ParameterConfigurationEvidence",
        source_ref=f"parameter:{resolved.parameter_id}",
        captured_at=evaluation_date,
        state="DEMONSTRATED",
        demonstration_ref=resolved.configuration_ref,
    )


def _prepared_rule_case(
    capture,
    *,
    threshold="900",
    payment="200",
    offered=30,
    minimum="60",
    control="Sí",
    extra_payment=False,
):
    kwargs, configs, _ = capture
    kwargs = dict(kwargs)
    effective = kwargs["effective_at"]

    configs["P-FIN-002"] = configs["P-FIN-002"].model_copy(
        update={"value": str(threshold)}
    )

    first = kwargs["finance_input"].cash_flows[0].model_copy(
        update={
            "amount": Decimal(payment),
            "due_date_evidenced": True,
        }
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
        update={
            "cash_flows": tuple(flows),
            "treasury_minimum": Decimal(threshold),
        }
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
    baseline_evidence = Evidence(
        evidence_id="EV-FIN-BASE",
        source_type="FinanceBasicResultEvidence",
        source_ref="finance:baseline",
        captured_at=kwargs["purchase"].operation_date,
        state="DEMONSTRATED",
        demonstration_ref=finance_basic_result_ref(baseline.finance_result),
    )

    minimum_r = _minimum_resolution(kwargs, minimum)
    minimum_e = _minimum_evidence(minimum_r, kwargs["purchase"].operation_date)
    control_r = _control_resolution(kwargs, control)
    control_e = _parameter_evidence(
        control_r,
        "EV-PAG004",
        kwargs["purchase"].operation_date,
    )
    threshold_r = package.treasury_minimum_resolution
    threshold_e = _parameter_evidence(
        threshold_r,
        "EV-FIN002",
        kwargs["purchase"].operation_date,
    )

    params = PAG002ParameterBundle(
        minimum_resolution=minimum_r,
        minimum_evidence=minimum_e,
        control_resolution=control_r,
        control_evidence=control_e,
        treasury_minimum_resolution=threshold_r,
        treasury_minimum_evidence=threshold_e,
    )
    finance = PAG002FinanceInputs(
        baseline_execution=baseline,
        baseline_evidence=baseline_evidence,
        documentary_capture=doc_capture,
    )
    supplier = _supplier_result(kwargs, offered)
    rule = authorized_rule("R-PAG-002", kwargs["context"].rules_version)
    return kwargs, supplier, params, finance, rule


def _evaluate(capture, **overrides):
    kwargs, supplier, params, finance, rule = _prepared_rule_case(
        capture,
        **overrides,
    )
    result = evaluate_r_pag_002(
        purchase=kwargs["purchase"],
        context=kwargs["context"],
        rule=rule,
        supplier_result=supplier,
        semantic_authority=_semantic_authority(),
        parameters=params,
        finance=finance,
    )
    return result


def test_r_pag_002_true_only_when_baseline_non_viable_and_minimum_term_viable(capture):
    result = _evaluate(capture, threshold="900", payment="200", offered=30, minimum="60")
    assert result.status == "EVALUABLE"
    assert result.outcome == "TRUE"
    assert "cambio único autorizado" in result.reason


def test_r_pag_002_false_when_offered_already_meets_minimum(capture):
    result = _evaluate(capture, offered=60, minimum="60")
    assert result.status == "EVALUABLE"
    assert result.outcome == "FALSE"
    assert "ya alcanza o supera" in result.reason


def test_r_pag_002_false_when_baseline_already_financially_viable(capture):
    result = _evaluate(capture, threshold="500", payment="200", offered=30, minimum="60")
    assert result.status == "EVALUABLE"
    assert result.outcome == "FALSE"
    assert "ya cumple el criterio financiero" in result.reason


def test_r_pag_002_false_when_minimum_term_remains_non_viable(capture):
    result = _evaluate(capture, threshold="1100", payment="200", offered=30, minimum="60")
    assert result.status == "EVALUABLE"
    assert result.outcome == "FALSE"
    assert "continúa sin cumplir" in result.reason


def test_r_pag_002_disabled_control_is_not_evaluable(capture):
    result = _evaluate(capture, control="No")
    assert result.status == "NOT_EVALUABLE"
    assert result.outcome is None
    assert "deshabilitado" in result.reason


def test_r_pag_002_multi_installment_is_not_evaluable(capture):
    result = _evaluate(
        capture,
        threshold="900",
        payment="200",
        offered=30,
        minimum="60",
        extra_payment=True,
    )
    assert result.status == "NOT_EVALUABLE"
    assert result.outcome is None
    assert "PAYMENT_BINDING_NOT_SINGLE" in result.reason


def test_r_pag_002_metadata_is_r1_high_conditional_buy():
    metadata = authorized_rule_metadata("R-PAG-002", "rules-v1")
    assert metadata.effect == "R1"
    assert metadata.severity == "ALTA"
    assert metadata.active_result == "COMPRAR CONDICIONADO"
