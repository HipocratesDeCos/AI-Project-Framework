from pathlib import Path
import tempfile
import unittest

from eios.company_reception import CompanyReception


class ReceivedRecordsTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db=Path(self.tmp.name)/'company.db'
        self.reception=CompanyReception(self.db)
        rows=''.join(str(i).zfill(4)+';Proveedor '+str(i)+'\n' for i in range(75))+'LAST;Jardinería Vallès\n'
        file=self.reception.read(('Codigo;Nombre\n'+rows).encode(),'suppliers.csv',delimiter=';')
        preview=self.reception.preview(dict(upload=file['upload'],company_id='A',legal_name='Empresa A',material_nature='REAL',as_of_date='2026-09-30',kind='supplier',number_format='ES',mapping=dict(supplier_id=0,legal_name=1)))
        self.batch=self.reception.commit(preview['ticket'])['batch_id']

    def page(self,**kwargs):
        return self.reception.record_page('A',self.batch,**kwargs)

    def test_all_rows_reachable_past_preview_with_exact_source_rows(self):
        first=self.page()
        self.assertEqual(first['total_records'],76)
        self.assertEqual(first['matched_records'],76)
        self.assertEqual(len(first['records']),50)
        self.assertEqual(first['records'][0]['data']['supplier_id'],'0000')
        second=self.page(offset=50)
        self.assertEqual(len(second['records']),26)
        self.assertEqual(second['records'][-1]['data']['supplier_id'],'LAST')
        self.assertEqual(second['records'][-1]['source_row'],77)
        self.assertEqual(second['fields'][0]['label'],'Código de proveedor')

    def test_searches_all_data_accent_case_insensitively_preserving_values(self):
        result=self.page(query='jardineria valles')
        self.assertEqual(result['matched_records'],1)
        self.assertEqual(result['records'][0]['data']['legal_name'],'Jardinería Vallès')
        self.assertEqual(result['records'][0]['source_row'],77)
        self.assertEqual(self.page(query='0001')['records'][0]['data']['supplier_id'],'0001')
        self.assertEqual(self.page(query='NO MATCH')['records'],[])
        self.assertEqual(self.page(query='NO MATCH')['offset'],0)

    def test_out_of_range_offsets_clamp_to_last_page(self):
        result=self.page(offset=9999999)
        self.assertEqual(result['offset'],50)
        self.assertEqual(len(result['records']),26)
        self.assertEqual(self.page(offset=50,query='jardineria')['offset'],0)

    def test_company_scope_and_paging_search_validation(self):
        for kwargs in [dict(offset=-1),dict(offset=True),dict(offset='50'),dict(limit=0),dict(limit=101),dict(limit=True),dict(query=1),dict(query='a'*201)]:
            with self.assertRaises(ValueError):self.page(**kwargs)
        for company,bid in [('B',self.batch),('A','x'*64),('A','../file')]:
            with self.assertRaises(ValueError):self.reception.record_page(company,bid)

    def test_read_only_and_pending_admission(self):
        before=self.db.read_bytes()
        report=self.page(query='LAST')
        self.assertEqual(before,self.db.read_bytes())
        self.assertFalse(report['decision_authority'])
        self.assertEqual(report['admission_status'],'PENDING')
        self.assertEqual(report['operational_path'],'FORBIDDEN')

    def test_numeric_search_accepts_spanish_decimal_comma(self):
        file=self.reception.read(b'Cuenta;Saldo;Moneda\n572;125,50;EUR\n','balance.csv',delimiter=';')
        preview=self.reception.preview(dict(upload=file['upload'],company_id='A',legal_name='Empresa A',material_nature='REAL',as_of_date='2026-09-30',kind='balance',number_format='ES',mapping=dict(account_code=0,balance=1,currency=2)))
        bid=self.reception.commit(preview['ticket'])['batch_id']
        for query in ['125,50','125.50']:
            result=self.reception.record_page('A',bid,query=query)
            self.assertEqual(result['records'][0]['data']['balance'],'125.50')

    def test_pdf_remains_unextracted_support(self):
        file=self.reception.read(b'%PDF-1.4\n%%EOF','support.pdf')
        preview=self.reception.preview(dict(upload=file['upload'],company_id='A',legal_name='Empresa A',material_nature='REAL',as_of_date='2026-09-30',kind='document',number_format='ES',mapping={}))
        bid=self.reception.commit(preview['ticket'])['batch_id']
        result=self.reception.record_page('A',bid)
        self.assertEqual(result['kind'],'document')
        self.assertEqual(result['records'],[])
        self.assertEqual(result['total_records'],0)
