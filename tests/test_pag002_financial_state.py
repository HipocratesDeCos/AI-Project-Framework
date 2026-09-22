from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

from eios.core.models import DecisionContext, Evidence
from eios.finance import FinanceBasicInput, FinancialSnapshot, run_provenanced_finance_basic
from eios.parameters.center import Configuration
from eios.parameters.resolution import ResolvedConfiguration
from eios.payment_term_minimum import resolve_minimum_payment_term
from eios.rules.finance import finance_basic_result_ref
from eios.rules.payment_financial import classify_pag002_financial_state


EFFECTIVE_AT = datetime(2026, 9, 22, 9, 0, tzinfo=timezone.utc)
EVAL_DATE = EFFECTIVE_AT.date()


def _context():
    return DecisionContext(
        decision_id="DEC-PAG002",
        scenario_id="SCN-PAG002",
        rules_version="rules-v1",
        parameters_version="params-v1",
        data_snapshot_id="snapshot-v1",
    )


def _resolved(parameter_id, value, unit, configuration_id):
    cfg = Configuration(
        configuration_id=configuration_id,
        parameter_id=parameter_id,
        company_id="COMP-A",
        value=str(value),
        value_type="DECIMAL",
        unit=unit,
        valid_from=EFFECTIVE_AT - timedelta(days=1),
        valid_to=None,
        created_at=EFFECTIVE_AT - timedelta(days=2),
        updated_at=EFFECTIVE_AT - timedelta(days=1),
    )
    return ResolvedConfiguration(
        configuration=cfg,
        parameters_version="params-v1",
        effective_at=EFFECTIVE_AT,
    )


def _parameter_evidence(resolved, evidence_id):
    return Evidence(
        evidence_id=evidence_id,
        source_type="ParameterConfigurationEvidence",
        source_ref=f"parameter:{resolved.parameter_id}",
        captured_at=EVAL_DATE,
        state="DEMONSTRATED",
        demonstration_ref=resolved.configuration_ref,
    )


def _finance_execution(*, opening="1000", payment="0", treasury_minimum="500"):
    context = _context()
    horizon = _resolved("P-FIN-001", "30", "días", 101)
    cash_flows = ()
    if Decimal(payment) > 0:
        from eios.finance import CashFlow
        cash_flows = (
            CashFlow(
                flow_id="PAY-OP",
                flow_type="PAYMENT",
                amount=Decimal(payment),
                currency="EUR",
                due_date=date(2026, 9, 25),
                source_ref="payment:op",
                evidence_state="DEMONSTRATED",
            ),
        )
    payload = FinanceBasicInput(
        context=context,
        snapshot=FinancialSnapshot(
            company_scope="COMP-A",
            as_of_date=EVAL_DATE,
            data_snapshot_id=context.data_snapshot_id,
            currency="EUR",
            available_treasury=Decimal(opening),
            treasury_evidence_ref="bank:snapshot",
        ),
        cash_flows=cash_flows,
        horizon_days=30,
        treasury_minimum=Decimal(treasury_minimum),
    )
    return run_provenanced_finance_basic(payload, horizon)


def _finance_evidence(execution):
    return Evidence(
        evidence_id="EV-FIN",
        source_type="FinanceBasicResultEvidence",
        source_ref="finance-basic",
        captured_at=EVAL_DATE,
        state="DEMONSTRATED",
        demonstration_ref=finance_basic_result_ref(execution.finance_result),
    )


def test_minimum_term_available():
    resolved = _resolved("P-PAG-001", "60", "días", 1)
    result = resolve_minimum_payment_term(
        context=_context(),
        company_scope="COMP-A",
        evaluation_date=EVAL_DATE,
        minimum_resolution=resolved,
        minimum_evidence=_parameter_evidence(resolved, "EV-PAG001"),
    )
    assert result.state == "AVAILABLE"
    assert result.minimum_payment_term_days == Decimal("60")


def test_minimum_term_rejects_negative_and_noncanonical_unit():
    negative = _resolved("P-PAG-001", "-1", "días", 1)
    result = resolve_minimum_payment_term(
        context=_context(),
        company_scope="COMP-A",
        evaluation_date=EVAL_DATE,
        minimum_resolution=negative,
        minimum_evidence=_parameter_evidence(negative, "EV-NEG"),
    )
    assert result.state == "NOT_EVALUABLE"

    wrong_unit = _resolved("P-PAG-001", "60", "days", 2)
    result = resolve_minimum_payment_term(
        context=_context(),
        company_scope="COMP-A",
        evaluation_date=EVAL_DATE,
        minimum_resolution=wrong_unit,
        minimum_evidence=_parameter_evidence(wrong_unit, "EV-UNIT"),
    )
    assert result.state == "NOT_EVALUABLE"


def test_minimum_term_missing_is_not_evaluable():
    result = resolve_minimum_payment_term(
        context=_context(),
        company_scope="COMP-A",
        evaluation_date=EVAL_DATE,
        minimum_resolution=None,
        minimum_evidence=None,
    )
    assert result.state == "NOT_EVALUABLE"
    assert result.reason_code == "MISSING_CONFIGURATION"


def test_pag002_financial_state_viable_when_capacity_meets_minimum():
    execution = _finance_execution(opening="1000", payment="200", treasury_minimum="500")
    threshold = _resolved("P-FIN-002", "500", "EUR", 2)
    result = classify_pag002_financial_state(
        context=_context(),
        finance_execution=execution,
        finance_evidence=_finance_evidence(execution),
        treasury_minimum_resolution=threshold,
        treasury_minimum_evidence=_parameter_evidence(threshold, "EV-FIN002"),
    )
    assert result.state == "PAG002_FINANCIALLY_VIABLE"
    assert result.financial_capacity_forecast == "800"
    assert result.treasury_minimum == "500"


def test_pag002_financial_state_non_viable_when_capacity_below_minimum():
    execution = _finance_execution(opening="1000", payment="700", treasury_minimum="500")
    threshold = _resolved("P-FIN-002", "500", "EUR", 2)
    result = classify_pag002_financial_state(
        context=_context(),
        finance_execution=execution,
        finance_evidence=_finance_evidence(execution),
        treasury_minimum_resolution=threshold,
        treasury_minimum_evidence=_parameter_evidence(threshold, "EV-FIN002"),
    )
    assert result.state == "PAG002_FINANCIALLY_NON_VIABLE"
    assert result.financial_capacity_forecast == "300"


def test_pag002_financial_state_not_determinable_without_threshold():
    execution = _finance_execution()
    result = classify_pag002_financial_state(
        context=_context(),
        finance_execution=execution,
        finance_evidence=_finance_evidence(execution),
        treasury_minimum_resolution=None,
        treasury_minimum_evidence=None,
    )
    assert result.state == "PAG002_FINANCIAL_STATE_NOT_DETERMINABLE"
    assert result.financial_capacity_forecast is None
    assert result.treasury_minimum is None


def test_pag002_financial_state_does_not_publish_global_viability_fields():
    execution = _finance_execution()
    threshold = _resolved("P-FIN-002", "500", "EUR", 2)
    result = classify_pag002_financial_state(
        context=_context(),
        finance_execution=execution,
        finance_evidence=_finance_evidence(execution),
        treasury_minimum_resolution=threshold,
        treasury_minimum_evidence=_parameter_evidence(threshold, "EV-FIN002"),
    )
    dumped = result.model_dump()
    assert "viability" not in dumped
    assert "recommendation" not in dumped
    assert "assessment" not in dumped
