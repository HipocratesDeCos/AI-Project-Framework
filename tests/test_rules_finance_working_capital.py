from datetime import date, datetime, timedelta
from decimal import Decimal

import pytest

from eios.core.models import DecisionContext, Evidence, PurchaseOperation
from eios.finance import (
    POST_OPERATION_WORKING_CAPITAL_EVIDENCE_SOURCE_TYPE,
    PostOperationWorkingCapitalPosition,
    post_operation_working_capital_position_ref,
    purchase_operation_ref,
)
from eios.parameters import ResolvedConfiguration
from eios.parameters.center import Configuration
from eios.rules.catalog import authorized_rule, authorized_rule_metadata
from eios.rules.finance import R_FIN_002, evaluate_r_fin_002
from eios.rules.orchestrator import FinanceWorkingCapitalRuleInputs, run_domain_rules


EVAL_DATE = date(2026, 9, 20)
EFFECTIVE_AT = datetime(2026, 9, 20, 12, 0, 0)


def _context():
    return DecisionContext(
        decision_id="DEC-FIN002-001",
        scenario_id="SCN-FIN002-001",
        rules_version="rules-v1",
        parameters_version="params-v1",
        data_snapshot_id="snap-v1",
    )


def _purchase():
    return PurchaseOperation(
        decision_id="DEC-FIN002-001",
        scenario_id="SCN-FIN002-001",
        article_id="ART-001",
        supplier_id="SUP-001",
        quantity=Decimal("10"),
        unit_price=Decimal("5"),
        currency="EUR",
        operation_date=EVAL_DATE,
    )


def _position(*, assets="100", liabilities="70", operation_ref=None, **updates):
    purchase = _purchase()
    data = dict(
        decision_id="DEC-FIN002-001",
        scenario_id="SCN-FIN002-001",
        data_snapshot_id="snap-v1",
        company_scope="COMPANY-A",
        article_id="ART-001",
        evaluation_date=EVAL_DATE,
        currency="EUR",
        purchase_operation_ref=operation_ref or purchase_operation_ref(purchase),
        current_assets_after_operation=(
            None if assets is None else Decimal(str(assets))
        ),
        current_liabilities_after_operation=(
            None if liabilities is None else Decimal(str(liabilities))
        ),
        post_operation_snapshot_ref="POST-SNAPSHOT-001",
        source_ref="ACCOUNTING-SOURCE-001",
        authority_ref="FIN002-AUTH-v0.1",
        trace_refs=("TRACE-FIN002-001",),
    )
    data.update(updates)
    return PostOperationWorkingCapitalPosition(**data)


def _position_evidence(position, *, state="DEMONSTRATED", demonstration_ref=None):
    return Evidence(
        evidence_id="EVID-FIN002-POSITION",
        source_type=POST_OPERATION_WORKING_CAPITAL_EVIDENCE_SOURCE_TYPE,
        source_ref="ACCOUNTING-SOURCE-001",
        captured_at=EVAL_DATE,
        state=state,
        demonstration_ref=(
            post_operation_working_capital_position_ref(position)
            if state == "DEMONSTRATED" and demonstration_ref is None
            else demonstration_ref
        ),
    )


