from copy import deepcopy
import json
import sqlite3
import unittest
from tests import test_company_sales_links as fixture
from eios.company_reception import CompanyReception
from eios.company_selected_inventory import InventorySelection


class SelectedInventoryTest(unittest.TestCase):
    add=fixture.SalesLinksTest.add
    financial_data=fixture.SalesLinksTest.financial_data
    set_policy=fixture.SalesLinksTest.set_policy
    setUp=fixture.SalesLinksTest.setUp
    tearDown=fixture.SalesLinksTest.tearDown

    def receive(self,sku='A',unit='palets',physical='10',reserved='2',company='one',cutoff='2026-09-30',name='Empresa sintética',nature='SYNTHETIC'):
        reader=CompanyReception(self.path)
        raw=f'SKU;Unidad;Fisico;Reservado\n{sku};{unit};{physical};{reserved}\n'.encode()
        read=reader.read(raw,'stock-'+sku+'-'+physical+'.csv')
        checked=reader.preview(dict(upload=read['upload'],company_id=company,legal_name=name,material_nature=nature,as_of_date=cutoff,kind='inventory',number_format='ES',mapping=dict(article_id=0,unit=1,physical=2,reserved=3)))
        self.assertEqual(checked['error_count'],0)
        return reader.commit(checked['ticket'])['batch_id']

    def request(self,ids):return dict(dataset_id='one',context_fingerprint=self.desk.state('one')['documentary_context']['fingerprint'],batch_ids=ids)
    def commit(self,preview):return self.selection.commit(dict(ticket=preview['ticket'],actor='Responsable',reason='Inventario ficticio revisado',acknowledge_dated_reference=True))

    def test_receive_preview_select_proposal_snapshot_and_clear(self):
        self.selection=InventorySelection(self.path);before=self.desk.state('one');bid=self.receive()
        preview=self.selection.preview(self.request([bid]));self.assertEqual(preview['sample'][0]['previous_available'],2)
        self.assertEqual(preview['sample'][0]['available'],'8');self.assertEqual(self.desk.state('one')['inventory'],before['inventory'])
        self.commit(preview);after=self.desk.state('one');stock=after['inventory']['A'];self.assertEqual(stock['available'],'8');self.assertEqual(stock['source_ref']['source_row'],2)
        self.assertEqual(after['sales'],before['sales']);self.assertEqual(after['history'],before['history'])
        self.assertNotEqual(after['documentary_context']['fingerprint'],before['documentary_context']['fingerprint'])
        stale=deepcopy(self.offer)
        with self.assertRaises(ValueError):self.desk.sales_offer(stale,persist=False)
        offer=dict(self.offer,context_fingerprint=after['documentary_context']['fingerprint']);saved=self.desk.sales_offer(offer)
        self.assertEqual(saved['lines'][0]['orientation']['inventory']['available'],'8')
        self.selection.clear(dict(dataset_id='one',context_fingerprint=after['documentary_context']['fingerprint'],actor='Responsable',reason='Retirada'))
        self.assertEqual(self.desk.state('one')['inventory'],before['inventory']);self.assertEqual(self.desk.state('one')['sales_proposals'][0],saved)

    def test_scope_units_unknown_skus_and_duplicate_parts_rejected(self):
        self.selection=InventorySelection(self.path)
        for bid in [self.receive(company='foreign',name='Otra'),self.receive(cutoff='2026-10-01'),self.receive(unit='uds.'),self.receive(sku='UNKNOWN')]:
            with self.subTest(bid=bid):
                try:p=self.selection.preview(self.request([bid]))
                except ValueError:continue
                self.assertIsNone(p['ticket']);self.assertGreater(p['error_count'],0)
        a=self.receive();b=self.receive(physical='20')
        p=self.selection.preview(self.request([a,b]));self.assertEqual(p['error_count'],1);self.assertIsNone(p['ticket'])

    def test_unknown_reservations_do_not_become_zero_and_idempotence(self):
        self.selection=InventorySelection(self.path);bid=self.receive(reserved='');p=self.selection.preview(self.request([bid]));self.assertEqual(p['unknown_reservations'],1)
        self.commit(p);stock=self.desk.state('one')['inventory']['A'];self.assertIsNone(stock['reserved']);self.assertIsNone(stock['available'])
        p=self.selection.preview(self.request([bid]));self.assertEqual(self.commit(p)['status'],'UNCHANGED')
        with sqlite3.connect(self.path) as c:self.assertEqual(c.execute('SELECT COUNT(*) FROM company_inventory_selection').fetchone()[0],1)

    def test_source_change_blocks_commit_and_selected_quantities_fail_closed(self):
        self.selection=InventorySelection(self.path);bid=self.receive();p=self.selection.preview(self.request([bid]))
        with sqlite3.connect(self.path) as c:c.execute('UPDATE received_company_batch SET content=? WHERE batch_id=?',(b'changed',bid))
        with self.assertRaises(ValueError):self.commit(p)
        bid=self.receive(physical='11');p=self.selection.preview(self.request([bid]));self.commit(p)
        with sqlite3.connect(self.path) as c:c.execute('UPDATE received_company_batch SET content=? WHERE batch_id=?',(b'changed-again',bid))
        state=self.desk.state('one');self.assertEqual(state['selected_inventory']['status'],'STALE');self.assertEqual(state['inventory'],{})
        self.selection.clear(dict(dataset_id='one',context_fingerprint=state['documentary_context']['fingerprint'],actor='Persona',reason='Origen no disponible'))
        self.assertEqual(self.desk.state('one')['inventory']['A']['available'],2)

    def test_replacing_selection_ttl_ack_and_prior_planning_not_reused(self):
        clock=[0];self.selection=InventorySelection(self.path,clock=lambda:clock[0]);bid=self.receive()
        p=self.selection.preview(self.request([bid]))
        with self.assertRaises(ValueError):self.selection.commit(dict(ticket=p['ticket'],actor='A',reason='R',acknowledge_dated_reference=False))
        clock[0]=601
        with self.assertRaises(ValueError):self.commit(p)
        p=self.selection.preview(self.request([bid]));self.commit(p)
        with sqlite3.connect(self.path) as c:
            c.execute('CREATE TABLE IF NOT EXISTS synthetic_article_planning(dataset_id TEXT,article_id TEXT,payload TEXT)')
            c.execute('INSERT INTO synthetic_article_planning VALUES(?,?,?)',('one','A',json.dumps(dict(article_id='A',unit='palets'))))
        self.assertEqual(self.desk.state('one')['planning']['A']['status'],'MISSING_DATA')
        from eios.company_commercial_catalogue import CommercialCatalogue
        cat=CommercialCatalogue(self.path);state=self.desk.state('one')
        preview=cat.preview(b'sku;descripcion;proveedor;coste;precio_pvp_recomendado;estado_baja;subfama\nNEW;Nuevo;Proveedor;10;20;False;Familia\n','catalogue.csv',dict(dataset_id='one',context_fingerprint=state['documentary_context']['fingerprint'],acknowledge_synthetic_units_eur_net=True,number_format='ES'))
        cat.commit(dict(ticket=preview['ticket'],actor='Persona',reason='Alta de ficha'))
        new=self.receive(sku='NEW',unit='uds.',physical='5',reserved='2')
        p=self.selection.preview(self.request([bid,new]));self.assertEqual(p['article_count'],2);self.commit(p)
        self.assertEqual(self.desk.state('one')['inventory']['NEW']['available'],'3')
        p=self.selection.preview(self.request([new]));self.assertEqual(p['reverted_articles'],1);self.commit(p)
        state=self.desk.state('one');self.assertEqual(state['inventory']['A']['available'],2)
        self.assertEqual(state['inventory']['NEW']['available'],'3')

