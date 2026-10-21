import json
import sqlite3
import unittest
from tests import test_company_reviewer_designation as fixture
from eios.company_finance_quality import rebuild_quality_preparation


class QualityDesignationTest(unittest.TestCase):
    tearDown = fixture.ReviewerDesignationTest.tearDown
    add = fixture.ReviewerDesignationTest.add
    financial_data = fixture.ReviewerDesignationTest.financial_data
    prepare = fixture.ReviewerDesignationTest.prepare
    activate = fixture.ReviewerDesignationTest.activate
    save = fixture.ReviewerDesignationTest.save

    def setUp(self):
        fixture.ReviewerDesignationTest.setUp(self)
        self.save()
        self.report = self.desk.review('one', self.named['proposal_id'])
        self.args = dict(self.quality, review_id=self.report['review_id'], include_designation=True)

    def quality_save(self, **patch):
        return self.desk.prepare_finance_quality(dict(self.args, **patch))

    def test_explicit_inclusion_reproduces_exact_canonical_preparation(self):
        result = self.quality_save()
        self.assertEqual(result['designation_status'], 'BOUND_PRESENTED_NOT_VERIFIED')
        self.assertEqual(result['designation_fingerprint'], self.report['reviewer_designation']['fingerprint'])
        report = self.desk.review('one', self.named['proposal_id'])
        with sqlite3.connect(self.path) as c:
            rebuilt = rebuild_quality_preparation(c, self.path, report)
        self.assertEqual(rebuilt.fingerprint, result['fingerprint'])
        payload = rebuilt.to_payload()
        self.assertEqual(payload['designation']['review_fingerprint'], payload['review_fingerprint'])
        self.assertEqual(len(payload['designation']['pending_controls']), 7)
        self.assertEqual(result['quality_evaluation_status'], 'NOT_EXECUTED')
        self.assertFalse(result['decision_authority'])
        self.assertIn('Incluida como material presentado', self.desk.printable_report('one', self.named['proposal_id'], report['review_id']))

    def test_default_does_not_include_or_infer_designation(self):
        args = dict(self.args)
        del args['include_designation']
        result = self.desk.prepare_finance_quality(args)
        self.assertEqual(result['designation_status'], 'NOT_SUPPLIED')
        with sqlite3.connect(self.path) as c:
            payload = json.loads(c.execute('SELECT payload FROM company_finance_quality_preparation').fetchone()[0])
        self.assertIsNone(payload['designation'])
        for value in ['true', 1, None]:
            with self.assertRaises(ValueError):
                self.quality_save(revision=1, include_designation=value)

    def test_corrected_designation_invalidates_selected_material_and_rejects_stale_save(self):
        self.quality_save()
        report = self.desk.review('one', self.named['proposal_id'])
        self.save(revision=1, link_ref='CORRECTED')
        with self.assertRaisesRegex(ValueError, 'designación ha cambiado'):
            self.quality_save(revision=1)
        with sqlite3.connect(self.path) as c, self.assertRaises(ValueError):
            rebuild_quality_preparation(c, self.path, report)
        current = self.desk.review('one', self.named['proposal_id'])
        self.assertEqual(current['finance_quality_preparation']['status'], 'PREVIOUS_MATERIAL_PREPARATION')
        result = self.quality_save(revision=1, review_id=current['review_id'])
        self.assertEqual(result['status'], 'PREPARED_PRESENTED_MATERIAL_ONLY')
        self.assertNotEqual(result['fingerprint'], report['finance_quality_preparation']['fingerprint'])

    def test_missing_or_changed_review_designation_cannot_be_selected(self):
        with self.assertRaises(ValueError):
            self.quality_save(review_id=self.designation['review_id'])
        self.desk.record_payment_documentary_review(dict(self.human_args, revision=1))
        current = self.desk.review('one', self.named['proposal_id'])
        with self.assertRaises(ValueError):
            self.quality_save(review_id=current['review_id'])

    def test_treasury_consumes_bound_preparation_and_becomes_historical_after_designation_changes(self):
        self.quality_save()
        report = self.desk.review('one', self.named['proposal_id'])
        support = dict(dataset_id='one', proposal_id=self.named['proposal_id'], review_id=report['review_id'],
            revision=0, reviewer='Declarante local', record_ref='SUPPORT-BOUND', documentary_company='Empresa sintética',
            available_amount='5000', currency='EUR', economic_date='2026-09-30',
            locator=dict(document_ref='DOC-FIN', page=1, section='Saldo sintético'), acknowledge=True)
        result = self.desk.record_treasury_support(support)
        self.assertEqual(result['status'], 'DECLARATION_BOUND_NOT_VALIDATED')
        self.save(revision=1, link_ref='CORRECTED')
        current = self.desk.review('one', self.named['proposal_id'])
        self.assertEqual(current['treasury_documentary_support']['status'], 'PREVIOUS_MATERIAL_SUPPORT')
        with self.assertRaises(ValueError):
            self.desk.record_treasury_support(dict(support, revision=1))
        self.assertEqual(current['finance_execution']['viability_status'], 'NOT_EVALUATED')

    def test_frozen_print_and_unselected_preparation_remain_unchanged(self):
        self.quality_save(include_designation=False)
        report = self.desk.review('one', self.named['proposal_id'])
        args = ('one', self.named['proposal_id'], report['review_id'])
        before = self.desk.printable_report(*args)
        self.save(revision=1, link_ref='CORRECTED')
        self.assertEqual(before, self.desk.printable_report(*args))
        current = self.desk.review('one', self.named['proposal_id'])
        self.assertEqual(current['finance_quality_preparation']['status'], 'PREPARED_PRESENTED_MATERIAL_ONLY')
        self.assertNotIn('CORRECTED', self.desk.commercial_draft('one', self.named['proposal_id'], current['review_id'])['body'])
