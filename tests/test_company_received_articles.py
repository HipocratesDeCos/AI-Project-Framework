import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

from eios.company_received_articles import received_article


class ReceivedArticlesTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db = Path(self.tmp.name) / 'company.db'
        self.ids = []
        with sqlite3.connect(self.db) as c:
            c.execute('CREATE TABLE received_company_batch(batch_id TEXT,metadata_json TEXT,records_json TEXT)')

    def add(self, kind, records, company='A', cutoff='2026-09-30'):
        bid = str(len(self.ids)).zfill(64)
        meta = dict(company_id=company, legal_name='Empresa '+company, material_nature='REAL', as_of_date=cutoff, kind=kind, filename=kind+'.csv', sheet='Datos', preview=[])
        with sqlite3.connect(self.db) as c:
            c.execute('INSERT INTO received_company_batch VALUES(?,?,?)', (bid,json.dumps(meta),json.dumps([dict(kind=kind,data=d,source_row=i+2) for i,d in enumerate(records)])))
        self.ids.append(bid)

    def catalog(self):
        self.add('article', [dict(article_id='0001',description='Sustrato',unit='uds',supplier_id='S1')])
        self.add('supplier', [dict(supplier_id='S1',legal_name='Proveedor')])

    def purchase(self, **changes):
        d = dict(article_id='0001',supplier_id='S1',invoice_number='F1',issue_date='2026-09-30',quantity='4',unit='uds',net_amount='514',currency='EUR')
        d.update(changes)
        return d

    def detail(self):
        return received_article(self.db,self.ids,'0001')

    def test_latest_per_supplier_unit_currency_exact_net_price_and_source(self):
        self.catalog()
        self.add('purchase_line',[self.purchase(invoice_number='OLD',issue_date='2026-09-01',net_amount='400'),self.purchase()])
        self.add('inventory',[dict(article_id='0001',unit='uds',physical='12',reserved='2',minimum_stock='0')])
        report = self.detail()
        last = report['last_purchases'][0]
        self.assertEqual(last['net_unit_price'],'128.5')
        self.assertEqual(last['quantity'],'4')
        self.assertEqual(last['status'],'DOCUMENTED_LAST_LINE')
        self.assertEqual(last['sources'][0]['row'],3)
        self.assertEqual(last['sources'][0]['filename'],'purchase_line.csv')
        self.assertEqual(report['stock']['available'],'10')
        self.assertEqual(report['inventory'][0]['data']['minimum_stock'],'0')

    def test_same_day_tie_and_duplicate_do_not_choose_or_sum(self):
        self.catalog()
        self.add('purchase_line',[self.purchase(),self.purchase(invoice_number='F2',net_amount='500')])
        last = self.detail()['last_purchases'][0]
        self.assertEqual(last['status'],'AMBIGUOUS_LAST_DATE')
        self.assertIsNone(last['quantity'])
        self.assertIsNone(last['net_unit_price'])
        self.assertEqual(len(last['sources']),2)
        self.add('inventory',[dict(article_id='0001',unit='uds',physical='2',reserved='0')])
        self.add('inventory',[dict(article_id='0001',unit='uds',physical='2',reserved='0')])
        report = self.detail()
        self.assertEqual(report['stock']['status'],'AMBIGUOUS_INVENTORY')
        self.assertIsNone(report['stock']['physical'])
        self.assertEqual(len(report['inventory']),2)

    def test_missing_reservations_and_absent_stock_are_not_zero(self):
        self.catalog()
        self.assertEqual(self.detail()['stock']['status'],'NO_INVENTORY')
        self.add('inventory',[dict(article_id='0001',unit='uds',physical='0',reserved=None)])
        stock = self.detail()['stock']
        self.assertEqual(stock['physical'],'0')
        self.assertIsNone(stock['reserved'])
        self.assertIsNone(stock['available'])
        self.add('sales_line',[dict(self.purchase(),customer_id='C1')])
        # Historical sales do not move an already documented snapshot.
        self.assertEqual(self.detail()['stock']['physical'],'0')

    def test_mismatched_units_and_conflicting_catalog_block_summary(self):
        self.catalog()
        self.add('purchase_line',[self.purchase(unit='palets')])
        self.add('inventory',[dict(article_id='0001',unit='palets',physical='2',reserved='0')])
        report = self.detail()
        self.assertEqual(report['last_purchases'][0]['status'],'UNIT_MISMATCH')
        self.assertIsNone(report['last_purchases'][0]['net_unit_price'])
        self.assertEqual(report['stock']['status'],'UNIT_MISMATCH')
        self.assertIsNone(report['stock']['available'])
        self.add('article',[dict(article_id='0001',description='Otro',unit='uds')])
        self.assertEqual(self.detail()['catalog_status'],'CONFLICTING_CATALOG')
        self.assertEqual(self.detail()['last_purchases'][0]['status'],'CONFLICTING_CATALOG')

    def test_no_catalog_or_supplier_is_explicit(self):
        self.add('purchase_line',[self.purchase()])
        index = received_article(self.db,self.ids)['articles']
        self.assertEqual(index[0]['article_id'],'0001')
        self.assertEqual(index[0]['catalog_status'],'MISSING_CATALOG')
        self.assertIsNone(index[0]['description'])
        self.add('article',[dict(article_id='0001',description='Sustrato',unit='uds')])
        self.assertEqual(self.detail()['last_purchases'][0]['status'],'MISSING_SUPPLIER')

    def test_currencies_and_suppliers_stay_separate(self):
        self.catalog()
        self.add('supplier',[dict(supplier_id='S2',legal_name='Otro')])
        self.add('purchase_line',[self.purchase(),self.purchase(invoice_number='USD',currency='USD'),self.purchase(invoice_number='S2',supplier_id='S2')])
        last = self.detail()['last_purchases']
        self.assertEqual(len(last),3)
        self.assertEqual({(x['supplier_id'],x['currency']) for x in last},{('S1','EUR'),('S1','USD'),('S2','EUR')})
        self.assertTrue(all(x['status']=='DOCUMENTED_LAST_LINE' for x in last))

    def test_conflicting_invoice_header_and_supplier_block_summary(self):
        self.catalog()
        self.add('purchase_line',[self.purchase(),self.purchase(issue_date='2026-09-01')])
        self.assertEqual(self.detail()['last_purchases'][0]['status'],'INVOICE_CONFLICT')
        self.add('supplier',[dict(supplier_id='S1',legal_name='Contradicción')])
        self.assertEqual(self.detail()['last_purchases'][0]['status'],'CONFLICTING_SUPPLIER')

    def test_all_rows_read_only_and_scope_validation(self):
        self.catalog()
        self.add('purchase_line',[self.purchase(invoice_number=str(i),issue_date='2026-09-01') for i in range(25)]+[self.purchase()])
        before = self.db.read_bytes()
        report = self.detail()
        self.assertEqual(len(report['purchases']),26)
        self.assertEqual(report['last_purchases'][0]['sources'][0]['row'],27)
        self.assertEqual(self.db.read_bytes(),before)
        self.assertEqual(report['admission_status'],'PENDING')
        self.assertEqual(report['operational_path'],'FORBIDDEN')
        self.assertFalse(report['decision_authority'])
        for ids,sku in [([],None),(self.ids,'UNKNOWN'),(self.ids,3)]:
            with self.assertRaises(ValueError): received_article(self.db,ids,sku)
        self.add('article',[dict(article_id='0001',description='Otro',unit='uds')],company='B')
        with self.assertRaises(ValueError): self.detail()
