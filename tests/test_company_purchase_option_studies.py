from copy import deepcopy
import unittest
from unittest.mock import patch
from tests import test_company_purchase_cash_preview as fixture


class PurchaseOptionStudiesTest(unittest.TestCase):
    def setUp(self):
        self.case=fixture.PurchaseCashPreviewTest();self.case.setUp();self.case.ready()
        self.data=dict(self.case.data,negotiation_selected_slot='response',unit_price='90')
        self.mine=dict(slot='mine',patch=dict(unit_price='50',pricing_mode='BEFORE_DISCOUNT',discount_mode='NONE',discount_value=None,due_date=self.data['due_date'],payment_installments=None),condition=dict(origin='HYPOTHETICAL',acceptance='PENDING'))
        self.provider=deepcopy(self.mine);self.provider.update(slot='response');self.provider['patch']['unit_price']='90'
        self.data['negotiation_alternatives']=[self.mine,self.provider]
    def tearDown(self):self.case.tearDown()
    def test_two_analyses_are_computed_and_frozen_with_selected_provider(self):
        financial=deepcopy(self.case.desk.sales_state('one')['sales_financial_context'])
        p=self.case.desk.save(self.data)
        entries={e['slot']:e for e in p['negotiation_at_save']['alternatives']}
        self.assertEqual(p['negotiation_at_save']['selected_slot'],'response')
        self.assertEqual(p['operation_total'],'10890.00')
        self.assertEqual(entries['mine']['cash_orientation']['current_terms']['total'],'6050.00')
        self.assertEqual(entries['response']['cash_orientation']['current_terms']['total'],'10890.00')
        self.assertNotEqual(entries['mine']['cash_orientation']['analysis_fingerprint'],entries['response']['cash_orientation']['analysis_fingerprint'])
        for e in entries.values():
            self.assertFalse(e['cash_orientation']['decision_authority']);self.assertEqual(e['cash_orientation']['viability_status'],'NOT_EVALUATED')
        self.assertEqual(financial,self.case.desk.sales_state('one')['sales_financial_context'])
        self.assertEqual(p,self.case.desk.state('one')['purchases'][0])
    def test_calendars_are_owned_by_each_option(self):
        self.mine['patch']['payment_installments']=[dict(component='MERCHANDISE',amount='6050.00',due_date=self.data['due_date'])]
        p=self.case.desk.save(self.data);entries={e['slot']:e for e in p['negotiation_at_save']['alternatives']}
        self.assertEqual(entries['mine']['payment_plan']['installments'][0]['amount'],'6050.00')
        self.assertEqual(entries['response']['payment_plan']['status'],'NOT_DECLARED')
        self.assertEqual(p['payment_plan']['status'],'NOT_DECLARED')
    def test_rejects_mismatched_selected_terms_or_calendar_without_saving(self):
        for patch in [dict(negotiation_alternatives=None),dict(negotiation_selected_slot='other'),dict(unit_price='91'),dict(payment_installments=[dict(component='MERCHANDISE',amount='10890.00',due_date=self.data['due_date'])])]:
            with self.subTest(patch=patch),self.assertRaises(ValueError):self.case.desk.save(dict(self.data,**patch))
        self.assertEqual(self.case.desk.state('one')['purchases'],[])

    def test_rejects_changed_financial_criteria_between_option_calculations(self):
        values=[dict(status='WITHIN_DECLARED_SCENARIO',parameter_activation={'revision':r}) for r in [1,2,1]]
        with patch('eios.company_purchase_cash_preview.preview',side_effect=values),self.assertRaisesRegex(ValueError,'criterios financieros'):
            self.case.desk.save(self.data)
        self.assertEqual(self.case.desk.state('one')['purchases'],[])

    def test_empty_other_option_calendar_identifies_its_owner(self):
        from datetime import date, timedelta
        self.mine['patch']['payment_installments']=[]
        end=date.fromisoformat(self.data['due_date'])
        rows=[dict(component='MERCHANDISE',amount='3630.00',due_date=(end-timedelta(days=n)).isoformat()) for n in [2,1,0]]
        self.provider['patch']['payment_installments']=rows
        self.data['payment_installments']=rows
        with self.assertRaisesRegex(ValueError,'Mi propuesta.*entre 1 y 20'):
            self.case.desk.save(self.data)
        self.assertEqual(self.case.desk.state('one')['purchases'],[])
        self.mine['patch']['payment_installments']=None
        saved=self.case.desk.save(self.data)
        self.assertEqual(len(saved['payment_plan']['installments']),3)
        self.assertEqual(saved['operation_total'],'10890.00')
