from io import BytesIO
from pathlib import Path
import tempfile
import unittest
from openpyxl import load_workbook

from eios.company_reception import CompanyReception
from eios.company_tables import tariff_mapping
from eios.company_sales_tariff_template import build_template


class TariffMappingTest(unittest.TestCase):
    def test_complete_profile_tracks_reordered_columns_without_fuzzy_guessing(self):
        headers=['Moneda','VÁLIDA HASTA','SKU','PVP sin IVA','Unidad','Válida desde','Descripción (consulta)']
        self.assertEqual(tariff_mapping(headers),dict(article_id=2,unit=4,recommended_sale_price=3,currency=0,valid_from=5,valid_until=1))
        for damaged in (headers+['PVP sin IVA'],headers+['article_id'],['Precio con IVA' if h=='PVP sin IVA' else h for h in headers],headers[:-2]):
            with self.subTest(headers=damaged):self.assertIsNone(tariff_mapping(damaged))

    def test_downloaded_workbook_receives_a_suggestion_then_still_requires_validation(self):
        state=dict(info=dict(company=dict(company_id='DEMO',legal_name='Empresa ficticia'),as_of_date='2026-09-30'),documentary_context=dict(material_nature='SYNTHETIC'),articles=[dict(article_id='0007',description='Artículo',unit_as_documented='uds.')])
        template=build_template(state)
        with tempfile.TemporaryDirectory() as folder:
            reception=CompanyReception(Path(folder)/'company.sqlite3')
            read=reception.read(template['content'],template['filename'],sheet='Tarifa')
            self.assertEqual(read['table_profile']['kind'],'sale_price')
            mapping=read['table_profile']['mapping']
            request=dict(upload=read['upload'],company_id='DEMO',legal_name='Empresa ficticia',material_nature='SYNTHETIC',as_of_date='2026-09-30',kind='sale_price',number_format='ES',mapping=mapping)
            preview=reception.preview(request)
            self.assertEqual(preview['error_count'],1);self.assertIsNone(preview['ticket'])
            workbook=load_workbook(BytesIO(template['content']));sheet=workbook['Tarifa']
            sheet['D2']='12,50';sheet['F2']='01/10/2026';sheet['G2']='31/12/2026'
            content=BytesIO();workbook.save(content);workbook.close()
            read=reception.read(content.getvalue(),template['filename'],sheet='Tarifa')
            preview=reception.preview(dict(request,upload=read['upload'],mapping=read['table_profile']['mapping']))
            self.assertEqual(preview['error_count'],0)
            self.assertEqual(preview['preview'][0]['data']['article_id'],'0007')
            self.assertEqual(preview['preview'][0]['data']['recommended_sale_price'],'12.50')
            self.assertIsNotNone(preview['ticket'])

    def test_ambiguous_or_unrelated_headers_never_select_a_tariff_profile(self):
        with tempfile.TemporaryDirectory() as folder:
            reception=CompanyReception(Path(folder)/'company.sqlite3')
            for data in (b'SKU;SKU;Unidad;PVP sin IVA;Moneda;Valida desde;Valida hasta\nA;B;uds.;10;EUR;01/10/2026;31/12/2026\n',b'Codigo;Nombre\nA;Ejemplo\n'):
                with self.subTest(data=data):self.assertIsNone(reception.read(data,'input.csv',delimiter=';')['table_profile'])
