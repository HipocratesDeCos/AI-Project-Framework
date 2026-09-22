from datetime import datetime, timedelta, timezone

from eios.core.models import DecisionContext, Evidence
from eios.parameters.center import Configuration
from eios.parameters.resolution import ResolvedConfiguration
from eios.early_payment_discount_control import resolve_early_payment_discount_control


EFFECTIVE_AT = datetime(2026, 9, 22, 9, 0, tzinfo=timezone.utc)
EVAL_DATE = EFFECTIVE_AT.date()


def _context(parameters_version="params-v1"):
    return DecisionContext(
        decision_id="DEC-PAG005",
        scenario_id="SCN-PAG005",
        rules_version="rules-v1",
        parameters_version=parameters_version,
        data_snapshot_id="snapshot-v1",
    )


def _resolved(value="Sí", *, parameter_id="P-PAG-005", company_id="COMP-A", parameters_version="params-v1", effective_at=EFFECTIVE_AT, valid_from=None, valid_to=None):
    cfg = Configuration(
        configuration_id=5,
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


def _evidence(resolved, *, evidence_id="EV-PAG005", source_type="ParameterConfigurationEvidence", state="DEMONSTRATED", captured_at=EVAL_DATE, demonstration_ref=None):
    return Evidence(
        evidence_id=evidence_id,
        source_type=source_type,
        source_ref="parameter:P-PAG-005",
        captured_at=captured_at,
        state=state,
        demonstration_ref=resolved.configuration_ref if demonstration_ref is None and state == "DEMONSTRATED" else demonstration_ref,
    )


def _call(resolved=None, evidence=None, *, company_scope="COMP-A", context=None, evaluation_date=EVAL_DATE):
    resolved = resolved or _resolved()
    evidence = evidence or _evidence(resolved)
    return resolve_early_payment_discount_control(
        context=context or _context(),
        company_scope=company_scope,
        evaluation_date=evaluation_date,
        control_resolution=resolved,
        control_evidence=evidence,
    )


def test_si_enables_discount_context_only():
    result = _call()
    assert result.state == "ENABLED"
    assert result.reason_code == "EARLY_PAYMENT_DISCOUNT_CONTEXT_ENABLED"
    assert not hasattr(result, "discount_percentage")
    assert not hasattr(result, "effective_cost")


def test_no_disables_discount_context_only():
    resolved = _resolved("No")
    result = _call(resolved, _evidence(resolved))
    assert result.state == "DISABLED"
    assert result.reason_code == "EARLY_PAYMENT_DISCOUNT_CONTEXT_DISABLED"


def test_missing_is_not_evaluable_control():
    result = resolve_early_payment_discount_control(
        context=_context(),
        company_scope="COMP-A",
        evaluation_date=EVAL_DATE,
        control_resolution=None,
        control_evidence=None,
    )
    assert result.state == "NOT_EVALUABLE"
    assert result.reason_code == "MISSING_DISCOUNT_CONTROL_CONFIGURATION"


def test_alias_true_is_rejected():
    resolved = _resolved("true")
    result = _call(resolved, _evidence(resolved))
    assert result.reason_code == "INVALID_DISCOUNT_CONTROL_CONFIGURATION"


def test_wrong_parameter_is_invalid():
    resolved = _resolved(parameter_id="P-PAG-004")
    result = _call(resolved, _evidence(resolved))
    assert result.reason_code == "INVALID_DISCOUNT_CONTROL_CONFIGURATION"


def test_wrong_company_is_invalid():
    resolved = _resolved(company_id="COMP-B")
    result = _call(resolved, _evidence(resolved))
    assert result.reason_code == "INVALID_DISCOUNT_CONTROL_CONFIGURATION"


def test_wrong_version_is_invalid():
    resolved = _resolved(parameters_version="params-v2")
    result = _call(resolved, _evidence(resolved))
    assert result.reason_code == "INVALID_DISCOUNT_CONTROL_CONFIGURATION"


def test_expired_is_invalid():
    resolved = _resolved(valid_to=EFFECTIVE_AT)
    result = _call(resolved, _evidence(resolved))
    assert result.reason_code == "INVALID_DISCOUNT_CONTROL_CONFIGURATION"


def test_gap_evidence_is_invalid():
    resolved = _resolved()
    result = _call(resolved, _evidence(resolved, state="GAP", demonstration_ref=None))
    assert result.reason_code == "INVALID_DISCOUNT_CONTROL_EVIDENCE"


def test_wrong_evidence_ref_is_invalid():
    resolved = _resolved()
    result = _call(resolved, _evidence(resolved, demonstration_ref="wrong"))
    assert result.reason_code == "INVALID_DISCOUNT_CONTROL_EVIDENCE"


def test_wrong_capture_date_is_invalid():
    resolved = _resolved()
    result = _call(resolved, _evidence(resolved, captured_at=EVAL_DATE - timedelta(days=1)))
    assert result.reason_code == "INVALID_DISCOUNT_CONTROL_EVIDENCE"
