import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

from eios.company_reception import CompanyReception
from eios.company_dossier_versions import save_version,version,versions


class DossierVersionsTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db=Path(self.tmp.name)/'company.db'
        self.reception=CompanyReception(self.db)
        self.ids=[]
        self.add_supplier('S1')

    def add_supplier(self,supplier,company='A',cutoff='2026-09-30'):
        file=self.reception.read(('Codigo;Nombre\n'+supplier+';Proveedor\n').encode(),'suppliers.csv',delimiter=';')
        report=self.reception.preview(dict(upload=file['upload'],company_id=company,legal_name='Empresa '+company,material_nature='REAL',as_of_date=cutoff,kind='supplier',number_format='ES',mapping=dict(supplier_id=0,legal_name=1)))
        self.ids.append(self.reception.commit(report['ticket'])['batch_id'])

    def test_persist_and_reopen_without_admission_or_source_change(self):
        with sqlite3.connect(self.db) as c:
            before=c.execute('SELECT * FROM received_company_batch').fetchall()
        result=save_version(self.db,self.ids,'Recepción inicial')
        report=version(self.db,result['dossier_id'])
        self.assertEqual(report['name'],'Recepción inicial')
        self.assertEqual(report['manifest']['batch_ids'],self.ids)
        self.assertEqual(report['manifest']['files'][0]['filename'],'suppliers.csv')
        self.assertEqual(report['check']['check_schema'],'EIOS-RECEIVED-REFERENCE-CHECK-01/v0.1')
        self.assertEqual(report['manifest']['admission_status'],'PENDING')
        self.assertEqual(report['manifest']['operational_path'],'FORBIDDEN')
        self.assertFalse(report['manifest']['decision_authority'])
        self.assertEqual(versions(self.db)[0]['dossier_id'],result['dossier_id'])
        with sqlite3.connect(self.db) as c:
            self.assertEqual(c.execute('SELECT * FROM received_company_batch').fetchall(),before)
            tables={row[0] for row in c.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        self.assertNotIn('documentary_company_snapshot',tables)
        self.assertNotIn('manual_purchase_proposal',tables)

    def test_same_selection_is_idempotent_and_keeps_original_name_and_check(self):
        self.add_supplier('S2')
        first=save_version(self.db,self.ids,'Primera')
        before=self.db.read_bytes()
        second=save_version(self.db,list(reversed(self.ids)),'Otro nombre')
        self.assertEqual(second['status'],'UNCHANGED')
        self.assertEqual(second['name'],'Primera')
        self.assertEqual(second['created_at'],first['created_at'])
        self.assertEqual(second['dossier_id'],first['dossier_id'])
        self.assertEqual(self.db.read_bytes(),before)
        self.assertEqual(len(versions(self.db)),1)

    def test_name_cannot_overwrite_different_selection(self):
        first=save_version(self.db,self.ids,'V1')
        self.add_supplier('S2')
        with self.assertRaisesRegex(ValueError,'otra selección'):
            save_version(self.db,self.ids,'V1')
        second=save_version(self.db,self.ids,'V2')
        self.assertNotEqual(first['dossier_id'],second['dossier_id'])
        self.assertEqual(len(versions(self.db)),2)
        self.assertEqual(len(version(self.db,first['dossier_id'])['manifest']['batch_ids']),1)
        self.assertEqual(len(version(self.db,second['dossier_id'])['manifest']['batch_ids']),2)

    def test_incomplete_selection_keeps_issues(self):
        file=self.reception.read(b'Sku;Nombre;Unidad;Proveedor\nA1;Articulo;uds;MISSING\n','article.csv',delimiter=';')
        checked=self.reception.preview(dict(upload=file['upload'],company_id='A',legal_name='Empresa A',material_nature='REAL',as_of_date='2026-09-30',kind='article',number_format='ES',mapping=dict(article_id=0,description=1,unit=2,supplier_id=3)))
        bid=self.reception.commit(checked['ticket'])['batch_id']
        saved=save_version(self.db,[bid],'Pendiente proveedor')
        report=version(self.db,saved['dossier_id'])
        self.assertEqual(report['check']['issues'][0]['code'],'MISSING_REFERENCE')
        self.assertEqual(versions(self.db)[0]['issue_count'],1)
        self.assertFalse(report['manifest']['decision_authority'])

    def test_read_only_listing_retrieval_and_corrupt_check_rejected(self):
        saved=save_version(self.db,self.ids,'V1')
        before=self.db.read_bytes()
        versions(self.db);version(self.db,saved['dossier_id'])
        self.assertEqual(self.db.read_bytes(),before)
        with sqlite3.connect(self.db) as c:
            c.execute("UPDATE received_company_dossier SET check_json='{}'")
        with self.assertRaisesRegex(ValueError,'integridad'):
            version(self.db,saved['dossier_id'])

    def test_invalid_selection_name_and_unavailable_version(self):
        self.assertEqual(versions(self.db),[])
        for name in ['', ' '*5, 'a'*121, 'line\nbreak', 1]:
            with self.assertRaises(ValueError):save_version(self.db,self.ids,name)
        with self.assertRaises(ValueError):save_version(self.db,[],'V1')
        with self.assertRaises(ValueError):version(self.db,'a'*64)
        self.add_supplier('S2',company='B')
        with self.assertRaises(ValueError):save_version(self.db,self.ids,'Mixta')
        self.assertEqual(versions(self.db),[])
