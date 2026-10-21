import base64
import json
import sqlite3
import unittest

from eios.company_finance_execution import execute_documentary_finance
from tests import test_company_finance_activation as fixtures


class CompanyPaymentCaptureTest(unittest.TestCase):
    tearDown=fixtures.FinanceActivationTest.tearDown
    add=fixtures.FinanceActivationTest.add
    financial_data=fixtures.FinanceActivationTest.financial_data
    prepare=fixtures.FinanceActivationTest.prepare
    activate=fixtures.FinanceActivationTest.activate

    def setUp(self):
        fixtures.FinanceActivationTest.setUp(self)
        self.financial_data()
        with sqlite3.connect(self.path) as c:
            c.execute('ALTER TABLE documentary_source ADD COLUMN document_ref TEXT')
            c.execute('ALTER TABLE documentary_source ADD COLUMN content BLOB')
            c.execute('INSERT INTO documentary_source VALUES(?,?,?)',('one','DOC-FIN',b'Synthetic payment terms'))
        self.prepare()
        self.activate()
        self.saved=self.desk.save(dict(self.data,unit_price='250',vat_percent='0',
            due_date='2026-10-15',shipping_mode='NONE',payment_installments=[
                dict(component='MERCHANDISE',amount='500',due_date='2026-10-15')]))
        self.initial=self.desk.review('one',self.saved['proposal_id'])
        self.payload=dict(dataset_id='one',proposal_id=self.saved['proposal_id'],
            review_id=self.initial['review_id'],revision=0,sequence=1,action='BIND',flow_id='P-1',
            locator=dict(document_ref='DOC-FIN',page=1,section='Cuota única'),
            actor='Local test',reason='Explicit synthetic correspondence')

    def capture(self):
        self.desk.declare_payment_association(self.payload)
        return self.desk.review('one',self.saved['proposal_id'])

    def test_canonical_capture_keeps_bytes_package_and_pending_states(self):
        report=self.capture()
        execution=report['finance_execution']
        capture=execution['documentary_capture']
        self.assertEqual(report['version'],'COMPANY-CONTEXT-REVIEW-07')
        self.assertEqual(capture['status'],'CAPTURED_LISTED_ASSOCIATIONS')
        self.assertEqual((capture['document_count'],capture['binding_count']),(1,1))
        self.assertEqual(capture['pending_review_control_count'],8)
        self.assertEqual(capture['required_calendar_status'],'NOT_SUPPLIED')
        with sqlite3.connect(self.path) as c:
            payload=json.loads(c.execute('SELECT payload FROM company_payment_documentary_capture WHERE fingerprint=?',
                (capture['fingerprint'],)).fetchone()[0])
        self.assertEqual(payload['schema_version'],'DOC-PAY-CAP-01/v0.1')
        self.assertEqual(payload['finance_package_fingerprint'],execution['finance_package_fingerprint'])
        self.assertEqual(base64.b64decode(payload['documents'][0]['content_base64']),b'Synthetic payment terms')
        self.assertEqual(payload['bindings'][0]['flow_id'],'P-1')
        self.assertIsNone(payload['order_ref'])
        self.assertIsNone(payload['confirmation_ref'])
        flows=payload['finance_package']['finance_input']['cash_flows']
        self.assertEqual(len(flows),2)
        self.assertTrue(all(f['evidence_state']=='NOT_EVIDENCED' for f in flows))
        self.assertEqual(execution['finance_result']['projection']['status'],'NOT_EVIDENCED')
        self.assertEqual(execution['purchase_effect_status'],'NOT_EVALUATED')
        self.assertFalse(capture['decision_authority'])

    def test_missing_binding_and_withdrawal_do_not_fabricate_capture(self):
        self.assertEqual(self.initial['finance_execution']['documentary_capture']['status'],'NOT_CAPTURED')
        self.capture()
        self.desk.declare_payment_association(dict(self.payload,revision=1,action='CLEAR'))
        after=self.desk.review('one',self.saved['proposal_id'])
        self.assertEqual(after['finance_execution']['documentary_capture']['status'],'NOT_CAPTURED')
        with sqlite3.connect(self.path) as c:
            self.assertEqual(c.execute('SELECT count(*) FROM company_payment_documentary_capture').fetchone()[0],1)

    def test_idempotent_capture_and_frozen_report(self):
        report=self.capture()
        args=('one',self.saved['proposal_id'],report['review_id'])
        html=self.desk.printable_report(*args)
        self.assertIn('CAPTURA DOCUMENTAL DE PAGOS',html)
        self.assertIn(report['finance_execution']['documentary_capture']['fingerprint'],html)
        repeated=self.desk.review('one',self.saved['proposal_id'])
        self.assertEqual(repeated['finance_execution']['documentary_capture'],report['finance_execution']['documentary_capture'])
        with sqlite3.connect(self.path) as c:
            self.assertEqual(c.execute('SELECT count(*) FROM company_payment_documentary_capture').fetchone()[0],1)
            c.execute('DELETE FROM documentary_source')
        self.assertEqual(self.desk.printable_report(*args),html)
        draft=self.desk.commercial_draft(*args)
        self.assertNotIn('DOC-FIN',draft['body'])
        self.assertNotIn('CAPTURA DOCUMENTAL',draft['body'])

    def test_changed_support_blocks_capture_without_promoting_or_appending_flows(self):
        report=self.capture()
        with sqlite3.connect(self.path) as c:
            c.execute('UPDATE documentary_source SET content=?',(b'changed',))
        result=execute_documentary_finance(self.path,self.saved,report['financial_context'],report['payment_associations'])
        self.assertEqual(result['documentary_capture']['status'],'NOT_CAPTURED')
        self.assertIn('difieren',result['documentary_capture']['message'])
        self.assertEqual(len(result['finance_input']['cash_flows']),2)
        self.assertTrue(all(f['evidence_state']=='NOT_EVIDENCED' for f in result['finance_input']['cash_flows']))
