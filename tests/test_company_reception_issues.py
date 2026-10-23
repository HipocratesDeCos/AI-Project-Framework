import base64
import csv
from io import StringIO
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

from eios.company_reception import CompanyReception

class ReceptionIssuesTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.db=Path(self.tmp.name)/'company.db';self.now=0
        self.r=CompanyReception(self.db,clock=lambda:self.now)
    def preview(self,content=b'Code;Name\nC1;Cliente\nC1;Repetido\n',filename='customers.csv',**changes):
        read=self.r.read(content,filename,delimiter=';')
        self.request=dict(upload=read['upload'],company_id='DEMO',legal_name='Empresa ficticia',material_nature='SYNTHETIC',as_of_date='2026-09-30',kind='customer',number_format='ES',mapping=dict(customer_id=0,legal_name=1))
        self.request.update(changes);return self.r.preview(self.request)
    def report(self,p):
        result=self.r.issues(dict(ticket=p['issue_report_ticket']))
        rows=list(csv.DictReader(StringIO(base64.b64decode(result['content_base64']).decode('utf-8-sig')),delimiter=';'))
        return result,rows
    def test_full_error_rows_not_limited_to_screen_sample_and_no_write(self):
        content=('Code;Name\n'+'C1;Cliente\n'*151).encode();p=self.preview(content)
        self.assertEqual(p['error_count'],150);self.assertEqual(len(p['errors']),100);self.assertIsNone(p['ticket'])
        result,rows=self.report(p);self.assertEqual(result['error_row_count'],150);self.assertEqual(len(rows),150)
        self.assertEqual(rows[-1]['Fila'],'152');self.assertEqual(rows[0]['Tipo'],'ERROR');self.assertEqual(rows[0]['Fecha_corte'],'30/09/2026')
        self.assertEqual(rows[0]['Codigo_empresa'],'DEMO');self.assertFalse(self.db.exists());self.assertFalse(result['decision_authority'])
        self.assertEqual(result['operational_path'],'FORBIDDEN')
    def test_warning_report_preserves_save_ticket_and_batch_identity(self):
        content=b'SKU;Unidad;Fisico\nA;uds.;12\n'
        args=dict(kind='inventory',mapping=dict(article_id=0,unit=1,physical=2))
        first=self.preview(content,filename='stock.csv',**args);self.assertIsNotNone(first['ticket'])
        result,rows=self.report(first);self.assertEqual(result['warning_count'],1);self.assertEqual(rows[0]['Fila'],'2');self.assertEqual(rows[0]['Tipo'],'AVISO')
        original=self.r.commit(first['ticket']);self.assertEqual(original['status'],'RECEIVED')
        second=self.preview(content,filename='stock.csv',**args);self.report(second)
        again=self.r.commit(second['ticket']);self.assertEqual(again['status'],'UNCHANGED');self.assertEqual(again['batch_id'],original['batch_id'])
        with sqlite3.connect(self.db) as c:meta=json.loads(c.execute('SELECT metadata_json FROM received_company_batch').fetchone()[0])
        self.assertNotIn('issue_report_ticket',meta)
    def test_clean_file_has_no_report_and_export_is_not_a_commit_ticket(self):
        p=self.preview(b'Code;Name\nC1;Cliente\n');self.assertIsNone(p['issue_report_ticket'])
        with self.assertRaises(ValueError):self.r.issues(dict(ticket=p['ticket']))
        p=self.preview()
        with self.assertRaises(ValueError):self.r.commit(p['issue_report_ticket'])
        self.assertFalse(self.db.exists())
    def test_new_preview_read_or_failed_preview_invalidates_previous_report(self):
        p=self.preview();old=p['issue_report_ticket'];self.r.preview(self.request)
        with self.assertRaises(ValueError):self.r.issues(dict(ticket=old))
        p=self.r.preview(self.request)
        with self.assertRaises(ValueError):self.r.preview(dict(self.request,mapping={}))
        with self.assertRaises(ValueError):self.report(p)
        p=self.preview();self.r.read(b'Code;Name\nC2;Otro\n','other.csv',delimiter=';')
        with self.assertRaises(ValueError):self.report(p)
    def test_expiry_invalid_tokens_and_tampered_source_are_rejected(self):
        p=self.preview()
        for data in (None,{},dict(ticket=1),dict(ticket='invented'),dict(ticket='ñ')):
            with self.subTest(data=data),self.assertRaises(ValueError):self.r.issues(data)
        self.now=601
        with self.assertRaises(ValueError):self.report(p)
        self.now=0;p=self.preview();self.r.file['content']=b'changed'
        with self.assertRaises(ValueError):self.report(p)
    def test_mutating_returned_screen_sample_cannot_change_download(self):
        p=self.preview();p['errors'][0]['messages'][:]=['Changed by client'];p['legal_name']='Other'
        _,rows=self.report(p);self.assertIn('duplicado',rows[0]['Mensaje']);self.assertEqual(rows[0]['Empresa'],'Empresa ficticia')
    def test_csv_quotes_unicode_multiline_and_formula_like_metadata(self):
        p=self.preview(filename='=SUM(1,2).csv',legal_name='  =HYPERLINK("x")')
        _,rows=self.report(p);self.assertTrue(rows[0]['Archivo'].startswith("'="));self.assertTrue(rows[0]['Empresa'].startswith("'="))
        self.assertIn('Identificador duplicado',rows[0]['Mensaje'])
        p=self.preview(b'Code;Name\n;\nC2;\n')
        _,rows=self.report(p);self.assertIn('dato vacío',rows[-1]['Mensaje'])
    def test_pdf_warning_has_no_invented_row(self):
        p=self.preview(b'%PDF-1.4\nsource',filename='document.pdf',kind='document',mapping={})
        _,rows=self.report(p);self.assertEqual(rows[0]['Fila'],'');self.assertEqual(rows[0]['Tipo'],'AVISO')
        self.assertIn('PDF conservado',rows[0]['Mensaje'])
    def test_multiple_messages_in_one_row_roundtrip_as_one_csv_incident(self):
        p=self.preview(b'Code;Name;Locality\n; ;Sabadell\n',mapping=dict(customer_id=0,legal_name=1,locality=2))
        self.assertEqual(len(p['errors'][0]['messages']),2)
        result,rows=self.report(p);self.assertEqual(result['error_row_count'],1);self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]['Mensaje'],'\n'.join(p['errors'][0]['messages']))
    def test_original_row_numbers_survive_header_offset_and_excel_sheet(self):
        from tests.test_company_reception import workbook
        self.preview();read=self.r.read(b'Title\nCode;Name\nC1;Cliente\nC1;Repetido\n','offset.csv',delimiter=';',header_row=2)
        p=self.r.preview(dict(self.request,upload=read['upload']));_,rows=self.report(p);self.assertEqual(rows[0]['Fila'],'4')
        read=self.r.read(workbook(),'stock.xlsx')
        p=self.r.preview(dict(self.request,upload=read['upload'],kind='inventory',mapping=dict(article_id=0,unit=1,physical=2,reserved=3)))
        _,rows=self.report(p);self.assertEqual(rows[0]['Fila'],'2');self.assertEqual(rows[0]['Hoja'],'Inventario');self.assertIn('fórmula',rows[0]['Mensaje'])
