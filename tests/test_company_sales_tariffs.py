from copy import deepcopy
import json
import sqlite3
import unittest
from tests import test_company_sales_negotiation as fixture
from eios.company_reception import CompanyReception
from eios.company_sales_tariffs import save_tariff
from eios.company_tables import normalize,read_table


class SalesTariffTest(unittest.TestCase):
    add=fixture.SalesNegotiationTest.add
    financial_data=fixture.SalesNegotiationTest.financial_data
    set_policy=fixture.SalesNegotiationTest.set_policy
    tearDown=fixture.SalesNegotiationTest.tearDown

    def setUp(self):
        fixture.SalesNegotiationTest.setUp(self)
        self.batch=self.upload()

    def upload(self,sku='A',unit='palets',price='80,00',currency='EUR',company='one',name='Empresa sintética'):
        reception=CompanyReception(self.path)
        data=f'SKU;Unidad;PVP;Moneda;Desde;Hasta\n{sku};{unit};{price};{currency};01/10/2026;31/12/2026\n'.encode()
        upload=reception.read(data,'tarifa.csv',delimiter=';')
        checked=reception.preview(dict(upload=upload['upload'],company_id=company,legal_name=name,material_nature='SYNTHETIC',as_of_date='2026-09-30',kind='sale_price',number_format='ES',mapping=dict(zip(['article_id','unit','recommended_sale_price','currency','valid_from','valid_until'],range(6)))))
        self.assertEqual(checked['error_count'],0)
        return reception.commit(checked['ticket'])['batch_id']

    def request(self,**patch):
        return dict(dict(dataset_id='one',article_id='A',context_fingerprint=self.desk.state('one')['documentary_context']['fingerprint'],batch_id=self.batch,source_row=2,source_fingerprint=next(r['source_fingerprint'] for r in self.orientation()['tariff_candidates'] if r['batch_id']==self.batch),actor='Responsable sintético',reason='Tarifa de prueba seleccionada',acknowledge_net_unit=True),**patch)

    def orientation(self,**patch):
        return self.desk.sales_orientation(dict(dict(dataset_id='one',article_id='A',customer_id='C',offer_date='2026-10-22'),**patch))

    def test_tariff_keeps_source_exact_price_margin_and_customer_history_precedence(self):
        r=save_tariff(self.path,self.request());self.assertFalse(r['decision_authority'])
        o=self.orientation();p=o['price_reference']
        self.assertEqual(p['recommended_unit_price'],'80.00')
        self.assertEqual(p['recommended_margin_percent'],'37.50')
        self.assertEqual(p['price_source'],'EXPLICIT_RECEIVED_TARIFF')
        self.assertEqual(p['tariff_reference']['selection']['source_row'],2)
        self.assertEqual(p['tariff_reference']['admission_status'],'PENDING')
        self.assertEqual(o['default_unit_price'],'90')
        self.assertEqual(self.orientation(customer_id='')['default_unit_price'],'80.00')
        saved=self.desk.sales_offer(dict(self.offer,context_fingerprint=self.desk.state('one')['documentary_context']['fingerprint']))
        self.assertEqual(saved['negotiation']['origin_prices'][0]['tariff_reference']['selection']['batch_id'],self.batch)
        save_tariff(self.path,self.request(clear=True))
        self.assertEqual(self.desk.state('one')['sales_proposals'][0],saved)
        self.assertEqual(self.orientation()['price_reference']['price_source'],'CALCULATED_FROM_PREPARED_TARGET')

    def test_invalid_date_or_expiry_does_not_fall_back_to_a_calculated_pvp(self):
        save_tariff(self.path,self.request())
        for when in ('2026-09-30','2027-01-01','invalid',None):
            with self.subTest(when=when):
                p=self.orientation(offer_date=when)['price_reference']
                self.assertIsNone(p['recommended_unit_price'])
                self.assertIn(p['price_source'],('RECEIVED_TARIFF_DATE_REQUIRED','RECEIVED_TARIFF_OUTSIDE_VALIDITY'))
        for when in ('2026-10-01','2026-12-31'):self.assertEqual(self.orientation(offer_date=when)['price_reference']['recommended_unit_price'],'80.00')

    def test_source_change_invalidates_tariff_context_and_old_evaluation(self):
        save_tariff(self.path,self.request());old=self.desk.state('one')['documentary_context']['fingerprint']
        with sqlite3.connect(self.path) as c:c.execute('UPDATE received_company_batch SET content=? WHERE batch_id=?',(b'changed',self.batch))
        p=self.orientation()['price_reference'];self.assertEqual(p['price_source'],'RECEIVED_TARIFF_STALE');self.assertIsNone(p['recommended_unit_price'])
        self.assertNotEqual(self.desk.state('one')['documentary_context']['fingerprint'],old)
        with self.assertRaises(ValueError):self.desk.sales_offer(dict(self.offer,context_fingerprint=old),persist=False)

    def test_wrong_unit_currency_sku_company_or_missing_ack_rejected(self):
        for kwargs in (dict(unit='uds.'),dict(currency='USD'),dict(sku='B'),dict(company='other')):
            batch=self.upload(**kwargs)
            with self.subTest(kwargs=kwargs),self.assertRaises(ValueError):save_tariff(self.path,self.request(batch_id=batch))
        for patch in (dict(acknowledge_net_unit=False),dict(actor=''),dict(reason=''),dict(source_row=True),dict(context_fingerprint='old'),dict(source_fingerprint='old')):
            with self.subTest(patch=patch),self.assertRaises(ValueError):save_tariff(self.path,self.request(**patch))

    def test_concurrent_selection_requires_current_context_and_preserves_revisions(self):
        request=self.request();save_tariff(self.path,request)
        with self.assertRaises(ValueError):save_tariff(self.path,request)
        save_tariff(self.path,self.request(clear=True))
        with sqlite3.connect(self.path) as c:self.assertEqual(c.execute('SELECT COUNT(*) FROM company_sales_tariff').fetchone()[0],2)

    def test_upload_rejects_negative_price_and_reversed_dates(self):
        mapping=dict(zip(['article_id','unit','recommended_sale_price','currency','valid_from','valid_until'],range(6)))
        for row in ('A;palets;-1;EUR;01/10/2026;31/12/2026','A;palets;80;EUR;31/12/2026;01/10/2026','A;palets;=1+1;EUR;01/10/2026;31/12/2026'):
            table=read_table(('SKU;Unidad;PVP;Moneda;Desde;Hasta\n'+row+'\n').encode(),'t.csv',delimiter=';')
            self.assertEqual(normalize(table,'sale_price',mapping,'2026-09-30','ES')['error_count'],1)
