from datetime import date, datetime, timedelta
from decimal import Decimal
import inspect

import pytest

from eios.core.models import DecisionContext, Evidence, PurchaseOperation
from eios.data_freshness import (
    DATA_SNAPSHOT_FRESHNESS_EVIDENCE_SOURCE_TYPE,
    DataSnapshotFreshnessObservation,
    DataSnapshotFreshnessProducer,
    data_snapshot_freshness_ref,
)
from eios.parameters import ResolvedConfiguration
from eios.parameters.center import Configuration
from eios.rules.catalog import authorized_rule, authorized_rule_metadata
from eios.rules.data_quality import P_DAT_001, R_DAT_001, evaluate_r_dat_001
from eios.rules.orchestrator import DataFreshnessRuleInputs, run_domain_rules


EVAL_DATE = date(2026, 9, 21)
EFFECTIVE_AT = datetime(2026, 9, 21, 12)


def _context():
    return DecisionContext(
        decision_id="DEC-DAT001",
        scenario_id="SCN-DAT001",
        rules_version="rules-v1",
        parameters_version="params-v1",
        data_snapshot_id="snapshot-v1",
    )


def _purchase():
    return PurchaseOperation(
        decision_id="DEC-DAT001",
        scenario_id="SCN-DAT001",
        article_id="ART-001",
        supplier_id="SUP-001",
        quantity=Decimal("10"),
        unit_price=Decimal("100"),
        currency="EUR",
        operation_date=EVAL_DATE,
    )


def _producer():
    return DataSnapshotFreshnessProducer(
        authority_ref="DAT001-AUTH-v0.1",
        methodology_ref="DAT001-v0.1",
    )


def _observation(*, updated=date(2026, 8, 10), state="AVAILABLE"):
    return _producer().produce(
        purchase=_purchase(),
        context=_context(),
        company_scope="COMPANY-A",
        state=state,
        source_updated_date=updated,
        source_ref="snapshot-metadata",
        trace_refs=("TRACE-DAT001",),
    )


def _freshness_evidence(obs, *, state="DEMONSTRATED", demonstration_ref=None):
    return Evidence(
        evidence_id="EVID-DAT001",
        source_type=DATA_SNAPSHOT_FRESHNESS_EVIDENCE_SOURCE_TYPE,
        source_ref="snapshot-metadata",
        captured_at=obs.evaluation_date,
        state=state,
        demonstration_ref=(
            data_snapshot_freshness_ref(obs)
            if state == "DEMONSTRATED" and demonstration_ref is None
            else demonstration_ref
        ),
    )


def _resolution(value="6", unit="semanas", *, parameter_id=P_DAT_001, company_id="COMPANY-A", effective_at=EFFECTIVE_AT):
    cfg = Configuration(
        configuration_id=801,
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
        evidence_id="EVID-P-DAT-001",
        source_type="ParameterConfigurationEvidence",
        source_ref="parameter-center",
        captured_at=resolution.effective_at.date(),
        state=state,
        demonstration_ref=resolution.configuration_ref if state == "DEMONSTRATED" else None,
    )


def _evaluate(*, obs=None, freshness_evidence=None, resolution=None, parameter_evidence=None):
    obs = obs or _observation()
    freshness_evidence = freshness_evidence or _freshness_evidence(obs)
    resolution = resolution or _resolution()
    parameter_evidence = parameter_evidence or _parameter_evidence(resolution)
    return evaluate_r_dat_001(
        _purchase(),
        _context(),
        authorized_rule(R_DAT_001, "rules-v1"),
        obs,
        freshness_evidence,
        resolution,
        parameter_evidence,
    )


def test_cutoff_equality_is_true():
    obs = _observation(updated=date(2026, 8, 10))
    result = _evaluate(obs=obs, freshness_evidence=_freshness_evidence(obs))
    assert result.status == "EVALUABLE"
    assert result.outcome == "TRUE"


def test_one_day_before_cutoff_is_false():
    obs = _observation(updated=date(2026, 8, 9))
    result = _evaluate(obs=obs, freshness_evidence=_freshness_evidence(obs))
    assert result.status == "EVALUABLE"
    assert result.outcome == "FALSE"


def test_current_evaluation_date_is_true():
    obs = _observation(updated=EVAL_DATE)
    result = _evaluate(obs=obs, freshness_evidence=_freshness_evidence(obs))
    assert result.outcome == "TRUE"


def test_future_date_is_not_evaluable():
    obs = _observation(updated=date(2026, 9, 22))
    result = _evaluate(obs=obs, freshness_evidence=_freshness_evidence(obs))
    assert result.status == "NOT_EVALUABLE"
    assert result.outcome is None


@pytest.mark.parametrize("state", ("NOT_EVIDENCED", "CONFLICTING_DATA", "NOT_DETERMINABLE"))
def test_non_available_states_are_not_evaluable(state):
    obs = _observation(updated=None, state=state)
    result = _evaluate(obs=obs, freshness_evidence=_freshness_evidence(obs))
    assert result.status == "NOT_EVALUABLE"


