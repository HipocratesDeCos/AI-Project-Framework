import json
from pathlib import Path
import re
import shutil
import socket
import sqlite3
import subprocess
import sys
import tempfile
import time
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from eios.company_app import PAGE
from tests import test_company_purchase_screen as fixture


class PrintableProposalReportTest(unittest.TestCase):
    setUp = fixture.PurchaseScreenTest.setUp
    tearDown = fixture.PurchaseScreenTest.tearDown

    def report(self, **patch):
        saved = self.desk.save(dict(self.data, **patch))
        return self.desk.review('one', saved['proposal_id'])

    def export(self, report):
        return self.desk.printable_report('one', report['proposal_id'], report['review_id'])

    def test_complete_sections_unknown_costs_and_print_layout(self):
        report = self.report()
        html = self.export(report)
        for expected in ('@page', '@media print', 'window.print()', 'Guardar como PDF',
                         'IDENTIFICACIÓN Y FECHAS', 'IMPORTES Y CONDICIONES',
                         'COMPARACIÓN CON LA ÚLTIMA COMPRA', 'STOCK, COBERTURA',
                         'TESORERÍA Y DECISIÓN', 'COMPROBACIONES PENDIENTES',
                         'FUENTES Y TRAZABILIDAD', 'Pendiente / sin datos',
                         report['review_id'], 'FORBIDDEN', '242.00 EUR'):
            self.assertIn(expected, html)
        self.assertNotIn('<script src=', html)
        self.assertIn('No constituye aceptación', html)

    def test_user_text_and_source_metadata_are_escaped(self):
        with sqlite3.connect(self.path) as c:
            c.execute('ALTER TABLE documentary_source ADD COLUMN document_ref TEXT')
            c.execute('ALTER TABLE documentary_source ADD COLUMN metadata_json TEXT')
            c.execute('ALTER TABLE documentary_source ADD COLUMN content BLOB')
            c.execute('INSERT INTO documentary_source VALUES(?,?,?,?)',
                      ('one', '<img src=x onerror=alert(1)>',
                       json.dumps(dict(filename='<script>alert(1)</script>')), b'file'))
        html = self.export(self.report(reference='<script>alert(1)</script>'))
        self.assertNotIn('<script>', html)
        self.assertNotIn('<img src=', html)
        self.assertIn('&lt;script&gt;', html)
        self.assertIn('&lt;img', html)

    def test_export_is_exact_saved_review_after_database_changes(self):
        report = self.report()
        before = self.export(report)
        with sqlite3.connect(self.path) as c:
            c.execute("DELETE FROM documentary_company_record WHERE dataset_id='one'")
            c.execute("UPDATE documentary_company_snapshot SET manifest_json='{}' WHERE dataset_id='one'")
        self.assertEqual(self.export(report), before)

    def test_cross_company_or_unknown_review_rejected(self):
        report = self.report()
        for dataset, proposal, review in [('two',report['proposal_id'],report['review_id']),
                                          ('one','foreign',report['review_id']),
                                          ('one',report['proposal_id'],'absent')]:
            with self.assertRaises(ValueError):
                self.desk.printable_report(dataset, proposal, review)

    def test_no_review_has_explicit_error(self):
        saved = self.desk.save(self.data)
        with self.assertRaisesRegex(ValueError, 'Primero revisa'):
            self.desk.printable_report('one', saved['proposal_id'], 'absent')

    def test_legacy_review_without_capture_stays_explicit(self):
        report = self.report()
        report['proposal'].pop('documentary_context_at_save')
        report['proposal'].pop('stock_context_at_save')
        with sqlite3.connect(self.path) as c:
            c.execute('UPDATE manual_purchase_context_review SET payload=? WHERE review_id=?',
                      (json.dumps(report), report['review_id']))
        html = self.export(report)
        self.assertIn('SIN CAPTURA DOCUMENTAL', html)
        self.assertIn('Sin captura anterior', html)

    @unittest.skipUnless(shutil.which('node'), 'Node not installed')
    def test_page_javascript_syntax(self):
        script = PAGE.split('<script>')[1].split('</script>')[0]
        path = Path(self.tmp.name) / 'page.js'
        path.write_text(script, encoding='utf-8')
        result = subprocess.run(['node', '--check', str(path)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_http_export_requires_token_and_returns_scoped_html(self):
        report = self.report()
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', 0))
            port = sock.getsockname()[1]
        process = subprocess.Popen([sys.executable, '-m', 'eios.company_app', '--db', str(self.path), '--port', str(port)],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            root = 'http://127.0.0.1:' + str(port)
            deadline = time.monotonic() + 15
            while True:
                try:
                    page = urlopen(root, timeout=1).read().decode()
                    break
                except OSError:
                    if process.poll() is not None or time.monotonic() > deadline:
                        self.fail('Company HTTP app did not start')
                    time.sleep(.05)
            token = json.loads(re.search(r'const token=([^;]+);', page).group(1))
            data = json.dumps(dict(dataset_id='one',proposal_id=report['proposal_id'],review_id=report['review_id'])).encode()
            request = Request(root+'/api/purchases/report', data=data, headers={'Content-Type':'application/json'}, method='POST')
            with self.assertRaises(HTTPError) as error:
                urlopen(request, timeout=5)
            self.assertEqual(error.exception.code, 403)
            request.add_header('X-EIOS-Token', token)
            with urlopen(request, timeout=5) as response:
                html = response.read().decode()
                self.assertEqual(response.headers.get_content_type(), 'text/html')
                self.assertEqual(response.headers['Cache-Control'], 'no-store')
                self.assertIn(report['review_id'], html)
                self.assertIn('242.00 EUR', html)
        finally:
            process.terminate()
            process.wait(timeout=10)
