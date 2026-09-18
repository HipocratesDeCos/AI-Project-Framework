from dataclasses import FrozenInstanceError
from datetime import date
from decimal import Decimal

import pytest

from test_finance_decision_input_package import capture
from eios.core.finance_decision_input_package import build_finance_decision_input_package
from eios.core.documentary_payment_capture import (
    DocumentaryMaterial, DocumentaryLocator, DocumentaryPaymentBinding, build_documentary_payment_capture,
)
from eios.core.required_installment_coverage import (
    RequiredInstallment, RequiredInstallmentCalendar, RequiredInstallmentCoverage,
    check_required_installment_coverage, validate_coverage_for_material,
)


@pytest.fixture
def material(capture):
    kwargs, _, _ = capture
    first = kwargs['finance_input'].cash_flows[0]
    flows = tuple(first.model_copy(update={'flow_id': f'payment-{n}', 'amount': Decimal('605'),
        'currency': 'EUR', 'due_date': day}) for n, day in [(1, date(2026, 9, 30)), (2, date(2026, 10, 30))])
    kwargs['finance_input'] = kwargs['finance_input'].model_copy(update={'cash_flows': flows})
    package = build_finance_decision_input_package(**kwargs)
    locators = (DocumentaryLocator(document_ref='order', page=2, section='Payment terms'),
                DocumentaryLocator(document_ref='confirmation', page=3, section='Calendar ratification'))
    required = tuple(RequiredInstallment(installment_ref=f'PED-2026-015 / cuota {n}', sequence=n,
        amount=Decimal('605'), currency='EUR', due_date=day, locators=locators)
        for n, day in [(1, date(2026, 9, 30)), (2, date(2026, 10, 30))])
    calendar = RequiredInstallmentCalendar(declaration_ref='synthetic-required-calendar',
        authority_ref='project-owner:explicit-synthetic-case-requirement', case_kind='SYNTHETIC',
        operation_ref='COMPRA-2026-001', order_ref='PED-2026-015', order_version='1', confirmation_ref='CONF-015',
        total_due=Decimal('1210'), currency='EUR', installments=required)
    args = dict(package=package, documents=(DocumentaryMaterial(document_ref='order', content=b'Synthetic order stand-in'),
        DocumentaryMaterial(document_ref='confirmation', content=b'Synthetic confirmation stand-in')),
        bindings=tuple(DocumentaryPaymentBinding(installment_ref=i.installment_ref,
            flow_id=f.flow_id, locators=locators) for i, f in zip(required, flows)),
        case_kind='SYNTHETIC', operation_ref=calendar.operation_ref, order_ref=calendar.order_ref,
        order_version=calendar.order_version, confirmation_ref=calendar.confirmation_ref)
    return args, calendar, kwargs


def checked(material):
    args, calendar, _ = material
    return check_required_installment_coverage(capture=build_documentary_payment_capture(**args), calendar=calendar)


def test_exact_two_obligations_with_two_sources(material):
    result = checked(material).to_payload()
    assert result['required_calendar_matches']
    assert len(result['observations']) == len(result['capture']['bindings']) == 2
    assert all(len(b['locators']) == 2 for b in result['capture']['bindings'])
    assert result['calendar']['total_due'] == '1210'
    assert result['capture']['finance_package']['finance_input']['horizon_days'] == material[0]['package'].finance_input.horizon_days
    assert result['calendar']['case_kind'] == result['capture']['case_kind'] == 'SYNTHETIC'


@pytest.mark.parametrize('missing', [0, 1])
def test_any_missing_installment_prevents_match(material, missing):
    args, _, _ = material
    args['bindings'] = tuple(b for n, b in enumerate(args['bindings']) if n != missing)
    result = checked(material).to_payload()
    assert not result['required_calendar_matches']
    assert result['observations'][missing]['issues'] == ['MISSING_ASSOCIATION']
    assert result['unassociated_payment_flow_ids'] == [f'payment-{missing+1}']


def test_same_total_wrong_identity_not_sufficient(material):
    args, _, _ = material
    args['bindings'] = (args['bindings'][0], args['bindings'][1].model_copy(update={'installment_ref': 'other'}))
    result = checked(material).to_payload()
    assert not result['required_calendar_matches']
    assert result['unexpected_installment_refs'] == ['other']
    assert sum(Decimal(f['amount']) for f in result['capture']['finance_package']['finance_input']['cash_flows']) == Decimal('1210')


@pytest.mark.parametrize('field,value,issue', [('amount', Decimal('604'), 'AMOUNT_MISMATCH'),
    ('currency', 'USD', 'CURRENCY_MISMATCH'), ('due_date', date(2026, 10, 30), 'DUE_DATE_MISMATCH'),
    ('amount', None, 'AMOUNT_MISMATCH')])
def test_discrepancies_observed_without_correction(material, field, value, issue):
    args, _, kwargs = material
    finance = kwargs['finance_input']
    first = finance.cash_flows[0].model_copy(update={field: value, 'evidence_state': 'NOT_EVIDENCED'})
    kwargs['finance_input'] = finance.model_copy(update={'cash_flows': (first, finance.cash_flows[1])})
    args['package'] = build_finance_decision_input_package(**kwargs)
    result = checked(material).to_payload()
    assert issue in result['observations'][0]['issues']
    assert not result['required_calendar_matches']
    assert result['observations'][0]['observed_evidence_state'] == 'NOT_EVIDENCED'


