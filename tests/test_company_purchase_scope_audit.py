from copy import deepcopy
import unittest
from tests import test_company_purchase_screen as fixtures
from eios.company_purchase_draft import prepare


class PurchaseScopeAuditTest(unittest.TestCase):
    tearDown=fixtures.PurchaseScreenTest.tearDown
    def setUp(self):
        fixtures.PurchaseScreenTest.setUp(self)
        self.one=self.desk.save(dict(self.data,reference='MISMA-REFERENCIA'))
        self.two=self.desk.save(dict(self.data,dataset_id='two',reference='MISMA-REFERENCIA'))
    def test_same_article_and_reference_do_not_allow_foreign_review_or_copy(self):
        state=self.desk.state('two');before=deepcopy(state['purchases'])
        with self.assertRaises(ValueError):self.desk.review('two',self.one['proposal_id'])
        with self.assertRaises(ValueError):prepare(self.desk,dict(dataset_id='two',proposal_id=self.one['proposal_id'],documentary_context_fingerprint=state['documentary_context']['fingerprint']))
        self.assertEqual(self.desk.state('two')['purchases'],before)
    def test_cross_company_draft_source_and_preview_are_rejected(self):
        one=self.desk.state('one');two=self.desk.state('two');values=prepare(self.desk,dict(dataset_id='one',proposal_id=self.one['proposal_id'],documentary_context_fingerprint=one['documentary_context']['fingerprint']))['values']
        values.update(dataset_id='two',documentary_context_fingerprint=two['documentary_context']['fingerprint'])
        with self.assertRaises(ValueError):self.desk.save(values)
        with self.assertRaises(ValueError):self.desk.purchase_cash_preview(dict(self.data,dataset_id='two',documentary_context_fingerprint=one['documentary_context']['fingerprint']))
        self.assertEqual(len(self.desk.state('one')['purchases']),1);self.assertEqual(len(self.desk.state('two')['purchases']),1)
    def test_saved_review_ids_do_not_cross_company_scope(self):
        review=self.desk.review('one',self.one['proposal_id'])
        with self.assertRaises(ValueError):self.desk._saved_review('two',self.one['proposal_id'],review['review_id'])
        with self.assertRaises(ValueError):self.desk._saved_review('two',self.two['proposal_id'],review['review_id'])
