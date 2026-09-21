from datetime import date, datetime, timedelta
from decimal import Decimal

import pytest

from eios.core.models import DecisionContext, Evidence, PurchaseOperation
from eios.parameters import ResolvedConfiguration
from eios.parameters.center import Configuration
from eios.pricing import (
    CRITICAL_PRICE_BASELINE_EVIDENCE_SOURCE_TYPE,
    CriticalPriceBaseline,
    critical_price_baseline_ref,
    critical_price_purchase_ref,
)
from eios.rules.catalog import authorized_rule, authorized_rule_metadata
from eios.rules.orchestrator import CriticalPriceRuleInputs, run_domain_rules
from eios.rules.pricing import R_PRE_002, evaluate_r_pre_002


EVAL_DATE = date(2026, 9, 21)
EFFECTIVE_AT = datetime(2026, 9, 21, 12, 0, 0)


def _context():
    return DecisionContext(
        decision_id="DEC-PRE002-001",
        scenario_id="SCN-PRE002-001",
        rules_version="rules-v1",
        parameters_version="params-v1",
        data_snapshot_id="snap-v1",
    )


def _purchase(*, unit_price="110", currency="EUR"):
    return PurchaseOperation(
        decision_id="DEC-PRE002-001",
        scenario_id="SCN-PRE002-001",
        article_id="ART-001",
        supplier_id="SUP-001",
        quantity=Decimal("10"),
        unit_price=Decimal(unit_price),
        currency=currency,
        operation_date=EVAL_DATE,
    )


def _baseline(*, purchase=None, state="AVAILABLE", price="100", currency=None, **updates):
    purchase = purchase or _purchase()
    data = dict(
        decision_id="DEC-PRE002-001",
        scenario_id="SCN-PRE002-001",
        data_snapshot_id="snap-v1",
        company_scope="COMPANY-A",
        article_id="ART-001",
        evaluation_date=EVAL_DATE,
        currency=currency or purchase.currency,
        purchase_operation_ref=critical_price_purchase_ref(purchase),
        state=state,
        baseline_price=Decimal(price) if state == "AVAILABLE" and price is not None else None,
        source_ref="CRITICAL-PRICE-SOURCE",
        authority_ref="PRE002-AUTH-v0.1",
        methodology_ref="CRITICAL-PRICE-METHOD-v1",
        trace_refs=("TRACE-PRE002",),
    )
    data.update(updates)
    return CriticalPriceBaseline(**data)


def _baseline_evidence(baseline, *, state="DEMONSTRATED", demonstration_ref=None):
    return Evidence(
        evidence_id="EVID-PRE002-BASE",
        source_type=CRITICAL_PRICE_BASELINE_EVIDENCE_SOURCE_TYPE,
        source_ref="CRITICAL-PRICE-SOURCE",
        captured_at=EVAL_DATE,
        state=state,
        demonstration_ref=(
            critical_price_baseline_ref(baseline)
            if state == "DEMONSTRATED" and demonstration_ref is None
            else demonstration_ref
        ),
    )


def _resolution(value="10", *, unit="%", parameter_id="P-PRE-005",
                company_id="COMPANY-A", parameters_version="params-v1",
                effective_at=EFFECTIVE_AT, valid_from=None, valid_to=None):
    cfg = Configuration(
        configuration_id=405,
        parameter_id=parameter_id,
        company_id=company_id,
        value=str(value),
        value_type="decimal",
        unit=unit,
        valid_from=valid_from or EFFECTIVE_AT - timedelta(days=30),
        valid_to=valid_to,
        created_at=EFFECTIVE_AT - timedelta(days=40),
        updated_at=EFFECTIVE_AT - timedelta(days=10),
    )
    return ResolvedConfiguration(
        configuration=cfg,
        parameters_version=parameters_version,
        effective_at=effective_at,
    )


def _parameter_evidence(resolution, *, state="DEMONSTRATED", demonstration_ref=None):
    return Evidence(
        evidence_id="EVID-P-PRE-005",
        source_type="ParameterConfigurationEvidence",
        source_ref="parameter-center",
        captured_at=EVAL_DATE,
        state=state,
        demonstration_ref=(
            resolution.configuration_ref
            if state == "DEMONSTRATED" and demonstration_ref is None
            else demonstration_ref
        ),
    )


