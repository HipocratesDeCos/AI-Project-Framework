from datetime import datetime,timezone
import json
import sqlite3
import unittest

from eios.company_finance_parameters import activate_finance_parameters,read_finance_activation
from eios.company_parameters import save_parameters
from eios.company_finance_execution import execute_documentary_finance
from eios.company_financial_context import financial_context
from tests import test_company_financial_context as fixtures


class FinanceActivationTest(unittest.TestCase):
    tearDown=fixtures.FinancialContextTest.tearDown
    add=fixtures.FinancialContextTest.add
    financial_data=fixtures.FinancialContextTest.financial_data

    def setUp(self):
        fixtures.FinancialContextTest.setUp(self)
        with sqlite3.connect(self.path) as c:
            for dataset in ('one','two'):
                raw=c.execute('SELECT manifest_json FROM documentary_company_snapshot WHERE dataset_id=?',(dataset,)).fetchone()[0]
                manifest=json.loads(raw);manifest['material_nature']='SYNTHETIC'
                c.execute('UPDATE documentary_company_snapshot SET manifest_json=? WHERE dataset_id=?',(json.dumps(manifest),dataset))

    def prepare(self,minimum='2000',revision=0,dataset='one'):
        return save_parameters(self.path,self.desk.store,dict(dataset_id=dataset,revision=revision,
            actor='Test user',reason='Explicit synthetic policy',profile={},values={'P-FIN-001':'90.0','P-FIN-002':minimum},
            references={},critical_acknowledged=True))

    def activate(self,revision=1,dataset='one',**patch):
        data=dict(dataset_id=dataset,revision=revision,actor='Test user',reason='Activate explicit cutoff',acknowledge=True)
        data.update(patch)
        return activate_finance_parameters(self.path,self.desk.store,data)

    def context(self):
        return financial_context(self.desk.store,'one',self.desk.store.describe('one'))

    def test_atomic_activation_history_scope_and_idempotency(self):
        self.prepare()
        state=self.activate()
        activation=state['finance_activation']
        self.assertEqual(activation['as_of_date'],'2026-09-30')
        self.assertEqual(activation['values']['P-FIN-002'],'2000')
        self.assertEqual(len(activation['configurations']),2)
        self.assertFalse(activation['decision_authority'])
        self.assertEqual(self.activate()['finance_activation'],activation)
        self.assertIsNone(read_finance_activation(self.path,'two','2026-09-30'))
        with sqlite3.connect(self.path) as c:
            self.assertEqual(c.execute('SELECT count(*) FROM company_finance_parameter_history').fetchone()[0],2)
            self.assertEqual(c.execute('SELECT count(*) FROM company_finance_parameter_configuration').fetchone()[0],2)
        self.prepare(dataset='two',minimum='100')
        self.assertEqual(self.activate(dataset='two')['finance_activation']['values']['P-FIN-002'],'100')
        self.assertEqual(read_finance_activation(self.path,'one','2026-09-30')['values']['P-FIN-002'],'2000')

    def test_no_silent_overwrite_and_stale_or_unacknowledged_activation(self):
        self.prepare()
        for patch in [dict(acknowledge=False),dict(actor=''),dict(reason=''),dict(revision=0)]:
            with self.assertRaises(ValueError):
                self.activate(**patch)
        self.activate()
        self.prepare(minimum='3000',revision=1)
        with self.assertRaisesRegex(ValueError,'No se sobrescribe'):
            self.activate(revision=2)
        self.assertEqual(read_finance_activation(self.path,'one','2026-09-30')['values']['P-FIN-002'],'2000')

    def test_real_material_not_activated(self):
        self.prepare()
        with sqlite3.connect(self.path) as c:
            manifest=json.loads(c.execute("SELECT manifest_json FROM documentary_company_snapshot WHERE dataset_id='one'").fetchone()[0])
            manifest['material_nature']='REAL'
            c.execute("UPDATE documentary_company_snapshot SET manifest_json=? WHERE dataset_id='one'",(json.dumps(manifest),))
        with self.assertRaisesRegex(ValueError,'sintética'):
            self.activate()

    def test_no_default_before_activation_and_evidence_states_preserved(self):
        self.financial_data()
        proposal=self.desk.save(self.data)
        self.assertEqual(execute_documentary_finance(self.path,proposal,self.context())['status'],'NOT_EXECUTED')
        self.prepare();self.activate()
        result=execute_documentary_finance(self.path,proposal,self.context())
        self.assertEqual(result['status'],'EXECUTED')
        self.assertEqual(result['finance_result']['projection']['status'],'NOT_EVIDENCED')
        self.assertTrue(all(item['evidence_state']=='NOT_EVIDENCED' for item in result['finance_input']['cash_flows']))
        self.assertEqual(result['purchase_effect_status'],'NOT_EVALUATED')
        self.assertEqual(result['viability_status'],'NOT_EVALUATED')
        self.assertEqual(result['operational_path'],'FORBIDDEN')
        self.assertTrue(result['finance_package_fingerprint'])

    def test_existing_engine_calculates_only_supplied_flows_and_report_is_frozen(self):
        self.financial_data()
        with sqlite3.connect(self.path) as c:
            rows=c.execute("SELECT record_id,record_json FROM documentary_company_record WHERE kind='cash_flow' AND dataset_id='one'").fetchall()
            for identity,raw in rows:
                record=json.loads(raw);record['data']['canonical']['evidence_state']='DEMONSTRATED'
                record['data']['canonical']['due_date_evidenced']=True
                c.execute("UPDATE documentary_company_record SET record_json=? WHERE dataset_id='one' AND record_id=?",(json.dumps(record),identity))
        self.prepare();self.activate()
        proposal=self.desk.save(self.data)
        review=self.desk.review('one',proposal['proposal_id'])
        execution=review['finance_execution']
        self.assertEqual(review['version'],'COMPANY-CONTEXT-REVIEW-13')
        self.assertEqual(execution['status'],'EXECUTED')
        self.assertEqual(execution['finance_result']['projection']['status'],'DETERMINED')
        self.assertEqual(len(execution['finance_input']['cash_flows']),2)
        self.assertEqual(execution['purchase_effect_status'],'NOT_EVALUATED')
        self.assertFalse(execution['decision_authority'])
        html=self.desk.printable_report('one',proposal['proposal_id'],review['review_id'])
        self.assertIn('PROYECCIÓN DOCUMENTAL',html)
        self.assertIn('2.000 EUR',html)
        with sqlite3.connect(self.path) as c:
            c.execute("DELETE FROM documentary_company_record WHERE kind='cash_flow'")
        self.assertEqual(self.desk.printable_report('one',proposal['proposal_id'],review['review_id']),html)

    def test_zero_minimum_does_not_invent_percentage_margin(self):
        self.financial_data();self.prepare(minimum='0');self.activate()
        proposal=self.desk.save(self.data)
        result=execute_documentary_finance(self.path,proposal,self.context())
        self.assertEqual(result['status'],'EXECUTED')
        self.assertIsNone(result['finance_result']['safety_margin']['value_pct'])
