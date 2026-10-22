from copy import deepcopy
from decimal import Decimal
import unittest
from tests import test_company_sales_proposals as fixture
from tests import test_company_financial_context as finance_fixture
from eios.company_parameters import save_parameters
from eios.company_sales_proposals import printable_offer


class SalesNegotiationTest(unittest.TestCase):
    tearDown=fixture.SalesOfferTest.tearDown
    add=finance_fixture.FinancialContextTest.add
    financial_data=finance_fixture.FinancialContextTest.financial_data

    def setUp(self):
        fixture.SalesOfferTest.setUp(self)
        self.financial_data()
        self.set_policy()
        self.state=self.desk.sales_state('one')
        self.offer.update(context_fingerprint=self.state['documentary_context']['fingerprint'],
            commercial_parameter_revision=1,seller_freight_cost='10',gift_description='Gorra sintética',gift_cost='5')

    def set_policy(self,revision=0,minimum='20',target='30'):
        return save_parameters(self.path,self.desk.store,dict(dataset_id='one',revision=revision,actor='Director sintético',reason='Prueba comercial explícita',acknowledge_critical=True,values={'P-MGE-001':minimum,'P-MGE-002':target}))

    def quote(self,**patch):
        return self.desk.sales_offer(dict(self.offer,**patch),persist=False)

    def test_origin_is_parameter_based_and_stays_constant_while_negotiating(self):
        a=self.quote()['negotiation']
        b=self.quote(lines=[dict(self.offer['lines'][0],unit_price='60',discount_value='5')])['negotiation']
        self.assertEqual(a['origin_prices'],b['origin_prices'])
        self.assertEqual(a['origin_prices'][0]['recommended_unit_price'],'71.43')
        self.assertEqual(a['origin_prices'][0]['maximum_reference_discount_percent'],'12.50')
        self.assertEqual(len(a['scenarios']),0)
        self.assertEqual(len(b['scenarios']),3)
        self.assertEqual(a['contribution_margin_percent'],'39.47')
        self.assertEqual(a['gift_budget'],'42.00')
        self.assertTrue(b['below_declared_minimum'])
        for scenario in b['scenarios']:
            self.assertGreaterEqual(Decimal(scenario['margin_percent']),20)
            self.assertTrue(all(Decimal(l['net_unit_price'])>=0 for l in scenario['lines']))

    def test_financial_inputs_are_bound_without_inventing_a_sales_projection(self):
        n=self.quote(lines=[dict(self.offer['lines'][0],unit_price='60')])['negotiation'];f=n['financial_context']
        self.assertEqual(f['treasury'],'5000')
        self.assertEqual(f['working_capital'],'8000')
        self.assertEqual(f['payments_before_collection'],'500')
        self.assertEqual(f['collections_before_collection'],'1000')
        self.assertEqual(f['forecast_status'],'NOT_EXECUTED')
        self.assertFalse(n['decision_authority'])
        self.assertEqual(n['viability_status'],'NOT_EVALUATED')
        self.assertTrue(all(x['canonical']['evidence_state']=='NOT_EVIDENCED' for x in n['financial_inputs']['cash_flows']))
        self.assertEqual(n['scenarios'][1]['suggested_due_date'],self.offer['delivery_date'])
        self.assertEqual(n['scenarios'][2]['suggested_due_date'],self.offer['offer_date'])
        self.assertFalse(n['scenarios'][1]['include_gift'])
        self.assertEqual(n['scenarios'][1]['freight_charged'],'10')
        self.assertEqual(n['scenarios'][2]['freight_charged'],'0')

    def test_negative_working_capital_changes_collection_advice(self):
        from eios.company_sales_negotiation import analyze_offer
        state=deepcopy(self.state)
        state['sales_financial_context']['working_capital_input']['current_liabilities']='30000'
        payload=self.quote()
        n=analyze_offer(payload,state,self.offer)
        self.assertTrue(n['financial_context']['pressure_indicator'])
        self.assertEqual(n['scenarios'][0]['suggested_due_date'],self.offer['offer_date'])
        self.assertIn('anticipado',n['scenarios'][0]['collection_terms'])

    def test_missing_policy_cost_or_foreign_balance_never_becomes_a_positive_result(self):
        from eios.company_sales_negotiation import analyze_offer
        payload=self.quote();state=deepcopy(self.state)
        state['sales_parameters']['values']={}
        n=analyze_offer(payload,state,self.offer)
        self.assertIsNone(n['origin_prices'][0]['recommended_unit_price'])
        self.assertEqual(n['scenarios'],[])
        self.assertTrue(n['pending'])
        n=self.quote(seller_freight_cost='')['negotiation']
        self.assertIsNone(n['contribution_margin_percent'])
        self.assertEqual(n['scenarios'],[])
        state=deepcopy(self.state)
        state['sales_financial_context']['working_capital_input']['company_scope']='OTHER'
        n=analyze_offer(payload,state,self.offer)
        self.assertIsNone(n['financial_context']['working_capital'])

    def test_merchandising_cost_is_explicit_and_parameter_revision_cannot_drift(self):
        for patch in (dict(gift_cost=''),dict(gift_cost='NaN'),dict(gift_description='',gift_cost='1'),dict(seller_freight_cost='-1')):
            with self.subTest(patch=patch),self.assertRaises(ValueError):self.quote(**patch)
        self.quote(gift_description='',gift_cost='0.00')
        self.set_policy(revision=1,target='35')
        with self.assertRaisesRegex(ValueError,'parámetros comerciales han cambiado'):self.quote()

    def test_saved_internal_advice_is_frozen_and_not_in_customer_document(self):
        result=self.desk.sales_offer(self.offer)
        html=printable_offer(self.path,'one',result['proposal_id'])
        self.set_policy(revision=1,target='35')
        self.assertEqual(self.desk.state('one')['sales_proposals'][0]['negotiation'],result['negotiation'])
        self.assertEqual(html,printable_offer(self.path,'one',result['proposal_id']))
        for term in ('Gorra sintética','working_capital','negotiation','71,43','margen'):
            self.assertNotIn(term,html)
