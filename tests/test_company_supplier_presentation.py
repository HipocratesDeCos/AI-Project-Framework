import json
from pathlib import Path
import shutil
import sqlite3
import subprocess
import unittest

from eios.company_app import PAGE
from eios.company_presentation import number_text, date_text
from tests import test_company_purchase_screen as fixture


class ProposalSupplierPresentationTest(unittest.TestCase):
    setUp = fixture.PurchaseScreenTest.setUp
    tearDown = fixture.PurchaseScreenTest.tearDown

    def supplier(self, **patch):
        data = dict(supplier_id='S', legal_name='Proveedor Ejemplo, S.L.', **patch)
        with sqlite3.connect(self.path) as c:
            c.execute("UPDATE documentary_company_record SET record_json=? WHERE dataset_id='one' AND kind='supplier'",
                      (json.dumps(dict(data=data)),))

    def draft(self, proposal):
        review = self.desk.review('one', proposal['proposal_id'])
        return self.desk.commercial_draft('one', proposal['proposal_id'], review['review_id'])

    def test_supplier_default_contact_and_saved_values(self):
        self.supplier(contact_name=' Ana López ', delivery_location='Almacén 2, Calle Ejemplo 15')
        proposal = self.desk.save(self.data)
        self.assertEqual(proposal['delivery_location'], 'Almacén 2, Calle Ejemplo 15')
        self.assertEqual(proposal['supplier_commercial_at_save']['contact_name'], 'Ana López')
        body = self.draft(proposal)['body']
        self.assertIn('Estimado Ana López:', body)
        self.assertIn('Lugar de entrega: Almacén 2, Calle Ejemplo 15', body)
        self.assertIn('01/11/2026', body)
        self.assertEqual(proposal['due_date'], '2026-11-01')

    def test_legal_name_fallback_and_explicit_override(self):
        self.supplier(contact_name=' ', delivery_location='Lugar por defecto')
        proposal = self.desk.save(dict(self.data, delivery_location='Otra entrega'))
        self.assertEqual(proposal['delivery_location'], 'Otra entrega')
        self.assertIn('Estimado Proveedor Ejemplo, S.L.:', self.draft(proposal)['body'])
        proposal2 = self.desk.save(dict(self.data, reference='P-2', delivery_location=''))
        self.assertIsNone(proposal2['delivery_location'])

    def test_no_delivery_is_inferred_from_supplier_locality(self):
        self.supplier(locality='Sabadell')
        proposal = self.desk.save(self.data)
        self.assertIsNone(proposal['delivery_location'])
        self.assertIn('Lugar de entrega: Pendiente de confirmar', self.draft(proposal)['body'])

    def test_text_validation_without_write(self):
        self.supplier()
        for value in (123, 'x'*501):
            with self.assertRaises(ValueError):
                self.desk.save(dict(self.data, delivery_location=value))
        self.assertEqual(self.desk.state('one')['purchases'], [])

    def test_spanish_numbers_dates_and_identifiers(self):
        for value, expected in [('1234.50','1.234,50'),('1000','1.000'),
                                ('-1234567.890','-1.234.567,890'),('0','0')]:
            self.assertEqual(number_text(value), expected)
        self.assertEqual(number_text('1234', 2), '1.234,00')
        self.assertEqual(date_text('2026-09-30'), '30/09/2026')
        self.assertEqual(date_text('2026-09-30T12:30:00+00:00'), '30/09/2026 12:30:00 +0000')
        self.assertEqual(date_text('INV-2026-001'), 'INV-2026-001')
        self.supplier()
        proposal = self.desk.save(dict(self.data, quantity='1000', unit_price='1234.5'))
        body = self.draft(proposal)['body']
        self.assertIn('Cantidad: 1.000 palets', body)
        self.assertIn('Precio neto unitario: 1.234,50 EUR', body)
        self.assertEqual(proposal['quantity'], '1000')
        self.assertEqual(proposal['article_id'], 'A')

    @unittest.skipUnless(shutil.which('node'), 'Node not installed')
    def test_ui_number_and_date_conversion(self):
        names = ['stockDate','stockNumber','money','inputDateISO','canonicalDates']
        functions = []
        for name in names:
            start = PAGE.index('function ' + name + '(')
            end = PAGE.index('\n', start)
            functions.append(PAGE[start:end])
        script = '\n'.join(functions) + '''
const assert=require('node:assert/strict');
assert.equal(money('1234.5'),'1.234,50');
assert.equal(stockNumber('1234'),'1.234');
assert.equal(stockDate('2026-09-30'),'30/09/2026');
assert.equal(inputDateISO('30/09/2026'),'2026-09-30');
assert.throws(()=>inputDateISO('31/02/2026'));
assert.deepEqual(canonicalDates({order_date:'30/09/2026',reference:'OP-2026-001'}),{order_date:'2026-09-30',reference:'OP-2026-001'});
'''
        path = Path(self.tmp.name) / 'presentation.js'
        path.write_text(script, encoding='utf-8')
        result = subprocess.run(['node',str(path)], capture_output=True, text=True)
        self.assertEqual(result.returncode,0,result.stderr)
