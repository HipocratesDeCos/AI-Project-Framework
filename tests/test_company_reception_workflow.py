"""Acceptance test for the multi-file company workflow through the real HTTP API."""
import csv
from hashlib import sha256
from io import BytesIO, StringIO
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
from urllib.parse import quote
from urllib.request import Request, urlopen
from zipfile import ZipFile


class CompanyReceptionWorkflowTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db = Path(self.tmp.name) / 'isolated-company.db'
        # Empty active-company schema suffices to start the local app. No business
        # dataset or purchase is created by this test.
        with sqlite3.connect(self.db) as connection:
            connection.execute('CREATE TABLE documentary_company_snapshot(dataset_id TEXT PRIMARY KEY)')
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', 0))
            port = sock.getsockname()[1]
        self.url = 'http://127.0.0.1:' + str(port)
        self.server = subprocess.Popen([sys.executable, '-m', 'eios.company_app', '--db', str(self.db), '--port', str(port)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.addCleanup(self.stop)
        for _ in range(200):
            try:
                with urlopen(self.url, timeout=2) as response:
                    page = response.read().decode()
                break
            except OSError:
                if self.server.poll() is not None:
                    self.fail('Local company app failed to start')
                time.sleep(.03)
        else:
            self.fail('Local company app did not become ready')
        self.token = json.loads(re.search(r'token=("[^"]+")', page).group(1))
        self.sources = {}

    def stop(self):
        self.server.terminate()
        self.server.wait(timeout=5)

    def request(self, path, data=None, raw=None, headers=None, binary=False):
        request_headers = {'X-EIOS-Token':self.token}
        request_headers.update(headers or {})
        body = raw
        if data is not None:
            body = json.dumps(data).encode()
            request_headers['Content-Type'] = 'application/json'
        with urlopen(Request(self.url + path, data=body, headers=request_headers), timeout=10) as response:
            content = response.read()
            return content if binary else json.loads(content)

    def receive(self, kind, fields, rows, name=None):
        filename = name or kind + '.csv'
        if kind == 'document':
            content = b'%PDF-1.4\n%%EOF'
            mapping = {}
        else:
            text = StringIO(newline='')
            writer = csv.writer(text, delimiter=';', lineterminator='\r\n')
            writer.writerow(fields)
            writer.writerows(rows)
            content = text.getvalue().encode('utf-8-sig')
            mapping = dict(zip(fields, range(len(fields))))
        uploaded = self.request('/api/reception/read', raw=content, headers={'X-EIOS-Filename':quote(filename), 'X-EIOS-Delimiter':';'})
        preview = self.request('/api/reception/preview', data=dict(upload=uploaded['upload'],company_id='GARDEN-ACCEPTANCE',legal_name='Jardinería de prueba',material_nature='SYNTHETIC',as_of_date='2026-09-30',kind=kind,number_format='ES',mapping=mapping))
        self.assertEqual(preview['error_count'], 0)
        receipt = self.request('/api/reception/commit', data={'ticket':preview['ticket']})
        self.assertFalse(receipt['decision_authority'])
        self.assertEqual(receipt['admission_status'], 'PENDING')
        self.assertEqual(receipt['operational_path'], 'FORBIDDEN')
        self.sources[receipt['batch_id']] = content
        return receipt['batch_id']

    def test_multi_file_review_correction_and_export_without_operational_changes(self):
        fixtures = [
            ('supplier',['supplier_id','legal_name'],[['S-001','Proveedor de prueba']]),
            ('customer',['customer_id','legal_name'],[['C-001','Cliente de prueba']]),
            ('article',['article_id','description','unit','supplier_id'],[['A-0001','Estimulador de jardinería 5L','uds','S-001']]),
            ('purchase_line',['invoice_number','issue_date','supplier_id','article_id','quantity','unit','net_amount','currency'],[
                ['F-OLD','2026-09-01','S-001','A-0001','10','uds','1200,00','EUR'],
                ['F-LAST','2026-09-30','S-001','A-0001','40','uds','5140,00','EUR']]),
            ('inventory',['article_id','unit','physical','reserved'],[['A-0001','palets','75','15']]),
            ('stock_policy',['article_id','unit','minimum_stock','safety_stock','reorder_point','lead_time_days'],[['A-0001','uds','10','5','20','7']]),
            ('sales_line',['invoice_number','issue_date','customer_id','article_id','quantity','unit','net_amount','currency'],[
                ['V-001','2026-09-20','C-001','A-0001','3','uds','450,00','EUR'],
                ['V-002','2026-09-25','C-001','A-0001','1','uds','150,00','EUR']]),
            ('cash_flow',['flow_id','direction','amount','currency','due_date','counterparty'],[
                ['P-001','PAGO','125,50','EUR','2026-10-31','S-001'],
                ['C-001','COBRO','100,00','EUR','2026-09-30','C-001'],
                ['FX-001','PAGO','50,00','USD','2026-10-15','Soporte exterior']]),
            ('balance',['account_code','description','balance','currency'],[
                ['570','Caja','650,00','EUR'],['5720001','Banco','1250,50','EUR'],['4000001','Proveedor','-500,00','EUR']]),
            ('document',[],[]),
        ]
        batches = [self.receive(kind,fields,rows,name='soporte.pdf' if kind=='document' else None) for kind,fields,rows in fixtures]
        selected = dict(batch_ids=batches)
        overview = self.request('/api/reception/overviews')[0]
        self.assertEqual(overview['file_count'],10)
        self.assertEqual(overview['record_count'],15)
        initial_check = self.request('/api/reception/check',data=selected)
        self.assertEqual(sum(x['code']=='UNIT_MISMATCH' for x in initial_check['issues']),1)
        initial_article = self.request('/api/reception/articles',data=dict(selected,article_id='A-0001'))
        self.assertEqual(initial_article['stock']['status'],'UNIT_MISMATCH')
        self.assertIsNone(initial_article['stock']['physical'])
        initial_version = self.request('/api/reception/versions/save',data=dict(selected,name='Recepción inicial'))

        corrected_inventory = self.receive('inventory',['article_id','unit','physical','reserved'],[['A-0001','uds','75','15']],name='inventory_corrected.csv')
        corrected_batches = [corrected_inventory if bid==batches[4] else bid for bid in batches]
        corrected = dict(batch_ids=corrected_batches)
        check = self.request('/api/reception/check',data=corrected)
        self.assertFalse(any(x['code']=='UNIT_MISMATCH' for x in check['issues']))
        self.assertTrue(any(x['code']=='OUTSIDE_SCOPE' for x in check['issues']))
        article = self.request('/api/reception/articles',data=dict(corrected,article_id='A-0001'))
        self.assertEqual(article['last_purchases'][0]['net_unit_price'],'128.50')
        self.assertEqual(article['last_purchases'][0]['quantity'],'40')
        self.assertEqual(article['last_purchases'][0]['sources'][0]['row'],3)
        self.assertEqual(article['stock']['available'],'60')
        self.assertEqual(len(article['sales']),2)
        financials = self.request('/api/reception/financials',data=corrected)
        amounts = {(x['currency'],x['direction'],x['maturity']):x['amount'] for x in financials['flow_summaries']}
        self.assertEqual(amounts[('EUR','PAGO','AFTER_CUTOFF')],'125.50')
        self.assertEqual(amounts[('USD','PAGO','AFTER_CUTOFF')],'50.00')
        self.assertEqual(len(financials['account_summaries']),3)
        self.assertFalse(financials['decision_authority'])

        page = self.request('/api/reception/records',data=dict(company_id='GARDEN-ACCEPTANCE',batch_id=batches[3],query='F-LAST',offset=0,limit=50))
        self.assertEqual(page['matched_records'],1)
        self.assertEqual(page['records'][0]['source_row'],3)
        final_version = self.request('/api/reception/versions/save',data=dict(corrected,name='Inventario corregido'))
        reopened = self.request('/api/reception/version',data={'dossier_id':final_version['dossier_id']})
        self.assertEqual(set(reopened['manifest']['batch_ids']),set(corrected_batches))
        unchanged = self.request('/api/reception/versions/save',data=dict(corrected,name='No duplicar'))
        self.assertEqual(unchanged['status'],'UNCHANGED')
        comparison = self.request('/api/reception/versions/compare',data=dict(before_id=initial_version['dossier_id'],after_id=final_version['dossier_id']))
        self.assertEqual([x['batch_id'] for x in comparison['added_files']],[corrected_inventory])
        self.assertEqual([x['batch_id'] for x in comparison['removed_files']],[batches[4]])
        self.assertEqual(len(comparison['shared_files']),9)
        archive_bytes = self.request('/api/reception/version/export',data={'dossier_id':final_version['dossier_id']},binary=True)
        with ZipFile(BytesIO(archive_bytes)) as archive:
            exported = json.loads(archive.read('expediente_manifest.json'))
            self.assertEqual(len(archive.namelist()),13)
            self.assertEqual(exported['manifest'],reopened['manifest'])
            for item in exported['files']:
                content = archive.read(item['path'])
                self.assertEqual(content,self.sources[item['batch_id']])
                self.assertEqual(sha256(content).hexdigest(),item['source_sha256'])
            self.assertNotIn(batches[4],[item['batch_id'] for item in exported['files']])
            self.assertIn('PENDIENTE DE ADMISIÓN',archive.read('indice.html').decode())
        with sqlite3.connect(self.db) as connection:
            self.assertEqual(connection.execute('SELECT COUNT(*) FROM received_company_batch').fetchone()[0],11)
            self.assertEqual(connection.execute('SELECT COUNT(*) FROM received_company_dossier').fetchone()[0],2)
            self.assertEqual(connection.execute('SELECT COUNT(*) FROM documentary_company_snapshot').fetchone()[0],0)
            self.assertEqual(connection.execute('SELECT COUNT(*) FROM manual_purchase_proposal').fetchone()[0],0)
        with self.assertRaises(HTTPError) as denied:
            urlopen(Request(self.url+'/api/reception/versions/save',data=b'{}'),timeout=2)
        self.assertEqual(denied.exception.code,403)
