from copy import deepcopy
import json
import sqlite3
import unittest
from tests import test_company_sales_links as fixture
from eios.company_reception import CompanyReception
from eios.company_selected_purchases import PurchaseHistorySelection


class SelectedPurchasesTest(unittest.TestCase):
    add=fixture.SalesLinksTest.add
    financial_data=fixture.SalesLinksTest.financial_data
    set_policy=fixture.SalesLinksTest.set_policy
    setUp=fixture.SalesLinksTest.setUp
    tearDown=fixture.SalesLinksTest.tearDown

    def receive(self,invoice='NEW-1',issued='2026-09-30',sku='A',supplier='S',unit='palets',quantity='10',net='700',company='one',cutoff='2026-09-30',filename='purchases.csv'):
        reader=CompanyReception(self.path);content=f'Factura;Fecha;Proveedor;SKU;Cantidad;Unidad;Neto;Moneda\n{invoice};{issued};{supplier};{sku};{quantity};{unit};{net};EUR\n'.encode();r=reader.read(content,filename)
        p=reader.preview(dict(upload=r['upload'],company_id=company,legal_name='Empresa sintética' if company=='one' else 'Otra empresa',material_nature='SYNTHETIC',as_of_date=cutoff,kind='purchase_line',number_format='ES',mapping=dict(invoice_number=0,issue_date=1,supplier_id=2,article_id=3,quantity=4,unit=5,net_amount=6,currency=7)))
        self.assertEqual(p['error_count'],0);return reader.commit(p['ticket'])['batch_id']
    def request(self,ids):return dict(dataset_id='one',batch_ids=ids,context_fingerprint=self.desk.state('one')['documentary_context']['fingerprint'])
    def commit(self,p):return self.selection.commit(dict(ticket=p['ticket'],actor='Responsable',reason='Compras ficticias revisadas',acknowledge_references=True))

    def test_selection_changes_last_cost_quantity_and_minimum_without_posting(self):
        self.selection=PurchaseHistorySelection(self.path);before=self.desk.state('one');original=self.desk.store.records('one','purchase_invoice_line');bid=self.receive();p=self.selection.preview(self.request([bid]))
        self.assertEqual(p['sample'][0]['effective_net_unit_price'],'70');self.assertEqual(self.desk.state('one')['history'],before['history'])
        self.commit(p);after=self.desk.state('one');self.assertEqual(after['history']['A'][0]['quantity'],'10');self.assertEqual(after['history']['A'][0]['effective_net_unit_price'],'70')
        self.assertEqual(after['inventory'],before['inventory']);self.assertEqual(self.desk.store.records('one','purchase_invoice_line'),original)
        self.assertEqual(after['stock_minimums']['A']['automatic']['quantity'],'10')
        ori=self.desk.sales_orientation(dict(dataset_id='one',customer_id='C',article_id='A'));self.assertEqual(ori['reference_unit_cost'],'70');self.assertEqual(ori['cost_scope'],'SELECTED_RECEIVED_PURCHASE_LINES_NOT_ADMITTED')
        with self.assertRaises(ValueError):self.desk.sales_offer(self.offer,persist=False)
        offer=dict(self.offer,context_fingerprint=after['documentary_context']['fingerprint']);saved=self.desk.sales_offer(offer)
        self.selection.clear(dict(dataset_id='one',context_fingerprint=after['documentary_context']['fingerprint'],actor='Persona',reason='Retirada'))
        self.assertEqual(self.desk.state('one')['history'],before['history']);self.assertEqual(self.desk.state('one')['sales_proposals'][0],saved)

    def test_original_invoice_overlap_duplicate_lines_and_header_conflicts(self):
        self.selection=PurchaseHistorySelection(self.path)
        p=self.selection.preview(self.request([self.receive(invoice='P1')]))
        self.assertIsNone(p['ticket']);self.assertIn('ya existe',p['errors'][0]['message'])
        a=self.receive();b=self.receive(filename='copy.csv');p=self.selection.preview(self.request([a,b]));self.assertIsNone(p['ticket']);self.assertIn('repetida',p['errors'][0]['message'])
        b=self.receive(issued='2026-09-29',filename='different-date.csv');p=self.selection.preview(self.request([a,b]));self.assertIsNone(p['ticket']);self.assertIn('contradictoria',p['errors'][0]['message'])

    def test_scope_unit_unknown_supplier_and_non_primary_supplier(self):
        self.selection=PurchaseHistorySelection(self.path)
        for options in (dict(company='other'),dict(cutoff='2026-10-01'),dict(unit='uds.'),dict(sku='UNKNOWN'),dict(supplier='UNKNOWN')):
            bid=self.receive(**options)
            try:p=self.selection.preview(self.request([bid]))
            except ValueError:continue
            self.assertIsNone(p['ticket']);self.assertGreater(p['error_count'],0)
        self.add('supplier','S2',dict(supplier_id='S2',legal_name='Otro proveedor'))
        p=self.selection.preview(self.request([self.receive(supplier='S2')]))
        self.assertEqual(p['non_primary_supplier_lines'],1);self.commit(p)
        self.assertEqual(self.desk.sales_orientation(dict(dataset_id='one',customer_id='C',article_id='A'))['reference_unit_cost'],'50')
        state=self.desk.state('one');self.assertEqual(len(state['received_purchase_lines']),1)
        self.assertIn('S2',{s['supplier_id'] for s in state['stock_metrics']['A']['suppliers']})

    def test_changed_source_stales_references_and_blocks_commit_without_fallback(self):
        self.selection=PurchaseHistorySelection(self.path);bid=self.receive();p=self.selection.preview(self.request([bid]))
        with sqlite3.connect(self.path) as c:c.execute('UPDATE received_company_batch SET content=? WHERE batch_id=?',(b'changed',bid))
        with self.assertRaises(ValueError):self.commit(p)
        bid=self.receive(filename='valid.csv');p=self.selection.preview(self.request([bid]));self.commit(p)
        with sqlite3.connect(self.path) as c:c.execute('UPDATE received_company_batch SET content=? WHERE batch_id=?',(b'changed',bid))
        state=self.desk.state('one');self.assertEqual(state['selected_purchase_history']['status'],'STALE');self.assertEqual(state['history']['A'],[])
        self.assertIsNone(self.desk.sales_orientation(dict(dataset_id='one',customer_id='C',article_id='A'))['reference_unit_cost'])
        self.selection.clear(dict(dataset_id='one',context_fingerprint=state['documentary_context']['fingerprint'],actor='P',reason='Retirar origen modificado'))
        self.assertEqual(self.desk.sales_orientation(dict(dataset_id='one',customer_id='C',article_id='A'))['reference_unit_cost'],'50')

    def test_ambiguity_idempotence_ack_expiry_and_catalogue_article(self):
        clock=[0];self.selection=PurchaseHistorySelection(self.path,clock=lambda:clock[0]);a=self.receive();p=self.selection.preview(self.request([a]))
        with self.assertRaises(ValueError):self.selection.commit(dict(ticket=p['ticket'],actor='P',reason='R',acknowledge_references=False))
        clock[0]=601
        with self.assertRaises(ValueError):self.commit(p)
        p=self.selection.preview(self.request([a]));self.commit(p);p=self.selection.preview(self.request([a]));self.assertEqual(self.commit(p)['status'],'UNCHANGED')
        b=self.receive(invoice='NEW-2',net='800');p=self.selection.preview(self.request([a,b]));self.commit(p)
        self.assertIsNone(self.desk.sales_orientation(dict(dataset_id='one',customer_id='C',article_id='A'))['reference_unit_cost'])
        from eios.company_commercial_catalogue import CommercialCatalogue
        cat=CommercialCatalogue(self.path);state=self.desk.state('one');p=cat.preview(b'sku;descripcion;proveedor;coste;precio_pvp_recomendado;estado_baja;subfama\nNEW;Nuevo;Proveedor catalogo;10;20;False;Familia\n','catalogue.csv',dict(dataset_id='one',context_fingerprint=state['documentary_context']['fingerprint'],acknowledge_synthetic_units_eur_net=True,number_format='ES'));cat.commit(dict(ticket=p['ticket'],actor='P',reason='Catalogo'))
        article=next(a for a in self.desk.state('one')['articles'] if a['article_id']=='NEW')
        p=self.selection.preview(self.request([self.receive(invoice='NEW-3',sku='NEW',supplier=article['supplier_id'],unit='uds.',net='120',quantity='10')]))
        self.commit(p);ori=self.desk.sales_orientation(dict(dataset_id='one',customer_id='C',article_id='NEW'));self.assertEqual(ori['reference_unit_cost'],'12');self.assertIsNone(ori['inventory'])
