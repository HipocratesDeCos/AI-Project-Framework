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

    def test_chart_points_reconcile_to_scenario_and_documentary_dates(self):
        self.ready()
        result = self.desk.purchase_cash_preview(self.data)
        points = result['scenario']['points']
        self.assertEqual(points[0], dict(date=result['cutoff'], balance=result['opening_balance']))
        self.assertEqual(points[-1]['date'], result['horizon_end'])
        self.assertEqual(points[-1]['balance'], result['scenario']['closing_balance'])
        self.assertEqual(min(Decimal(p['balance']) for p in points), Decimal(result['scenario']['minimum_balance']))
        self.assertEqual([p['date'] for p in points], sorted(p['date'] for p in points))
        self.assertIn('2026-11-01', [p['date'] for p in points])

    def reference(self,**patch):
        self.data.update(quantity='2',unit_price='100')
        self.state['history']['A']=[dict(issue_date='2026-09-20',comparable=True,unit='palets',currency='EUR',effective_net_unit_price='80',invoice_number='H-80',source_refs=[dict(document_ref='H-DOC')],**patch)]

    def test_price_opportunity_without_deficit_is_source_bound_and_replayable(self):
        self.ready();self.reference()
        before=deepcopy(self.state)
        result=preview(self.path,self.state,self.data)
        self.assertEqual(result['status'],'WITHIN_DECLARED_SCENARIO')
        option=next(a for a in result['alternatives'] if a['kind']=='HISTORICAL_PRICE')
        self.assertEqual(Decimal(option['savings']),Decimal('48.40'))
        self.assertEqual(option['source']['invoice_number'],'H-80')
        self.assertEqual(option['origin'],'HYPOTHETICAL')
        self.assertEqual(option['supplier_acceptance'],'NOT_CONFIRMED')
        replay=preview(self.path,self.state,dict(self.data,**option['patch']),alternatives=False)
        self.assertEqual(replay['total'],option['total'])
        self.assertEqual(replay['scenario']['minimum_balance'],option['minimum_balance'])
        self.assertEqual(before,self.state)
        self.assertFalse(option['decision_authority'])

    def test_reference_does_not_reapply_discount_and_reallocates_declared_installments(self):
        self.ready();self.reference();self.data.update(payment_installments=[dict(component='MERCHANDISE',amount='121',due_date='2026-10-20'),dict(component='MERCHANDISE',amount='121',due_date='2026-11-01')])
        result=preview(self.path,self.state,self.data)
        option=next(a for a in result['alternatives'] if a['kind']=='HISTORICAL_PRICE')
        self.assertEqual(option['patch']['discount_mode'],'NONE')
        rows=option['patch']['payment_installments']
        self.assertEqual([r['due_date'] for r in rows],['2026-10-20','2026-11-01'])
        self.assertEqual(sum(Decimal(r['amount']) for r in rows),Decimal('193.60'))
        self.assertEqual(preview(self.path,self.state,dict(self.data,**option['patch']),alternatives=False)['total'],'193.60')

    def test_reference_ambiguity_unit_currency_and_future_are_not_opportunities(self):
        self.ready();self.reference()
        for patch in [dict(comparable=False),dict(unit='cajas'),dict(currency='USD'),dict(issue_date='2027-01-01')]:
            state=deepcopy(self.state);state['history']['A'][0].update(patch)
            self.assertFalse(any(a['kind']=='HISTORICAL_PRICE' for a in preview(self.path,state,self.data)['alternatives']))
        state=deepcopy(self.state);state['history']['A']*=2
        self.assertFalse(any(a['kind']=='HISTORICAL_PRICE' for a in preview(self.path,state,self.data)['alternatives']))
        state=deepcopy(self.state);state['selected_purchase_history']={'status':'STALE'}
        self.assertFalse(any(a['kind']=='HISTORICAL_PRICE' for a in preview(self.path,state,self.data)['alternatives']))

    def test_collection_based_deferral_improves_liquidity_without_deficit(self):
        self.ready();self.data.update(quantity='20',unit_price='100')
        self.add('cash_flow','C-LATE',dict(canonical=dict(flow_id='C-LATE',flow_type='COLLECTION',amount='1000',currency='EUR',due_date='2026-12-01',due_date_evidenced=False,source_ref='DOC',evidence_state='NOT_EVIDENCED')))
        state=self.desk.sales_state('one');result=preview(self.path,state,self.data)
        option=next(a for a in result['alternatives'] if a['kind']=='COLLECTION_ALIGNED_PAYMENT')
        self.assertGreater(Decimal(option['minimum_balance_improvement']),0)
        self.assertEqual(Decimal(option['savings']),0)
        self.assertEqual(option['source']['flow_ids'],['C-LATE'])
        self.assertEqual(preview(self.path,state,dict(self.data,**option['patch']),alternatives=False)['status'],'WITHIN_DECLARED_SCENARIO')

    def test_stock_review_remains_available_when_financial_parameters_are_missing(self):
        self.financial_data();self.data.update(shipping_mode='NONE')
        r=preview(self.path,self.desk.sales_state('one'),self.data)
        self.assertEqual(r['status'],'PENDING')
        self.assertIn('quantity_review',r)
        self.assertEqual(r['quantity_review']['quantity_assessment'],'NOT_DETERMINED')

    def test_comparison_metadata_matches_replayed_server_calculations(self):
        self.ready();self.reference();r=preview(self.path,self.state,self.data)
        self.assertEqual(r['current_terms']['quantity'],'2')
        self.assertEqual(r['current_terms']['total'],r['total'])
        for a in r['alternatives']:
            replay=preview(self.path,self.state,dict(self.data,**a['patch']),alternatives=False)
            self.assertEqual(a['total'],replay['current_terms']['total'])
            self.assertEqual(a['quantity'],replay['current_terms']['quantity'])
            self.assertEqual(a['net_unit_price'],replay['current_terms']['net_unit_price'])
            self.assertEqual(a['minimum_date'],replay['scenario']['minimum_date'])
            self.assertEqual(a['payments'],replay['payments'])
