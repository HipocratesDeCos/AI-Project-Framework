from copy import deepcopy
import unittest
from decimal import Decimal

from eios.company_purchase_stock_scenario import calculate
from eios.company_purchase_need_explanation import explain
from tests.test_company_purchase_stock_scenario import StockScenarioTest
from tests.test_company_exclusive_workbook import ExclusiveWorkbookTest
from tests.test_company_workbook_stock_activation import planned_book
from eios.company_exclusive_workbook import activate


class NeedExplanationTest(unittest.TestCase):
    def test_reference_example_and_no_mutation(self):
        x=StockScenarioTest();x.setUp()
        x.raw.update(order_date='2026-11-04',available_at_order='60',daily_demand='5',lead_time_days='7',target_days='30',safety_stock='20',purchase_step='10',receipts=[dict(date='2026-11-18',quantity='50')])
        x.data.update(order_date='2026-11-04',quantity='400')
        r=calculate(x.state,x.data);before=deepcopy(r);e=explain(r)
        self.assertEqual(e['horizon_days'],37);self.assertEqual(e['period_consumption'],'185')
        self.assertEqual(e['net_need_at_critical_date'],'95');self.assertEqual(r['scenario_quantity'],'100')
        self.assertEqual(e['calculated']['end_stock'],'25');self.assertEqual(e['current']['end_stock'],'325')
        self.assertEqual(e['excess_quantity'],'300');self.assertEqual(r,before)
        self.assertFalse(e['decision_authority']);self.assertEqual(e['source_fingerprint'],r['fingerprint'])

    def test_late_receipt_cannot_hide_a_larger_intermediate_need(self):
        x=StockScenarioTest();x.setUp();x.raw.update(available_at_order='0',receipts=[dict(date='2026-10-14',quantity='200')])
        r=calculate(x.state,x.data);e=explain(r)
        self.assertTrue(e['timing_matters']);self.assertEqual(e['aggregate_net_need'],'0')
        self.assertGreater(Decimal(e['net_need_at_critical_date']),0)
        self.assertEqual(r['status'],'PRE_DELIVERY_SHORTFALL')
        self.assertGreaterEqual(Decimal(e['calculated']['margin_over_safety']),0)

    def test_same_day_and_zero_demand(self):
        x=StockScenarioTest();x.setUp();x.raw.update(lead_time_days='0',daily_demand='0')
        r=calculate(x.state,x.data);e=explain(r)
        self.assertIsNone(r['minimum_before_delivery']);self.assertEqual(e['period_consumption'],'0')


class NeedPreviewIntegrationTest(unittest.TestCase):
    def test_calculates_without_negotiation_price_or_finance_parameters(self):
        x=ExclusiveWorkbookTest();x.setUp()
        try:
            did=activate(x.path,'one',x.receive(planned_book()))['dataset_id'];state=x.desk.state(did)
            fp=state['documentary_context']['fingerprint'];p=state['planning']['A']['workbook_assumptions']
            raw={k:p[k] for k in ['article_id','unit','available_at_order','daily_demand','lead_time_days','target_days','safety_stock','purchase_step','actor','source_reference']}
            raw.update(dataset_id=did,documentary_fingerprint=fp,order_date='2026-09-30',acknowledge=True,receipts=[{k:v for k,v in r.items() if k!='reference'} for r in p['receipts']])
            data=dict(dataset_id=did,documentary_context_fingerprint=fp,article_id='A',supplier_id='4000001',order_date='2026-09-30',quantity='10',stock_planning=raw)
            result=x.desk.purchase_stock_preview(data)
            self.assertTrue(result['explanation']);self.assertFalse(result['decision_authority'])
            with self.assertRaises(ValueError):x.desk.purchase_stock_preview(dict(data,documentary_context_fingerprint='OLD'))
            raw['acknowledge']=False
            with self.assertRaises(ValueError):x.desk.purchase_stock_preview(data)
        finally:x.tearDown()
