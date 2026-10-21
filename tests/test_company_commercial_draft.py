import json
import sqlite3
import unittest
from eios.company_commercial_draft import commercial_draft
from tests import test_company_purchase_screen as fixture


class CommercialDraftTest(unittest.TestCase):
    setUp = fixture.PurchaseScreenTest.setUp
    tearDown = fixture.PurchaseScreenTest.tearDown

    def saved_review(self, **patch):
        saved = self.desk.save(dict(self.data, **patch))
        return self.desk.review('one', saved['proposal_id'])

    def draft(self, report):
        return self.desk.commercial_draft('one', report['proposal_id'], report['review_id'])

    def test_commercial_values_and_explicit_unknowns(self):
        report = self.saved_review()
        draft = self.draft(report)
        self.assertIn('242.00 EUR', draft['body'])
        self.assertIn('2 palets', draft['body'])
        self.assertIn('2026-11-01', draft['body'])
        self.assertIn('Total declarado de la operación: Pendiente de confirmar', draft['body'])
        self.assertIn('no constituye una aceptación ni un pedido', draft['body'])
        self.assertIsNone(draft['recipient'])
        self.assertFalse(draft['sent'])
        self.assertFalse(draft['decision_authority'])
        self.assertEqual(draft['attachments'], [])
        self.assertEqual(draft['operational_path'], 'FORBIDDEN')
        self.assertEqual(draft['acceptance_status'], 'NOT_RECORDED')

    def test_buyer_freight_and_discount_are_kept_separate(self):
        report = self.saved_review(pricing_mode='BEFORE_DISCOUNT',discount_mode='PERCENT',discount_value='10',
                                   shipping_mode='BUYER',shipping_net='5',shipping_vat_percent='21',
                                   shipping_billed_by='CARRIER',shipping_due_date='2026-11-03')
        body = self.draft(report)['body']
        for text in ('Precio neto unitario: 90.00 EUR', 'Descuento aplicado a la línea: 20.00 EUR',
                     'Total mercancía: 217.80 EUR', 'Total portes: 6.05 EUR',
                     'Total declarado de la operación: 223.85 EUR', 'Emisor de portes: transportista', '2026-11-03'):
            self.assertIn(text, body)

    def test_internal_finance_stock_sources_and_history_not_disclosed(self):
        report = self.saved_review()
        report['finance']['message'] = 'SECRET_FINANCIAL'
        report['stock']['message'] = 'SECRET_INVENTORY'
        report['price']['message'] = 'SECRET_NEGOTIATION'
        report['proposal']['documentary_context_at_save']['sources'] = [dict(document_ref='SECRET_SOURCE')]
        draft = commercial_draft(report)
        text = json.dumps(draft, ensure_ascii=False)
        for marker in ('SECRET_FINANCIAL','SECRET_INVENTORY','SECRET_NEGOTIATION','SECRET_SOURCE'):
            self.assertNotIn(marker, text)

    def test_saved_revision_stable_and_no_purchase_mutation(self):
        report = self.saved_review()
        before = self.draft(report)
        with sqlite3.connect(self.path) as c:
            original = c.execute('SELECT payload FROM manual_purchase_proposal').fetchall()
            c.execute("DELETE FROM documentary_company_record WHERE dataset_id='one'")
        self.assertEqual(self.draft(report), before)
        with sqlite3.connect(self.path) as c:
            self.assertEqual(c.execute('SELECT payload FROM manual_purchase_proposal').fetchall(), original)

    def test_wrong_company_or_review_rejected(self):
        report = self.saved_review()
        with self.assertRaises(ValueError):
            self.desk.commercial_draft('two', report['proposal_id'],report['review_id'])
        with self.assertRaises(ValueError):
            self.desk.commercial_draft('one', report['proposal_id'],'missing')
