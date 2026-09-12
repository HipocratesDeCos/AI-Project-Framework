from datetime import date, datetime, timezone
from decimal import Decimal

import pytest

from eios.core.crc_mvp import RuleMetadata
from eios.core.models import Assessment, DecisionContext, Evidence, PurchaseOperation, Rule
from eios.finance import CashFlow, FinanceBasicInput, FinancialSnapshot, calculate_finance_basic
from eios.parameters import resolve_configuration_for_context
from eios.parameters.center import Configuration, ParameterConfigurationError
from eios.rules import (
    FINANCE_BASIC_EVIDENCE_SOURCE_TYPE,
    PARAMETER_CONFIGURATION_EVIDENCE_SOURCE_TYPE,
    evaluate_r_fin_001,
    finance_basic_result_ref,
)
from eios.rules.runtime import RuleAssessmentBinding, run_assessment_set_vertical


AS_OF = date(2026, 9, 11)
EFFECTIVE = datetime(2026, 9, 11, 12, 0, tzinfo=timezone.utc)
RULES = "rules-v1"
PARAMS = "params-v1"
SNAPSHOT = "snapshot-v1"
DECISION = "D-FIN-1"
SCENARIO = "S-FIN-1"
COMPANY = "COMP-1"


def _context() -> DecisionContext:
    return DecisionContext(
        decision_id=DECISION,
        scenario_id=SCENARIO,
        rules_version=RULES,
        parameters_version=PARAMS,
        data_snapshot_id=SNAPSHOT,
    )


def _purchase() -> PurchaseOperation:
    return PurchaseOperation(
        decision_id=DECISION,
        scenario_id=SCENARIO,
        article_id="ART-1",
        supplier_id="SUP-1",
        quantity=Decimal("10"),
        unit_price=Decimal("5"),
        currency="EUR",
        operation_date=AS_OF,
    )


def _finance_input(*, opening: Decimal | None = Decimal("120"), minimum: Decimal | None = Decimal("100")) -> FinanceBasicInput:
    return FinanceBasicInput(
        context=_context(),
        snapshot=FinancialSnapshot(
            company_scope=COMPANY,
            as_of_date=AS_OF,
            data_snapshot_id=SNAPSHOT,
            currency="EUR",
            available_treasury=opening,
            treasury_evidence_ref="bank:snapshot" if opening is not None else None,
        ),
        cash_flows=(
            CashFlow(
                flow_id="PAY-PURCHASE",
                flow_type="PAYMENT",
                amount=Decimal("50"),
                currency="EUR",
                due_date=date(2026, 9, 20),
                due_date_evidenced=True,
                source_ref="invoice:purchase",
                evidence_state="DEMONSTRATED",
            ),
        ),
        horizon_days=30,
        treasury_minimum=minimum,
    )


def _configuration(*, value: str = "100", unit: str = "€", company: str = COMPANY) -> Configuration:
    return Configuration(
        configuration_id=2002,
        parameter_id="P-FIN-002",
        company_id=company,
        value=value,
        value_type="decimal",
        unit=unit,
        valid_from=datetime(2026, 9, 1, tzinfo=timezone.utc),
        valid_to=None,
        created_at=datetime(2026, 9, 1, tzinfo=timezone.utc),
        updated_at=datetime(2026, 9, 1, tzinfo=timezone.utc),
    )


def _evidence(finance_result, resolved):
    finance = Evidence(
        evidence_id="EV-FIN-BASIC",
        source_type=FINANCE_BASIC_EVIDENCE_SOURCE_TYPE,
        source_ref="finance:basic",
        captured_at=AS_OF,
        state="DEMONSTRATED",
        demonstration_ref=finance_basic_result_ref(finance_result),
    )
    parameter = Evidence(
        evidence_id="EV-P-FIN-002",
        source_type=PARAMETER_CONFIGURATION_EVIDENCE_SOURCE_TYPE,
        source_ref="parameter-center:P-FIN-002",
        captured_at=AS_OF,
        state="DEMONSTRATED",
        demonstration_ref=resolved.configuration_ref,
    )
    return finance, parameter


def test_contextual_configuration_binds_decision_parameter_version() -> None:
    context = _context()
    resolved = resolve_configuration_for_context(_configuration(), context, EFFECTIVE)
    assert resolved is not None
    assert resolved.parameter_id == "P-FIN-002"
    assert resolved.parameters_version == PARAMS
    assert resolved.company_id == COMPANY
    assert resolved.configuration_ref.startswith("parameter_configuration:2002@")


def test_contextual_configuration_rejects_non_effective_value() -> None:
    config = _configuration()
    with pytest.raises(ParameterConfigurationError, match="no está vigente"):
        resolve_configuration_for_context(
            config,
            _context(),
            datetime(2026, 8, 31, 12, 0, tzinfo=timezone.utc),
        )


def test_r_fin_001_true_when_capacity_falls_below_p_fin_002() -> None:
    context = _context()
    purchase = _purchase()
    payload = _finance_input()
    result = calculate_finance_basic(payload)
    assert result.projection.financial_capacity_forecast == Decimal("70")

    resolved = resolve_configuration_for_context(_configuration(value="100"), context, EFFECTIVE)
    assert resolved is not None
    finance_evidence, parameter_evidence = _evidence(result, resolved)

    assessment = evaluate_r_fin_001(
        purchase,
        context,
        Rule(rule_id="R-FIN-001", version=RULES, requires_evidence=True),
        payload,
        result,
        finance_evidence,
        resolved,
        parameter_evidence,
    )
    assert assessment.status == "EVALUABLE"
    assert assessment.outcome == "TRUE"
    assert assessment.evidence_ids == ["EV-FIN-BASIC", "EV-P-FIN-002"]


