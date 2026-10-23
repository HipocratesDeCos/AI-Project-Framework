from copy import deepcopy
import json
import sqlite3
import unittest

from tests import test_company_sales_links as fixture
from tests import test_company_selected_sales as sales_fixture
from eios.company_data_status import describe_status
from eios.company_reception import CompanyReception
from eios.company_selected_sales import SalesHistorySelection

class CompanyDataStatusTest(unittest.TestCase):
    add=fixture.SalesLinksTest.add
    financial_data=fixture.SalesLinksTest.financial_data
    set_policy=fixture.SalesLinksTest.set_policy
    setUp=fixture.SalesLinksTest.setUp
    tearDown=fixture.SalesLinksTest.tearDown
    receive=sales_fixture.SelectedSalesTest.receive
    request=sales_fixture.SelectedSalesTest.request
    commit=sales_fixture.SelectedSalesTest.commit
    def status(self):return self.desk.state('one')['data_status']
    def block(self,key):return next(b for b in self.status()['blocks'] if b['key']==key)
    def test_overview_is_read_only_and_does_not_claim_admission(self):
        state=self.desk.state('one');before=deepcopy(state)
        with sqlite3.connect(self.path) as c:original=list(c.iterdump())
        report=describe_status(self.path,state)
        with sqlite3.connect(self.path) as c:self.assertEqual(list(c.iterdump()),original)
        self.assertEqual(state,before);self.assertEqual(len(report['blocks']),6)
        self.assertEqual(report['dataset_id'],'one');self.assertFalse(report['decision_authority']);self.assertEqual(report['operational_path'],'FORBIDDEN')
        self.assertEqual(report['context_fingerprint'],state['documentary_context']['fingerprint'])
    def test_receiving_sales_is_distinct_from_selecting_and_withdrawing(self):
        bid=self.receive();block=self.block('sales')
        self.assertEqual(block['received_file_count'],1);self.assertEqual(block['metrics'][1]['value'],0);self.assertEqual(block['status'],'BASELINE')
        self.selection=SalesHistorySelection(self.path);self.commit(self.selection.preview(self.request([bid])))
        block=self.block('sales');self.assertEqual(block['status'],'SELECTED');self.assertEqual(block['metrics'][1]['value'],1);self.assertEqual(block['source_files'],['sales.csv'])
        self.selection.clear(dict(dataset_id='one',context_fingerprint=self.desk.state('one')['documentary_context']['fingerprint'],actor='P',reason='Retirada'))
        block=self.block('sales');self.assertEqual(block['status'],'CLEARED');self.assertEqual(block['metrics'][1]['value'],0)
        self.assertEqual(block['received_file_count'],1)
    def test_receipt_counts_use_exact_company_cutoff_name_and_nature(self):
        self.receive();self.receive(company='other',filename='other.csv');self.receive(cutoff='2026-10-01',filename='other-date.csv')
        self.assertEqual(self.status()['ordinary_received_file_count'],1)
        with sqlite3.connect(self.path) as c:
            rows=c.execute("SELECT batch_id,metadata_json FROM received_company_batch WHERE company_id='one'").fetchall()
            bid,raw=next((bid,raw) for bid,raw in rows if json.loads(raw)['as_of_date']=='2026-09-30')
            meta=json.loads(raw);meta['material_nature']='REAL';c.execute('UPDATE received_company_batch SET metadata_json=? WHERE batch_id=?',(json.dumps(meta),bid))
        self.assertEqual(self.status()['ordinary_received_file_count'],0)
        meta['material_nature']='SYNTHETIC';meta['legal_name']='Otra razón social'
        with sqlite3.connect(self.path) as c:c.execute('UPDATE received_company_batch SET metadata_json=? WHERE batch_id=?',(json.dumps(meta),bid))
        self.assertEqual(self.status()['ordinary_received_file_count'],0)
    def test_stale_history_is_flagged_without_showing_selected_lines(self):
        self.selection=SalesHistorySelection(self.path);bid=self.receive();self.commit(self.selection.preview(self.request([bid])))
        with sqlite3.connect(self.path) as c:c.execute('UPDATE received_company_batch SET content=? WHERE batch_id=?',(b'changed',bid))
        block=self.block('sales');self.assertEqual(block['status'],'STALE');self.assertEqual(block['metrics'][1]['value'],0);self.assertEqual(block['source_files'],[])
    def test_zero_stock_is_known_but_unknown_reservations_are_not_available(self):
        state=self.desk.state('one');state['inventory']={'A':dict(unit='palets',physical='0',available=None)}
        report=describe_status(self.path,state);block=next(b for b in report['blocks'] if b['key']=='inventory')
        self.assertEqual(block['metrics'][0]['value'],1);self.assertEqual(block['metrics'][1]['value'],0)
        state['inventory']['A']['available']='0'
        block=next(b for b in describe_status(self.path,state)['blocks'] if b['key']=='inventory')
        self.assertEqual(block['metrics'][1]['value'],1)
        state['inventory']['A']['unit']='uds.'
        block=next(b for b in describe_status(self.path,state)['blocks'] if b['key']=='inventory')
        self.assertEqual(block['metrics'][0]['value'],0)
    def test_received_financial_rows_do_not_become_original_movements(self):
        before=self.block('finance');r=CompanyReception(self.path)
        read=r.read(b'Id;Direction;Amount;Currency;Due\nNEW;COBRO;500;EUR;31/10/2026\n','flows.csv',delimiter=';')
        p=r.preview(dict(upload=read['upload'],company_id='one',legal_name='Empresa sintética',material_nature='SYNTHETIC',as_of_date='2026-09-30',kind='cash_flow',number_format='ES',mapping=dict(flow_id=0,direction=1,amount=2,currency=3,due_date=4)))
        r.commit(p['ticket']);after=self.block('finance')
        self.assertEqual(after['metrics'],before['metrics']);self.assertEqual(after['received_file_count'],1)
        self.assertIn('no los incorpora automáticamente',after['description'])
    def test_unreadable_unselected_metadata_is_flagged_without_breaking_state(self):
        bid=self.receive()
        with sqlite3.connect(self.path) as c:c.execute('UPDATE received_company_batch SET metadata_json=? WHERE batch_id=?',('invalid json',bid))
        report=self.status();self.assertEqual(report['unclassified_company_file_count'],1);self.assertEqual(report['ordinary_received_file_count'],0)
    def test_empty_reference_blocks_do_not_look_configured(self):
        state=self.desk.state('one');state.update(articles=[],inventory={},customers=[],suppliers=[],history={},sales=dict(invoices=[]),purchase_documents=dict(invoices=[]))
        state['info']=dict(state['info'],record_counts={})
        report=describe_status(self.path,state)
        self.assertTrue(all(b['status']=='MISSING' for b in report['blocks']))
        self.assertTrue(all(all(m['value']==0 for m in b['metrics']) for b in report['blocks']))
    def test_tariff_origin_status_and_source_files_are_not_confused_with_validity(self):
        state=self.desk.state('one');state['articles'][0]['received_sale_tariff']=dict(status='ACTIVE',selection=dict(filename='tariff.csv'))
        block=next(b for b in describe_status(self.path,state)['blocks'] if b['key']=='catalogue')
        self.assertEqual(block['status'],'SELECTED');self.assertIn('tariff.csv',block['source_files'])
        self.assertIn('vigencia',block['description'])
        state['articles'][0]['received_sale_tariff']['status']='STALE'
        block=next(b for b in describe_status(self.path,state)['blocks'] if b['key']=='catalogue')
        self.assertEqual(block['status'],'STALE');self.assertNotIn('tariff.csv',block['source_files'])
