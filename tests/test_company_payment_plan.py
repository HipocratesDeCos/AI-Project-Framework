"""Declared schedules conserve candidates, without adding cash flows or evidence."""
import json
import sqlite3
import unittest

from eios.company_app import PurchaseDesk, PAGE
from eios.company_commercial_terms import commercial_terms
from eios.company_payment_plan import payment_plan
from tests import test_company_purchase_screen as fixture


def row(amount='121', due='2026-11-01', component='MERCHANDISE'):
    return dict(component=component, amount=amount, due_date=due)


class PaymentPlanTest(unittest.TestCase):
    def setUp(self):
        self.data = dict(quantity='2', unit_price='100', vat_percent='21',
                         order_date='2026-10-01', due_date='2026-11-01', shipping_mode='NONE')
        self.proposal = dict(commercial_terms(self.data), proposal_id='proposal-001', currency='EUR')

    def plan(self, rows, **patch):
        return payment_plan(dict(payment_installments=rows), dict(self.proposal, **patch))

    def test_missing_schedule_is_not_inferred(self):
        p = payment_plan({}, self.proposal)
        self.assertEqual(p['status'], 'NOT_DECLARED')
        self.assertEqual(p['installments'], [])

    def test_installments_keep_canonical_evidence_pending(self):
        p = self.plan([row('121', '2026-10-15'), row('121')])
        self.assertEqual(p['total'], '242.00')
        self.assertEqual(p['status'], 'DECLARED_UNVERIFIED')
        self.assertFalse(p['included_in_documentary_projection'])
        self.assertEqual(p['cash_flow_membership_status'], 'NOT_REVIEWED')
        self.assertEqual(p['completeness_status'], 'OTHER_COSTS_NOT_ESTABLISHED')
        for item in p['installments']:
            f = item['canonical_candidate']
            self.assertEqual(f['evidence_state'], 'NOT_EVIDENCED')
            self.assertFalse(f['due_date_evidenced'])
            self.assertIsNone(f['source_ref'])
        self.assertEqual(len({i['canonical_candidate']['flow_id'] for i in p['installments']}), 2)

    def test_invalid_schedule_fails_closed(self):
        invalid = [[], {}, '[]', [row('242')]*21, [row('241')], [row('243')],
                   [row('242','2026-10-31')], [row('242','2026-09-30')],
                   [row('121'),row('121')], [row('121'),row('121','2026-10-15')],
                   [row('242',component='OTHER')], [row('242',component='FREIGHT')],
                   [row('NaN')], [row('Infinity')], [row('-1')], [row('0')],
                   [row('242.001')], [row(True)], [dict(row('242'), source_ref='invented')],
                   [row('242','01/11/2026')]]
        for rows in invalid:
            with self.subTest(rows=rows):
                with self.assertRaises(ValueError):
                    self.plan(rows)

    def test_unknown_freight_blocks_full_calendar(self):
        proposal = dict(commercial_terms(dict(self.data, shipping_mode='PENDING')),
                        proposal_id='proposal-001', currency='EUR')
        with self.assertRaises(ValueError):
            payment_plan(dict(payment_installments=[row('242')]), proposal)

    def test_freight_is_separate_and_total_includes_tax(self):
        terms = commercial_terms(dict(self.data, shipping_mode='BUYER', shipping_net='10',
                    shipping_vat_percent='21', shipping_billed_by='CARRIER', shipping_due_date='2026-11-15'))
        p = payment_plan(dict(payment_installments=[row('242'),row('12.10','2026-11-15','FREIGHT')]),
                         dict(terms, proposal_id='proposal-001', currency='EUR'))
        self.assertEqual(p['total'],'254.10')
        with self.assertRaises(ValueError):
            payment_plan(dict(payment_installments=[row('254.10')]),
                         dict(terms, proposal_id='proposal-001', currency='EUR'))

    def test_zero_cost_does_not_invent_zero_installments(self):
        terms = commercial_terms(dict(self.data, unit_price='0'))
        p = payment_plan({}, dict(terms, proposal_id='proposal-001', currency='EUR'))
        self.assertEqual(p['status'],'NOT_DECLARED')


class PaymentPlanPersistenceTest(unittest.TestCase):
    setUp = fixture.PurchaseScreenTest.setUp
    tearDown = fixture.PurchaseScreenTest.tearDown

    def test_schedule_persists_in_exact_review_report_and_draft(self):
        saved = self.desk.save(dict(self.data, shipping_mode='NONE',
            payment_installments=[row('100','2026-10-15'),row('142')]))
        self.assertEqual(PurchaseDesk(self.path).state('one')['purchases'][0],saved)
        review = self.desk.review('one',saved['proposal_id'])
        args = ('one',saved['proposal_id'],review['review_id'])
        html = self.desk.printable_report(*args)
        self.assertIn('CALENDARIO DECLARADO',html)
        self.assertIn('15/10/2026',html)
        self.assertIn('100,00 EUR',html)
        draft = self.desk.commercial_draft(*args)
        self.assertIn('Calendario de pagos propuesto',draft['body'])
        self.assertIn('142,00 EUR',draft['body'])
        self.assertNotIn('canonical_candidate',draft['body'])
        self.assertFalse(draft['sent'])
        self.assertEqual(review['proposal']['payment_plan'],saved['payment_plan'])
        self.assertIsNone(review['finance_execution']['finance_result'])
        with sqlite3.connect(self.path) as c:
            self.assertEqual(c.execute("SELECT count(*) FROM documentary_company_record WHERE kind='cash_flow'").fetchone()[0],0)
        self.assertEqual(self.desk.printable_report(*args),html)

    def test_invalid_schedule_never_writes_proposal(self):
        with self.assertRaises(ValueError):
            self.desk.save(dict(self.data,shipping_mode='NONE',payment_installments=[row('200')]))
        self.assertEqual(self.desk.state('one')['purchases'],[])

    def test_optional_editor_and_submission_are_wired(self):
        for item in ('payment-plan-enabled','payment-plan-add','declaredPaymentRows()',
                     'd.payment_installments=declaredPaymentRows()','renderPaymentPlan(container,proposal.payment_plan)'):
            self.assertIn(item,PAGE)
