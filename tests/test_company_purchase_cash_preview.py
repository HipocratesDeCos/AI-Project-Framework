from copy import deepcopy
from decimal import Decimal
import unittest
from tests import test_company_finance_activation as fixture
from eios.company_purchase_cash_preview import preview


class PurchaseCashPreviewTest(unittest.TestCase):
    setUp=fixture.FinanceActivationTest.setUp
    tearDown=fixture.FinanceActivationTest.tearDown
    add=fixture.FinanceActivationTest.add
    prepare=fixture.FinanceActivationTest.prepare
    activate=fixture.FinanceActivationTest.activate
    financial_data=fixture.FinanceActivationTest.financial_data

    def ready(self):
        self.financial_data();self.prepare();self.activate()
        self.data.update(shipping_mode='NONE',quantity='100',unit_price='100')
        self.state=self.desk.sales_state('one')
        self.data['documentary_context_fingerprint']=self.state['documentary_context']['fingerprint']

    def test_known_shortfall_before_save_and_verified_price_quantity_alternatives(self):
        self.ready();before=deepcopy(self.state['sales_financial_context'])
        r=self.desk.purchase_cash_preview(self.data)
        self.assertEqual(r['status'],'SHORTFALL',r['message'])
        self.assertEqual(Decimal(r['scenario']['deficit']),Decimal('8600'))
        self.assertEqual(r['scenario']['first_shortfall_date'],'2026-11-01')
        self.assertEqual({a['kind'] for a in r['alternatives']},{'PRICE','QUANTITY'})
        for a in r['alternatives']:
            tested=preview(self.path,self.state,dict(self.data,**a['patch']),alternatives=False)
            self.assertEqual(tested['status'],'WITHIN_DECLARED_SCENARIO')
        self.assertEqual(r['capital_measure']['amount'],r['scenario']['deficit'])
        self.assertEqual(self.desk.state('one')['purchases'],[])
        self.assertEqual(before,self.desk.sales_state('one')['sales_financial_context'])
        self.assertFalse(r['decision_authority']);self.assertEqual(r['viability_status'],'NOT_EVALUATED')
        self.assertEqual(r['formal_engine']['with_declared_plan']['projection']['status'],'NOT_EVIDENCED')

    def test_balance_overrun_remains_visible_without_activated_horizon_or_complete_freight(self):
        self.financial_data()
        self.data.update(shipping_mode='NONE',quantity='20000',unit_price='8',vat_percent='21')
        state=self.desk.sales_state('one')
        r=preview(self.path,state,self.data)
        self.assertEqual(r['status'],'PENDING')
        self.assertIn('horizonte',r['message'])
        b=r['balance_comparison']
        self.assertEqual(Decimal(b['purchase_amount']),Decimal('193600'))
        self.assertEqual(Decimal(b['excess_over_balance']),Decimal('188600'))
        self.assertFalse(b['includes_forecast'])
        self.assertNotIn('scenario',r)
        partial=preview(self.path,state,dict(self.data,shipping_mode='PENDING'))
        self.assertEqual(partial['balance_comparison']['amount_basis'],'MERCHANDISE_ONLY')
        self.assertEqual(partial['status'],'PENDING')
        state['sales_financial_context']['financial_snapshot']=None
        missing=preview(self.path,state,self.data)
        self.assertEqual(missing['status'],'PENDING')
        self.assertNotIn('balance_comparison',missing)

    def test_deferral_only_when_collections_support_it_inside_horizon(self):
        self.ready();self.add('cash_flow','C-2',dict(canonical=dict(flow_id='C-2',flow_type='COLLECTION',amount='10000',currency='EUR',due_date='2026-12-01',due_date_evidenced=False,source_ref='DOC',evidence_state='NOT_EVIDENCED')))
        state=self.desk.sales_state('one');r=preview(self.path,state,self.data)
        delay=next(a for a in r['alternatives'] if a['kind']=='DEFER')
        self.assertEqual(delay['patch']['due_date'],'2026-12-01')
        self.assertEqual(preview(self.path,state,dict(self.data,**delay['patch']),alternatives=False)['status'],'WITHIN_DECLARED_SCENARIO')
        self.assertEqual(preview(self.path,state,dict(self.data,due_date='2027-01-01'))['status'],'PENDING')

    def test_missing_data_duplicate_candidate_and_stale_context_do_not_claim_capacity(self):
        self.ready()
        for values in [dict(self.data,shipping_mode='PENDING'),dict(self.data,quantity='2',unit_price='250',vat_percent='0',due_date='2026-10-15')]:
            self.assertEqual(preview(self.path,self.state,values)['status'],'PENDING')
        state=deepcopy(self.state);state['sales_financial_context']['cash_flows'][0]['canonical']['amount']=None
        self.assertEqual(preview(self.path,state,self.data)['status'],'PENDING')
        with self.assertRaises(ValueError):self.desk.purchase_cash_preview(dict(self.data,documentary_context_fingerprint='stale'))

    def test_declared_installments_preserved_and_frozen_when_saved(self):
        self.ready();self.data.update(quantity='2',unit_price='100',payment_installments=[dict(component='MERCHANDISE',amount='121',due_date='2026-10-20'),dict(component='MERCHANDISE',amount='121',due_date='2026-11-01')])
        r=self.desk.purchase_cash_preview(self.data)
        self.assertEqual(r['payment_basis'],'DECLARED_INSTALLMENTS');self.assertEqual(len(r['payments']),2)
        saved=self.desk.save(self.data)
        self.assertEqual(saved['cash_orientation_at_save']['analysis_fingerprint'],r['analysis_fingerprint'])
        self.assertEqual(self.desk.state('one')['purchases'][0]['cash_orientation_at_save'],r)
        report=self.desk.review('one',saved['proposal_id'])
        html=self.desk.printable_report('one',saved['proposal_id'],report['review_id'])
        self.assertIn('ESTUDIO DE TESORERÍA AL GUARDAR',html)
