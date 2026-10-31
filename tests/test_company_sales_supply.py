from copy import deepcopy
import unittest
from tests import test_company_sales_proposals as fixture
from eios.company_sales_supply import assess
from eios.company_sales_proposals import save_offer,printable_offer


class SupplyTest(unittest.TestCase):
    setUp=fixture.SalesOfferTest.setUp
    tearDown=fixture.SalesOfferTest.tearDown

    def test_unknown_is_not_zero_and_reserved_is_not_available(self):
        self.assertEqual(assess(None,20,'Unidad')['status'],'UNKNOWN')
        self.assertIsNone(assess(None,20,'Unidad')['available'])
        inv=dict(unit='Unidad',physical=20,reserved=20,available=0)
        self.assertEqual(assess(inv,1,'Unidad')['status'],'NONE')
        inv['available']=None
        self.assertEqual(assess(inv,1,'Unidad')['status'],'UNKNOWN')
        inv['available']=20
        self.assertEqual(assess(inv,1,'palets')['status'],'UNKNOWN')
        self.assertFalse(assess(inv,20,'Unidad')['conditional'])

    def test_duplicate_sku_is_aggregated_and_condition_is_frozen_in_print(self):
        state=self.desk.sales_state('one');before=deepcopy(state)
        data=dict(self.offer,lines=self.offer['lines']*2)
        result=save_offer(self.path,state,data)
        item=result['supply']['items'][0]
        self.assertEqual(item['status'],'SHORT');self.assertEqual(item['requested'],'4')
        self.assertEqual(item['shortage'],'2');self.assertTrue(result['supply']['conditional'])
        self.assertEqual(item['procurement_request']['status'],'DRAFT_NOT_SENT')
        self.assertIn('PV-001 / A',item['procurement_request']['reference'])
        html=printable_offer(self.path,'one',result['proposal_id'])
        self.assertIn('PRECIO Y ENTREGA PENDIENTES',html)
        self.assertEqual(state,before)
        self.assertEqual(self.desk.state('one')['purchases'],[])
        self.assertFalse(result['decision_authority'])

    def test_missing_available_does_not_crash_or_claim_supply(self):
        state=self.desk.sales_state('one');state['inventory']['A']['available']=None
        result=save_offer(self.path,state,self.offer,persist=False)
        self.assertEqual(result['supply']['items'][0]['status'],'UNKNOWN')
        self.assertTrue(result['warnings'])

    def test_sufficient_inventory_does_not_require_procurement(self):
        result=self.desk.sales_offer(self.offer,persist=False)
        self.assertFalse(result['supply']['conditional'])
        self.assertNotIn('procurement_request',result['supply']['items'][0])
