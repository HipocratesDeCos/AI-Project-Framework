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

    def test_amount_preview_does_not_require_order_or_payment_dates(self):
        for price, total in [('13.50','1633.50'),('14','1694.00')]:
            data = dict(quantity='100',unit_price=price,vat_percent='21',pricing_mode='BEFORE_DISCOUNT',
                        discount_mode='PERCENT',discount_value='0',shipping_mode='SUPPLIER',order_date='',due_date='2026-11-03')
            quote = commercial_terms(data, require_dates=False)
            self.assertEqual(quote['operation_total'], total)
            self.assertEqual(quote['schedule_status'], 'PENDING_DATES')
            self.assertIsNone(quote['order_date'])
            with self.assertRaises(ValueError):
                commercial_terms(data)
        data.pop('due_date')
        self.assertEqual(commercial_terms(data, require_dates=False)['operation_total'], '1694.00')

    def test_freight_amount_can_be_quoted_before_its_due_date(self):
        data = dict(self.data,order_date='',due_date='',shipping_mode='BUYER',shipping_net='10',
                    shipping_vat_percent='21',shipping_billed_by='CARRIER')
        quote = commercial_terms(data, require_dates=False)
        self.assertEqual(quote['operation_total'], '254.10')
        self.assertIsNone(quote['commercial_terms']['shipping']['due_date'])
        with self.assertRaises(ValueError):
            commercial_terms(data)
        data['shipping_mode'] = 'PENDING'
        for key in ['shipping_net','shipping_vat_percent','shipping_billed_by']:data.pop(key)
        self.assertIsNone(commercial_terms(data, require_dates=False)['operation_total'])

    def test_amount_preview_keeps_totals_when_dates_are_reversed(self):
        data=dict(quantity='1000',unit_price='2.60',vat_percent='21',pricing_mode='BEFORE_DISCOUNT',discount_mode='PERCENT',discount_value='10',shipping_mode='SUPPLIER',order_date='2026-11-04',due_date='2026-02-15')
        quote=commercial_terms(data,require_dates=False)
        self.assertEqual(quote['unit_price'],'2.34')
        self.assertEqual(quote['operation_total'],'2831.40')
        self.assertEqual(quote['schedule_status'],'INVALID_DATES')
        self.assertIn('anterior al pedido',quote['schedule_issues'][0])
        with self.assertRaisesRegex(ValueError,'anterior al pedido'):commercial_terms(data)
        data.update(shipping_mode='BUYER',shipping_net='10',shipping_vat_percent='21',shipping_billed_by='CARRIER',shipping_due_date='2026-02-15',due_date='2026-11-30')
        self.assertEqual(commercial_terms(data,require_dates=False)['operation_total'],'2843.50')
        with self.assertRaisesRegex(ValueError,'portes.*anterior'):commercial_terms(data)
