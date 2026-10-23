import base64
import csv
from io import StringIO
from pathlib import Path
import sqlite3
import tempfile
import unittest
from eios.company_reception import CompanyReception
from eios.company_sales_receivables import SalesReceivables, reconcile

class SalesReceivablesTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.db=Path(self.tmp.name)/'company.db';self.reception=CompanyReception(self.db)
        self.sale=dict(invoice_number='F1',issue_date='2026-09-30',customer_id='C1',article_id='A1',quantity='10',unit='uds.',net_amount='180',currency='EUR',description='Artículo',line_number='1',unit_price_before_discount='20',discount_percent='10',discount_amount='20',vat_percent='21',vat_amount='37.80',invoice_total='217.80')
        self.quotas=[dict(installment_ref='F1-'+str(n),customer_id='C1',invoice_number='F1',installment_number=str(n),due_date='2026-10-'+str(10+n),amount='72.60',currency='EUR',payment_method='Transferencia',pending_amount='72.60') for n in range(1,4)]
    def receive(self,kind,rows):
        headers=list(dict.fromkeys(k for row in rows for k in row));s=StringIO();w=csv.DictWriter(s,fieldnames=headers);w.writeheader();w.writerows(rows)
        return self.receive_bytes(kind,s.getvalue().encode(),headers)
    def receive_bytes(self,kind,content,headers):
        read=self.reception.read(content,kind+'.csv')
        p=self.reception.preview(dict(upload=read['upload'],company_id='DEMO',legal_name='Empresa ficticia',material_nature='SYNTHETIC',as_of_date='2026-09-30',kind=kind,number_format='EN',mapping={h:i for i,h in enumerate(headers)}))
        self.assertEqual(p['error_count'],0,p)
        result=self.reception.commit(p['ticket'])
        return self.reception.batches()[0]['batch_id'] if 'batch_id' not in result else result['batch_id']
    def inputs(self):return [self.receive('sales_line',[self.sale]),self.receive('sales_installment',self.quotas)]
    def test_three_installments_roundtrip_no_duplicate_or_financial_promotion(self):
        ids=self.inputs();service=SalesReceivables(self.db);report=service.check(dict(batch_ids=ids))
        self.assertEqual(report['candidate_count'],3);self.assertEqual(report['invoices'][0]['status'],'RECONCILED')
        export=service.export(dict(ticket=report['ticket'],acknowledge_draft=True));content=base64.b64decode(export['content_base64'])
        headers=next(csv.reader(StringIO(content.decode('utf-8-sig'))))
        ids.append(self.receive_bytes('cash_flow',content,headers));again=reconcile(self.db,ids)
        self.assertEqual(again['candidate_count'],0);self.assertEqual(again['result'],'NO_NEW_COLLECTIONS')
        self.assertTrue(all(q['status']=='ALREADY_IN_FORECAST' for q in again['invoices'][0]['quotas']))
        with sqlite3.connect(self.db) as c:self.assertIsNone(c.execute("SELECT name FROM sqlite_master WHERE name='documentary_company_record'").fetchone())
    def test_original_amount_reconciles_but_only_pending_is_exported(self):
        self.quotas[0]['pending_amount']='0';self.quotas[1]['pending_amount']='12.60'
        report=reconcile(self.db,self.inputs());self.assertEqual(report['candidate_count'],2)
        self.assertEqual([r['amount'] for r in report['draft_collections']],['12.60','72.60'])
    def test_missing_pending_never_assumes_full_debt(self):
        del self.quotas[0]['pending_amount'];r=reconcile(self.db,self.inputs())
        self.assertEqual(r['candidate_count'],0);self.assertIn('PENDING_AMOUNT_UNKNOWN',[i['code'] for i in r['invoices'][0]['issues']])
    def test_unknown_vat_and_partial_invoice_block_export(self):
        del self.sale['vat_amount'];del self.sale['vat_percent'];self.sale['invoice_total']='300'
        r=reconcile(self.db,self.inputs());self.assertEqual(r['candidate_count'],0)
        self.assertTrue({'MISSING_VAT','INSTALLMENTS_TOTAL_MISMATCH'}<={i['code'] for i in r['invoices'][0]['issues']})
    def test_percentage_can_calculate_vat_with_explicit_provenance(self):
        del self.sale['vat_amount'];r=reconcile(self.db,self.inputs())
        self.assertEqual(r['candidate_count'],3);self.assertEqual(r['invoices'][0]['vat_basis'],['CALCULATED_FROM_DECLARED_RATE'])
    def test_unlinked_same_amount_date_is_blocked_then_explicit_link_resolves(self):
        ids=self.inputs();flow=dict(flow_id='EXISTING',direction='COBRO',amount='72.60',currency='EUR',due_date=self.quotas[0]['due_date'])
        fid=self.receive('cash_flow',[flow]);r=reconcile(self.db,ids+[fid]);self.assertEqual(r['candidate_count'],0)
        self.assertIn('POSSIBLE_DUPLICATE_COLLECTION',[i['code'] for i in r['invoices'][0]['issues']])
        self.quotas[0]['flow_id']='EXISTING';new=self.receive('sales_installment',self.quotas)
        r=reconcile(self.db,[ids[0],new,fid]);self.assertEqual(r['candidate_count'],2)
    def test_source_tampering_blocks_export(self):
        ids=self.inputs();s=SalesReceivables(self.db);r=s.check(dict(batch_ids=ids))
        with sqlite3.connect(self.db) as c:c.execute('UPDATE received_company_batch SET content=? WHERE batch_id=?',(b'changed',ids[0]))
        with self.assertRaises(ValueError):s.export(dict(ticket=r['ticket'],acknowledge_draft=True))
    def test_export_requires_acknowledgment_and_single_use_ticket(self):
        s=SalesReceivables(self.db);r=s.check(dict(batch_ids=self.inputs()))
        with self.assertRaises(ValueError):s.export(dict(ticket=r['ticket']))
        s.export(dict(ticket=r['ticket'],acknowledge_draft=True))
        with self.assertRaises(ValueError):s.export(dict(ticket=r['ticket'],acknowledge_draft=True))
    def test_discount_is_checked_against_already_net_amount(self):
        self.sale['net_amount']='160'
        with self.assertRaises(AssertionError):self.receive('sales_line',[self.sale])
    def test_mixed_companies_are_rejected(self):
        ids=self.inputs()
        with sqlite3.connect(self.db) as c:c.execute("UPDATE received_company_batch SET metadata_json=replace(metadata_json,'Empresa ficticia','Otra empresa') WHERE batch_id=?",(ids[1],))
        with self.assertRaises(ValueError):reconcile(self.db,ids)
    def test_multiple_lines_repeat_header_total_only_once(self):
        self.sale['invoice_total']='435.60';second=dict(self.sale,article_id='A2',line_number='2')
        for q in self.quotas:q['amount']='145.20';q['pending_amount']='145.20'
        ids=[self.receive('sales_line',[self.sale,second]),self.receive('sales_installment',self.quotas)]
        r=reconcile(self.db,ids);self.assertEqual(r['candidate_count'],3)
        self.assertEqual(r['invoices'][0]['documented_invoice_total'],'435.60')
    def test_duplicate_installment_across_sources_blocks_invoice(self):
        ids=self.inputs();copy=dict(self.quotas[0],payment_method='Efectivo')
        ids.append(self.receive('sales_installment',[copy]));r=reconcile(self.db,ids)
        self.assertEqual(r['candidate_count'],0)
        self.assertIn('DUPLICATE_INSTALLMENT_REF',[i['code'] for i in r['invoices'][0]['issues']])
    def test_expired_preparation_requires_new_check(self):
        clock=[0];s=SalesReceivables(self.db,clock=lambda:clock[0]);r=s.check(dict(batch_ids=self.inputs()));clock[0]=601
        with self.assertRaises(ValueError):s.export(dict(ticket=r['ticket'],acknowledge_draft=True))
    def test_legacy_sales_row_has_no_new_unmapped_fields(self):
        from eios.company_tables import read_table,normalize
        row={k:self.sale[k] for k in ['invoice_number','issue_date','customer_id','article_id','quantity','unit','net_amount','currency']}
        headers=list(row);s=StringIO();w=csv.writer(s);w.writerow(headers);w.writerow(row.values())
        n=normalize(read_table(s.getvalue().encode(),'legacy.csv'),'sales_line',{h:i for i,h in enumerate(headers)},'2026-09-30','EN')
        self.assertEqual(n['records'][0]['data'],row)
