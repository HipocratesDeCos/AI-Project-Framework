from datetime import datetime, timedelta, timezone
from decimal import Decimal

from eios.core.models import DecisionContext, Evidence
from eios.parameters.center import Configuration
from eios.parameters.resolution import ResolvedConfiguration
from eios.payment_term_tolerance import resolve_payment_term_tolerance


EFFECTIVE_AT = datetime(2026, 9, 22, 6, 0, tzinfo=timezone.utc)
EVAL_DATE = EFFECTIVE_AT.date()


def _context(parameters_version="params-v1"):
    return DecisionContext(
        decision_id="DEC-PAG001-TOL",
        scenario_id="SCN-PAG001-TOL",
        rules_version="rules-v1",
        parameters_version=parameters_version,
        data_snapshot_id="snapshot-v1",
    )


def _resolved(parameter_id, value, *, unit="días", company_id="COMP-A", parameters_version="params-v1", effective_at=EFFECTIVE_AT, configuration_id=1, valid_from=None, valid_to=None):
    configuration = Configuration(
        configuration_id=configuration_id,
        parameter_id=parameter_id,
        company_id=company_id,
        value=value,
        value_type="DECIMAL",
        unit=unit,
        valid_from=valid_from or (EFFECTIVE_AT - timedelta(days=1)),
        valid_to=valid_to,
        created_at=EFFECTIVE_AT - timedelta(days=2),
        updated_at=EFFECTIVE_AT - timedelta(days=1),
    )
    return ResolvedConfiguration(
        configuration=configuration,
        parameters_version=parameters_version,
        effective_at=effective_at,
    )


def _evidence(resolved, evidence_id, *, source_type="ParameterConfigurationEvidence", state="DEMONSTRATED", captured_at=EVAL_DATE, demonstration_ref=None):
    return Evidence(
        evidence_id=evidence_id,
        source_type=source_type,
        source_ref=f"source:{evidence_id}",
        captured_at=captured_at,
        state=state,
        demonstration_ref=(
            resolved.configuration_ref if demonstration_ref is None and state == "DEMONSTRATED"
            else demonstration_ref
        ),
    )


def _call(target=None, tolerance=None, target_ev=None, tolerance_ev=None, *, context=None, company_scope="COMP-A", evaluation_date=EVAL_DATE):
    target = target or _resolved("P-PAG-002", "90", configuration_id=2)
    tolerance = tolerance or _resolved("P-PAG-003", "15", configuration_id=3)
    target_ev = target_ev or _evidence(target, "EV-TARGET")
    tolerance_ev = tolerance_ev or _evidence(tolerance, "EV-TOL")
    return resolve_payment_term_tolerance(
        context=context or _context(),
        company_scope=company_scope,
        evaluation_date=evaluation_date,
        target_resolution=target,
        target_evidence=target_ev,
        tolerance_resolution=tolerance,
        tolerance_evidence=tolerance_ev,
    )


def test_valid_target_minus_tolerance_materializes_threshold():
    result = _call()
    assert result.state == "AVAILABLE"
    assert result.reason_code == "AVAILABLE"
    assert result.target_days == Decimal("90")
    assert result.tolerance_days == Decimal("15")
    assert result.effective_threshold_days == Decimal("75")


def test_zero_tolerance_recovers_target_threshold():
    tolerance = _resolved("P-PAG-003", "0", configuration_id=3)
    result = _call(tolerance=tolerance, tolerance_ev=_evidence(tolerance, "EV-TOL"))
    assert result.state == "AVAILABLE"
    assert result.effective_threshold_days == Decimal("90")


def test_tolerance_equal_target_allows_zero_threshold():
    tolerance = _resolved("P-PAG-003", "90", configuration_id=3)
    result = _call(tolerance=tolerance, tolerance_ev=_evidence(tolerance, "EV-TOL"))
    assert result.state == "AVAILABLE"
    assert result.effective_threshold_days == Decimal("0")


def test_tolerance_greater_than_target_is_invalid_configuration():
    tolerance = _resolved("P-PAG-003", "91", configuration_id=3)
    result = _call(tolerance=tolerance, tolerance_ev=_evidence(tolerance, "EV-TOL"))
    assert result.state == "NOT_EVALUABLE"
    assert result.reason_code == "INVALID_CONFIGURATION"
    assert result.effective_threshold_days is None


def test_negative_target_is_invalid_configuration():
    target = _resolved("P-PAG-002", "-1", configuration_id=2)
    result = _call(target=target, target_ev=_evidence(target, "EV-TARGET"))
    assert result.state == "NOT_EVALUABLE"
    assert result.reason_code == "INVALID_CONFIGURATION"


def test_negative_tolerance_is_invalid_configuration():
    tolerance = _resolved("P-PAG-003", "-1", configuration_id=3)
    result = _call(tolerance=tolerance, tolerance_ev=_evidence(tolerance, "EV-TOL"))
    assert result.state == "NOT_EVALUABLE"
    assert result.reason_code == "INVALID_CONFIGURATION"


