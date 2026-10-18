import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

from eios.company_app import PurchaseDesk


class PurchaseScreenTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / 'company.db'
        with sqlite3.connect(self.path) as c:
            c.executescript('CREATE TABLE documentary_company_snapshot(dataset_id TEXT PRIMARY KEY,company_id TEXT,as_of_date TEXT,manifest_json TEXT); CREATE TABLE documentary_company_record(dataset_id TEXT,kind TEXT,record_id TEXT,record_json TEXT); CREATE TABLE documentary_source(dataset_id TEXT);')
            for dataset in ('one', 'two'):
                c.execute('INSERT INTO documentary_company_snapshot VALUES(?,?,?,?)', (dataset, dataset, '2026-09-30', json.dumps(dict(company=dict(company_id=dataset),as_of_date='2026-09-30'))))
                for kind, data in [('supplier',dict(supplier_id='S')),('article',dict(article_id='A',supplier_id='S',unit_as_documented='palets'))]:
                    c.execute('INSERT INTO documentary_company_record VALUES(?,?,?,?)',(dataset,kind,kind,json.dumps(dict(data=data))))
        self.desk = PurchaseDesk(self.path)
        self.data = dict(dataset_id='one',supplier_id='S',article_id='A',reference='P-001',quantity='2',unit_price='100',vat_percent='21',order_date='2026-10-01',due_date='2026-11-01')

    def tearDown(self):
        self.tmp.cleanup()

    def test_persistence_scope_and_totals(self):
        result = self.desk.save(self.data)
        self.assertEqual(result['total'], '242.00')
        self.assertFalse(result['decision_authority'])
        reopened = PurchaseDesk(self.path)
        self.assertEqual(len(reopened.state('one')['purchases']), 1)
        self.assertEqual(reopened.state('two')['purchases'], [])

    def test_invalid_and_duplicate_do_not_write(self):
        for patch in [dict(quantity='NaN'),dict(quantity='-1'),dict(supplier_id='OTHER'),dict(due_date='2026-01-01'),dict(dataset_id='absent'),dict(vat_percent='101')]:
            with self.assertRaises((ValueError,KeyError)):
                self.desk.save(dict(self.data, **patch))
        self.assertEqual(self.desk.state('one')['purchases'], [])
        self.desk.save(self.data)
        with self.assertRaises(ValueError):
            self.desk.save(self.data)
        self.assertEqual(len(self.desk.state('one')['purchases']), 1)
