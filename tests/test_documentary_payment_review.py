from dataclasses import FrozenInstanceError
from datetime import datetime, timezone, timedelta

import pytest
from pydantic import ValidationError

from test_documentary_payment_capture import arguments, capture
from eios.core.documentary_payment_capture import build_documentary_payment_capture, DocumentaryMaterial, DocumentaryLocator
from eios.core.documentary_payment_review import (
    DocumentaryReviewFinding, DocumentaryPaymentHumanReview,
    build_documentary_payment_human_review, validate_review_for_capture, GLOBAL_CONDITIONS, INSTALLMENT_CONDITIONS,
)


@pytest.fixture
def review_args(arguments):
    return dict(capture=build_documentary_payment_capture(**arguments), review_ref='synthetic-review',
                reviewer_ref='synthetic-person', reviewed_at=datetime(2026, 9, 18, 10, tzinfo=timezone.utc), findings=())


def positive(arguments, condition='AMOUNT'):
    return DocumentaryReviewFinding(condition=condition, installment_ref='order/1',
        outcome='CONFIRMED_BY_REVIEW', note='Synthetic human assertion; not actual review',
        locators=arguments['bindings'][0].locators)


def test_empty_and_partial_reviews_publish_pending(review_args, arguments):
    empty = build_documentary_payment_human_review(**review_args)
    assert len(empty.pending_controls) == 8
    assert empty.to_payload()['capture']['case_kind'] == 'SYNTHETIC'
    review_args['findings'] = (positive(arguments),)
    partial = build_documentary_payment_human_review(**review_args)
    assert len(partial.pending_controls) == 7
    assert partial.to_payload()['capture'] == review_args['capture'].to_payload()
    assert partial.to_payload()['previous_review_ref'] is None
    assert partial.to_payload()['reviewed_at'] == review_args['reviewed_at'].isoformat()


def test_conflict_and_not_confirmed_remain_explicit(review_args):
    review_args['findings'] = (
        DocumentaryReviewFinding(condition='AMOUNT', installment_ref='order/1', outcome='CONFLICT_REPORTED', note='Amounts differ'),
        DocumentaryReviewFinding(condition='CURRENCY', installment_ref='order/1', outcome='NOT_CONFIRMED', note='Currency unavailable'),
    )
    result = build_documentary_payment_human_review(**review_args)
    assert len(result.pending_controls) == 6
    assert [f['outcome'] for f in result.to_payload()['findings']] == ['CONFLICT_REPORTED', 'NOT_CONFIRMED']


@pytest.mark.parametrize('changes', [
    {'installment_ref': 'foreign'}, {'installment_ref': None}, {'condition': 'DOCUMENT_TERMS'},
    {'locators': ()}, {'note': '   '},
])
def test_invalid_positive_findings(review_args, arguments, changes):
    review_args['findings'] = (positive(arguments).model_copy(update=changes),)
    with pytest.raises(ValueError):
        build_documentary_payment_human_review(**review_args)


@pytest.mark.parametrize('locator', [
    DocumentaryLocator(document_ref='absent', page=1, section='Terms'),
    DocumentaryLocator(document_ref='doc', page=99, section='Other section'),
])
def test_foreign_locators(review_args, arguments, locator):
    review_args['findings'] = (positive(arguments).model_copy(update={'locators': (locator,)}),)
    with pytest.raises(ValueError):
        build_documentary_payment_human_review(**review_args)


def test_duplicate_findings_and_bypass_rejected(review_args, arguments):
    finding = positive(arguments)
    review_args['findings'] = (finding, finding)
    with pytest.raises(ValueError, match='Duplicate'):
        build_documentary_payment_human_review(**review_args)
    review_args['findings'] = (finding.model_copy(update={'outcome': 'APTO'}),)
    with pytest.raises(ValidationError):
        build_documentary_payment_human_review(**review_args)


