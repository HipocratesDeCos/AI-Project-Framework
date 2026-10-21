import json
import sqlite3
import unittest
from tests import test_company_quality_designation as fixture
from eios.core.documentary_reviewer_designation import CONDITIONS
from eios.company_finance_quality import rebuild_quality_preparation


class DesignationObservationTest(unittest.TestCase):
    tearDown = fixture.QualityDesignationTest.tearDown
    add = fixture.QualityDesignationTest.add
    financial_data = fixture.QualityDesignationTest.financial_data
    prepare = fixture.QualityDesignationTest.prepare
    activate = fixture.QualityDesignationTest.activate
    save = fixture.QualityDesignationTest.save
    quality_save = fixture.QualityDesignationTest.quality_save

    def setUp(self):
        fixture.QualityDesignationTest.setUp(self)
        self.observation = dict(condition='PERSON_CORRESPONDENCE', outcome='DECLARED_CONSISTENT',
            note='Resultado local sintético, sin autenticación.', locators=self.designation['declarations'][0]['locators'])
        self.input = dict(self.designation, review_id=self.report['review_id'], revision=1,
            observation=self.observation)

    def observe(self, **patch):
        return self.desk.record_designation_observation(dict(self.input, **patch))

    def test_preserves_original_material_and_undeclared_conditions(self):
        result = self.observe()
        self.assertEqual(len(result['pending_controls']), 6)
        self.assertEqual(result['observations'][0]['outcome'], 'DECLARED_CONSISTENT')
        with sqlite3.connect(self.path) as c:
            rows = c.execute('SELECT payload FROM company_reviewer_designation ORDER BY revision').fetchall()
        before, after = [json.loads(r[0]) for r in rows]
        for key in ('review','review_fingerprint','documents','declarations','reviewer_ref','company_scope'):
            self.assertEqual(before[key], after[key])
        self.assertEqual(result['identity_status'], 'NOT_AUTHENTICATED')
        self.assertEqual(result['authority_status'], 'NOT_VERIFIED')

    def test_positive_requires_support_and_foreign_documents_are_rejected(self):
        for patch in [dict(locators=[]), dict(locators=[dict(document_ref='FOREIGN', page=1, section='Other')]),
                      dict(note=''), dict(condition='AUTO_APPROVED')]:
            with self.subTest(patch=patch), self.assertRaises(ValueError):
                self.observe(observation=dict(self.observation, **patch))
        result = self.observe(observation=dict(self.observation, outcome='NOT_ESTABLISHED', locators=[]))
        self.assertEqual(result['observations'][0]['outcome'], 'NOT_ESTABLISHED')
        self.assertFalse(result['decision_authority'])
        with self.assertRaises(ValueError):
            self.observe(revision=2, acknowledge=False)

    def test_correction_replaces_only_one_condition_and_keeps_history(self):
        self.observe()
        with self.assertRaises(ValueError):
            self.observe()
        report = self.desk.review('one', self.named['proposal_id'])
        self.observe(revision=2, review_id=report['review_id'], observation=dict(self.observation, outcome='DECLARED_INCONSISTENT'))
        report = self.desk.review('one', self.named['proposal_id'])
        result = self.observe(revision=3, review_id=report['review_id'], observation=dict(self.observation, condition='VALIDITY'))
        self.assertEqual(len(result['observations']), 2)
        self.assertEqual(result['observations'][0]['outcome'], 'DECLARED_INCONSISTENT')
        with sqlite3.connect(self.path) as c:
            self.assertEqual(c.execute('SELECT count(*) FROM company_reviewer_designation').fetchone()[0], 4)

    def test_changed_human_review_and_stale_designation_anchors_rejected(self):
        self.observe()
        with self.assertRaisesRegex(ValueError, 'designación ha cambiado'):
            self.observe(revision=2)
        self.desk.record_payment_documentary_review(dict(self.human_args, revision=1))
        current = self.desk.review('one', self.named['proposal_id'])
        with self.assertRaises(ValueError):
            self.observe(revision=2, review_id=current['review_id'])

    def test_updated_designation_requires_new_preparation_and_rebuilds_exactly(self):
        self.quality_save()
        old = self.desk.review('one', self.named['proposal_id'])
        self.observe()
        current = self.desk.review('one', self.named['proposal_id'])
        self.assertEqual(current['finance_quality_preparation']['status'], 'PREVIOUS_MATERIAL_PREPARATION')
        with sqlite3.connect(self.path) as c, self.assertRaises(ValueError):
            rebuild_quality_preparation(c, self.path, old)
        result = self.quality_save(revision=1, review_id=current['review_id'])
        current = self.desk.review('one', self.named['proposal_id'])
        with sqlite3.connect(self.path) as c:
            rebuilt = rebuild_quality_preparation(c, self.path, current)
        self.assertEqual(result['fingerprint'], rebuilt.fingerprint)
        self.assertEqual(len(rebuilt.to_payload()['designation']['observations']), 1)

    def test_all_conditions_annotated_do_not_authorize_or_evaluate_purchase(self):
        for index, condition in enumerate(CONDITIONS):
            report = self.desk.review('one', self.named['proposal_id'])
            result = self.observe(revision=index+1, review_id=report['review_id'],
                observation=dict(self.observation, condition=condition))
        self.assertEqual(result['pending_controls'], [])
        self.assertEqual(result['authority_status'], 'NOT_VERIFIED')
        report = self.desk.review('one', self.named['proposal_id'])
        self.assertEqual(report['finance_execution']['viability_status'], 'NOT_EVALUATED')
        self.assertTrue(all(f['canonical']['evidence_state']=='NOT_EVIDENCED' for f in report['financial_context']['cash_flows']))

    def test_print_is_frozen_escaped_and_provider_draft_excludes_internal_findings(self):
        args = ('one', self.named['proposal_id'], self.report['review_id'])
        original = self.desk.printable_report(*args)
        self.observe(observation=dict(self.observation, note='<script>private observation</script>'))
        self.assertEqual(original, self.desk.printable_report(*args))
        report = self.desk.review('one', self.named['proposal_id'])
        args = ('one', self.named['proposal_id'], report['review_id'])
        self.assertIn('&lt;script&gt;private observation&lt;/script&gt;', self.desk.printable_report(*args))
        self.assertNotIn('private observation', self.desk.commercial_draft(*args)['body'])
