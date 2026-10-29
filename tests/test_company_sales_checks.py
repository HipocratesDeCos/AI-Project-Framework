import unittest
from tests.test_company_sales_negotiation import SalesNegotiationTest


class SalesChecksTest(SalesNegotiationTest):
    def test_checks_distinguish_available_data_from_authority(self):
        result=self.quote()
        checks={c['code']:c for c in result['negotiation']['proposal_evaluation']['checks']}
        self.assertEqual(checks['MARGIN']['status'],'CHECKED')
        self.assertEqual(checks['TREASURY']['status'],'CHECKED')
        for key in ('QUALITY','CASH_PLAN','AUTHORITY'):
            self.assertEqual(checks[key]['status'],'PENDING')
        self.assertFalse(result['decision_authority'])

    def test_missing_minimum_has_a_specific_action(self):
        from eios.company_sales_checks import sales_checks
        result=self.quote();state=dict(self.state,sales_parameters={'values':{}})
        checks=sales_checks(result,state,result['negotiation'])
        self.assertEqual(checks[0]['action'],'PARAMETERS')
        self.assertIn('Configura',checks[0]['message'])
