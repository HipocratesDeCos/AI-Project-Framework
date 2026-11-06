import unittest
from copy import deepcopy
from decimal import Decimal
from tests import test_company_purchase_scenario_search as fixtures
from eios.company_purchase_cash_preview import preview
from eios.company_proposal_report import _purchase_summary


class PurchaseSummaryTest(unittest.TestCase):
    def test_reference_coverage_is_visible_when_finance_is_pending(self):
        from eios.company_purchase_summary import summarize
        r=dict(status='PENDING',message='Activa horizonte y reserva.',alternatives=[],
               reference_stock_coverage=dict(status='FINITE',coverage_days='151.178378',as_of_date='2026-09-30'))
        s=summarize(r)
        self.assertEqual(s['stock']['status'],'REFERENCE_ONLY')
        self.assertEqual(s['stock']['coverage_days'],'151')
        self.assertIsNone(s['stock']['current_meets_target'])
        self.assertEqual(s['status'],'PENDING')
        self.assertIn('No incluye esta compra',s['stock']['limitation'])

    def test_cash_preview_keeps_stock_reference_before_finance_parameters(self):
        import sqlite3
        self.ready()
        article=next(a for a in self.state['articles'] if a['article_id']=='A')
        unit=article['unit_as_documented']
        self.state['inventory']={'A':dict(article_id='A',unit=unit,as_of_date='2026-09-30',physical='310',reserved='6',available='304')}
        self.state['planning']={'A':dict(status='FINITE',coverage_days='151.178378',daily_demand='2.01087',unit=unit,as_of_date='2026-09-30',valid_to='2026-12-29',engine='eios.stock.engine.calculate_coverage')}
        with sqlite3.connect(self.path) as c:c.execute('DELETE FROM company_finance_parameter_activation')
        r=preview(self.path,self.state,dict(self.data,shipping_mode='SUPPLIER'))
        self.assertEqual(r['blocking_code'],'FINANCE_PARAMETERS')
        self.assertEqual(r['purchase_summary']['stock']['coverage_days'],'151')
        self.assertEqual(r['alternatives'],[])

    setUp=fixtures.CombinationSearchTest.setUp
    tearDown=fixtures.CombinationSearchTest.tearDown
    ready=fixtures.CombinationSearchTest.ready
    reference=fixtures.CombinationSearchTest.reference
    add=fixtures.CombinationSearchTest.add
    prepare=fixtures.CombinationSearchTest.prepare
    activate=fixtures.CombinationSearchTest.activate
    financial_data=fixtures.CombinationSearchTest.financial_data
    setup_case=fixtures.CombinationSearchTest.setup_case

    def test_pending_has_exact_action_and_no_financial_success(self):
        self.ready();r=preview(self.path,self.state,dict(self.data,due_date='2027-12-01'))
        s=r['purchase_summary'];self.assertEqual(s['status'],'PENDING')
        self.assertEqual(s['next_action'],r['message']);self.assertIn('horizonte',s['next_action'])
        self.assertTrue(r['analysis_fingerprint']);self.assertFalse(s['decision_authority'])

    def test_cash_success_does_not_imply_justified_stock(self):
        self.ready();self.data.update(quantity='25',unit_price='100');r=preview(self.path,self.state,self.data)
        s=r['purchase_summary'];self.assertEqual(s['status'],'WITHIN_DECLARED_SCENARIO')
        self.assertEqual(s['stock']['status'],'NOT_ASSESSED');self.assertIn('supuestos',s['next_action'])
        self.assertFalse(s['sensitivity']['reserve_respected'])
        self.assertEqual(Decimal(s['sensitivity']['deficit']),Decimal('525'))

    def test_combined_options_preserve_source_and_quantity_caveat(self):
        self.setup_case();r=preview(self.path,self.state,self.data);before=deepcopy(r)
        s=r['purchase_summary'];option=next(a for a in s['alternatives'] if a['total']=='2904.00')
        self.assertFalse(option['same_quantity']);self.assertTrue(option['source']['components'])
        self.assertEqual(option['supplier_acceptance'],'NOT_CONFIRMED')
        self.assertEqual(s['references']['documentary_context_fingerprint'],self.state['documentary_context']['fingerprint'])
        html=_purchase_summary(r);self.assertIn('SIGUIENTE ACCIÓN AL GUARDAR',html);self.assertEqual(before,r)

    def test_stock_shortfall_is_not_hidden_by_sufficient_cash(self):
        self.setup_case();self.data.update(unit_price='1');self.data['stock_planning'].update(lead_time_days='10')
        r=preview(self.path,self.state,self.data);s=r['purchase_summary']
        self.assertEqual(s['status'],'WITHIN_DECLARED_SCENARIO')
        self.assertFalse(s['stock']['current_meets_target']);self.assertIn('antes',s['stock']['message'])
        self.assertIn('stock',s['next_action'])

    def test_current_stock_target_not_scenario_target_drives_explanation(self):
        self.setup_case();self.data.update(quantity='20',unit_price='1')
        s=preview(self.path,self.state,self.data)['purchase_summary']
        self.assertFalse(s['stock']['current_meets_target']);self.assertIn('no mantiene',s['stock']['message'])

    def test_old_study_is_not_reconstructed_and_report_escapes_summary(self):
        self.assertIn('no se reconstruye',_purchase_summary({'status':'SHORTFALL'}))
        self.ready();r=preview(self.path,self.state,self.data);r['purchase_summary']['next_action']='<img src=x>'
        html=_purchase_summary(r);self.assertIn('&lt;img',html);self.assertNotIn('<img',html)
