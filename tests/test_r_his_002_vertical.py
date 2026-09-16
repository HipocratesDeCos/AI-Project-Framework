from dataclasses import fields
from datetime import date, datetime, timezone
from decimal import Decimal
from inspect import signature

import pytest

from eios.core.crc_mvp import RuleMetadata
from eios.core.models import (
    Assessment,
    DecisionContext,
    Evidence,
    EvidenceValidation,
    PurchaseOperation,
    Rule,
)
from eios.parameters import resolve_configuration_for_context
from eios.parameters.center import Configuration
from eios.pricing import (
    PriceIntelligenceAssessmentContext,
    PriceIntelligenceInput,
    PriceReference,
    SufficiencyObservation,
    run_price_intelligence,
)
from eios.rules import (
    PARAMETER_CONFIGURATION_EVIDENCE_SOURCE_TYPE,
    PRICE_INTELLIGENCE_EVIDENCE_SOURCE_TYPE,
    evaluate_r_his_002,
    price_intelligence_result_ref,
)
from eios.rules.orchestrator import HistorySufficiencyRuleInputs
from eios.rules.runtime import RuleAssessmentBinding, run_assessment_set_vertical


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


def _pricing_input(
    comparable: int,
    *,
    context: DecisionContext | None = None,
    purchase: PurchaseOperation | None = None,
) -> PriceIntelligenceInput:
    context = context or _context()
    purchase = purchase or _purchase()
    references = tuple(
        PriceReference(
            source_transaction_id=f"REF-{index}",
            article_identity=purchase.article_id,
            supplier_identity=purchase.supplier_id,
            quantity=Decimal("1"),
            unit="unidad",
            unit_price=Decimal("10") + Decimal(index),
            currency=purchase.currency,
            operation_date=EVAL,
            evidence_refs=(f"EV-REF-{index}",),
        )
        for index in range(comparable)
    )
    validations = tuple(
        EvidenceValidation(
            evidence_id=f"EV-REF-{index}",
            status="VALID",
            reason="Evidencia de referencia validada.",
        )
        for index in range(comparable)
    )
    return PriceIntelligenceInput(
        decision_context=context,
        purchase_operation=purchase,
        references=references,
        evidence_validations=validations,
        methodology_version=METHODOLOGY,
    )


def _pricing_assessment_context() -> PriceIntelligenceAssessmentContext:
    return PriceIntelligenceAssessmentContext(sufficiency=SufficiencyObservation())


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


def _pricing_evidence(
    pricing_input: PriceIntelligenceInput,
    pricing_context: PriceIntelligenceAssessmentContext,
    *,
    state: str = "DEMONSTRATED",
    demonstration_ref: str | None = None,
) -> Evidence:
    if state == "DEMONSTRATED" and demonstration_ref is None:
        result = run_price_intelligence(pricing_input, pricing_context)
        demonstration_ref = price_intelligence_result_ref(result)
    return Evidence(
        evidence_id="EV-PRICE",
        source_type=PRICE_INTELLIGENCE_EVIDENCE_SOURCE_TYPE,
        source_ref="pricing:c1",
        captured_at=EVAL,
        state=state,
        demonstration_ref=demonstration_ref,
    )


def _parameter_evidence(resolved) -> Evidence:
    return Evidence(
        evidence_id="EV-P-PRE-006",
        source_type=PARAMETER_CONFIGURATION_EVIDENCE_SOURCE_TYPE,
        source_ref="parameter-center:P-PRE-006",
        captured_at=EVAL,
        state="DEMONSTRATED",
        demonstration_ref=resolved.configuration_ref,
    )


def _evaluate(comparable: int, threshold: str = "2") -> Assessment:
    context = _context()
    pricing_input = _pricing_input(comparable)
    pricing_context = _pricing_assessment_context()
    resolved = resolve_configuration_for_context(_configuration(threshold), context, EFFECTIVE)
    assert resolved is not None
    return evaluate_r_his_002(
        _purchase(),
        context,
        Rule(rule_id="R-HIS-002", version=RULES, requires_evidence=True),
        pricing_input,
        pricing_context,
        _pricing_evidence(pricing_input, pricing_context),
        COMPANY,
        resolved,
        _parameter_evidence(resolved),
    )


def test_r_his_002_true_when_comparable_history_below_parameter() -> None:
    assessment = _evaluate(comparable=1)
    assert assessment.status == "EVALUABLE"
    assert assessment.outcome == "TRUE"
    assert assessment.evidence_ids == ["EV-PRICE", "EV-P-PRE-006"]


