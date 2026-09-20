from datetime import date, datetime, timedelta
from decimal import Decimal

import pytest

from eios.core.models import DecisionContext, Evidence, PurchaseOperation
from eios.parameters import ResolvedConfiguration
from eios.parameters.center import Configuration
from eios.rules.catalog import authorized_rule, authorized_rule_metadata
from eios.rules.orchestrator import StockCoverageNeedRuleInputs, run_domain_rules
from eios.rules.stock import R_STK_002, evaluate_r_stk_002
from eios.stock.rule_inputs import (
    JUSTIFIED_NEED_EVIDENCE_SOURCE_TYPE,
    PROJECTED_COVERAGE_EVIDENCE_SOURCE_TYPE,
    JustifiedNeedState,
    ProjectedCoverageAfterPurchase,
    justified_need_ref,
    projected_coverage_ref,
    stock_purchase_operation_ref,
)


EVAL_DATE = date(2026, 9, 20)
EFFECTIVE_AT = datetime(2026, 9, 20, 12, 0, 0)


def _context():
    return DecisionContext(
        decision_id="DEC-STK002-001",
        scenario_id="SCN-STK002-001",
        rules_version="rules-v1",
        parameters_version="params-v1",
        data_snapshot_id="snap-v1",
    )


def _purchase():
    return PurchaseOperation(
        decision_id="DEC-STK002-001",
        scenario_id="SCN-STK002-001",
        article_id="ART-001",
        supplier_id="SUP-001",
        quantity=Decimal("10"),
        unit_price=Decimal("5"),
        currency="EUR",
        operation_date=EVAL_DATE,
    )


def _common():
    return dict(
        decision_id="DEC-STK002-001",
        scenario_id="SCN-STK002-001",
        data_snapshot_id="snap-v1",
        company_scope="COMPANY-A",
        article_id="ART-001",
        evaluation_date=EVAL_DATE,
        purchase_operation_ref=stock_purchase_operation_ref(_purchase()),
        source_ref="STK002-SOURCE",
        authority_ref="STK002-AUTH-v0.1",
        trace_refs=("TRACE-STK002",),
    )


def _coverage(state="FINITE", days="100", **updates):
    data = _common()
    data.update(
        state=state,
        coverage_days=Decimal(days) if state == "FINITE" and days is not None else None,
    )
    data.update(updates)
    return ProjectedCoverageAfterPurchase(**data)


def _need(state="ABSENT", **updates):
    data = _common()
    data.update(state=state)
    data.update(updates)
    return JustifiedNeedState(**data)


def _coverage_evidence(carrier, *, state="DEMONSTRATED", demonstration_ref=None):
    return Evidence(
        evidence_id="EVID-STK002-COVERAGE",
        source_type=PROJECTED_COVERAGE_EVIDENCE_SOURCE_TYPE,
        source_ref="STK002-SOURCE",
        captured_at=EVAL_DATE,
        state=state,
        demonstration_ref=(
            projected_coverage_ref(carrier)
            if state == "DEMONSTRATED" and demonstration_ref is None
            else demonstration_ref
        ),
    )


def _need_evidence(carrier, *, state="DEMONSTRATED", demonstration_ref=None):
    return Evidence(
        evidence_id="EVID-STK002-NEED",
        source_type=JUSTIFIED_NEED_EVIDENCE_SOURCE_TYPE,
        source_ref="STK002-SOURCE",
        captured_at=EVAL_DATE,
        state=state,
        demonstration_ref=(
            justified_need_ref(carrier)
            if state == "DEMONSTRATED" and demonstration_ref is None
            else demonstration_ref
        ),
    )


def _resolution(
    value="90",
    *,
    parameter_id="P-STK-004",
    company_id="COMPANY-A",
    parameters_version="params-v1",
    unit="días",
    effective_at=EFFECTIVE_AT,
    valid_from=None,
    valid_to=None,
):
    configuration = Configuration(
        configuration_id=304,
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
        configuration=configuration,
        parameters_version=parameters_version,
        effective_at=effective_at,
    )


