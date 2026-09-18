from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

import pytest

from test_treasury_documentary_support import support_args, prepared_args, material, capture
from eios.core.documentary_payment_capture import DocumentaryMaterial
from eios.core.finance_quality_preparation import build_finance_quality_preparation, PresentedQualityCriteria
from eios.core.treasury_documentary_support import build_treasury_documentary_support, TreasuryObservation, CONDITIONS
from eios.core.treasury_contextual_assessment import (
    ContextualSupportLocator, TreasuryContextualDeclaration, TreasuryContextualAssessment,
    build_treasury_contextual_assessment, validate_contextual_assessment_for_material,
)


@pytest.fixture
def declaration():
    return TreasuryContextualDeclaration(condition='AVAILABILITY', criterion_reference='mock-criteria',
        criterion_version='0.1', applicability='APPLIES', applicability_reason='Mock scope',
        necessity='NECESSARY_FOR_DETERMINED_PROJECTION', necessity_reason='Opening treasury',
        impact_reason='Unknown availability prevents determined projection',
        support_assessment='NOT_ESTABLISHED', support_reason='Synthetic material only')


@pytest.fixture
def args(support_args, declaration):
    return dict(preparation=support_args['preparation'],
        treasury_support=build_treasury_documentary_support(**support_args),
        assessment_ref='mock-context', declarations=(declaration,))


def locator(origin='TREASURY_SUPPORT', reference='mock-source'):
    return ContextualSupportLocator(origin=origin, document_ref=reference, page=1, section='Mock')


def test_full_material_partiality_and_immutable_exports(args):
    result = build_treasury_contextual_assessment(**args)
    validate_contextual_assessment_for_material(result, args['preparation'], args['treasury_support'])
    payload = result.to_payload()
    assert payload['preparation'] == args['preparation'].to_payload()
    assert payload['treasury_support'] == args['treasury_support'].to_payload()
    assert len(payload['pending_conditions']) == 5
    assert payload['declarations'][0]['support_assessment'] == 'NOT_ESTABLISHED'
    assert payload['additional_case_kind'] is payload['reviewer_ref'] is None
    payload['declarations'].clear()
    assert len(result.to_payload()['declarations']) == 1
    with pytest.raises(FrozenInstanceError):
        result._material = b'changed'
    with pytest.raises(TypeError):
        TreasuryContextualAssessment()


def test_empty_declarations_preserve_all_pending(args):
    args['declarations'] = ()
    assert build_treasury_contextual_assessment(**args).to_payload()['pending_conditions'] == list(CONDITIONS)


def test_additional_material_bytes_and_separate_nature(args):
    args.update(additional_documents=(DocumentaryMaterial(document_ref='additional', content=b'Mock mandate'),),
        additional_case_kind='PRESENTED_OPERATIONAL')
    args['declarations'] = (args['declarations'][0].model_copy(update={
        'support_assessment': 'DECLARED_SUFFICIENT',
        'support_locators': (locator('ADDITIONAL_ASSESSMENT_MATERIAL', 'additional'),)}),)
    result = build_treasury_contextual_assessment(**args)
    assert result.additional_document_bytes('additional') == b'Mock mandate'
    assert result.to_payload()['treasury_support']['case_kind'] == 'SYNTHETIC'
    assert result.to_payload()['additional_case_kind'] == 'PRESENTED_OPERATIONAL'
    with pytest.raises(KeyError):
        result.additional_document_bytes('mock-source')


@pytest.mark.parametrize('invalid', ['criterion', 'duplicate', 'necessity', 'observation',
    'duplicate-observation', 'unsupported-positive', 'foreign-locator', 'wrong-origin',
    'blank-reason', 'bad-page', 'critical-field', 'list'])
def test_reject_invalid_declarations(args, invalid):
    item = args['declarations'][0]
    updates = {
        'criterion': {'criterion_version': 'foreign'},
        'necessity': {'applicability': 'DOES_NOT_APPLY'},
        'observation': {'observation_conditions': ('RESTRICTIONS',)},
        'duplicate-observation': {'observation_conditions': ('RESTRICTIONS', 'RESTRICTIONS')},
        'unsupported-positive': {'support_assessment': 'DECLARED_SUFFICIENT'},
        'foreign-locator': {'support_locators': (locator(reference='foreign'),)},
        'wrong-origin': {'support_locators': (locator('ADDITIONAL_ASSESSMENT_MATERIAL'),)},
        'blank-reason': {'impact_reason': ' '},
        'bad-page': {'support_locators': (locator().model_copy(update={'page': 0}),)},
        'critical-field': {'critical': True},
    }
    if invalid == 'list':
        args['declarations'] = [item]
    elif invalid == 'critical-field':
        # Caller-supplied quality flags are not part of the input contract.
        data = item.model_dump(mode='python')
        data['critical'] = True
        with pytest.raises(ValueError):
            TreasuryContextualDeclaration.model_validate(data)
        return
    else:
        args['declarations'] = (item.model_copy(update=updates.get(invalid, {})),) * (2 if invalid == 'duplicate' else 1)
    with pytest.raises((TypeError, ValueError)):
        build_treasury_contextual_assessment(**args)


