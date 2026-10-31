import sqlite3
import unittest
from tests import test_company_exclusive_workbook as fixture
from eios.company_exclusive_workbook import activate
from eios.company_source_visibility import source_status,mark_received
from eios.company_reception import CompanyReception


class SourceVisibilityTest(unittest.TestCase):
    setUp=fixture.ExclusiveWorkbookTest.setUp
    tearDown=fixture.ExclusiveWorkbookTest.tearDown
    add=fixture.ExclusiveWorkbookTest.add
    financial_data=fixture.ExclusiveWorkbookTest.financial_data
    set_policy=fixture.ExclusiveWorkbookTest.set_policy
    receive=fixture.ExclusiveWorkbookTest.receive

    def test_baseline_active_and_historical_are_distinct(self):
        self.assertEqual(source_status(self.path,'one')['status'],'BASELINE')
        bid=self.receive();did=activate(self.path,'one',bid)['dataset_id']
        active=source_status(self.path,did)
        self.assertEqual(active['status'],'ACTIVE');self.assertEqual(active['filename'],'Empresa.xlsx')
        self.assertEqual(active['version_id'],did)
        self.assertEqual(source_status(self.path,'one')['status'],'HISTORICAL')
        self.assertEqual(source_status(self.path,'two')['status'],'BASELINE')
        rows=mark_received(self.path,CompanyReception(self.path).batches())
        self.assertTrue(all(r['workbook_usage']=='ACTIVE' for r in rows))
        self.assertTrue(all(r['active_workbooks'][0]['dataset_id']==did for r in rows))

    def test_same_filename_with_new_bytes_marks_only_the_selected_version_active(self):
        bid=self.receive();first=activate(self.path,'one',bid)['dataset_id']
        bid=self.receive(fixture.book(customer='4300002'));second=activate(self.path,first,bid)['dataset_id']
        self.assertNotEqual(first,second)
        self.assertEqual(source_status(self.path,first)['status'],'HISTORICAL')
        self.assertEqual(source_status(self.path,second)['status'],'ACTIVE')
        rows=mark_received(self.path,CompanyReception(self.path).batches())
        self.assertTrue(any(r['workbook_usage']=='RECEIVED' for r in rows))
        self.assertTrue(any(r['workbook_usage']=='ACTIVE' for r in rows))
        self.assertTrue(all(x['dataset_id']==second for r in rows for x in r['active_workbooks']))

    def test_printable_offer_keeps_its_source_version(self):
        from eios.company_sales_proposals import printable_offer
        bid=self.receive();did=activate(self.path,'one',bid)['dataset_id']
        state=self.desk.sales_state(did)
        args=dict(self.offer,dataset_id=did,customer_id='4300001',commercial_parameter_revision=state['sales_parameters']['revision'],context_fingerprint=state['documentary_context']['fingerprint'])
        saved=self.desk.sales_offer(args)
        html=printable_offer(self.path,did,saved['proposal_id'])
        self.assertIn('Versión documental utilizada:',html)
        self.assertIn('Empresa.xlsx',html)
        self.assertIn(did[:12],html)
