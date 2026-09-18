"""Cross-record regression tests; synthetic declarations do not produce QTG."""
from datetime import datetime, timezone

import pytest

from test_required_installment_coverage import material, capture
from eios.core.documentary_payment_capture import DocumentaryMaterial, DocumentaryLocator, build_documentary_payment_capture
from eios.core.documentary_payment_review import (
    GLOBAL_CONDITIONS, INSTALLMENT_CONDITIONS, DocumentaryReviewFinding,
    build_documentary_payment_human_review, validate_review_for_capture,
)
from eios.core.documentary_reviewer_designation import (
    CONDITIONS, DesignationObservation, build_documentary_reviewer_designation_link,
    validate_designation_link_for_review,
)
from eios.core.required_installment_coverage import check_required_installment_coverage, validate_coverage_for_material


def review_for(source, *, complete=False, review_ref='synthetic-chain-review'):
    payload = source.to_payload()
    findings = []
    if complete:
        support = DocumentaryLocator(**payload['bindings'][0]['locators'][0])
        findings += [DocumentaryReviewFinding(condition=c, outcome='CONFIRMED_BY_REVIEW',
            note='Synthetic supplied assertion, not an actual review', locators=(support,)) for c in GLOBAL_CONDITIONS]
        findings += [DocumentaryReviewFinding(condition=c, installment_ref=b['installment_ref'],
            outcome='CONFIRMED_BY_REVIEW', note='Synthetic assertion, not a verified fact',
            locators=tuple(DocumentaryLocator(**loc) for loc in b['locators']))
            for b in payload['bindings'] for c in INSTALLMENT_CONDITIONS]
    return build_documentary_payment_human_review(capture=source, review_ref=review_ref,
        reviewer_ref='synthetic-chain-person', reviewed_at=datetime(2026, 9, 18, 12, tzinfo=timezone.utc),
        findings=tuple(findings))


def designation_for(review, *, complete=False):
    support = DocumentaryLocator(document_ref='synthetic-designation', page=1, section='Mock scope')
    observations = tuple(DesignationObservation(condition=c, outcome='DECLARED_CONSISTENT',
        note='Fictitious declaration, no actual identity or mandate proof', locators=(support,)) for c in CONDITIONS) if complete else ()
    return build_documentary_reviewer_designation_link(review=review, link_ref='synthetic-chain-link',
        designation_ref='synthetic-designation', designation_kind='SYNTHETIC', reviewer_ref='synthetic-chain-person',
        company_scope=review.to_payload()['capture']['finance_package']['finance_input']['snapshot']['company_scope'],
        documents=(DocumentaryMaterial(document_ref='synthetic-designation', content=b'Mock data only, not uploaded designation PDF'),),
        declarations=(), observations=observations)


def test_complete_coverage_does_not_fill_human_or_designation_gaps(material):
    args, calendar, _ = material
    source = build_documentary_payment_capture(**args)
    coverage = check_required_installment_coverage(capture=source, calendar=calendar)
    review = review_for(source)
    designation = designation_for(review)
    assert coverage.to_payload()['required_calendar_matches']
    assert len(review.pending_controls) == 13
    assert len(designation.pending_controls) == 7
    assert designation.to_payload()['review']['capture'] == coverage.to_payload()['capture']


def test_all_positive_local_records_never_emit_operational_quality(material, monkeypatch):
    import eios.finance.provenance as finance
    import eios.quality.gate as gate
    def forbidden(*args, **kwargs):
        raise AssertionError('No Finance/QTG call from the documentary chain')
    monkeypatch.setattr(finance, 'run_provenanced_finance_basic', forbidden)
    monkeypatch.setattr(gate, 'evaluate_quality', forbidden)
    args, calendar, _ = material
    source = build_documentary_payment_capture(**args)
    coverage = check_required_installment_coverage(capture=source, calendar=calendar)
    review = review_for(source, complete=True)
    designation = designation_for(review, complete=True)
    assert coverage.to_payload()['required_calendar_matches']
    assert not review.pending_controls and not designation.pending_controls
    validate_review_for_capture(review, source)
    validate_designation_link_for_review(designation, review)
    validate_coverage_for_material(coverage, source, calendar)
    assert coverage.to_payload()['calendar']['case_kind'] == 'SYNTHETIC'
    for record in (coverage, review, designation):
        payload = record.to_payload()
        assert not {'quality_result', 'authorized', 'paid', 'quality_checks'} & payload.keys()
    assert review.to_payload()['capture'] == source.to_payload()


def test_positive_review_does_not_hide_calendar_reference_conflict(material):
    args, calendar, _ = material
    args['order_version'] = 'other-version'
    source = build_documentary_payment_capture(**args)
    review = review_for(source, complete=True)
    designation = designation_for(review, complete=True)
    coverage = check_required_installment_coverage(capture=source, calendar=calendar).to_payload()
    assert not review.pending_controls and not designation.pending_controls
    assert not coverage['required_calendar_matches']
    assert coverage['reference_mismatches'] == ['order_version']
    assert review.to_payload()['findings'][0]['outcome'] == 'CONFIRMED_BY_REVIEW'


def test_changed_document_invalidates_both_capture_bound_records(material):
    args, calendar, _ = material
    source = build_documentary_payment_capture(**args)
    coverage = check_required_installment_coverage(capture=source, calendar=calendar)
    review = review_for(source, complete=True)
    designation = designation_for(review, complete=True)
    args['documents'] = (args['documents'][0].model_copy(update={'content': b'Changed mock terms'}), args['documents'][1])
    changed = build_documentary_payment_capture(**args)
    with pytest.raises(ValueError):
        validate_review_for_capture(review, changed)
    with pytest.raises(ValueError):
        validate_coverage_for_material(coverage, changed, calendar)
    with pytest.raises(ValueError):
        validate_designation_link_for_review(designation, review_for(changed, complete=True))


def test_changed_required_calendar_is_not_bound_by_human_review_alone(material):
    args, calendar, _ = material
    source = build_documentary_payment_capture(**args)
    coverage = check_required_installment_coverage(capture=source, calendar=calendar)
    review = review_for(source, complete=True)
    changed = calendar.model_copy(update={'authority_ref': 'different-required-calendar-authority'})
    validate_review_for_capture(review, source)  # Review covers capture, not required-calendar authority.
    with pytest.raises(ValueError):
        validate_coverage_for_material(coverage, source, changed)
    assert coverage.fingerprint != check_required_installment_coverage(capture=source, calendar=changed).fingerprint
