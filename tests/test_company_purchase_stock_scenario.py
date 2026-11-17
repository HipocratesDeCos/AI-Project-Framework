from copy import deepcopy
from decimal import Decimal
import unittest
from eios.company_purchase_stock_scenario import calculate
from tests import test_company_purchase_cash_preview as fixtures

class StockScenarioTest(unittest.TestCase):
    def setUp(self):
        self.state=dict(info=dict(dataset_id='D'),articles=[dict(article_id='A',supplier_id='S',unit_as_documented='unidad')],documentary_context=dict(fingerprint='FP'))
        self.raw=dict(dataset_id='D',article_id='A',unit='unidad',documentary_fingerprint='FP',order_date='2026-10-01',available_at_order='20',daily_demand='2',lead_time_days='3',target_days='10',safety_stock='4',purchase_step='1',receipts=[],actor='Andrés',source_reference='Hipótesis Q1',acknowledge=True)
        self.data=dict(article_id='A',supplier_id='S',order_date='2026-10-01',quantity='50',stock_planning=self.raw)
    def test_quantity_target_dated_receipts_and_immutability(self):
        before=deepcopy(self.raw);r=calculate(self.state,self.data)
        self.assertEqual(Decimal(r['scenario_quantity']),Decimal('10'))
        self.assertEqual(self.raw,before);self.assertFalse(r['decision_authority']);self.assertEqual(r['need_authority'],'NOT_ESTABLISHED')
        self.raw['receipts']=[dict(date='2026-10-04',quantity='7')]
        self.assertEqual(Decimal(calculate(self.state,self.data)['scenario_quantity']),Decimal('3'))
        self.raw['purchase_step']='5'
        self.assertEqual(Decimal(calculate(self.state,self.data)['scenario_quantity']),Decimal('5'))
    def test_late_receipts_do_not_hide_early_need_and_zero_demand(self):
        self.raw.update(available_at_order='1',receipts=[dict(date='2026-10-10',quantity='100')])
        self.assertEqual(calculate(self.state,self.data)['status'],'PRE_DELIVERY_SHORTFALL')
        self.raw.update(available_at_order='20',daily_demand='0',receipts=[])
        self.assertEqual(Decimal(calculate(self.state,self.data)['scenario_quantity']),0)
    def test_invalid_assumptions_and_changed_context_fail_closed(self):
        for key,value in [('acknowledge',False),('documentary_fingerprint','OLD'),('article_id','B'),('unit','cajas'),('daily_demand','NaN'),('daily_demand',True),('target_days','0'),('lead_time_days','366'),('target_days','1.5'),('purchase_step','0'),('actor','')]:
            data=deepcopy(self.data);data['stock_planning'][key]=value
            with self.subTest(key=key,value=value),self.assertRaises(ValueError):calculate(self.state,data)
        self.raw['receipts']=[dict(date='2027-01-01',quantity='10')]
        with self.assertRaises(ValueError):calculate(self.state,self.data)

class StockOpportunityIntegrationTest(unittest.TestCase):
    setUp=fixtures.PurchaseCashPreviewTest.setUp
    tearDown=fixtures.PurchaseCashPreviewTest.tearDown
    ready=fixtures.PurchaseCashPreviewTest.ready
    add=fixtures.PurchaseCashPreviewTest.add
    prepare=fixtures.PurchaseCashPreviewTest.prepare
    activate=fixtures.PurchaseCashPreviewTest.activate
    financial_data=fixtures.PurchaseCashPreviewTest.financial_data
    def hypothesis(self):
        self.ready();self.data.update(quantity='20',unit_price='100')
        self.data['stock_planning']=dict(dataset_id='one',article_id='A',unit='palets',documentary_fingerprint=self.state['documentary_context']['fingerprint'],order_date=self.data['order_date'],available_at_order='10',daily_demand='1',lead_time_days='2',target_days='10',safety_stock='0',purchase_step='1',receipts=[],actor='Andrés',source_reference='Hipótesis Q1',acknowledge=True)
    def test_stock_alternative_replays_and_is_preserved_on_save(self):
        from eios.company_purchase_cash_preview import preview
        self.hypothesis();r=preview(self.path,self.state,self.data)
        a=next(a for a in r['alternatives'] if a['kind']=='STOCK_TARGET')
        self.assertEqual(Decimal(a['patch']['quantity']),Decimal('2'))
        self.assertEqual(preview(self.path,self.state,dict(self.data,**a['patch']),alternatives=False)['total'],a['total'])
        saved=self.desk.save(self.data)
        self.assertEqual(saved['stock_planning_at_save']['fingerprint'],r['stock_planning']['fingerprint'])
        self.assertEqual(saved['cash_orientation_at_save']['stock_planning'],r['stock_planning'])
        invalid=deepcopy(self.data);invalid['reference']='BAD';invalid['stock_planning']['acknowledge']=False
        with self.assertRaises(ValueError):self.desk.save(invalid)
    def test_no_unsafe_quantity_alternative_when_pre_delivery_gap(self):
        from eios.company_purchase_cash_preview import preview
        self.hypothesis();self.data['stock_planning'].update(available_at_order='0',lead_time_days='3')
        r=preview(self.path,self.state,self.data)
        self.assertEqual(r['stock_planning']['status'],'PRE_DELIVERY_SHORTFALL')
        self.assertFalse(any(a['kind']=='STOCK_TARGET' for a in r['alternatives']))

    def test_cash_only_quantity_cut_cannot_undercut_declared_stock_target(self):
        from eios.company_purchase_cash_preview import preview
        self.hypothesis();self.data.update(quantity='100')
        self.data['stock_planning'].update(available_at_order='0',lead_time_days='0',target_days='40')
        r=preview(self.path,self.state,self.data)
        self.assertEqual(r['status'],'SHORTFALL')
        self.assertFalse(any(a['kind']=='QUANTITY' for a in r['alternatives']))
