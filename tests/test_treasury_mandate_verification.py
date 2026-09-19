from datetime import datetime, timezone

import pytest

from test_treasury_contextual_assessment import args, declaration, support_args, prepared_args, material, capture
from eios.core.documentary_payment_capture import DocumentaryMaterial
from eios.core.treasury_contextual_assessment import build_treasury_contextual_assessment
from eios.core.treasury_mandate_verification import (
    CONDITIONS, MandateVerificationLocator, MandateVerificationObservation,
    TreasuryMandateVerification, build_treasury_mandate_verification,
    validate_mandate_verification_for_target,
)


def loc(origin, ref):
    return MandateVerificationLocator(origin=origin, document_ref=ref, page=1, section='Mock')


@pytest.fixture
def record_args(args):
    target = build_treasury_contextual_assessment(**args)
    company = target.to_payload()['preparation']['capture']['finance_package']['finance_input']['snapshot']['company_scope']
    return dict(target=target, verification_ref='mock-verification', company_scope=company,
        reviewer_ref='mock-reviewer', mandate_ref='mock-mandate', target_review_ref='mock-treasury-review',
        verifier_ref='mock-supervisor', verified_at=datetime(2026, 9, 19, tzinfo=timezone.utc),
        channel_ref='opaque-governed-channel-ref', channel_kind='MOCK_CORPORATE_DIRECTORY',
        recognition_basis='INDEPENDENTLY_SUPPORTED', mandate_kind='SYNTHETIC',
        mandate_documents=(DocumentaryMaterial(document_ref='mandate', content=b'Mock mandate'),),
        channel_recognition_documents=(DocumentaryMaterial(document_ref='channel', content=b'Mock channel recognition'),),
        contrast_documents=(DocumentaryMaterial(document_ref='contrast', content=b'Mock contrast'),),
        observations=())


def confirmed(condition):
    return MandateVerificationObservation(condition=condition, outcome='CONFIRMED_BY_CONTRAST',
        note='Synthetic confirmation only', locators=(loc('CONTRAST_SUPPORT', 'contrast'),))


def test_three_outcomes_are_derived(record_args):
    record_args['observations'] = tuple(confirmed(c) for c in CONDITIONS)
    accredited = build_treasury_mandate_verification(**record_args)
    assert accredited.to_payload()['verification_outcome'] == 'ACREDITADO_POR_CONTRASTE'
    assert accredited.to_payload()['pending_conditions'] == []
    record_args['observations'] = record_args['observations'][:-1]
    assert build_treasury_mandate_verification(**record_args).to_payload()['verification_outcome'] == 'INCONCLUYENTE'
    record_args['observations'] += (MandateVerificationObservation(condition=CONDITIONS[-1],
        outcome='NOT_CONFIRMED_BY_CONTRAST', note='Synthetic negative support',
        locators=(loc('MANDATE_DOCUMENT', 'mandate'),)),)
    assert build_treasury_mandate_verification(**record_args).to_payload()['verification_outcome'] == 'NO_ACREDITADO'


def test_conflict_and_negative_precedence(record_args):
    record_args['observations'] = (MandateVerificationObservation(condition='PERSON_IDENTITY',
        outcome='CONFLICT_REPORTED', note='Mock conflict'),)
    assert build_treasury_mandate_verification(**record_args).to_payload()['verification_outcome'] == 'INCONCLUYENTE'
    record_args['observations'] += (MandateVerificationObservation(condition='COMPANY_RELATION',
        outcome='NOT_CONFIRMED_BY_CONTRAST', note='Mock negative', locators=(loc('CHANNEL_RECOGNITION_SUPPORT', 'channel'),)),)
    assert build_treasury_mandate_verification(**record_args).to_payload()['verification_outcome'] == 'NO_ACREDITADO'


def test_preserves_bytes_and_isolated_exports(record_args):
    result = build_treasury_mandate_verification(**record_args)
    assert result.document_bytes('MANDATE_DOCUMENT', 'mandate') == b'Mock mandate'
    assert result.document_bytes('CHANNEL_RECOGNITION_SUPPORT', 'channel') == b'Mock channel recognition'
    with pytest.raises(KeyError): result.document_bytes('CONTRAST_SUPPORT', 'foreign')
    payload = result.to_payload(); payload['company_scope'] = 'changed'
    assert result.to_payload()['company_scope'] == record_args['company_scope']
    with pytest.raises(TypeError): TreasuryMandateVerification()


@pytest.mark.parametrize('case', ['company', 'naive', 'blank', 'collision', 'empty-group',
    'duplicate-condition', 'foreign-locator', 'unsupported-confirmed', 'bad-page', 'list'])
def test_reject_invalid_material(record_args, case):
    if case == 'company': record_args['company_scope'] = 'foreign'
    elif case == 'naive': record_args['verified_at'] = datetime(2026, 9, 19)
    elif case == 'blank': record_args['channel_ref'] = ' '
    elif case == 'collision': record_args['contrast_documents'] = (DocumentaryMaterial(document_ref='mandate', content=b'x'),)
    elif case == 'empty-group': record_args['contrast_documents'] = ()
    elif case == 'list': record_args['observations'] = []
    else:
        observation = confirmed('PERSON_IDENTITY')
        if case == 'foreign-locator': observation = observation.model_copy(update={'locators': (loc('CONTRAST_SUPPORT', 'foreign'),)})
        if case == 'unsupported-confirmed': observation = observation.model_copy(update={'locators': ()})
        if case == 'bad-page': observation = observation.model_copy(update={'locators': (loc('CONTRAST_SUPPORT', 'contrast').model_copy(update={'page': 0}),)})
        record_args['observations'] = (observation,) * (2 if case == 'duplicate-condition' else 1)
    with pytest.raises((TypeError, ValueError)):
        build_treasury_mandate_verification(**record_args)


def test_exact_target_reuse_and_identity(record_args, args):
    original = build_treasury_mandate_verification(**record_args)
    args['assessment_ref'] = 'changed-context'
    changed = build_treasury_contextual_assessment(**args)
    with pytest.raises(ValueError, match='different target'):
        validate_mandate_verification_for_target(original, changed)
    record_args['target'] = changed
    assert build_treasury_mandate_verification(**record_args).fingerprint != original.fingerprint


def test_no_quality_or_finance_execution(record_args, monkeypatch):
    def forbidden(*a, **kw): raise AssertionError('Engine invoked')
    monkeypatch.setattr('eios.finance.provenance.run_provenanced_finance_basic', forbidden)
    monkeypatch.setattr('eios.quality.gate.evaluate_quality', forbidden)
    payload = build_treasury_mandate_verification(**record_args).to_payload()
    assert not {'quality_result', 'quality_checks', 'authorized', 'status', 'confidence'} & payload.keys()
