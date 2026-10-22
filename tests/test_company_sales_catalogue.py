from copy import deepcopy
import unittest
from eios.company_sales_catalogue import expanded_catalogue
from tests import test_company_sales_links as fixture


class ExpandedCatalogueTest(unittest.TestCase):
    def test_different_model_or_measure_never_reuses_an_existing_sku(self):
        articles=[dict(article_id='EXT250',description='Extractor 250mm',unit_as_documented='uds.')]
        sales=dict(invoices=[dict(invoice_number='F1',issue_date='2026-09-30',customer_id='C',lines=[dict(record_id='F1#1',article_id=None,description='Extractor 315mm',unit=None,quantity='10',net_amount='4200',currency='EUR',source_refs=[dict(document_ref='D',page=1)])])])
        original=deepcopy((articles,sales));catalogue=expanded_catalogue('one',articles,sales);item=catalogue['prepared_references'][0]
        self.assertEqual(catalogue['total_reference_count'],2)
        self.assertNotEqual(item['proposed_article_id'],'EXT250')
        self.assertIsNone(item['unit_as_documented']);self.assertIsNone(item['reference_unit_cost']);self.assertIsNone(item['recommended_sale_price']);self.assertIsNone(item['inventory'])
        self.assertFalse(item['selectable_for_proposal']);self.assertFalse(item['decision_authority'])
        self.assertEqual(item['source_refs'],sales['invoices'][0]['lines'][0]['source_refs'])
        self.assertEqual((articles,sales),original)
        self.assertEqual(expanded_catalogue('one',articles,sales),catalogue)
        self.assertNotEqual(expanded_catalogue('two',articles,sales)['prepared_references'][0]['proposed_article_id'],item['proposed_article_id'])

    def test_same_description_is_not_merged_or_assumed_to_be_the_same_article(self):
        line=dict(record_id='F1#1',article_id=None,description='Maceta 11L',unit=None,source_refs=[])
        sales=dict(invoices=[dict(invoice_number='F1',issue_date='2026-09-30',customer_id='C',lines=[line,dict(line,record_id='F1#2')])])
        r=expanded_catalogue('one',[dict(article_id='MAC11',description='Maceta 11L')],sales)
        self.assertEqual(r['prepared_reference_count'],2)
        self.assertEqual(len({x['proposed_article_id'] for x in r['prepared_references']}),2)

    def test_explicit_link_to_existing_catalogue_does_not_add_a_duplicate(self):
        sales=dict(invoices=[dict(invoice_number='F1',issue_date='2026-09-30',customer_id='C',lines=[dict(record_id='F1#1',article_id='A',description='Descripción alternativa',unit='uds.')])])
        r=expanded_catalogue('one',[dict(article_id='A')],sales)
        self.assertEqual(r['prepared_reference_count'],0)


class CatalogueStateTest(unittest.TestCase):
    add=fixture.SalesLinksTest.add
    financial_data=fixture.SalesLinksTest.financial_data
    set_policy=fixture.SalesLinksTest.set_policy
    tearDown=fixture.SalesLinksTest.tearDown
    def setUp(self):fixture.SalesLinksTest.setUp(self)

    def test_state_prepares_reference_but_offer_still_requires_a_valid_article(self):
        before=self.desk.store.records('one','sales_invoice_line')
        state=self.desk.state('one');candidate=state['sales_catalogue']['prepared_references'][0]
        self.assertEqual(state['sales_catalogue']['catalogue_article_count'],1)
        self.assertEqual(state['sales_catalogue']['prepared_reference_count'],1)
        self.assertNotIn(candidate['proposed_article_id'],{a['article_id'] for a in state['articles']})
        offer=dict(self.offer,context_fingerprint=state['documentary_context']['fingerprint'],lines=[dict(self.offer['lines'][0],article_id=candidate['proposed_article_id'])])
        with self.assertRaises(ValueError):self.desk.sales_offer(offer,persist=False)
        self.assertEqual(self.desk.store.records('one','sales_invoice_line'),before)
