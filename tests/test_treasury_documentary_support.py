from datetime import date, datetime, timezone
from decimal import Decimal

import pytest

from test_finance_quality_preparation import prepared_args, material, capture
from eios.core.finance_quality_preparation import build_finance_quality_preparation, PresentedQualityCriteria
from eios.core.documentary_payment_capture import DocumentaryMaterial, DocumentaryLocator
from eios.core.treasury_documentary_support import (
    TreasuryDeclaration, TreasuryObservation, build_treasury_documentary_support,
    validate_treasury_support_for_preparation,
)


@pytest.fixture
def support_args(prepared_args):
    preparation = build_finance_quality_preparation(**prepared_args)
    snapshot = preparation.to_payload()['capture']['finance_package']['finance_input']['snapshot']
    return dict(preparation=preparation, record_ref='mock-treasury',
        target_company_scope=snapshot['company_scope'], case_kind='SYNTHETIC',
        documents=(DocumentaryMaterial(document_ref='mock-source', content=b'Synthetic support only'),),
        declaration=TreasuryDeclaration(documentary_company='Presented company label',
            currency=snapshot['currency'], economic_date=date.fromisoformat(snapshot['as_of_date']),
            available_amount=Decimal(str(snapshot['available_treasury'])),
            locators=(DocumentaryLocator(document_ref='mock-source', page=1, section='Treasury'),)))


def test_exact_binding_and_preserved_bytes(support_args):
    support = build_treasury_documentary_support(**support_args)
    validate_treasury_support_for_preparation(support, support_args['preparation'])
    assert support.document_bytes('mock-source') == b'Synthetic support only'
    payload = support.to_payload()
    assert all(payload['technical_comparisons'].values())
    assert len(payload['pending_controls']) == 6
    assert payload['reviewer_ref'] is payload['reviewed_at'] is None
    payload['record_ref'] = 'changed'
    assert support.to_payload()['record_ref'] == 'mock-treasury'
    with pytest.raises(KeyError):
        support.document_bytes('foreign')


@pytest.mark.parametrize('field,value,key', [
    ('available_amount', Decimal('0'), 'amount_matches'),
    ('currency', 'USD', 'currency_matches'),
    ('economic_date', date(2000, 1, 1), 'economic_date_matches'),
])
def test_discrepancies_retained_not_corrected(support_args, field, value, key):
    original = support_args['preparation'].to_payload()
    support_args['declaration'] = support_args['declaration'].model_copy(update={field: value})
    payload = build_treasury_documentary_support(**support_args).to_payload()
    assert payload['technical_comparisons'][key] is False
    assert payload['preparation'] == original


def test_unknown_values_not_zero(support_args):
    support_args['declaration'] = support_args['declaration'].model_copy(update={
        'available_amount': None, 'currency': None, 'economic_date': None})
    payload = build_treasury_documentary_support(**support_args).to_payload()
    assert set(payload['technical_comparisons'].values()) == {None}


def test_positive_amount_does_not_certify_availability(support_args):
    support_args['observations'] = (TreasuryObservation(condition='AMOUNT_SUPPORT',
        outcome='DECLARED_CONSISTENT', note='Synthetic declared match',
        locators=support_args['declaration'].locators), TreasuryObservation(condition='RESTRICTIONS',
        outcome='DECLARED_INCONSISTENT', note='Restricted funds reported; not available'))
    payload = build_treasury_documentary_support(**support_args).to_payload()
    assert 'AVAILABILITY' in payload['pending_controls']
    assert 'RESTRICTIONS' not in payload['pending_controls']
    assert 'status' not in payload and 'confidence' not in payload


@pytest.mark.parametrize('change', ['company', 'duplicate-doc', 'foreign-locator',
    'duplicate-condition', 'unsupported-positive', 'blank-note', 'negative', 'nan', 'naive', 'person-only'])
