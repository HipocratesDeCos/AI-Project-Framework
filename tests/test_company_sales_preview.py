import unittest
from copy import deepcopy
from tests import test_company_sales_negotiation as fixture


class SalesPreviewTest(unittest.TestCase):
    tearDown=fixture.SalesNegotiationTest.tearDown
    add=fixture.SalesNegotiationTest.add
    financial_data=fixture.SalesNegotiationTest.financial_data
    set_policy=fixture.SalesNegotiationTest.set_policy

    def setUp(self):fixture.SalesNegotiationTest.setUp(self)

    def minimal(self):
        data=deepcopy(self.offer)
        for key in ('reference','valid_until','delivery_date','delivery_location','payment_terms'):
            data[key]=''
        data['lines'][0]['vat_percent']=''
        return data

    def test_commercial_evaluation_before_emission_metadata_or_tax_is_supplied(self):
        data=self.minimal()
        r=self.desk.sales_offer(data,persist=False)
        self.assertEqual(r['net_amount'],'190.00')
        self.assertIsNone(r['vat_amount'])
        self.assertIsNone(r['total'])
        self.assertIsNone(r['reference'])
        self.assertIsNone(r['delivery_date'])
        self.assertIsNone(r['payment_terms'])
        self.assertIsNone(r['lines'][0]['vat_percent'])
        self.assertEqual(r['lines'][0]['tax_status'],'NOT_SUPPLIED')
        self.assertFalse(r['document_ready'])
        self.assertIn('IVA de A',r['document_completion_missing'])
        self.assertEqual(r['negotiation']['contribution_margin_percent'],'39.47')
        self.assertEqual(self.desk.state('one')['sales_proposals'],[])
        with self.assertRaises(ValueError):self.desk.sales_offer(data)

    def test_explicit_zero_tax_is_different_from_missing_tax(self):
        data=deepcopy(self.offer)
        data['freight_net']='0';data['freight_vat_percent']=''
        data['lines'][0]['vat_percent']='0'
        r=self.desk.sales_offer(data,persist=False)
        self.assertEqual(r['vat_amount'],'0.00')
        self.assertEqual(r['total'],'180.00')
        self.assertTrue(r['document_ready'])
        self.assertIsNone(r['freight_vat_percent'])
        self.desk.sales_offer(data)
        data['lines'][0]['vat_percent']=''
        r=self.desk.sales_offer(data,persist=False)
        self.assertIsNone(r['total'])
        self.assertFalse(r['document_ready'])

    def test_charged_freight_without_tax_can_be_evaluated_but_not_saved(self):
        data=deepcopy(self.offer);data['freight_vat_percent']=''
        r=self.desk.sales_offer(data,persist=False)
        self.assertEqual(r['net_amount'],'190.00')
        self.assertIsNone(r['freight_tax'])
        self.assertIsNone(r['total'])
        self.assertIn('IVA de los portes',r['document_completion_missing'])
        with self.assertRaises(ValueError):self.desk.sales_offer(data)

    def test_invalid_supplied_dates_and_tax_are_rejected_in_preview(self):
        for patch in [dict(delivery_date='31/02/2026'),dict(valid_until='2026-01-01'),dict(reference='R'*101),dict(freight_vat_percent='NaN')]:
            with self.subTest(patch=patch),self.assertRaises(ValueError):
                self.desk.sales_offer(dict(self.offer,**patch),persist=False)

    def test_partial_rejected_offer_does_not_invent_delivery_for_counteroffer(self):
        data=self.minimal();data['lines'][0]['unit_price']='60'
        r=self.desk.sales_offer(data,persist=False)
        self.assertEqual(r['negotiation']['proposal_evaluation']['status'],'NOT_APPROPRIATE_AS_PROPOSED')
        self.assertIsNone(r['negotiation']['scenarios'][1]['suggested_due_date'])
        self.assertIsNone(r['total'])

    def test_completion_produces_the_same_authoritative_totals_and_saved_payload(self):
        incomplete=self.desk.sales_offer(self.minimal(),persist=False)
        complete=self.desk.sales_offer(self.offer,persist=False)
        self.assertEqual(complete['net_amount'],incomplete['net_amount'])
        self.assertEqual(complete['total'],'229.90')
        self.assertEqual(complete['document_completion_missing'],[])
        self.assertTrue(complete['document_ready'])
        saved=self.desk.sales_offer(self.offer)
        self.assertEqual(saved['total'],complete['total'])
        self.assertEqual(self.desk.state('one')['sales_proposals'],[saved])
