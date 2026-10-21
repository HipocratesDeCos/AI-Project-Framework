import json
import sqlite3
import unittest

from tests import test_company_treasury_support as fixture


class TreasuryContextTest(unittest.TestCase):
    tearDown = fixture.CompanyTreasurySupportTest.tearDown
    add = fixture.CompanyTreasurySupportTest.add
    financial_data = fixture.CompanyTreasurySupportTest.financial_data
    prepare = fixture.CompanyTreasurySupportTest.prepare
    activate = fixture.CompanyTreasurySupportTest.activate
    save_quality = fixture.CompanyTreasurySupportTest.save_quality
    save_support = fixture.CompanyTreasurySupportTest.save_support

    def setUp(self):
        fixture.CompanyTreasurySupportTest.setUp(self)
        self.save_support()
        self.report = self.desk.review('one', self.named['proposal_id'])
        locator = dict(origin='TREASURY_SUPPORT', document_ref='DOC-FIN', page=1, section='Saldo sintético')
        self.context = dict(dataset_id='one', proposal_id=self.named['proposal_id'], review_id=self.report['review_id'],
            revision=0, reviewer='Valorador local', assessment_ref='CONTEXT-SYNTH-001', declaration=dict(
                condition='AVAILABILITY', criterion_reference=self.quality['criteria'][0]['reference'], criterion_version='v1',
                applicability='APPLIES', applicability_reason='Declarada aplicable en este ejemplo sintético.',
                necessity='NECESSARY_FOR_DETERMINED_PROJECTION', necessity_reason='El saldo requiere revisión explícita.',
                impact_reason='Afecta a la interpretación del saldo.', support_assessment='DECLARED_SUFFICIENT',
                support_reason='Suficiencia declarada para la prueba, sin autoridad acreditada.',
                observation_conditions=[], support_locators=[locator]))
        self.observation = dict(condition='AVAILABILITY', outcome='DECLARED_CONSISTENT', note='Comprobación sintética explícita.',
            locators=[dict(document_ref='DOC-FIN', page=1, section='Saldo sintético')])

    def save_context(self, **patch):
        return self.desk.record_treasury_context(dict(self.context, **patch))

    def save_observation(self, **patch):
        data = dict(self.context, revision=1, observation=self.observation)
        data.update(patch)
        return self.desk.record_treasury_observation(data)

    def test_observation_preserves_support_and_leaves_unexamined_conditions_pending(self):
        result = self.save_observation()
        self.assertEqual(len(result['pending_controls']), 5)
        self.assertEqual(result['observations'][0]['outcome'], 'DECLARED_CONSISTENT')
        self.assertEqual(result['declaration']['available_amount'], '5000')
        with sqlite3.connect(self.path) as c:
            self.assertEqual(c.execute('SELECT count(*) FROM company_treasury_documentary_support').fetchone()[0], 2)
        with self.assertRaises(ValueError):
            self.save_observation()

    def test_positive_observation_requires_conserved_support_negative_can_be_unestablished(self):
        for patch in [dict(locators=[]), dict(locators=[dict(document_ref='FOREIGN', page=1, section='X')])]:
            with self.assertRaises(ValueError):
                self.save_observation(observation=dict(self.observation, **patch))
        result = self.save_observation(observation=dict(self.observation, outcome='NOT_ESTABLISHED', locators=[]))
        self.assertEqual(result['observations'][0]['outcome'], 'NOT_ESTABLISHED')
        self.assertEqual(len(result['pending_controls']), 5)

    def test_canonical_context_is_bound_to_actual_criterion_and_exact_material(self):
        result = self.save_context()
        self.assertEqual(result['status'], 'BOUND_DECLARATIONS_ONLY')
        self.assertEqual(len(result['pending_conditions']), 5)
        self.assertEqual(result['quality_evaluation_status'], 'NOT_EXECUTED')
        with sqlite3.connect(self.path) as c:
            payload = json.loads(c.execute('SELECT payload FROM company_treasury_contextual_assessment').fetchone()[0])
        self.assertEqual(payload['schema_version'], 'FIN-TREASURY-CONTEXT-01/v0.1')
        self.assertEqual(payload['preparation_fingerprint'], self.report['finance_quality_preparation']['fingerprint'])
        self.assertEqual(payload['treasury_support_fingerprint'], self.report['treasury_documentary_support']['fingerprint'])
        self.assertEqual(payload['additional_documents'], [])
        self.assertFalse(result['decision_authority'])

    def test_foreign_criterion_support_or_observation_and_inconsistent_applicability_fail(self):
        for patch in [dict(criterion_reference='FOREIGN'), dict(criterion_version='v999'),
                      dict(support_locators=[]), dict(observation_conditions=['AVAILABILITY']),
                      dict(applicability='DOES_NOT_APPLY'), dict(support_reason=''),
                      dict(support_locators=[dict(origin='TREASURY_SUPPORT', document_ref='FOREIGN', page=1, section='X')])]:
            with self.subTest(patch=patch):
                with self.assertRaises(ValueError):
                    self.save_context(declaration=dict(self.context['declaration'], **patch))

    def test_observation_link_is_explicit_and_stale_support_anchor_is_rejected(self):
        self.save_observation()
        with self.assertRaises(ValueError):
            self.save_context()
        report = self.desk.review('one', self.named['proposal_id'])
        result = self.save_context(review_id=report['review_id'], declaration=dict(self.context['declaration'], observation_conditions=['AVAILABILITY']))
        self.assertEqual(result['declarations'][0]['observation_conditions'], ['AVAILABILITY'])

    def test_corrections_keep_history_and_changed_support_does_not_inherit_old_declarations(self):
        self.save_context()
        with self.assertRaises(ValueError):
            self.save_context()
        self.save_context(revision=1, declaration=dict(self.context['declaration'], condition='RESTRICTIONS'))
        self.save_support(revision=1, record_ref='SUPPORT-NEW')
        with self.assertRaises(ValueError):
            self.save_context(revision=2)
        report = self.desk.review('one', self.named['proposal_id'])
        self.assertEqual(report['treasury_contextual_assessment']['status'], 'PREVIOUS_MATERIAL_ASSESSMENT')
        result = self.save_context(revision=2, review_id=report['review_id'])
        self.assertEqual(len(result['declarations']), 1)
        with sqlite3.connect(self.path) as c:
            self.assertEqual(c.execute('SELECT count(*) FROM company_treasury_contextual_assessment').fetchone()[0], 3)

    def test_all_declared_conditions_still_do_not_evaluate_quality_or_viability(self):
        conditions = ('SOURCE_CORRESPONDENCE','ECONOMIC_CUTOFF','AMOUNT_SUPPORT','AVAILABILITY','RESTRICTIONS','SOURCE_SUFFICIENCY')
        for revision, condition in enumerate(conditions):
            result = self.save_context(revision=revision, declaration=dict(self.context['declaration'], condition=condition))
        self.assertEqual(result['pending_conditions'], [])
        report = self.desk.review('one', self.named['proposal_id'])
        self.assertEqual(report['finance_execution']['viability_status'], 'NOT_EVALUATED')
        self.assertTrue(all(f['canonical']['evidence_state']=='NOT_EVIDENCED' for f in report['financial_context']['cash_flows']))

    def test_frozen_report_escaping_and_draft_privacy(self):
        args = ('one', self.named['proposal_id'], self.report['review_id'])
        old = self.desk.printable_report(*args)
        self.save_context(declaration=dict(self.context['declaration'], support_reason='<script>local</script>'))
        self.assertEqual(self.desk.printable_report(*args), old)
        report = self.desk.review('one', self.named['proposal_id'])
        args = ('one', self.named['proposal_id'], report['review_id'])
        html = self.desk.printable_report(*args)
        self.assertIn('VALORACIÓN CONTEXTUAL DECLARADA', html)
        self.assertIn('&lt;script&gt;local&lt;/script&gt;', html)
        self.assertNotIn('<script>local</script>', html)
        self.assertNotIn('CONTEXT-SYNTH', self.desk.commercial_draft(*args)['body'])
