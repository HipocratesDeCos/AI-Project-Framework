from datetime import date, datetime, timedelta
from decimal import Decimal

import pytest

from eios.core.models import DecisionContext, Evidence, PurchaseOperation
from eios.parameters import ResolvedConfiguration
from eios.parameters.center import Configuration
from eios.pricing import (
    COMPARABLE_PRICE_REFERENCE_EVIDENCE_SOURCE_TYPE,
    ComparablePriceReference,
    comparable_price_purchase_ref,
    comparable_price_reference_ref,
)
from eios.rules.catalog import authorized_rule, authorized_rule_metadata
from eios.rules.orchestrator import ComparableRecentPriceRuleInputs, run_domain_rules
from eios.rules.pricing import R_PRE_001, evaluate_r_pre_001


EVAL_DATE = date(2026, 5, 31)
EFFECTIVE_AT = datetime(2026, 5, 31, 12, 0, 0)


def _context():
    return DecisionContext(
        decision_id="DEC-PRE001-001",
        scenario_id="SCN-PRE001-001",
        rules_version="rules-v1",
        parameters_version="params-v1",
        data_snapshot_id="snap-v1",
    )


def _purchase(*, unit_price="105", operation_date=EVAL_DATE, currency="EUR"):
    return PurchaseOperation(
        decision_id="DEC-PRE001-001",
        scenario_id="SCN-PRE001-001",
        article_id="ART-001",
        supplier_id="SUP-001",
        quantity=Decimal("10"),
        unit_price=Decimal(unit_price),
        currency=currency,
        operation_date=operation_date,
    )


def _reference(
    *,
    purchase=None,
    reference_date=date(2026, 2, 28),
    reference_price="100",
    comparability_state="COMPARABLE",
    currency=None,
    **updates,
):
    purchase = purchase or _purchase()
    data = dict(
        decision_id="DEC-PRE001-001",
        scenario_id="SCN-PRE001-001",
        data_snapshot_id="snap-v1",
        company_scope="COMPANY-A",
        article_id="ART-001",
        evaluation_date=purchase.operation_date,
        currency=currency or purchase.currency,
        purchase_operation_ref=comparable_price_purchase_ref(purchase),
        reference_operation_ref="HIST-OP-001",
        reference_date=reference_date,
        reference_price=(
            Decimal(reference_price) if reference_price is not None else None
        ),
        comparability_state=comparability_state,
        source_ref="PRICE-HISTORY-SOURCE",
        authority_ref="PRE001-AUTH-v0.1",
        methodology_ref="COMPARABLE-REF-v1",
        trace_refs=("TRACE-PRE001",),
    )
    data.update(updates)
    return ComparablePriceReference(**data)


def _reference_evidence(reference, *, state="DEMONSTRATED", demonstration_ref=None):
    return Evidence(
        evidence_id="EVID-PRE001-REF",
        source_type=COMPARABLE_PRICE_REFERENCE_EVIDENCE_SOURCE_TYPE,
        source_ref="PRICE-HISTORY-SOURCE",
        captured_at=reference.evaluation_date,
        state=state,
        demonstration_ref=(
            comparable_price_reference_ref(reference)
            if state == "DEMONSTRATED" and demonstration_ref is None
            else demonstration_ref
        ),
    )


def _resolution(
    parameter_id,
    value,
    unit,
    *,
    company_id="COMPANY-A",
    parameters_version="params-v1",
    effective_at=EFFECTIVE_AT,
    valid_from=None,
    valid_to=None,
):
    configuration = Configuration(
        configuration_id=401 if parameter_id == "P-PRE-001" else 404,
        parameter_id=parameter_id,
        company_id=company_id,
        value=str(value),
        value_type="decimal",
        unit=unit,
        valid_from=valid_from or effective_at - timedelta(days=30),
        valid_to=valid_to,
        created_at=effective_at - timedelta(days=40),
        updated_at=effective_at - timedelta(days=10),
    )
    return ResolvedConfiguration(
        configuration=configuration,
        parameters_version=parameters_version,
        effective_at=effective_at,
    )


def _parameter_evidence(resolution, evidence_id):
    return Evidence(
        evidence_id=evidence_id,
        source_type="ParameterConfigurationEvidence",
        source_ref="parameter-center",
        captured_at=resolution.effective_at.date(),
        state="DEMONSTRATED",
        demonstration_ref=resolution.configuration_ref,
    )


def _evaluate(
    *,
    purchase=None,
    reference=None,
    reference_evidence=None,
    recency=None,
    recency_evidence=None,
    alert=None,
    alert_evidence=None,
):
    purchase = purchase or _purchase()
    reference = reference or _reference(purchase=purchase)
    reference_evidence = reference_evidence or _reference_evidence(reference)
    recency = recency or _resolution("P-PRE-001", "3", "meses")
    recency_evidence = recency_evidence or _parameter_evidence(recency, "EVID-P-PRE-001")
    alert = alert or _resolution("P-PRE-004", "5", "%")
    alert_evidence = alert_evidence or _parameter_evidence(alert, "EVID-P-PRE-004")
    return evaluate_r_pre_001(
        purchase,
        _context(),
        authorized_rule(R_PRE_001, "rules-v1"),
        reference,
        reference_evidence,
        recency,
        recency_evidence,
        alert,
        alert_evidence,
    )


