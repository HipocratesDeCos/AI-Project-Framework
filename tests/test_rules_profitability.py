from datetime import date, datetime, timedelta
from decimal import Decimal

import pytest

from eios.core.models import DecisionContext, Evidence, PurchaseOperation
from eios.parameters import ResolvedConfiguration
from eios.parameters.center import Configuration
from eios.profitability import (
    AuthorizedCostBasis,
    AuthorizedSaleBasis,
    ProfitabilityInput,
    run_provenanced_profitability,
)
from eios.rules.catalog import authorized_rule, authorized_rule_metadata, implemented_rule_ids
from eios.rules.orchestrator import ProfitabilityRuleInputs, run_domain_rules
from eios.rules.profitability import (
    MGEParameterBundle,
    PERCENTAGE_POINTS_UNIT,
    PERCENT_UNIT,
    PROFITABILITY_EVIDENCE_SOURCE_TYPE,
    P_MGE_001,
    P_MGE_002,
    P_MGE_003,
    R_MGE_001,
    R_MGE_002,
    R_MGE_003,
    evaluate_r_mge_001,
    evaluate_r_mge_002,
    evaluate_r_mge_003,
    profitability_result_ref,
)


EVAL_DATE = date(2026, 9, 20)
EFFECTIVE_AT = datetime(2026, 9, 20, 12, 0, 0)


def _context():
    return DecisionContext(
        decision_id="DEC-MGE-RULE-001",
        scenario_id="SCN-MGE-RULE-001",
        rules_version="rules-v1",
        parameters_version="params-v1",
        data_snapshot_id="snap-v1",
    )


def _purchase():
    return PurchaseOperation(
        decision_id="DEC-MGE-RULE-001",
        scenario_id="SCN-MGE-RULE-001",
        article_id="ART-001",
        supplier_id="SUP-001",
        quantity=Decimal("10"),
        unit_price=Decimal("5"),
        currency="EUR",
        operation_date=EVAL_DATE,
    )


def _basis_common():
    return dict(
        state="KNOWN",
        decision_id="DEC-MGE-RULE-001",
        scenario_id="SCN-MGE-RULE-001",
        data_snapshot_id="snap-v1",
        company_scope="COMPANY-A",
        article_id="ART-001",
        evaluation_date=EVAL_DATE,
        currency="EUR",
        economic_basis_ref="BASIS:UNIT",
        authority_ref="MGE-AUTH-v0.1",
    )


def _execution(margin_pct: str):
    margin = Decimal(margin_pct)
    sale = Decimal("100")
    cost = sale - margin
    payload = ProfitabilityInput(
        context=_context(),
        purchase_operation=_purchase(),
        company_scope="COMPANY-A",
        evaluation_date=EVAL_DATE,
        sale_basis=AuthorizedSaleBasis(
            **_basis_common(),
            value=sale,
            source_ref="SALE-SRC",
            trace_refs=("TRACE-SALE",),
        ),
        cost_basis=AuthorizedCostBasis(
            **_basis_common(),
            value=cost,
            source_ref="COST-SRC",
            trace_refs=("TRACE-COST",),
        ),
        methodology_version="MGE-AUTH-v0.1",
    )
    return run_provenanced_profitability(payload)


def _zero_sale_execution():
    payload = ProfitabilityInput(
        context=_context(),
        purchase_operation=_purchase(),
        company_scope="COMPANY-A",
        evaluation_date=EVAL_DATE,
        sale_basis=AuthorizedSaleBasis(
            **_basis_common(),
            value=Decimal("0"),
            source_ref="SALE-SRC",
            trace_refs=("TRACE-SALE",),
        ),
        cost_basis=AuthorizedCostBasis(
            **_basis_common(),
            value=Decimal("70"),
            source_ref="COST-SRC",
            trace_refs=("TRACE-COST",),
        ),
        methodology_version="MGE-AUTH-v0.1",
    )
    return run_provenanced_profitability(payload)


