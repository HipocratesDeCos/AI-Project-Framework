import tempfile
from pathlib import Path
import unittest
from eios.company_purchase_demo import build_demo
from eios.company_app import PurchaseDesk


class PurchaseDemoTest(unittest.TestCase):
    def test_complete_demo_replays_expected_cases_and_never_overwrites(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'demo.sqlite3';result=build_demo(path)
            expected={'DEMO-BASE':('8954.00','46.00','SHORTFALL'),
                'DEMO-CANTIDAD':('1790.80','7209.20','WITHIN_DECLARED_SCENARIO'),
                'DEMO-COMBINADA':('1512.50','7487.50','WITHIN_DECLARED_SCENARIO'),
                'DEMO-APLAZADA':('8954.00','5046.00','WITHIN_DECLARED_SCENARIO'),
                'DEMO-CUOTAS':('8954.00','4523.00','WITHIN_DECLARED_SCENARIO')}
            for case in result['cases']:
                self.assertEqual((case['total'],case['minimum_balance'],case['status']),expected[case['reference']])
                self.assertEqual(case['target_quantity'],'100')
            before=path.read_bytes()
            with self.assertRaises(ValueError):build_demo(path)
            self.assertEqual(before,path.read_bytes())
            desk=PurchaseDesk(path);state=desk.state(result['dataset_id']);self.assertEqual(len(state['purchases']),5)
            for saved in state['purchases']:
                cash=saved['cash_orientation_at_save'];review=cash['quantity_review']
                self.assertEqual(review['simulation_readiness'],'COMPLETE_HYPOTHETICAL')
                self.assertEqual(len(review['simulation_covered']),5)
                self.assertIn('DEMAND',{m['code'] for m in review['missing']})
                self.assertFalse(saved['decision_authority'])
                self.assertEqual(saved['operational_path'],'FORBIDDEN')
            self.assertTrue(any(a['kind']=='COMBINED' for a in state['purchases'][0]['cash_orientation_at_save']['alternatives']))