@pytest.mark.parametrize(
    ("purchase_price", "threshold", "expected"),
    (
        ("104.99", "5", "FALSE"),
        ("105", "5", "TRUE"),
        ("105.01", "5", "TRUE"),
        ("100", "0", "TRUE"),
        ("99", "5", "FALSE"),
    ),
)
def test_r_pre_001_uplift_boundary(purchase_price, threshold, expected):
    purchase = _purchase(unit_price=purchase_price)
    reference = _reference(purchase=purchase)
    alert = _resolution("P-PRE-004", threshold, "%")
    result = _evaluate(
        purchase=purchase,
        reference=reference,
        reference_evidence=_reference_evidence(reference),
        alert=alert,
        alert_evidence=_parameter_evidence(alert, "EVID-P-PRE-004"),
    )
    assert result.status == "EVALUABLE"
    assert result.outcome == expected
    assert result.evidence_ids == [
        "EVID-PRE001-REF",
        "EVID-P-PRE-001",
        "EVID-P-PRE-004",
    ]


def test_calendar_month_clipping_makes_feb_28_recent_from_may_31():
    result = _evaluate(reference=_reference(reference_date=date(2026, 2, 28)))
    assert result.status == "EVALUABLE"
    assert result.outcome == "TRUE"


def test_reference_one_day_before_clipped_cutoff_is_false():
    result = _evaluate(reference=_reference(reference_date=date(2026, 2, 27)))
    assert result.status == "EVALUABLE"
    assert result.outcome == "FALSE"
    assert result.evidence_ids == ["EVID-PRE001-REF", "EVID-P-PRE-001"]


def test_future_reference_is_structural_error():
    reference = _reference(reference_date=date(2026, 6, 1))
    with pytest.raises(ValueError, match="futura"):
        _evaluate(reference=reference, reference_evidence=_reference_evidence(reference))


@pytest.mark.parametrize(
    "state",
    ("NOT_COMPARABLE", "NOT_EVIDENCED", "CONFLICTING_DATA", "NOT_DETERMINABLE"),
)
def test_non_comparable_or_indeterminate_reference_is_not_evaluable(state):
    reference = _reference(comparability_state=state)
    result = _evaluate(reference=reference, reference_evidence=_reference_evidence(reference))
    assert result.status == "NOT_EVALUABLE"
    assert result.outcome is None


def test_reference_evidence_gap_is_not_evaluable():
    reference = _reference()
    result = _evaluate(
        reference=reference,
        reference_evidence=_reference_evidence(reference, state="GAP"),
    )
    assert result.status == "NOT_EVALUABLE"


def test_forged_reference_evidence_is_structural_error():
    reference = _reference()
    with pytest.raises(ValueError, match="no está vinculada"):
        _evaluate(
            reference=reference,
            reference_evidence=_reference_evidence(
                reference,
                demonstration_ref="comparable_price_reference:forged",
            ),
        )


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("decision_id", "OTHER"),
        ("scenario_id", "OTHER"),
        ("data_snapshot_id", "OTHER"),
        ("article_id", "OTHER"),
        ("evaluation_date", date(2026, 5, 30)),
    ),
)
def test_reference_identity_mismatch_is_structural(field, value):
    reference = _reference(**{field: value})
    with pytest.raises(ValueError):
        _evaluate(reference=reference, reference_evidence=_reference_evidence(reference))


def test_purchase_binding_mismatch_is_structural():
    reference = _reference(purchase_operation_ref="comparable_price_purchase:forged")
    with pytest.raises(ValueError, match="PurchaseOperation exacta"):
        _evaluate(reference=reference, reference_evidence=_reference_evidence(reference))


def test_currency_mismatch_is_structural_and_no_fx_is_applied():
    reference = _reference(currency="USD")
    with pytest.raises(ValueError, match="otra moneda"):
        _evaluate(reference=reference, reference_evidence=_reference_evidence(reference))


@pytest.mark.parametrize(
    ("parameter_id", "value", "unit"),
    (
        ("P-PRE-001", "0", "meses"),
        ("P-PRE-001", "1.5", "meses"),
        ("P-PRE-001", "3", "days"),
        ("P-PRE-004", "-1", "%"),
        ("P-PRE-004", "NaN", "%"),
        ("P-PRE-004", "5", "points"),
    ),
)
def test_invalid_parameter_semantics_are_not_evaluable(parameter_id, value, unit):
    resolution = _resolution(parameter_id, value, unit)
    evidence = _parameter_evidence(
        resolution,
        "EVID-P-PRE-001" if parameter_id == "P-PRE-001" else "EVID-P-PRE-004",
    )
    kwargs = (
        dict(recency=resolution, recency_evidence=evidence)
        if parameter_id == "P-PRE-001"
        else dict(alert=resolution, alert_evidence=evidence)
    )
    result = _evaluate(**kwargs)
    assert result.status == "NOT_EVALUABLE"


