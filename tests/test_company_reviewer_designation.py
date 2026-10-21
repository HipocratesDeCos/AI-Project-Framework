import json
import sqlite3
import unittest
from tests import test_company_finance_quality as fixture


class ReviewerDesignationTest(unittest.TestCase):
    tearDown = fixture.CompanyFinanceQualityTest.tearDown
    add = fixture.CompanyFinanceQualityTest.add
    financial_data = fixture.CompanyFinanceQualityTest.financial_data
    prepare = fixture.CompanyFinanceQualityTest.prepare
    activate = fixture.CompanyFinanceQualityTest.activate

    def setUp(self):
        fixture.CompanyFinanceQualityTest.setUp(self)
        self.finding = dict(condition='OPERATION_CORRESPONDENCE', installment_ref=None,
            outcome='NOT_CONFIRMED', note='Prueba sintética.', locators=[])
        self.human_args = dict(self.quality, reviewer='Revisor local', finding=self.finding)
        self.desk.record_payment_documentary_review(self.human_args)
        self.report = self.desk.review('one', self.named['proposal_id'])
        scope = self.report['finance_execution']['finance_input']['snapshot']['company_scope']
        self.designation = dict(self.quality, review_id=self.report['review_id'],
            link_ref='DESIGN-SYNTH-001', designation_ref='DOC-FIN', designation_kind='SYNTHETIC',
            reviewer_ref='Revisor local', company_scope=scope, acknowledge=True,
            declarations=[dict(field='PERSON', text='Transcripción sintética de prueba.',
                locators=[dict(document_ref='DOC-FIN', page=1, section='Ejemplo sintético')])])

    def save(self, **patch):
        return self.desk.record_reviewer_designation(dict(self.designation, **patch))

    def test_exact_review_bytes_and_pending_authority_preserved(self):
        result = self.save()
        self.assertEqual(result['status'], 'PRESENTED_DECLARATIONS_ONLY')
        self.assertEqual(len(result['pending_controls']), 7)
        self.assertEqual(result['authority_status'], 'NOT_VERIFIED')
        self.assertFalse(result['decision_authority'])
        with sqlite3.connect(self.path) as c:
            payload = json.loads(c.execute('SELECT payload FROM company_reviewer_designation').fetchone()[0])
        self.assertEqual(payload['schema_version'], 'DOC-PAY-DESIG-01/v0.1')
        self.assertEqual(payload['review_fingerprint'], self.report['payment_documentary_review']['fingerprint'])
        self.assertEqual(payload['documents'][0]['document_ref'], 'DOC-FIN')
        self.assertEqual(payload['observations'], [])

    def test_foreign_targets_documents_and_missing_acknowledgment_rejected(self):
        for patch in [dict(reviewer_ref='Other'), dict(company_scope='Other'),
                      dict(designation_ref='FOREIGN'), dict(acknowledge=False), dict(declarations=[]),
                      dict(designation_kind='AUTOMATIC'), dict(revision=True),
                      dict(declarations=[dict(self.designation['declarations'][0], locators=[])])]:
            with self.subTest(patch=patch), self.assertRaises((ValueError, TypeError)):
                self.save(**patch)

    def test_revision_history_and_changed_human_review_reject_stale_anchor(self):
        self.save()
        with self.assertRaises(ValueError):
            self.save()
        self.save(revision=1, link_ref='CORRECTION')
        self.desk.record_payment_documentary_review(dict(self.human_args, revision=1))
        with self.assertRaisesRegex(ValueError, 'ha cambiado'):
            self.save(revision=2)
        report = self.desk.review('one', self.named['proposal_id'])
        self.assertEqual(report['reviewer_designation']['status'], 'PREVIOUS_REVIEW_DESIGNATION')
        self.save(revision=2, review_id=report['review_id'])
        with sqlite3.connect(self.path) as c:
            self.assertEqual(c.execute('SELECT count(*) FROM company_reviewer_designation').fetchone()[0], 3)

    def test_missing_human_review_and_tampered_record_rejected(self):
        with self.assertRaises(ValueError):
            self.save(review_id=self.quality['review_id'])
        self.save()
        with sqlite3.connect(self.path) as c:
            payload = json.loads(c.execute('SELECT payload FROM company_reviewer_designation').fetchone()[0])
            payload['reviewer_ref'] = 'Tampered'
            c.execute('UPDATE company_reviewer_designation SET payload=?', (json.dumps(payload),))
        with self.assertRaisesRegex(ValueError, 'huella'):
            self.desk.review('one', self.named['proposal_id'])

    def test_print_frozen_escaped_and_provider_draft_private(self):
        args = ('one', self.named['proposal_id'], self.report['review_id'])
        original = self.desk.printable_report(*args)
        self.save(declarations=[dict(self.designation['declarations'][0], text='<script>private</script>')])
        self.assertEqual(original, self.desk.printable_report(*args))
        report = self.desk.review('one', self.named['proposal_id'])
        args = ('one', self.named['proposal_id'], report['review_id'])
        self.assertIn('&lt;script&gt;private&lt;/script&gt;', self.desk.printable_report(*args))
        self.assertNotIn('private', self.desk.commercial_draft(*args)['body'])
        self.assertEqual(report['finance_execution']['viability_status'], 'NOT_EVALUATED')
