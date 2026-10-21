import base64
import json
import sqlite3
import unittest

from tests import test_company_required_calendar as fixture


class CompanyFinanceQualityTest(unittest.TestCase):
    tearDown = fixture.RequiredCompanyCalendarTest.tearDown
    add = fixture.RequiredCompanyCalendarTest.add
    financial_data = fixture.RequiredCompanyCalendarTest.financial_data
    prepare = fixture.RequiredCompanyCalendarTest.prepare
    activate = fixture.RequiredCompanyCalendarTest.activate

    def setUp(self):
        fixture.RequiredCompanyCalendarTest.setUp(self)
        self.desk.record_required_calendar(self.calendar)
        self.report = self.desk.review('one', self.named['proposal_id'])
        self.quality = dict(dataset_id='one', proposal_id=self.named['proposal_id'],
            review_id=self.report['review_id'], revision=0, actor='Preparador local', acknowledge=True,
            criteria=[dict(reference='CRITERIO-SYNTH-EXPLICITO', version='v1',
                           content='Texto sintético aportado expresamente. No acredita autoridad.')])

    def save_quality(self, **patch):
        return self.desk.prepare_finance_quality(dict(self.quality, **patch))

    def test_canonical_preparation_preserves_explicit_criteria_without_evaluation(self):
        result = self.save_quality()
        self.assertEqual(result['status'], 'PREPARED_PRESENTED_MATERIAL_ONLY')
        with sqlite3.connect(self.path) as c:
            payload = json.loads(c.execute('SELECT payload FROM company_finance_quality_preparation').fetchone()[0])
        self.assertEqual(payload['schema_version'], 'QTG-FIN-PREP-01/v0.1')
        self.assertEqual(base64.b64decode(payload['presented_criteria'][0]['content_base64']).decode(),
                         self.quality['criteria'][0]['content'])
        self.assertEqual(payload['coverage_fingerprint'], self.report['required_calendar_coverage']['fingerprint'])
        self.assertIsNone(payload['review'])
        self.assertIsNone(payload['designation'])
        self.assertEqual(result['quality_evaluation_status'], 'NOT_EXECUTED')
        self.assertEqual(result['viability_status'], 'NOT_EVALUATED')
        self.assertFalse(result['decision_authority'])
        self.assertTrue(all(f['evidence_state'] == 'NOT_EVIDENCED'
                            for f in payload['capture']['finance_package']['finance_input']['cash_flows']))

    def test_missing_criteria_acknowledgment_scope_and_duplicate_criteria_fail(self):
        for patch in [dict(criteria=[]), dict(acknowledge=False), dict(actor=''), dict(dataset_id='two'),
                      dict(criteria=[dict(reference='R', version='v1', content='')]),
                      dict(criteria=self.quality['criteria'] * 2),
                      dict(criteria=[dict(reference='R', version='v1', content='x' * 8001)])]:
            with self.subTest(patch=patch):
                with self.assertRaises(ValueError):
                    self.save_quality(**patch)
        with sqlite3.connect(self.path) as c:
            self.assertEqual(c.execute('SELECT count(*) FROM company_finance_quality_preparation').fetchone()[0], 0)

    def test_calendar_changes_reject_stale_anchor_and_mark_previous_material(self):
        self.save_quality()
        self.desk.record_required_calendar(dict(self.calendar, revision=1, declaration_ref='CAL-NEW'))
        with self.assertRaisesRegex(ValueError, 'calendario ha cambiado'):
            self.save_quality(revision=1)
        current = self.desk.review('one', self.named['proposal_id'])
        self.assertEqual(current['finance_quality_preparation']['status'], 'PREVIOUS_MATERIAL_PREPARATION')

    def test_documentary_findings_are_bound_exactly_and_stale_anchor_rejected(self):
        finding = dict(condition='OPERATION_CORRESPONDENCE', installment_ref=None,
                       outcome='CONFIRMED_BY_REVIEW', note='Correspondencia sintética cotejada.',
                       locators=[dict(document_ref='DOC-FIN', page=1, section='Cuota única')])
        human = self.desk.record_payment_documentary_review(dict(self.quality, reviewer='Revisor', finding=finding))
        with self.assertRaisesRegex(ValueError, 'revisión documental ha cambiado'):
            self.save_quality()
        self.report = self.desk.review('one', self.named['proposal_id'])
        result = self.save_quality(review_id=self.report['review_id'])
        self.assertEqual(result['review_fingerprint'], human['fingerprint'])
        with sqlite3.connect(self.path) as c:
            payload = json.loads(c.execute('SELECT payload FROM company_finance_quality_preparation').fetchone()[0])
        self.assertEqual(payload['review']['findings'][0]['note'], finding['note'])
        self.assertIsNone(payload['designation'])

    def test_revision_history_frozen_print_and_commercial_draft_privacy(self):
        args = ('one', self.named['proposal_id'], self.report['review_id'])
        old = self.desk.printable_report(*args)
        self.save_quality()
        self.assertEqual(self.desk.printable_report(*args), old)
        with self.assertRaises(ValueError):
            self.save_quality()
        self.save_quality(revision=1, criteria=[dict(self.quality['criteria'][0], version='v2')])
        current = self.desk.review('one', self.named['proposal_id'])
        args = ('one', self.named['proposal_id'], current['review_id'])
        html = self.desk.printable_report(*args)
        self.assertIn('CRITERIO-SYNTH-EXPLICITO', html)
        self.assertIn('v2', html)
        self.assertNotIn(self.quality['criteria'][0]['content'], html)
        draft = self.desk.commercial_draft(*args)
        self.assertNotIn('CRITERIO-SYNTH-EXPLICITO', draft['body'])
        with sqlite3.connect(self.path) as c:
            self.assertEqual(c.execute('SELECT count(*) FROM company_finance_quality_preparation').fetchone()[0], 2)

    def test_structural_differences_are_conserved_without_becoming_quality_pass(self):
        rows = [dict(self.calendar['installments'][0], due_date='2026-10-16')]
        self.desk.record_required_calendar(dict(self.calendar, revision=1, installments=rows))
        current = self.desk.review('one', self.named['proposal_id'])
        result = self.save_quality(review_id=current['review_id'])
        self.assertEqual(result['quality_evaluation_status'], 'NOT_EXECUTED')
        with sqlite3.connect(self.path) as c:
            payload = json.loads(c.execute('SELECT payload FROM company_finance_quality_preparation').fetchone()[0])
        self.assertFalse(payload['coverage']['required_calendar_matches'])
