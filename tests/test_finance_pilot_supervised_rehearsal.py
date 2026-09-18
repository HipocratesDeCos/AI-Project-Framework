"""Synthetic rehearsal of presented acts, not an operational review or QTG."""
from datetime import date
from decimal import Decimal

import pytest

from test_documentary_payment_chain_boundaries import material, capture, review_for, designation_for
from eios.core.documentary_payment_capture import DocumentaryLocator, DocumentaryMaterial, build_documentary_payment_capture
from eios.core.finance_quality_preparation import PresentedQualityCriteria, build_finance_quality_preparation
from eios.core.required_installment_coverage import check_required_installment_coverage
from eios.core.treasury_documentary_support import TreasuryDeclaration, TreasuryObservation, CONDITIONS, build_treasury_documentary_support
from eios.core.treasury_contextual_assessment import (
    TreasuryContextualDeclaration, ContextualSupportLocator,
    build_treasury_contextual_assessment, validate_contextual_assessment_for_material,
)


def rehearse(args, calendar, *, treasury_unknown=False, treasury_conflict=False, incomplete=False):
    source = build_documentary_payment_capture(**args)
    coverage = check_required_installment_coverage(capture=source, calendar=calendar)
    review = review_for(source, complete=not incomplete)
    designation = designation_for(review, complete=not incomplete)
    preparation = build_finance_quality_preparation(capture=source, calendar=calendar, coverage=coverage,
        review=review, designation=designation, criteria=(PresentedQualityCriteria(
            reference='mock-supervision', version='0.1', content=b'Synthetic rehearsal criteria, not operational approval'),))
    snapshot = preparation.to_payload()['capture']['finance_package']['finance_input']['snapshot']
    support_locator = DocumentaryLocator(document_ref='mock-treasury', page=1, section='Mock balance')
    support = build_treasury_documentary_support(preparation=preparation, record_ref='mock-support',
        target_company_scope=snapshot['company_scope'], case_kind='SYNTHETIC',
        documents=(DocumentaryMaterial(document_ref='mock-treasury', content=b'Synthetic treasury only'),),
        declaration=TreasuryDeclaration(documentary_company=snapshot['company_scope'],
            currency='USD' if treasury_conflict else snapshot['currency'],
            economic_date=date.fromisoformat(snapshot['as_of_date']),
            available_amount=None if treasury_unknown else Decimal(str(snapshot['available_treasury'])),
            locators=(support_locator,)),
        observations=() if incomplete else tuple(TreasuryObservation(condition=c,
            outcome='DECLARED_INCONSISTENT' if treasury_conflict and c == 'RESTRICTIONS' else 'DECLARED_CONSISTENT',
            note='Mock reported restriction' if treasury_conflict and c == 'RESTRICTIONS' else 'Synthetic assertion only',
            locators=(support_locator,)) for c in CONDITIONS))
    contextual = build_treasury_contextual_assessment(preparation=preparation, treasury_support=support,
        assessment_ref='mock-context', declarations=() if incomplete else tuple(TreasuryContextualDeclaration(
            condition=c, criterion_reference='mock-supervision', criterion_version='0.1',
            applicability='APPLIES', applicability_reason='Mock documentary-cutoff use',
            necessity='NECESSARY_FOR_DETERMINED_PROJECTION', necessity_reason='Mock contextual assertion',
            impact_reason='Presented explanation, not software determination',
            support_assessment='DECLARED_SUFFICIENT', support_reason='Synthetic assertion, not source verification',
            observation_conditions=(c,), support_locators=(ContextualSupportLocator(
                origin='TREASURY_SUPPORT', document_ref='mock-treasury', page=1, section='Mock balance'),)) for c in CONDITIONS))
    validate_contextual_assessment_for_material(contextual, preparation, support)
    return preparation, support, contextual


@pytest.fixture(autouse=True)
def prohibit_execution(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError('Rehearsal must not execute Finance or QTG')
    monkeypatch.setattr('eios.finance.provenance.run_provenanced_finance_basic', forbidden)
    monkeypatch.setattr('eios.quality.gate.evaluate_quality', forbidden)


def test_complete_presented_chain_is_not_operational_authority(material):
    args, calendar, _ = material
    preparation, support, contextual = rehearse(args, calendar)
    payload = preparation.to_payload()
    assert payload['coverage']['required_calendar_matches']
    assert payload['review']['pending_controls'] == payload['designation']['pending_controls'] == []
    assert contextual.to_payload()['pending_conditions'] == []
    assert payload['designation']['designation_kind'] == 'SYNTHETIC'
    assert support.to_payload()['case_kind'] == 'SYNTHETIC'
    for record in (preparation, support, contextual):
        assert not {'authorized', 'quality_result', 'quality_checks', 'status', 'confidence', 'paid'} & record.to_payload().keys()


@pytest.mark.parametrize('case', ['missing-quota', 'foreign-order', 'unknown-treasury', 'treasury-conflict', 'incomplete-review'])
def test_positive_declarations_do_not_remove_rehearsal_limitations(material, case):
    args, calendar, _ = material
    if case == 'missing-quota':
        args['bindings'] = args['bindings'][:1]
    if case == 'foreign-order':
        args['order_version'] = 'foreign'
    preparation, support, contextual = rehearse(args, calendar,
        treasury_unknown=case == 'unknown-treasury', treasury_conflict=case == 'treasury-conflict',
        incomplete=case == 'incomplete-review')
    payload = preparation.to_payload()
    if case == 'missing-quota':
        assert not payload['coverage']['required_calendar_matches']
        assert 'MISSING_ASSOCIATION' in payload['coverage']['observations'][1]['issues']
    elif case == 'foreign-order':
        assert payload['coverage']['reference_mismatches'] == ['order_version']
    elif case == 'unknown-treasury':
        assert support.to_payload()['technical_comparisons']['amount_matches'] is None
    elif case == 'treasury-conflict':
        assert support.to_payload()['technical_comparisons']['currency_matches'] is False
        assert any(o['outcome'] == 'DECLARED_INCONSISTENT' for o in support.to_payload()['observations'])
    else:
        assert len(payload['review']['pending_controls']) == 13
        assert len(payload['designation']['pending_controls']) == 7
        assert len(contextual.to_payload()['pending_conditions']) == 6


def test_document_change_requires_new_complete_chain(material):
    args, calendar, _ = material
    old_preparation, old_support, old_context = rehearse(args, calendar)
    args['documents'] = (args['documents'][0].model_copy(update={'content': b'Changed synthetic terms'}), args['documents'][1])
    new_preparation, new_support, new_context = rehearse(args, calendar)
    assert new_preparation.fingerprint != old_preparation.fingerprint
    assert new_context.fingerprint != old_context.fingerprint
    with pytest.raises(ValueError, match='different material'):
        validate_contextual_assessment_for_material(old_context, new_preparation, new_support)
