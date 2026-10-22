from copy import deepcopy
import json
import sqlite3
import unittest
from tests import test_company_sales_links as fixture
from eios.company_commercial_catalogue import CommercialCatalogue,apply_catalogue


class CommercialCatalogueTest(unittest.TestCase):
    add=fixture.SalesLinksTest.add
    financial_data=fixture.SalesLinksTest.financial_data
    set_policy=fixture.SalesLinksTest.set_policy
    setUp=fixture.SalesLinksTest.setUp
    tearDown=fixture.SalesLinksTest.tearDown

    def upload(self,body=None,**options):
        content=(body or 'sku;descripcion;proveedor;coste;precio_pvp_recomendado;estado_baja;subfama\nNEW;Nuevo;Proveedor del catálogo;44;88;False;Familia\nOFF;Baja;Otro;20;30;True;Familia\n').encode()
        state=self.desk.state('one')
        request=dict(dataset_id='one',context_fingerprint=state['documentary_context']['fingerprint'],acknowledge_synthetic_units_eur_net=True,number_format='ES',**options)
        return self.catalogue.preview(content,'catalogue.csv',request)

    def make(self):self.catalogue=CommercialCatalogue(self.path)
    def commit(self,r):return self.catalogue.commit(dict(ticket=r['ticket'],actor='Persona de prueba',reason='Catálogo ficticio revisado'))

    def test_preview_commit_orientation_and_reversal_without_rewriting_originals(self):
        self.make();before=self.desk.state('one');records=self.desk.store.records('one','article');r=self.upload()
        self.assertEqual(r['new_articles'],1);self.assertEqual(r['inactive_excluded'],1)
        self.assertEqual(len(self.desk.state('one')['articles']),1)
        self.commit(r);after=self.desk.state('one');self.assertEqual(len(after['articles']),2)
        self.assertEqual(before['inventory'],after['inventory']);self.assertEqual(before['history']['A'],after['history']['A'])
        self.assertEqual(self.desk.store.records('one','article'),records)
        self.assertNotEqual(before['documentary_context']['fingerprint'],after['documentary_context']['fingerprint'])
        ori=self.desk.sales_orientation(dict(dataset_id='one',customer_id='C',article_id='NEW'))
        self.assertEqual(ori['reference_unit_cost'],'44');self.assertEqual(ori['default_unit_price'],'88')
        self.assertIsNone(ori['inventory']);self.assertEqual(ori['purchase_references'],[])
        self.assertEqual(ori['cost_scope'],'EXPLICIT_SYNTHETIC_CATALOGUE_NOT_LAST_PURCHASE')
        offer=deepcopy(self.offer);offer['lines'][0]['article_id']='NEW';offer['context_fingerprint']=after['documentary_context']['fingerprint']
        saved=self.desk.sales_offer(offer,persist=False);self.assertEqual(saved['lines'][0]['article_id'],'NEW')
        new=next(a for a in after['articles'] if a['article_id']=='NEW')
        purchase=self.desk.save(dict(dataset_id='one',supplier_id=new['supplier_id'],article_id='NEW',reference='PURCHASE-NEW',quantity='2',unit_price='44',vat_percent='21',order_date='2026-10-01',due_date='2026-11-01',shipping_mode='NONE'))
        review=self.desk.review('one',purchase['proposal_id']);self.assertFalse(review.get('decision_authority',False))
        self.catalogue.clear(dict(dataset_id='one',context_fingerprint=after['documentary_context']['fingerprint'],actor='Persona',reason='Retirada'))
        self.assertEqual(len(self.desk.state('one')['articles']),1)
        with self.assertRaises(ValueError):self.desk.sales_offer(offer,persist=False)

    def test_idempotence_and_stale_preview(self):
        self.make();r=self.upload();self.commit(r)
        r=self.upload();self.assertEqual(self.commit(r)['status'],'UNCHANGED')
        r=self.upload();other=CommercialCatalogue(self.path)
        state=self.desk.state('one');other.clear(dict(dataset_id='one',context_fingerprint=state['documentary_context']['fingerprint'],actor='Otra',reason='Retirada'))
        with self.assertRaises(ValueError):self.commit(r)

    def test_scope_ack_duplicates_and_other_units(self):
        self.make()
        with self.assertRaises(ValueError):self.catalogue.preview(b'anything','a.csv',dict(dataset_id='one',acknowledge_synthetic_units_eur_net=False))
        body='sku;descripcion;proveedor;coste;precio_pvp_recomendado;estado_baja;subfama\nNEW;N;P;1;2;False;F\n NEW ;N;P;1;2;False;F\n'
        r=self.upload(body);self.assertIsNone(r['ticket']);self.assertEqual(r['error_count'],1)
        with sqlite3.connect(self.path) as c:
            row=c.execute("SELECT record_json FROM documentary_company_record WHERE dataset_id='one' AND kind='article'").fetchone();record=json.loads(row[0]);record['data']['unit_as_documented']='palets'
            c.execute("UPDATE documentary_company_record SET record_json=? WHERE dataset_id='one' AND kind='article'",(json.dumps(record),))
        r=self.upload('sku;descripcion;proveedor;coste;precio_pvp_recomendado;estado_baja;subfama\nA;N;P;1;2;False;F\n')
        self.assertEqual(r['error_count'],1);self.assertIsNone(r['ticket'])

    def test_context_integrity_and_original_supplier_preservation(self):
        self.make()
        with sqlite3.connect(self.path) as c:
            for kind,key,raw in c.execute("SELECT kind,record_id,record_json FROM documentary_company_record WHERE dataset_id='one' AND kind IN ('article','purchase_invoice_line')").fetchall():
                record=json.loads(raw);record['data']['unit_as_documented']='uds.'
                c.execute("UPDATE documentary_company_record SET record_json=? WHERE dataset_id='one' AND kind=? AND record_id=?",(json.dumps(record),kind,key))
        before=self.desk.state('one');original=before['articles'][0]
        r=self.upload('sku;descripcion;proveedor;coste;precio_pvp_recomendado;estado_baja;subfama\nA;Nombre alternativo;Nombre diferente;10;100;False;Familia\n')
        self.commit(r);state=self.desk.state('one');a=state['articles'][0]
        self.assertEqual(a['supplier_id'],original['supplier_id']);self.assertEqual(a.get('description'),original.get('description'))
        ori=self.desk.sales_orientation(dict(dataset_id='one',customer_id='C',article_id='A'))
        self.assertNotEqual(ori['reference_unit_cost'],'10') # Existing history has priority.
        with sqlite3.connect(self.path) as c:c.execute("UPDATE company_commercial_catalogue SET content=?",(b'changed',))
        with self.assertRaises(ValueError):self.desk.state('one')

    def test_formula_pvp_is_pending_and_default_reader_limit_is_unchanged(self):
        self.make()
        from unittest.mock import patch
        table=dict(sheet='articulos',headers=['sku','descripcion','proveedor','coste','precio_pvp_recomendado','estado_baja','subfama'],rows=[dict(row=2,values=['NEW','N','P',10,dict(formula=True),'False','F'])])
        with patch('eios.company_commercial_catalogue.read_table',return_value=table):r=self.upload()
        self.assertEqual(r['pending_prices'],1);self.commit(r)
        a=next(a for a in self.desk.state('one')['articles'] if a['article_id']=='NEW');self.assertIsNone(a['recommended_sale_price'])
        from eios.company_tables import read_table
        content=('sku\n'+'A\n'*5001).encode()
        with self.assertRaises(ValueError):read_table(content,'a.csv',delimiter=';')
        self.assertEqual(len(read_table(content,'a.csv',delimiter=';',max_rows=20000)['rows']),5001)
