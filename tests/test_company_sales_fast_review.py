import unittest
from copy import deepcopy
from tests import test_company_sales_negotiation as fixture
from tests import test_company_finance_activation as activation
from eios.company_sales_fast_review import stock_check,cash_preview


class FastSalesReviewTest(fixture.SalesNegotiationTest):
    prepare=activation.FinanceActivationTest.prepare
    activate=activation.FinanceActivationTest.activate

    def test_administrative_discrepancies_do_not_make_at_sight_commercial_checks_pending(self):
        state=deepcopy(self.state)
        state['sales_quality']={'status':'DISCREPANCIES','summary':{'total':51,'discrepancies':14,'pending':37}}
        from eios.company_sales_proposals import save_offer
        result=save_offer(self.path,state,dict(self.offer,due_date=self.offer['offer_date']),persist=False)
        conclusion=result['negotiation']['proposal_evaluation']['commercial_conclusion']
        self.assertEqual(conclusion['status'],'WITHIN_CHECKED_LIMITS')
        self.assertFalse(conclusion['decision_authority'])
        self.assertFalse(result['decision_authority'])
        quality=next(c for c in result['negotiation']['proposal_evaluation']['checks'] if c['code']=='QUALITY')
        self.assertEqual(quality['status'],'REVIEW')

    def test_missing_margin_and_deferred_collection_remain_operation_specific(self):
        result=self.quote(due_date=self.offer['offer_date'],seller_freight_cost='')
        self.assertEqual(result['negotiation']['proposal_evaluation']['commercial_conclusion']['status'],'MISSING_OPERATION_DATA')
        result=self.quote()
        self.assertTrue(result['negotiation']['proposal_evaluation']['commercial_conclusion']['deferred'])
        self.assertNotEqual(result['negotiation']['proposal_evaluation']['commercial_conclusion']['status'],'WITHIN_CHECKED_LIMITS')

    def test_stock_aggregates_repeated_article_and_requests_renegotiation(self):
        payload=self.quote()
        lines=[deepcopy(payload['lines'][0]) for _ in range(2)]
        for line in lines:line['quantity']='6';line['orientation']['inventory']['available']='10'
        result=stock_check(dict(payload,lines=lines))
        self.assertEqual(result['status'],'REVIEW')
        self.assertIn('12',result['message'])
        result=self.quote(lines=[dict(self.offer['lines'][0],quantity='9999')])
        self.assertEqual(result['negotiation']['proposal_evaluation']['commercial_conclusion']['status'],'RENEGOTIATE')

    def test_financial_engine_runs_without_saved_offer_or_promoted_evidence(self):
        self.prepare(revision=1);self.activate(revision=2)
        state=self.desk.sales_state('one');before=deepcopy(state['sales_financial_context']['cash_flows'])
        result=self.desk.sales_offer(dict(self.offer,commercial_parameter_revision=2,context_fingerprint=state['documentary_context']['fingerprint']),persist=False)
        preview=result['negotiation']['automatic_cash_preview']
        self.assertEqual(preview['status'],'EXECUTED',preview['message'])
        self.assertEqual(preview['new_flow_count'],1)
        self.assertEqual(preview['with_declared_plan']['projection']['status'],'NOT_EVIDENCED')
        self.assertIsNone(preview['with_declared_plan']['projection']['financial_capacity_forecast'])
        self.assertEqual(before,self.desk.sales_state('one')['sales_financial_context']['cash_flows'])
        self.assertEqual(self.desk.sales_state('one')['sales_proposals'],[])
        self.assertFalse(preview['decision_authority'])
        finance=deepcopy(state['sales_financial_context']);finance['cash_flows'][0]['canonical'].update(flow_type='COLLECTION',amount=result['total'],due_date=result['due_date'])
        self.assertEqual(cash_preview(self.path,result,finance)['status'],'NOT_EXECUTED')
