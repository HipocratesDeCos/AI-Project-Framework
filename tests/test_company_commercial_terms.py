"""Proposal money is descriptive, and unknown freight remains unknown."""
import unittest
from eios.company_commercial_terms import commercial_terms
from tests import test_company_purchase_screen as fixture

class CommercialTermsTest(unittest.TestCase):
    def setUp(self):
        self.data=dict(quantity='2',unit_price='100',vat_percent='21',order_date='2026-10-01',due_date='2026-11-01')
    def quote(self, **patch):
        return commercial_terms(dict(self.data,**patch))
    def test_pending_is_not_zero(self):
        result=self.quote()
        self.assertEqual(result['total'],'242.00')
        self.assertIsNone(result['operation_total'])
    def test_percentage_and_independent_carrier_due(self):
        r=self.quote(pricing_mode='BEFORE_DISCOUNT',discount_mode='PERCENT',discount_value='10',shipping_mode='BUYER',shipping_net='10',shipping_vat_percent='21',shipping_billed_by='CARRIER',shipping_due_date='2026-11-15')
        self.assertEqual((r['unit_price'],r['net'],r['tax'],r['total'],r['operation_total']),('90.00','180.00','37.80','217.80','229.90'))
        self.assertEqual(r['commercial_terms']['shipping']['due_date'],'2026-11-15')
    def test_euro_discount_is_per_line(self):
        r=self.quote(pricing_mode='BEFORE_DISCOUNT',discount_mode='LINE_AMOUNT',discount_value='20')
        self.assertEqual(r['net'],'180.00')
        self.assertEqual(r['unit_price'],'90.00')
    def test_known_zero_modes(self):
        for mode in ('SUPPLIER','INCLUDED','NONE'):
            self.assertEqual(self.quote(shipping_mode=mode)['operation_total'],'242.00')
    def test_net_rejects_second_discount(self):
        for patch in (dict(discount_mode='PERCENT',discount_value='10'),dict(discount_value='0')):
            with self.assertRaises(ValueError): self.quote(**patch)
    def test_invalid_discount_inputs(self):
        for mode,value in [('PERCENT','101'),('PERCENT','NaN'),('LINE_AMOUNT','201'),('LINE_AMOUNT','0.001'),('PERCENT',True)]:
            with self.assertRaises(ValueError): self.quote(pricing_mode='BEFORE_DISCOUNT',discount_mode=mode,discount_value=value)
    def test_buyer_requires_all_fields_and_valid_dates(self):
        valid=dict(shipping_mode='BUYER',shipping_net='10',shipping_vat_percent='21',shipping_billed_by='SUPPLIER',shipping_due_date='2026-11-15')
        for key in ('shipping_net','shipping_vat_percent','shipping_billed_by','shipping_due_date'):
            patch=dict(valid);patch.pop(key)
            with self.assertRaises(ValueError): self.quote(**patch)
        with self.assertRaises(ValueError): self.quote(**dict(valid,shipping_due_date='2026-09-01'))
    def test_hidden_stale_shipping_rejected(self):
        with self.assertRaises(ValueError): self.quote(shipping_mode='INCLUDED',shipping_net='10')
    def test_zero_discount_and_free_goods(self):
        r=self.quote(pricing_mode='BEFORE_DISCOUNT',discount_mode='PERCENT',discount_value='100',shipping_mode='NONE')
        self.assertEqual(r['operation_total'],'0.00')
    def test_rounding_half_even(self):
        self.assertEqual(self.quote(quantity='1',unit_price='1.005',vat_percent='0')['net'],'1.00')
    def test_fractional_quantity_does_not_round_effective_unit(self):
        r=self.quote(quantity='3',unit_price='1',pricing_mode='BEFORE_DISCOUNT',discount_mode='LINE_AMOUNT',discount_value='1')
        self.assertTrue(r['unit_price'].startswith('0.666666666666666666'))
        self.assertEqual(r['net'],'2.00')

class CommercialPersistenceTest(unittest.TestCase):
    setUp = fixture.PurchaseScreenTest.setUp
    tearDown = fixture.PurchaseScreenTest.tearDown
    def test_commercial_terms_survive_reopen(self):
        from eios.company_app import PurchaseDesk
        result=self.desk.save(dict(self.data,pricing_mode='BEFORE_DISCOUNT',discount_mode='LINE_AMOUNT',discount_value='20',shipping_mode='NONE'))
        saved=PurchaseDesk(self.path).state('one')['purchases'][0]
        self.assertEqual(saved,result)
        self.assertEqual(saved['operation_total'],'217.80')
        self.assertEqual(saved['unit_price'],'90.00')