@pytest.mark.parametrize(
    ("parameter_id", "company_id", "version", "effective_at"),
    (
        ("P-OTHER", "COMPANY-A", "params-v1", EFFECTIVE_AT),
        ("P-PRE-001", "OTHER", "params-v1", EFFECTIVE_AT),
        ("P-PRE-001", "COMPANY-A", "other", EFFECTIVE_AT),
        ("P-PRE-001", "COMPANY-A", "params-v1", datetime(2026, 5, 30, 12)),
    ),
)
def test_recency_parameter_identity_mismatch_is_structural(
    parameter_id, company_id, version, effective_at
):
    resolution = _resolution(
        parameter_id, "3", "meses",
        company_id=company_id,
        parameters_version=version,
        effective_at=effective_at,
    )
    with pytest.raises(ValueError):
        _evaluate(
            recency=resolution,
            recency_evidence=_parameter_evidence(resolution, "EVID-P-PRE-001"),
        )


def test_inactive_parameter_is_structural_error():
    resolution = _resolution(
        "P-PRE-001",
        "3",
        "meses",
        valid_from=EFFECTIVE_AT + timedelta(days=1),
    )
    with pytest.raises(ValueError, match="no está vigente"):
        _evaluate(
            recency=resolution,
            recency_evidence=_parameter_evidence(resolution, "EVID-P-PRE-001"),
        )


def test_missing_parameters_fail_closed():
    reference = _reference()
    result = evaluate_r_pre_001(
        _purchase(),
        _context(),
        authorized_rule(R_PRE_001, "rules-v1"),
        reference,
        _reference_evidence(reference),
        None,
        None,
        None,
        None,
    )
    assert result.status == "NOT_EVALUABLE"


def test_custom_parameters_prove_no_three_month_or_five_percent_defaults():
    recency = _resolution("P-PRE-001", "1", "meses")
    alert = _resolution("P-PRE-004", "20", "%")
    reference = _reference(reference_date=date(2026, 4, 30))
    purchase = _purchase(unit_price="110")
    reference = _reference(
        purchase=purchase,
        reference_date=date(2026, 4, 30),
        reference_price="100",
    )
    result = _evaluate(
        purchase=purchase,
        reference=reference,
        reference_evidence=_reference_evidence(reference),
        recency=recency,
        recency_evidence=_parameter_evidence(recency, "EVID-P-PRE-001"),
        alert=alert,
        alert_evidence=_parameter_evidence(alert, "EVID-P-PRE-004"),
    )
    assert result.status == "EVALUABLE"
    assert result.outcome == "FALSE"


def test_metadata_is_r2_high():
    metadata = authorized_rule_metadata(R_PRE_001, "rules-v1")
    assert metadata.effect == "R2"
    assert metadata.severity == "ALTA"


def test_orchestrator_executes_pre001_bundle():
    purchase = _purchase(unit_price="105")
    reference = _reference(purchase=purchase)
    recency = _resolution("P-PRE-001", "3", "meses")
    alert = _resolution("P-PRE-004", "5", "%")
    result = run_domain_rules(
        purchase=purchase,
        context=_context(),
        base_result="COMPRAR",
        comparable_recent_price=ComparableRecentPriceRuleInputs(
            reference=reference,
            reference_evidence=_reference_evidence(reference),
            recency_resolution=recency,
            recency_evidence=_parameter_evidence(recency, "EVID-P-PRE-001"),
            alert_resolution=alert,
            alert_evidence=_parameter_evidence(alert, "EVID-P-PRE-004"),
        ),
    )
    assert R_PRE_001 in result.executed_rule_ids
    assessment = next(x for x in result.assessments if x.rule_id == R_PRE_001)
    assert assessment.outcome == "TRUE"
    assert result.crc_result.consolidated_result == "NEGOCIAR"


def test_orchestrator_omits_pre001_without_bundle():
    result = run_domain_rules(
        purchase=_purchase(),
        context=_context(),
        base_result="COMPRAR",
    )
    assert R_PRE_001 in result.omitted_rule_ids


def test_reference_carrier_invariants():
    with pytest.raises(Exception):
        _reference(reference_price="0")
    with pytest.raises(Exception):
        _reference(reference_price="NaN")
    with pytest.raises(Exception):
        _reference(reference_price=None)
    with pytest.raises(ValueError, match="duplicados"):
        _reference(trace_refs=("T1", "T1"))

    reference = _reference()
    with pytest.raises(Exception):
        reference.currency = "USD"


def test_pre001_evaluator_does_not_consume_price_intelligence_result():
    import inspect
    import eios.rules.pricing as pricing_rules

    source = inspect.getsource(pricing_rules.evaluate_r_pre_001)
    assert "PriceIntelligenceResult" not in source
    assert "run_price_intelligence" not in source
