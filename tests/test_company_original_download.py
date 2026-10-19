from hashlib import sha256
import json
from pathlib import Path
import re
import socket
import sqlite3
import subprocess
import sys
import tempfile
import time
import unittest
from urllib.error import HTTPError
from urllib.parse import unquote
from urllib.request import Request, urlopen

from eios.company_reception import CompanyReception


class OriginalDownloadTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db = Path(self.tmp.name) / 'company.db'
        self.reception = CompanyReception(self.db)
        self.content = 'Codigo;Nombre\r\n0001;Proveedor español\r\n'.encode('utf-8-sig')
        self.filename = 'proveedores españoles.csv'
        file = self.reception.read(self.content, self.filename, delimiter=';')
        report = self.reception.preview(dict(upload=file['upload'], company_id='CLIENT', legal_name='Empresa', material_nature='REAL', as_of_date='2026-09-30', kind='supplier', number_format='ES', mapping=dict(supplier_id=0, legal_name=1)))
        self.batch = self.reception.commit(report['ticket'])['batch_id']

    def test_exact_original_and_read_only(self):
        before = self.db.read_bytes()
        result = self.reception.original('CLIENT', self.batch)
        self.assertEqual(result['content'], self.content)
        self.assertEqual(result['filename'], self.filename)
        self.assertEqual(result['source_sha256'], sha256(self.content).hexdigest())
        self.assertEqual(self.db.read_bytes(), before)
        self.assertEqual(self.reception.batches()[0]['admission_status'], 'PENDING')

    def test_company_scope_unknown_and_invalid_ids(self):
        for company, bid in [('OTHER', self.batch), ('CLIENT', 'f'*64), ('CLIENT', '../../x'), ('CLIENT', None)]:
            with self.assertRaises(ValueError):
                self.reception.original(company, bid)

    def test_corrupted_bytes_rejected(self):
        with sqlite3.connect(self.db) as c:
            c.execute('UPDATE received_company_batch SET content=?', (b'changed',))
        with self.assertRaisesRegex(ValueError, 'integridad'):
            self.reception.original('CLIENT', self.batch)

    def test_http_download_requires_session_and_preserves_filename(self):
        with sqlite3.connect(self.db) as c:
            c.execute("CREATE TABLE documentary_company_snapshot(dataset_id TEXT PRIMARY KEY)")
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', 0))
            port = sock.getsockname()[1]
        server = subprocess.Popen([sys.executable, '-m', 'eios.company_app', '--db', str(self.db), '--port', str(port)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        def stop():
            server.terminate()
            server.wait(timeout=5)
        self.addCleanup(stop)
        url = 'http://127.0.0.1:' + str(port)
        for _ in range(100):
            try:
                with urlopen(url, timeout=1) as response:
                    page = response.read().decode()
                break
            except OSError:
                if server.poll() is not None:
                    self.fail('Server failed to start')
                time.sleep(.03)
        else:
            self.fail('Server did not become ready')
        token = re.search(r'const token=("[^"]+")', page)
        if token is None:
            token = re.search(r'token=("[^"]+")', page)
        self.assertIsNotNone(token)
        token = json.loads(token.group(1))
        payload = json.dumps(dict(company_id='CLIENT', batch_id=self.batch)).encode()
        endpoint = url + '/api/reception/original'
        with self.assertRaises(HTTPError) as rejected:
            urlopen(Request(endpoint, data=payload), timeout=2)
        self.assertEqual(rejected.exception.code, 403)
        request = Request(endpoint, data=payload, headers={'X-EIOS-Token':token, 'Content-Type':'application/json'})
        with urlopen(request, timeout=2) as response:
            self.assertEqual(response.read(), self.content)
            self.assertEqual(response.headers['Content-Type'], 'application/octet-stream')
            self.assertIn(self.filename, unquote(response.headers['Content-Disposition']))
            self.assertEqual(response.headers['Cache-Control'], 'no-store')
            self.assertEqual(response.headers['X-EIOS-Source-SHA256'], sha256(self.content).hexdigest())
