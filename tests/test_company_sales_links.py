from copy import deepcopy
import json
import sqlite3
import unittest
from tests import test_company_sales_negotiation as fixture
from eios.company_sales_links import save_link


class SalesLinksTest(unittest.TestCase):
    add=fixture.SalesNegotiationTest.add
    financial_data=fixture.SalesNegotiationTest.financial_data
    set_policy=fixture.SalesNegotiationTest.set_policy
    tearDown=fixture.SalesNegotiationTest.tearDown

    def setUp(self):
        fixture.SalesNegotiationTest.setUp(self)
        with sqlite3.connect(self.path) as c:
            raw=c.execute("SELECT record_json FROM documentary_company_record WHERE dataset_id='one' AND record_id='F1#1'").fetchone()[0]
            record=json.loads(raw);record['data']['article_id']=None;record['data']['unit_as_documented']=None
            c.execute("UPDATE documentary_company_record SET record_json=? WHERE dataset_id='one' AND record_id='F1#1'",(json.dumps(record),))
        self.original=deepcopy(record)

    def request(self,**patch):
        return dict(dict(dataset_id='one',context_fingerprint=self.desk.state('one')['documentary_context']['fingerprint'],line_id='F1#1',article_id='A',actor='Responsable sintético',reason='Correspondencia SKU y unidad revisada',acknowledge_unit=True),**patch)

    def context(self):return self.desk.sales_orientation(dict(dataset_id='one',customer_id='C',article_id='A'))

    def test_explicit_link_restores_history_without_rewriting_source_and_can_be_removed(self):
        self.assertEqual(self.context()['sales_history'],[])
        before=self.desk.state('one')['documentary_context']['fingerprint']
        r=save_link(self.path,self.desk.store,self.request())
        self.assertFalse(r['decision_authority'])
        self.assertNotEqual(before,self.desk.state('one')['documentary_context']['fingerprint'])
        context=self.context();self.assertEqual(context['default_unit_price'],'90')
        self.assertEqual(context['default_price_source'],'LAST_CUSTOMER_SALE')
        history=context['sales_history'][0];self.assertEqual(history['manual_link']['origin'],'MANUAL_EXPLICIT_LINK')
        self.assertEqual(history['source_refs'],self.original['source_refs'])
        self.assertEqual(self.desk.store.records('one','sales_invoice_line')[0],self.original)
        save_link(self.path,self.desk.store,self.request(article_id=None))
        self.assertEqual(self.context()['sales_history'],[])
        with sqlite3.connect(self.path) as c:self.assertEqual(c.execute('SELECT COUNT(*) FROM company_sales_line_link').fetchone()[0],2)

    def test_stale_page_unknown_article_missing_ack_or_reason_rejected(self):
        for patch in [dict(context_fingerprint='old'),dict(article_id='missing'),dict(acknowledge_unit=False),dict(reason=''),dict(actor=''),dict(line_id='missing'),dict(dataset_id='two')]:
            with self.subTest(patch=patch),self.assertRaises(ValueError):save_link(self.path,self.desk.store,self.request(**patch))

    def test_changed_source_invalidates_link_and_old_offer_context(self):
        save_link(self.path,self.desk.store,self.request())
        old=self.desk.state('one')['documentary_context']['fingerprint']
        with sqlite3.connect(self.path) as c:
            raw=deepcopy(self.original);raw['data']['net_amount']='200'
            c.execute("UPDATE documentary_company_record SET record_json=? WHERE dataset_id='one' AND record_id='F1#1'",(json.dumps(raw),))
        self.assertEqual(self.context()['sales_history'],[])
        line=self.desk.state('one')['sales']['invoices'][0]['lines'][0]
        self.assertEqual(line['manual_link']['status'],'STALE')
        with self.assertRaises(ValueError):self.desk.sales_offer(dict(self.offer,context_fingerprint=old),persist=False)

    def test_documented_sku_or_unit_cannot_be_overwritten(self):
        for key,value in [('article_id','B'),('unit_as_documented','litros')]:
            with sqlite3.connect(self.path) as c:
                raw=deepcopy(self.original);raw['data'][key]=value
                c.execute("UPDATE documentary_company_record SET record_json=? WHERE dataset_id='one' AND record_id='F1#1'",(json.dumps(raw),))
            with self.assertRaises(ValueError):save_link(self.path,self.desk.store,self.request())

    def test_two_stale_editors_cannot_overwrite_each_other(self):
        request=self.request()
        save_link(self.path,self.desk.store,request)
        with self.assertRaises(ValueError):save_link(self.path,self.desk.store,request)
        with sqlite3.connect(self.path) as c:self.assertEqual(c.execute('SELECT COUNT(*) FROM company_sales_line_link').fetchone()[0],1)

    def test_saved_offer_keeps_manual_origin_and_is_immutable_after_withdrawal(self):
        save_link(self.path,self.desk.store,self.request())
        offer=dict(self.offer,context_fingerprint=self.desk.state('one')['documentary_context']['fingerprint'])
        saved=self.desk.sales_offer(offer)
        self.assertEqual(saved['lines'][0]['orientation']['sales_history'][0]['manual_link']['origin'],'MANUAL_EXPLICIT_LINK')
        save_link(self.path,self.desk.store,self.request(article_id=None))
        self.assertEqual(self.context()['sales_history'],[])
        self.assertEqual(self.desk.state('one')['sales_proposals'][0],saved)
