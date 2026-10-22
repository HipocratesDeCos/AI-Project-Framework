import json
import sqlite3
import unittest
from copy import deepcopy
from tests import test_company_sales_negotiation as fixture


class SalesWorkflowTest(unittest.TestCase):
    tearDown=fixture.SalesNegotiationTest.tearDown
    add=fixture.SalesNegotiationTest.add
    financial_data=fixture.SalesNegotiationTest.financial_data
    set_policy=fixture.SalesNegotiationTest.set_policy
    quote=fixture.SalesNegotiationTest.quote

    def setUp(self):fixture.SalesNegotiationTest.setUp(self)

    def orientation(self,customer='C'):
        return self.desk.sales_orientation(dict(dataset_id='one',article_id='A',customer_id=customer))

    def overdue(self,**patch):
        d=dict(invoice_number='F1',customer_id='C',pending='10',original_due_date='2026-09-15',revised_due_date=None)
        d.update(patch);self.add('sales_installment','F1#Q1',d)
        self.offer['context_fingerprint']=self.desk.state('one')['documentary_context']['fingerprint']

    def test_selection_returns_source_references_default_previous_net_and_full_history(self):
        r=self.orientation()
        self.assertEqual(r['default_unit_price'],'90')
        self.assertEqual(r['default_price_source'],'LAST_CUSTOMER_SALE')
        self.assertEqual(r['price_reference']['recommended_unit_price'],'71.43')
        self.assertEqual(len(r['sales_history']),1)
        self.assertEqual(r['sales_history'][0]['source_refs'],[dict(document_ref='D',page=1)])
        self.assertEqual(self.orientation('')['default_unit_price'],'71.43')

    def test_documented_catalogue_price_takes_precedence_over_recalculation(self):
        with sqlite3.connect(self.path) as c:
            raw=json.loads(c.execute("SELECT record_json FROM documentary_company_record WHERE dataset_id='one' AND kind='article'").fetchone()[0])
            raw['data'].update(recommended_sale_price='123.45',sale_currency='EUR')
            c.execute("UPDATE documentary_company_record SET record_json=? WHERE dataset_id='one' AND kind='article'",(json.dumps(raw),))
        r=self.orientation()
        self.assertEqual(r['price_reference']['recommended_unit_price'],'123.45')
        self.assertEqual(r['price_reference']['price_source'],'DOCUMENTED_CATALOGUE_RECOMMENDED_SALE_PRICE')
        self.assertEqual(r['default_unit_price'],'90')

    def test_overdue_customer_with_deferred_payment_is_flagged_and_all_alternatives_require_advance(self):
        self.overdue()
        n=self.quote(negotiation_reason='PAYMENT_TERMS',proposal_origin='CUSTOMER',negotiation_note='Solicita financiar a 60 días')['negotiation']
        e=n['proposal_evaluation']
        self.assertEqual(e['status'],'NOT_APPROPRIATE_AS_PROPOSED')
        self.assertIn('OVERDUE_CUSTOMER_DEFERRED_COLLECTION',{r['code'] for r in e['reasons']})
        self.assertEqual(e['customer_credit']['default_history_status'],'NOT_VERIFIED')
        self.assertEqual(len(n['scenarios']),3)
        self.assertTrue(all(s['suggested_due_date']==self.offer['offer_date'] for s in n['scenarios']))
        self.assertFalse(e['automatic_acceptance'])
        self.assertEqual(e['protocol_execution_status'],'SALES_BINDING_PENDING')

    def test_agreed_revised_date_and_future_pending_are_not_reported_as_overdue(self):
        self.overdue(revised_due_date='2026-10-15')
        r=self.orientation()['customer_credit']
        self.assertEqual(r['overdue_installments'],[])
        self.assertEqual(r['completeness_status'],'NOT_ESTABLISHED')
        self.assertEqual(self.quote()['negotiation']['scenarios'],[])

    def test_no_automatic_alternatives_before_adverse_evaluation_or_unknown_credit_clearance(self):
        n=self.quote()['negotiation']
        self.assertEqual(n['scenarios'],[])
        self.assertEqual(n['proposal_evaluation']['status'],'PENDING_VALIDATION')
        self.assertEqual(n['proposal_evaluation']['customer_credit']['status'],'UNKNOWN')
        self.assertFalse(n['decision_authority'])
        n=self.quote(negotiation_reason='CLIENT_STOCK',proposal_origin='CUSTOMER')['negotiation']
        self.assertTrue(any('cantidad' in p for p in n['proposal_evaluation']['pending']))
        self.assertEqual(n['scenarios'],[])

    def test_ambiguous_last_prices_require_explicit_history_choice(self):
        self.add('sales_invoice_line','F1#2',dict(invoice_number='F1',article_id='A',line=2,quantity='1',net_amount='80',unit_price='80',unit_as_documented='palets',currency='EUR'))
        r=self.orientation()
        self.assertIsNone(r['default_unit_price'])
        self.assertEqual(r['default_price_source'],'AMBIGUOUS_HISTORY')
        self.assertEqual(len(r['sales_history']),2)

    def test_negotiation_reason_and_origin_are_explicit_and_preserved(self):
        for patch in [dict(negotiation_reason='BAD'),dict(proposal_origin='AUTO_APPROVED'),dict(negotiation_reason='OTHER',negotiation_note='')]:
            with self.subTest(patch=patch),self.assertRaises(ValueError):self.quote(**patch)
        result=self.desk.sales_offer(dict(self.offer,negotiation_reason='PRICE',proposal_origin='CUSTOMER',negotiation_note='Contraoferta del cliente'))
        saved=self.desk.state('one')['sales_proposals'][0]
        self.assertEqual(saved['negotiation']['proposal_evaluation']['negotiation_note'],'Contraoferta del cliente')

    def test_absolute_margin_restricts_gift_budget_and_all_counteroffers(self):
        from eios.company_parameters import save_parameters
        save_parameters(self.path,self.desk.store,dict(dataset_id='one',revision=1,actor='Director',reason='Límite absoluto explícito',values={'P-MGE-001':'20','P-MGE-002':'30','P-MGE-004':'100'}))
        self.offer['commercial_parameter_revision']=2
        n=self.quote()['negotiation']
        self.assertEqual(n['gift_budget'],'0.00')
        self.assertIn('CONTRIBUTION_BELOW_MINIMUM',{r['code'] for r in n['proposal_evaluation']['reasons']})
        from decimal import Decimal
        for index,scenario in enumerate(n['scenarios']):
            revenue=sum(Decimal(l['net_unit_price'])*Decimal(l['quantity']) for l in scenario['lines'])+Decimal(scenario['freight_charged'])
            cost=Decimal('110') if index==1 else Decimal('115')
            self.assertGreaterEqual(revenue-cost,100)

    def test_rounding_does_not_hide_a_minimum_margin_breach(self):
        from eios.company_sales_negotiation import analyze_offer
        args=dict(self.offer,seller_freight_cost='0',gift_description='',gift_cost='0',freight_net='0',lines=[dict(self.offer['lines'][0],unit_price='50',discount_value='0')])
        payload=self.desk.sales_offer(args,persist=False)
        payload['lines'][0]['orientation']['reference_unit_cost']='40.002'
        n=analyze_offer(payload,self.desk.sales_state('one'),args)
        self.assertEqual(n['contribution_margin_percent'],'20.00')
        self.assertTrue(n['below_declared_minimum'])
        self.assertIn('MARGIN_BELOW_MINIMUM',{r['code'] for r in n['proposal_evaluation']['reasons']})
