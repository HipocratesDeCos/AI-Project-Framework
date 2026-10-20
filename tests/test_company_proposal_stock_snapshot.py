import unittest
from tests import test_company_purchase_screen as fixture
from eios.company_stock_minimum import save_minimums

class ProposalStockSnapshotTest(unittest.TestCase):
    setUp=fixture.PurchaseScreenTest.setUp
    tearDown=fixture.PurchaseScreenTest.tearDown
    def minimum(self,value,revision):
        save_minimums(self.path,self.desk.store,dict(dataset_id='one',changes=[dict(article_id='A',unit='palets',value=value,revision=revision)]))
    def test_frozen_minimum_survives_changes_and_reopen(self):
        from eios.company_app import PurchaseDesk
        self.minimum('3',0)
        proposal=self.desk.save(dict(self.data,stock_minimum_revision=1))
        self.minimum('9',1)
        saved=PurchaseDesk(self.path).state('one')['purchases'][0]
        self.assertEqual(saved['stock_context_at_save'],proposal['stock_context_at_save'])
        self.assertEqual(saved['stock_context_at_save']['minimum']['value'],'3')
        self.assertIsNone(saved['stock_context_at_save']['inventory'])
        self.assertEqual(self.desk.state('one')['stock_minimums']['A']['value'],'9')
        report=self.desk.review('one',saved['proposal_id'])
        self.assertEqual(report['proposal']['stock_context_at_save']['minimum']['value'],'3')
        self.assertFalse(report['decision_authority'])
    def test_stale_visible_minimum_blocked_without_write(self):
        self.minimum('3',0)
        with self.assertRaises(ValueError):self.desk.save(dict(self.data,stock_minimum_revision=0))
        self.assertEqual(self.desk.state('one')['purchases'],[])
    def test_absence_is_preserved_without_inventing_inventory(self):
        proposal=self.desk.save(self.data)
        context=proposal['stock_context_at_save']
        self.assertIsNone(context['minimum']['value'])
        self.assertEqual(context['minimum']['status'],'UNKNOWN')
        self.assertIsNone(context['inventory'])
        self.assertFalse(context['decision_authority'])
