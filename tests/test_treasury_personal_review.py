from datetime import datetime, timezone

import pytest

from test_treasury_mandate_verification import (
    record_args, confirmed, declaration, args, support_args, prepared_args, material, capture,
)
from eios.core.documentary_payment_capture import DocumentaryLocator
from eios.core.treasury_mandate_verification import (
    CONDITIONS as MANDATE_CONDITIONS, MandateVerificationObservation,
    build_treasury_mandate_verification,
)
from eios.core.treasury_personal_review import (
    CONDITIONS, TreasuryReviewFinding, TreasuryPersonalReview,
    build_treasury_personal_review, validate_treasury_review_for_material,
)


@pytest.fixture
def review_args(record_args):
    record_args['target_review_ref'] = 'mock-treasury-review'
    record_args['observations'] = tuple(confirmed(c) for c in MANDATE_CONDITIONS)
    mandate = build_treasury_mandate_verification(**record_args)
    return dict(assessment=record_args['target'], mandate=mandate,
        review_ref='mock-treasury-review', reviewer_ref='mock-reviewer',
        reviewed_at=datetime(2026, 9, 19, tzinfo=timezone.utc), findings=())


def finding(condition, outcome='CONFIRMED_BY_REVIEW'):
    return TreasuryReviewFinding(condition=condition, outcome=outcome,
        note='Synthetic finding only', locators=(DocumentaryLocator(
            document_ref='mock-source', page=1, section='Mock'),))


def test_authorized_complete_review_is_still_not_quality(review_args):
    review_args['findings'] = tuple(finding(c) for c in CONDITIONS)
    result = build_treasury_personal_review(**review_args)
    payload = result.to_payload()
    assert payload['assurance_scope'] == 'AUTHORIZED_REVIEWER_PRESENTED_FINDINGS'
    assert result.pending_controls == ()
    assert not {'quality_result', 'quality_checks', 'status', 'confidence', 'authorized'} & payload.keys()
    validate_treasury_review_for_material(result, review_args['assessment'], review_args['mandate'])


@pytest.mark.parametrize('mandate_outcome', ['INCONCLUYENTE', 'NO_ACREDITADO'])
def test_unresolved_or_negative_mandate_preserves_findings_without_authority(review_args, record_args, mandate_outcome):
    if mandate_outcome == 'INCONCLUYENTE':
        record_args['observations'] = (confirmed('PERSON_IDENTITY'),)
    else:
        record_args['observations'] = (MandateVerificationObservation(condition='PERSON_IDENTITY',
            outcome='NOT_CONFIRMED_BY_CONTRAST', note='Synthetic negative',
            locators=confirmed('PERSON_IDENTITY').locators),)
    review_args['mandate'] = build_treasury_mandate_verification(**record_args)
    review_args['findings'] = (finding('AVAILABILITY'),)
    payload = build_treasury_personal_review(**review_args).to_payload()
    assert payload['mandate']['verification_outcome'] == mandate_outcome
    assert payload['assurance_scope'] == 'PRESENTED_UNAUTHORIZED_OR_UNRESOLVED_FINDINGS'
    assert payload['findings'][0]['outcome'] == 'CONFIRMED_BY_REVIEW'


def test_partial_and_conflicting_findings_remain_visible(review_args):
    review_args['findings'] = (TreasuryReviewFinding(condition='RESTRICTIONS',
        outcome='CONFLICT_REPORTED', note='Synthetic unresolved restriction'),)
    payload = build_treasury_personal_review(**review_args).to_payload()
    assert len(payload['pending_controls']) == 5
    assert payload['findings'][0]['outcome'] == 'CONFLICT_REPORTED'


@pytest.mark.parametrize('case', ['reviewer', 'review-ref', 'naive', 'self-previous', 'duplicate',
    'foreign-locator', 'unsupported-positive', 'blank-note', 'bad-page', 'list'])
def test_reject_invalid_review(review_args, case):
    if case == 'reviewer': review_args['reviewer_ref'] = 'foreign'
    elif case == 'review-ref': review_args['review_ref'] = 'foreign'
    elif case == 'naive': review_args['reviewed_at'] = datetime(2026, 9, 19)
    elif case == 'self-previous': review_args['previous_review_ref'] = review_args['review_ref']
    elif case == 'list': review_args['findings'] = []
    else:
        item = finding('AVAILABILITY')
        if case == 'foreign-locator': item = item.model_copy(update={'locators': (DocumentaryLocator(document_ref='foreign', page=1, section='x'),)})
        if case == 'unsupported-positive': item = item.model_copy(update={'locators': ()})
        if case == 'blank-note': item = item.model_copy(update={'note': ' '})
        if case == 'bad-page': item = item.model_copy(update={'locators': (DocumentaryLocator.model_construct(document_ref='mock-source', page=0, section='x'),)})
        review_args['findings'] = (item,) * (2 if case == 'duplicate' else 1)
    with pytest.raises((TypeError, ValueError)):
        build_treasury_personal_review(**review_args)


def test_changed_mandate_rejected_and_changes_identity(review_args, record_args):
    original = build_treasury_personal_review(**review_args)
    record_args['channel_kind'] = 'CHANGED_MOCK_CHANNEL'
    changed = build_treasury_mandate_verification(**record_args)
    with pytest.raises(ValueError, match='different material'):
        validate_treasury_review_for_material(original, review_args['assessment'], changed)
    review_args['mandate'] = changed
    assert build_treasury_personal_review(**review_args).fingerprint != original.fingerprint


def test_no_engine_execution(review_args, monkeypatch):
    def forbidden(*a, **kw): raise AssertionError('Engine invoked')
    monkeypatch.setattr('eios.finance.provenance.run_provenanced_finance_basic', forbidden)
    monkeypatch.setattr('eios.quality.gate.evaluate_quality', forbidden)
    build_treasury_personal_review(**review_args)
    with pytest.raises(TypeError): TreasuryPersonalReview()
