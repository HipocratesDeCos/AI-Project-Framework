from hashlib import sha256
from pathlib import Path
import sqlite3
import tempfile
import unittest

from eios.core.models import PurchaseOperation
from eios.company_dossier_versions import save_version
from eios.company_purchase_preparation import preparation_options,prepare_purchase
from eios.company_reception import CompanyReception,canonical


class PurchasePreparationTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.make_fixture()

    def receive(self,kind,fields,rows):
        content=(';'.join(fields)+'\n'+'\n'.join(';'.join(row) for row in rows)+'\n').encode()
        uploaded=self.reception.read(content,kind+'.csv',delimiter=';')
        checked=self.reception.preview(dict(upload=uploaded['upload'],company_id='PREP-COMPANY',legal_name='Empresa de preparación',material_nature=self.material,as_of_date='2026-09-30',kind=kind,number_format='ES',mapping=dict(zip(fields,range(len(fields))))))
        self.assertEqual(checked['error_count'],0)
        self.ids.append(self.reception.commit(checked['ticket'])['batch_id'])

    def save(self,name='Versión inicial'):
        self.dossier_id=save_version(self.db,self.ids,name)['dossier_id']

    def make_fixture(self,material='SYNTHETIC'):
        self.material=material
        self.db=Path(self.tmp.name)/(material.lower()+'.db')
        self.reception=CompanyReception(self.db)
        self.ids=[]
        self.receive('article',['article_id','description','unit','supplier_id'],[['A-0001','Estimulador 5L','uds','S-001']])
        self.receive('supplier',['supplier_id','legal_name'],[['S-001','Proveedor']])
        self.receive('purchase_line',['invoice_number','issue_date','supplier_id','article_id','quantity','unit','net_amount','currency'],[
            ['OLD','2026-09-01','S-001','A-0001','10','uds','1200,00','EUR'],
            ['LAST','2026-09-30','S-001','A-0001','40','uds','5140,00','EUR']])
        self.receive('inventory',['article_id','unit','physical','reserved'],[['A-0001','uds','75','15']])
        self.save()

    def operation(self,**changes):
        data=dict(reference='PROP-001',article_id='A-0001',supplier_id='S-001',unit='uds',quantity='10',unit_price='130.0000',currency='EUR',operation_date='2026-10-07')
        data.update(changes)
        return data

    def prepare(self,**changes):
        return prepare_purchase(self.db,self.dossier_id,self.operation(**changes))

    def test_existing_canonical_contract_and_source_binding_without_dip_or_execution(self):
        report=self.prepare()
        purchase=PurchaseOperation.model_validate(report['purchase_operation'])
        self.assertEqual(purchase.article_id,'A-0001')
        self.assertEqual(str(purchase.unit_price),'130.0000')
        self.assertEqual(report['dossier_id'],self.dossier_id)
        self.assertEqual(report['price_reference']['net_unit_price'],'128.50')
        self.assertEqual(report['price_reference']['quantity'],'40')
        self.assertEqual(report['price_reference']['difference_percent'],'1.17')
        self.assertEqual(report['stock_reference']['available'],'60')
        self.assertEqual(report['price_reference']['sources'][0]['row'],3)
        self.assertEqual(report['evaluation_status'],'NOT_EXECUTED')
        for key in ['decision_context','evidence','financial_input','decision_input_package']:
            self.assertIsNone(report[key])
        self.assertFalse(report['decision_authority'])
        self.assertEqual(report['operational_path'],'FORBIDDEN')
        self.assertEqual(report['admission_status'],'PENDING')
        self.assertEqual(len(report['pending']),6)

    def test_history_date_bound_and_no_future_inventory(self):
        report=self.prepare(operation_date='2026-09-15')
        self.assertEqual(report['price_reference']['net_unit_price'],'120.00')
        self.assertEqual(report['price_reference']['date'],'2026-09-01')
        self.assertEqual(report['stock_reference']['status'],'SNAPSHOT_AFTER_OPERATION')
        self.assertIsNone(report['stock_reference']['available'])
        self.assertIsNone(report['stock_reference']['physical'])
        self.assertEqual(self.prepare(operation_date='2026-08-01')['price_reference']['status'],'NO_ELIGIBLE_HISTORY')

    def test_last_date_ambiguity_never_falls_back(self):
        self.receive('purchase_line',['invoice_number','issue_date','supplier_id','article_id','quantity','unit','net_amount','currency'],[['OTHER','2026-09-30','S-001','A-0001','1','uds','100,00','EUR']])
        self.save('Dos líneas en la última fecha')
        reference=self.prepare()['price_reference']
        self.assertEqual(reference['status'],'AMBIGUOUS_LAST_DATE')
        self.assertIsNone(reference['net_unit_price'])
        self.assertEqual(len(reference['sources']),2)

    def test_last_unit_mismatch_and_invoice_conflicts_remain_explicit(self):
        self.receive('purchase_line',['invoice_number','issue_date','supplier_id','article_id','quantity','unit','net_amount','currency'],[['LAST-PALLET','2026-09-30','S-001','A-0001','1','palets','1000,00','EUR']])
        self.save('Unidad distinta')
        self.assertEqual(self.prepare()['price_reference']['status'],'UNIT_MISMATCH')
        self.receive('purchase_line',['invoice_number','issue_date','supplier_id','article_id','quantity','unit','net_amount','currency'],[['LAST','2026-09-29','S-001','A-0001','40','uds','5140,00','EUR']])
        self.save('Factura contradictoria')
        self.assertEqual(self.prepare()['price_reference']['status'],'CONFLICTING_INVOICE')

    def test_exact_unit_supplier_article_and_closed_currency_decimal_contract(self):
        for changes in [dict(unit='palets'),dict(supplier_id='OTHER'),dict(article_id='UNKNOWN'),dict(currency='USD'),dict(unit_price='1.23456'),dict(quantity='0'),dict(quantity=True),dict(unit_price='NaN'),dict(quantity='Infinity'),dict(operation_date='bad date'),dict(reference=''),dict(reference='x'*101),dict(reference='line\nbreak')]:
            with self.subTest(changes=changes),self.assertRaises(ValueError):self.prepare(**changes)
        with self.assertRaises(ValueError):
            prepare_purchase(self.db,self.dossier_id,dict(self.operation(),evidence='DEMONSTRATED'))
        # Zero is permitted by the existing canonical price contract; no rule verdict follows.
        self.assertTrue(self.prepare(unit_price='0')['operation_contract_valid'])
        self.assertTrue(self.prepare(unit_price='1.2345')['operation_contract_valid'])

    def test_catalogue_conflicts_are_not_selectable(self):
        self.receive('article',['article_id','description','unit','supplier_id'],[['A-0001','Descripción contradictoria','uds','S-001']])
        self.save('Ficha contradictoria')
        options=preparation_options(self.db,self.dossier_id)
        self.assertEqual(options['articles'],[])
        self.assertEqual(options['blocked'][0]['identifier'],'A-0001')
        with self.assertRaises(ValueError):self.prepare()

    def test_real_material_is_preserved_not_relabelled_or_admitted(self):
        self.make_fixture('REAL')
        report=self.prepare()
        self.assertEqual(report['material_nature'],'REAL')
        self.assertFalse(report['decision_authority'])
        self.assertIsNone(report['decision_input_package'])

    def test_read_only_deterministic_fingerprint_and_no_business_tables(self):
        before=self.db.read_bytes()
        report=self.prepare()
        again=self.prepare()
        self.assertEqual(report,again)
        self.assertEqual(self.db.read_bytes(),before)
        identifier=report.pop('preparation_id')
        self.assertEqual(identifier,sha256(canonical(report).encode()).hexdigest())
        with sqlite3.connect(self.db) as connection:
            tables={row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        self.assertNotIn('manual_purchase_proposal',tables)
        self.assertNotIn('documentary_company_snapshot',tables)
