import json
from hashlib import sha256
import re
import socket
import sqlite3
import subprocess
import sys
import time
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from tests import test_company_payment_capture as fixture


class CapturedPaymentDocumentTest(unittest.TestCase):
    setUp=fixture.CompanyPaymentCaptureTest.setUp
    tearDown=fixture.CompanyPaymentCaptureTest.tearDown
    add=fixture.CompanyPaymentCaptureTest.add
    financial_data=fixture.CompanyPaymentCaptureTest.financial_data
    prepare=fixture.CompanyPaymentCaptureTest.prepare
    activate=fixture.CompanyPaymentCaptureTest.activate
    capture=fixture.CompanyPaymentCaptureTest.capture

    def get_document(self,report,reference='DOC-FIN',dataset='one'):
        return self.desk.captured_payment_document(dataset,self.saved['proposal_id'],report['review_id'],reference)

    def test_exact_saved_bytes_download_after_current_sources_are_deleted(self):
        report=self.capture()
        document=self.get_document(report)
        self.assertEqual(document['content'],b'Synthetic payment terms')
        self.assertEqual(document['source_sha256'],sha256(document['content']).hexdigest())
        with sqlite3.connect(self.path) as c:
            c.execute('DELETE FROM documentary_source')
            c.execute("DELETE FROM documentary_company_record WHERE kind='cash_flow'")
        self.assertEqual(self.get_document(report),document)
        self.assertEqual(report['finance_execution']['documentary_capture']['documents'][0]['document_ref'],'DOC-FIN')

    def test_scope_absent_capture_and_foreign_reference_rejected(self):
        with self.assertRaises(ValueError):
            self.get_document(self.initial)
        report=self.capture()
        with self.assertRaises(ValueError):
            self.get_document(report,reference='OTHER')
        with self.assertRaises(ValueError):
            self.get_document(report,dataset='two')

    def test_altered_capture_and_missing_capture_are_rejected(self):
        report=self.capture()
        with sqlite3.connect(self.path) as c:
            row=c.execute('SELECT fingerprint,payload FROM company_payment_documentary_capture').fetchone()
            payload=json.loads(row[1])
            payload['documents'][0]['sha256']='0'*64
            c.execute('UPDATE company_payment_documentary_capture SET payload=?',(json.dumps(payload),))
        with self.assertRaises(ValueError):
            self.get_document(report)
        with sqlite3.connect(self.path) as c:
            c.execute('DELETE FROM company_payment_documentary_capture')
        with self.assertRaises(ValueError):
            self.get_document(report)

    def test_filename_uses_saved_context_and_removes_paths_and_control_characters(self):
        # Add source metadata before saving a new proposal so it is genuinely frozen.
        with sqlite3.connect(self.path) as c:
            c.execute('ALTER TABLE documentary_source ADD COLUMN metadata_json TEXT')
            c.execute('UPDATE documentary_source SET metadata_json=?',
                (json.dumps(dict(filename='C:'+chr(92)+'folder'+chr(92)+'soporte.pdf'+chr(13)+chr(10))),))
        saved=self.desk.save(dict(self.data,reference='WITH-NAME',unit_price='250',vat_percent='0',
            due_date='2026-10-15',shipping_mode='NONE',payment_installments=[
                dict(component='MERCHANDISE',amount='500',due_date='2026-10-15')]))
        report=self.desk.review('one',saved['proposal_id'])
        self.desk.declare_payment_association(dict(self.payload,proposal_id=saved['proposal_id'],review_id=report['review_id']))
        report=self.desk.review('one',saved['proposal_id'])
        document=self.desk.captured_payment_document('one',saved['proposal_id'],report['review_id'],'DOC-FIN')
        self.assertEqual(document['filename'],'soporte.pdf')

    def test_http_requires_token_and_returns_verified_attachment(self):
        report=self.capture()
        with socket.socket() as sock:
            sock.bind(('127.0.0.1',0))
            port=sock.getsockname()[1]
        process=subprocess.Popen([sys.executable,'-m','eios.company_app','--db',str(self.path),'--port',str(port)],
            stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        try:
            root='http://127.0.0.1:'+str(port)
            deadline=time.monotonic()+15
            while True:
                try:
                    page=urlopen(root,timeout=1).read().decode()
                    break
                except OSError:
                    if process.poll() is not None or time.monotonic()>deadline:
                        self.fail('Company app did not start')
                    time.sleep(.05)
            token=json.loads(re.search(r'const token=([^;]+);',page).group(1))
            data=json.dumps(dict(dataset_id='one',proposal_id=self.saved['proposal_id'],
                review_id=report['review_id'],document_ref='DOC-FIN')).encode()
            request=Request(root+'/api/purchases/payments/document',data=data,
                headers={'Content-Type':'application/json'},method='POST')
            with self.assertRaises(HTTPError) as error:
                urlopen(request,timeout=5)
            self.assertEqual(error.exception.code,403)
            request.add_header('X-EIOS-Token',token)
            with urlopen(request,timeout=5) as response:
                self.assertEqual(response.read(),b'Synthetic payment terms')
                self.assertEqual(response.headers.get_content_type(),'application/octet-stream')
                self.assertEqual(response.headers['Cache-Control'],'no-store')
                self.assertEqual(response.headers['X-Content-Type-Options'],'nosniff')
                self.assertIn('attachment',response.headers['Content-Disposition'])
                self.assertEqual(response.headers['X-EIOS-Source-SHA256'],sha256(b'Synthetic payment terms').hexdigest())
        finally:
            process.terminate()
            process.wait(timeout=10)
