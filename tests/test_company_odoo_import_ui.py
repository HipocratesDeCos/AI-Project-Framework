"""Visual Odoo RFQ import: preview contract, guardrails and integration wiring."""

import csv
from hashlib import sha256
from io import BytesIO, StringIO
import inspect
import unittest

from openpyxl import Workbook

from eios.company_app import PAGE, main
from eios.company_odoo_import_ui import HTML, JS
from integrations.odoo.purchase_order_export_v02 import preview_file

HEADERS = [
    'ID', 'Referencia del pedido', 'Proveedor', 'Fecha del pedido',
    'Estado', 'Moneda/Nombre', 'Líneas del pedido/ID',
    'Líneas del pedido/Producto', 'Producto/Referencia interna',
    'Líneas del pedido/Cantidad', 'Líneas del pedido/Precio unitario',
    'Líneas del pedido/Subtotal', 'Impuestos', 'Total',
]
CASES = [
    (10, 'ILU-0001', 2, 415.8, 831.6, 174.64, 1006.24),
    (9, 'SUS-0021', 40, 8.5, 340, 71.4, 411.4),
    (8, 'SUS-0013', 36, 8.5, 306, 64.26, 370.26),
    (7, 'SUS-0007', 48, 8.5, 408, 85.68, 493.68),
    (6, 'CON-0151', 3, 64.35, 193.05, 40.54, 233.59),
    (5, 'SUS-0001', 32, 8.42, 269.44, 56.58, 326.02),
    (4, 'SUS-0025', 45, 8.5, 382.5, 80.33, 462.83),
    (3, 'TUT-0001', 240, .35, 84, 17.64, 101.64),
    (1, 'ILU-0012', 6, 28, 168, 35.28, 203.28),
]


def sample_rows():
    rows = []
    for number, sku, qty, unit_price, base, tax, total in CASES:
        rows.append([
            f'__export__.purchase_order_{number}',
            f'EIOS-DEMO-PO-2026-{number:03}',
            f'Proveedor {number}', None, 'SdP', 'Euro',
            f'eios_demo.import_line_2026_{number:03}',
            f'[{sku}] Producto de prueba {number}', sku, qty, unit_price,
            base, tax, total,
        ])
    rows.insert(-1, [
        '__export__.purchase_order_2', 'EIOS-DEMO-PO-2026-002',
        'Proveedor 2', None, 'SdP', 'Euro', None, None, None,
        None, None, None, 0, 0,
    ])
    return rows


def build_csv(rows=None):
    stream = StringIO(newline='')
    writer = csv.writer(stream, delimiter=';')
    writer.writerow(HEADERS)
    writer.writerows(sample_rows() if rows is None else rows)
    return stream.getvalue().encode('utf-8-sig')


def build_xlsx(rows=None):
    wb = Workbook()
    sheet = wb.active
    sheet.append(HEADERS)
    for row in sample_rows() if rows is None else rows:
        sheet.append(row)
    stream = BytesIO()
    wb.save(stream)
    wb.close()
    return stream.getvalue()


class OdooPurchaseUiTests(unittest.TestCase):
    def test_preview_panel_embedded_in_company_file_workspace(self):
        self.assertIn('id="odoo-purchase-file"', HTML)
        self.assertIn('id="odoo-purchase-check"', HTML)
        self.assertIn('id="odoo-purchase-import"', PAGE)
        self.assertIn('/api/odoo/purchase-orders/preview', JS)
        self.assertIn('X-EIOS-Token', JS)
        self.assertIn('X-EIOS-Filename', JS)
        self.assertIn('odoo-purchase-orders', PAGE)
        self.assertNotIn('id="odoo-purchase-save"', HTML)
        self.assertNotIn('/api/odoo/purchase-orders/commit', inspect.getsource(main))

    def test_company_app_preview_route_present_with_upload_limit(self):
        source = inspect.getsource(main)
        self.assertIn("if self.path == '/api/odoo/purchase-orders/preview':", source)
        self.assertIn("'X-EIOS-Token'", source)
        self.assertIn("'X-EIOS-Filename'", source)
        self.assertIn("preview_file(self.rfile.read(size), filename)", source)
        self.assertIn("'checked_at'", source)
        self.assertIn("MAX_BYTES if self.path in", source)

    def test_realistic_ten_row_excel_preview_no_partial_admission(self):
        original = build_xlsx()
        result = preview_file(original, 'Pedido de compra (purchase.order) (4).xlsx')
        self.assertEqual(result['sha256'], sha256(original).hexdigest())
        self.assertEqual(result['errors'], [])
        self.assertEqual(len(result['orders_preview']), 9)
        self.assertEqual(result['summary']['complete_orders'], 9)
        self.assertEqual(result['summary']['pending_orders'], 1)
        self.assertEqual(result['summary']['lines_with_external_id'], 9)
        self.assertEqual(result['summary']['base'], '2982.59')
        self.assertEqual(result['summary']['tax'], '626.35')
        self.assertEqual(result['summary']['total'], '3608.94')
        self.assertEqual(result['pending_orders'][0]['reference'], 'EIOS-DEMO-PO-2026-002')
        self.assertFalse(result['accepted'])
        self.assertFalse(result['persistence_allowed'])
        self.assertFalse(result['decision_authority'])
        self.assertEqual(result['operational_path'], 'FORBIDDEN')

    def test_csv_same_contract_with_missing_order_date(self):
        result = preview_file(build_csv(), 'odoo_purchase.csv')
        self.assertEqual(result['summary']['complete_orders'], 9)
        self.assertEqual(result['summary']['pending_orders'], 1)
        self.assertTrue(any(i['code'] == 'ORDER_DATE_MISSING' for i in result['warnings']))
        self.assertTrue(all(o['order_date'] is None for o in result['orders_preview']))

    def test_corrupted_row_fails_closed(self):
        rows = sample_rows()
        rows[0][11] = 1
        result = preview_file(build_xlsx(rows), 'orders.xlsx')
        self.assertFalse(result['accepted'])
        self.assertEqual(result['orders_preview'], [])
        self.assertTrue(result['errors'])
        self.assertFalse(result['persistence_allowed'])

    def test_no_line_is_not_zero_value_purchase(self):
        result = preview_file(build_xlsx(), 'orders.xlsx')
        pending = result['pending_orders'][0]
        self.assertEqual(pending['reason'], 'NO_ORDER_LINES')
        self.assertEqual(pending['total'], '0.00')
        self.assertNotIn(pending['external_id'],
                         {o['external_id'] for o in result['orders_preview']})


if __name__ == '__main__':
    unittest.main()