def test_r_fin_001_false_when_capacity_meets_threshold() -> None:
    context = _context()
    purchase = _purchase()
    payload = _finance_input(minimum=Decimal("60"))
    result = calculate_finance_basic(payload)
    resolved = resolve_configuration_for_context(_configuration(value="60"), context, EFFECTIVE)
    assert resolved is not None
    finance_evidence, parameter_evidence = _evidence(result, resolved)

    assessment = evaluate_r_fin_001(
        purchase,
        context,
        Rule(rule_id="R-FIN-001", version=RULES, requires_evidence=True),
        payload,
        result,
        finance_evidence,
        resolved,
        parameter_evidence,
    )
    assert assessment.status == "EVALUABLE"
    assert assessment.outcome == "FALSE"


def test_r_fin_001_missing_parameter_is_not_evaluable_not_zero() -> None:
    context = _context()
    purchase = _purchase()
    payload = _finance_input(minimum=None)
    result = calculate_finance_basic(payload)
    finance_evidence = Evidence(
        evidence_id="EV-FIN-BASIC",
        source_type=FINANCE_BASIC_EVIDENCE_SOURCE_TYPE,
        source_ref="finance:basic",
        captured_at=AS_OF,
        state="DEMONSTRATED",
        demonstration_ref=finance_basic_result_ref(result),
    )

    assessment = evaluate_r_fin_001(
        purchase,
        context,
        Rule(rule_id="R-FIN-001", version=RULES, requires_evidence=True),
        payload,
        result,
        finance_evidence,
        None,
        None,
    )
    assert assessment.status == "NOT_EVALUABLE"
    assert assessment.outcome is None


def test_r_fin_001_non_determined_projection_is_not_evaluable() -> None:
    context = _context()
    purchase = _purchase()
    payload = _finance_input(opening=None)
    result = calculate_finance_basic(payload)
    assert result.projection.status == "NOT_EVIDENCED"
    resolved = resolve_configuration_for_context(_configuration(), context, EFFECTIVE)
    assert resolved is not None
    finance_evidence, parameter_evidence = _evidence(result, resolved)

    assessment = evaluate_r_fin_001(
        purchase,
        context,
        Rule(rule_id="R-FIN-001", version=RULES, requires_evidence=True),
        payload,
        result,
        finance_evidence,
        resolved,
        parameter_evidence,
    )
    assert assessment.status == "NOT_EVALUABLE"
    assert assessment.outcome is None


def test_fin_r0_dominates_stock_rules_in_multidomain_runtime() -> None:
    context = _context()
    purchase = _purchase()
    payload = _finance_input()
    result = calculate_finance_basic(payload)
    resolved = resolve_configuration_for_context(_configuration(), context, EFFECTIVE)
    assert resolved is not None
    finance_evidence, parameter_evidence = _evidence(result, resolved)
    fin_rule = Rule(rule_id="R-FIN-001", version=RULES, requires_evidence=True)
    fin_assessment = evaluate_r_fin_001(
        purchase,
        context,
        fin_rule,
        payload,
        result,
        finance_evidence,
        resolved,
        parameter_evidence,
    )
    assert fin_assessment.outcome == "TRUE"

    stk_excess_rule = Rule(rule_id="R-STK-003", version=RULES, requires_evidence=True)
    stk_exception_rule = Rule(rule_id="R-STK-004", version=RULES, requires_evidence=True)
    stk_excess = Assessment(
        rule_id="R-STK-003",
        status="EVALUABLE",
        outcome="TRUE",
        evidence_ids=["EV-STK-003"],
        reason="Exceso M07 demostrado.",
    )
    stk_exception = Assessment(
        rule_id="R-STK-004",
        status="EVALUABLE",
        outcome="TRUE",
        evidence_ids=["EV-STK-004"],
        reason="Mitigación M08 demostrada.",
    )

    vertical = run_assessment_set_vertical(
        purchase=purchase,
        context=context,
        bindings=(
            RuleAssessmentBinding(
                rule=fin_rule,
                assessment=fin_assessment,
                metadata=RuleMetadata(
                    rule_id="R-FIN-001", version=RULES, effect="R0", severity="CRÍTICA"
                ),
            ),
            RuleAssessmentBinding(
                rule=stk_excess_rule,
                assessment=stk_excess,
                metadata=RuleMetadata(
                    rule_id="R-STK-003", version=RULES, effect="R2", severity="ALTA"
                ),
            ),
            RuleAssessmentBinding(
                rule=stk_exception_rule,
                assessment=stk_exception,
                metadata=RuleMetadata(
                    rule_id="R-STK-004", version=RULES, effect="R1", severity="ALTA"
                ),
            ),
        ),
        base_result="COMPRAR",
    )

    assert vertical.crc_result.consolidated_result == "NO COMPRAR"
    assert vertical.crc_result.dominant_reason.startswith("R-FIN-001 demostrada")
    assert set(vertical.crc_result.conflicts) == {"R-STK-003:R2", "R-STK-004:R1"}
    assert tuple(item.rule_id for item in vertical.assessments) == (
        "R-FIN-001",
        "R-STK-003",
        "R-STK-004",
    )
