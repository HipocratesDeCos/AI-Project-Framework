from datetime import date, datetime, timezone
from decimal import Decimal

from eios.core.crc_mvp import RuleMetadata
from eios.core.models import Assessment, DecisionContext, Evidence, PurchaseOperation, Rule
from eios.finance import CashFlow, FinanceBasicInput, FinancialSnapshot, calculate_finance_basic
from eios.parameters import resolve_configuration_for_context
from eios.parameters.center import Configuration
from eios.rules import (
    FINANCE_BASIC_EVIDENCE_SOURCE_TYPE,
    PARAMETER_CONFIGURATION_EVIDENCE_SOURCE_TYPE,
    evaluate_r_fin_001,
    evaluate_r_fin_003,
    finance_basic_result_ref,
)
from eios.rules.runtime import RuleAssessmentBinding, run_assessment_set_vertical


AS_OF = date(2026, 9, 11)
EFFECTIVE = datetime(2026, 9, 11, 12, 0, tzinfo=timezone.utc)
RULES = "rules-v1"
PARAMS = "params-v1"
SNAPSHOT = "snapshot-v1"
DECISION = "D-FIN-3"
SCENARIO = "S-FIN-3"
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


def _payload() -> FinanceBasicInput:
    return FinanceBasicInput(
        context=_context(),
        snapshot=FinancialSnapshot(
            company_scope=COMPANY,
            as_of_date=AS_OF,
            data_snapshot_id=SNAPSHOT,
            currency="EUR",
            available_treasury=Decimal("120"),
            treasury_evidence_ref="bank:snapshot",
        ),
        cash_flows=(
            CashFlow(
                flow_id="PAY-PURCHASE",
                flow_type="PAYMENT",
                amount=Decimal("10"),
                currency="EUR",
                due_date=date(2026, 9, 20),
                due_date_evidenced=True,
                source_ref="invoice:purchase",
                evidence_state="DEMONSTRATED",
            ),
        ),
        horizon_days=30,
        treasury_minimum=Decimal("100"),
    )


def _configuration(parameter_id: str, value: str, unit: str, config_id: int) -> Configuration:
    return Configuration(
        configuration_id=config_id,
        parameter_id=parameter_id,
        company_id=COMPANY,
        value=value,
        value_type="decimal",
        unit=unit,
        valid_from=datetime(2026, 9, 1, tzinfo=timezone.utc),
        valid_to=None,
        created_at=datetime(2026, 9, 1, tzinfo=timezone.utc),
        updated_at=datetime(2026, 9, 1, tzinfo=timezone.utc),
    )


def _parameter_evidence(evidence_id: str, resolved) -> Evidence:
    return Evidence(
        evidence_id=evidence_id,
        source_type=PARAMETER_CONFIGURATION_EVIDENCE_SOURCE_TYPE,
        source_ref=f"parameter-center:{resolved.parameter_id}",
        captured_at=AS_OF,
        state="DEMONSTRATED",
        demonstration_ref=resolved.configuration_ref,
    )


def _finance_setup(p_fin_002: str = "100", p_fin_004: str = "15"):
    context = _context()
    payload = _payload()
    result = calculate_finance_basic(payload)
    minimum = resolve_configuration_for_context(
        _configuration("P-FIN-002", p_fin_002, "€", 2002), context, EFFECTIVE
    )
    margin = resolve_configuration_for_context(
        _configuration("P-FIN-004", p_fin_004, "%", 2004), context, EFFECTIVE
    )
    assert minimum is not None and margin is not None
    finance_evidence = Evidence(
        evidence_id="EV-FIN-BASIC",
        source_type=FINANCE_BASIC_EVIDENCE_SOURCE_TYPE,
        source_ref="finance:basic",
        captured_at=AS_OF,
        state="DEMONSTRATED",
        demonstration_ref=finance_basic_result_ref(result),
    )
    return (
        context,
        payload,
        result,
        finance_evidence,
        minimum,
        _parameter_evidence("EV-P-FIN-002", minimum),
        margin,
        _parameter_evidence("EV-P-FIN-004", margin),
    )