@pytest.mark.parametrize('field', ['operation_ref', 'order_ref', 'order_version', 'confirmation_ref'])
def test_foreign_reference(material, field):
    material[0][field] = 'foreign'
    result = checked(material).to_payload()
    assert result['reference_mismatches'] == [field]
    assert not result['required_calendar_matches']


def test_order_of_storage_not_execution_order(material):
    args, calendar, kwargs = material
    args['bindings'] = tuple(reversed(args['bindings']))
    kwargs['finance_input'] = kwargs['finance_input'].model_copy(update={'cash_flows': tuple(reversed(kwargs['finance_input'].cash_flows))})
    args['package'] = build_finance_decision_input_package(**kwargs)
    calendar = calendar.model_copy(update={'installments': tuple(reversed(calendar.installments))})
    assert check_required_installment_coverage(capture=build_documentary_payment_capture(**args), calendar=calendar).to_payload()['required_calendar_matches']


def test_support_not_associated_remains_visible(material):
    args, _, _ = material
    args['bindings'] = (args['bindings'][0].model_copy(update={'locators': args['bindings'][0].locators[:1]}), args['bindings'][1])
    assert checked(material).to_payload()['observations'][0]['issues'] == ['REQUIRED_SUPPORT_NOT_ASSOCIATED']


@pytest.mark.parametrize('change', ['total', 'duplicate', 'sequence', 'nan', 'bypass'])
def test_invalid_declared_calendar_rejected(material, change):
    args, calendar, _ = material
    first, second = calendar.installments
    updates = {
        'total': {'total_due': Decimal('1000')},
        'duplicate': {'installments': (first, first)},
        'sequence': {'installments': (first, second.model_copy(update={'due_date': first.due_date}))},
        'nan': {'total_due': Decimal('NaN')},
        'bypass': {'installments': (first.model_copy(update={'sequence': True}), second)},
    }
    with pytest.raises(ValueError):
        check_required_installment_coverage(capture=build_documentary_payment_capture(**args), calendar=calendar.model_copy(update=updates[change]))


def test_unknown_additional_payment_not_discarded(material):
    args, _, kwargs = material
    finance = kwargs['finance_input']
    additional = finance.cash_flows[0].model_copy(update={'flow_id': 'unresolved-alias'})
    kwargs['finance_input'] = finance.model_copy(update={'cash_flows': finance.cash_flows + (additional,)})
    args['package'] = build_finance_decision_input_package(**kwargs)
    result = checked(material).to_payload()
    assert result['unassociated_payment_flow_ids'] == ['unresolved-alias']
    assert result['assurance_scope'] == 'DECLARED_CALENDAR_STRUCTURAL_MATCH_ONLY'
    assert 'economic_completeness' not in result


def test_immutable_binding_to_both_materials(material):
    args, calendar, _ = material
    source = build_documentary_payment_capture(**args)
    result = check_required_installment_coverage(capture=source, calendar=calendar)
    result.to_payload()['observations'].clear()
    assert len(result.to_payload()['observations']) == 2
    with pytest.raises(FrozenInstanceError):
        result._material = b'forged'
    with pytest.raises(TypeError):
        RequiredInstallmentCoverage()
    validate_coverage_for_material(result, source, calendar)
    with pytest.raises(ValueError, match='different'):
        validate_coverage_for_material(result, source, calendar.model_copy(update={'authority_ref': 'changed'}))
    args['documents'] = (args['documents'][0].model_copy(update={'content': b'changed'}), args['documents'][1])
    changed = build_documentary_payment_capture(**args)
    with pytest.raises(ValueError, match='different'):
        validate_coverage_for_material(result, changed, calendar)
    assert result.fingerprint != check_required_installment_coverage(capture=changed, calendar=calendar).fingerprint


def test_structural_match_never_upgrades_evidence_or_calls_engines(material, monkeypatch):
    import eios.finance.provenance as provenance
    import eios.quality.gate as gate
    def forbidden(*args, **kwargs):
        raise AssertionError('No analytical or QTG execution')
    monkeypatch.setattr(provenance, 'run_provenanced_finance_basic', forbidden)
    monkeypatch.setattr(gate, 'evaluate_quality', forbidden)
    args, _, kwargs = material
    finance = kwargs['finance_input']
    kwargs['finance_input'] = finance.model_copy(update={'cash_flows': tuple(f.model_copy(update={
        'evidence_state': 'NOT_EVIDENCED', 'due_date_evidenced': False}) for f in finance.cash_flows)})
    args['package'] = build_finance_decision_input_package(**kwargs)
    result = checked(material).to_payload()
    assert result['required_calendar_matches']  # Structural comparison, not admissibility.
    assert all(o['observed_evidence_state'] == 'NOT_EVIDENCED' for o in result['observations'])
    assert all(not o['observed_due_date_evidenced'] for o in result['observations'])
    assert not {'quality_result', 'authorized', 'paid'} & result.keys()
