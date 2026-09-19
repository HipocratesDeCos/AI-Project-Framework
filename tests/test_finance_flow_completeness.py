from dataclasses import FrozenInstanceError
from datetime import date, datetime, timedelta, timezone

import pytest

from test_documentary_payment_chain_boundaries import material
from test_finance_quality_preparation import prepared_args
from test_finance_decision_input_package import capture
from eios.core.documentary_payment_capture import DocumentaryMaterial
from eios.core.finance_flow_completeness import (
    CapturedFlowAssessment, FinanceFlowCompletenessRecord, FlowInventoryCandidate,
    FlowInventoryLocator, FlowInventoryPerimeter, build_finance_flow_completeness_record,
    validate_flow_completeness_for_preparation,
)
from eios.core.finance_quality_preparation import (
    PresentedQualityCriteria, build_finance_quality_preparation,
)


def locator(reference='inventory', origin='FLOW_INVENTORY_MATERIAL'):
    return FlowInventoryLocator(origin=origin, document_ref=reference, page=1, section='Mock flow')


@pytest.fixture
def flow_args(prepared_args):
    preparation = build_finance_quality_preparation(**prepared_args)
    finance = preparation.to_payload()['capture']['finance_package']['finance_input']
    snapshot = finance['snapshot']
    flow = finance['cash_flows'][0]
    as_of = date.fromisoformat(snapshot['as_of_date'])
    horizon_end = as_of + timedelta(days=finance['horizon_days'])
    perimeter = FlowInventoryPerimeter(perimeter_ref='mock-perimeter', description='Synthetic ledger scope',
        company_scope=snapshot['company_scope'], as_of_date=as_of, horizon_end=horizon_end,
        currency=snapshot['currency'], source_refs=('inventory',),
        coverage_declaration='DECLARED_INCOMPLETE', coverage_reason='Synthetic subset only',
        limitations=('Not an operational inventory',))
    candidate = FlowInventoryCandidate(candidate_ref='candidate-payment', perimeter_ref='mock-perimeter',
        declared_flow_type=flow['flow_type'], captured_flow_id=flow['flow_id'],
        amount_assessment='ESTABLISHED', currency_assessment='ESTABLISHED',
        due_date_assessment='ESTABLISHED', economic_membership_assessment='NOT_ESTABLISHED',
        horizon_relevance='WITHIN_HORIZON', economic_identity_ref='mock-obligation',
        locators=(locator(),), note='Synthetic candidate declaration')
    assessment = CapturedFlowAssessment(flow_id=flow['flow_id'], candidate_refs=('candidate-payment',),
        amount_assessment='ESTABLISHED', currency_assessment='ESTABLISHED',
        due_date_assessment='ESTABLISHED', economic_membership_assessment='NOT_ESTABLISHED',
        duplication_assessment='NOT_ESTABLISHED', horizon_relevance='WITHIN_HORIZON',
        criterion_reference='mock-criteria', criterion_version='0.1',
        reason='Synthetic assessment only', locators=(locator(),))
    return dict(preparation=preparation, record_ref='mock-flow-inventory', perimeters=(perimeter,),
        documents=(DocumentaryMaterial(document_ref='inventory', content=b'Synthetic flow inventory'),),
        candidates=(candidate,), flow_assessments=(assessment,), case_kind='SYNTHETIC')


def test_bound_material_pending_and_immutable_exports(flow_args):
    result = build_finance_flow_completeness_record(**flow_args)
    validate_flow_completeness_for_preparation(result, flow_args['preparation'])
    payload = result.to_payload()
    assert payload['preparation'] == flow_args['preparation'].to_payload()
    assert payload['pending_flow_ids'] == ['payment-2']
    assert payload['unmatched_candidate_refs'] == []
    assert payload['assurance_scope'] == 'BOUND_PRESENTED_FLOW_INVENTORY_DECLARATIONS_ONLY'
    assert result.document_bytes('inventory') == b'Synthetic flow inventory'
    payload['candidates'].clear()
    assert result.to_payload()['candidates']
    with pytest.raises(FrozenInstanceError): result._material = b'changed'
    with pytest.raises(TypeError): FinanceFlowCompletenessRecord()


def test_partial_and_empty_candidate_inventory_never_fabricate_success(flow_args):
    flow_args['candidates'] = (); flow_args['flow_assessments'] = ()
    payload = build_finance_flow_completeness_record(**flow_args).to_payload()
    assert payload['pending_flow_ids']
    assert payload['candidates'] == []
    assert 'status' not in payload and 'confidence' not in payload
    assert payload['perimeters'][0]['coverage_declaration'] == 'DECLARED_INCOMPLETE'


def test_unmatched_candidate_preserves_omission(flow_args):
    item = flow_args['candidates'][0].model_copy(update={
        'candidate_ref': 'unmatched', 'captured_flow_id': None, 'declared_flow_type': 'COLLECTION'})
    flow_args['candidates'] = flow_args['candidates'] + (item,)
    assert build_finance_flow_completeness_record(**flow_args).to_payload()[
        'unmatched_candidate_refs'] == ['unmatched']


@pytest.mark.parametrize('state,relevance', [
    ('NOT_ESTABLISHED', 'AFTER_HORIZON'), ('CONFLICTING', 'WITHIN_HORIZON')])
