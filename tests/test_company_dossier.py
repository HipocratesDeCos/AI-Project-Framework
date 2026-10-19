import json
import os
import sqlite3
import tempfile
import unittest

from eios.company_dossier import check_dossier


class DossierTest(unittest.TestCase):
    def setUp(self):
        f = tempfile.NamedTemporaryFile(delete=False)
        self.db = f.name
        f.close()
        self.addCleanup(os.unlink, self.db)
        with sqlite3.connect(self.db) as c:
            c.execute('CREATE TABLE received_company_batch (batch_id TEXT, metadata_json TEXT, records_json TEXT)')
        self.ids = []

    def add(self, kind, records, company='ACME', cutoff='2026-09-30'):
        bid = str(len(self.ids)).zfill(64)
        meta = dict(company_id=company, legal_name=company, material_nature='REAL', as_of_date=cutoff, filename=kind+'.csv', sheet='Datos', kind=kind)
        records = [dict(kind=kind, data=d, source_row=i+2) for i, d in enumerate(records)]
        with sqlite3.connect(self.db) as c:
            c.execute('INSERT INTO received_company_batch VALUES(?,?,?)', (bid, json.dumps(meta), json.dumps(records)))
        self.ids.append(bid)
        return bid

    def catalog(self):
        self.add('supplier', [dict(supplier_id='S1', legal_name='Proveedor')])
        self.add('customer', [dict(customer_id='C1', legal_name='Cliente')])
        self.add('article', [dict(article_id='A1', description='Artículo', unit='uds', supplier_id='S1')])

    def sale(self, **changes):
        return dict(dict(invoice_number='V1', issue_date='2026-09-01', customer_id='C1', article_id='A1', quantity='1', unit='uds', net_amount='2', currency='EUR'), **changes)

    def test_consistent_read_only_not_admitted(self):
        self.catalog()
        self.add('sales_line', [self.sale()])
        with open(self.db, 'rb') as f:
            before = f.read()
        result = check_dossier(self.db, self.ids)
        self.assertEqual(result['issue_count'], 0)
        self.assertFalse(result['decision_authority'])
        self.assertEqual(result['admission_status'], 'PENDING')
        self.assertEqual(result['operational_path'], 'FORBIDDEN')
        with open(self.db, 'rb') as f:
            self.assertEqual(f.read(), before)
        self.assertEqual(result['review_id'], check_dossier(self.db, list(reversed(self.ids)))['review_id'])

    def test_all_rows_and_precise_source(self):
        self.catalog()
        self.add('sales_line', [self.sale(invoice_number='V'+str(i)) for i in range(25)] + [self.sale(article_id='MISSING')])
        result = check_dossier(self.db, self.ids)
        issue = result['issues'][0]
        self.assertEqual(issue['code'], 'MISSING_REFERENCE')
        self.assertEqual(issue['source']['row'], 27)
        self.assertEqual(issue['source']['filename'], 'sales_line.csv')
        self.assertEqual(result['record_count'], 29)

    def test_missing_catalog_and_unit_conflict(self):
        self.add('sales_line', [self.sale()])
        self.assertEqual(check_dossier(self.db, self.ids)['issue_count'], 2)
        self.catalog()
        self.add('inventory', [dict(article_id='A1', unit='palets', physical='1')])
        issue = check_dossier(self.db, self.ids)['issues'][0]
        self.assertEqual(issue['code'], 'UNIT_MISMATCH')
        self.assertEqual(issue['related']['filename'], 'article.csv')

    def test_conflicting_catalog_stock_and_invoice(self):
        self.catalog()
        self.add('article', [dict(article_id='A1', description='Otra', unit='uds', supplier_id='S1')])
        self.add('inventory', [dict(article_id='A1', unit='uds', physical='10', minimum_stock='2')])
        self.add('stock_policy', [dict(article_id='A1', unit='uds', minimum_stock='3')])
        self.add('sales_line', [self.sale(), self.sale(currency='USD')])
        codes = {x['code'] for x in check_dossier(self.db, self.ids)['issues']}
        self.assertTrue({'CONFLICTING_ID', 'STOCK_CONFLICT', 'INVOICE_CONFLICT'} <= codes)

    def test_scope_selection_and_context(self):
        first = self.add('document', [])
        report = check_dossier(self.db, [first])
        self.assertEqual(report['issues'][0]['code'], 'OUTSIDE_SCOPE')
        second = self.add('customer', [], company='OTHER')
        for selected in ([], [first, first], ['z'*64], [first, second], 'bad'):
            with self.assertRaises(ValueError):
                check_dossier(self.db, selected)
        third = self.add('customer', [], cutoff='2026-08-31')
        with self.assertRaises(ValueError):
            check_dossier(self.db, [first, third])
        self.assertEqual(check_dossier(self.db, [first])['batch_ids'], [first])
