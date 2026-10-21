import json
import sqlite3

from eios.company_app import PurchaseDesk
from tests.test_company_purchase_screen import PurchaseScreenTest


class ProposalContextTest(PurchaseScreenTest):
    def test_saved_binding_survives_reopen_and_scopes_company(self):
        saved = self.desk.save(self.data)
        context = saved['documentary_context_at_save']
        self.assertEqual(context['company_id'], 'one')
        self.assertEqual(context['dataset_id'], 'one')
        self.assertEqual(context['documentary_cutoff'], '2026-09-30')
        self.assertEqual(len(context['records']), 2)
        self.assertFalse(context['decision_authority'])
        self.assertEqual(PurchaseDesk(self.path).state('one')['purchases'][0]['documentary_context_at_save'], context)
        self.assertNotEqual(self.desk.state('two')['documentary_context']['fingerprint'], context['fingerprint'])

    def mutate_article(self):
        with sqlite3.connect(self.path) as c:
            c.execute("UPDATE documentary_company_record SET record_json=? WHERE dataset_id='one' AND kind='article'",
                      (json.dumps(dict(data=dict(article_id='A',supplier_id='S',unit_as_documented='palets',description='Changed'))),))

    def test_changed_records_block_review_and_stale_form(self):
        saved = self.desk.save(self.data)
        fingerprint = saved['documentary_context_at_save']['fingerprint']
        self.mutate_article()
        with self.assertRaisesRegex(ValueError, 'han cambiado'):
            self.desk.review('one', saved['proposal_id'])
        with self.assertRaisesRegex(ValueError, 'ha cambiado'):
            self.desk.save(dict(self.data, reference='NEW', documentary_context_fingerprint=fingerprint))
        self.assertEqual(len(self.desk.state('one')['purchases']), 1)

    def test_source_bytes_and_metadata_participate_in_identity(self):
        with sqlite3.connect(self.path) as c:
            c.execute('ALTER TABLE documentary_source ADD COLUMN document_ref TEXT')
            c.execute('ALTER TABLE documentary_source ADD COLUMN metadata_json TEXT')
            c.execute('ALTER TABLE documentary_source ADD COLUMN content BLOB')
            c.execute('INSERT INTO documentary_source VALUES(?,?,?,?)', ('one','DOC-1',json.dumps(dict(path='invoice.pdf')),b'original'))
        saved = self.desk.save(self.data)
        self.assertEqual(saved['documentary_context_at_save']['sources'][0]['metadata']['path'], 'invoice.pdf')
        with sqlite3.connect(self.path) as c:
            c.execute("UPDATE documentary_source SET content=? WHERE dataset_id='one'", (b'replaced',))
        with self.assertRaisesRegex(ValueError, 'han cambiado'):
            self.desk.review('one', saved['proposal_id'])

    def test_legacy_proposal_not_backfilled(self):
        saved = self.desk.save(self.data)
        saved.pop('documentary_context_at_save')
        with sqlite3.connect(self.path) as c:
            c.execute('UPDATE manual_purchase_proposal SET payload=? WHERE proposal_id=?', (json.dumps(saved),saved['proposal_id']))
        report = self.desk.review('one', saved['proposal_id'])
        self.assertNotIn('documentary_context_at_save', report['proposal'])
        self.assertFalse(report['decision_authority'])
