import json
import sqlite3
import unittest

from tests import test_company_payment_capture as fixture


class CompanyDocumentaryReviewTest(unittest.TestCase):
    tearDown=fixture.CompanyPaymentCaptureTest.tearDown
    add=fixture.CompanyPaymentCaptureTest.add
    financial_data=fixture.CompanyPaymentCaptureTest.financial_data
    prepare=fixture.CompanyPaymentCaptureTest.prepare
    activate=fixture.CompanyPaymentCaptureTest.activate
    capture=fixture.CompanyPaymentCaptureTest.capture

    def setUp(self):
        fixture.CompanyPaymentCaptureTest.setUp(self)
        self.report=self.capture()
        self.data_review=dict(dataset_id='one',proposal_id=self.saved['proposal_id'],
            review_id=self.report['review_id'],revision=0,reviewer='Revisor local',
            finding=dict(condition='AMOUNT',
                installment_ref=self.saved['payment_plan']['installments'][0]['canonical_candidate']['flow_id'],
                outcome='CONFIRMED_BY_REVIEW',note='Importe cotejado con el soporte sintético.',
                locators=[dict(document_ref='DOC-FIN',page=1,section='Cuota única')]))

    def save(self,**patch):
        return self.desk.record_payment_documentary_review(dict(self.data_review,**patch))

    def test_canonical_review_preserves_capture_and_pending_controls(self):
        result=self.save()
        self.assertEqual(result['confirmed_count'],1)
        self.assertEqual(result['pending_control_count'],7)
        self.assertEqual(result['control_count'],8)
        self.assertEqual(result['evidence_upgrade_status'],'NOT_PERFORMED')
        with sqlite3.connect(self.path) as c:
            payload=json.loads(c.execute('SELECT payload FROM company_payment_human_review').fetchone()[0])
        self.assertEqual(payload['schema_version'],'DOC-PAY-REVIEW-01/v0.1')
        self.assertEqual(payload['capture_fingerprint'],self.report['finance_execution']['documentary_capture']['fingerprint'])
        self.assertEqual(payload['findings'][0]['condition'],'AMOUNT')
        flows=payload['capture']['finance_package']['finance_input']['cash_flows']
        self.assertTrue(all(f['evidence_state']=='NOT_EVIDENCED' for f in flows))

    def test_correction_keeps_previous_review_and_stale_revision_fails(self):
        first=self.save()
        with self.assertRaises(ValueError):
            self.save()
        finding=dict(self.data_review['finding'],outcome='CONFLICT_REPORTED',note='Diferencia detectada.')
        second=self.save(revision=1,finding=finding)
        self.assertEqual(second['previous_review_ref'],first['review_ref'])
        self.assertEqual(second['confirmed_count'],0)
        self.assertEqual(second['conflict_count'],1)
        with sqlite3.connect(self.path) as c:
            self.assertEqual(c.execute('SELECT count(*) FROM company_payment_human_review').fetchone()[0],2)

    def test_confirmation_requires_exact_conserved_support(self):
        for patch in [dict(locators=[]),
                      dict(locators=[dict(document_ref='FOREIGN',page=1,section='Cuota única')]),
                      dict(locators=[dict(document_ref='DOC-FIN',page=2,section='Otra sección')]),
                      dict(installment_ref='OTHER'),dict(condition='UNKNOWN'),dict(note='')]:
            with self.subTest(patch=patch):
                with self.assertRaises(ValueError):
                    self.save(finding=dict(self.data_review['finding'],**patch))

    def test_negative_finding_without_support_does_not_become_confirmation(self):
        result=self.save(finding=dict(self.data_review['finding'],outcome='NOT_CONFIRMED',
            locators=[],note='No se ha podido confirmar el importe.'))
        self.assertEqual(result['not_confirmed_count'],1)
        self.assertEqual(result['confirmed_count'],0)
        self.assertEqual(result['pending_control_count'],7)

    def test_historical_print_and_source_deletion_keep_exact_review(self):
        args=('one',self.saved['proposal_id'],self.report['review_id'])
        old=self.desk.printable_report(*args)
        self.save()
        self.assertEqual(self.desk.printable_report(*args),old)
        new=self.desk.review('one',self.saved['proposal_id'])
        html=self.desk.printable_report('one',self.saved['proposal_id'],new['review_id'])
        self.assertIn('REVISIÓN DOCUMENTAL REGISTRADA',html)
        self.assertIn('Importe cotejado',html)
        self.assertEqual(new['finance_execution']['finance_result']['projection']['status'],'NOT_EVIDENCED')
        with sqlite3.connect(self.path) as c:
            c.execute('DELETE FROM documentary_source')
        # Recording another finding uses the conserved capture, not today's sources.
        result=self.save(revision=1,finding=dict(self.data_review['finding'],condition='CURRENCY'))
        self.assertEqual(result['confirmed_count'],2)

    def test_all_confirmed_controls_do_not_upgrade_evidence_or_determine_viability(self):
        installment=self.data_review['finding']['installment_ref']
        controls=[(condition,None) for condition in ('OPERATION_CORRESPONDENCE','DOCUMENT_TERMS','LISTED_DUPLICATION')]
        controls += [(condition,installment) for condition in ('INSTALLMENT_ASSOCIATION','AMOUNT','CURRENCY','DUE_DATE','SUPPORT_CONSISTENCY')]
        for revision,(condition,target) in enumerate(controls):
            result=self.save(revision=revision,finding=dict(self.data_review['finding'],
                condition=condition,installment_ref=target))
        self.assertEqual(result['pending_control_count'],0)
        self.assertEqual(result['confirmed_count'],8)
        self.assertEqual(result['calendar_check_scope'],'SEPARATE_CALENDAR_COVERAGE')
        report=self.desk.review('one',self.saved['proposal_id'])
        self.assertEqual(report['finance_execution']['viability_status'],'NOT_EVALUATED')
        self.assertTrue(all(f['canonical']['evidence_state']=='NOT_EVIDENCED' for f in report['financial_context']['cash_flows']))

    def test_missing_capture_and_wrong_scope_rejected(self):
        for patch in [dict(review_id=self.initial['review_id']),dict(dataset_id='two'),dict(reviewer=''),dict(revision=True)]:
            with self.subTest(patch=patch):
                with self.assertRaises(ValueError):
                    self.save(**patch)
