import unittest
import sqlite3
from tests.test_company_sales_negotiation import SalesNegotiationTest as Fixture
from eios.company_reception import CompanyReception
from eios.company_sales_quality import report,save


class SalesQualityTest(unittest.TestCase):
    setUp=Fixture.setUp
    tearDown=Fixture.tearDown
    add=Fixture.add
    financial_data=Fixture.financial_data
    set_policy=Fixture.set_policy

    def receive(self,kind,raw,name,mapping=None):
        reader=CompanyReception(self.path);r=reader.read(raw,name)
        p=reader.preview(dict(upload=r['upload'],company_id='one',legal_name='Empresa sintética',material_nature='SYNTHETIC',as_of_date='2026-09-30',kind=kind,number_format='ES',mapping=mapping or {}))
        self.assertEqual(p['error_count'],0,p)
        return reader.commit(p['ticket'])['batch_id']

    def inputs(self,pending='100'):
        self.receive('balance',b'Cuenta;Saldo;Moneda\n572;58300;EUR\n','balance.csv',dict(account_code=0,balance=1,currency=2))
        self.receive('cash_flow',b'Ref;Tipo;Importe;Moneda;Fecha;Cliente;Factura;Cuota\nC1;COBRO;100;EUR;2026-10-15;C;F1;Q1\nP1;PAGO;50;EUR;2026-10-15;;;\n','flujos.csv',dict(flow_id=0,direction=1,amount=2,currency=3,due_date=4,customer_id=5,invoice_number=6,installment_ref=7))
        self.receive('sales_installment',f'Cuota;Cliente;Factura;Numero;Fecha;Importe;Moneda;Forma;Pendiente\nQ1;C;F1;1;2026-10-15;100;EUR;Transferencia;{pending}\n'.encode(),'cuotas.csv',dict(installment_ref=0,customer_id=1,invoice_number=2,installment_number=3,due_date=4,amount=5,currency=6,payment_method=7,pending_amount=8))
        self.receive('document',b'%PDF-1.4\nsynthetic independent bank support','extracto.pdf')

    def status(self):
        state=self.desk.sales_state('one')
        return state,state['sales_quality']

    def request(self):
        state,r=self.status();doc=next(s['source_id'] for s in r['sources'] if s['kind']=='document')
        return dict(dataset_id='one',context_fingerprint=state['documentary_context']['fingerprint'],basis_fingerprint=r['basis_fingerprint'],revision=r['review_revision'],actor='Revisor de prueba',note='Contraste del expediente sintético',acknowledge=True,movement_links=[dict(flow_id='P1',source_id=doc,note='Lectura declarada del soporte del pago')],account_observations=[dict(account_code='572',source_id=doc,observed_balance='58300',currency='EUR',as_of_date='2026-09-30')],coverage='DECLARED_COMPLETE',coverage_until='2026-12-31',coverage_sources=[doc])

    def test_technical_matching_declaration_and_reconciliation_never_promote_evidence(self):
        self.inputs();state,r=self.status()
        self.assertEqual(r['summary']['matched'],1)
        self.assertEqual(r['summary']['pending'],1)
        old=state['documentary_context']['fingerprint'];req=self.request();save(self.path,req,state['sales_financial_context'])
        state,r=self.status()
        self.assertEqual(r['review_status'],'CURRENT')
        self.assertEqual(r['summary']['declared_reviewed'],1)
        self.assertEqual(r['accounts'][0]['status'],'DECLARED_MATCH')
        self.assertEqual(r['coverage'],'DECLARED_COMPLETE')
        self.assertNotEqual(old,state['documentary_context']['fingerprint'])
        self.assertTrue(all(f['canonical']['evidence_state']=='NOT_EVIDENCED' for f in state['sales_financial_context']['cash_flows']))
        self.assertIsNone(state['sales_financial_context']['opening_treasury_reconciled'])
        self.assertFalse(r['decision_authority']);self.assertEqual(r['quality_evaluation_status'],'NOT_EXECUTED')
        with self.assertRaises(ValueError):save(self.path,req,state['sales_financial_context'])

    def test_discrepancy_cannot_be_removed_by_manual_link(self):
        self.inputs(pending='80');state,r=self.status()
        self.assertEqual(r['summary']['discrepancies'],1)
        req=self.request();quota=next(s['source_id'] for s in r['sources'] if s['kind']=='sales_installment')
        req['movement_links']=[dict(flow_id='C1',source_id=quota,note='No se fuerza una coincidencia')]
        with self.assertRaises(ValueError):save(self.path,req,state['sales_financial_context'])

    def test_changed_sources_invalidate_review_and_old_offer_remains_frozen(self):
        self.inputs();state,_=self.status();save(self.path,self.request(),state['sales_financial_context'])
        state,r=self.status();offer=self.desk.sales_offer(dict(self.offer,context_fingerprint=state['documentary_context']['fingerprint']))
        self.add('cash_count','CASH',dict(as_of_date='2026-09-30',currency='EUR',cash_total='1'))
        state,r=self.status()
        self.assertEqual(r['review_status'],'STALE')
        self.assertEqual(r['accounts'][0]['status'],'PENDING')
        self.assertEqual(offer['negotiation']['proposal_evaluation']['checks'][3]['status'],'INFO')

    def test_wrong_observation_scope_and_missing_ack_are_rejected(self):
        self.inputs();state,_=self.status()
        for patch in [dict(acknowledge=False),dict(actor=''),dict(coverage_until='2026-01-01')]:
            with self.subTest(patch=patch),self.assertRaises(ValueError):save(self.path,dict(self.request(),**patch),state['sales_financial_context'])
        req=self.request();req['account_observations'][0]['as_of_date']='2026-10-01'
        with self.assertRaises(ValueError):save(self.path,req,state['sales_financial_context'])

    def test_difference_is_recorded_without_becoming_a_reconciliation(self):
        self.inputs();state,_=self.status();req=self.request();req['account_observations'][0]['observed_balance']='58000'
        save(self.path,req,state['sales_financial_context']);_,r=self.status()
        self.assertEqual(r['accounts'][0]['status'],'DIFFERENCE')
        self.assertEqual(r['status'],'DISCREPANCIES')

    def test_at_sight_credit_check_is_informative_even_with_old_arrears(self):
        self.inputs();self.add('sales_installment','F1#Q1',dict(invoice_number='F1',customer_id='C',pending='10',currency='EUR',original_due_date='2026-09-15',revised_due_date=None))
        state,_=self.status();offer=dict(self.offer,due_date=self.offer['offer_date'],context_fingerprint=state['documentary_context']['fingerprint'])
        result=self.desk.sales_offer(offer,persist=False);credit=next(c for c in result['negotiation']['proposal_evaluation']['checks'] if c['code']=='CREDIT')
        self.assertEqual(credit['status'],'INFO');self.assertIn('Sin aplazamiento',credit['message'])
        self.assertFalse(any(r['code']=='OVERDUE_CUSTOMER_DEFERRED_COLLECTION' for r in result['negotiation']['proposal_evaluation']['reasons']))
        offer['due_date']='2026-11-30';result=self.desk.sales_offer(offer,persist=False)
        self.assertTrue(any(r['code']=='OVERDUE_CUSTOMER_DEFERRED_COLLECTION' for r in result['negotiation']['proposal_evaluation']['reasons']))

    def test_equivalent_quota_exports_do_not_conflict_on_decimal_format(self):
        self.inputs()
        self.add('sales_installment','Q1',dict(invoice_number='F1',customer_id='C',pending='100.00',currency='EUR',original_due_date='2026-10-15',revised_due_date=None))
        _,r=self.status()
        self.assertEqual(r['summary']['matched'],1)
        self.assertEqual(r['summary']['discrepancies'],0)

    def test_complete_coverage_cannot_hide_a_missing_quota(self):
        self.inputs()
        self.add('sales_installment','Q2',dict(invoice_number='F2',customer_id='C',pending='25',currency='EUR',original_due_date='2026-10-20',revised_due_date=None))
        state,r=self.status()
        self.assertEqual(len(r['quota_gaps']),1)
        with self.assertRaisesRegex(ValueError,'Hay cuotas'):
            save(self.path,self.request(),state['sales_financial_context'])
        req=self.request();req['coverage']='DECLARED_INCOMPLETE'
        save(self.path,req,state['sales_financial_context'])
        self.assertEqual(self.status()[1]['coverage'],'DECLARED_INCOMPLETE')
