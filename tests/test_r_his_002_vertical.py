from datetime import date, datetime, timezone
from decimal import Decimal

import pytest

from eios.core.crc_mvp import RuleMetadata
from eios.core.models import Assessment, DecisionContext, Evidence, PurchaseOperation, Rule
from eios.parameters import resolve_configuration_for_context
from eios.parameters.center import Configuration
from eios.pricing import PriceCounts, PriceIntelligenceInput, PriceIntelligenceResult
from eios.rules import (
    PARAMETER_CONFIGURATION_EVIDENCE_SOURCE_TYPE,
    PRICE_INTELLIGENCE_EVIDENCE_SOURCE_TYPE,
    RuleAssessmentBinding,
    evaluate_r_his_002,
    price_intelligence_result_ref,
    run_assessment_set_vertical,
)


EVAL = date(2026, 9, 11)
EFFECTIVE = datetime(2026, 9, 11, 12, 0, tzinfo=timezone.utc)
RULES = "rules-v1"
PARAMS = "params-v1"
SNAPSHOT = "snapshot-v1"
DECISION = "D-HIS-2"
SCENARIO = "S-HIS-2"
COMPANY = "COMP-1"
METHODOLOGY = "price-v1.3"


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
        unit_price=Decimal("12"),
        currency="EUR",
        operation_date=EVAL,
    )


def _pricing_input() -> PriceIntelligenceInput:
    return PriceIntelligenceInput(
        decision_context=_context(),
        purchase_operation=_purchase(),
        references=(),
        evidence_validations=(),
        methodology_version=METHODOLOGY,
    )


def _result(*, comparable: int, selected: int, sufficient: bool = False) -> PriceIntelligenceResult:
    assert comparable >= selected
    if selected == 0:
        pr_value = None
        currency = None
        sufficiency = "NOT_JUSTIFIABLE"
        pr_status = "PR_NOT_JUSTIFIABLE"
        reference_set = ()
    elif sufficient:
        pr_value = Decimal("10")
        currency = "EUR"
        sufficiency = "SUFFICIENT"
        pr_status = "PR_AVAILABLE"
        reference_set = tuple(f"REF-{i}" for i in range(selected))
    else:
        pr_value = Decimal("10")
        currency = "EUR"
        sufficiency = "LIMITED"
        pr_status = "PR_LIMITED"
        reference_set = tuple(f"REF-{i}" for i in range(selected))

    return PriceIntelligenceResult(
        decision_id=DECISION,
        scenario_id=SCENARIO,
        data_snapshot_id=SNAPSHOT,
        methodology_version=METHODOLOGY,
        pr_value=pr_value,
        currency=currency,
        sufficiency_status=sufficiency,
        pr_status=pr_status,
        pr_limitations=() if sufficient else ("LIMITED_HISTORY",),
        reference_set=reference_set,
        counts=PriceCounts(
            n_raw=max(comparable, 1),
            n_unique=max(comparable, 1),
            n_comparable=comparable,
            n_representative=selected,
            n_selected=selected,
        ),
        aggregation_method="MEDIAN_UNWEIGHTED",
        trace_references=("trace:price",),
    )


def _configuration(value: str = "2", company: str = COMPANY) -> Configuration:
    return Configuration(
        configuration_id=1006,
        parameter_id="P-PRE-006",
        company_id=company,
        value=value,
        value_type="integer",
        unit="operaciones",
        valid_from=datetime(2026, 9, 1, tzinfo=timezone.utc),
        valid_to=None,
        created_at=datetime(2026, 9, 1, tzinfo=timezone.utc),
        updated_at=datetime(2026, 9, 1, tzinfo=timezone.utc),
    )


def _evidence(result, resolved):
    pricing = Evidence(
        evidence_id="EV-PRICE",
        source_type=PRICE_INTELLIGENCE_EVIDENCE_SOURCE_TYPE,
        source_ref="pricing:c1",
        captured_at=EVAL,
        state="DEMONSTRATED",
        demonstration_ref=price_intelligence_result_ref(result),
    )
    parameter = Evidence(
        evidence_id="EV-P-PRE-006",
        source_type=PARAMETER_CONFIGURATION_EVIDENCE_SOURCE_TYPE,
        source_ref="parameter-center:P-PRE-006",
        captured_at=EVAL,
        state="DEMONSTRATED",
        demonstration_ref=resolved.configuration_ref,
    )
    return pricing, parameter


