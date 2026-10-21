import json
import sqlite3
import unittest

from tests import test_company_payment_capture as fixture


class RequiredCompanyCalendarTest(unittest.TestCase):
    tearDown=fixture.CompanyPaymentCaptureTest.tearDown
    add=fixture.CompanyPaymentCaptureTest.add
    financial_data=fixture.CompanyPaymentCaptureTest.financial_data
    prepare=fixture.CompanyPaymentCaptureTest.prepare
    activate=fixture.CompanyPaymentCaptureTest.activate

    def setUp(self):
        fixture.CompanyPaymentCaptureTest.setUp(self)
        self.named=self.desk.save(dict(self.data,reference='NAMED',unit_price='250',vat_percent='0',
            due_date='2026-10-15',shipping_mode='NONE',document_order_ref='PED-SYNTH-001',
            document_order_version='v1',document_confirmation_ref='CONF-SYNTH-001',
            payment_installments=[dict(component='MERCHANDISE',amount='500',due_date='2026-10-15')]))
        initial=self.desk.review('one',self.named['proposal_id'])
        self.desk.declare_payment_association(dict(self.payload,proposal_id=self.named['proposal_id'],review_id=initial['review_id']))
        self.report=self.desk.review('one',self.named['proposal_id'])
        installment=self.named['payment_plan']['installments'][0]
        self.calendar=dict(dataset_id='one',proposal_id=self.named['proposal_id'],review_id=self.report['review_id'],
            revision=0,actor='Declarante local',declaration_ref='CAL-SYNTH-001',authority_ref='Referencia sintética expresamente declarada',
            acknowledge=True,total_due='500',installments=[dict(installment_ref=installment['canonical_candidate']['flow_id'],
                sequence=1,amount='500',currency='EUR',due_date='2026-10-15',
                locators=[dict(document_ref='DOC-FIN',page=1,section='Cuota única')])])

    def save(self,**patch):
        return self.desk.record_required_calendar(dict(self.calendar,**patch))

    def test_explicit_references_are_captured_and_canonical_coverage_matches(self):
        result=self.save()
        self.assertEqual(result['status'],'STRUCTURAL_MATCH')
        self.assertEqual(result['assurance_scope'],'DECLARED_CALENDAR_STRUCTURAL_MATCH_ONLY')
        with sqlite3.connect(self.path) as c:
            payload=json.loads(c.execute('SELECT payload FROM company_required_payment_calendar').fetchone()[0])
        self.assertEqual(payload['schema_version'],'DOC-PAY-COVER-01/v0.1')
        self.assertEqual(payload['capture']['order_ref'],'PED-SYNTH-001')
        self.assertEqual(payload['capture']['order_version'],'v1')
        self.assertEqual(payload['capture']['confirmation_ref'],'CONF-SYNTH-001')
        self.assertTrue(payload['required_calendar_matches'])
        self.assertEqual(payload['observations'][0]['observed_evidence_state'],'NOT_EVIDENCED')
        report=self.desk.review('one',self.named['proposal_id'])
        self.assertEqual(report['version'],'COMPANY-CONTEXT-REVIEW-13')
        self.assertEqual(report['finance_execution']['viability_status'],'NOT_EVALUATED')
        self.assertEqual(len(report['finance_execution']['finance_input']['cash_flows']),2)

    def test_missing_references_are_not_backfilled(self):
        from eios.company_required_calendar import document_references
        self.assertEqual(document_references({}),dict(order_ref=None,order_version=None,confirmation_ref=None))
        with self.assertRaises(ValueError):
            document_references(dict(document_order_ref='PARTIAL'))
        with self.assertRaises(ValueError):
            self.desk.record_required_calendar(dict(self.calendar,proposal_id=self.saved['proposal_id'],
                review_id=self.initial['review_id']))

    def test_explicit_date_difference_is_stored_as_difference_without_rewriting_flow(self):
        rows=[dict(self.calendar['installments'][0],due_date='2026-10-16')]
        result=self.save(installments=rows)
        self.assertEqual(result['status'],'STRUCTURAL_DIFFERENCES')
        self.assertIn('DUE_DATE_MISMATCH',result['observations'][0]['issues'])
        self.assertEqual(result['observations'][0]['observed_evidence_state'],'NOT_EVIDENCED')

    def test_stale_revision_total_support_and_acknowledgment_rejected(self):
        for patch in [dict(acknowledge=False),dict(total_due='499'),dict(authority_ref=''),dict(actor=''),
                      dict(installments=[]),dict(installments=[dict(self.calendar['installments'][0],
                        locators=[dict(document_ref='FOREIGN',page=1,section='X')])])]:
            with self.subTest(patch=patch):
                with self.assertRaises(ValueError):
                    self.save(**patch)
        self.save()
        with self.assertRaises(ValueError):
            self.save()

    def test_simultaneous_maturities_fail_without_changing_original_data(self):
        first=dict(self.calendar['installments'][0],amount='250')
        second=dict(first,installment_ref='DECLARED-SECOND',sequence=2)
        with self.assertRaisesRegex(ValueError,'estrictamente crecientes'):
            self.save(installments=[first,second])
        with sqlite3.connect(self.path) as c:
            self.assertEqual(c.execute('SELECT count(*) FROM company_required_payment_calendar').fetchone()[0],0)

    def test_saved_print_and_calendar_history_remain_frozen(self):
        args=('one',self.named['proposal_id'],self.report['review_id'])
        old=self.desk.printable_report(*args)
        first=self.save()
        self.assertEqual(self.desk.printable_report(*args),old)
        current=self.desk.review('one',self.named['proposal_id'])
        html=self.desk.printable_report('one',self.named['proposal_id'],current['review_id'])
        self.assertIn('Coincidencia estructural',html)
        self.assertIn('CAL-SYNTH-001',html)
        self.save(revision=1,declaration_ref='CAL-SYNTH-002')
        with sqlite3.connect(self.path) as c:
            self.assertEqual(c.execute('SELECT count(*) FROM company_required_payment_calendar').fetchone()[0],2)
        self.assertEqual(first['revision'],1)