def test_r_fin_003_true_when_safety_margin_below_p_fin_004() -> None:
    (
        context,
        payload,
        result,
        finance_evidence,
        minimum,
        minimum_evidence,
        margin,
        margin_evidence,
    ) = _finance_setup()
    assert result.projection.financial_capacity_forecast == Decimal("110")
    assert result.safety_margin.value_pct == Decimal("10.0")

    assessment = evaluate_r_fin_003(
        _purchase(),
        context,
        Rule(rule_id="R-FIN-003", version=RULES, requires_evidence=True),
        payload,
        result,
        finance_evidence,
        minimum,
        minimum_evidence,
        margin,
        margin_evidence,
    )
    assert assessment.status == "EVALUABLE"
    assert assessment.outcome == "TRUE"
    assert assessment.evidence_ids == [
        "EV-FIN-BASIC",
        "EV-P-FIN-002",
        "EV-P-FIN-004",
    ]


def test_r_fin_003_false_when_safety_margin_meets_p_fin_004() -> None:
    setup = _finance_setup(p_fin_004="5")
    context, payload, result, finance_evidence, minimum, minimum_evidence, margin, margin_evidence = setup
    assessment = evaluate_r_fin_003(
        _purchase(),
        context,
        Rule(rule_id="R-FIN-003", version=RULES, requires_evidence=True),
        payload,
        result,
        finance_evidence,
        minimum,
        minimum_evidence,
        margin,
        margin_evidence,
    )
    assert assessment.status == "EVALUABLE"
    assert assessment.outcome == "FALSE"


def test_r_fin_003_rejects_margin_built_with_different_p_fin_002() -> None:
    setup = _finance_setup(p_fin_002="90")
    context, payload, result, finance_evidence, minimum, minimum_evidence, margin, margin_evidence = setup
    assessment = evaluate_r_fin_003(
        _purchase(),
        context,
        Rule(rule_id="R-FIN-003", version=RULES, requires_evidence=True),
        payload,
        result,
        finance_evidence,
        minimum,
        minimum_evidence,
        margin,
        margin_evidence,
    )
    assert assessment.status == "NOT_EVALUABLE"
    assert assessment.outcome is None


def test_fin_003_conditions_purchase_when_fin_001_is_not_triggered() -> None:
    (
        context,
        payload,
        result,
        finance_evidence,
        minimum,
        minimum_evidence,
        margin,
        margin_evidence,
    ) = _finance_setup()
    purchase = _purchase()
    fin_001_rule = Rule(rule_id="R-FIN-001", version=RULES, requires_evidence=True)
    fin_003_rule = Rule(rule_id="R-FIN-003", version=RULES, requires_evidence=True)

    fin_001 = evaluate_r_fin_001(
        purchase,
        context,
        fin_001_rule,
        payload,
        result,
        finance_evidence,
        minimum,
        minimum_evidence,
    )
    fin_003 = evaluate_r_fin_003(
        purchase,
        context,
        fin_003_rule,
        payload,
        result,
        finance_evidence,
        minimum,
        minimum_evidence,
        margin,
        margin_evidence,
    )
    assert fin_001.outcome == "FALSE"
    assert fin_003.outcome == "TRUE"

    stk_rule = Rule(rule_id="R-STK-003", version=RULES, requires_evidence=True)
    stk_assessment = Assessment(
        rule_id="R-STK-003",
        status="EVALUABLE",
        outcome="TRUE",
        evidence_ids=["EV-STK-003"],
        reason="Exceso M07 demostrado.",
    )

    vertical = run_assessment_set_vertical(
        purchase=purchase,
        context=context,
        bindings=(
            RuleAssessmentBinding(
                rule=fin_001_rule,
                assessment=fin_001,
                metadata=RuleMetadata(
                    rule_id="R-FIN-001", version=RULES, effect="R0", severity="CRÍTICA"
                ),
            ),
            RuleAssessmentBinding(
                rule=fin_003_rule,
                assessment=fin_003,
                metadata=RuleMetadata(
                    rule_id="R-FIN-003", version=RULES, effect="R1", severity="ALTA"
                ),
            ),
            RuleAssessmentBinding(
                rule=stk_rule,
                assessment=stk_assessment,
                metadata=RuleMetadata(
                    rule_id="R-STK-003", version=RULES, effect="R2", severity="ALTA"
                ),
            ),
        ),
        base_result="COMPRAR",
    )
    assert vertical.crc_result.consolidated_result == "COMPRAR CONDICIONADO"
    assert vertical.crc_result.dominant_reason.startswith("R-FIN-003 demostrada")
    assert set(vertical.crc_result.conflicts) == {"R-STK-003:R2"}
