import json
import sqlite3
import unittest

from eios.company_financial_context import financial_context
from tests import test_company_purchase_screen as fixture


class FinancialContextTest(unittest.TestCase):
    setUp = fixture.PurchaseScreenTest.setUp
    tearDown = fixture.PurchaseScreenTest.tearDown

    def add(self, kind, record_id, data, dataset='one'):
        with sqlite3.connect(self.path) as c:
            c.execute('INSERT INTO documentary_company_record VALUES(?,?,?,?)',
                      (dataset,kind,record_id,json.dumps(dict(kind=kind,record_id=record_id,data=data,source_refs=[dict(document_ref='DOC-FIN')]))))

    def financial_data(self):
        self.add('financial_snapshot','SNAP',dict(company_scope='one',as_of_date='2026-09-30',
            data_snapshot_id='financial-snapshot',currency='EUR',available_treasury='5000',treasury_evidence_ref='DOC-FIN'))
        self.add('working_capital','WC',dict(company_scope='one',as_of_date='2026-09-30',currency='EUR',
            current_assets='20000',current_liabilities='12000',assets_source_ref='DOC-BAL',liabilities_source_ref='DOC-BAL'))
        for identity,kind,amount in [('C-1','COLLECTION','1000'),('P-1','PAYMENT','500')]:
            self.add('cash_flow',identity,dict(canonical=dict(flow_id=identity,flow_type=kind,amount=amount,
                currency='EUR',due_date='2026-10-15',due_date_evidenced=False,source_ref='DOC-FIN',evidence_state='NOT_EVIDENCED')))

    def capture(self):
        return financial_context(self.desk.store,'one',self.desk.store.describe('one'))

    def test_existing_inputs_preserved_without_evidence_promotion(self):
        self.financial_data()
        context = self.capture()
        self.assertEqual(context['financial_snapshot']['available_treasury'],'5000')
        self.assertEqual(context['working_capital_input']['current_assets'],'20000')
        self.assertEqual(len(context['cash_flows']),2)
        self.assertEqual(context['evidence_pending_count'],2)
        self.assertTrue(all(f['canonical']['evidence_state']=='NOT_EVIDENCED' for f in context['cash_flows']))
        self.assertEqual(context['execution_status'],'NOT_EXECUTED')
        self.assertEqual(context['viability_status'],'NOT_EVALUATED')
        self.assertIsNone(context['cash_flow_inventory_complete'])
        self.assertFalse(context['decision_authority'])
        self.assertNotIn('financial_capacity_forecast',context)

    def test_invoice_installments_and_forecast_are_not_added_as_extra_flows(self):
        self.financial_data()
        self.add('purchase_installment','I-1',dict(amount='500',due_date='2026-10-15'))
        self.add('daily_treasury_forecast','D-1',dict(amount='500'))
        context = self.capture()
        self.assertEqual(len(context['cash_flows']),2)
        self.assertEqual(context['record_counts']['daily_treasury_forecast'],1)

    def test_company_scope_and_invalid_canonical_data_are_explicit(self):
        self.financial_data()
        self.add('cash_flow','BAD',dict(canonical=dict(flow_id='BAD',flow_type='UNKNOWN')))
        context=self.capture()
        self.assertTrue(any('formato canónico' in x for x in context['issues']))
        other=financial_context(self.desk.store,'two',self.desk.store.describe('two'))
        self.assertIsNone(other['financial_snapshot'])
        self.assertEqual(other['cash_flows'],[])

    def test_duplicate_identity_is_not_silently_certified(self):
        self.financial_data()
        self.add('cash_flow','OTHER',dict(canonical=dict(flow_id='P-1',flow_type='PAYMENT',amount='500',currency='EUR',
            due_date='2026-10-15',source_ref='DOC-FIN',evidence_state='NOT_EVIDENCED')))
        context=self.capture()
        self.assertTrue(any('duplicada' in x for x in context['issues']))
        self.assertEqual(context['execution_status'],'NOT_EXECUTED')

    def test_review_and_print_preserve_financial_capture(self):
        self.financial_data()
        saved=self.desk.save(self.data)
        review=self.desk.review('one',saved['proposal_id'])
        self.assertEqual(review['version'],'COMPANY-CONTEXT-REVIEW-04')
        self.assertEqual(review['financial_context']['financial_snapshot']['available_treasury'],'5000')
        html=self.desk.printable_report('one',saved['proposal_id'],review['review_id'])
        self.assertIn('5.000,00 EUR',html)
        self.assertIn('15/10/2026',html)
        self.assertIn('Pendiente de validar',html)
        with sqlite3.connect(self.path) as c:
            c.execute("DELETE FROM documentary_company_record WHERE kind='cash_flow'")
        self.assertEqual(self.desk.printable_report('one',saved['proposal_id'],review['review_id']),html)

    def test_no_silent_zero_or_default_horizon(self):
        context=self.capture()
        self.assertIsNone(context['financial_snapshot'])
        self.assertNotIn('horizon_days',context)
        self.assertNotIn('treasury_minimum',context)
        self.assertTrue(context['issues'])
        self.assertEqual(context['viability_status'],'NOT_EVALUATED')
