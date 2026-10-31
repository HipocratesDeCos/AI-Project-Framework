import sqlite3
import unittest
from tests import test_company_exclusive_workbook as fixture
from eios.company_upload_flow import companies
from eios.company_workbook_reception import CompanyWorkbookReception
from eios.company_exclusive_workbook import activate,dataset_options


class UploadFlowTest(unittest.TestCase):
    setUp=fixture.ExclusiveWorkbookTest.setUp
    tearDown=fixture.ExclusiveWorkbookTest.tearDown
    add=fixture.ExclusiveWorkbookTest.add
    financial_data=fixture.ExclusiveWorkbookTest.financial_data
    set_policy=fixture.ExclusiveWorkbookTest.set_policy
    receive=fixture.ExclusiveWorkbookTest.receive

    def test_company_picker_uses_registered_identity_without_rewriting_the_old_snapshot(self):
        self.receive()
        with sqlite3.connect(self.path) as c:c.execute('UPDATE received_company SET legal_name=? WHERE company_id=?',('Nombre registrado, S.L.','one'))
        rows={r['company_id']:r for r in companies(self.path)}
        self.assertEqual(rows['one']['legal_name'],'Nombre registrado, S.L.')
        self.assertTrue(rows['one']['registered'])
        self.assertFalse(rows['two']['registered'])
        self.assertEqual(self.desk.state('one')['info']['company']['legal_name'],'Empresa sintética')

    def test_guided_received_activation_creates_its_own_company_without_archiving_another(self):
        service=CompanyWorkbookReception(self.path)
        p=service.preview(fixture.book(),'Nueva_v1.xlsx',dict(company_id='new-co',legal_name='Otra empresa nueva, S.L.',as_of_date='2026-09-30',material_nature='SYNTHETIC',number_format='ES'))
        received=service.commit(p['ticket']);bid=received['batch_ids'][0]
        with self.assertRaises(ValueError):activate(self.path,'one',bid)
        result=activate(self.path,'one',bid,from_received=True)
        state=self.desk.state(result['dataset_id'])
        self.assertEqual(state['info']['company']['company_id'],'new-co')
        self.assertEqual([c['customer_id'] for c in state['customers']],['4300001'])
        with sqlite3.connect(self.path) as c:rows=c.execute('SELECT dataset_id,company_id,as_of_date FROM documentary_company_snapshot').fetchall()
        self.assertFalse(next(r for r in dataset_options(self.path,rows) if r['dataset_id']=='one')['historical'])
        self.assertEqual([c['customer_id'] for c in self.desk.state('one')['customers']],['C'])