@pytest.mark.parametrize('value', [datetime(2026, 9, 18), '2026-09-18', None])
def test_explicit_review_time_required(review_args, value):
    review_args['reviewed_at'] = value
    with pytest.raises(ValueError):
        build_documentary_payment_human_review(**review_args)


def test_immutable_identity_and_export(review_args):
    result = build_documentary_payment_human_review(**review_args)
    exported = result.to_payload()
    exported['capture']['documents'].clear()
    assert result.to_payload()['capture']['documents']
    result.pending_controls[0]['condition'] = 'forged'
    assert result.pending_controls[0]['condition'] != 'forged'
    with pytest.raises(FrozenInstanceError):
        result._material = b'forged'
    with pytest.raises(TypeError):
        DocumentaryPaymentHumanReview()
    for field, value in [('reviewer_ref', 'other-person'), ('reviewed_at', review_args['reviewed_at'] + timedelta(hours=1))]:
        changed = dict(review_args, **{field: value})
        assert build_documentary_payment_human_review(**changed).fingerprint != result.fingerprint


@pytest.mark.parametrize('field,value', [('operation_ref', 'other-operation'), ('case_kind', 'PRESENTED_OPERATIONAL')])
def test_review_reuse_rejected_after_capture_change(review_args, arguments, field, value):
    review = build_documentary_payment_human_review(**review_args)
    validate_review_for_capture(review, review_args['capture'])
    arguments[field] = value
    with pytest.raises(ValueError, match='different'):
        validate_review_for_capture(review, build_documentary_payment_capture(**arguments))


def test_document_change_requires_new_review(review_args, arguments):
    review = build_documentary_payment_human_review(**review_args)
    arguments['documents'] = (DocumentaryMaterial(document_ref='doc', content=b'changed'),)
    with pytest.raises(ValueError):
        validate_review_for_capture(review, build_documentary_payment_capture(**arguments))


def test_no_bindings_still_has_global_pending_controls(review_args, arguments):
    arguments['bindings'] = ()
    review_args['capture'] = build_documentary_payment_capture(**arguments)
    assert len(build_documentary_payment_human_review(**review_args).pending_controls) == 3


def test_previous_review_preserved_without_resolution(review_args):
    review_args['previous_review_ref'] = 'prior'
    assert build_documentary_payment_human_review(**review_args).to_payload()['previous_review_ref'] == 'prior'
    review_args['previous_review_ref'] = review_args['review_ref']
    with pytest.raises(ValueError):
        build_documentary_payment_human_review(**review_args)


def test_full_inventory_is_not_qtg_approval(review_args, arguments):
    support = arguments['bindings'][0].locators
    globals_ = tuple(DocumentaryReviewFinding(condition=c, outcome='CONFIRMED_BY_REVIEW',
        note='Synthetic supplied finding', locators=support) for c in GLOBAL_CONDITIONS)
    installments = tuple(positive(arguments, c) for c in INSTALLMENT_CONDITIONS)
    review_args['findings'] = globals_ + installments
    result = build_documentary_payment_human_review(**review_args)
    assert result.pending_controls == ()
    assert result.to_payload()['capture']['case_kind'] == 'SYNTHETIC'
    assert not {'quality_result', 'status', 'confidence', 'critical'}.intersection(result.to_payload())
    assert result.to_payload()['capture']['finance_package']['finance_input']['cash_flows'][1]['evidence_state'] == 'NOT_EVIDENCED'


def test_no_engine_or_gate_execution(review_args, monkeypatch):
    import eios.finance.provenance as finance
    import eios.quality.gate as quality
    def forbidden(*args, **kwargs):
        raise AssertionError('registration cannot execute analysis or quality')
    monkeypatch.setattr(finance, 'run_provenanced_finance_basic', forbidden)
    monkeypatch.setattr(quality, 'evaluate_quality', forbidden)
    build_documentary_payment_human_review(**review_args)
