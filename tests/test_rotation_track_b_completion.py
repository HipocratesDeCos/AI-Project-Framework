from datetime import date, datetime, timezone
from decimal import Decimal
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from eios.core.decision_input_package import build_decision_input_package
from eios.core.models import DecisionContext, Evidence, PurchaseOperation
from eios.parameters.center import Configuration, ParameterConfigurationCenter, ParameterDefinition
from eios.rotation import (
    P_ROT_002,
    P_ROT_003,
    R_ROT_001,
    RotationMetricSourceEvidence,
    build_rotation_metric_evidence,
    evaluate_r_rot_001,
)
from eios.rules.catalog import authorized_rule_metadata
from eios.rules.orchestrator import RotationMetricRuleInputs, run_domain_rules


EFFECTIVE = datetime(2026, 9, 23, 8, 0, tzinfo=timezone.utc)
OP_DATE = date(2026, 9, 23)
COMPANY = "COMP-ROT"
PARAMS = "params-rot-v1"


def _purchase():
    return PurchaseOperation(
        decision_id="D-ROT-001",
        scenario_id="S-ROT",
        article_id="ART-001",
        supplier_id="SUP-001",
        quantity=Decimal("10"),
        unit_price=Decimal("5"),
        operation_date=OP_DATE,
    )


def _context():
    return DecisionContext(
        decision_id="D-ROT-001",
        scenario_id="S-ROT",
        rules_version="rules-v1",
        parameters_version=PARAMS,
        data_snapshot_id="snap-rot",
    )


def _config(pid: str, value: str, unit: str, cid: int):
    return Configuration(
        configuration_id=cid,
        parameter_id=pid,
        company_id=COMPANY,
        value=value,
        value_type="decimal" if pid == P_ROT_003 else "integer",
        unit=unit,
        valid_from=datetime(2026, 9, 1, tzinfo=timezone.utc),
        valid_to=None,
        created_at=datetime(2026, 9, 1, tzinfo=timezone.utc),
        updated_at=datetime(2026, 9, 1, tzinfo=timezone.utc),
    )


def _ref(cid: int):
    return f"parameter_configuration:{cid}@{EFFECTIVE.isoformat()}"


def _ev(eid: str, *, source_ref="rot:test", demonstration_ref="rot:test", state="DEMONSTRATED"):
    return Evidence(
        evidence_id=eid,
        source_type="rotation-test",
        source_ref=source_ref,
        captured_at=OP_DATE,
        state=state,
        demonstration_ref=demonstration_ref if state == "DEMONSTRATED" else None,
    )


def _package(period="30", threshold="0.10", requested=(P_ROT_002, P_ROT_003), extra=()):
    configs = {
        P_ROT_002: _config(P_ROT_002, period, "días", 7102),
        P_ROT_003: _config(P_ROT_003, threshold, "eventos/día", 7103),
    }
    center = ParameterConfigurationCenter(
        SimpleNamespace(
            get_parameter=lambda pid: ParameterDefinition(pid)
            if pid in {P_ROT_002, P_ROT_003}
            else None
        ),
        SimpleNamespace(can_modify=lambda *args: False),
        SimpleNamespace(get_at=lambda company_id, pid, effective_at: configs.get(pid)),
    )
    evidence = (
        _ev("E-CFG-2", source_ref=_ref(7102), demonstration_ref="config:7102"),
        _ev("E-CFG-3", source_ref=_ref(7103), demonstration_ref="config:7103"),
        *extra,
    )
    return build_decision_input_package(
        purchase=_purchase(),
        context=_context(),
        evidence=evidence,
        financial_snapshot=None,
        company_id=COMPANY,
        effective_at=EFFECTIVE,
        requested_parameter_ids=requested,
        center=center,
    )


def _source(*, refs=(), coverage="COMPLETE"):
    return RotationMetricSourceEvidence(
        article_id="ART-001",
        window_start=date(2026, 8, 25),
        window_end=OP_DATE,
        source_ref="sales-ledger:ART-001",
        source_semantics_ref="sales-semantics:v1",
        completeness_ref="sales-complete:track-b",
        valid_sale_evidence_refs=refs,
        trace_refs=("trace:rot001",),
        coverage_state=coverage,
    )


def _support(*sales):
    base = [
        _ev("E-SEM", demonstration_ref="sales-semantics:v1"),
        _ev("E-COMP", demonstration_ref="sales-complete:track-b"),
    ]
    base.extend(_ev(eid, demonstration_ref=f"sale:{eid}") for eid in sales)
    return tuple(base)