def _parameter_evidence(resolution, *, state="DEMONSTRATED", demonstration_ref=None):
    return Evidence(
        evidence_id="EVID-P-STK-004",
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


def _evaluate(
    *,
    coverage=None,
    need=None,
    coverage_evidence=None,
    need_evidence=None,
    resolution=None,
    parameter_evidence=None,
):
    coverage = coverage or _coverage()
    need = need or _need()
    coverage_evidence = coverage_evidence or _coverage_evidence(coverage)
    need_evidence = need_evidence or _need_evidence(need)
    resolution = resolution or _resolution()
    parameter_evidence = parameter_evidence or _parameter_evidence(resolution)
    return evaluate_r_stk_002(
        _purchase(),
        _context(),
        authorized_rule(R_STK_002, "rules-v1"),
        coverage,
        coverage_evidence,
        need,
        need_evidence,
        resolution,
        parameter_evidence,
    )


@pytest.mark.parametrize(
    ("days", "need_state", "expected"),
    (
        ("91", "ABSENT", "TRUE"),
        ("90", "ABSENT", "FALSE"),
        ("89", "ABSENT", "FALSE"),
        ("91", "PRESENT", "FALSE"),
        ("89", "PRESENT", "FALSE"),
    ),
)
def test_r_stk_002_exact_condition(days, need_state, expected):
    result = _evaluate(coverage=_coverage(days=days), need=_need(need_state))
    assert result.status == "EVALUABLE"
    assert result.outcome == expected
    assert result.evidence_ids == [
        "EVID-STK002-COVERAGE",
        "EVID-STK002-NEED",
        "EVID-P-STK-004",
    ]


def test_unbounded_coverage_with_absent_need_is_true():
    result = _evaluate(coverage=_coverage(state="UNBOUNDED", days=None))
    assert result.status == "EVALUABLE"
    assert result.outcome == "TRUE"


def test_unbounded_coverage_with_present_need_is_false():
    result = _evaluate(
        coverage=_coverage(state="UNBOUNDED", days=None),
        need=_need("PRESENT"),
    )
    assert result.outcome == "FALSE"


@pytest.mark.parametrize(
    "coverage_state",
    ("NOT_EVIDENCED", "CONFLICTING_DATA", "NOT_DETERMINABLE"),
)
def test_indeterminate_coverage_is_not_evaluable(coverage_state):
    result = _evaluate(coverage=_coverage(state=coverage_state, days=None))
    assert result.status == "NOT_EVALUABLE"
    assert result.outcome is None


@pytest.mark.parametrize(
    "need_state",
    ("NOT_EVIDENCED", "CONFLICTING_DATA", "NOT_DETERMINABLE"),
)
def test_indeterminate_need_is_not_evaluable_even_when_coverage_would_be_false(need_state):
    result = _evaluate(
        coverage=_coverage(days="10"),
        need=_need(need_state),
    )
    assert result.status == "NOT_EVALUABLE"
    assert result.outcome is None


def test_gap_carrier_evidence_is_not_evaluable():
    coverage = _coverage()
    result = _evaluate(
        coverage=coverage,
        coverage_evidence=_coverage_evidence(coverage, state="GAP"),
    )
    assert result.status == "NOT_EVALUABLE"


def test_forged_coverage_evidence_ref_is_structural_error():
    coverage = _coverage()
    with pytest.raises(ValueError, match="coverage_evidence"):
        _evaluate(
            coverage=coverage,
            coverage_evidence=_coverage_evidence(
                coverage,
                demonstration_ref="projected_coverage_after_purchase:forged",
            ),
        )


def test_forged_need_evidence_ref_is_structural_error():
    need = _need()
    with pytest.raises(ValueError, match="need_evidence"):
        _evaluate(
            need=need,
            need_evidence=_need_evidence(
                need,
                demonstration_ref="justified_need_state:forged",
            ),
        )


def test_purchase_binding_mismatch_is_structural_error():
    coverage = _coverage(purchase_operation_ref="stock_purchase_operation:forged")
    with pytest.raises(ValueError, match="PurchaseOperation exacta"):
        _evaluate(
            coverage=coverage,
            coverage_evidence=_coverage_evidence(coverage),
        )


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("decision_id", "OTHER"),
        ("scenario_id", "OTHER"),
        ("data_snapshot_id", "OTHER"),
        ("article_id", "OTHER"),
        ("evaluation_date", date(2026, 9, 19)),
    ),
)
def test_carrier_identity_mismatch_is_structural(field, value):
    coverage = _coverage(**{field: value})
    with pytest.raises(ValueError):
        _evaluate(
            coverage=coverage,
            coverage_evidence=Evidence(
                evidence_id="EVID-STK002-COVERAGE",
                source_type=PROJECTED_COVERAGE_EVIDENCE_SOURCE_TYPE,
                source_ref="STK002-SOURCE",
                captured_at=coverage.evaluation_date,
                state="DEMONSTRATED",
                demonstration_ref=projected_coverage_ref(coverage),
            ),
        )


