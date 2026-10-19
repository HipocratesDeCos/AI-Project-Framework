from pathlib import Path
import sqlite3
import tempfile
import unittest

from eios.company_tables import read_table,normalize
from eios.company_reception import CompanyReception


class SalesStockReceptionTest(unittest.TestCase):
    def sales(self, row='F-1;30/09/2026;C01;SKU-001;2;uds.;125,50;EUR'):
        content=('Factura;Fecha;Cliente;SKU;Cantidad;Unidad;Neto;Moneda\n'+row+'\n').encode()
        table=read_table(content,'ventas.csv',delimiter=';')
        fields=['invoice_number','issue_date','customer_id','article_id','quantity','unit','net_amount','currency']
        return content,table,dict(zip(fields,range(8)))

    def test_sales_source_amount_and_customer_are_preserved(self):
        content,table,mapping=self.sales()
        checked=normalize(table,'sales_line',mapping,'2026-09-30','ES')
        record=checked['records'][0]
        self.assertEqual(checked['error_count'],0)
        self.assertEqual(record['source_row'],2)
        self.assertEqual(record['data']['net_amount'],'125.50')
        self.assertEqual(record['data']['customer_id'],'C01')
        self.assertNotIn('supplier_id',record['data'])

    def test_sales_future_date_credit_and_missing_customer_block_save(self):
        for row in ['F-1;01/10/2026;C01;SKU-001;2;uds.;125,50;EUR',
                    'F-1;30/09/2026;C01;SKU-001;-2;uds.;-125,50;EUR',
                    'F-1;30/09/2026;;SKU-001;2;uds.;125,50;EUR']:
            _,table,mapping=self.sales(row)
            result=normalize(table,'sales_line',mapping,'2026-09-30','ES')
            self.assertEqual(result['error_count'],1)
            self.assertEqual(result['records'],[])
        _,table,mapping=self.sales()
        table['rows'].append(dict(row=3,values=list(table['rows'][0]['values'])))
        checked=normalize(table,'sales_line',mapping,'2026-09-30','ES')
        self.assertEqual(len(checked['records']),2)
        self.assertEqual(len(checked['warnings']),1)

    def test_inventory_can_receive_thresholds_without_inventing_reservations(self):
        table=read_table(b'SKU;Unit;Physical;Minimum;Safety;Point;Lead\nA;uds.;25;0;3;10;7\n','stock.csv',delimiter=';')
        mapping=dict(article_id=0,unit=1,physical=2,minimum_stock=3,safety_stock=4,reorder_point=5,lead_time_days=6)
        checked=normalize(table,'inventory',mapping,'2026-09-30','ES')
        self.assertEqual(checked['error_count'],0)
        data=checked['records'][0]['data']
        self.assertEqual(data['minimum_stock'],'0')
        self.assertEqual(data['reorder_point'],'10')
        self.assertEqual(data['lead_time_days'],'7')
        self.assertIsNone(data['reserved'])
        self.assertIsNone(data['available'])
        self.assertNotIn('alarm_active',data)
        plain=normalize(table,'inventory',dict(article_id=0,unit=1,physical=2),'2026-09-30','ES')['records'][0]['data']
        self.assertFalse({'minimum_stock','safety_stock','reorder_point','lead_time_days'} & plain.keys())

    def test_separate_policy_requires_a_value_and_rejects_invalid_days(self):
        table=read_table(b'SKU;Unit;Minimum;Days\nA;uds.;0;7\n','rules.csv',delimiter=';')
        mapping=dict(article_id=0,unit=1,minimum_stock=2,lead_time_days=3)
        self.assertEqual(normalize(table,'stock_policy',mapping,'2026-09-30','ES')['error_count'],0)
        empty=dict(article_id=0,unit=1)
        self.assertEqual(normalize(table,'stock_policy',empty,'2026-09-30','ES')['error_count'],1)
        for value in ('-1','2,5'):
            table['rows'][0]['values'][3]=value
            self.assertEqual(normalize(table,'stock_policy',mapping,'2026-09-30','ES')['error_count'],1)
        table['rows'][0]['values'][3]='7'
        table['rows'][0]['values'][2]='-5'
        self.assertEqual(normalize(table,'stock_policy',mapping,'2026-09-30','ES')['error_count'],1)

    def test_sales_and_policy_persist_without_admission_or_core_tables(self):
        content,_,mapping=self.sales()
        with tempfile.TemporaryDirectory() as temp:
            db=Path(temp)/'received.sqlite3';reception=CompanyReception(db)
            file=reception.read(content,'ventas.csv',delimiter=';')
            context=dict(company_id='NEW',legal_name='New company',material_nature='REAL',as_of_date='2026-09-30',number_format='ES')
            report=reception.preview(dict(context,upload=file['upload'],kind='sales_line',mapping=mapping))
            first=reception.commit(report['ticket'])
            file=reception.read(b'SKU;Unit;Min\nSKU-001;uds.;0\n','minimos.csv',delimiter=';')
            report=reception.preview(dict(context,upload=file['upload'],kind='stock_policy',mapping=dict(article_id=0,unit=1,minimum_stock=2)))
            second=reception.commit(report['ticket'])
            self.assertNotEqual(first['batch_id'],second['batch_id'])
            for batch in reception.batches():
                self.assertEqual(batch['admission_status'],'PENDING')
                self.assertFalse(batch['decision_authority'])
                self.assertEqual(batch['operational_path'],'FORBIDDEN')
                self.assertEqual(batch['material_nature'],'REAL')
            with sqlite3.connect(db) as c:
                tables={r[0] for r in c.execute("select name from sqlite_master where type='table'")}
            self.assertEqual(tables,{'received_company','received_company_batch'})