def _profitability_evidence(execution, *, state="DEMONSTRATED", demonstration_ref=None):
    ref = profitability_result_ref(execution.profitability_result)
    return Evidence(
        evidence_id="EVID-MGE-RESULT",
        source_type=PROFITABILITY_EVIDENCE_SOURCE_TYPE,
        source_ref="mge-rule-test",
        captured_at=EVAL_DATE,
        state=state,
        demonstration_ref=(ref if demonstration_ref is None and state == "DEMONSTRATED" else demonstration_ref),
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
        configuration_id={
            P_MGE_001: 101,
            P_MGE_002: 102,
            P_MGE_003: 103,
        }.get(parameter_id, 999),
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


def _parameter_evidence(resolution, evidence_id, *, state="DEMONSTRATED", demonstration_ref=None):
    return Evidence(
        evidence_id=evidence_id,
        source_type="ParameterConfigurationEvidence",
        source_ref="parameter-center",
        captured_at=EVAL_DATE,
        state=state,
        demonstration_ref=(
            resolution.configuration_ref
            if demonstration_ref is None and state == "DEMONSTRATED"
            else demonstration_ref
        ),
    )


def _bundle(
    *,
    minimum="20",
    target="30",
    tolerance="3",
    minimum_unit=PERCENT_UNIT,
    target_unit=PERCENT_UNIT,
    tolerance_unit=PERCENTAGE_POINTS_UNIT,
):
    minimum_resolution = _resolution(P_MGE_001, minimum, minimum_unit)
    target_resolution = _resolution(P_MGE_002, target, target_unit)
    tolerance_resolution = _resolution(P_MGE_003, tolerance, tolerance_unit)
    return MGEParameterBundle(
        minimum_resolution=minimum_resolution,
        minimum_evidence=_parameter_evidence(minimum_resolution, "EVID-P-MGE-001"),
        target_resolution=target_resolution,
        target_evidence=_parameter_evidence(target_resolution, "EVID-P-MGE-002"),
        tolerance_resolution=tolerance_resolution,
        tolerance_evidence=_parameter_evidence(tolerance_resolution, "EVID-P-MGE-003"),
    )


def _eval(evaluator, rule_id, margin, *, bundle=None, execution=None, evidence=None):
    execution = execution or _execution(margin)
    evidence = evidence or _profitability_evidence(execution)
    return evaluator(
        _purchase(),
        _context(),
        authorized_rule(rule_id, _context().rules_version),
        execution,
        evidence,
        bundle or _bundle(),
    )


@pytest.mark.parametrize(
    "margin,expected",
    [
        ("19.999", "TRUE"),
        ("20", "FALSE"),
        ("30", "FALSE"),
    ],
)
def test_r_mge_001_exact_minimum_boundary(margin, expected):
    result = _eval(evaluate_r_mge_001, R_MGE_001, margin)
    assert result.status == "EVALUABLE"
    assert result.outcome == expected


@pytest.mark.parametrize(
    "margin,expected",
    [
        ("26.999", "FALSE"),
        ("27", "TRUE"),
        ("29.999", "TRUE"),
        ("30", "FALSE"),
        ("19", "FALSE"),
    ],
)
def test_r_mge_002_exact_authorized_band(margin, expected):
    result = _eval(evaluate_r_mge_002, R_MGE_002, margin)
    assert result.status == "EVALUABLE"
    assert result.outcome == expected


@pytest.mark.parametrize(
    "margin,expected",
    [
        ("29.999", "FALSE"),
        ("30", "TRUE"),
        ("40", "TRUE"),
    ],
)
def test_r_mge_003_exact_target_boundary(margin, expected):
    result = _eval(evaluate_r_mge_003, R_MGE_003, margin)
    assert result.status == "EVALUABLE"
    assert result.outcome == expected


def test_gap_between_minimum_and_target_tolerance_triggers_no_mge_rule():
    bundle = _bundle(minimum="20", target="30", tolerance="3")
    results = (
        _eval(evaluate_r_mge_001, R_MGE_001, "25", bundle=bundle),
        _eval(evaluate_r_mge_002, R_MGE_002, "25", bundle=bundle),
        _eval(evaluate_r_mge_003, R_MGE_003, "25", bundle=bundle),
    )
    assert [item.outcome for item in results] == ["FALSE", "FALSE", "FALSE"]


def test_tolerance_zero_makes_r_mge_002_empty_without_overlap():
    bundle = _bundle(tolerance="0")
    r2 = _eval(evaluate_r_mge_002, R_MGE_002, "29.999", bundle=bundle)
    r3 = _eval(evaluate_r_mge_003, R_MGE_003, "30", bundle=bundle)
    assert r2.outcome == "FALSE"
    assert r3.outcome == "TRUE"


def test_minimum_equal_target_preserves_non_overlap():
    bundle = _bundle(minimum="30", target="30", tolerance="3")
    below = (
        _eval(evaluate_r_mge_001, R_MGE_001, "29", bundle=bundle),
        _eval(evaluate_r_mge_002, R_MGE_002, "29", bundle=bundle),
        _eval(evaluate_r_mge_003, R_MGE_003, "29", bundle=bundle),
    )
    at_target = (
        _eval(evaluate_r_mge_001, R_MGE_001, "30", bundle=bundle),
        _eval(evaluate_r_mge_002, R_MGE_002, "30", bundle=bundle),
        _eval(evaluate_r_mge_003, R_MGE_003, "30", bundle=bundle),
    )
    assert [item.outcome for item in below] == ["TRUE", "FALSE", "FALSE"]
    assert [item.outcome for item in at_target] == ["FALSE", "FALSE", "TRUE"]


@pytest.mark.parametrize(
    "bundle",
    [
        _bundle(minimum="31", target="30", tolerance="3"),
        _bundle(minimum="20", target="30", tolerance="-1"),
    ],
)
def test_conflicting_parameter_set_makes_all_rules_not_evaluable(bundle):
    results = (
        _eval(evaluate_r_mge_001, R_MGE_001, "25", bundle=bundle),
        _eval(evaluate_r_mge_002, R_MGE_002, "25", bundle=bundle),
        _eval(evaluate_r_mge_003, R_MGE_003, "25", bundle=bundle),
    )
    assert all(item.status == "NOT_EVALUABLE" for item in results)
    assert all(item.outcome is None for item in results)


def test_not_determined_profitability_makes_all_rules_not_evaluable():
    execution = _zero_sale_execution()
    evidence = _profitability_evidence(execution)
    bundle = _bundle()
    results = (
        _eval(evaluate_r_mge_001, R_MGE_001, "0", bundle=bundle, execution=execution, evidence=evidence),
        _eval(evaluate_r_mge_002, R_MGE_002, "0", bundle=bundle, execution=execution, evidence=evidence),
        _eval(evaluate_r_mge_003, R_MGE_003, "0", bundle=bundle, execution=execution, evidence=evidence),
    )
    assert all(item.status == "NOT_EVALUABLE" for item in results)


def test_profitability_gap_evidence_is_not_evaluable_not_false():
    execution = _execution("30")
    evidence = _profitability_evidence(execution, state="GAP")
    result = _eval(
        evaluate_r_mge_003,
        R_MGE_003,
        "30",
        execution=execution,
        evidence=evidence,
    )
    assert result.status == "NOT_EVALUABLE"
    assert result.outcome is None


def test_missing_parameter_evidence_is_not_evaluable_without_fake_id():
    bundle = _bundle()
    bundle = MGEParameterBundle(
        minimum_resolution=bundle.minimum_resolution,
        minimum_evidence=None,
        target_resolution=bundle.target_resolution,
        target_evidence=bundle.target_evidence,
        tolerance_resolution=bundle.tolerance_resolution,
        tolerance_evidence=bundle.tolerance_evidence,
    )
    result = _eval(evaluate_r_mge_001, R_MGE_001, "10", bundle=bundle)
    assert result.status == "NOT_EVALUABLE"
    assert "EVID-P-MGE-001" not in result.evidence_ids
    assert result.evidence_ids == [
        "EVID-MGE-RESULT",
        "EVID-P-MGE-002",
        "EVID-P-MGE-003",
    ]


@pytest.mark.parametrize(
    "bundle",
    [
        _bundle(minimum_unit="points"),
        _bundle(target_unit="points"),
        _bundle(tolerance_unit="%"),
    ],
)
def test_unit_mismatch_is_not_evaluable(bundle):
    result = _eval(evaluate_r_mge_002, R_MGE_002, "28", bundle=bundle)
    assert result.status == "NOT_EVALUABLE"
    assert result.outcome is None


def test_custom_thresholds_prove_catalog_defaults_are_not_hardcoded():
    bundle = _bundle(minimum="15", target="40", tolerance="2")
    assert _eval(evaluate_r_mge_001, R_MGE_001, "16", bundle=bundle).outcome == "FALSE"
    assert _eval(evaluate_r_mge_002, R_MGE_002, "38", bundle=bundle).outcome == "TRUE"
    assert _eval(evaluate_r_mge_003, R_MGE_003, "40", bundle=bundle).outcome == "TRUE"


def test_all_four_evidence_ids_are_preserved_for_complete_bundle():
    result = _eval(evaluate_r_mge_002, R_MGE_002, "28")
    assert result.evidence_ids == [
        "EVID-MGE-RESULT",
        "EVID-P-MGE-001",
        "EVID-P-MGE-002",
        "EVID-P-MGE-003",
    ]


def test_wrong_parameter_id_is_structural_error():
    bundle = _bundle()
    wrong = _resolution("P-OTHER", "20", PERCENT_UNIT)
    wrong_evidence = _parameter_evidence(wrong, "EVID-WRONG")
    bundle = MGEParameterBundle(
        minimum_resolution=wrong,
        minimum_evidence=wrong_evidence,
        target_resolution=bundle.target_resolution,
        target_evidence=bundle.target_evidence,
        tolerance_resolution=bundle.tolerance_resolution,
        tolerance_evidence=bundle.tolerance_evidence,
    )
    with pytest.raises(ValueError, match="P-MGE-001"):
        _eval(evaluate_r_mge_001, R_MGE_001, "10", bundle=bundle)


def test_wrong_parameters_version_is_structural_error():
    bundle = _bundle()
    resolution = _resolution(P_MGE_001, "20", PERCENT_UNIT, parameters_version="other")
    evidence = _parameter_evidence(resolution, "EVID-P-MGE-001")
    bundle = MGEParameterBundle(
        minimum_resolution=resolution,
        minimum_evidence=evidence,
        target_resolution=bundle.target_resolution,
        target_evidence=bundle.target_evidence,
        tolerance_resolution=bundle.tolerance_resolution,
        tolerance_evidence=bundle.tolerance_evidence,
    )
    with pytest.raises(ValueError, match="parameters_version"):
        _eval(evaluate_r_mge_001, R_MGE_001, "10", bundle=bundle)


def test_wrong_company_scope_is_structural_error():
    bundle = _bundle()
    resolution = _resolution(P_MGE_001, "20", PERCENT_UNIT, company_id="OTHER")
    evidence = _parameter_evidence(resolution, "EVID-P-MGE-001")
    bundle = MGEParameterBundle(
        minimum_resolution=resolution,
        minimum_evidence=evidence,
        target_resolution=bundle.target_resolution,
        target_evidence=bundle.target_evidence,
        tolerance_resolution=bundle.tolerance_resolution,
        tolerance_evidence=bundle.tolerance_evidence,
    )
    with pytest.raises(ValueError, match="company_scope"):
        _eval(evaluate_r_mge_001, R_MGE_001, "10", bundle=bundle)


def test_wrong_effective_date_is_structural_error():
    bundle = _bundle()
    resolution = _resolution(
        P_MGE_001,
        "20",
        PERCENT_UNIT,
        effective_at=datetime(2026, 9, 19, 12, 0, 0),
    )
    evidence = Evidence(
        evidence_id="EVID-P-MGE-001",
        source_type="ParameterConfigurationEvidence",
        source_ref="parameter-center",
        captured_at=EVAL_DATE,
        state="DEMONSTRATED",
        demonstration_ref=resolution.configuration_ref,
    )
    bundle = MGEParameterBundle(
        minimum_resolution=resolution,
        minimum_evidence=evidence,
        target_resolution=bundle.target_resolution,
        target_evidence=bundle.target_evidence,
        tolerance_resolution=bundle.tolerance_resolution,
        tolerance_evidence=bundle.tolerance_evidence,
    )
    with pytest.raises(ValueError, match="evaluation_date"):
        _eval(evaluate_r_mge_001, R_MGE_001, "10", bundle=bundle)


def test_wrong_parameter_demonstration_ref_is_structural_error():
    bundle = _bundle()
    bad_evidence = _parameter_evidence(
        bundle.minimum_resolution,
        "EVID-P-MGE-001",
        demonstration_ref="parameter_configuration:forged",
    )
    bundle = MGEParameterBundle(
        minimum_resolution=bundle.minimum_resolution,
        minimum_evidence=bad_evidence,
        target_resolution=bundle.target_resolution,
        target_evidence=bundle.target_evidence,
        tolerance_resolution=bundle.tolerance_resolution,
        tolerance_evidence=bundle.tolerance_evidence,
    )
    with pytest.raises(ValueError, match="no está vinculada"):
        _eval(evaluate_r_mge_001, R_MGE_001, "10", bundle=bundle)


def test_wrong_profitability_demonstration_ref_is_structural_error():
    execution = _execution("30")
    evidence = _profitability_evidence(
        execution,
        demonstration_ref="profitability:forged",
    )
    with pytest.raises(ValueError, match="ProfitabilityResult"):
        _eval(
            evaluate_r_mge_003,
            R_MGE_003,
            "30",
            execution=execution,
            evidence=evidence,
        )


def test_inactive_configuration_is_structural_error():
    bundle = _bundle()
    resolution = _resolution(
        P_MGE_001,
        "20",
        PERCENT_UNIT,
        valid_from=EFFECTIVE_AT + timedelta(days=1),
    )
    evidence = _parameter_evidence(resolution, "EVID-P-MGE-001")
    bundle = MGEParameterBundle(
        minimum_resolution=resolution,
        minimum_evidence=evidence,
        target_resolution=bundle.target_resolution,
        target_evidence=bundle.target_evidence,
        tolerance_resolution=bundle.tolerance_resolution,
        tolerance_evidence=bundle.tolerance_evidence,
    )
    with pytest.raises(ValueError, match="no está vigente"):
        _eval(evaluate_r_mge_001, R_MGE_001, "10", bundle=bundle)


def test_tampered_profitability_execution_is_rejected_before_rule_evaluation():
    execution = _execution("30")
    object.__setattr__(
        execution.profitability_result,
        "margin_percentage",
        Decimal("99"),
    )
    with pytest.raises(ValueError):
        _eval(
            evaluate_r_mge_003,
            R_MGE_003,
            "30",
            execution=execution,
            evidence=_profitability_evidence(execution),
        )


def test_catalog_metadata_is_exact_and_has_no_r0_escalation():
    expected = {
        R_MGE_001: ("R1", "ALTA"),
        R_MGE_002: ("R2", "MEDIA"),
        R_MGE_003: ("R3", "INFORMATIVA"),
    }
    for rule_id, pair in expected.items():
        metadata = authorized_rule_metadata(rule_id, "rules-v1")
        assert (metadata.effect, metadata.severity) == pair
    assert {R_MGE_001, R_MGE_002, R_MGE_003}.issubset(set(implemented_rule_ids()))


def test_orchestrator_executes_all_three_mge_rules_as_one_bundle():
    execution = _execution("28")
    bundle = _bundle()
    result = run_domain_rules(
        purchase=_purchase(),
        context=_context(),
        base_result="COMPRAR",
        profitability=ProfitabilityRuleInputs(
            profitability_execution=execution,
            profitability_evidence=_profitability_evidence(execution),
            minimum_resolution=bundle.minimum_resolution,
            minimum_evidence=bundle.minimum_evidence,
            target_resolution=bundle.target_resolution,
            target_evidence=bundle.target_evidence,
            tolerance_resolution=bundle.tolerance_resolution,
            tolerance_evidence=bundle.tolerance_evidence,
        ),
    )

    assert {R_MGE_001, R_MGE_002, R_MGE_003}.issubset(set(result.executed_rule_ids))
    by_id = {item.rule_id: item for item in result.assessments}
    assert by_id[R_MGE_001].outcome == "FALSE"
    assert by_id[R_MGE_002].outcome == "TRUE"
    assert by_id[R_MGE_003].outcome == "FALSE"


def test_orchestrator_omits_all_three_mge_rules_when_bundle_absent():
    result = run_domain_rules(
        purchase=_purchase(),
        context=_context(),
        base_result="COMPRAR",
    )
    assert R_MGE_001 in result.omitted_rule_ids
    assert R_MGE_002 in result.omitted_rule_ids
    assert R_MGE_003 in result.omitted_rule_ids
    assert R_MGE_001 not in result.executed_rule_ids
    assert R_MGE_002 not in result.executed_rule_ids
    assert R_MGE_003 not in result.executed_rule_ids
