from copy import deepcopy
import json
import sqlite3
import unittest
from tests import test_company_purchase_screen as fixture
from eios.company_sales_proposals import printable_offer, orientation


class SalesOfferTest(unittest.TestCase):
    tearDown = fixture.PurchaseScreenTest.tearDown

    def setUp(self):
        fixture.PurchaseScreenTest.setUp(self)
        with sqlite3.connect(self.path) as c:
            manifest=dict(company=dict(company_id='one',legal_name='Empresa sintética'),as_of_date='2026-09-30',material_nature='SYNTHETIC')
            c.execute('UPDATE documentary_company_snapshot SET manifest_json=? WHERE dataset_id=?',(json.dumps(manifest),'one'))
            rows=[('customer','C',dict(customer_id='C',legal_name='<script>Cliente</script>')),
                  ('purchase_invoice','P1',dict(issue_date='2026-09-20',supplier_id='S',currency='EUR')),
                  ('purchase_invoice_line','P1#1',dict(invoice_id='P1',article_id='A',supplier_id='S',quantity='2',net_amount='100',unit_price='50',unit_as_documented='palets',currency='EUR')),
                  ('sales_invoice','F1',dict(invoice_number='F1',customer_id='C',issue_date='2026-09-21',economic_position='ISSUED_BY_CUTOFF',currency='EUR')),
                  ('sales_invoice_line','F1#1',dict(invoice_number='F1',article_id='A',line=1,quantity='2',net_amount='180',unit_price='100',unit_as_documented='palets',currency='EUR'))]
            for kind,ref,data in rows:
                c.execute('INSERT INTO documentary_company_record VALUES(?,?,?,?)',('one',kind,ref,json.dumps(dict(record_id=ref,data=data,source_refs=[dict(document_ref='D',page=1)]))))
            c.execute('CREATE TABLE synthetic_planning_inventory(dataset_id TEXT,article_id TEXT,payload TEXT)')
            c.execute('INSERT INTO synthetic_planning_inventory VALUES(?,?,?)',('one','A',json.dumps(dict(unit='palets',physical=3,reserved=1,available=2,as_of_date='2026-09-30',material_nature='SYNTHETIC'))))
        self.state=self.desk.state('one')
        self.offer=dict(dataset_id='one',context_fingerprint=self.state['documentary_context']['fingerprint'],customer_id='C',reference='PV-001',offer_date='2026-10-22',valid_until='2026-11-01',delivery_date='2026-10-30',due_date='2026-11-30',delivery_location='Almacén cliente',payment_terms='Transferencia a 30 días',freight_net='10',freight_vat_percent='21',lines=[dict(article_id='A',quantity='2',unit_price='100',discount_value='10',vat_percent='21')])

    def test_totals_multiple_lines_margin_and_frozen_persistence(self):
        result=self.desk.sales_offer(dict(self.offer,lines=self.offer['lines']*2))
        self.assertEqual(result['net_amount'],'370.00')
        self.assertEqual(result['vat_amount'],'77.70')
        self.assertEqual(result['total'],'447.70')
        self.assertEqual(result['lines'][0]['reference_margin_percent'],'44.44')
        self.assertTrue(result['warnings'])
        self.assertEqual(result['lines'][0]['orientation']['latest_sales'][0]['net_unit_price'],'90')
        self.assertFalse(result['decision_authority'])
        self.assertEqual(result['operational_path'],'FORBIDDEN')
        self.assertEqual(self.desk.state('two')['sales_proposals'],[])
        self.assertEqual(self.desk.state('one')['sales_proposals'],[result])
        self.assertEqual(self.desk.state('one')['inventory'],self.state['inventory'])
        self.assertEqual(self.desk.state('one')['sales'],self.state['sales'])
        self.assertEqual(self.desk.state('one')['purchases'],[])
        html=printable_offer(self.path,'one',result['proposal_id'])
        with sqlite3.connect(self.path) as c:
            c.execute('DELETE FROM documentary_company_record')
        self.assertEqual(printable_offer(self.path,'one',result['proposal_id']),html)

    def test_preview_does_not_save_and_reference_is_unique(self):
        preview=self.desk.sales_offer(self.offer,persist=False)
        self.assertEqual(preview['total'],'229.90')
        self.assertEqual(self.desk.state('one')['sales_proposals'],[])
        self.desk.sales_offer(self.offer)
        with self.assertRaises(ValueError):self.desk.sales_offer(self.offer)

    def test_invalid_foreign_missing_and_stale_data_do_not_write(self):
        for patch in [dict(customer_id='OTHER'),dict(dataset_id='two'),dict(context_fingerprint='old'),dict(lines=[]),dict(lines=self.offer['lines']*31),dict(valid_until='2026-01-01'),dict(freight_net='NaN'),dict(freight_vat_percent='101'),dict(freight_net='0.001'),dict(payment_terms='')]:
            with self.subTest(patch=patch),self.assertRaises(ValueError):self.desk.sales_offer(dict(self.offer,**patch))
        for patch in [dict(quantity='0'),dict(quantity=True),dict(article_id='OTHER'),dict(unit_price='Infinity'),dict(discount_value='101'),dict(vat_percent='')]:
            with self.subTest(patch=patch),self.assertRaises(ValueError):self.desk.sales_offer(dict(self.offer,lines=[dict(self.offer['lines'][0],**patch)]))
        self.assertEqual(self.desk.state('one')['sales_proposals'],[])

    def test_history_requires_exact_sku_unit_currency_and_unique_latest_cost(self):
        state=deepcopy(self.state)
        a=state['articles'][0]
        self.assertEqual(orientation(state,'C',a)['reference_unit_cost'],'50')
        state['history']['A']*=2
        self.assertIsNone(orientation(state,'C',a)['reference_unit_cost'])
        state['sales']['invoices'][0]['lines'][0]['unit']='uds'
        self.assertEqual(orientation(state,'C',a)['latest_sales'],[])
        state['sales']['invoices'][0]['lines'][0]['unit']='palets'
        state['sales']['invoices'][0]['lines'][0]['currency']='USD'
        self.assertEqual(orientation(state,'C',a)['latest_sales'],[])
        state['inventory']['A']['unit']='uds'
        self.assertIsNone(orientation(state,'C',a)['inventory'])

    def test_client_report_escapes_inputs_and_excludes_internal_context(self):
        result=self.desk.sales_offer(self.offer)
        html=printable_offer(self.path,'one',result['proposal_id'])
        self.assertIn('&lt;script&gt;Cliente&lt;/script&gt;',html)
        self.assertIn('22/10/2026',html)
        self.assertIn('229,90',html)
        for token in ('<script>Cliente','reference_margin_percent','purchase_references','documentary_context','44,44'):
            self.assertNotIn(token,html)
        with self.assertRaises(ValueError):printable_offer(self.path,'two',result['proposal_id'])
