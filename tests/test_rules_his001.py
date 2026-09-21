from datetime import date, datetime, timedelta

import pytest

from eios.core.models import DecisionContext, Evidence, PurchaseOperation
from eios.parameters import ResolvedConfiguration
from eios.parameters.center import Configuration
from eios.pricing import (
    HISTORICAL_REFERENCE_TEMPORAL_EVIDENCE_SOURCE_TYPE,
    HistoricalReferenceTemporalObservation,
    historical_reference_purchase_ref,
    historical_reference_temporal_ref,
)
from eios.rules.catalog import authorized_rule, authorized_rule_metadata
from eios.rules.orchestrator import HistoryTemporalRuleInputs, run_domain_rules
from eios.rules.pricing import P_DAT_002, R_HIS_001, evaluate_r_his_001


EVAL_DATE = date(2026, 5, 31)
EFFECTIVE_AT = datetime(2026, 5, 31, 12)


def _context():
    return DecisionContext(
        decision_id="DEC-HIS001-001",
        scenario_id="SCN-HIS001-001",
        rules_version="rules-v1",
        parameters_version="params-v1",
        data_snapshot_id="snap-v1",
    )


def _purchase():
    from decimal import Decimal
    return PurchaseOperation(
        decision_id="DEC-HIS001-001",
        scenario_id="SCN-HIS001-001",
        article_id="ART-001",
        supplier_id="SUP-001",
        quantity=Decimal("10"),
        unit_price=Decimal("100"),
        currency="EUR",
        operation_date=EVAL_DATE,
    )


def _observation(*, reference_date=date(2025, 5, 31), state="AVAILABLE", **updates):
    purchase = _purchase()
    data = dict(
        decision_id=purchase.decision_id,
        scenario_id=purchase.scenario_id,
        data_snapshot_id="snap-v1",
        company_scope="COMPANY-A",
        purchase_operation_ref=historical_reference_purchase_ref(purchase),
        reference_id="HIST-001",
        reference_operation_date=reference_date,
        evaluation_date=purchase.operation_date,
        state=state,
        source_ref="history-source",
        authority_ref="HIS001-AUTH-v0.1",
        methodology_ref="HIS001-v0.1",
        trace_refs=("TRACE-HIS001",),
    )
    data.update(updates)
    return HistoricalReferenceTemporalObservation(**data)


def _reference_evidence(obs, *, state="DEMONSTRATED", demonstration_ref=None):
    return Evidence(
        evidence_id="EVID-HIS001-REF",
        source_type=HISTORICAL_REFERENCE_TEMPORAL_EVIDENCE_SOURCE_TYPE,
        source_ref="history-source",
        captured_at=obs.evaluation_date,
        state=state,
        demonstration_ref=(
            historical_reference_temporal_ref(obs)
            if state == "DEMONSTRATED" and demonstration_ref is None
            else demonstration_ref
        ),
    )


def _resolution(value="12", unit="meses", *, parameter_id=P_DAT_002, company_id="COMPANY-A", effective_at=EFFECTIVE_AT):
    cfg = Configuration(
        configuration_id=702,
        parameter_id=parameter_id,
        company_id=company_id,
        value=str(value),
        value_type="decimal",
        unit=unit,
        valid_from=effective_at - timedelta(days=30),
        valid_to=None,
        created_at=effective_at - timedelta(days=40),
        updated_at=effective_at - timedelta(days=10),
    )
    return ResolvedConfiguration(
        configuration=cfg,
        parameters_version="params-v1",
        effective_at=effective_at,
    )


def _parameter_evidence(resolution, *, state="DEMONSTRATED"):
    return Evidence(
        evidence_id="EVID-P-DAT-002",
        source_type="ParameterConfigurationEvidence",
        source_ref="parameter-center",
        captured_at=resolution.effective_at.date(),
        state=state,
        demonstration_ref=resolution.configuration_ref if state == "DEMONSTRATED" else None,
    )


def _evaluate(*, obs=None, ref_evidence=None, resolution=None, param_evidence=None):
    obs = obs or _observation()
    ref_evidence = ref_evidence or _reference_evidence(obs)
    resolution = resolution or _resolution()
    param_evidence = param_evidence or _parameter_evidence(resolution)
    return evaluate_r_his_001(
        _purchase(),
        _context(),
        authorized_rule(R_HIS_001, "rules-v1"),
        obs,
        ref_evidence,
        resolution,
        param_evidence,
    )


def test_reference_older_than_cutoff_is_true():
    result = _evaluate(obs=_observation(reference_date=date(2025, 5, 30)))
    assert result.status == "EVALUABLE"
    assert result.outcome == "TRUE"


