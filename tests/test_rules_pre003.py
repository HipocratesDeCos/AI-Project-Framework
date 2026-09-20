from datetime import date
from decimal import Decimal

import pytest

from eios.core.models import DecisionContext, Evidence, PurchaseOperation
from eios.pricing import (
    RECOMMENDED_PRICE_CEILING_EVIDENCE_SOURCE_TYPE,
    RecommendedPriceCeiling,
    recommended_price_ceiling_ref,
    recommended_price_purchase_ref,
)
from eios.rules.catalog import authorized_rule, authorized_rule_metadata
from eios.rules.orchestrator import RecommendedPriceRuleInputs, run_domain_rules
from eios.rules.pricing import R_PRE_003, evaluate_r_pre_003


EVAL_DATE = date(2026, 9, 20)


def _context():
    return DecisionContext(
        decision_id="DEC-PRE003-001",
        scenario_id="SCN-PRE003-001",
        rules_version="rules-v1",
        parameters_version="params-v1",
        data_snapshot_id="snap-v1",
    )


def _purchase(*, unit_price="100", currency="EUR"):
    return PurchaseOperation(
        decision_id="DEC-PRE003-001",
        scenario_id="SCN-PRE003-001",
        article_id="ART-001",
        supplier_id="SUP-001",
        quantity=Decimal("10"),
        unit_price=Decimal(unit_price),
        currency=currency,
        operation_date=EVAL_DATE,
    )


def _ceiling(
    *,
    state="AVAILABLE",
    price="100",
    purchase=None,
    currency=None,
    **updates,
):
    purchase = purchase or _purchase()
    data = dict(
        decision_id="DEC-PRE003-001",
        scenario_id="SCN-PRE003-001",
        data_snapshot_id="snap-v1",
        company_scope="COMPANY-A",
        article_id="ART-001",
        evaluation_date=EVAL_DATE,
        currency=currency or purchase.currency,
        purchase_operation_ref=recommended_price_purchase_ref(purchase),
        state=state,
        ceiling_price=Decimal(price) if state == "AVAILABLE" and price is not None else None,
        source_ref="PMR-SOURCE",
        authority_ref="PRE003-AUTH-v0.1",
        methodology_ref="PMR-METHOD-v1",
        trace_refs=("TRACE-PMR-001",),
    )
    data.update(updates)
    return RecommendedPriceCeiling(**data)


def _evidence(carrier, *, state="DEMONSTRATED", demonstration_ref=None):
    return Evidence(
        evidence_id="EVID-PMR-001",
        source_type=RECOMMENDED_PRICE_CEILING_EVIDENCE_SOURCE_TYPE,
        source_ref="PMR-SOURCE",
        captured_at=carrier.evaluation_date,
        state=state,
        demonstration_ref=(
            recommended_price_ceiling_ref(carrier)
            if state == "DEMONSTRATED" and demonstration_ref is None
            else demonstration_ref
        ),
    )


def _evaluate(*, purchase=None, ceiling=None, evidence=None):
    purchase = purchase or _purchase()
    ceiling = ceiling or _ceiling(purchase=purchase)
    evidence = evidence or _evidence(ceiling)
    return evaluate_r_pre_003(
        purchase,
        _context(),
        authorized_rule(R_PRE_003, "rules-v1"),
        ceiling,
        evidence,
    )


@pytest.mark.parametrize(
    ("purchase_price", "ceiling_price", "expected"),
    (
        ("99.99", "100", "TRUE"),
        ("100", "100", "TRUE"),
        ("100.01", "100", "FALSE"),
        ("0", "0", "TRUE"),
    ),
)
def test_r_pre_003_exact_boundary(purchase_price, ceiling_price, expected):
    purchase = _purchase(unit_price=purchase_price)
    ceiling = _ceiling(price=ceiling_price, purchase=purchase)
    result = _evaluate(purchase=purchase, ceiling=ceiling, evidence=_evidence(ceiling))
    assert result.status == "EVALUABLE"
    assert result.outcome == expected
    assert result.evidence_ids == ["EVID-PMR-001"]