def test_reject_invalid_material(support_args, change):
    if change == 'company':
        support_args['target_company_scope'] = 'foreign'
    elif change == 'duplicate-doc':
        support_args['documents'] *= 2
    elif change == 'foreign-locator':
        support_args['declaration'] = support_args['declaration'].model_copy(update={
            'locators': (DocumentaryLocator(document_ref='foreign', page=1, section='x'),)})
    elif change in ('negative', 'nan'):
        support_args['declaration'] = support_args['declaration'].model_copy(update={
            'available_amount': Decimal('-1' if change == 'negative' else 'NaN')})
    elif change in ('naive', 'person-only'):
        support_args['reviewer_ref'] = 'declared-person'
        if change == 'naive':
            support_args['reviewed_at'] = datetime(2026, 9, 18)
    else:
        observation = TreasuryObservation(condition='AVAILABILITY', outcome='NOT_ESTABLISHED', note='Unknown')
        if change == 'unsupported-positive':
            observation = observation.model_copy(update={'outcome': 'DECLARED_CONSISTENT'})
        if change == 'blank-note':
            observation = observation.model_copy(update={'note': ' '})
        support_args['observations'] = (observation,) * (2 if change == 'duplicate-condition' else 1)
    with pytest.raises((TypeError, ValueError)):
        build_treasury_documentary_support(**support_args)


def test_changes_identity_and_rejects_reuse(support_args, prepared_args):
    support = build_treasury_documentary_support(**support_args)
    prepared_args['criteria'] = (PresentedQualityCriteria(reference='changed', version='2', content=b'mock'),)
    other = build_finance_quality_preparation(**prepared_args)
    with pytest.raises(ValueError, match='different preparation'):
        validate_treasury_support_for_preparation(support, other)
    support_args['preparation'] = other
    assert build_treasury_documentary_support(**support_args).fingerprint != support.fingerprint


def test_no_finance_or_quality_execution(support_args, monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError('Consumer invoked')
    monkeypatch.setattr('eios.finance.provenance.run_provenanced_finance_basic', forbidden)
    monkeypatch.setattr('eios.quality.gate.evaluate_quality', forbidden)
    support_args.update(reviewer_ref='mock-person', reviewed_at=datetime(2026, 9, 18, tzinfo=timezone.utc))
    build_treasury_documentary_support(**support_args)


@pytest.mark.parametrize('change', ['document', 'note', 'date', 'amount'])
def test_each_support_change_changes_fingerprint(support_args, change):
    original = build_treasury_documentary_support(**support_args)
    if change == 'document':
        support_args['documents'] = (DocumentaryMaterial(document_ref='mock-source', content=b'Changed mock'),)
    elif change == 'note':
        support_args['observations'] = (TreasuryObservation(condition='RESTRICTIONS',
            outcome='NOT_ESTABLISHED', note='Undrawn credit is not available treasury'),)
    else:
        field, value = ('economic_date', date(2000, 1, 1)) if change == 'date' else ('available_amount', Decimal('0'))
        support_args['declaration'] = support_args['declaration'].model_copy(update={field: value})
    assert build_treasury_documentary_support(**support_args).fingerprint != original.fingerprint


def test_positive_observation_does_not_erase_mismatch(support_args):
    support_args['declaration'] = support_args['declaration'].model_copy(update={'currency': 'USD'})
    support_args['observations'] = (TreasuryObservation(condition='SOURCE_SUFFICIENCY',
        outcome='DECLARED_CONSISTENT', note='Presented assertion, not verified',
        locators=support_args['declaration'].locators),)
    payload = build_treasury_documentary_support(**support_args).to_payload()
    assert payload['technical_comparisons']['currency_matches'] is False


@pytest.mark.parametrize('invalid', ['bytes', 'page', 'blank-reference', 'time-only'])
def test_revalidate_copied_models_and_pair(support_args, invalid):
    if invalid == 'bytes':
        support_args['documents'] = (DocumentaryMaterial.model_construct(document_ref='mock-source', content='text'),)
    elif invalid == 'page':
        support_args['declaration'] = support_args['declaration'].model_copy(update={'locators': (
            DocumentaryLocator.model_construct(document_ref='mock-source', page=0, section='x'),)})
    elif invalid == 'blank-reference':
        support_args['record_ref'] = ' '
    else:
        support_args['reviewed_at'] = datetime(2026, 9, 18, tzinfo=timezone.utc)
    with pytest.raises((TypeError, ValueError)):
        build_treasury_documentary_support(**support_args)
