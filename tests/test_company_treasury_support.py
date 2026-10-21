import base64
import json
import sqlite3
import unittest

from tests import test_company_finance_quality as fixture


class CompanyTreasurySupportTest(unittest.TestCase):
    tearDown = fixture.CompanyFinanceQualityTest.tearDown
    add = fixture.CompanyFinanceQualityTest.add
    financial_data = fixture.CompanyFinanceQualityTest.financial_data
    prepare = fixture.CompanyFinanceQualityTest.prepare
    activate = fixture.CompanyFinanceQualityTest.activate
    save_quality = fixture.CompanyFinanceQualityTest.save_quality

    def setUp(self):
        fixture.CompanyFinanceQualityTest.setUp(self)
        self.save_quality()
        self.report = self.desk.review('one', self.named['proposal_id'])
        self.support = dict(dataset_id='one', proposal_id=self.named['proposal_id'],
            review_id=self.report['review_id'], revision=0, reviewer='Declarante de tesorería',
            record_ref='TREASURY-SYNTH-001', documentary_company='Empresa sintética',
            available_amount='5000', currency='EUR', economic_date='2026-09-30',
            locator=dict(document_ref='DOC-FIN', page=1, section='Saldo sintético'), acknowledge=True)

    def save_support(self, **patch):
        return self.desk.record_treasury_support(dict(self.support, **patch))

    def test_canonical_support_keeps_bytes_and_all_contextual_controls_pending(self):
        result = self.save_support()
        self.assertEqual(result['status'], 'DECLARATION_BOUND_NOT_VALIDATED')
        self.assertTrue(all(result['technical_comparisons'].values()))
        self.assertEqual(len(result['pending_controls']), 6)
        with sqlite3.connect(self.path) as c:
            payload = json.loads(c.execute('SELECT payload FROM company_treasury_documentary_support').fetchone()[0])
        self.assertEqual(payload['schema_version'], 'FIN-TREASURY-SUPPORT-01/v0.1')
        self.assertEqual(base64.b64decode(payload['documents'][0]['content_base64']), b'Synthetic payment terms')
        self.assertEqual(payload['observations'], [])
        self.assertEqual(payload['preparation_fingerprint'], self.report['finance_quality_preparation']['fingerprint'])
        self.assertEqual(result['quality_evaluation_status'], 'NOT_EXECUTED')
        self.assertFalse(result['decision_authority'])

    def test_discrepancies_are_preserved_without_replacing_the_financial_snapshot(self):
        result = self.save_support(available_amount='4999', currency='USD', economic_date='2026-10-01')
        self.assertTrue(all(value is False for value in result['technical_comparisons'].values()))
        report = self.desk.review('one', self.named['proposal_id'])
        self.assertEqual(report['financial_context']['financial_snapshot']['available_treasury'], '5000')
        self.assertEqual(report['finance_execution']['viability_status'], 'NOT_EVALUATED')
        self.assertEqual(report['finance_execution']['finance_result']['projection']['status'], 'NOT_EVIDENCED')

    def test_explicit_inputs_source_scope_and_revision_are_required(self):
        for patch in [dict(acknowledge=False), dict(reviewer=''), dict(record_ref=''),
                      dict(documentary_company=''), dict(currency='EU'), dict(available_amount='NaN'),
                      dict(available_amount='-1'), dict(available_amount=True), dict(economic_date='30/09/2026'),
                      dict(locator=dict(document_ref='FOREIGN', page=1, section='X')),
                      dict(locator=dict(document_ref='DOC-FIN', page=True, section='X')), dict(dataset_id='two')]:
            with self.subTest(patch=patch):
                with self.assertRaises(ValueError):
                    self.save_support(**patch)
        self.save_support()
        with self.assertRaises(ValueError):
            self.save_support()

    def test_captured_source_survives_deletion_and_zero_is_not_a_default(self):
        with sqlite3.connect(self.path) as c:
            c.execute('DELETE FROM documentary_source')
        result = self.save_support(available_amount='0')
        self.assertEqual(result['declaration']['available_amount'], '0')
        self.assertFalse(result['technical_comparisons']['amount_matches'])

    def test_changed_preparation_and_calendar_anchors_are_rejected(self):
        self.save_quality(revision=1, criteria=[dict(self.quality['criteria'][0], version='v2')])
        with self.assertRaises(ValueError):
            self.save_support()

    def test_append_only_history_and_exact_historical_print(self):
        args = ('one', self.named['proposal_id'], self.report['review_id'])
        old = self.desk.printable_report(*args)
        self.save_support()
        self.assertEqual(self.desk.printable_report(*args), old)
        report = self.desk.review('one', self.named['proposal_id'])
        html = self.desk.printable_report('one', self.named['proposal_id'], report['review_id'])
        self.assertIn('TREASURY-SYNTH-001', html)
        self.assertIn('5.000,00 EUR', html)
        self.save_support(revision=1, record_ref='TREASURY-SYNTH-002')
        with sqlite3.connect(self.path) as c:
            self.assertEqual(c.execute('SELECT count(*) FROM company_treasury_documentary_support').fetchone()[0], 2)
        draft = self.desk.commercial_draft('one', self.named['proposal_id'], report['review_id'])
        self.assertNotIn('TREASURY-SYNTH', draft['body'])

    def test_latest_support_is_marked_previous_when_calendar_changes(self):
        self.save_support()
        self.desk.record_required_calendar(dict(self.calendar, revision=1, declaration_ref='NEW-CALENDAR'))
        current = self.desk.review('one', self.named['proposal_id'])
        self.assertEqual(current['treasury_documentary_support']['status'], 'PREVIOUS_MATERIAL_SUPPORT')

    def test_separate_treasury_source_is_hashed_before_conservation(self):
        with sqlite3.connect(self.path) as c:
            c.execute('INSERT INTO documentary_source VALUES(?,?,?)', ('one', 'DOC-BANK', b'Synthetic bank support'))
        named = self.desk.save(dict(self.named, reference='SEPARATE-SUPPORT', shipping_mode='NONE',
            document_order_ref='P-EXTRA', document_order_version='v1', document_confirmation_ref='C-EXTRA',
            payment_installments=[dict(component='MERCHANDISE', amount='500', due_date='2026-10-15')]))
        report = self.desk.review('one', named['proposal_id'])
        self.desk.declare_payment_association(dict(self.payload, proposal_id=named['proposal_id'], review_id=report['review_id']))
        report = self.desk.review('one', named['proposal_id'])
        installments = [dict(self.calendar['installments'][0],
            installment_ref=named['payment_plan']['installments'][0]['canonical_candidate']['flow_id'])]
        self.desk.record_required_calendar(dict(self.calendar, proposal_id=named['proposal_id'],
            review_id=report['review_id'], installments=installments))
        report = self.desk.review('one', named['proposal_id'])
        self.desk.prepare_finance_quality(dict(self.quality, proposal_id=named['proposal_id'], review_id=report['review_id']))
        report = self.desk.review('one', named['proposal_id'])
        data = dict(self.support, proposal_id=named['proposal_id'], review_id=report['review_id'],
                    locator=dict(document_ref='DOC-BANK', page=1, section='Saldo'))
        with sqlite3.connect(self.path) as c:
            c.execute("UPDATE documentary_source SET content=? WHERE document_ref='DOC-BANK'", (b'changed',))
        with self.assertRaisesRegex(ValueError, 'ha cambiado'):
            self.desk.record_treasury_support(data)
        with sqlite3.connect(self.path) as c:
            c.execute("UPDATE documentary_source SET content=? WHERE document_ref='DOC-BANK'", (b'Synthetic bank support',))
        result = self.desk.record_treasury_support(data)
        self.assertEqual(result['documents'][0]['document_ref'], 'DOC-BANK')
