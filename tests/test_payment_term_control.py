from datetime import datetime, timedelta, timezone

from eios.core.models import DecisionContext, Evidence
from eios.parameters.center import Configuration
from eios.parameters.resolution import ResolvedConfiguration
from eios.payment_term_control import resolve_payment_term_control


EFFECTIVE_AT = datetime(2026, 9, 22, 7, 0, tzinfo=timezone.utc)
EVAL_DATE = EFFECTIVE_AT.date()


def _context(parameters_version="params-v1"):
    return DecisionContext(
        decision_id="DEC-PAG004",
        scenario_id="SCN-PAG004",
        rules_version="rules-v1",
        parameters_version=parameters_version,
        data_snapshot_id="snapshot-v1",
    )


def _resolved(value="Sí", *, parameter_id="P-PAG-004", company_id="COMP-A", parameters_version="params-v1", effective_at=EFFECTIVE_AT, valid_from=None, valid_to=None):
    cfg = Configuration(
        configuration_id=4,
        parameter_id=parameter_id,
        company_id=company_id,
        value=value,
        value_type="BOOLEAN",
        unit="Sí/No",
        valid_from=valid_from or (EFFECTIVE_AT - timedelta(days=1)),
        valid_to=valid_to,
        created_at=EFFECTIVE_AT - timedelta(days=2),
        updated_at=EFFECTIVE_AT - timedelta(days=1),
    )
    return ResolvedConfiguration(
        configuration=cfg,
        parameters_version=parameters_version,
        effective_at=effective_at,
    )


def _evidence(resolved, *, evidence_id="EV-PAG004", source_type="ParameterConfigurationEvidence", state="DEMONSTRATED", captured_at=EVAL_DATE, demonstration_ref=None):
    return Evidence(
        evidence_id=evidence_id,
        source_type=source_type,
        source_ref="parameter:P-PAG-004",
        captured_at=captured_at,
        state=state,
        demonstration_ref=resolved.configuration_ref if demonstration_ref is None and state == "DEMONSTRATED" else demonstration_ref,
    )


def _call(resolved=None, evidence=None, *, company_scope="COMP-A", context=None, evaluation_date=EVAL_DATE):
    resolved = resolved or _resolved()
    evidence = evidence or _evidence(resolved)
    return resolve_payment_term_control(
        context=context or _context(),
        company_scope=company_scope,
        evaluation_date=evaluation_date,
        control_resolution=resolved,
        control_evidence=evidence,
    )


def test_si_enables_payment_term_criterion():
    result = _call()
    assert result.state == "ENABLED"
    assert result.reason_code == "PAYMENT_TERM_CRITERION_ENABLED"


def test_no_disables_criterion_without_fabricating_false():
    resolved = _resolved("No")
    result = _call(resolved, _evidence(resolved))
    assert result.state == "DISABLED"
    assert result.reason_code == "PAYMENT_TERM_CRITERION_DISABLED"
    assert not hasattr(result, "outcome")


def test_missing_configuration_is_not_disabled():
    result = resolve_payment_term_control(
        context=_context(),
        company_scope="COMP-A",
        evaluation_date=EVAL_DATE,
        control_resolution=None,
        control_evidence=None,
    )
    assert result.state == "NOT_EVALUABLE"
    assert result.reason_code == "MISSING_CONTROL_CONFIGURATION"


def test_missing_evidence_is_missing_control_configuration():
    resolved = _resolved()
    result = resolve_payment_term_control(
        context=_context(),
        company_scope="COMP-A",
        evaluation_date=EVAL_DATE,
        control_resolution=resolved,
        control_evidence=None,
    )
    assert result.state == "NOT_EVALUABLE"
    assert result.reason_code == "MISSING_CONTROL_CONFIGURATION"


def test_true_alias_is_not_authorized():
    resolved = _resolved("true")
    result = _call(resolved, _evidence(resolved))
    assert result.reason_code == "INVALID_CONTROL_CONFIGURATION"


def test_one_alias_is_not_authorized():
    resolved = _resolved("1")
    result = _call(resolved, _evidence(resolved))
    assert result.reason_code == "INVALID_CONTROL_CONFIGURATION"


def test_wrong_parameter_id_is_invalid_configuration():
    resolved = _resolved(parameter_id="P-PAG-999")
    result = _call(resolved, _evidence(resolved))
    assert result.reason_code == "INVALID_CONTROL_CONFIGURATION"


def test_wrong_company_is_invalid_configuration():
    resolved = _resolved(company_id="COMP-B")
    result = _call(resolved, _evidence(resolved))
    assert result.reason_code == "INVALID_CONTROL_CONFIGURATION"


def test_wrong_parameters_version_is_invalid_configuration():
    resolved = _resolved(parameters_version="params-v2")
    result = _call(resolved, _evidence(resolved))
    assert result.reason_code == "INVALID_CONTROL_CONFIGURATION"


def test_wrong_effective_date_is_invalid_configuration():
    resolved = _resolved(effective_at=EFFECTIVE_AT + timedelta(days=1))
    result = _call(resolved, _evidence(resolved))
    assert result.reason_code == "INVALID_CONTROL_CONFIGURATION"


def test_expired_configuration_is_invalid_configuration():
    resolved = _resolved(valid_to=EFFECTIVE_AT)
    result = _call(resolved, _evidence(resolved))
    assert result.reason_code == "INVALID_CONTROL_CONFIGURATION"


def test_gap_evidence_is_invalid_control_evidence():
    resolved = _resolved()
    evidence = _evidence(resolved, state="GAP", demonstration_ref=None)
    result = _call(resolved, evidence)
    assert result.reason_code == "INVALID_CONTROL_EVIDENCE"


def test_wrong_evidence_source_type_is_invalid_control_evidence():
    resolved = _resolved()
    evidence = _evidence(resolved, source_type="OtherEvidence")
    result = _call(resolved, evidence)
    assert result.reason_code == "INVALID_CONTROL_EVIDENCE"


def test_wrong_demonstration_ref_is_invalid_control_evidence():
    resolved = _resolved()
    evidence = _evidence(resolved, demonstration_ref="wrong-ref")
    result = _call(resolved, evidence)
    assert result.reason_code == "INVALID_CONTROL_EVIDENCE"


def test_wrong_capture_date_is_invalid_control_evidence():
    resolved = _resolved()
    evidence = _evidence(resolved, captured_at=EVAL_DATE - timedelta(days=1))
    result = _call(resolved, evidence)
    assert result.reason_code == "INVALID_CONTROL_EVIDENCE"
