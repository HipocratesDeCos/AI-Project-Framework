import unittest
from copy import deepcopy

from eios.company_purchase_negotiation import capture
from tests import test_company_purchase_screen as screen_fixture


class NegotiationCaptureTest(unittest.TestCase):
    def setUp(self):
        self.base = dict(quantity='2', unit_price='100', vat_percent='21',
                         order_date='2026-10-01', due_date='2026-11-01', shipping_mode='NONE')
        self.variant = dict(slot='mine', patch=dict(unit_price='100', pricing_mode='BEFORE_DISCOUNT',
                            discount_mode='PERCENT', discount_value='10', due_date='2026-11-15'),
                            condition=dict(origin='HYPOTHETICAL', acceptance='PENDING'))

    def test_quotes_are_calculated_on_server_with_shared_tax_and_freight(self):
        result = capture(self.base, [self.variant])
        self.assertEqual(result['alternatives'][0]['quote']['operation_total'], '217.80')
        self.assertFalse(result['decision_authority'])
        self.assertEqual(self.base['unit_price'], '100')

    def test_rejects_undocumented_offer_and_injected_quantity(self):
        variant = deepcopy(self.variant)
        variant['condition']['origin'] = 'DOCUMENTED'
        with self.assertRaises(ValueError):
            capture(self.base, [variant])
        variant = deepcopy(self.variant)
        variant['patch']['quantity'] = '200'
        with self.assertRaises(ValueError):
            capture(self.base, [variant])

    def test_rejects_double_discount_on_net_and_duplicate_columns(self):
        variant = deepcopy(self.variant)
        variant['patch']['pricing_mode'] = 'NET'
        with self.assertRaises(ValueError):
            capture(self.base, [variant])
        with self.assertRaises(ValueError):
            capture(self.base, [self.variant, self.variant])

    def test_persisted_negotiation_survives_reopen_and_invalid_does_not_save(self):
        case = screen_fixture.PurchaseScreenTest()
        case.setUp()
        try:
            invalid = deepcopy(self.variant)
            invalid['patch']['unit_price'] = '-1'
            with self.assertRaises(ValueError):
                case.desk.save(dict(case.data, negotiation_alternatives=[invalid]))
            self.assertEqual(case.desk.state('one')['purchases'], [])
            case.desk.save(dict(case.data, shipping_mode='NONE', negotiation_alternatives=[self.variant]))
            from eios.company_app import PurchaseDesk
            saved = PurchaseDesk(case.path).state('one')['purchases'][0]
            self.assertEqual(saved['negotiation_at_save']['alternatives'][0]['quote']['operation_total'], '217.80')
            self.assertEqual(saved['total'], '242.00')
        finally:
            case.tearDown()