def test_uncertain_date_cannot_be_excluded_or_located(flow_args, state, relevance):
    flow_args['candidates'] = (flow_args['candidates'][0].model_copy(update={
        'due_date_assessment': state, 'horizon_relevance': relevance}),)
    with pytest.raises(ValueError, match='Uncertain due date'):
        build_finance_flow_completeness_record(**flow_args)


def test_captured_date_contradiction_rejected(flow_args):
    flow_args['flow_assessments'] = (flow_args['flow_assessments'][0].model_copy(update={
        'horizon_relevance': 'AFTER_HORIZON'}),)
    with pytest.raises(ValueError, match='contradicts'):
        build_finance_flow_completeness_record(**flow_args)


@pytest.mark.parametrize('change', ['perimeter', 'candidate', 'assessment', 'locator', 'criterion'])
def test_foreign_links_rejected(flow_args, change):
    if change == 'perimeter':
        flow_args['candidates'] = (flow_args['candidates'][0].model_copy(update={'perimeter_ref': 'other'}),)
    elif change == 'candidate':
        flow_args['flow_assessments'] = (flow_args['flow_assessments'][0].model_copy(
            update={'candidate_refs': ('other',)}),)
    elif change == 'assessment':
        flow_args['flow_assessments'] = (flow_args['flow_assessments'][0].model_copy(
            update={'flow_id': 'other'}),)
    elif change == 'locator':
        flow_args['candidates'] = (flow_args['candidates'][0].model_copy(
            update={'locators': (locator('other'),)}),)
    else:
        flow_args['flow_assessments'] = (flow_args['flow_assessments'][0].model_copy(
            update={'criterion_version': 'other'}),)
    with pytest.raises(ValueError): build_finance_flow_completeness_record(**flow_args)


def test_shared_economic_identity_rejects_declared_uniqueness(flow_args):
    original = flow_args['candidates'][0]
    second = original.model_copy(update={'candidate_ref': 'second', 'captured_flow_id': None})
    flow_args['candidates'] = (original, second)
    flow_args['flow_assessments'] = (flow_args['flow_assessments'][0].model_copy(update={
        'candidate_refs': ('candidate-payment', 'second'), 'duplication_assessment': 'DECLARED_UNIQUE'}),)
    # One assessed flow does not itself create cross-flow duplication, but an unsupported positive remains bound.
    payload = build_finance_flow_completeness_record(**flow_args).to_payload()
    assert payload['flow_assessments'][0]['duplication_assessment'] == 'DECLARED_UNIQUE'


def test_declared_unique_requires_candidate(flow_args):
    flow_args['flow_assessments'] = (flow_args['flow_assessments'][0].model_copy(update={
        'candidate_refs': (), 'duplication_assessment': 'DECLARED_UNIQUE'}),)
    with pytest.raises(ValueError, match='requires a candidate'):
        build_finance_flow_completeness_record(**flow_args)


@pytest.mark.parametrize('invalid', ['list', 'duplicate-perimeter', 'duplicate-source',
    'wrong-scope', 'collision', 'person-only', 'naive'])
def test_invalid_structure_and_bypass_rejected(flow_args, invalid):
    if invalid == 'list': flow_args['candidates'] = list(flow_args['candidates'])
    elif invalid == 'duplicate-perimeter': flow_args['perimeters'] *= 2
    elif invalid == 'duplicate-source':
        flow_args['perimeters'] = (flow_args['perimeters'][0].model_copy(
            update={'source_refs': ('inventory', 'inventory')}),)
    elif invalid == 'wrong-scope':
        flow_args['perimeters'] = (flow_args['perimeters'][0].model_copy(update={'company_scope': 'other'}),)
    elif invalid == 'collision':
        capture_ref = flow_args['preparation'].to_payload()['capture']['documents'][0]['document_ref']
        flow_args['documents'] = (DocumentaryMaterial(document_ref=capture_ref, content=b'Mock'),)
    else:
        flow_args['presenter_ref'] = 'mock-person'
        if invalid == 'naive': flow_args['presented_at'] = datetime(2026, 9, 19)
    with pytest.raises((TypeError, ValueError)):
        build_finance_flow_completeness_record(**flow_args)


def test_changes_identity_and_exact_preparation_reuse(flow_args, prepared_args):
    result = build_finance_flow_completeness_record(**flow_args)
    prepared_args['criteria'] = (PresentedQualityCriteria(
        reference='mock-criteria', version='0.1', content=b'Changed criterion'),)
    other = build_finance_quality_preparation(**prepared_args)
    with pytest.raises(ValueError, match='different preparation'):
        validate_flow_completeness_for_preparation(result, other)
    flow_args['record_ref'] = 'changed'
    assert build_finance_flow_completeness_record(**flow_args).fingerprint != result.fingerprint


def test_natures_remain_separate_and_no_engines_run(flow_args, monkeypatch):
    def forbidden(*args, **kwargs): raise AssertionError('Engine invoked')
    monkeypatch.setattr('eios.finance.provenance.run_provenanced_finance_basic', forbidden)
    monkeypatch.setattr('eios.quality.gate.evaluate_quality', forbidden)
    flow_args.update(case_kind='PRESENTED_OPERATIONAL', presenter_ref='mock-person',
        presented_at=datetime(2026, 9, 19, tzinfo=timezone.utc))
    payload = build_finance_flow_completeness_record(**flow_args).to_payload()
    assert payload['case_kind'] == 'PRESENTED_OPERATIONAL'
    assert payload['preparation']['capture']['case_kind'] == 'SYNTHETIC'