def _evaluate(result, threshold: str = "2"):
    context = _context()
    resolved = resolve_configuration_for_context(_configuration(threshold), context, EFFECTIVE)
    assert resolved is not None
    pricing_evidence, parameter_evidence = _evidence(result, resolved)
    assessment = evaluate_r_his_002(
        _purchase(),
        context,
        Rule(rule_id="R-HIS-002", version=RULES, requires_evidence=True),
        _pricing_input(),
        result,
        pricing_evidence,
        COMPANY,
        resolved,
        parameter_evidence,
    )
    return assessment


def test_r_his_002_true_when_comparable_history_below_parameter() -> None:
    result = _result(comparable=1, selected=0)
    assessment = _evaluate(result)
    assert assessment.status == "EVALUABLE"
    assert assessment.outcome == "TRUE"
    assert assessment.evidence_ids == ["EV-PRICE", "EV-P-PRE-006"]


def test_r_his_002_false_when_comparable_history_reaches_parameter() -> None:
    result = _result(comparable=2, selected=2, sufficient=True)
    assessment = _evaluate(result)
    assert assessment.status == "EVALUABLE"
    assert assessment.outcome == "FALSE"


def test_r_his_002_missing_parameter_is_not_evaluable() -> None:
    result = _result(comparable=1, selected=0)
    pricing_evidence = Evidence(
        evidence_id="EV-PRICE",
        source_type=PRICE_INTELLIGENCE_EVIDENCE_SOURCE_TYPE,
        source_ref="pricing:c1",
        captured_at=EVAL,
        state="DEMONSTRATED",
        demonstration_ref=price_intelligence_result_ref(result),
    )
    assessment = evaluate_r_his_002(
        _purchase(),
        _context(),
        Rule(rule_id="R-HIS-002", version=RULES, requires_evidence=True),
        _pricing_input(),
        result,
        pricing_evidence,
        COMPANY,
        None,
        None,
    )
    assert assessment.status == "NOT_EVALUABLE"
    assert assessment.outcome is None


def test_r_his_002_rejects_configuration_from_other_company() -> None:
    result = _result(comparable=1, selected=0)
    context = _context()
    resolved = resolve_configuration_for_context(
        _configuration(company="OTHER-COMPANY"), context, EFFECTIVE
    )
    assert resolved is not None
    pricing_evidence, parameter_evidence = _evidence(result, resolved)
    with pytest.raises(ValueError, match="otro company_id"):
        evaluate_r_his_002(
            _purchase(),
            context,
            Rule(rule_id="R-HIS-002", version=RULES, requires_evidence=True),
            _pricing_input(),
            result,
            pricing_evidence,
            COMPANY,
            resolved,
            parameter_evidence,
        )


def test_r3_history_warning_does_not_override_stock_r2() -> None:
    history = _evaluate(_result(comparable=1, selected=0))
    assert history.outcome == "TRUE"

    history_rule = Rule(rule_id="R-HIS-002", version=RULES, requires_evidence=True)
    stock_rule = Rule(rule_id="R-STK-003", version=RULES, requires_evidence=True)
    stock = Assessment(
        rule_id="R-STK-003",
        status="EVALUABLE",
        outcome="TRUE",
        evidence_ids=["EV-STK-003"],
        reason="Exceso de stock demostrado.",
    )

    vertical = run_assessment_set_vertical(
        purchase=_purchase(),
        context=_context(),
        bindings=(
            RuleAssessmentBinding(
                rule=history_rule,
                assessment=history,
                metadata=RuleMetadata(
                    rule_id="R-HIS-002",
                    version=RULES,
                    effect="R3",
                    severity="INFORMATIVA",
                ),
            ),
            RuleAssessmentBinding(
                rule=stock_rule,
                assessment=stock,
                metadata=RuleMetadata(
                    rule_id="R-STK-003",
                    version=RULES,
                    effect="R2",
                    severity="ALTA",
                ),
            ),
        ),
        base_result="COMPRAR",
    )
    assert vertical.crc_result.consolidated_result == "NEGOCIAR"
    assert vertical.crc_result.dominant_reason == "Exceso de stock demostrado."
    assert tuple(item.rule_id for item in vertical.assessments) == (
        "R-HIS-002",
        "R-STK-003",
    )