def test_carriers_must_share_company_scope():
    need = _need(company_scope="OTHER")
    with pytest.raises(ValueError, match="company_scope"):
        _evaluate(need=need, need_evidence=_need_evidence(need))


def test_missing_parameter_is_not_evaluable():
    coverage = _coverage()
    need = _need()
    result = evaluate_r_stk_002(
        _purchase(),
        _context(),
        authorized_rule(R_STK_002, "rules-v1"),
        coverage,
        _coverage_evidence(coverage),
        need,
        _need_evidence(need),
        None,
        None,
    )
    assert result.status == "NOT_EVALUABLE"
    assert result.evidence_ids == [
        "EVID-STK002-COVERAGE",
        "EVID-STK002-NEED",
    ]


@pytest.mark.parametrize(
    "resolution",
    (
        _resolution(parameter_id="P-OTHER"),
        _resolution(parameters_version="other"),
        _resolution(company_id="OTHER"),
        _resolution(effective_at=datetime(2026, 9, 19, 12, 0, 0)),
    ),
)
def test_parameter_identity_mismatch_is_structural(resolution):
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


@pytest.mark.parametrize("unit", ("dias", "days", "%"))
def test_parameter_unit_mismatch_is_not_evaluable(unit):
    resolution = _resolution(unit=unit)
    result = _evaluate(
        resolution=resolution,
        parameter_evidence=_parameter_evidence(resolution),
    )
    assert result.status == "NOT_EVALUABLE"


@pytest.mark.parametrize("value", ("NaN", "Infinity", "-1", "not-a-number"))
def test_invalid_threshold_is_not_evaluable(value):
    resolution = _resolution(value=value)
    result = _evaluate(
        resolution=resolution,
        parameter_evidence=_parameter_evidence(resolution),
    )
    assert result.status == "NOT_EVALUABLE"


def test_parameter_evidence_gap_is_not_evaluable():
    resolution = _resolution()
    result = _evaluate(
        resolution=resolution,
        parameter_evidence=_parameter_evidence(resolution, state="GAP"),
    )
    assert result.status == "NOT_EVALUABLE"


def test_forged_parameter_ref_is_structural_error():
    resolution = _resolution()
    with pytest.raises(ValueError, match="P-STK-004"):
        _evaluate(
            resolution=resolution,
            parameter_evidence=_parameter_evidence(
                resolution,
                demonstration_ref="parameter_configuration:forged",
            ),
        )


def test_metadata_is_r2_high_without_r0_escalation():
    metadata = authorized_rule_metadata(R_STK_002, "rules-v1")
    assert metadata.effect == "R2"
    assert metadata.severity == "ALTA"


def test_custom_threshold_proves_90_is_not_hardcoded():
    resolution = _resolution("120")
    result = _evaluate(
        coverage=_coverage(days="100"),
        resolution=resolution,
        parameter_evidence=_parameter_evidence(resolution),
    )
    assert result.outcome == "FALSE"


def test_orchestrator_executes_r_stk_002_bundle():
    coverage = _coverage(days="100")
    need = _need("ABSENT")
    resolution = _resolution("90")
    result = run_domain_rules(
        purchase=_purchase(),
        context=_context(),
        base_result="COMPRAR",
        stock_coverage_need=StockCoverageNeedRuleInputs(
            coverage=coverage,
            coverage_evidence=_coverage_evidence(coverage),
            need=need,
            need_evidence=_need_evidence(need),
            maximum_resolution=resolution,
            parameter_evidence=_parameter_evidence(resolution),
        ),
    )
    assert R_STK_002 in result.executed_rule_ids
    assessment = next(x for x in result.assessments if x.rule_id == R_STK_002)
    assert assessment.outcome == "TRUE"
    assert result.crc_result.consolidated_result == "NEGOCIAR"


def test_orchestrator_omits_r_stk_002_without_bundle():
    result = run_domain_rules(
        purchase=_purchase(),
        context=_context(),
        base_result="COMPRAR",
    )
    assert R_STK_002 in result.omitted_rule_ids


def test_carrier_invariants():
    with pytest.raises(Exception):
        _coverage(state="FINITE", days=None)
    with pytest.raises(Exception):
        _coverage(state="UNBOUNDED", days="10")
    with pytest.raises(Exception):
        _coverage(days="-1")
    with pytest.raises(ValueError, match="duplicados"):
        _coverage(trace_refs=("T1", "T1"))