@pytest.mark.parametrize(
    "state",
    ("NOT_EVIDENCED", "CONFLICTING_DATA", "NOT_DETERMINABLE"),
)
def test_unavailable_ceiling_is_not_evaluable(state):
    ceiling = _ceiling(state=state, price=None)
    result = _evaluate(ceiling=ceiling, evidence=_evidence(ceiling))
    assert result.status == "NOT_EVALUABLE"
    assert result.outcome is None


def test_gap_evidence_is_not_evaluable_not_false():
    ceiling = _ceiling()
    result = _evaluate(
        ceiling=ceiling,
        evidence=_evidence(ceiling, state="GAP"),
    )
    assert result.status == "NOT_EVALUABLE"
    assert result.outcome is None


def test_forged_evidence_ref_is_structural_error():
    ceiling = _ceiling()
    with pytest.raises(ValueError, match="no está vinculada"):
        _evaluate(
            ceiling=ceiling,
            evidence=_evidence(
                ceiling,
                demonstration_ref="recommended_price_ceiling:forged",
            ),
        )


@pytest.mark.parametrize(
    ("field", "value", "match"),
    (
        ("decision_id", "OTHER", "otra decisión"),
        ("scenario_id", "OTHER", "otro escenario"),
        ("data_snapshot_id", "OTHER", "data_snapshot_id"),
        ("article_id", "OTHER", "otro artículo"),
        ("evaluation_date", date(2026, 9, 19), "evaluation_date"),
    ),
)
def test_identity_mismatch_is_structural(field, value, match):
    ceiling = _ceiling(**{field: value})
    with pytest.raises(ValueError, match=match):
        _evaluate(ceiling=ceiling, evidence=_evidence(ceiling))


def test_purchase_binding_mismatch_is_structural():
    ceiling = _ceiling(purchase_operation_ref="recommended_price_purchase:forged")
    with pytest.raises(ValueError, match="PurchaseOperation exacta"):
        _evaluate(ceiling=ceiling, evidence=_evidence(ceiling))


def test_currency_mismatch_is_structural_and_no_fx_is_applied():
    purchase = _purchase(currency="EUR")
    ceiling = _ceiling(purchase=purchase, currency="USD")
    with pytest.raises(ValueError, match="otra moneda"):
        _evaluate(purchase=purchase, ceiling=ceiling, evidence=_evidence(ceiling))


def test_metadata_is_r3_informative():
    metadata = authorized_rule_metadata(R_PRE_003, "rules-v1")
    assert metadata.effect == "R3"
    assert metadata.severity == "INFORMATIVA"


def test_orchestrator_executes_r_pre_003_from_independent_bundle():
    purchase = _purchase(unit_price="90")
    ceiling = _ceiling(price="100", purchase=purchase)
    result = run_domain_rules(
        purchase=purchase,
        context=_context(),
        base_result="NEGOCIAR",
        recommended_price=RecommendedPriceRuleInputs(
            ceiling=ceiling,
            ceiling_evidence=_evidence(ceiling),
        ),
    )
    assert R_PRE_003 in result.executed_rule_ids
    assessment = next(x for x in result.assessments if x.rule_id == R_PRE_003)
    assert assessment.outcome == "TRUE"
    assert result.crc_result.consolidated_result == "NEGOCIAR"


def test_orchestrator_omits_r_pre_003_without_bundle():
    result = run_domain_rules(
        purchase=_purchase(),
        context=_context(),
        base_result="COMPRAR",
    )
    assert R_PRE_003 in result.omitted_rule_ids
    assert R_PRE_003 not in result.executed_rule_ids


def test_carrier_invariants_and_frozen_contract():
    with pytest.raises(Exception):
        _ceiling(state="AVAILABLE", price=None)
    with pytest.raises(Exception):
        _ceiling(state="NOT_EVIDENCED", price=None, ceiling_price=Decimal("10"))
    with pytest.raises(Exception):
        _ceiling(price="-1")
    with pytest.raises(ValueError, match="duplicados"):
        _ceiling(trace_refs=("T1", "T1"))

    carrier = _ceiling()
    with pytest.raises(Exception):
        carrier.currency = "USD"


def test_rule_module_does_not_depend_on_price_intelligence_result():
    import inspect
    import eios.rules.pricing as pricing_rules

    source = inspect.getsource(pricing_rules.evaluate_r_pre_003)
    assert "PriceIntelligenceResult" not in source
    assert "run_price_intelligence" not in source
