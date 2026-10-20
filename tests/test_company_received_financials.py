import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

from eios.company_received_financials import received_financials


class ReceivedFinancialsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db = Path(self.tmp.name) / 'company.db'
        self.ids = []
        with sqlite3.connect(self.db) as c:
            c.execute('CREATE TABLE received_company_batch(batch_id TEXT,metadata_json TEXT,records_json TEXT)')

    def add(self, kind, records, company='A', cutoff='2026-09-30'):
        bid = str(len(self.ids)).zfill(64)
        meta = dict(company_id=company,legal_name='Empresa '+company,material_nature='REAL',as_of_date=cutoff,kind=kind,filename=kind+'.csv',sheet='Datos',preview=[])
        with sqlite3.connect(self.db) as c:
            c.execute('INSERT INTO received_company_batch VALUES(?,?,?)',(bid,json.dumps(meta),json.dumps([dict(kind=kind,data=data,source_row=i+2) for i,data in enumerate(records)])))
        self.ids.append(bid)

    def flow(self, **changes):
        data = dict(flow_id='P1',direction='PAGO',amount='125.50',currency='EUR',due_date='2026-10-31',counterparty='Proveedor')
        data.update(changes)
        return data

    def report(self):
        return received_financials(self.db,self.ids)

    def test_sums_separate_currency_direction_and_maturity(self):
        self.add('cash_flow',[self.flow(),self.flow(flow_id='P2',amount='0.10'),self.flow(flow_id='P3',currency='USD'),self.flow(flow_id='C1',direction='COBRO'),self.flow(flow_id='P4',due_date='2026-09-30')])
        groups = {(x['currency'],x['direction'],x['maturity']):x for x in self.report()['flow_summaries']}
        self.assertEqual(len(groups),4)
        self.assertEqual(groups[('EUR','PAGO','AFTER_CUTOFF')]['amount'],'125.60')
        self.assertEqual(groups[('EUR','PAGO','BY_CUTOFF')]['amount'],'125.50')
        self.assertEqual(groups[('USD','PAGO','AFTER_CUTOFF')]['amount'],'125.50')
        self.assertEqual(groups[('EUR','COBRO','AFTER_CUTOFF')]['amount'],'125.50')

    def test_duplicate_reference_suppresses_total_without_dropping_sources(self):
        self.add('cash_flow',[self.flow()])
        self.add('cash_flow',[self.flow(),self.flow(flow_id='UNIQUE',currency='USD')])
        report = self.report()
        eur = next(x for x in report['flow_summaries'] if x['currency']=='EUR')
        usd = next(x for x in report['flow_summaries'] if x['currency']=='USD')
        self.assertIsNone(eur['amount'])
        self.assertEqual(eur['status'],'AMBIGUOUS_REFERENCES')
        self.assertEqual(usd['amount'],'125.50')
        self.assertEqual(len(report['flows']),3)
        self.assertEqual(report['flows'][0]['reference_status'],'REPEATED_REFERENCE')
        self.assertNotEqual(report['flows'][0]['source']['batch_id'],report['flows'][1]['source']['batch_id'])

    def test_conflicting_reference_blocks_both_affected_currency_groups(self):
        self.add('cash_flow',[self.flow(),self.flow(currency='USD')])
        report = self.report()
        self.assertTrue(all(x['amount'] is None for x in report['flow_summaries']))
        self.assertTrue(all(x['reference_status']=='CONFLICTING_REFERENCE' for x in report['flows']))

    def test_signed_accounts_are_not_aggregated_or_netted(self):
        self.add('balance',[dict(account_code='572',description='Bancos',balance='1000',currency='EUR'),dict(account_code='5720001',balance='-50.25',currency='EUR')])
        report = self.report()
        self.assertEqual(len(report['account_summaries']),2)
        self.assertEqual(report['account_summaries'][1]['balance'],'-50.25')
        self.assertNotIn('total_balance',report)
        self.assertEqual(report['flows'],[])
        self.assertEqual(report['flow_summaries'],[])

    def test_repeated_or_conflicting_balances_have_no_unique_value(self):
        record = dict(account_code='570',balance='650.00',currency='EUR')
        self.add('balance',[record])
        self.add('balance',[record])
        report = self.report()
        self.assertEqual(report['account_summaries'][0]['status'],'REPEATED_BALANCE')
        self.assertIsNone(report['account_summaries'][0]['balance'])
        self.assertEqual(len(report['balances']),2)
        self.add('balance',[dict(record,balance='651')])
        self.assertEqual(self.report()['account_summaries'][0]['status'],'CONFLICTING_BALANCE')

    def test_all_rows_exact_decimals_zero_unknown_and_support(self):
        self.add('cash_flow',[self.flow(flow_id=str(i),amount='0.01') for i in range(25)]+[self.flow(flow_id='LAST',amount='0',counterparty=None)])
        self.add('document',[])
        report = self.report()
        self.assertEqual(len(report['flows']),26)
        self.assertEqual(report['flow_summaries'][0]['amount'],'0.25')
        last = next(x for x in report['flows'] if x['data']['flow_id']=='LAST')
        self.assertEqual(last['source']['row'],27)
        self.assertIsNone(last['data']['counterparty'])
        self.assertEqual(report['support_documents'][0]['filename'],'document.csv')

    def test_read_only_no_admission_and_same_context_required(self):
        self.add('cash_flow',[self.flow()])
        before = self.db.read_bytes()
        report = self.report()
        self.assertEqual(self.db.read_bytes(),before)
        self.assertFalse(report['decision_authority'])
        self.assertEqual(report['operational_path'],'FORBIDDEN')
        self.assertEqual(report['admission_status'],'PENDING')
        with self.assertRaises(ValueError): received_financials(self.db,[])
        self.add('balance',[],company='B')
        with self.assertRaises(ValueError): self.report()
