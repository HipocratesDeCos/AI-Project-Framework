from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
from zipfile import ZipFile

from eios.company_dossier_export import export_version
from eios.company_dossier_versions import save_version,version
from eios.company_reception import CompanyReception,canonical


class DossierExportTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db=Path(self.tmp.name)/'company.db'
        self.reception=CompanyReception(self.db)
        self.ids=[]
        self.contents={}
        self.add('S1')

    def add(self,identifier,company='A',filename='suppliers.csv'):
        content=('Codigo;Nombre\r\n'+identifier+';Proveedor español\r\n').encode('utf-8-sig')
        uploaded=self.reception.read(content,filename,delimiter=';')
        checked=self.reception.preview(dict(upload=uploaded['upload'],company_id=company,legal_name='Empresa '+company,material_nature='REAL',as_of_date='2026-09-30',kind='supplier',number_format='ES',mapping=dict(supplier_id=0,legal_name=1)))
        bid=self.reception.commit(checked['ticket'])['batch_id']
        self.ids.append(bid);self.contents[bid]=content

    def save(self,name='Recepción inicial'):
        return save_version(self.db,self.ids,name)['dossier_id']

    def test_complete_exact_archive_and_no_database_changes(self):
        identifier=self.save()
        saved=version(self.db,identifier)
        before=self.db.read_bytes()
        exported=export_version(self.db,identifier)
        self.assertEqual(before,self.db.read_bytes())
        self.assertTrue(exported['filename'].endswith('.zip'))
        with ZipFile(BytesIO(exported['content'])) as archive:
            self.assertEqual(len(archive.namelist()),4)
            package=json.loads(archive.read('expediente_manifest.json'))
            check=json.loads(archive.read('comprobacion_referencias.json'))
            self.assertEqual(package['manifest'],saved['manifest'])
            self.assertEqual(check,saved['check'])
            self.assertEqual(sha256(canonical(check).encode()).hexdigest(),package['manifest']['check_sha256'])
            self.assertEqual(sha256(canonical(package['manifest']).encode()).hexdigest(),identifier)
            item=package['files'][0]
            self.assertEqual(archive.read(item['path']),self.contents[item['batch_id']])
            self.assertEqual(sha256(archive.read(item['path'])).hexdigest(),item['source_sha256'])
            html=archive.read('indice.html').decode()
            self.assertIn('PENDIENTE DE ADMISIÓN',html)
            self.assertIn('Proveedores',html)
            self.assertFalse(package['decision_authority'])
            self.assertEqual(package['operational_path'],'FORBIDDEN')

    def test_duplicate_filenames_are_unique_and_exclude_other_company(self):
        self.add('S2')
        identifier=self.save()
        self.add('OTHER',company='B')
        with ZipFile(BytesIO(export_version(self.db,identifier)['content'])) as archive:
            package=json.loads(archive.read('expediente_manifest.json'))
            paths=[item['path'] for item in package['files']]
            self.assertEqual(len(set(paths)),2)
            self.assertEqual(len(paths),2)
            for item in package['files']:
                self.assertNotIn(b'OTHER',archive.read(item['path']))

    def test_html_escaped_and_archive_paths_safe(self):
        self.add('S2',filename='proveedor<bad>:name.csv')
        identifier=self.save('<script>alert(1)</script>')
        with ZipFile(BytesIO(export_version(self.db,identifier)['content'])) as archive:
            html=archive.read('indice.html').decode()
            self.assertNotIn('<script>',html)
            self.assertIn('&lt;script&gt;',html)
            self.assertIn('proveedor&lt;bad&gt;:name.csv',html)
            for name in archive.namelist():
                self.assertFalse(name.startswith('/'))
                self.assertNotIn('..',Path(name).parts)
                self.assertNotIn(':',name)
                self.assertNotIn('<',name)

    def test_corrupted_original_blocks_export(self):
        identifier=self.save()
        with sqlite3.connect(self.db) as c:
            c.execute('UPDATE received_company_batch SET content=?',(b'changed',))
        with self.assertRaisesRegex(ValueError,'integridad'):
            export_version(self.db,identifier)

    def test_changed_original_metadata_hash_does_not_bypass_saved_hash(self):
        identifier=self.save()
        with sqlite3.connect(self.db) as c:
            metadata=json.loads(c.execute('SELECT metadata_json FROM received_company_batch').fetchone()[0])
            metadata['source_sha256']=sha256(b'changed').hexdigest()
            c.execute('UPDATE received_company_batch SET content=?,metadata_json=?',(b'changed',json.dumps(metadata)))
        with self.assertRaisesRegex(ValueError,'versión guardada'):
            export_version(self.db,identifier)

    def test_limit_and_unavailable_version_rejected(self):
        identifier=self.save()
        with patch('eios.company_dossier_export.MAX_EXPORT_BYTES',1):
            with self.assertRaisesRegex(ValueError,'límite'):
                export_version(self.db,identifier)
        with self.assertRaises(ValueError):export_version(self.db,'x'*64)
