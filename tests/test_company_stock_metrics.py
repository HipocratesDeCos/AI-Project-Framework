import json
import sqlite3
import unittest
from tests import test_company_purchase_screen as fixture
from eios.company_stock_metrics import stock_metrics

class StockMetricsTest(unittest.TestCase):
    setUp=fixture.PurchaseScreenTest.setUp
    tearDown=fixture.PurchaseScreenTest.tearDown
    def record(self,kind,key,data):
        with sqlite3.connect(self.path) as c:c.execute('INSERT INTO documentary_company_record VALUES(?,?,?,?)',('one',kind,key,json.dumps(dict(record_id=key,data=data,source_refs=[dict(document_ref=key)]))))
    def metrics(self):return stock_metrics(self.desk.store,'one','2026-09-30')['A']
    def purchase(self,supplier='S2',when='2026-09-30',unit='palets',header_supplier=None):
        self.record('supplier',supplier,dict(supplier_id=supplier,legal_name='Proveedor '+supplier))
        self.record('purchase_invoice','INV',dict(supplier_id=header_supplier or supplier,issue_date=when))
        self.record('purchase_invoice_line','LINE',dict(article_id='A',supplier_id=supplier,invoice_id='INV',unit_as_documented=unit))
    def test_catalog_and_additional_documented_supplier(self):
        self.purchase()
        rows=self.metrics()['suppliers']
        self.assertEqual([r['supplier_id'] for r in rows],['S','S2'])
        self.assertEqual(rows[1]['name'],'Proveedor S2')
        self.assertEqual(rows[1]['source_refs'],[dict(document_ref='LINE')])
    def test_future_purchase_excluded(self):
        self.purchase(when='2026-10-01')
        self.assertEqual(len(self.metrics()['suppliers']),1)
    def test_wrong_unit_excluded(self):
        self.purchase(unit='uds')
        self.assertEqual(len(self.metrics()['suppliers']),1)
    def test_inconsistent_supplier_excluded(self):
        self.purchase(header_supplier='OTHER')
        self.assertEqual(len(self.metrics()['suppliers']),1)
    def test_rotation_not_inferred_from_current_stock(self):
        rotation=self.metrics()['rotation']
        self.assertIsNone(rotation['value'])
        self.assertEqual(rotation['status'],'MISSING_DATA')
        self.assertEqual(stock_metrics(self.desk.store,'two','2026-09-30')['A']['suppliers'][0]['supplier_id'],'S')
