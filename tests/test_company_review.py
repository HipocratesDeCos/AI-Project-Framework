from copy import deepcopy
from decimal import Decimal
import json
import sqlite3
import unittest

from eios.company_review import review_proposal
from tests import test_company_purchase_screen as screen_fixture


class ReviewCalculationTest(unittest.TestCase):
    def setUp(self):
        self.proposal = dict(proposal_id='P',dataset_id='D',reference='REF',article_id='A',
                             unit='uds.',currency='EUR',unit_price='110',order_date='2026-10-01')
        self.info = dict(as_of_date='2026-09-30',company=dict(company_id='C'))
        self.row = dict(issue_date='2026-09-30',invoice_number='F',effective_net_unit_price='100',
                        quantity='5',unit='uds.',currency='EUR',comparable=True,source_refs=[dict(document_ref='DOC-1')])
        self.inventory = dict(dataset_id='D',article_id='A',unit='uds.',as_of_date='2026-09-30',available='20')
        self.plan = dict(status='FINITE',as_of_date='2026-09-30',unit='uds.',valid_to='2026-10-30',coverage_days='20')

    def review(self, history=None):
        return review_proposal(self.proposal,self.info,[self.row] if history is None else history,self.inventory,self.plan)

    def test_exact_comparison_provenance_and_no_authority(self):
        original=deepcopy(self.proposal)
        r=self.review()
        self.assertEqual(Decimal(r['price']['difference_per_unit']),Decimal('10'))
        self.assertEqual(r['price']['difference_percent'],'10.00')
        self.assertEqual(r['price']['reference']['source_refs'],self.row['source_refs'])
        self.assertEqual(r['stock']['inventory']['as_of_date'],'2026-09-30')
        self.assertTrue(r['stock']['forecast_applicable_on_order_date'])
        self.assertEqual(r['status'],'PARTIAL_CONTEXT_REVIEW')
        self.assertFalse(r['decision_authority'])
        self.assertEqual(r['operational_path'],'FORBIDDEN')
        self.assertEqual(self.proposal,original)
        self.assertEqual(self.review()['review_id'],r['review_id'])
        self.proposal['unit_price']='111'
        self.assertNotEqual(self.review()['review_id'],r['review_id'])

    def test_no_arbitrary_choice_and_no_incomparable_reference(self):
        self.assertEqual(self.review([self.row,deepcopy(self.row)])['price']['status'],'UNAVAILABLE')
        self.row['comparable']=False
        self.assertEqual(self.review()['price']['status'],'UNAVAILABLE')
        self.row['comparable']=True
        self.row['unit']='palets'
        self.assertEqual(self.review()['price']['status'],'UNAVAILABLE')

    def test_future_evidence_excluded_and_expired_forecast_flagged(self):
        self.proposal['order_date']='2026-09-29'
        r=self.review()
        self.assertEqual(r['price']['status'],'UNAVAILABLE')
        self.assertEqual(r['stock']['status'],'UNAVAILABLE')
        self.proposal['order_date']='2026-11-01'
        self.assertFalse(self.review()['stock']['forecast_applicable_on_order_date'])
        self.inventory['unit']='palets'
        self.assertEqual(self.review()['stock']['status'],'UNAVAILABLE')


class ReviewPersistenceTest(unittest.TestCase):
    def setUp(self):
        self.fixture=screen_fixture.PurchaseScreenTest()
        self.fixture.setUp()

    def tearDown(self):
        self.fixture.tearDown()

    def test_version_isolation_idempotency_and_original_preserved(self):
        f=self.fixture
        p=f.desk.save(f.data)
        with self.assertRaises(ValueError):
            f.desk.review('two',p['proposal_id'])
        r=f.desk.review('one',p['proposal_id'])
        again=f.desk.review('one',p['proposal_id'])
        self.assertEqual(r,again)
        self.assertEqual(f.desk.state('one')['purchases'],[p])
        with sqlite3.connect(f.path) as c:
            rows=c.execute('SELECT payload FROM manual_purchase_context_review').fetchall()
        self.assertEqual(len(rows),1)
        self.assertEqual(json.loads(rows[0][0])['proposal'],p)