def _resolution(
    value="25",
    *,
    parameter_id="P-FIN-003",
    company_id="COMPANY-A",
    parameters_version="params-v1",
    unit="EUR",
    effective_at=EFFECTIVE_AT,
    valid_from=None,
    valid_to=None,
):
    configuration = Configuration(
        configuration_id=203,
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
        evidence_id="EVID-P-FIN-003",
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


def _evaluate(position=None, position_evidence=None, resolution=None, parameter_evidence=None):
    position = position or _position()
    position_evidence = position_evidence or _position_evidence(position)
    resolution = resolution or _resolution()
    parameter_evidence = parameter_evidence or _parameter_evidence(resolution)
    return evaluate_r_fin_002(
        _purchase(),
        _context(),
        authorized_rule(R_FIN_002, "rules-v1"),
        position,
        position_evidence,
        resolution,
        parameter_evidence,
    )


@pytest.mark.parametrize(
    ("assets", "liabilities", "threshold", "expected"),
    (
        ("100", "80", "25", "TRUE"),
        ("100", "75", "25", "FALSE"),
        ("100", "70", "25", "FALSE"),
        ("-10", "0", "-5", "TRUE"),
        ("-5", "0", "-5", "FALSE"),
    ),
)
def test_r_fin_002_exact_strict_boundary(assets, liabilities, threshold, expected):
    position = _position(assets=assets, liabilities=liabilities)
    resolution = _resolution(threshold)
    result = _evaluate(
        position=position,
        position_evidence=_position_evidence(position),
        resolution=resolution,
        parameter_evidence=_parameter_evidence(resolution),
    )
    assert result.status == "EVALUABLE"
    assert result.outcome == expected
    assert result.evidence_ids == ["EVID-FIN002-POSITION", "EVID-P-FIN-003"]


@pytest.mark.parametrize(
    ("assets", "liabilities"),
    ((None, "70"), ("100", None), (None, None)),
)
def test_missing_post_operation_magnitude_is_not_evaluable(assets, liabilities):
    position = _position(assets=assets, liabilities=liabilities)
    result = _evaluate(
        position=position,
        position_evidence=_position_evidence(position),
    )
    assert result.status == "NOT_EVALUABLE"
    assert result.outcome is None


def test_gap_position_evidence_is_not_false():
    position = _position()
    evidence = _position_evidence(position, state="GAP")
    result = _evaluate(position=position, position_evidence=evidence)
    assert result.status == "NOT_EVALUABLE"
    assert result.outcome is None


def test_forged_position_evidence_ref_is_structural_error():
    position = _position()
    evidence = _position_evidence(
        position,
        demonstration_ref="post_operation_working_capital:forged",
    )
    with pytest.raises(ValueError, match="no está vinculada"):
        _evaluate(position=position, position_evidence=evidence)


def test_forged_purchase_operation_ref_is_structural_error():
    position = _position(operation_ref="purchase_operation:forged")
    with pytest.raises(ValueError, match="PurchaseOperation exacta"):
        _evaluate(
            position=position,
            position_evidence=_position_evidence(position),
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
def test_position_identity_mismatch_is_structural(field, value, match):
    position = _position(**{field: value})
    with pytest.raises(ValueError, match=match):
        _evaluate(
            position=position,
            position_evidence=Evidence(
                evidence_id="EVID-FIN002-POSITION",
                source_type=POST_OPERATION_WORKING_CAPITAL_EVIDENCE_SOURCE_TYPE,
                source_ref="ACCOUNTING-SOURCE-001",
                captured_at=position.evaluation_date,
                state="DEMONSTRATED",
                demonstration_ref=post_operation_working_capital_position_ref(position),
            ),
        )


def test_missing_parameter_binding_is_not_evaluable():
    position = _position()
    result = evaluate_r_fin_002(
        _purchase(),
        _context(),
        authorized_rule(R_FIN_002, "rules-v1"),
        position,
        _position_evidence(position),
        None,
        None,
    )
    assert result.status == "NOT_EVALUABLE"
    assert result.evidence_ids == ["EVID-FIN002-POSITION"]


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
    position = _position()
    evidence = Evidence(
        evidence_id="EVID-P-FIN-003",
        source_type="ParameterConfigurationEvidence",
        source_ref="parameter-center",
        captured_at=EVAL_DATE,
        state="DEMONSTRATED",
        demonstration_ref=resolution.configuration_ref,
    )
    with pytest.raises(ValueError):
        _evaluate(
            position=position,
            position_evidence=_position_evidence(position),
            resolution=resolution,
            parameter_evidence=evidence,
        )


def test_inactive_parameter_configuration_is_structural_error():
    resolution = _resolution(valid_from=EFFECTIVE_AT + timedelta(days=1))
    with pytest.raises(ValueError, match="no está vigente"):
        _evaluate(
            resolution=resolution,
            parameter_evidence=_parameter_evidence(resolution),
        )


@pytest.mark.parametrize("unit", ("USD", "%", "días"))
def test_parameter_unit_mismatch_is_not_evaluable(unit):
    resolution = _resolution(unit=unit)
    result = _evaluate(
        resolution=resolution,
        parameter_evidence=_parameter_evidence(resolution),
    )
    assert result.status == "NOT_EVALUABLE"
    assert result.outcome is None


def test_euro_symbol_is_allowed_only_for_eur_position():
    resolution = _resolution(unit="€")
    result = _evaluate(
        resolution=resolution,
        parameter_evidence=_parameter_evidence(resolution),
    )
    assert result.status == "EVALUABLE"


@pytest.mark.parametrize("value", ("NaN", "Infinity", "-Infinity", "not-a-number"))
def test_non_finite_or_non_numeric_threshold_is_not_evaluable(value):
    resolution = _resolution(value=value)
    result = _evaluate(
        resolution=resolution,
        parameter_evidence=_parameter_evidence(resolution),
    )
    assert result.status == "NOT_EVALUABLE"
    assert result.outcome is None


def test_parameter_gap_evidence_is_not_evaluable():
    resolution = _resolution()
    result = _evaluate(
        resolution=resolution,
        parameter_evidence=_parameter_evidence(resolution, state="GAP"),
    )
    assert result.status == "NOT_EVALUABLE"
    assert result.outcome is None


def test_forged_parameter_evidence_ref_is_structural_error():
    resolution = _resolution()
    evidence = _parameter_evidence(
        resolution,
        demonstration_ref="parameter_configuration:forged",
    )
    with pytest.raises(ValueError, match="no está vinculada"):
        _evaluate(resolution=resolution, parameter_evidence=evidence)


def test_metadata_is_exact_r0_critical():
    metadata = authorized_rule_metadata(R_FIN_002, "rules-v1")
    assert metadata.effect == "R0"
    assert metadata.severity == "CRÍTICA"


def test_orchestrator_executes_r_fin_002_from_dedicated_bundle():
    position = _position(assets="100", liabilities="80")
    resolution = _resolution("25")
    result = run_domain_rules(
        purchase=_purchase(),
        context=_context(),
        base_result="COMPRAR",
        finance_working_capital=FinanceWorkingCapitalRuleInputs(
            position=position,
            position_evidence=_position_evidence(position),
            minimum_resolution=resolution,
            parameter_evidence=_parameter_evidence(resolution),
        ),
    )
    assert R_FIN_002 in result.executed_rule_ids
    assessment = next(x for x in result.assessments if x.rule_id == R_FIN_002)
    assert assessment.outcome == "TRUE"
    assert result.crc_result.consolidated_result == "NO COMPRAR"


def test_orchestrator_omits_r_fin_002_when_bundle_absent():
    result = run_domain_rules(
        purchase=_purchase(),
        context=_context(),
        base_result="COMPRAR",
    )
    assert R_FIN_002 in result.omitted_rule_ids
    assert R_FIN_002 not in result.executed_rule_ids


def test_carrier_is_frozen_and_rejects_duplicate_traces():
    position = _position()
    with pytest.raises(Exception):
        position.currency = "USD"
    with pytest.raises(ValueError, match="duplicados"):
        _position(trace_refs=("TRACE-1", "TRACE-1"))
