"""Preflight rejects mixed sources, unknown inputs and contradictory receipts."""
from copy import deepcopy
import unittest
from unittest.mock import patch

from eios.company_workbook_stock_planning import preview, PLAN_HEADERS, RECEIPT_HEADERS


def table(headers, rows, start=2):
    return dict(headers=headers, rows=[dict(row=start+i,values=v) for i,v in enumerate(rows)])


def fixture():
    fields={'Articles':('article',['article_id','description','unit'],[['A','Test','Unidad']]),
            'Inventory':('inventory',['article_id','unit','physical','reserved','observation_date','safety_stock'],[['A','Unidad',100,10,'2026-09-30',5]])}
    guide=[];tables={}
    for sheet,(kind,headers,rows) in fields.items():
        tables[sheet]=table(headers,rows)
        guide.extend([[sheet,kind,f,f] for f in headers])
    tables['97_Guia_Carga']=table(['Hoja','Tipo EIOS','Campo EIOS','Columna del archivo'],guide)
    tables['013_Planificacion_Stock']=table(PLAN_HEADERS,[['A','Unidad',2,'2026-09-30','2026-12-29',7,30,1,'VER TABLA PENDIENTES','Test','TEST-01','SUPUESTO DE PRUEBA']],27)
    tables['014_Recepciones_Pendientes']=table(RECEIPT_HEADERS,[['R1','A','Unidad',20,'2026-10-02','Test','TEST-01','SYNTHETIC_TEST']])
    return tables


class StockPreflightTest(unittest.TestCase):
    def run_preview(self,tables):
        with patch('eios.company_workbook_stock_planning.read_table',side_effect=lambda *a,**k:deepcopy(tables[k['sheet']])):
            return preview(b'one workbook','test.xlsx','2026-09-30')

    def test_bound_read_only_result_and_no_double_reservation(self):
        r=self.run_preview(fixture());p=r['plans']['A']
        self.assertEqual(p['available_at_order'],'90')
        self.assertEqual(p['receipts'][0]['quantity'],'20')
        self.assertEqual(r['status'],'VALIDATED_NOT_ACTIVE')
        self.assertFalse(r['decision_authority']);self.assertEqual(r['operational_path'],'FORBIDDEN')
        self.assertEqual(len(r['source_sha256']),64)

    def test_receipt_conflict_unit_duplicate_and_cutoff(self):
        for mode in ('unit','duplicate','date','state','after_blank'):
            with self.subTest(mode=mode):
                t=fixture();rs=t['014_Recepciones_Pendientes']['rows'];v=rs[0]['values']
                if mode=='unit':v[2]='Pack'
                elif mode=='date':v[4]='2026-09-30'
                elif mode=='state':t['013_Planificacion_Stock']['rows'][0]['values'][8]='NINGUNA DECLARADA'
                elif mode=='duplicate':rs.append(dict(row=3,values=v.copy()))
                else:rs.append(dict(row=5,values=['R2','A','Unidad',1,'2026-10-03','Test','TEST-01','SYNTHETIC_TEST']))
                with self.assertRaises(ValueError):self.run_preview(t)

    def test_forecast_missing_formula_wrong_date_and_horizon(self):
        for index,value in [(2,None),(2,{'formula':True,'cached':2}),(3,'2026-10-01'),(4,'2026-10-02'),(5,7.5),(7,0),(11,'CONFIRMADO')]:
            with self.subTest(index=index,value=value):
                t=fixture();t['013_Planificacion_Stock']['rows'][0]['values'][index]=value
                with self.assertRaises(ValueError):self.run_preview(t)

    def test_unknown_receipts_are_not_a_known_empty_list(self):
        t=fixture();t['014_Recepciones_Pendientes']['rows']=[]
        t['013_Planificacion_Stock']['rows'][0]['values'][8]='DESCONOCIDAS'
        r=self.run_preview(t)
        self.assertEqual(r['plans']['A']['pending_receipts_state'],'DESCONOCIDAS')
        self.assertEqual(r['status'],'VALIDATED_NOT_ACTIVE')

    def test_reject_old_inventory_and_missing_reservation(self):
        for index,value in [(3,None),(4,'2026-09-01')]:
            t=fixture();t['Inventory']['rows'][0]['values'][index]=value
            with self.assertRaises(ValueError):self.run_preview(t)


if __name__=='__main__':unittest.main()