def _evaluate(*, purchase=None, baseline=None, baseline_evidence=None,
              resolution=None, parameter_evidence=None):
    purchase = purchase or _purchase()
    baseline = baseline or _baseline(purchase=purchase)
    baseline_evidence = baseline_evidence or _baseline_evidence(baseline)
    resolution = resolution or _resolution()
    parameter_evidence = parameter_evidence or _parameter_evidence(resolution)
    return evaluate_r_pre_002(
        purchase,
        _context(),
        authorized_rule(R_PRE_002, "rules-v1"),
        baseline,
        baseline_evidence,
        resolution,
        parameter_evidence,
    )


@pytest.mark.parametrize(
    ("purchase_price", "threshold", "expected"),
    (
        ("109.99", "10", "FALSE"),
        ("110", "10", "FALSE"),
        ("110.01", "10", "TRUE"),
        ("100", "0", "FALSE"),
        ("100.01", "0", "TRUE"),
    ),
)
def test_r_pre_002_strict_boundary(purchase_price, threshold, expected):
    purchase = _purchase(unit_price=purchase_price)
    baseline = _baseline(purchase=purchase)
    resolution = _resolution(threshold)
    result = _evaluate(
        purchase=purchase,
        baseline=baseline,
        baseline_evidence=_baseline_evidence(baseline),
        resolution=resolution,
        parameter_evidence=_parameter_evidence(resolution),
    )
    assert result.status == "EVALUABLE"
    assert result.outcome == expected
    assert result.evidence_ids == ["EVID-PRE002-BASE", "EVID-P-PRE-005"]


@pytest.mark.parametrize(
    "state",
    ("NOT_EVIDENCED", "CONFLICTING_DATA", "NOT_DETERMINABLE"),
)
def test_unavailable_baseline_is_not_evaluable(state):
    baseline = _baseline(state=state, price=None)
    result = _evaluate(baseline=baseline, baseline_evidence=_baseline_evidence(baseline))
    assert result.status == "NOT_EVALUABLE"
    assert result.outcome is None


def test_gap_baseline_evidence_is_not_evaluable():
    baseline = _baseline()
    result = _evaluate(
        baseline=baseline,
        baseline_evidence=_baseline_evidence(baseline, state="GAP"),
    )
    assert result.status == "NOT_EVALUABLE"


def test_forged_baseline_evidence_is_structural_error():
    baseline = _baseline()
    with pytest.raises(ValueError, match="no está vinculada"):
        _evaluate(
            baseline=baseline,
            baseline_evidence=_baseline_evidence(
                baseline,
                demonstration_ref="critical_price_baseline:forged",
            ),
        )


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("decision_id", "OTHER"),
        ("scenario_id", "OTHER"),
        ("data_snapshot_id", "OTHER"),
        ("article_id", "OTHER"),
        ("evaluation_date", date(2026, 9, 20)),
    ),
)
def test_baseline_identity_mismatch_is_structural(field, value):
    baseline = _baseline(**{field: value})
    evidence = Evidence(
        evidence_id="EVID-PRE002-BASE",
        source_type=CRITICAL_PRICE_BASELINE_EVIDENCE_SOURCE_TYPE,
        source_ref="CRITICAL-PRICE-SOURCE",
        captured_at=baseline.evaluation_date,
        state="DEMONSTRATED",
        demonstration_ref=critical_price_baseline_ref(baseline),
    )
    with pytest.raises(ValueError):
        _evaluate(baseline=baseline, baseline_evidence=evidence)


def test_purchase_binding_mismatch_is_structural():
    baseline = _baseline(purchase_operation_ref="critical_price_purchase:forged")
    with pytest.raises(ValueError, match="PurchaseOperation exacta"):
        _evaluate(baseline=baseline, baseline_evidence=_baseline_evidence(baseline))


def test_currency_mismatch_is_structural_and_no_fx_is_applied():
    baseline = _baseline(currency="USD")
    with pytest.raises(ValueError, match="otra moneda"):
        _evaluate(baseline=baseline, baseline_evidence=_baseline_evidence(baseline))


def test_missing_parameter_is_not_evaluable():
    baseline = _baseline()
    result = evaluate_r_pre_002(
        _purchase(),
        _context(),
        authorized_rule(R_PRE_002, "rules-v1"),
        baseline,
        _baseline_evidence(baseline),
        None,
        None,
    )
    assert result.status == "NOT_EVALUABLE"


@pytest.mark.parametrize(
    ("value", "unit"),
    (
        ("-1", "%"),
        ("NaN", "%"),
        ("Infinity", "%"),
        ("10", "points"),
    ),
)
def test_invalid_parameter_semantics_are_not_evaluable(value, unit):
    resolution = _resolution(value, unit=unit)
    result = _evaluate(
        resolution=resolution,
        parameter_evidence=_parameter_evidence(resolution),
    )
    assert result.status == "NOT_EVALUABLE"


