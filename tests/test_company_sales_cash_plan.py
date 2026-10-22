import json
import sqlite3
import unittest
from copy import deepcopy
from tests import test_company_sales_proposals as fixture
from tests import test_company_financial_context as finance_fixture
from tests import test_company_finance_activation as activation_fixture


class SalesCashPlanTest(unittest.TestCase):
    tearDown=fixture.SalesOfferTest.tearDown
    add=finance_fixture.FinancialContextTest.add
    financial_data=finance_fixture.FinancialContextTest.financial_data
    prepare=activation_fixture.FinanceActivationTest.prepare
    activate=activation_fixture.FinanceActivationTest.activate

    def setUp(self):
        fixture.SalesOfferTest.setUp(self)
        self.financial_data()
        self.prepare();self.activate()
        self.offer['context_fingerprint']=self.desk.state('one')['documentary_context']['fingerprint']
        self.saved=self.desk.sales_offer(self.offer)
        self.args=dict(dataset_id='one',proposal_id=self.saved['proposal_id'])
        self.loaded=self.desk.sales_cash_plan(self.args)
        self.data=dict(self.args,revision=0,actor='Comercial local',acknowledge=True,
            documentary_context_fingerprint=self.loaded['documentary_context_fingerprint'],rows=[
                dict(flow_type='COLLECTION',amount=self.saved['total'],due_date=self.saved['due_date'],
                     disposition='NEW_DECLARATION',note='Cobro propuesto con IVA.')])

    def save(self,**patch):return self.desk.sales_cash_plan(dict(self.data,**patch),save=True)

    def test_canonical_engine_preserves_pending_evidence_and_active_horizon(self):
        result=self.save();plan=result['plan'];e=plan['execution']
        self.assertEqual(e['status'],'EXECUTED',e['message'])
        self.assertEqual(e['new_flow_count'],1)
        self.assertEqual(e['finance_input']['horizon_days'],90)
        self.assertEqual(e['with_declared_plan']['projection']['status'],'NOT_EVIDENCED')
        self.assertIsNone(e['with_declared_plan']['projection']['financial_capacity_forecast'])
        self.assertEqual(len(e['finance_input']['cash_flows']),3)
        self.assertTrue(all(f['evidence_state']=='NOT_EVIDENCED' for f in e['finance_input']['cash_flows']))
        self.assertFalse(e['finance_input']['cash_flows'][-1]['due_date_evidenced'])
        self.assertEqual(plan['viability_status'],'NOT_EVALUATED')
        self.assertFalse(plan['decision_authority'])
        self.assertEqual(self.desk.sales_cash_plan(self.args)['plan'],plan)
        self.assertEqual(len(self.desk.sales_state('one')['sales_financial_context']['cash_flows']),2)

    def test_installments_and_cost_payments_require_explicit_gross_amounts(self):
        result=self.save(rows=[dict(self.data['rows'][0],amount='100'),dict(self.data['rows'][0],amount='129.90',due_date='2026-12-01'),dict(flow_type='PAYMENT',amount='12.10',due_date='2026-10-30',disposition='NEW_DECLARATION',note='Logística: pago con IVA declarado.')])
        self.assertEqual(result['plan']['execution']['new_flow_count'],3)
        self.assertEqual(result['plan']['cost_inventory_status'],'COMPLETENESS_NOT_ESTABLISHED')
        self.assertEqual(result['plan']['execution']['finance_input']['cash_flows'][-1]['amount'],'12.10')

    def test_existing_payment_reused_without_duplication_and_conflicting_mapping_rejected(self):
        payment=dict(flow_type='PAYMENT',amount='500',due_date='2026-10-15',disposition='ALREADY_DOCUMENTED',existing_flow_id='P-1',note='Pago ya previsto, asociación declarada.')
        # Offer date must not precede documented costs in this forward-only plan.
        payment['due_date']='2026-10-15'
        with self.assertRaises(ValueError):self.save(rows=self.data['rows']+[payment])
        # Use a future saved offer with matching maturity by modifying the documentary source before saving it.
        self.add('cash_flow','P-2',dict(canonical=dict(flow_id='P-2',flow_type='PAYMENT',amount='12.10',currency='EUR',due_date='2026-10-30',due_date_evidenced=False,source_ref='DOC-FIN',evidence_state='NOT_EVIDENCED')))
        updated=dict(self.offer,reference='PV-NEW',context_fingerprint=self.desk.state('one')['documentary_context']['fingerprint'])
        saved=self.desk.sales_offer(updated)
        loaded=self.desk.sales_cash_plan(dict(self.args,proposal_id=saved['proposal_id']))
        self.data.update(proposal_id=saved['proposal_id'],documentary_context_fingerprint=loaded['documentary_context_fingerprint'])
        payment.update(existing_flow_id='P-2',amount='12.10',due_date='2026-10-30')
        result=self.save(rows=self.data['rows']+[payment])
        e=result['plan']['execution']
        self.assertEqual(e['new_flow_count'],1)
        self.assertEqual(e['reused_flow_count'],1)
        self.assertEqual(len(e['finance_input']['cash_flows']),4)
        self.assertEqual(sum(f['flow_id']=='P-2' for f in e['finance_input']['cash_flows']),1)
        for patch in [dict(amount='12.11'),dict(flow_type='COLLECTION'),dict(existing_flow_id='MISSING')]:
            with self.assertRaises(ValueError):self.save(revision=1,rows=self.data['rows']+[dict(payment,**patch)])
        other=self.desk.sales_offer(dict(updated,reference='PV-OTHER'))
        with self.assertRaisesRegex(ValueError,'otra oferta'):
            self.save(proposal_id=other['proposal_id'],rows=self.data['rows']+[payment])

    def test_invalid_totals_foreign_offer_missing_ack_and_stale_revision_rejected(self):
        for patch in [dict(rows=[]),dict(rows=[dict(self.data['rows'][0],amount='1')]),dict(acknowledge=False),dict(actor=''),dict(revision=True),dict(dataset_id='two'),dict(documentary_context_fingerprint='old'),dict(rows=[dict(self.data['rows'][0],amount='NaN')])]:
            with self.subTest(patch=patch),self.assertRaises(ValueError):self.save(**patch)
        self.save()
        with self.assertRaises(ValueError):self.save()
        self.save(revision=1)
        with sqlite3.connect(self.path) as c:
            self.assertEqual(c.execute('SELECT count(*) FROM company_sales_cash_plan').fetchone()[0],2)

    def test_changed_documentary_context_keeps_old_result_frozen_and_blocks_edit(self):
        result=self.save()
        self.add('cash_flow','EXTRA',dict(canonical=dict(flow_id='EXTRA',flow_type='PAYMENT',amount='1',currency='EUR',due_date='2026-11-01',due_date_evidenced=False,source_ref='DOC-FIN',evidence_state='NOT_EVIDENCED')))
        loaded=self.desk.sales_cash_plan(self.args)
        self.assertFalse(loaded['can_edit'])
        self.assertEqual(loaded['plan'],result['plan'])
        with self.assertRaises(ValueError):self.save(revision=1)

    def test_missing_activation_keeps_declaration_without_invented_parameters(self):
        with sqlite3.connect(self.path) as c:c.execute('DELETE FROM company_finance_parameter_configuration')
        result=self.save()['plan']
        self.assertEqual(result['execution']['status'],'NOT_EXECUTED')
        self.assertIsNone(result['execution']['with_declared_plan'])

    def test_existing_collection_is_not_duplicated_and_new_matching_claim_needs_explicit_distinction(self):
        self.add('cash_flow','C-OFFER',dict(canonical=dict(flow_id='C-OFFER',flow_type='COLLECTION',amount=self.saved['total'],currency='EUR',due_date=self.saved['due_date'],due_date_evidenced=False,source_ref='DOC-FIN',evidence_state='NOT_EVIDENCED')))
        saved=self.desk.sales_offer(dict(self.offer,reference='PV-MATCH',context_fingerprint=self.desk.state('one')['documentary_context']['fingerprint']))
        loaded=self.desk.sales_cash_plan(dict(self.args,proposal_id=saved['proposal_id']))
        self.data.update(proposal_id=saved['proposal_id'],documentary_context_fingerprint=loaded['documentary_context_fingerprint'])
        with self.assertRaisesRegex(ValueError,'coincidentes'):self.save()
        existing=dict(self.data['rows'][0],disposition='ALREADY_DOCUMENTED',existing_flow_id='C-OFFER')
        e=self.save(rows=[existing])['plan']['execution']
        self.assertEqual(e['new_flow_count'],0)
        self.assertEqual(e['reused_flow_count'],1)
        self.assertEqual(len(e['finance_input']['cash_flows']),3)
        result=self.save(revision=1,rows=[dict(self.data['rows'][0],separate_movement_acknowledged=True,note='Declarado otro cobro independiente, no el de C-OFFER.')])
        self.assertEqual(result['plan']['execution']['new_flow_count'],1)
        self.assertEqual(result['plan']['rows'][0]['coincident_existing_flow_ids'],['C-OFFER'])
        self.assertEqual(result['plan']['execution']['finance_input']['cash_flows'][-1]['evidence_state'],'NOT_EVIDENCED')

    def test_tampering_detected(self):
        self.save()
        with sqlite3.connect(self.path) as c:c.execute("UPDATE company_sales_cash_plan SET payload='{}'")
        with self.assertRaisesRegex(ValueError,'huella'):self.desk.sales_cash_plan(self.args)
