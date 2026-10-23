from io import StringIO
import csv
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from eios.company_tables import FIELDS
from eios.company_table_profiles import profiles, suggestions
from eios.company_reception import CompanyReception
from eios.company_reception_templates import definitions


class TableProfilesTest(unittest.TestCase):
    def test_every_ordinary_template_is_recognized_with_reordered_columns(self):
        for kind,item in definitions().items():
            if kind=='commercial_catalogue':continue
            for labels in (False,True):
                with self.subTest(kind=kind,labels=labels):
                    headers=[f['label'] if labels else f['key'] for f in reversed(item['fields'])]
                    result=profiles(headers)['table_profile']
                    self.assertEqual(result['kind'],kind)
                    self.assertEqual(result['mapping'],{f['key']:len(headers)-1-i for i,f in enumerate(item['fields'])})
                    self.assertEqual(result['basis'],'EXACT_TEMPLATE_HEADERS')

    def test_stock_policy_and_inventory_are_distinguished_by_full_schema(self):
        for kind in ('inventory','stock_policy'):
            headers=[f[0] for f in FIELDS[kind]]
            self.assertEqual(profiles(headers)['table_profile']['kind'],kind)
        self.assertIsNone(profiles(['article_id','unit'])['table_profile'])

    def test_duplicate_keys_or_labels_remain_unassigned_without_guessing(self):
        headers=['invoice_number','issue_date','customer_id','article_id','quantity','unit','net_amount','currency','Importe neto de la línea']
        result=profiles(headers);self.assertIsNone(result['table_profile'])
        proposed=result['column_suggestions']['sales_line']
        self.assertIsNone(proposed['mapping']['net_amount'])
        self.assertIn('net_amount',proposed['ambiguous_fields']);self.assertIn('net_amount',proposed['missing_required'])

    def test_extras_or_partial_tables_have_suggestions_without_content_selection(self):
        headers=[k for k,_,required in FIELDS['sales_line'] if required]+['Observaciones']
        result=profiles(headers);self.assertIsNone(result['table_profile'])
        mapping=result['column_suggestions']['sales_line']['mapping']
        self.assertEqual(mapping['customer_id'],2);self.assertIsNone(mapping['vat_amount'])
        self.assertEqual(result['column_suggestions']['sales_line']['missing_required'],[])
        self.assertIsNone(profiles(['Precio','IVA','Cantidad'])['table_profile'])
        self.assertIsNone(suggestions(['Precio','IVA','Cantidad'],'sales_line')['mapping']['vat_amount'])
        self.assertIsNone(suggestions(['Precio','IVA','Cantidad'],'sales_line')['mapping']['vat_percent'])

    def test_no_source_column_is_proposed_for_two_fields(self):
        with patch.dict(FIELDS,{'test':[('first','Compartida',True),('second','Compartida',True)]}):
            result=suggestions(['Compartida'],'test')
        self.assertEqual(result['mapping'],dict(first=None,second=None))
        self.assertEqual(result['ambiguous_fields'],['first','second'])

    def test_accents_case_spacing_and_separators_do_not_change_explicit_identity(self):
        headers=['  CÓDIGO DE CLIENTE  ','RaZÓn SOCIAL','NIF / identificación fiscal','Localidad']
        self.assertEqual(profiles(headers)['table_profile']['kind'],'customer')
        self.assertEqual(suggestions(['ARTICLE ID','UNIT','PHYSICAL'],'inventory')['mapping']['physical'],2)

    def test_reception_suggests_but_does_not_write_or_accept_invalid_template_rows(self):
        with tempfile.TemporaryDirectory() as folder:
            db=Path(folder)/'company.db';r=CompanyReception(db)
            fields=[f[0] for f in FIELDS['sales_installment']]
            s=StringIO();w=csv.writer(s);w.writerow(fields);w.writerow(['Q1','C1','F1','1','31/10/2026','100','EUR','Transferencia','200',''])
            read=r.read(s.getvalue().encode(),'unrelated-name.csv')
            self.assertEqual(read['table_profile']['kind'],'sales_installment');self.assertFalse(db.exists())
            report=r.preview(dict(upload=read['upload'],company_id='DEMO',legal_name='Empresa ficticia',material_nature='SYNTHETIC',as_of_date='2026-09-30',kind='sales_installment',number_format='EN',mapping=read['table_profile']['mapping']))
            self.assertGreater(report['error_count'],0);self.assertIsNone(report['ticket']);self.assertFalse(db.exists())

    def test_manual_mapping_can_override_suggestions_and_remains_validated(self):
        with tempfile.TemporaryDirectory() as folder:
            r=CompanyReception(Path(folder)/'company.db')
            read=r.read(b'customer_id;legal_name;tax_id;locality\nC1;Cliente;X;Sabadell\n','customers.csv')
            self.assertEqual(read['table_profile']['kind'],'customer')
            mapping=dict(read['table_profile']['mapping']);mapping['legal_name']=0
            with self.assertRaises(ValueError):r.preview(dict(upload=read['upload'],company_id='DEMO',legal_name='Empresa ficticia',material_nature='SYNTHETIC',as_of_date='2026-09-30',kind='customer',number_format='ES',mapping=mapping))

    def test_pdf_and_dedicated_commercial_catalogue_do_not_select_ordinary_profile(self):
        with tempfile.TemporaryDirectory() as folder:
            r=CompanyReception(Path(folder)/'company.db');read=r.read(b'%PDF-1.4\nsource','support.pdf')
            self.assertIsNone(read['table_profile']);self.assertEqual(read['column_suggestions'],{})
        headers=[f['key'] for f in definitions()['commercial_catalogue']['fields']]
        self.assertIsNone(profiles(headers)['table_profile'])
    def test_prepared_collection_export_headers_select_cash_flow(self):
        from eios.company_sales_receivables import EXPORT_FIELDS
        result=profiles(EXPORT_FIELDS)['table_profile']
        self.assertEqual(result['kind'],'cash_flow')
        self.assertEqual(result['mapping'],{field:i for i,field in enumerate(EXPORT_FIELDS)})
