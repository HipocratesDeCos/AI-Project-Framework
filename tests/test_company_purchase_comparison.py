from copy import deepcopy
import json
import sqlite3
from unittest.mock import patch
import unittest
from tests import test_company_purchase_cash_preview as fixture
from eios.company_purchase_comparison import compare, history


class PurchaseComparisonTest(unittest.TestCase):
    setUp=fixture.PurchaseCashPreviewTest.setUp
    tearDown=fixture.PurchaseCashPreviewTest.tearDown
    add=fixture.PurchaseCashPreviewTest.add
    prepare=fixture.PurchaseCashPreviewTest.prepare
    activate=fixture.PurchaseCashPreviewTest.activate
    financial_data=fixture.PurchaseCashPreviewTest.financial_data
    ready=fixture.PurchaseCashPreviewTest.ready
    def request(self):
        self.ready();self.data.update(quantity='2',unit_price='100')
        proposal=self.desk.save(self.data)
        return dict(dataset_id='one',proposal_id=proposal['proposal_id'],actor='Andrés',
            documentary_context_fingerprint=self.state['documentary_context']['fingerprint'],
            alternatives=[dict(label='Pronto pago',patch={'unit_price':'95'},
                conditions={'unit_price':dict(origin='HYPOTHETICAL')})])

    def test_compare_without_deficit_preserves_original_and_history(self):
        data=self.request();original=deepcopy(self.desk.state('one')['purchases'])
        result=compare(self.desk,data)
        self.assertEqual(result['baseline']['status'],'WITHIN_DECLARED_SCENARIO')
        self.assertEqual(result['alternatives'][0]['saving'],'12.10')
        self.assertIsNone(result['winner']);self.assertFalse(result['decision_authority'])
        self.assertEqual(result['alternatives'][0]['conditions']['unit_price']['evidence_status'],'DECLARED_UNVERIFIED')
        self.assertEqual(original,self.desk.state('one')['purchases'])
        self.assertFalse(history(self.desk,data)['comparisons'][0]['stale'])
        compare(self.desk,data)
        self.assertEqual(len(history(self.desk,data)['comparisons']),2)

    def test_fixed_quantity_unbacked_document_and_false_acceptance_rejected(self):
        data=self.request()
        for change in [dict(patch={'quantity':'1'},conditions={'quantity':{'origin':'HYPOTHETICAL'}}),
                       dict(conditions={'unit_price':{'origin':'DOCUMENTED'}}),
                       dict(conditions={'unit_price':{'origin':'HYPOTHETICAL','acceptance':'DECLARED_ACCEPTED'}})]:
            bad=deepcopy(data);bad['alternatives'][0].update(change)
            with self.assertRaises(ValueError): compare(self.desk,bad)
        self.assertEqual(history(self.desk,data)['comparisons'],[])

    def test_outside_horizon_and_invalid_discount_are_pending_not_favorable(self):
        data=self.request();data['alternatives'][0]=dict(label='Fuera de horizonte',patch={'due_date':'2027-01-01'},conditions={'due_date':{'origin':'HYPOTHETICAL'}})
        result=compare(self.desk,data)
        self.assertEqual(result['alternatives'][0]['result']['status'],'PENDING')
        self.assertIsNone(result['alternatives'][0]['saving'])
        data['alternatives'][0]=dict(label='Doble descuento',patch={'discount_mode':'PERCENT','discount_value':'3'},conditions={k:{'origin':'HYPOTHETICAL'} for k in ('discount_mode','discount_value')})
        self.assertEqual(compare(self.desk,data)['alternatives'][0]['result']['status'],'PENDING')

    def test_stale_context_and_parameter_race_rejected(self):
        data=self.request()
        with self.assertRaises(ValueError):compare(self.desk,dict(data,documentary_context_fingerprint='stale'))
        from eios.company_purchase_cash_preview import preview as real
        count=0
        def changing(*args,**kwargs):
            nonlocal count
            value=real(*args,**kwargs);count+=1
            if count==2:
                with sqlite3.connect(self.path) as c:
                    raw=c.execute('SELECT payload FROM company_finance_parameter_activation').fetchone()[0]
                    changed=json.loads(raw);changed['values']['P-FIN-002']='4000'
                    c.execute('UPDATE company_finance_parameter_activation SET payload=?',(json.dumps(changed),))
            return value
        with patch('eios.company_purchase_comparison.preview',side_effect=changing):
            with self.assertRaisesRegex(ValueError,'parámetros'):compare(self.desk,data)
        self.assertEqual(history(self.desk,data)['comparisons'],[])

    def test_historical_results_marked_stale_without_rewriting(self):
        data=self.request();result=compare(self.desk,data)
        self.add('cash_flow','C-NEW',dict(canonical=dict(flow_id='C-NEW',flow_type='COLLECTION',amount='10',currency='EUR',due_date='2026-12-01',due_date_evidenced=False,source_ref='DOC',evidence_state='NOT_EVIDENCED')))
        item=history(self.desk,data)['comparisons'][0]
        self.assertTrue(item['stale']);self.assertEqual(item['record'],result)

    def test_expired_document_is_never_verified_or_accepted(self):
        data=self.request()
        data['alternatives'][0]['conditions']['unit_price']=dict(origin='DOCUMENTED',source_reference='Oferta de prueba',valid_until='2020-01-01')
        c=compare(self.desk,data)['alternatives'][0]['conditions']['unit_price']
        self.assertEqual(c['validity_status'],'EXPIRED_AT_COMPARISON')
        self.assertEqual(c['evidence_status'],'DECLARED_UNVERIFIED')
        self.assertEqual(c['acceptance'],'PENDING')

    def test_installment_totals_must_match_alternative(self):
        data=self.request();a=data['alternatives'][0]
        a['patch']={'payment_installments':[dict(component='MERCHANDISE',amount='242',due_date=self.data['due_date'])]}
        a['conditions']={'payment_installments':dict(origin='HYPOTHETICAL')}
        self.assertEqual(compare(self.desk,data)['alternatives'][0]['result']['status'],'WITHIN_DECLARED_SCENARIO')
        a['patch']['payment_installments'][0]['amount']='1'
        self.assertEqual(compare(self.desk,data)['alternatives'][0]['result']['status'],'PENDING')

    def test_tampered_history_is_rejected(self):
        data=self.request();compare(self.desk,data)
        with sqlite3.connect(self.path) as c:
            payload=json.loads(c.execute('SELECT payload FROM purchase_condition_comparison').fetchone()[0])
            payload['actor']='Altered'
            c.execute('UPDATE purchase_condition_comparison SET payload=?',(json.dumps(payload),))
        with self.assertRaisesRegex(ValueError,'integridad'):history(self.desk,data)

    def test_negotiated_freight_and_vat_remain_part_of_financial_comparison(self):
        data = self.request()
        patch = dict(unit_price='100', pricing_mode='BEFORE_DISCOUNT', discount_mode='PERCENT',
                     discount_value='10', vat_percent='10', shipping_mode='BUYER',
                     shipping_net='10', shipping_vat_percent='21', shipping_billed_by='SUPPLIER',
                     shipping_due_date='2026-11-15')
        data['alternatives'] = [dict(label='Portes negociados', patch=patch,
                                    conditions={key:dict(origin='HYPOTHETICAL') for key in patch})]
        result = compare(self.desk, data)
        self.assertEqual(result['baseline']['total'], '242.00')
        self.assertEqual(result['alternatives'][0]['result']['total'], '210.10')
        self.assertEqual(result['alternatives'][0]['saving'], '31.90')