def test_missing_configuration_is_distinct_from_invalid_configuration():
    target = _resolved("P-PAG-002", "90", configuration_id=2)
    result = resolve_payment_term_tolerance(
        context=_context(),
        company_scope="COMP-A",
        evaluation_date=EVAL_DATE,
        target_resolution=target,
        target_evidence=_evidence(target, "EV-TARGET"),
        tolerance_resolution=None,
        tolerance_evidence=None,
    )
    assert result.state == "NOT_EVALUABLE"
    assert result.reason_code == "MISSING_CONFIGURATION"


def test_wrong_parameter_identity_is_invalid_configuration():
    target = _resolved("P-PAG-999", "90", configuration_id=2)
    result = _call(target=target, target_ev=_evidence(target, "EV-TARGET"))
    assert result.reason_code == "INVALID_CONFIGURATION"


def test_unit_must_be_days_without_conversion():
    tolerance = _resolved("P-PAG-003", "2", unit="semanas", configuration_id=3)
    result = _call(tolerance=tolerance, tolerance_ev=_evidence(tolerance, "EV-TOL"))
    assert result.state == "NOT_EVALUABLE"
    assert result.reason_code == "INVALID_CONFIGURATION"


def test_parameter_versions_must_match_same_effective_configuration_context():
    tolerance = _resolved(
        "P-PAG-003",
        "15",
        parameters_version="params-v2",
        configuration_id=3,
    )
    result = _call(tolerance=tolerance, tolerance_ev=_evidence(tolerance, "EV-TOL"))
    assert result.reason_code == "INCOHERENT_CONFIGURATION"


def test_company_scopes_must_match():
    tolerance = _resolved("P-PAG-003", "15", company_id="COMP-B", configuration_id=3)
    result = _call(tolerance=tolerance, tolerance_ev=_evidence(tolerance, "EV-TOL"))
    assert result.reason_code == "INCOHERENT_CONFIGURATION"


def test_effective_at_must_match_exact_selected_context():
    tolerance = _resolved(
        "P-PAG-003",
        "15",
        effective_at=EFFECTIVE_AT + timedelta(hours=1),
        configuration_id=3,
    )
    result = _call(tolerance=tolerance, tolerance_ev=_evidence(tolerance, "EV-TOL"))
    assert result.reason_code == "INCOHERENT_CONFIGURATION"


def test_effective_date_must_match_evaluation_date():
    result = _call(evaluation_date=EVAL_DATE + timedelta(days=1))
    assert result.reason_code == "INCOHERENT_CONFIGURATION"


def test_expired_configuration_is_invalid_even_when_pre_resolved():
    tolerance = _resolved(
        "P-PAG-003",
        "15",
        configuration_id=3,
        valid_to=EFFECTIVE_AT,
    )
    result = _call(tolerance=tolerance, tolerance_ev=_evidence(tolerance, "EV-TOL"))
    assert result.reason_code == "INVALID_CONFIGURATION"


def test_gap_evidence_is_invalid_evidence_not_missing_configuration():
    target = _resolved("P-PAG-002", "90", configuration_id=2)
    target_ev = _evidence(
        target,
        "EV-TARGET",
        state="GAP",
        demonstration_ref=None,
    )
    result = _call(target=target, target_ev=target_ev)
    assert result.reason_code == "INVALID_EVIDENCE"


def test_wrong_evidence_source_type_is_invalid_evidence():
    target = _resolved("P-PAG-002", "90", configuration_id=2)
    target_ev = _evidence(target, "EV-TARGET", source_type="OtherEvidence")
    result = _call(target=target, target_ev=target_ev)
    assert result.reason_code == "INVALID_EVIDENCE"


def test_wrong_demonstration_ref_is_invalid_evidence():
    target = _resolved("P-PAG-002", "90", configuration_id=2)
    target_ev = _evidence(target, "EV-TARGET", demonstration_ref="wrong-ref")
    result = _call(target=target, target_ev=target_ev)
    assert result.reason_code == "INVALID_EVIDENCE"


def test_evidence_capture_date_must_match_evaluation_date():
    target = _resolved("P-PAG-002", "90", configuration_id=2)
    target_ev = _evidence(
        target,
        "EV-TARGET",
        captured_at=EVAL_DATE - timedelta(days=1),
    )
    result = _call(target=target, target_ev=target_ev)
    assert result.reason_code == "INVALID_EVIDENCE"


def test_two_parameters_cannot_reuse_same_evidence_identity():
    target = _resolved("P-PAG-002", "90", configuration_id=2)
    tolerance = _resolved("P-PAG-003", "15", configuration_id=3)
    result = resolve_payment_term_tolerance(
        context=_context(),
        company_scope="COMP-A",
        evaluation_date=EVAL_DATE,
        target_resolution=target,
        target_evidence=_evidence(target, "EV-SAME"),
        tolerance_resolution=tolerance,
        tolerance_evidence=_evidence(tolerance, "EV-SAME"),
    )
    assert result.reason_code == "INVALID_EVIDENCE"


def test_decimal_values_are_preserved_without_rounding():
    target = _resolved("P-PAG-002", "90.5", configuration_id=2)
    tolerance = _resolved("P-PAG-003", "15.25", configuration_id=3)
    result = _call(
        target=target,
        tolerance=tolerance,
        target_ev=_evidence(target, "EV-TARGET"),
        tolerance_ev=_evidence(tolerance, "EV-TOL"),
    )
    assert result.state == "AVAILABLE"
    assert result.effective_threshold_days == Decimal("75.25")
