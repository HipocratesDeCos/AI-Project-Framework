from dataclasses import FrozenInstanceError
from hashlib import sha256
import json

import pytest

from test_documentary_payment_chain_boundaries import material, capture, review_for, designation_for
from eios.core.documentary_payment_capture import build_documentary_payment_capture
from eios.core.required_installment_coverage import RequiredInstallmentCoverage, check_required_installment_coverage
from eios.core.finance_quality_preparation import (
    FinanceQualityPreparation, PresentedQualityCriteria, build_finance_quality_preparation,
)


@pytest.fixture
def prepared_args(material):
    args, calendar, _ = material
    source = build_documentary_payment_capture(**args)
    return dict(capture=source, calendar=calendar,
        coverage=check_required_installment_coverage(capture=source, calendar=calendar),
        criteria=(PresentedQualityCriteria(reference='mock-criteria', version='0.1', content=b'Mock criterion material, not policy approval'),))


def test_capture_complete_material_and_explicit_absences(prepared_args):
    result = build_finance_quality_preparation(**prepared_args)
    payload = result.to_payload()
    assert payload['capture'] == prepared_args['capture'].to_payload()
    assert payload['calendar'] == prepared_args['calendar'].model_dump(mode='json')
    assert payload['coverage'] == prepared_args['coverage'].to_payload()
    assert payload['review'] is payload['review_fingerprint'] is None
    assert payload['designation'] is payload['designation_fingerprint'] is None
    assert payload['calendar']['case_kind'] == payload['capture']['case_kind'] == 'SYNTHETIC'
    content = result.criterion_bytes('mock-criteria', '0.1')
    assert content == prepared_args['criteria'][0].content
    assert payload['presented_criteria'][0]['sha256'] == sha256(content).hexdigest()
    with pytest.raises(KeyError):
        result.criterion_bytes('missing', '0.1')


def test_optional_records_preserve_findings_and_pending(prepared_args):
    prepared_args['review'] = review_for(prepared_args['capture'])
    prepared_args['designation'] = designation_for(prepared_args['review'])
    payload = build_finance_quality_preparation(**prepared_args).to_payload()
    assert len(payload['review']['pending_controls']) == 13
    assert len(payload['designation']['pending_controls']) == 7
    assert payload['designation']['review'] == payload['review']


@pytest.mark.parametrize('foreign', ['capture', 'calendar', 'review', 'designation'])
def test_reject_foreign_material(prepared_args, material, foreign):
    args, _, _ = material
    args['operation_ref'] = 'foreign'
    other = build_documentary_payment_capture(**args)
    if foreign == 'capture':
        prepared_args['capture'] = other
    elif foreign == 'calendar':
        prepared_args['calendar'] = prepared_args['calendar'].model_copy(update={'authority_ref': 'foreign'})
    elif foreign == 'review':
        prepared_args['review'] = review_for(other)
    else:
        prepared_args['review'] = review_for(prepared_args['capture'])
        prepared_args['designation'] = designation_for(review_for(other))
    with pytest.raises(ValueError):
        build_finance_quality_preparation(**prepared_args)


def test_designation_without_review_rejected(prepared_args):
    prepared_args['designation'] = designation_for(review_for(prepared_args['capture']))
    with pytest.raises(ValueError, match='requires'):
        build_finance_quality_preparation(**prepared_args)


def test_nonreproducible_coverage_rejected(prepared_args):
    forged = object.__new__(RequiredInstallmentCoverage)
    payload = prepared_args['coverage'].to_payload()
    payload['required_calendar_matches'] = False
    object.__setattr__(forged, '_material', json.dumps(payload).encode())
    prepared_args['coverage'] = forged
    with pytest.raises(ValueError, match='reproducible'):
        build_finance_quality_preparation(**prepared_args)


@pytest.mark.parametrize('criteria', [(), [], ('hash-only-reference',),
    (PresentedQualityCriteria.model_construct(reference='x', version='1', content=b''),),
    (PresentedQualityCriteria.model_construct(reference='x', version='1', content='not bytes'),),
    (PresentedQualityCriteria(reference=' ', version='1', content=b'x'),)])
def test_missing_or_invalid_criterion_material_rejected(prepared_args, criteria):
    prepared_args['criteria'] = criteria
    with pytest.raises((TypeError, ValueError)):
        build_finance_quality_preparation(**prepared_args)


def test_duplicate_criteria_rejected(prepared_args):
    prepared_args['criteria'] *= 2
    with pytest.raises(ValueError, match='Duplicate'):
        build_finance_quality_preparation(**prepared_args)


def test_immutable_exports_and_criterion_changes(prepared_args):
    result = build_finance_quality_preparation(**prepared_args)
    payload = result.to_payload()
    payload['capture']['bindings'].clear()
    payload['presented_criteria'].clear()
    assert result.to_payload()['capture']['bindings']
    assert result.to_payload()['presented_criteria']
    with pytest.raises(FrozenInstanceError):
        result._material = b'forged'
    with pytest.raises(TypeError):
        FinanceQualityPreparation()
    criterion = prepared_args['criteria'][0]
    for update in ({'content': b'changed'}, {'version': '0.2'}, {'reference': 'other'}):
        prepared_args['criteria'] = (criterion.model_copy(update=update),)
        assert build_finance_quality_preparation(**prepared_args).fingerprint != result.fingerprint


def test_negative_coverage_and_positive_declarations_do_not_trigger_gate(prepared_args, material, monkeypatch):
    import eios.finance.provenance as finance
    import eios.quality.gate as gate
    def forbidden(*args, **kwargs):
        raise AssertionError('Preparation must not execute engines')
    monkeypatch.setattr(finance, 'run_provenanced_finance_basic', forbidden)
    monkeypatch.setattr(gate, 'evaluate_quality', forbidden)
    args, calendar, _ = material
    args['bindings'] = args['bindings'][:1]
    source = build_documentary_payment_capture(**args)
    prepared_args.update(capture=source, calendar=calendar,
        coverage=check_required_installment_coverage(capture=source, calendar=calendar),
        review=review_for(source, complete=True))
    prepared_args['designation'] = designation_for(prepared_args['review'], complete=True)
    payload = build_finance_quality_preparation(**prepared_args).to_payload()
    assert not payload['coverage']['required_calendar_matches']
    assert not payload['review']['pending_controls'] and not payload['designation']['pending_controls']
    assert payload['assurance_scope'] == 'BOUND_PRESENTED_MATERIAL_ONLY'
    assert not {'quality_checks', 'quality_result', 'authorized', 'status'} & payload.keys()
