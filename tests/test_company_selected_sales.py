from copy import deepcopy
import json
import sqlite3
import unittest
from tests import test_company_sales_links as fixture
from eios.company_reception import CompanyReception
from eios.company_selected_sales import SalesHistorySelection

class SelectedSalesTest(unittest.TestCase):
    add=fixture.SalesLinksTest.add
    financial_data=fixture.SalesLinksTest.financial_data
    set_policy=fixture.SalesLinksTest.set_policy
    setUp=fixture.SalesLinksTest.setUp
    tearDown=fixture.SalesLinksTest.tearDown

    def receive(self,invoice='NEW-SALE',issued='2026-09-30',sku='A',customer='C',unit='palets',quantity='10',net='800',company='one',cutoff='2026-09-30',filename='sales.csv',line='1'):
        reader=CompanyReception(self.path);content=f'Factura;Fecha;Cliente;SKU;Cantidad;Unidad;Neto;Moneda;Linea;Descripcion;Descuento;IVA\n{invoice};{issued};{customer};{sku};{quantity};{unit};{net};EUR;{line};Articulo ficticio;10;21\n'.encode();r=reader.read(content,filename)
        p=reader.preview(dict(upload=r['upload'],company_id=company,legal_name='Empresa sintética' if company=='one' else 'Otra empresa',material_nature='SYNTHETIC',as_of_date=cutoff,kind='sales_line',number_format='ES',mapping=dict(invoice_number=0,issue_date=1,customer_id=2,article_id=3,quantity=4,unit=5,net_amount=6,currency=7,line_number=8,description=9,discount_percent=10,vat_percent=11)))
        self.assertEqual(p['error_count'],0);return reader.commit(p['ticket'])['batch_id']
    def request(self,ids):return dict(dataset_id='one',batch_ids=ids,context_fingerprint=self.desk.state('one')['documentary_context']['fingerprint'])
    def commit(self,p):return self.selection.commit(dict(ticket=p['ticket'],actor='Responsable',reason='Ventas ficticias revisadas',acknowledge_references=True))
    def orientation(self):return self.desk.sales_orientation(dict(dataset_id='one',customer_id='C',article_id='A'))

    def test_explicit_selection_restores_client_history_without_posting(self):
        self.selection=SalesHistorySelection(self.path);before=self.desk.state('one');original=deepcopy(self.desk.store.records('one','sales_invoice_line'))
        bid=self.receive();p=self.selection.preview(self.request([bid]));self.assertEqual(p['sample'][0]['effective_net_unit_price'],'80')
        self.assertEqual(self.orientation()['sales_history'],[]);self.commit(p)
        after=self.desk.state('one');ori=self.orientation()
        self.assertEqual(ori['default_unit_price'],'80');self.assertEqual(ori['latest_sales'][0]['quantity'],'10')
        self.assertEqual(ori['latest_sales'][0]['discount_percent'],'10');self.assertEqual(ori['latest_sales'][0]['vat_percent'],'21')
        self.assertEqual(ori['latest_sales'][0]['source_refs'][0]['filename'],'sales.csv')
        self.assertEqual(after['inventory'],before['inventory']);self.assertEqual(after['sales'],before['sales'])
        self.assertEqual(self.desk.store.records('one','sales_invoice_line'),original)
        self.assertNotEqual(after['documentary_context']['fingerprint'],before['documentary_context']['fingerprint'])
        with self.assertRaises(ValueError):self.desk.sales_offer(self.offer,persist=False)
        self.selection.clear(dict(dataset_id='one',context_fingerprint=after['documentary_context']['fingerprint'],actor='P',reason='Retirar'))
        self.assertEqual(self.orientation()['sales_history'],[])

    def test_overlap_duplicates_and_conflicting_invoice_headers_rejected(self):
        self.selection=SalesHistorySelection(self.path)
        p=self.selection.preview(self.request([self.receive(invoice='F1')]))
        self.assertIsNone(p['ticket']);self.assertIn('ya existe',p['errors'][0]['message'])
        a=self.receive();b=self.receive(filename='copy.csv',net='900');p=self.selection.preview(self.request([a,b]))
        self.assertIsNone(p['ticket']);self.assertIn('repetida',p['errors'][0]['message'])
        b=self.receive(filename='conflict.csv',issued='2026-09-29',line='2');p=self.selection.preview(self.request([a,b]))
        self.assertIsNone(p['ticket']);self.assertIn('contradictoria',p['errors'][0]['message'])

    def test_exact_scope_and_customer_article_unit_required(self):
        self.selection=SalesHistorySelection(self.path)
        for options in (dict(company='other'),dict(cutoff='2026-10-01'),dict(unit='uds.'),dict(sku='UNKNOWN'),dict(customer='UNKNOWN')):
            with self.subTest(options=options):
                bid=self.receive(**options)
                try:p=self.selection.preview(self.request([bid]))
                except ValueError:continue
                self.assertIsNone(p['ticket']);self.assertGreater(p['error_count'],0)

    def test_tampering_disables_default_without_hidden_older_price(self):
        from eios.company_sales_links import save_link
        save_link(self.path,self.desk.store,fixture.SalesLinksTest.request(self))
        self.assertEqual(self.orientation()['default_unit_price'],'90')
        self.selection=SalesHistorySelection(self.path);bid=self.receive();p=self.selection.preview(self.request([bid]));self.commit(p)
        with sqlite3.connect(self.path) as c:c.execute('UPDATE received_company_batch SET content=? WHERE batch_id=?',(b'changed',bid))
        ori=self.orientation();self.assertEqual(ori['sales_history_status']['status'],'STALE');self.assertEqual(ori['sales_history'],[])
        self.assertIsNone(ori['default_unit_price']);self.assertEqual(ori['default_price_source'],'STALE_RECEIVED_SALES_HISTORY')
        self.selection.clear(dict(dataset_id='one',context_fingerprint=self.desk.state('one')['documentary_context']['fingerprint'],actor='P',reason='Retirar origen modificado'))
        self.assertEqual(self.orientation()['default_unit_price'],'90')

    def test_same_day_prices_are_ambiguous_not_averaged(self):
        self.selection=SalesHistorySelection(self.path);a=self.receive();b=self.receive(invoice='NEW-2',net='900')
        self.commit(self.selection.preview(self.request([a,b])))
        ori=self.orientation();self.assertIsNone(ori['default_unit_price']);self.assertEqual(ori['default_price_source'],'AMBIGUOUS_HISTORY');self.assertEqual(len(ori['latest_sales']),2)

    def test_expiry_ack_idempotence_and_changed_source_block_commit(self):
        clock=[0];self.selection=SalesHistorySelection(self.path,clock=lambda:clock[0]);bid=self.receive();p=self.selection.preview(self.request([bid]))
        with self.assertRaises(ValueError):self.selection.commit(dict(ticket=p['ticket'],actor='P',reason='R',acknowledge_references=False))
        clock[0]=601
        with self.assertRaises(ValueError):self.commit(p)
        p=self.selection.preview(self.request([bid]));self.commit(p);p=self.selection.preview(self.request([bid]));self.assertEqual(self.commit(p)['status'],'UNCHANGED')
        p=self.selection.preview(self.request([bid]))
        with sqlite3.connect(self.path) as c:c.execute('UPDATE received_company_batch SET content=? WHERE batch_id=?',(b'changed',bid))
        with self.assertRaises(ValueError):self.commit(p)
    def test_customer_history_is_not_shared_and_new_catalogue_skus_are_supported(self):
        self.add('customer','C2',dict(customer_id='C2',legal_name='Otro cliente'))
        self.selection=SalesHistorySelection(self.path);p=self.selection.preview(self.request([self.receive(customer='C2')]))
        self.commit(p);self.assertEqual(self.orientation()['sales_history'],[])
        other=self.desk.sales_orientation(dict(dataset_id='one',customer_id='C2',article_id='A'))
        self.assertEqual(other['default_unit_price'],'80')
        from eios.company_commercial_catalogue import CommercialCatalogue
        cat=CommercialCatalogue(self.path);state=self.desk.state('one')
        p=cat.preview(b'sku;descripcion;proveedor;coste;precio_pvp_recomendado;estado_baja;subfama\nNEW;Nuevo;Proveedor catalogo;10;20;False;Familia\n','catalogue.csv',dict(dataset_id='one',context_fingerprint=state['documentary_context']['fingerprint'],acknowledge_synthetic_units_eur_net=True,number_format='ES'))
        cat.commit(dict(ticket=p['ticket'],actor='P',reason='Catalogo'))
        p=self.selection.preview(self.request([self.receive(sku='NEW',unit='uds.',net='120',quantity='10')]))
        self.commit(p);ori=self.desk.sales_orientation(dict(dataset_id='one',customer_id='C',article_id='NEW'))
        self.assertEqual(ori['default_unit_price'],'12');self.assertEqual(ori['reference_unit_cost'],'10');self.assertIsNone(ori['inventory'])