@pytest.mark.parametrize('invalid', ['collision', 'duplicate', 'missing-nature', 'empty-bytes', 'person-only', 'time-only', 'naive'])
def test_reject_invalid_additional_material_or_pair(args, invalid):
    if invalid in ('person-only', 'time-only', 'naive'):
        if invalid != 'time-only':
            args['reviewer_ref'] = 'mock-person'
        if invalid != 'person-only':
            args['reviewed_at'] = datetime(2026, 9, 18, tzinfo=None if invalid == 'naive' else timezone.utc)
    else:
        ref = 'mock-source' if invalid == 'collision' else 'additional'
        doc = DocumentaryMaterial(document_ref=ref, content=b'Mock')
        if invalid == 'empty-bytes':
            doc = doc.model_copy(update={'content': b''})
        args.update(additional_documents=(doc,) * (2 if invalid == 'duplicate' else 1),
            additional_case_kind=None if invalid == 'missing-nature' else 'SYNTHETIC')
    with pytest.raises((TypeError, ValueError)):
        build_treasury_contextual_assessment(**args)


def test_positive_assertions_do_not_erase_negative_observation_or_comparison(args, support_args):
    support_args['declaration'] = support_args['declaration'].model_copy(update={'currency': 'USD'})
    support_args['observations'] = (TreasuryObservation(condition='RESTRICTIONS',
        outcome='DECLARED_INCONSISTENT', note='Restricted balance'),)
    args['treasury_support'] = build_treasury_documentary_support(**support_args)
    base = args['declarations'][0]
    args['declarations'] = tuple(base.model_copy(update={'condition': condition,
        'support_assessment': 'DECLARED_SUFFICIENT', 'support_locators': (locator(),),
        'observation_conditions': ('RESTRICTIONS',)}) for condition in CONDITIONS)
    payload = build_treasury_contextual_assessment(**args).to_payload()
    assert payload['pending_conditions'] == []
    assert payload['treasury_support']['technical_comparisons']['currency_matches'] is False
    assert payload['treasury_support']['observations'][0]['outcome'] == 'DECLARED_INCONSISTENT'
    assert 'status' not in payload and 'confidence' not in payload


@pytest.mark.parametrize('change', ['reference', 'reason', 'source', 'criteria', 'person'])
def test_changes_identity_and_exact_material_reuse(args, support_args, prepared_args, change):
    original = build_treasury_contextual_assessment(**args)
    if change == 'reference':
        args['assessment_ref'] = 'changed'
    elif change == 'reason':
        args['declarations'] = (args['declarations'][0].model_copy(update={'impact_reason': 'Changed explanation'}),)
    elif change == 'source':
        support_args['record_ref'] = 'changed'
        args['treasury_support'] = build_treasury_documentary_support(**support_args)
    elif change == 'criteria':
        prepared_args['criteria'] = (PresentedQualityCriteria(reference='mock-criteria', version='0.1', content=b'Changed mock'),)
        args['preparation'] = build_finance_quality_preparation(**prepared_args)
        support_args['preparation'] = args['preparation']
        args['treasury_support'] = build_treasury_documentary_support(**support_args)
    else:
        args.update(reviewer_ref='mock-person', reviewed_at=datetime(2026, 9, 18, tzinfo=timezone.utc))
    assert build_treasury_contextual_assessment(**args).fingerprint != original.fingerprint
    if change in ('source', 'criteria'):
        with pytest.raises(ValueError, match='different material'):
            validate_contextual_assessment_for_material(original, args['preparation'], args['treasury_support'])


def test_no_engine_execution(args, monkeypatch):
    def forbidden(*a, **kw):
        raise AssertionError('Consumer invoked')
    monkeypatch.setattr('eios.finance.provenance.run_provenanced_finance_basic', forbidden)
    monkeypatch.setattr('eios.quality.gate.evaluate_quality', forbidden)
    build_treasury_contextual_assessment(**args)


def test_foreign_preparation_rejected_at_construction(args, prepared_args):
    prepared_args['criteria'] = (PresentedQualityCriteria(reference='foreign', version='1', content=b'Mock'),)
    args['preparation'] = build_finance_quality_preparation(**prepared_args)
    with pytest.raises(ValueError, match='different preparation'):
        build_treasury_contextual_assessment(**args)


def test_additional_document_and_nature_change_identity(args):
    args.update(additional_documents=(DocumentaryMaterial(document_ref='additional', content=b'Mock'),),
        additional_case_kind='SYNTHETIC')
    original = build_treasury_contextual_assessment(**args)
    args['additional_case_kind'] = 'PRESENTED_OPERATIONAL'
    assert build_treasury_contextual_assessment(**args).fingerprint != original.fingerprint
    args['additional_case_kind'] = 'SYNTHETIC'
    args['additional_documents'] = (DocumentaryMaterial(document_ref='additional', content=b'Changed mock'),)
    assert build_treasury_contextual_assessment(**args).fingerprint != original.fingerprint
