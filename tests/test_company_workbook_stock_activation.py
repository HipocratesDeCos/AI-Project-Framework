from io import BytesIO
from decimal import Decimal
from datetime import datetime
import unittest

from openpyxl import load_workbook
from tests.test_company_exclusive_workbook import ExclusiveWorkbookTest, book
from eios.company_workbook_stock_planning import PLAN_HEADERS, RECEIPT_HEADERS
from eios.company_workbook_reception import CompanyWorkbookReception
from eios.company_exclusive_workbook import activate


def planned_book(bad_unit=False):
    w=load_workbook(BytesIO(book()));i=w['Inventario'];i.cell(1,6,'observation_date');i.cell(2,6,datetime(2026,9,30));i.cell(1,7,'safety_stock');i.cell(2,7,1)
    for name in ('observation_date','safety_stock'):w['97_Guia_Carga'].append(['Inventario','inventory',name,name])
    p=w.create_sheet('013_Planificacion_Stock')
    for col,value in enumerate(PLAN_HEADERS,1):p.cell(26,col,value)
    for col,value in enumerate(['A','palets',1,datetime(2026,9,30),datetime(2026,12,29),7,30,1,'VER TABLA PENDIENTES','Test','TEST-PLAN','SUPUESTO DE PRUEBA'],1):p.cell(27,col,value)
    r=w.create_sheet('014_Recepciones_Pendientes');r.append(RECEIPT_HEADERS)
    r.append(['R1','A','wrong' if bad_unit else 'palets',2,datetime(2026,10,2),'Test','TEST-PLAN','SYNTHETIC_TEST'])
    f=BytesIO();w.save(f);return f.getvalue()


class StockActivationTest(ExclusiveWorkbookTest):
    def test_received_plan_reaches_coverage_without_affecting_old_snapshot(self):
        bid=self.receive(planned_book());did=activate(self.path,'one',bid)['dataset_id']
        state=self.desk.state(did);p=state['planning']['A']
        self.assertEqual(p['status'],'FINITE');self.assertEqual(Decimal(p['coverage_days']),8)
        self.assertEqual(p['workbook_assumptions']['receipts'][0]['reference'],'R1')
        self.assertFalse(p['decision_authority']);self.assertEqual(p['operational_path'],'FORBIDDEN')
        again=activate(self.path,did,bid)['dataset_id'];self.assertEqual(did,again)
        self.assertEqual(self.desk.state('one')['info']['dataset_id'],'one')
        next_bid=self.receive(book(extra=True));next_id=activate(self.path,did,next_bid)['dataset_id']
        self.assertEqual(self.desk.state(next_id)['planning']['A']['status'],'MISSING_DATA')
        self.assertEqual(self.desk.state(did)['planning']['A']['status'],'FINITE')

    def test_invalid_supplement_never_produces_a_reception_ticket(self):
        reader=CompanyWorkbookReception(self.path)
        with self.assertRaises(ValueError):reader.preview(planned_book(True),'Bad.xlsx',dict(company_id='one',legal_name='Empresa sintética',as_of_date='2026-09-30',material_nature='SYNTHETIC',number_format='ES'))
        self.assertIsNone(reader.checked)


if __name__=='__main__':unittest.main()
