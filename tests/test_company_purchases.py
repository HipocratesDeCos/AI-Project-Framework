import json
import sqlite3
import unittest
from tests import test_company_purchase_screen as fixture
from eios.company_purchases import documented_purchases

class DocumentaryPurchasesTest(unittest.TestCase):
    setUp=fixture.PurchaseScreenTest.setUp
    tearDown=fixture.PurchaseScreenTest.tearDown
    def record(self,kind,key,data,dataset='one'):
        with sqlite3.connect(self.path) as c:c.execute('INSERT INTO documentary_company_record VALUES(?,?,?,?)',(dataset,kind,key,json.dumps(dict(record_id=key,data=data,source_refs=[dict(document_ref='DOC-1')]))))
    def invoice(self,**patch):
        data=dict(invoice_id='INV',invoice_number='F-1',supplier_id='S',issue_date='2026-09-30',net_amount='100',vat_amount='21',gross_amount='121',currency='EUR');data.update(patch);self.record('purchase_invoice','INV',data)
    def line(self,**patch):
        data=dict(invoice_id='INV',supplier_id='S',article_id='A',line=1,quantity='2',unit_as_documented='palets',unit_price='50',net_amount='100',currency='EUR');data.update(patch);self.record('purchase_invoice_line','INV#1',data)
    def result(self,dataset='one'):return documented_purchases(self.desk.store,dataset,'2026-09-30')
    def test_invoice_and_source_bound_lines(self):
        self.invoice();self.line();invoice=self.result()['invoices'][0]
        self.assertEqual(invoice['gross_amount'],'121')
        self.assertEqual(invoice['lines'][0]['quantity'],'2')
        self.assertEqual(invoice['lines'][0]['source_refs'],[dict(document_ref='DOC-1')])
        self.assertNotIn('paid',invoice)
        self.assertEqual(self.desk.state('one')['purchases'],[])
    def test_future_excluded(self):
        self.invoice(issue_date='2026-10-01');self.line()
        self.assertEqual(self.result()['invoices'],[])
        self.assertEqual(self.result()['ignored_lines'],1)
    def test_unmatched_supplier_excluded(self):
        self.invoice(supplier_id='OTHER')
        self.assertEqual(len(self.result()['excluded']),1)
    def test_identity_mismatch_excluded(self):
        self.invoice(invoice_id='WRONG')
        self.assertEqual(self.result()['invoices'],[])
    def test_line_supplier_mismatch_not_linked(self):
        self.invoice();self.line(supplier_id='OTHER')
        result=self.result();self.assertEqual(result['ignored_lines'],1)
        self.assertEqual(result['invoices'][0]['lines'],[])
        self.assertTrue(result['invoices'][0]['warnings'])
    def test_missing_amount_not_zero_and_dataset_separation(self):
        self.invoice(net_amount=None,vat_amount='NaN');self.line()
        self.assertIsNone(self.result()['invoices'][0]['net_amount'])
        self.assertIsNone(self.result()['invoices'][0]['vat_amount'])
        self.assertEqual(self.result('two')['invoices'],[])
