from datetime import date
from io import BytesIO
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
import zipfile

from eios.company_tables import read_table,normalize,number
from eios.company_reception import CompanyReception


def workbook():
    # Minimal OOXML fixture for parsing, not a user-facing workbook.
    parts={
        '[Content_Types].xml':'<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>',
        '_rels/.rels':'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>',
        'xl/workbook.xml':'<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Inventario" sheetId="1" r:id="rId1"/></sheets></workbook>',
        'xl/_rels/workbook.xml.rels':'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/></Relationships>',
        'xl/worksheets/sheet1.xml':'<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData><row r="1"><c r="A1" t="inlineStr"><is><t>SKU</t></is></c><c r="B1" t="inlineStr"><is><t>Unidad</t></is></c><c r="C1" t="inlineStr"><is><t>Fisico</t></is></c><c r="D1" t="inlineStr"><is><t>Reserva</t></is></c><c r="E1" t="inlineStr"><is><t>Fecha</t></is></c></row><row r="2"><c r="A2" t="inlineStr"><is><t>0007</t></is></c><c r="B2" t="inlineStr"><is><t>uds.</t></is></c><c r="C2"><v>45.5</v></c><c r="D2"><f>SUM(1,2)</f><v>3</v></c><c r="E2" t="d"><v>2026-09-30</v></c></row></sheetData></worksheet>',
    }
    out=BytesIO()
    with zipfile.ZipFile(out,'w') as z:
        for name,text in parts.items(): z.writestr(name,text)
    return out.getvalue()


class TablesTest(unittest.TestCase):
    def test_locale_numbers_are_explicit_not_guessed(self):
        self.assertEqual(str(number('1.234,56','ES')),'1234.56')
        self.assertEqual(str(number('1,234.56','EN')),'1234.56')
        for value in ['1850.00','1,234.56','NaN','Infinity']:
            with self.assertRaises(ValueError): number(value,'ES')

    def test_csv_header_offset_rows_blanks_and_unknown_reservations(self):
        table=read_table('Título\nSKU;Unidad;Físico\n0007;uds.;12,5\n;;\n'.encode(),'stock.csv',header_row=2,delimiter=';')
        result=normalize(table,'inventory',dict(article_id=0,unit=1,physical=2,reserved=None),'2026-09-30','ES')
        self.assertEqual(result['records'][0]['source_row'],3)
        self.assertEqual(result['records'][0]['data']['physical'],'12.5')
        self.assertIsNone(result['records'][0]['data']['available'])
        self.assertEqual(len(result['warnings']),1)

    def test_xlsx_sheet_date_formula_and_text_identity(self):
        table=read_table(workbook(),'stock.xlsx')
        self.assertEqual(table['sheets'],['Inventario'])
        self.assertEqual(table['rows'][0]['values'][4],'2026-09-30')
        mapping=dict(article_id=0,unit=1,physical=2,reserved=3)
        result=normalize(table,'inventory',mapping,'2026-09-30','ES')
        self.assertEqual(result['error_count'],1)
        self.assertIn('fórmula',str(result['errors']))
        mapping['reserved']=None
        clean=normalize(table,'inventory',mapping,'2026-09-30','ES')
        self.assertEqual(clean['records'][0]['data']['article_id'],'0007')
        self.assertEqual(clean['records'][0]['data']['physical'],'45.5')
        table['rows'][0]['values'][0]=7
        self.assertEqual(normalize(table,'inventory',mapping,'2026-09-30','ES')['error_count'],1)

    def test_duplicates_invalid_dates_missing_required_and_duplicate_mapping(self):
        table=read_table(b'Code;Name\nS;One\nS;Two\n','s.csv',delimiter=';')
        self.assertEqual(normalize(table,'supplier',dict(supplier_id=0,legal_name=1),'2026-09-30','ES')['error_count'],1)
        with self.assertRaises(ValueError): normalize(table,'supplier',dict(supplier_id=0,legal_name=0),'2026-09-30','ES')
        with self.assertRaises(ValueError): normalize(table,'supplier',dict(supplier_id=None,legal_name=1),'2026-09-30','ES')
        buy=read_table(b'Invoice;Date;Supplier;Sku;Qty;Unit;Net;Currency\nF;31/09/2026;S;A;2;uds.;20,00;EUR\n','f.csv',delimiter=';')
        mapping=dict(zip(['invoice_number','issue_date','supplier_id','article_id','quantity','unit','net_amount','currency'],range(8)))
        self.assertEqual(normalize(buy,'purchase_line',mapping,'2026-09-30','ES')['error_count'],1)
        buy['rows'][0]['values'][1]='01/10/2026'
        self.assertEqual(normalize(buy,'purchase_line',mapping,'2026-09-30','ES')['error_count'],1)


    def test_cashflow_future_due_date_signed_balance_and_inventory_date(self):
        table=read_table(b'Ref;Direction;Amount;Currency;Due\nP-1;PAGO;125,50;EUR;31/10/2026\n','cash.csv',delimiter=';')
        fields=['flow_id','direction','amount','currency','due_date']
        result=normalize(table,'cash_flow',dict(zip(fields,range(5))),'2026-09-30','ES')
        self.assertEqual(result['records'][0]['data']['due_date'],'2026-10-31')
        balance=read_table(b'Account;Balance;Currency\n5720001;-1.234,56;EUR\n','b.csv',delimiter=';')
        record=normalize(balance,'balance',dict(account_code=0,balance=1,currency=2),'2026-09-30','ES')['records'][0]
        self.assertEqual(record['data']['balance'],'-1234.56')
        inventory=read_table(b'Sku;Unit;Qty;Date\nA;uds.;10;29/09/2026\n','i.csv',delimiter=';')
        checked=normalize(inventory,'inventory',dict(article_id=0,unit=1,physical=2,observation_date=3),'2026-09-30','ES')
        self.assertEqual(checked['error_count'],1)

    def test_row_limit_and_untrusted_xml_declarations_are_rejected(self):
        from unittest.mock import patch
        with patch('eios.company_tables.MAX_ROWS',1):
            with self.assertRaises(ValueError): read_table(b'C;N\n1;One\n2;Two\n','s.csv',delimiter=';')
        target=BytesIO()
        with zipfile.ZipFile(BytesIO(workbook())) as source,zipfile.ZipFile(target,'w') as out:
            for name in source.namelist():
                value=source.read(name)
                if name=='xl/workbook.xml': value=b'<!DOCTYPE workbook [<!ENTITY x "data">]>'+value
                out.writestr(name,value)
        with self.assertRaises(ValueError): read_table(target.getvalue(),'unsafe.xlsx')


class ReceptionTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.db=Path(self.tmp.name)/'company.db'
        self.now=0;self.reception=CompanyReception(self.db,clock=lambda:self.now)
        self.content=b'Codigo;Nombre\n0001;Supplier One\n'

    def tearDown(self): self.tmp.cleanup()

    def preview(self, **changes):
        file=self.reception.read(self.content,'suppliers.csv',delimiter=';')
        data=dict(upload=file['upload'],company_id='CLIENT-NEW',legal_name='New Company',material_nature='REAL',as_of_date='2026-09-30',kind='supplier',number_format='ES',mapping=dict(supplier_id=0,legal_name=1))
        data.update(changes)
        return self.reception.preview(data)

    def test_real_data_preview_no_write_preserved_bytes_and_no_canonical_promotion(self):
        report=self.preview()
        self.assertFalse(self.db.exists())
        self.assertEqual(report['material_nature'],'REAL')
        result=self.reception.commit(report['ticket'])
        self.assertEqual(result['admission_status'],'PENDING')
        self.assertFalse(result['decision_authority'])
        with sqlite3.connect(self.db) as c:
            raw,records=c.execute('select content,records_json from received_company_batch').fetchone()
            tables={r[0] for r in c.execute("select name from sqlite_master where type='table'")}
        self.assertEqual(raw,self.content)
        self.assertEqual(json.loads(records)[0]['data']['supplier_id'],'0001')
        self.assertNotIn('documentary_company_snapshot',tables)
        self.assertEqual(self.reception.batches()[0]['company_id'],'CLIENT-NEW')
        again=self.preview()
        self.assertEqual(self.reception.commit(again['ticket'])['status'],'UNCHANGED')

    def test_errors_never_allow_partial_import_and_identity_cannot_be_reused(self):
        self.content=b'Codigo;Nombre\nS;One\nS;Duplicate\n'
        report=self.preview()
        self.assertIsNone(report['ticket'])
        with self.assertRaises(ValueError): self.reception.commit('invented')
        self.assertFalse(self.db.exists())
        self.content=b'Codigo;Nombre\nS;One\n'
        first=self.preview();self.reception.commit(first['ticket'])
        second=self.preview(legal_name='Other Company')
        with self.assertRaises(ValueError): self.reception.commit(second['ticket'])
        self.assertEqual(len(self.reception.batches()),1)

    def test_changed_file_and_expired_preview_invalidate_tickets(self):
        first=self.preview()
        self.reception.read(self.content,'new.csv',delimiter=';')
        with self.assertRaises(ValueError): self.reception.commit(first['ticket'])
        second=self.preview();self.now=601
        with self.assertRaises(ValueError): self.reception.commit(second['ticket'])
        self.assertFalse(self.db.exists())

    def test_preview_cannot_mutate_the_frozen_source_records(self):
        report=self.preview()
        report['preview'][0]['data']['legal_name']='Altered after validation'
        report['mapping']['supplier_id']=1
        self.reception.commit(report['ticket'])
        saved=self.reception.batches()[0]
        self.assertEqual(saved['preview'][0]['data']['legal_name'],'Supplier One')
        self.assertEqual(saved['mapping']['supplier_id'],0)

    def test_pdf_is_support_only_no_extracted_or_invented_records(self):
        read=self.reception.read(b'%PDF-1.4\nsource bytes','invoice.pdf')
        report=self.reception.preview(dict(upload=read['upload'],company_id='C',legal_name='Company',material_nature='REAL',as_of_date='2026-09-30',kind='document',number_format='ES',mapping={}))
        self.assertEqual(report['record_count'],0)
        self.reception.commit(report['ticket'])
        self.assertEqual(self.reception.batches()[0]['kind'],'document')
