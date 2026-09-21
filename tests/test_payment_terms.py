from datetime import date
from decimal import Decimal

from eios.payment_terms import (
    PaymentTermObservationAdapter,
    PaymentTermSemanticAuthority,
)
from eios.supplier.models import (
    SupplierDataIssueRef,
    SupplierEvidenceResult,
    SupplierObservation,
    SupplierResultIdentity,
)


EVAL_DATE = date(2026, 9, 21)


def _identity():
    return SupplierResultIdentity(
        decision_id="DEC-PAG001",
        scenario_id="SCN-PAG001",
        rules_version="rules-v1",
        parameters_version="params-v1",
        data_snapshot_id="snapshot-v1",
        company_scope="COMPANY-A",
        article_id="ART-001",
        evaluation_date=EVAL_DATE,
    )


def _authority(semantic_ref="AUTHORED-PAYMENT-TERM-SEMANTIC"):
    return PaymentTermSemanticAuthority(
        semantic_ref=semantic_ref,
        meaning="OFFERED_PAYMENT_TERM_DAYS",
        authority_ref="PAG001-SEM-AUTH-v0.1",
        methodology_ref="PAG001-SEM-METHOD-v0.1",
        version="0.1",
    )


def _adapter():
    return PaymentTermObservationAdapter(
        authority_ref="PAG001-TERM-AUTH-v0.1",
        methodology_ref="PAG001-TERM-METHOD-v0.1",
    )


def _observation(observation_id="PAY-TERM-1", **overrides):
    data = dict(
        observation_id=observation_id,
        supplier_id="SUP-001",
        candidate_id=None,
        object_id="ART-001",
        dimension="PAYMENT_TERM",
        state="KNOWN",
        value_kind="DECIMAL",
        value_decimal=Decimal("60"),
        unit="days",
        semantic_ref="AUTHORED-PAYMENT-TERM-SEMANTIC",
        source_ref="supplier-contract:payment-term",
        evidence_id=f"EV-{observation_id}",
        captured_at=date(2026, 9, 20),
        trace_refs=(f"TRACE-{observation_id}",),
    )
    data.update(overrides)
    return SupplierObservation(**data)


def _result(*observations):
    return SupplierEvidenceResult(
        identity=_identity(),
        current_supplier_id="SUP-001",
        observations=tuple(observations),
    )


def test_zero_payment_term_observations_is_not_evidenced():
    result = _adapter().adapt(_result(), _authority())
    assert result.state == "NOT_EVIDENCED"
    assert result.offered_payment_term_days is None


def test_single_authorized_decimal_payment_term_is_available():
    result = _adapter().adapt(_result(_observation()), _authority())
    assert result.state == "AVAILABLE"
    assert result.offered_payment_term_days == Decimal("60")
    assert result.semantic_authority_ref == "PAG001-SEM-AUTH-v0.1"
    assert result.source_observation_id == "PAY-TERM-1"


def test_integer_payment_term_is_preserved_as_decimal_without_rounding():
    obs = _observation(
        value_kind="INTEGER",
        value_decimal=None,
        value_integer=45,
    )
    result = _adapter().adapt(_result(obs), _authority())
    assert result.state == "AVAILABLE"
    assert result.offered_payment_term_days == Decimal("45")


def test_arbitrary_semantic_literal_is_valid_only_when_explicitly_authorized():
    obs = _observation(semantic_ref="SEM-CUSTOM-XYZ")
    result = _adapter().adapt(_result(obs), _authority("SEM-CUSTOM-XYZ"))
    assert result.state == "AVAILABLE"
    assert result.offered_payment_term_days == Decimal("60")


def test_semantic_ref_text_does_not_authorize_itself():
    obs = _observation(semantic_ref="SEM-PAYMENT-DAYS")
    result = _adapter().adapt(_result(obs), _authority("OTHER-SEMANTIC"))
    assert result.state == "NOT_DETERMINABLE"
    assert result.offered_payment_term_days is None


def test_wrong_unit_is_present_but_not_determinable():
    obs = _observation(unit="months")
    result = _adapter().adapt(_result(obs), _authority())
    assert result.state == "NOT_DETERMINABLE"


def test_text_payment_term_is_not_parsed():
    obs = _observation(
        value_kind="TEXT",
        value_decimal=None,
        value_text="60 days",
        unit=None,
    )
    result = _adapter().adapt(_result(obs), _authority())
    assert result.state == "NOT_DETERMINABLE"


def test_future_capture_is_not_determinable():
    obs = _observation(captured_at=date(2026, 9, 22))
    result = _adapter().adapt(_result(obs), _authority())
    assert result.state == "NOT_DETERMINABLE"


def test_expired_observation_is_not_determinable():
    obs = _observation(valid_to=date(2026, 9, 20))
    result = _adapter().adapt(_result(obs), _authority())
    assert result.state == "NOT_DETERMINABLE"


def test_negative_days_are_not_determinable():
    obs = _observation(value_decimal=Decimal("-1"))
    result = _adapter().adapt(_result(obs), _authority())
    assert result.state == "NOT_DETERMINABLE"


def test_explicit_not_evidenced_observation_stays_not_evidenced():
    obs = _observation(
        state="NOT_EVIDENCED",
        value_decimal=None,
        source_ref=None,
        evidence_id=None,
        captured_at=None,
    )
    result = _adapter().adapt(_result(obs), _authority())
    assert result.state == "NOT_EVIDENCED"


def test_explicit_conflicting_observation_stays_conflicting():
    issue = SupplierDataIssueRef(
        issue_id="ISSUE-1",
        issue_type="CONTRADICTION",
        issue_record_ref="supplier-payment-term",
        evidence_refs=("EV-A", "EV-B"),
        trace_refs=("TRACE-CONFLICT",),
    )
    obs = _observation(
        state="CONFLICTING_DATA",
        value_decimal=None,
        source_ref=None,
        evidence_id=None,
        captured_at=None,
        issue_refs=(issue,),
    )
    result = _adapter().adapt(_result(obs), _authority())
    assert result.state == "CONFLICTING_DATA"
    assert result.offered_payment_term_days is None


def test_multiple_payment_term_observations_fail_closed_even_if_values_match():
    first = _observation("PAY-TERM-1", value_decimal=Decimal("60"))
    second = _observation("PAY-TERM-2", value_decimal=Decimal("60"))
    result = _adapter().adapt(_result(first, second), _authority())
    assert result.state == "CONFLICTING_DATA"
    assert result.offered_payment_term_days is None


def test_candidate_supplier_observation_is_not_current_supplier_term():
    obs = _observation(
        supplier_id="SUP-ALT",
        candidate_id="CAND-1",
    )
    result = _adapter().adapt(_result(obs), _authority())
    assert result.state == "NOT_EVIDENCED"


def test_non_payment_dimension_is_not_payment_term():
    obs = _observation(dimension="LEAD_TIME")
    result = _adapter().adapt(_result(obs), _authority())
    assert result.state == "NOT_EVIDENCED"
