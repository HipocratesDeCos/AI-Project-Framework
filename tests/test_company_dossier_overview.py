import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

from eios.company_dossier_overview import dossier_overviews


class DossierOverviewTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db = Path(self.tmp.name) / 'company.db'
        self.count = 0

    def add(self, kind, records, company='A', cutoff='2026-09-30', nature='REAL', warnings=0):
        self.count += 1
        bid = str(self.count).zfill(64)
        meta = dict(company_id=company, legal_name='Empresa '+company, material_nature=nature, as_of_date=cutoff, kind=kind, warning_count=warnings, preview=records[:20], record_count=999)
        with sqlite3.connect(self.db) as c:
            c.execute('CREATE TABLE IF NOT EXISTS received_company_batch(batch_id TEXT, metadata_json TEXT, records_json TEXT)')
            c.execute('INSERT INTO received_company_batch VALUES(?,?,?)', (bid, json.dumps(meta), json.dumps(records)))
        return bid

    def test_empty_database(self):
        self.assertEqual(dossier_overviews(self.db), [])
        with sqlite3.connect(self.db) as c:
            self.assertEqual(c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall(), [])

    def test_contexts_are_isolated(self):
        self.add('supplier', [dict(data={})])
        self.add('customer', [dict(data={})], company='B')
        self.add('inventory', [dict(data={})], cutoff='2026-08-31')
        self.add('article', [dict(data={})], nature='SYNTHETIC')
        groups = dossier_overviews(self.db)
        self.assertEqual(len(groups), 4)
        self.assertTrue(all(g['file_count'] == g['record_count'] == 1 for g in groups))
        for group in groups:
            self.assertEqual(group['admission_status'], 'PENDING')
            self.assertEqual(group['operational_path'], 'FORBIDDEN')
            self.assertFalse(group['decision_authority'])

    def test_all_stored_rows_not_preview_or_metadata_count(self):
        records = [dict(data=dict(article_id=str(i))) for i in range(25)]
        records.append(dict(data=dict(article_id='LAST', minimum_stock='0', lead_time_days='5')))
        bid = self.add('inventory', records, warnings=3)
        group = dossier_overviews(self.db)[0]
        self.assertEqual(group['record_count'], 26)
        self.assertEqual(group['categories']['inventory']['record_count'], 26)
        self.assertEqual(group['categories']['inventory']['batch_ids'], [bid])
        self.assertEqual(group['parameter_rows']['minimum_stock'], 1)
        self.assertEqual(group['parameter_rows']['lead_time_days'], 1)
        self.assertEqual(group['parameter_rows']['safety_stock'], 0)
        self.assertEqual(group['source_warning_count'], 3)

    def test_support_empty_missing_and_multiple_sources_differ(self):
        self.add('document', [])
        self.add('article', [])
        self.add('supplier', [dict(data={})])
        self.add('supplier', [dict(data={})])
        group = dossier_overviews(self.db)[0]
        categories = group['categories']
        self.assertEqual(categories['document']['status'], 'SUPPORT_ONLY')
        self.assertEqual(categories['article']['status'], 'EMPTY_FILE')
        self.assertEqual(categories['customer']['status'], 'NO_FILES')
        self.assertEqual(categories['supplier']['status'], 'RECEIVED_ROWS')
        self.assertEqual(categories['supplier']['file_count'], 2)
        self.assertEqual(categories['supplier']['record_count'], 2)
        self.assertIn('customer', group['missing_categories'])
        self.assertNotIn('document', group['missing_categories'])

    def test_read_only_and_deterministic(self):
        self.add('stock_policy', [dict(data=dict(minimum_stock=None, safety_stock='0'))])
        before = self.db.read_bytes()
        first = dossier_overviews(self.db)
        self.assertEqual(first, dossier_overviews(self.db))
        self.assertEqual(before, self.db.read_bytes())
        self.assertEqual(first[0]['parameter_rows']['safety_stock'], 1)
        self.assertEqual(first[0]['parameter_rows']['minimum_stock'], 0)