def test_r_his_002_false_when_comparable_history_reaches_parameter() -> None:
    assessment = _evaluate(comparable=2)
    assert assessment.status == "EVALUABLE"
    assert assessment.outcome == "FALSE"


def test_r_his_002_missing_parameter_is_not_evaluable() -> None:
    pricing_input = _pricing_input(1)
    pricing_context = _pricing_assessment_context()
    assessment = evaluate_r_his_002(
        _purchase(),
        _context(),
        Rule(rule_id="R-HIS-002", version=RULES, requires_evidence=True),
        pricing_input,
        pricing_context,
        _pricing_evidence(pricing_input, pricing_context),
        COMPANY,
        None,
        None,
    )
    assert assessment.status == "NOT_EVALUABLE"
    assert assessment.outcome is None


def test_r_his_002_rejects_configuration_from_other_company() -> None:
    context = _context()
    pricing_input = _pricing_input(1)
    pricing_context = _pricing_assessment_context()
    resolved = resolve_configuration_for_context(
        _configuration(company="OTHER-COMPANY"), context, EFFECTIVE
    )
    assert resolved is not None
    with pytest.raises(ValueError, match="otro company_id"):
        evaluate_r_his_002(
            _purchase(),
            context,
            Rule(rule_id="R-HIS-002", version=RULES, requires_evidence=True),
            pricing_input,
            pricing_context,
            _pricing_evidence(pricing_input, pricing_context),
            COMPANY,
            resolved,
            _parameter_evidence(resolved),
        )


def test_r_his_002_rejects_pricing_evidence_for_another_result() -> None:
    pricing_input = _pricing_input(1)
    pricing_context = _pricing_assessment_context()
    other_result = run_price_intelligence(_pricing_input(2), pricing_context)
    context = _context()
    resolved = resolve_configuration_for_context(_configuration(), context, EFFECTIVE)
    assert resolved is not None
    forged_evidence = _pricing_evidence(
        pricing_input,
        pricing_context,
        demonstration_ref=price_intelligence_result_ref(other_result),
    )

    with pytest.raises(ValueError, match="no está vinculada"):
        evaluate_r_his_002(
            _purchase(),
            context,
            Rule(rule_id="R-HIS-002", version=RULES, requires_evidence=True),
            pricing_input,
            pricing_context,
            forged_evidence,
            COMPANY,
            resolved,
            _parameter_evidence(resolved),
        )


def test_r_his_002_gap_pricing_evidence_is_not_evaluable() -> None:
    pricing_input = _pricing_input(1)
    pricing_context = _pricing_assessment_context()
    context = _context()
    resolved = resolve_configuration_for_context(_configuration(), context, EFFECTIVE)
    assert resolved is not None

    assessment = evaluate_r_his_002(
        _purchase(),
        context,
        Rule(rule_id="R-HIS-002", version=RULES, requires_evidence=True),
        pricing_input,
        pricing_context,
        _pricing_evidence(pricing_input, pricing_context, state="GAP"),
        COMPANY,
        resolved,
        _parameter_evidence(resolved),
    )

    assert assessment.status == "NOT_EVALUABLE"
    assert assessment.outcome is None


def test_r_his_002_rejects_pricing_input_from_other_context() -> None:
    other_context = _context().model_copy(update={"decision_id": "D-OTHER"})
    other_purchase = _purchase().model_copy(update={"decision_id": "D-OTHER"})
    pricing_input = _pricing_input(1, context=other_context, purchase=other_purchase)
    pricing_context = _pricing_assessment_context()

    with pytest.raises(ValueError, match="otro DecisionContext"):
        evaluate_r_his_002(
            _purchase(),
            _context(),
            Rule(rule_id="R-HIS-002", version=RULES, requires_evidence=True),
            pricing_input,
            pricing_context,
            _pricing_evidence(pricing_input, pricing_context),
            COMPANY,
            None,
            None,
        )


def test_r_his_002_api_has_no_detached_pricing_result() -> None:
    parameters = signature(evaluate_r_his_002).parameters
    bundle_fields = {field.name for field in fields(HistorySufficiencyRuleInputs)}

    assert "pricing_result" not in parameters
    assert "pricing_result" not in bundle_fields
    assert "pricing_assessment_context" in parameters
    assert "pricing_assessment_context" in bundle_fields


def test_r3_history_warning_does_not_override_stock_r2() -> None:
    history = _evaluate(comparable=1)
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
