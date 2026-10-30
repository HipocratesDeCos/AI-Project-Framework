import unittest
import sqlite3
from tests.test_company_sales_negotiation import SalesNegotiationTest as Fixture
from eios.company_reception import CompanyReception
from eios.company_sales_treasury import options,save


class SalesTreasuryTest(unittest.TestCase):
    setUp=Fixture.setUp
    tearDown=Fixture.tearDown
    add=Fixture.add
    financial_data=Fixture.financial_data
    set_policy=Fixture.set_policy

    def receive(self,kind='balance',company='one',rows=None,name='Empresa sintética'):
        reader=CompanyReception(self.path)
        if kind=='balance':
            raw=('Cuenta;Saldo;Moneda\n'+(rows or '570;650;EUR\n572;58300;EUR\n572001;100;EUR\n')).encode();mapping=dict(account_code=0,balance=1,currency=2)
        else:
            raw=b'Ref;Tipo;Importe;Moneda;Fecha\nFLOW1;PAGO;500;EUR;2026-10-15\n';mapping=dict(flow_id=0,direction=1,amount=2,currency=3,due_date=4)
        r=reader.read(raw,kind+'.csv');p=reader.preview(dict(upload=r['upload'],company_id=company,legal_name=name,material_nature='SYNTHETIC',as_of_date='2026-09-30',kind=kind,number_format='ES',mapping=mapping))
        self.assertEqual(p['error_count'],0)
        return reader.commit(p['ticket'])['batch_id']

    def request(self,bid,flow=None,codes=None):
        batches=options(self.path,'one')['batches']
        return dict(dataset_id='one',context_fingerprint=self.desk.state('one')['documentary_context']['fingerprint'],balance_batch=bid,flow_batch=flow,account_codes=codes or ['570','572'],source_fingerprints={b['batch_id']:b['fingerprint'] for b in batches if b['batch_id'] in (bid,flow)},actor='Responsable',reason='Referencia de prueba',acknowledge=True)

    def test_selected_balances_and_replacement_flows_reach_sales_and_stale_fails_closed(self):
        bid=self.receive();flow=self.receive('cash_flow');before=self.desk.sales_state('one');request=self.request(bid,flow)
        save(self.path,request);after=self.desk.sales_state('one');finance=after['sales_financial_context']
        self.assertEqual(finance['financial_snapshot']['available_treasury'],'58950')
        self.assertEqual(len(finance['cash_flows']),1)
        self.assertEqual(finance['record_counts']['cash_flow'],1)
        self.assertEqual(finance['cash_flows'][0]['canonical']['evidence_state'],'NOT_EVIDENCED')
        self.assertIsNone(finance['opening_treasury_reconciled'])
        self.assertNotEqual(before['documentary_context']['fingerprint'],after['documentary_context']['fingerprint'])
        with self.assertRaises(ValueError):save(self.path,request)
        with sqlite3.connect(self.path) as c:c.execute('UPDATE received_company_batch SET content=? WHERE batch_id=?',(b'tamper',bid))
        stale=self.desk.sales_state('one')['sales_financial_context']
        self.assertIsNone(stale['financial_snapshot']);self.assertEqual(stale['treasury_selection']['status'],'STALE')

    def test_parent_child_and_foreign_sources_rejected_and_clear_is_reversible(self):
        bid=self.receive();foreign=self.receive(company='two',name='Otra empresa')
        self.assertNotIn(foreign,[b['batch_id'] for b in options(self.path,'one')['batches']])
        with self.assertRaises(ValueError):save(self.path,self.request(bid,codes=['572','572001']))
        with self.assertRaises(ValueError):save(self.path,self.request(foreign))
        initial=self.desk.sales_state('one')['sales_financial_context']['financial_snapshot']
        save(self.path,self.request(bid));clear=self.request(bid);clear['clear']=True;save(self.path,clear)
        self.assertEqual(self.desk.sales_state('one')['sales_financial_context']['financial_snapshot'],initial)

    def test_acknowledgement_required_and_negative_balances_not_assumed_available(self):
        bid=self.receive(rows='570;-1;EUR\n572;100;EUR\n')
        r=self.request(bid);r['acknowledge']=False
        with self.assertRaises(ValueError):save(self.path,r)
        r['acknowledge']=True
        with self.assertRaises(ValueError):save(self.path,r)

    def test_financial_engine_uses_selected_sources_and_saved_offer_is_frozen(self):
        from tests.test_company_finance_activation import FinanceActivationTest
        FinanceActivationTest.prepare(self,revision=1)
        FinanceActivationTest.activate(self,revision=2)
        bid=self.receive();flow=self.receive('cash_flow');save(self.path,self.request(bid,flow))
        request=dict(self.offer,commercial_parameter_revision=2,context_fingerprint=self.desk.state('one')['documentary_context']['fingerprint'])
        offer=self.desk.sales_offer(request)
        plan=self.desk.sales_cash_plan(dict(dataset_id='one',proposal_id=offer['proposal_id'],revision=0,actor='Comercial',acknowledge=True,documentary_context_fingerprint=request['context_fingerprint'],rows=[dict(flow_type='COLLECTION',amount=offer['total'],due_date=offer['due_date'],disposition='NEW_DECLARATION',note='Cobro de prueba')]),save=True)['plan']
        execution=plan['execution']
        self.assertEqual(execution['status'],'EXECUTED',execution['message'])
        self.assertEqual(execution['finance_input']['snapshot']['available_treasury'],'58950')
        self.assertEqual(len(execution['finance_input']['cash_flows']),2)
        self.assertFalse(plan['decision_authority'])
        self.assertEqual(execution['with_declared_plan']['projection']['status'],'NOT_EVIDENCED')
        clear=self.request(bid);clear['clear']=True;save(self.path,clear)
        read=self.desk.sales_cash_plan(dict(dataset_id='one',proposal_id=offer['proposal_id']))
        self.assertFalse(read['can_edit']);self.assertEqual(read['plan'],plan)

    def test_same_legal_name_with_different_internal_id_requires_explicit_confirmation(self):
        bid=self.receive(company='Cliente_001',name='EMPRESA SINTÉTICA.')
        item=next(x for x in options(self.path,'one')['batches'] if x['batch_id']==bid)
        self.assertTrue(item['requires_identity_confirmation'])
        request=self.request(bid)
        with self.assertRaises(ValueError):save(self.path,request)
        request['confirm_identity']=True;save(self.path,request)
        finance=self.desk.sales_state('one')['sales_financial_context']
        self.assertEqual(finance['financial_snapshot']['available_treasury'],'58950')
        self.assertEqual(finance['treasury_selection']['status'],'SELECTED_DECLARATION_NOT_RECONCILED')

    def test_confirmation_never_allows_a_different_legal_name(self):
        bid=self.receive(company='other',name='Otra empresa')
        result=options(self.path,'one')
        self.assertTrue(any(x['company_id']=='other' for x in result['excluded']))
        request=self.request(bid);request['confirm_identity']=True
        with self.assertRaises(ValueError):save(self.path,request)
