from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

import pytest

from test_finance_decision_input_package import capture
from test_required_installment_coverage import material
from test_finance_quality_preparation import prepared_args
from test_finance_flow_completeness import flow_args, locator
from eios.core.documentary_payment_capture import DocumentaryMaterial
from eios.core.finance_flow_completeness import build_finance_flow_completeness_record
from eios.core.flow_inventory_mandate import (
    CONDITIONS as MANDATE_CONDITIONS, FlowInventoryMandateVerification,
    FlowMandateLocator, FlowMandateObservation, build_flow_inventory_mandate_verification,
    validate_flow_mandate_for_target,
)
from eios.core.flow_inventory_review import (
    CONDITIONS as REVIEW_CONDITIONS, FlowInventoryPersonalReview, FlowInventoryReviewFinding,
    build_flow_inventory_personal_review, validate_flow_review_for_material,
)


def mlocator(origin='MANDATE_DOCUMENT', reference='mandate'):
    return FlowMandateLocator(origin=origin, document_ref=reference, page=1, section='Mock')


def observations(outcome='CONFIRMED_BY_CONTRAST', complete=True):
    items = MANDATE_CONDITIONS if complete else MANDATE_CONDITIONS[:1]
    return tuple(FlowMandateObservation(condition=c, outcome=outcome,
        note='Synthetic mandate observation', locators=(mlocator(),) if outcome != 'CONFLICT_REPORTED' else ())
        for c in items)


@pytest.fixture
def mandate_args(flow_args):
    target = build_finance_flow_completeness_record(**flow_args)
    return dict(target=target, verification_ref='mock-verification', company_scope='company',
        reviewer_ref='mock-reviewer', mandate_ref='mock-mandate', target_review_ref='mock-review',
        verifier_ref='mock-verifier', verified_at=datetime(2026, 9, 19, tzinfo=timezone.utc),
        channel_ref='mock-channel', channel_kind='SYNTHETIC_TEST_CHANNEL',
        recognition_basis='INDEPENDENTLY_SUPPORTED', mandate_kind='SYNTHETIC',
        mandate_documents=(DocumentaryMaterial(document_ref='mandate', content=b'Mock mandate'),),
        channel_recognition_documents=(DocumentaryMaterial(document_ref='channel', content=b'Mock channel'),),
        contrast_documents=(DocumentaryMaterial(document_ref='contrast', content=b'Mock contrast'),),
        observations=observations())


def finding(condition='PERIMETER_COVERAGE', outcome='CONFIRMED_BY_REVIEW'):
    return FlowInventoryReviewFinding(condition=condition, outcome=outcome,
        note='Synthetic review finding', perimeter_refs=('mock-perimeter',))


def review_args(mandate_args, mandate=None):
    return dict(target=mandate_args['target'], mandate=mandate or build_flow_inventory_mandate_verification(**mandate_args),
        review_ref='mock-review', reviewer_ref='mock-reviewer',
        reviewed_at=datetime(2026, 9, 19, 12, tzinfo=timezone.utc), findings=(finding(),))


@pytest.mark.parametrize('outcome,complete,expected', [
    ('CONFIRMED_BY_CONTRAST', True, 'ACREDITADO_POR_CONTRASTE'),
    ('CONFIRMED_BY_CONTRAST', False, 'INCONCLUYENTE'),
    ('CONFLICT_REPORTED', True, 'INCONCLUYENTE'),
    ('NOT_CONFIRMED_BY_CONTRAST', False, 'NO_ACREDITADO')])
def test_mandate_outcome_is_derived(mandate_args, outcome, complete, expected):
    mandate_args['observations'] = observations(outcome, complete)
    result = build_flow_inventory_mandate_verification(**mandate_args)
    assert result.to_payload()['verification_outcome'] == expected
    assert 'authorized' not in result.to_payload()


def test_mandate_material_identity_and_bytes(mandate_args):
    result = build_flow_inventory_mandate_verification(**mandate_args)
    validate_flow_mandate_for_target(result, mandate_args['target'])
    assert result.document_bytes('MANDATE_DOCUMENT', 'mandate') == b'Mock mandate'
    with pytest.raises(KeyError): result.document_bytes('MANDATE_DOCUMENT', 'foreign')
    with pytest.raises(FrozenInstanceError): result._material = b'changed'
    with pytest.raises(TypeError): FlowInventoryMandateVerification()


@pytest.mark.parametrize('invalid', ['company', 'duplicate-condition', 'foreign-locator',
    'missing-support', 'naive', 'list', 'collision'])
