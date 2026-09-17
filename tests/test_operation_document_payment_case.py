"""Synthetic documentary example; not an extraction or QTG producer."""
import json
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace

import pytest

from eios.core.finance_decision_input_package import build_finance_decision_input_package
from eios.core.models import DecisionContext, PurchaseOperation
from eios.finance.models import CashFlow, FinanceBasicInput, FinancialSnapshot
from eios.finance.provenance import run_provenanced_finance_basic
from eios.parameters.center import Configuration, ParameterConfigurationCenter, ParameterDefinition


def case():
    return json.loads((Path(__file__).parent / 'fixtures/operation_document_payment_case_v2.json').read_text())


def test_documentary_totals_and_installment_identity():
    data = case()
    assert data['case_kind'] == 'SYNTHETIC'
    assert Decimal(data['quantity']) * Decimal(data['unit_price']) == Decimal(data['base_amount'])
    assert Decimal(data['base_amount']) + Decimal(data['documented_tax_amount']) == Decimal(data['documented_total_due'])
    assert sum(Decimal(p['amount']) for p in data['payments']) == Decimal('1210.00')
    assert len({p['installment_ref'] for p in data['payments']}) == 2
    assert all(p['pdf_pages'] == [2, 3] for p in data['payments'])


@pytest.mark.parametrize('horizon,expected_dates,expected_treasury', [
    (30, ['2026-09-30'], '1395.00'),
    (60, ['2026-09-30', '2026-10-30'], '790.00'),
])
def test_documentary_payments_captured_and_counted_once(horizon, expected_dates, expected_treasury):
    data = case()
    # These identities and opening balance are explicit test setup, not PDF facts.
    context = DecisionContext(decision_id='TEST-DOC-D', scenario_id='TEST-DOC-S',
                              rules_version='test-r', parameters_version='test-p', data_snapshot_id='test-snap')
    now = datetime(2026, 9, 17, 12, tzinfo=timezone.utc)
    configuration = Configuration(1, 'P-FIN-001', 'TEST-COMPANY', str(horizon), 'numeric', 'días', now, None, now, now)
    center = ParameterConfigurationCenter(
        SimpleNamespace(get_parameter=lambda pid: ParameterDefinition(pid)),
        SimpleNamespace(can_modify=lambda *args: False),
        SimpleNamespace(get_at=lambda *args: configuration),
    )
    purchase = PurchaseOperation(decision_id=context.decision_id, scenario_id=context.scenario_id,
                                 article_id=data['article_id'], supplier_id='TEST-SUPPLIER',
                                 quantity=Decimal(data['quantity']), unit_price=Decimal(data['unit_price']),
                                 operation_date=date.fromisoformat(data['document_date']))
    flows = tuple(CashFlow(flow_id=p['installment_ref'], flow_type='PAYMENT',
                          amount=Decimal(p['amount']), currency=data['currency'],
                          due_date=date.fromisoformat(p['due_date']), due_date_evidenced=True,
                          source_ref='synthetic:PED-2026-015:CONF-015:' + p['installment_ref'],
                          evidence_state='DEMONSTRATED') for p in data['payments'])
    finance = FinanceBasicInput(context=context, snapshot=FinancialSnapshot(
        company_scope='TEST-COMPANY', as_of_date=now.date(), data_snapshot_id=context.data_snapshot_id,
        currency='EUR', available_treasury=Decimal('2000'), treasury_evidence_ref='synthetic:opening-balance'),
        cash_flows=flows, horizon_days=horizon)
    package = build_finance_decision_input_package(purchase=purchase, context=context, evidence=(),
        finance_input=finance, company_id='TEST-COMPANY', effective_at=now,
        requested_parameter_ids=('P-FIN-001',), center=center)
    assert len(package.finance_input.cash_flows) == 2  # Capture preserves the later installment.
    execution = run_provenanced_finance_basic(package.finance_input, package.horizon_resolution)
    projection = execution.finance_result.projection
    assert projection.status == 'DETERMINED'  # Analytical status for synthetic inputs only.
    assert [p.date.isoformat() for p in projection.points] == expected_dates
    assert all(p.payments == Decimal('605') for p in projection.points)
    assert projection.financial_capacity_forecast == Decimal(expected_treasury)
    assert package.finance_input.treasury_minimum is None