@pytest.mark.parametrize(
    ("parameter_id", "company_id", "version", "effective_at"),
    (
        ("P-OTHER", "COMPANY-A", "params-v1", EFFECTIVE_AT),
        ("P-PRE-005", "OTHER", "params-v1", EFFECTIVE_AT),
        ("P-PRE-005", "COMPANY-A", "other", EFFECTIVE_AT),
        ("P-PRE-005", "COMPANY-A", "params-v1", datetime(2026, 9, 20, 12)),
    ),
)
def test_parameter_identity_mismatch_is_structural(parameter_id, company_id, version, effective_at):
    resolution = _resolution(
        parameter_id=parameter_id,
        company_id=company_id,
        parameters_version=version,
        effective_at=effective_at,
    )
    with pytest.raises(ValueError):
        _evaluate(
            resolution=resolution,
            parameter_evidence=_parameter_evidence(resolution),
        )


def test_inactive_parameter_is_structural_error():
    resolution = _resolution(valid_from=EFFECTIVE_AT + timedelta(days=1))
    with pytest.raises(ValueError, match="no está vigente"):
        _evaluate(
            resolution=resolution,
            parameter_evidence=_parameter_evidence(resolution),
        )


def test_parameter_evidence_gap_is_not_evaluable():
    resolution = _resolution()
    result = _evaluate(
        resolution=resolution,
        parameter_evidence=_parameter_evidence(resolution, state="GAP"),
    )
    assert result.status == "NOT_EVALUABLE"


def test_forged_parameter_ref_is_structural_error():
    resolution = _resolution()
    with pytest.raises(ValueError, match="P-PRE-005"):
        _evaluate(
            resolution=resolution,
            parameter_evidence=_parameter_evidence(
                resolution,
                demonstration_ref="parameter_configuration:forged",
            ),
        )


def test_custom_threshold_proves_ten_percent_is_not_hardcoded():
    purchase = _purchase(unit_price="115")
    baseline = _baseline(purchase=purchase, price="100")
    resolution = _resolution("20")
    result = _evaluate(
        purchase=purchase,
        baseline=baseline,
        baseline_evidence=_baseline_evidence(baseline),
        resolution=resolution,
        parameter_evidence=_parameter_evidence(resolution),
    )
    assert result.status == "EVALUABLE"
    assert result.outcome == "FALSE"


def test_metadata_is_r1_high_without_r0_escalation():
    metadata = authorized_rule_metadata(R_PRE_002, "rules-v1")
    assert metadata.effect == "R1"
    assert metadata.severity == "ALTA"


def test_orchestrator_executes_pre002_bundle():
    purchase = _purchase(unit_price="111")
    baseline = _baseline(purchase=purchase, price="100")
    resolution = _resolution("10")
    result = run_domain_rules(
        purchase=purchase,
        context=_context(),
        base_result="COMPRAR",
        critical_price=CriticalPriceRuleInputs(
            baseline=baseline,
            baseline_evidence=_baseline_evidence(baseline),
            critical_resolution=resolution,
            critical_evidence=_parameter_evidence(resolution),
        ),
    )
    assert R_PRE_002 in result.executed_rule_ids
    assessment = next(x for x in result.assessments if x.rule_id == R_PRE_002)
    assert assessment.outcome == "TRUE"
    assert result.crc_result.consolidated_result == "COMPRAR CONDICIONADO"


def test_orchestrator_omits_pre002_without_bundle():
    result = run_domain_rules(
        purchase=_purchase(),
        context=_context(),
        base_result="COMPRAR",
    )
    assert R_PRE_002 in result.omitted_rule_ids


def test_carrier_invariants_and_frozen_contract():
    with pytest.raises(Exception):
        _baseline(state="AVAILABLE", price=None)
    with pytest.raises(Exception):
        _baseline(state="NOT_EVIDENCED", price=None, baseline_price=Decimal("10"))
    with pytest.raises(Exception):
        _baseline(price="0")
    with pytest.raises(Exception):
        _baseline(price="NaN")
    with pytest.raises(ValueError, match="duplicados"):
        _baseline(trace_refs=("T1", "T1"))

    baseline = _baseline()
    with pytest.raises(Exception):
        baseline.currency = "USD"


def test_pre002_evaluator_does_not_consume_other_price_rule_carriers():
    import inspect
    import eios.rules.pricing as pricing_rules

    source = inspect.getsource(pricing_rules.evaluate_r_pre_002)
    assert "ComparablePriceReference" not in source
    assert "RecommendedPriceCeiling" not in source
    assert "PriceIntelligenceResult" not in source