def test_invalid_mandate_rejected(mandate_args, invalid):
    if invalid == 'company': mandate_args['company_scope'] = 'foreign'
    elif invalid == 'duplicate-condition': mandate_args['observations'] = observations()[:1] * 2
    elif invalid == 'foreign-locator':
        mandate_args['observations'] = (observations()[0].model_copy(
            update={'locators': (mlocator(reference='foreign'),)}),)
    elif invalid == 'missing-support':
        mandate_args['observations'] = (observations()[0].model_copy(update={'locators': ()}),)
    elif invalid == 'naive': mandate_args['verified_at'] = datetime(2026, 9, 19)
    elif invalid == 'list': mandate_args['observations'] = list(observations())
    else: mandate_args['contrast_documents'] = (DocumentaryMaterial(document_ref='mandate', content=b'x'),)
    with pytest.raises((TypeError, ValueError)): build_flow_inventory_mandate_verification(**mandate_args)


@pytest.mark.parametrize('mandate_state,scope', [
    ('accredited', 'AUTHORIZED_REVIEWER_PRESENTED_FLOW_FINDINGS'),
    ('inconclusive', 'PRESENTED_UNAUTHORIZED_OR_UNRESOLVED_FLOW_FINDINGS'),
    ('negative', 'PRESENTED_UNAUTHORIZED_OR_UNRESOLVED_FLOW_FINDINGS')])
def test_review_scope_derived_without_erasing_findings(mandate_args, mandate_state, scope):
    if mandate_state == 'inconclusive': mandate_args['observations'] = observations(complete=False)
    elif mandate_state == 'negative': mandate_args['observations'] = observations('NOT_CONFIRMED_BY_CONTRAST', False)
    mandate = build_flow_inventory_mandate_verification(**mandate_args)
    args = review_args(mandate_args, mandate)
    payload = build_flow_inventory_personal_review(**args).to_payload()
    assert payload['assurance_scope'] == scope
    assert payload['findings'] and len(payload['pending_conditions']) == 8


def test_complete_positive_review_does_not_create_quality_result(mandate_args):
    args = review_args(mandate_args)
    args['findings'] = tuple(finding(condition) for condition in REVIEW_CONDITIONS)
    payload = build_flow_inventory_personal_review(**args).to_payload()
    assert payload['pending_conditions'] == []
    assert payload['target']['pending_flow_ids'] == ['payment-2']
    assert 'status' not in payload and 'confidence' not in payload


@pytest.mark.parametrize('invalid', ['review-ref', 'reviewer', 'self-previous', 'naive',
    'duplicate-condition', 'foreign-perimeter', 'foreign-candidate', 'foreign-flow', 'unsupported'])
def test_invalid_review_rejected(mandate_args, invalid):
    args = review_args(mandate_args)
    if invalid == 'review-ref': args['review_ref'] = 'foreign'
    elif invalid == 'reviewer': args['reviewer_ref'] = 'foreign'
    elif invalid == 'self-previous': args['previous_review_ref'] = args['review_ref']
    elif invalid == 'naive': args['reviewed_at'] = datetime(2026, 9, 19)
    elif invalid == 'duplicate-condition': args['findings'] *= 2
    elif invalid == 'foreign-perimeter': args['findings'] = (finding().model_copy(update={'perimeter_refs': ('foreign',)}),)
    elif invalid == 'foreign-candidate': args['findings'] = (finding().model_copy(
        update={'perimeter_refs': (), 'candidate_refs': ('foreign',)}),)
    elif invalid == 'foreign-flow': args['findings'] = (finding().model_copy(
        update={'perimeter_refs': (), 'flow_ids': ('foreign',)}),)
    else: args['findings'] = (finding().model_copy(update={'perimeter_refs': (), 'locators': ()}),)
    with pytest.raises((TypeError, ValueError)): build_flow_inventory_personal_review(**args)


def test_exact_chain_reuse_mutability_and_engine_isolation(mandate_args, flow_args, monkeypatch):
    mandate = build_flow_inventory_mandate_verification(**mandate_args)
    args = review_args(mandate_args, mandate)
    review = build_flow_inventory_personal_review(**args)
    validate_flow_review_for_material(review, args['target'], mandate)
    payload = review.to_payload(); payload['findings'].clear()
    assert review.to_payload()['findings']
    with pytest.raises(FrozenInstanceError): review._material = b'changed'
    with pytest.raises(TypeError): FlowInventoryPersonalReview()
    flow_args['record_ref'] = 'changed'
    other = build_finance_flow_completeness_record(**flow_args)
    with pytest.raises(ValueError): validate_flow_review_for_material(review, other, mandate)
    def forbidden(*a, **kw): raise AssertionError('Engine invoked')
    monkeypatch.setattr('eios.finance.provenance.run_provenanced_finance_basic', forbidden)
    monkeypatch.setattr('eios.quality.gate.evaluate_quality', forbidden)
    build_flow_inventory_personal_review(**args)
