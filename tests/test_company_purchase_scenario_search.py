from copy import deepcopy
from datetime import date,timedelta
from decimal import Decimal
import unittest
from tests import test_company_purchase_cash_preview as fixtures
from eios.company_purchase_cash_preview import preview
from eios.company_purchase_scenario_search import metric_comparison

class CombinationSearchTest(unittest.TestCase):
    setUp=fixtures.PurchaseCashPreviewTest.setUp
    tearDown=fixtures.PurchaseCashPreviewTest.tearDown
    ready=fixtures.PurchaseCashPreviewTest.ready
    reference=fixtures.PurchaseCashPreviewTest.reference
    add=fixtures.PurchaseCashPreviewTest.add
    prepare=fixtures.PurchaseCashPreviewTest.prepare
    activate=fixtures.PurchaseCashPreviewTest.activate
    financial_data=fixtures.PurchaseCashPreviewTest.financial_data

    def setup_case(self):
        self.ready();self.reference();self.data['quantity']='100';self.state['history']['A'][0]['effective_net_unit_price']='30'
        self.data['stock_planning']=dict(dataset_id='one',article_id='A',unit='palets',documentary_fingerprint=self.state['documentary_context']['fingerprint'],order_date=self.data['order_date'],available_at_order='0',daily_demand='1',lead_time_days='0',target_days='80',safety_stock='0',purchase_step='1',receipts=[],actor='Andrés',source_reference='H-80',acknowledge=True)

    def test_combination_can_succeed_when_price_or_quantity_alone_cannot(self):
        self.setup_case();before=deepcopy(self.state);r=preview(self.path,self.state,self.data)
        self.assertEqual(r['status'],'SHORTFALL')
        self.assertFalse(any(a['kind'] in ('HISTORICAL_PRICE','STOCK_TARGET') for a in r['alternatives']))
        option=next(a for a in r['alternatives'] if a['kind']=='COMBINED')
        self.assertEqual(option['quantity'],'80');self.assertEqual(option['total'],'2904.00')
        self.assertEqual({c['kind'] for c in option['source']['components']},{'HISTORICAL_PRICE','STOCK_TARGET'})
        replay=preview(self.path,self.state,dict(self.data,**option['patch']),alternatives=False)
        self.assertEqual(replay['status'],'WITHIN_DECLARED_SCENARIO')
        self.assertEqual(replay['total'],option['total']);self.assertEqual(before,self.state)
        self.assertEqual(option['supplier_acceptance'],'NOT_CONFIRMED')

    def test_stress_removes_only_the_named_collection_without_modifying_base(self):
        self.ready();self.data.update(quantity='25',unit_price='100');before=deepcopy(self.state)
        r=preview(self.path,self.state,self.data)
        self.assertEqual(r['status'],'WITHIN_DECLARED_SCENARIO')
        self.assertEqual(r['collection_sensitivity']['excluded_collection']['flow_id'],'C-1')
        self.assertEqual(Decimal(r['current_terms']['collection_sensitivity']['deficit']),Decimal('525'))
        self.assertFalse(r['current_terms']['collection_sensitivity']['reserve_respected'])
        self.assertEqual(before,self.state)

    def test_search_is_bounded_deterministic_and_records_rejections(self):
        self.setup_case()
        for i in range(55):
            day=(date(2026,11,2)+timedelta(days=i)).isoformat();identifier='C-FUT-'+str(i)
            self.state['sales_financial_context']['cash_flows'].append(dict(record_id=identifier,canonical=dict(flow_id=identifier,flow_type='COLLECTION',amount='10',currency='EUR',due_date=day)))
        self.state['sales_financial_context']['record_counts']['cash_flow']=len(self.state['sales_financial_context']['cash_flows'])
        r=preview(self.path,self.state,self.data);again=preview(self.path,self.state,self.data)
        self.assertEqual(r['analysis_fingerprint'],again['analysis_fingerprint'])
        self.assertEqual(r['combination_analysis']['evaluated'],64)
        self.assertTrue(r['combination_analysis']['truncated'])
        self.assertTrue(r['combination_analysis']['rejected'])
        self.assertTrue(any(a['kind']=='COMBINED' for a in r['alternatives']))

    def test_metric_comparison_does_not_rank_different_volumes(self):
        current=dict(quantity='10',total='100',minimum_balance='200')
        alternatives=[dict(quantity='10',total='90',minimum_balance='210'),dict(quantity='5',total='40',minimum_balance='250'),dict(quantity='10',total='80',minimum_balance='190')]
        metric_comparison(current,alternatives)
        self.assertEqual(current['metric_comparison']['dominated_by'],['ALT-1'])
        self.assertEqual(alternatives[0]['metric_comparison']['dominated_by'],[])
        self.assertEqual(alternatives[1]['metric_comparison']['dominated_by'],[])
        self.assertEqual(alternatives[2]['metric_comparison']['dominated_by'],[])

    def test_saved_comparison_report_escapes_sources_and_keeps_sensitivity(self):
        from eios.company_proposal_report import _scenario_comparison
        self.setup_case();self.data['stock_planning']['source_reference']='<img src=x onerror=alert(1)>'
        r=preview(self.path,self.state,self.data);html=_scenario_comparison(r)
        self.assertIn('COMBINACIONES Y SENSIBILIDAD CONSERVADAS',html)
        self.assertIn('C-1',html);self.assertIn('2.904,00',html)
        self.assertIn('&lt;img',html);self.assertNotIn('<img src=x',html)
        self.assertEqual(_scenario_comparison({'scenario':{}}),'')
