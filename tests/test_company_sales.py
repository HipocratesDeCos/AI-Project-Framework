from copy import deepcopy
import unittest

from eios.company_sales import documented_sales


class Store:
    def __init__(self,rows): self.rows=rows
    def records(self,dataset,kind): return self.rows.get(kind,[]) if dataset=='one' else []


class DocumentedSalesTest(unittest.TestCase):
    def setUp(self):
        self.header=dict(record_id='F1',data=dict(invoice_number='F1',customer_id='C1',issue_date_pdf='2026-09-20',economic_position='ISSUED_BY_CUTOFF',currency='EUR',net_amount='100.00',vat_amount='21.00',gross_amount='121.00',pending='101.00'),source_refs=[dict(document_ref='D1',page=1)])
        self.line=dict(record_id='F1#1',data=dict(invoice_number='F1',line=1,description='Documented product',article_id=None,unit_as_documented=None,quantity='2',unit_price='50.00',net_amount='100.00',currency='EUR'),source_refs=[dict(document_ref='D1',page=1,section='Line 1')])
        self.rows=dict(customer=[dict(data=dict(customer_id='C1')),dict(data=dict(customer_id='C2'))],sales_invoice=[self.header],sales_invoice_line=[self.line])

    def read(self,dataset='one'): return documented_sales(Store(self.rows),dataset,'2026-09-30')

    def test_source_shape_amounts_and_missing_sku_unit_preserved(self):
        result=self.read();invoice=result['invoices'][0];line=invoice['lines'][0]
        self.assertEqual(invoice['customer_id'],'C1')
        self.assertEqual(invoice['gross_amount'],'121.00')
        self.assertEqual(invoice['pending'],'101.00')
        self.assertIsNone(invoice['collected_at_cutoff'])
        self.assertIsNone(line['article_id'])
        self.assertIsNone(line['unit'])
        self.assertEqual(line['description'],'Documented product')
        self.assertEqual(line['source_refs'],self.line['source_refs'])
        line['source_refs'][0]['document_ref']='changed response'
        self.assertEqual(self.line['source_refs'][0]['document_ref'],'D1')

    def test_dataset_scope_and_customer_binding(self):
        self.assertEqual(self.read('two')['invoices'],[])
        self.header['data']['customer_id']='OTHER'
        result=self.read()
        self.assertEqual(result['invoices'],[])
        self.assertEqual(len(result['excluded']),1)
        self.assertEqual(result['ignored_lines'],1)

    def test_future_missing_date_and_unissued_invoices_not_history(self):
        for patch in [dict(issue_date_pdf='2026-10-01'),dict(issue_date_pdf='invalid'),dict(issue_date_pdf=None),dict(economic_position='PLANNED')]:
            original=deepcopy(self.header['data']);self.header['data'].update(patch)
            result=self.read()
            self.assertEqual(result['invoices'],[])
            self.assertEqual(len(result['excluded']),1)
            self.header['data']=original

    def test_orphan_and_foreign_customer_lines_are_not_reassigned(self):
        self.line['data']['invoice_number']='MISSING'
        self.assertEqual(self.read()['invoices'][0]['lines'],[])
        self.line['data']['invoice_number']='F1'
        self.line['data']['customer_id']='C2'
        result=self.read()
        self.assertEqual(result['invoices'][0]['lines'],[])
        self.assertEqual(result['ignored_lines'],1)
        self.assertTrue(result['invoices'][0]['warnings'])
        self.header['data']['invoice_number']='other-reference'
        self.assertEqual(self.read()['invoices'],[])

    def test_invalid_amounts_remain_unknown_and_currency_conflict_visible(self):
        self.header['data']['net_amount']='NaN'
        self.line['data']['quantity']=''
        self.line['data']['currency']='USD'
        invoice=self.read()['invoices'][0]
        self.assertIsNone(invoice['net_amount'])
        self.assertIsNone(invoice['lines'][0]['quantity'])
        self.assertEqual(invoice['currency'],'EUR')
        self.assertEqual(invoice['lines'][0]['currency'],'USD')
        self.assertTrue(invoice['warnings'])

    def test_order_of_invoices_and_lines(self):
        newer=deepcopy(self.header);newer['record_id']='F2';newer['data'].update(invoice_number='F2',customer_id='C2',issue_date_pdf='2026-09-30')
        self.rows['sales_invoice'].append(newer)
        second=deepcopy(self.line);second['record_id']='F1#2';second['data']['line']=2
        self.rows['sales_invoice_line']=[second,self.line]
        result=self.read()
        self.assertEqual([i['invoice_number'] for i in result['invoices']],['F2','F1'])
        self.assertEqual([l['line'] for l in result['invoices'][1]['lines']],[1,2])