def test_reference_equal_to_cutoff_is_false():
    result = _evaluate(obs=_observation(reference_date=date(2025, 5, 31)))
    assert result.status == "EVALUABLE"
    assert result.outcome == "FALSE"


def test_calendar_month_clipping():
    resolution = _resolution("3")
    obs = _observation(reference_date=date(2026, 2, 28))
    result = _evaluate(obs=obs, resolution=resolution, param_evidence=_parameter_evidence(resolution))
    assert result.status == "EVALUABLE"
    assert result.outcome == "FALSE"


def test_one_day_before_clipped_cutoff_is_true():
    resolution = _resolution("3")
    obs = _observation(reference_date=date(2026, 2, 27))
    result = _evaluate(obs=obs, resolution=resolution, param_evidence=_parameter_evidence(resolution))
    assert result.outcome == "TRUE"


def test_future_reference_is_not_evaluable():
    result = _evaluate(obs=_observation(reference_date=date(2026, 6, 1)))
    assert result.status == "NOT_EVALUABLE"
    assert result.outcome is None


@pytest.mark.parametrize("state", ("NOT_EVIDENCED", "CONFLICTING_DATA", "NOT_DETERMINABLE"))
def test_indeterminate_states_are_not_evaluable(state):
    obs = _observation(reference_date=None, state=state)
    result = _evaluate(obs=obs, ref_evidence=_reference_evidence(obs))
    assert result.status == "NOT_EVALUABLE"


def test_reference_evidence_gap_is_not_evaluable():
    obs = _observation()
    result = _evaluate(obs=obs, ref_evidence=_reference_evidence(obs, state="GAP"))
    assert result.status == "NOT_EVALUABLE"


def test_forged_reference_evidence_is_structural_error():
    obs = _observation()
    with pytest.raises(ValueError, match="no está vinculada"):
        _evaluate(obs=obs, ref_evidence=_reference_evidence(obs, demonstration_ref="forged"))


@pytest.mark.parametrize("field,value", (
    ("decision_id", "OTHER"),
    ("scenario_id", "OTHER"),
    ("data_snapshot_id", "OTHER"),
    ("evaluation_date", date(2026, 5, 30)),
    ("purchase_operation_ref", "forged"),
))
def test_identity_mismatch_is_structural(field, value):
    obs = _observation(**{field: value})
    with pytest.raises(ValueError):
        _evaluate(obs=obs, ref_evidence=_reference_evidence(obs))


@pytest.mark.parametrize("value,unit", (("0", "meses"), ("1.5", "meses"), ("12", "days"), ("NaN", "meses")))
def test_invalid_parameter_semantics_are_not_evaluable(value, unit):
    resolution = _resolution(value, unit)
    result = _evaluate(resolution=resolution, param_evidence=_parameter_evidence(resolution))
    assert result.status == "NOT_EVALUABLE"


def test_missing_parameter_fails_closed():
    obs = _observation()
    result = evaluate_r_his_001(
        _purchase(),
        _context(),
        authorized_rule(R_HIS_001, "rules-v1"),
        obs,
        _reference_evidence(obs),
        None,
        None,
    )
    assert result.status == "NOT_EVALUABLE"


def test_custom_parameter_proves_no_twelve_month_default():
    resolution = _resolution("1")
    obs = _observation(reference_date=date(2026, 4, 30))
    result = _evaluate(obs=obs, resolution=resolution, param_evidence=_parameter_evidence(resolution))
    assert result.outcome == "FALSE"


def test_metadata_is_r3_medium():
    metadata = authorized_rule_metadata(R_HIS_001, "rules-v1")
    assert metadata.effect == "R3"
    assert metadata.severity == "MEDIA"


def test_orchestrator_executes_his001_bundle():
    obs = _observation(reference_date=date(2025, 5, 30))
    resolution = _resolution()
    result = run_domain_rules(
        purchase=_purchase(),
        context=_context(),
        base_result="COMPRAR",
        history_temporal=HistoryTemporalRuleInputs(
            observation=obs,
            reference_evidence=_reference_evidence(obs),
            maximum_age_resolution=resolution,
            parameter_evidence=_parameter_evidence(resolution),
        ),
    )
    assert R_HIS_001 in result.executed_rule_ids
    assessment = next(x for x in result.assessments if x.rule_id == R_HIS_001)
    assert assessment.outcome == "TRUE"


def test_orchestrator_omits_his001_without_bundle():
    result = run_domain_rules(
        purchase=_purchase(),
        context=_context(),
        base_result="COMPRAR",
    )
    assert R_HIS_001 in result.omitted_rule_ids