def test_non_available_cannot_publish_date():
    with pytest.raises(ValueError, match="Solo AVAILABLE"):
        _observation(updated=EVAL_DATE, state="NOT_EVIDENCED")


def test_available_requires_date():
    with pytest.raises(ValueError, match="AVAILABLE requiere"):
        _observation(updated=None, state="AVAILABLE")


def test_freshness_evidence_gap_is_not_evaluable():
    obs = _observation()
    result = _evaluate(obs=obs, freshness_evidence=_freshness_evidence(obs, state="GAP"))
    assert result.status == "NOT_EVALUABLE"


def test_forged_freshness_evidence_is_structural_error():
    obs = _observation()
    with pytest.raises(ValueError, match="no está vinculada"):
        _evaluate(
            obs=obs,
            freshness_evidence=_freshness_evidence(obs, demonstration_ref="forged"),
        )


def test_snapshot_identity_mismatch_is_structural():
    obs = _observation().model_copy(update={"data_snapshot_id": "other"})
    with pytest.raises(ValueError, match="data_snapshot_id"):
        _evaluate(obs=obs, freshness_evidence=_freshness_evidence(obs))


def test_purchase_binding_mismatch_is_structural():
    obs = _observation().model_copy(update={"purchase_operation_ref": "forged"})
    with pytest.raises(ValueError, match="PurchaseOperation exacta"):
        _evaluate(obs=obs, freshness_evidence=_freshness_evidence(obs))


@pytest.mark.parametrize("value,unit", (("0", "semanas"), ("1.5", "semanas"), ("6", "days"), ("NaN", "semanas")))
def test_invalid_parameter_semantics_are_not_evaluable(value, unit):
    resolution = _resolution(value, unit)
    result = _evaluate(resolution=resolution, parameter_evidence=_parameter_evidence(resolution))
    assert result.status == "NOT_EVALUABLE"


def test_missing_parameter_fails_closed():
    obs = _observation()
    result = evaluate_r_dat_001(
        _purchase(),
        _context(),
        authorized_rule(R_DAT_001, "rules-v1"),
        obs,
        _freshness_evidence(obs),
        None,
        None,
    )
    assert result.status == "NOT_EVALUABLE"


def test_custom_parameter_proves_no_six_week_default():
    resolution = _resolution("1")
    obs = _observation(updated=date(2026, 9, 14))
    result = _evaluate(
        obs=obs,
        freshness_evidence=_freshness_evidence(obs),
        resolution=resolution,
        parameter_evidence=_parameter_evidence(resolution),
    )
    assert result.outcome == "TRUE"

    older = _observation(updated=date(2026, 9, 13))
    result = _evaluate(
        obs=older,
        freshness_evidence=_freshness_evidence(older),
        resolution=resolution,
        parameter_evidence=_parameter_evidence(resolution),
    )
    assert result.outcome == "FALSE"


def test_producer_binds_context_and_purchase_exactly():
    obs = _observation()
    assert obs.data_snapshot_id == _context().data_snapshot_id
    assert obs.evaluation_date == _purchase().operation_date


def test_producer_does_not_consume_rule_parameter_or_quality_gate():
    source = inspect.getsource(DataSnapshotFreshnessProducer)
    assert "P-DAT-001" not in source
    assert "ResolvedConfiguration" not in source
    assert "QualityTrustResult" not in source
    assert "captured_at" not in source
    assert "effective_at" not in source


def test_rule_does_not_consume_dip_or_quality_gate():
    import eios.rules.data_quality as module
    source = inspect.getsource(module)
    assert "DecisionInputPackage" not in source
    assert "QualityTrustResult" not in source
    assert "date.today" not in source
    assert "datetime.now" not in source


def test_metadata_is_r3_informative():
    metadata = authorized_rule_metadata(R_DAT_001, "rules-v1")
    assert metadata.effect == "R3"
    assert metadata.severity == "INFORMATIVA"


def test_orchestrator_executes_dat001_bundle():
    obs = _observation()
    resolution = _resolution()
    result = run_domain_rules(
        purchase=_purchase(),
        context=_context(),
        base_result="COMPRAR",
        data_freshness=DataFreshnessRuleInputs(
            observation=obs,
            freshness_evidence=_freshness_evidence(obs),
            maximum_age_resolution=resolution,
            parameter_evidence=_parameter_evidence(resolution),
        ),
    )
    assert R_DAT_001 in result.executed_rule_ids
    assessment = next(x for x in result.assessments if x.rule_id == R_DAT_001)
    assert assessment.outcome == "TRUE"
    assert result.crc_result.consolidated_result == "COMPRAR"


def test_orchestrator_omits_dat001_without_bundle():
    result = run_domain_rules(
        purchase=_purchase(),
        context=_context(),
        base_result="COMPRAR",
    )
    assert R_DAT_001 in result.omitted_rule_ids
