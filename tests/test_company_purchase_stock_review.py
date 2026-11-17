from copy import deepcopy
from decimal import Decimal
import unittest
from eios.company_purchase_stock_review import review_quantity
from eios.company_planning import coverage_for_article
from tests.test_company_planning import PlanningTest


class PurchaseStockReviewTest(unittest.TestCase):
    def setUp(self):
        stock,plan=PlanningTest().values();stock['available']='2'
        self.state=dict(info=dict(dataset_id='snapshot',as_of_date='2026-09-30'),articles=[dict(article_id='A',supplier_id='S',unit_as_documented='palets')],inventory={'A':stock},planning={'A':coverage_for_article('C','snapshot',stock,plan)},stock_minimums={'A':dict(value='3',unit='palets',source='MANUAL',revision=1)})
        self.data=dict(article_id='A',supplier_id='S',quantity='10',order_date='2026-10-01')

    def test_reuses_existing_coverage_and_preserves_need_boundary(self):
        before=deepcopy(self.state);r=review_quantity(self.state,self.data)
        self.assertEqual(Decimal(r['coverage']['coverage_days']),Decimal('20'))
        self.assertEqual(r['coverage']['engine'],'eios.stock.engine.calculate_coverage')
        self.assertEqual(r['inventory']['available'],'2')
        self.assertTrue(r['coverage']['covers_lead_time_at_inventory'])
        self.assertEqual(r['minimum']['gap_at_inventory'],'1')
        self.assertEqual(r['quantity_assessment'],'NOT_DETERMINED')
        self.assertEqual(before,self.state)
        self.assertFalse(r['decision_authority']);self.assertEqual(r['operational_path'],'FORBIDDEN')
        self.assertIn('INVENTORY_MOVEMENTS',{m['code'] for m in r['missing']})
        self.assertIn('PURCHASE_TARGET',{m['code'] for m in r['missing']})
        self.assertNotIn('recommended_quantity',r)

    def test_expired_or_different_unit_forecast_is_not_reused(self):
        for patch in [dict(valid_to='2026-09-30'),dict(unit='cajas'),dict(as_of_date='2026-09-29'),dict(engine='OTHER')]:
            state=deepcopy(self.state);state['planning']['A'].update(patch);r=review_quantity(state,self.data)
            self.assertIsNone(r['coverage']);self.assertIn('DEMAND',{m['code'] for m in r['missing']})

    def test_invalid_inventory_missing_and_automatic_minimum_are_explicit(self):
        for patch in [dict(unit='cajas'),dict(available='5'),dict(physical='NaN'),dict(as_of_date='2026-11-01'),dict(dataset_id='OTHER')]:
            state=deepcopy(self.state);state['inventory']['A'].update(patch);self.assertIsNone(review_quantity(state,self.data)['inventory'])
        state=deepcopy(self.state);state['stock_minimums']['A']['source']='AUTOMATIC';r=review_quantity(state,self.data)
        self.assertIn('AUTOMATIC_MINIMUM',{m['code'] for m in r['missing']})
        state['planning']={};r=review_quantity(state,self.data)
        self.assertEqual({m['code'] for m in r['missing']} & {'DEMAND','DELIVERY'},{'DEMAND','DELIVERY'})
        state['selected_inventory']={'status':'STALE'};self.assertIsNone(review_quantity(state,self.data)['inventory'])

    def test_zero_demand_is_not_a_recommendation_and_zero_stock_is_known(self):
        stock,plan=PlanningTest().values(physical=0,reserved=0,demand='0');stock['available']='0'
        self.state['inventory']['A']=stock;self.state['planning']['A']=coverage_for_article('C','snapshot',stock,plan)
        r=review_quantity(self.state,self.data)
        self.assertEqual(r['coverage']['status'],'UNBOUNDED');self.assertEqual(r['inventory']['available'],'0')
        self.assertIn('ZERO_DEMAND',{m['code'] for m in r['missing']})

    def test_short_coverage_compares_delivery_without_inventing_quantity(self):
        stock,plan=PlanningTest().values(physical=1,reserved=0,demand='1');stock['available']='1'
        self.state['inventory']['A']=stock;self.state['planning']['A']=coverage_for_article('C','snapshot',stock,plan)
        self.assertFalse(review_quantity(self.state,self.data)['coverage']['covers_lead_time_at_inventory'])
