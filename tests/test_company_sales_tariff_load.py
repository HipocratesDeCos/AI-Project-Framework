import json
from pathlib import Path
import sqlite3
import unittest
from tests import test_company_sales_negotiation as fixture
from eios.company_sales_tariff_load import load_tariff


class TariffLoadTest(unittest.TestCase):
    add=fixture.SalesNegotiationTest.add
    financial_data=fixture.SalesNegotiationTest.financial_data
    set_policy=fixture.SalesNegotiationTest.set_policy
    tearDown=fixture.SalesNegotiationTest.tearDown

    def setUp(self):
        fixture.SalesNegotiationTest.setUp(self)
        self.file=Path(self.path).parent/'Tarifa_SINTETICA.csv'
        self.write()

    def write(self,sku='A',unit='palets',price='80,00'):
        self.file.write_text(f'SKU;Unidad;PVP sin IVA;Moneda;Válida desde;Válida hasta\n{sku};{unit};{price};EUR;01/10/2026;31/12/2026\n')

    def load(self):return load_tariff(self.path,self.file,'Preparación sintética',dataset='one')

    def test_load_selects_reference_with_sources_and_repeating_preserves_it(self):
        first=self.load();self.assertEqual(first['selected'],['A']);self.assertFalse(first['decision_authority'])
        orientation=self.desk.sales_orientation(dict(dataset_id='one',article_id='A',customer_id='C',offer_date='2026-10-22'))
        self.assertEqual(orientation['price_reference']['recommended_unit_price'],'80.00')
        self.assertIn('ficticia',orientation['price_reference']['tariff_reference']['reason'])
        self.assertEqual(orientation['default_unit_price'],'90')
        second=self.load();self.assertEqual(second['selected'],[]);self.assertEqual(second['preserved'],['A'])
        with sqlite3.connect(self.path) as c:
            self.assertEqual(c.execute('SELECT COUNT(*) FROM company_sales_tariff').fetchone()[0],1)
            self.assertEqual(c.execute('SELECT COUNT(*) FROM received_company_batch').fetchone()[0],1)

    def test_incompatible_or_duplicate_rows_are_rejected_before_any_reception(self):
        for sku,unit,price in [('foreign','palets','80,00'),('A','uds.','80,00'),('A','palets','-1')]:
            self.write(sku,unit,price)
            with self.assertRaises(ValueError):self.load()
        self.write();self.file.write_text(self.file.read_text()+self.file.read_text().splitlines()[1]+'\n')
        with self.assertRaises(ValueError):self.load()
        with sqlite3.connect(self.path) as c:self.assertIsNone(c.execute("SELECT name FROM sqlite_master WHERE name='received_company_batch'").fetchone())

    def test_existing_catalogue_price_is_preserved_and_old_evaluations_expire(self):
        old=self.desk.state('one')['documentary_context']['fingerprint'];self.load()
        with self.assertRaises(ValueError):self.desk.sales_offer(dict(self.offer,context_fingerprint=old),persist=False)
        with sqlite3.connect(self.path) as c:
            raw=c.execute("SELECT record_id,record_json FROM documentary_company_record WHERE dataset_id='one' AND kind='article'").fetchone()
            record=json.loads(raw[1]);record['data'].update(recommended_sale_price='99',sale_currency='EUR')
            c.execute("UPDATE documentary_company_record SET record_json=? WHERE dataset_id='one' AND kind='article' AND record_id=?",(json.dumps(record),raw[0]))
        self.assertEqual(self.load()['preserved'],['A'])
        self.assertEqual(self.desk.store.records('one','article')[0]['data']['recommended_sale_price'],'99')

    def test_dataset_and_actor_must_be_explicit_and_real_company_is_blocked(self):
        with self.assertRaises(ValueError):load_tariff(self.path,self.file,'Actor')
        with self.assertRaises(ValueError):load_tariff(self.path,self.file,'',dataset='one')
        with sqlite3.connect(self.path) as c:
            row=c.execute("SELECT manifest_json FROM documentary_company_snapshot WHERE dataset_id='one'").fetchone()
            manifest=json.loads(row[0]);manifest['material_nature']='REAL'
            c.execute("UPDATE documentary_company_snapshot SET manifest_json=? WHERE dataset_id='one'",(json.dumps(manifest),))
        with self.assertRaises(ValueError):self.load()
