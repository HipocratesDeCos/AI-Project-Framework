"""Exercise the actual local HTTP endpoint and its no-write boundary."""

from contextlib import closing
import json
import re
import socket
import sqlite3
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

import csv
from io import StringIO


def build_csv():
    stream = StringIO(newline='')
    writer = csv.writer(stream, delimiter=';')
    writer.writerow([
        'ID', 'Referencia del pedido', 'Proveedor', 'Fecha del pedido',
        'Estado', 'Moneda/Nombre', 'Líneas del pedido/ID',
        'Líneas del pedido/Producto', 'Producto/Referencia interna',
        'Líneas del pedido/Cantidad', 'Líneas del pedido/Precio unitario',
        'Líneas del pedido/Subtotal', 'Impuestos', 'Total',
    ])
    writer.writerow([
        '__export__.purchase_order_1', 'EIOS-DEMO-PO-2026-001',
        'Proveedor 1', '', 'SdP', 'Euro', 'eios_demo.line_1',
        '[ILU-0012] Producto de prueba', 'ILU-0012',
        6, 28, 168, 35.28, 203.28,
    ])
    writer.writerow([
        '__export__.purchase_order_2', 'EIOS-DEMO-PO-2026-002',
        'Proveedor 2', '', 'SdP', 'Euro', '', '', '',
        '', '', '', 0, 0,
    ])
    return stream.getvalue().encode('utf-8-sig')


class OdooPreviewHttpTests(unittest.TestCase):
    def test_real_local_http_preview_requires_token_and_does_not_persist(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / 'company.sqlite3'
            with sqlite3.connect(db) as connection:
                connection.execute('''
                    CREATE TABLE documentary_company_snapshot (
                        dataset_id TEXT PRIMARY KEY,
                        company_id TEXT NOT NULL,
                        as_of_date TEXT NOT NULL,
                        manifest_json TEXT NOT NULL
                    )
                ''')
            with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
                sock.bind(('127.0.0.1', 0))
                port = sock.getsockname()[1]
            url = f'http://127.0.0.1:{port}'
            process = subprocess.Popen([
                sys.executable, '-m', 'eios.company_app',
                '--db', str(db), '--port', str(port),
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            try:
                page = None
                for _ in range(50):
                    if process.poll() is not None:
                        self.fail('EIOS local server closed before starting')
                    try:
                        with urlopen(url + '/', timeout=2) as response:
                            page = response.read().decode('utf-8')
                        break
                    except (URLError, TimeoutError):
                        time.sleep(.1)
                self.assertIsNotNone(page, 'Local HTTP server did not start')
                match = re.search(r'const token=("[^"]+");', page)
                self.assertIsNotNone(match, 'Session token missing from page')
                token = json.loads(match.group(1))
                body = build_csv()
                route = url + '/api/odoo/purchase-orders/preview'

                request = Request(route, data=body, method='POST', headers={
                    'X-EIOS-Filename': quote('Pedidos Odoo.csv'),
                    'Content-Type': 'application/octet-stream',
                })
                with self.assertRaises(HTTPError) as denied:
                    urlopen(request, timeout=5)
                self.assertEqual(denied.exception.code, 403)

                request.add_header('X-EIOS-Token', token)
                with urlopen(request, timeout=10) as response:
                    result = json.load(response)
                self.assertEqual(result['filename'], 'Pedidos Odoo.csv')
                self.assertTrue(result['checked_at'])
                self.assertEqual(result['summary']['complete_orders'], 1)
                self.assertEqual(result['summary']['pending_orders'], 1)
                self.assertEqual(result['summary']['total'], '203.28')
                self.assertFalse(result['accepted'])
                self.assertFalse(result['persistence_allowed'])
                self.assertEqual(result['operational_path'], 'FORBIDDEN')

                wrong_filename = Request(route, data=body, method='POST', headers={
                    'X-EIOS-Filename': 'pedidos.pdf',
                    'X-EIOS-Token': token,
                    'Content-Type': 'application/octet-stream',
                })
                with self.assertRaises(HTTPError) as rejected:
                    urlopen(wrong_filename, timeout=5)
                self.assertEqual(rejected.exception.code, 400)

                with sqlite3.connect(db) as connection:
                    self.assertEqual(connection.execute(
                        'SELECT COUNT(*) FROM documentary_company_snapshot'
                    ).fetchone()[0], 0)
                    self.assertIsNone(connection.execute(
                        "SELECT name FROM sqlite_master WHERE type='table' "
                        "AND name='received_company_batch'"
                    ).fetchone())
            finally:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)


if __name__ == '__main__':
    unittest.main()
