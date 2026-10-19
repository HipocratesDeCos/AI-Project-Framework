from io import BytesIO
import json
from pathlib import Path
import sqlite3
import unittest
from unittest.mock import patch
import zipfile

from eios.company_upload import PreparedCompanyImport
from tests import test_company_documentary_intake as intake_fixture


class PreparedUploadTest(unittest.TestCase):
    def setUp(self):
        self.fixture=intake_fixture.CompanyIntakeTests()
        self.fixture.setUp()
        self.now=0
        self.upload=PreparedCompanyImport(self.fixture.store,clock=lambda:self.now)

    def tearDown(self):
        self.fixture.tearDown()

    def package(self):
        def usable(rows):
            rows[2]['data'].update(article_id='SKU',supplier_id='SUP',description='Article',unit_as_documented='uds.')
            rows.append(dict(kind='supplier',record_id='SUP',data=dict(supplier_id='SUP',legal_name='Supplier'),source_refs=[dict(document_ref='DOC')]))
        return self.fixture.package(usable).read_bytes()

    def change_manifest(self,content,field,value):
        result=BytesIO()
        with zipfile.ZipFile(BytesIO(content)) as source,zipfile.ZipFile(result,'w') as target:
            for name in source.namelist():
                data=source.read(name)
                if name=='company_manifest.json':
                    manifest=json.loads(data);manifest[field]=value;data=json.dumps(manifest).encode()
                target.writestr(name,data)
        return result.getvalue()

    def test_preview_has_no_database_write_commit_is_exact_and_idempotent(self):
        content=self.package()
        preview=self.upload.preview(content)
        self.assertFalse(self.fixture.db.exists())
        self.assertEqual(preview['documents'],1)
        self.assertEqual(preview['records'],5)
        result=self.upload.commit(preview['ticket'])
        self.assertEqual(result['status'],'IMPORTED')
        self.assertEqual(result['dataset_id'],preview['dataset_id'])
        self.assertEqual(self.fixture.store.document(result['dataset_id'],'DOC'),b'synthetic source')
        with self.assertRaises(ValueError):
            self.upload.commit(preview['ticket'])
        second=self.upload.preview(content)
        self.assertEqual(self.upload.commit(second['ticket'])['status'],'UNCHANGED')

    def test_wrong_replaced_or_expired_ticket_cannot_import(self):
        content=self.package()
        first=self.upload.preview(content)
        second=self.upload.preview(content)
        for ticket in (first['ticket'],'wrong',None):
            with self.assertRaises(ValueError): self.upload.commit(ticket)
        self.now=601
        with self.assertRaisesRegex(ValueError,'caducado'): self.upload.commit(second['ticket'])
        self.assertFalse(self.fixture.db.exists())

    def test_bad_archive_real_material_and_incomplete_catalogue_rejected(self):
        for content in (b'not a ZIP',self.change_manifest(self.package(),'material_nature','REAL'),
                        self.fixture.package().read_bytes()):
            with self.assertRaises(ValueError): self.upload.preview(content)
        self.assertFalse(self.fixture.db.exists())
        self.assertIsNone(self.upload.pending)

    def test_limits_and_missing_manifest_rejected_before_read_dataset(self):
        content=self.package()
        with patch('eios.company_upload.MAX_UPLOAD_BYTES',1):
            with self.assertRaises(ValueError): self.upload.preview(content)
        with patch('eios.company_upload.MAX_EXPANDED_BYTES',1):
            with self.assertRaisesRegex(ValueError,'descomprimidos'): self.upload.preview(content)
        with patch('eios.company_upload.MAX_MEMBERS',1):
            with self.assertRaises(ValueError): self.upload.preview(content)
        output=BytesIO()
        with zipfile.ZipFile(output,'w') as z: z.writestr('installer.zip',b'inner')
        with self.assertRaisesRegex(ValueError,'company_manifest.json'): self.upload.preview(output.getvalue())

    def test_new_version_preserves_existing_snapshot_and_proposal(self):
        first=self.upload.preview(self.package());self.upload.commit(first['ticket'])
        from eios.company_app import PurchaseDesk
        desk=PurchaseDesk(self.fixture.db)
        proposal=desk.save(dict(dataset_id=first['dataset_id'],supplier_id='SUP',article_id='SKU',reference='P',quantity='1',unit_price='10',vat_percent='21',order_date='2026-10-01',due_date='2026-10-31'))
        changed=self.change_manifest(self.package(),'company',dict(company_id='COMP',legal_name='Version two'))
        preview=self.upload.preview(changed);self.upload.commit(preview['ticket'])
        self.assertNotEqual(first['dataset_id'],preview['dataset_id'])
        self.assertEqual(desk.state(first['dataset_id'])['purchases'],[proposal])
        self.assertEqual(desk.state(preview['dataset_id'])['purchases'],[])
        with sqlite3.connect(self.fixture.db) as c:
            self.assertEqual(c.execute('select count(*) from documentary_company_snapshot').fetchone()[0],2)
