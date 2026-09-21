from datetime import date, datetime, timedelta
from decimal import Decimal

import pytest

from eios.core.models import DecisionContext, Evidence, PurchaseOperation
from eios.data_freshness import (
    DATA_SNAPSHOT_FRESHNESS_EVIDENCE_SOURCE_TYPE,
    DataSnapshotFreshnessProducer,
    data_snapshot_freshness_ref,
)
from eios.parameters import ResolvedConfiguration
from eios.parameters.center import Configuration
from eios.rules.catalog import authorized_rule, authorized_rule_metadata
from eios.rules.data_quality import P_DAT_001, R_DAT_001, R_DAT_002, evaluate_r_dat_001, evaluate_r_dat_002


EVAL_DATE = date(2026, 9, 21)
EFFECTIVE_AT = datetime(2026, 9, 21, 12)


def _context():
    return DecisionContext(
        decision_id="DEC-DAT002",
        scenario_id="SCN-DAT002",
        rules_version="rules-v1",
        parameters_version="params-v1",
        data_snapshot_id="snapshot-v1",
    )


def _purchase():
    return PurchaseOperation(
        decision_id="DEC-DAT002",
        scenario_id="SCN-DAT002",
        article_id="ART-001",
        supplier_id="SUP-001",
        quantity=Decimal("10"),
        unit_price=Decimal("100"),
        currency="EUR",
        operation_date=EVAL_DATE,
    )


def _observation(updated=date(2026, 8, 10), state="AVAILABLE"):
    return DataSnapshotFreshnessProducer(
        authority_ref="DAT001-AUTH-v0.1",
        methodology_ref="DAT001-v0.1",
    ).produce(
        purchase=_purchase(),
        context=_context(),
        company_scope="COMPANY-A",
        state=state,
        source_updated_date=updated,
        source_ref="snapshot-metadata",
        trace_refs=("TRACE-DAT002",),
    )


def _evidence(obs, state="DEMONSTRATED"):
    return Evidence(
        evidence_id="EVID-DAT002",
        source_type=DATA_SNAPSHOT_FRESHNESS_EVIDENCE_SOURCE_TYPE,
        source_ref="snapshot-metadata",
        captured_at=obs.evaluation_date,
        state=state,
        demonstration_ref=data_snapshot_freshness_ref(obs) if state == "DEMONSTRATED" else None,
    )


def _resolution(value="6", unit="semanas"):
    cfg = Configuration(
        configuration_id=802,
        parameter_id=P_DAT_001,
        company_id="COMPANY-A",
        value=str(value),
        value_type="decimal",
        unit=unit,
        valid_from=EFFECTIVE_AT - timedelta(days=30),
        valid_to=None,
        created_at=EFFECTIVE_AT - timedelta(days=40),
        updated_at=EFFECTIVE_AT - timedelta(days=10),
    )
    return ResolvedConfiguration(
        configuration=cfg,
        parameters_version="params-v1",
        effective_at=EFFECTIVE_AT,
    )


def _param_evidence(resolution, state="DEMONSTRATED"):
    return Evidence(
        evidence_id="EVID-P-DAT-001",
        source_type="ParameterConfigurationEvidence",
        source_ref="parameter-center",
        captured_at=resolution.effective_at.date(),
        state=state,
        demonstration_ref=resolution.configuration_ref if state == "DEMONSTRATED" else None,
    )


def _evaluate(updated=date(2026, 8, 10), state="AVAILABLE", resolution=None):
    obs = _observation(updated, state)
    resolution = resolution or _resolution()
    return evaluate_r_dat_002(
        _purchase(),
        _context(),
        authorized_rule(R_DAT_002, "rules-v1"),
        obs,
        _evidence(obs),
        resolution,
        _param_evidence(resolution),
    )


def test_cutoff_equality_is_false():
    result = _evaluate(date(2026, 8, 10))
    assert result.status == "EVALUABLE"
    assert result.outcome == "FALSE"


def test_one_day_before_cutoff_is_true():
    result = _evaluate(date(2026, 8, 9))
    assert result.status == "EVALUABLE"
    assert result.outcome == "TRUE"


def test_current_date_is_false():
    assert _evaluate(EVAL_DATE).outcome == "FALSE"


def test_future_date_is_not_evaluable():
    result = _evaluate(date(2026, 9, 22))
    assert result.status == "NOT_EVALUABLE"
    assert result.outcome is None


@pytest.mark.parametrize("state", ("NOT_EVIDENCED", "CONFLICTING_DATA", "NOT_DETERMINABLE"))
def test_non_available_is_not_evaluable(state):
    obs = _observation(None, state)
    resolution = _resolution()
    result = evaluate_r_dat_002(
        _purchase(), _context(), authorized_rule(R_DAT_002, "rules-v1"),
        obs, _evidence(obs), resolution, _param_evidence(resolution)
    )
    assert result.status == "NOT_EVALUABLE"


def test_missing_parameter_is_not_evaluable():
    obs = _observation()
    result = evaluate_r_dat_002(
        _purchase(), _context(), authorized_rule(R_DAT_002, "rules-v1"),
        obs, _evidence(obs), None, None
    )
    assert result.status == "NOT_EVALUABLE"


def test_gap_evidence_is_not_evaluable():
    obs = _observation()
    resolution = _resolution()
    result = evaluate_r_dat_002(
        _purchase(), _context(), authorized_rule(R_DAT_002, "rules-v1"),
        obs, _evidence(obs, "GAP"), resolution, _param_evidence(resolution)
    )
    assert result.status == "NOT_EVALUABLE"


def test_metadata_is_r3_medium():
    metadata = authorized_rule_metadata(R_DAT_002, "rules-v1")
    assert metadata.effect == "R3"
    assert metadata.severity == "MEDIA"


@pytest.mark.parametrize(
    "updated,dat001_outcome,dat002_outcome",
    (
        (date(2026, 8, 10), "TRUE", "FALSE"),
        (date(2026, 8, 9), "FALSE", "TRUE"),
        (EVAL_DATE, "TRUE", "FALSE"),
    ),
)
def test_dat001_dat002_are_complementary_only_when_evaluable(updated, dat001_outcome, dat002_outcome):
    obs = _observation(updated)
    resolution = _resolution()
    ev = _evidence(obs)
    pev = _param_evidence(resolution)

    fresh = evaluate_r_dat_001(
        _purchase(), _context(), authorized_rule(R_DAT_001, "rules-v1"),
        obs, ev, resolution, pev
    )
    stale = evaluate_r_dat_002(
        _purchase(), _context(), authorized_rule(R_DAT_002, "rules-v1"),
        obs, ev, resolution, pev
    )
    assert fresh.status == stale.status == "EVALUABLE"
    assert fresh.outcome == dat001_outcome
    assert stale.outcome == dat002_outcome


def test_not_evaluable_is_not_cross_inferred():
    obs = _observation(None, "NOT_EVIDENCED")
    resolution = _resolution()
    ev = _evidence(obs)
    pev = _param_evidence(resolution)

    fresh = evaluate_r_dat_001(
        _purchase(), _context(), authorized_rule(R_DAT_001, "rules-v1"),
        obs, ev, resolution, pev
    )
    stale = evaluate_r_dat_002(
        _purchase(), _context(), authorized_rule(R_DAT_002, "rules-v1"),
        obs, ev, resolution, pev
    )
    assert fresh.status == "NOT_EVALUABLE"
    assert stale.status == "NOT_EVALUABLE"
    assert fresh.outcome is stale.outcome is None