def test_metric_is_event_frequency_per_day_without_rounding() -> None:
    package = _package(threshold="0.0666666666666666666666666667", extra=_support("E-S1", "E-S2"))
    metric, threshold = build_rotation_metric_evidence(package, _source(refs=("E-S1", "E-S2")))
    assert metric.valid_sale_event_count == 2
    assert metric.rotation_metric == Decimal(2) / Decimal(30)
    assert metric.metric_unit == "eventos/día"
    assert metric.rotation_metric < threshold


@pytest.mark.parametrize(
    ("sales", "threshold", "outcome"),
    [
        (("E-S1",), "0.04", "TRUE"),
        (("E-S1",), str(Decimal(1) / Decimal(30)), "FALSE"),
        (("E-S1",), "0.03", "FALSE"),
        ((), "0.01", "TRUE"),
    ],
)
def test_r_rot_001_threshold_semantics(sales, threshold, outcome) -> None:
    package = _package(threshold=threshold, extra=_support(*sales))
    result = evaluate_r_rot_001(package, _source(refs=sales))
    assert result.status == "EVALUABLE"
    assert result.outcome == outcome


@pytest.mark.parametrize("coverage", ["PARTIAL", "NOT_DEMONSTRATED", "CONFLICTING"])
def test_incomplete_coverage_is_not_evaluable(coverage) -> None:
    package = _package(extra=_support())
    result = evaluate_r_rot_001(package, _source(coverage=coverage))
    assert result.status == "NOT_EVALUABLE"
    assert result.outcome is None


def test_gap_sale_reference_does_not_count() -> None:
    extra = (
        _ev("E-SEM", demonstration_ref="sales-semantics:v1"),
        _ev("E-COMP", demonstration_ref="sales-complete:track-b"),
        _ev("E-S1", state="GAP"),
    )
    result = evaluate_r_rot_001(_package(extra=extra), _source(refs=("E-S1",)))
    assert result.status == "NOT_EVALUABLE"


def test_source_rejects_duplicate_sale_refs() -> None:
    with pytest.raises(ValidationError, match="duplicados"):
        _source(refs=("E-S1", "E-S1"))


def test_p_rot_001_is_not_track_b_authority() -> None:
    package = _package(requested=(P_ROT_002, P_ROT_003), extra=_support())
    assert "P-ROT-001" not in package.requested_parameter_ids
    result = evaluate_r_rot_001(package, _source())
    assert result.status == "EVALUABLE"


@pytest.mark.parametrize(
    ("period", "threshold"),
    [
        ("0", "0.10"),
        ("1.5", "0.10"),
        ("30", "0"),
        ("30", "-0.01"),
        ("30", "NaN"),
    ],
)
def test_invalid_parameter_values_fail_closed(period, threshold) -> None:
    package = _package(period=period, threshold=threshold, extra=_support())
    result = evaluate_r_rot_001(package, _source())
    assert result.status == "NOT_EVALUABLE"


def test_missing_parameter_fails_closed() -> None:
    package = _package(requested=(P_ROT_002,), extra=_support())
    result = evaluate_r_rot_001(package, _source())
    assert result.status == "NOT_EVALUABLE"


def test_metadata_is_r2_alta_negociar() -> None:
    metadata = authorized_rule_metadata(R_ROT_001, "rules-v1")
    assert metadata.effect == "R2"
    assert metadata.severity == "ALTA"
    assert metadata.active_result == "NEGOCIAR"


def test_orchestrator_crc_resolves_active_rot001_to_negociar() -> None:
    package = _package(threshold="0.10", extra=_support("E-S1"))
    result = run_domain_rules(
        purchase=_purchase(),
        context=_context(),
        base_result="COMPRAR",
        rotation_metric=RotationMetricRuleInputs(
            package=package,
            source=_source(refs=("E-S1",)),
        ),
    )
    assert R_ROT_001 in result.executed_rule_ids
    assert result.crc_result.consolidated_result == "NEGOCIAR"


def test_orchestrator_rejects_detached_dip_identity() -> None:
    package = _package(extra=_support())
    other = _purchase().model_copy(update={"article_id": "OTHER"})
    with pytest.raises(ValueError, match="package.purchase incompatible"):
        run_domain_rules(
            purchase=other,
            context=_context(),
            base_result="COMPRAR",
            rotation_metric=RotationMetricRuleInputs(package=package, source=_source()),
        )
