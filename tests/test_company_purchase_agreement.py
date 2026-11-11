from copy import deepcopy
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from eios.company_purchase_demo import build_demo
from eios.company_app import PurchaseDesk
from eios.company_purchase_agreement import save


class AgreementTest(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.path=Path(self.temp.name)/'demo.sqlite3';self.dataset=build_demo(self.path)['dataset_id'];self.desk=PurchaseDesk(self.path);self.source=self.desk.state(self.dataset)['purchases'][0];self.report=self.desk.review(self.dataset,self.source['proposal_id'])
    def tearDown(self):self.temp.cleanup()
    def data(self,**patch):
        value=dict(dataset_id=self.dataset,proposal_id=self.source['proposal_id'],review_id=self.report['review_id'],revision=0,action='DECLARE',actor='Andrés',agreement_date='2026-11-05',source_reference='CONF-DEMO-01',acknowledge=True);value.update(patch);return value
    def test_declare_and_retract_preserve_study_finance_and_old_report(self):
        before=deepcopy(self.desk.state(self.dataset)['purchases']);old=self.desk.printable_report(self.dataset,self.source['proposal_id'],self.report['review_id'])
        state=save(self.path,self.report,self.data());self.assertEqual(state['status'],'DECLARED_UNVERIFIED');self.assertFalse(state['purchase_authorized']);self.assertEqual(state['events'][0]['condition']['evidence_status'],'DECLARED_UNVERIFIED')
        updated=self.desk.review(self.dataset,self.source['proposal_id']);self.assertEqual(updated['purchase_agreement'],state)
        self.assertEqual(self.desk.state(self.dataset)['purchases'],before);self.assertEqual(self.desk.printable_report(self.dataset,self.source['proposal_id'],self.report['review_id']),old)
        self.assertEqual(updated['finance_execution'],self.report['finance_execution'])
        retired=save(self.path,updated,self.data(revision=1,action='RETRACT',reason='Referencia equivocada'));self.assertEqual(retired['status'],'RETRACTED');self.assertEqual(len(retired['events']),2)
    def test_missing_ack_support_invalid_date_and_stale_revision_rejected(self):
        for patch in [dict(acknowledge=False),dict(source_reference=''),dict(actor=''),dict(agreement_date='2026-01-01'),dict(agreement_date='invalid'),dict(action='RETRACT',reason='sin acuerdo')]:
            with self.assertRaises(ValueError):save(self.path,self.report,self.data(**patch))
        save(self.path,self.report,self.data())
        with self.assertRaises(ValueError):save(self.path,self.report,self.data())
        with self.assertRaises(ValueError):save(self.path,self.report,self.data(revision=1))
    def test_changed_context_and_tampered_history_are_rejected(self):
        stale=deepcopy(self.report);stale['proposal']['documentary_context_at_save']['fingerprint']='stale'
        with self.assertRaises(ValueError):save(self.path,stale,self.data())
        state=save(self.path,self.report,self.data());
        with sqlite3.connect(self.path) as c:
            raw=c.execute('SELECT payload FROM company_purchase_agreement_event').fetchone()[0];event=json.loads(raw);event['actor']='changed';c.execute('UPDATE company_purchase_agreement_event SET payload=?',(json.dumps(event),))
        with self.assertRaises(ValueError):self.desk.review(self.dataset,self.source['proposal_id'])
    def test_new_draft_does_not_inherit_agreement(self):
        from eios.company_purchase_draft import prepare
        save(self.path,self.report,self.data());state=self.desk.state(self.dataset);draft=prepare(self.desk,dict(dataset_id=self.dataset,proposal_id=self.source['proposal_id'],documentary_context_fingerprint=state['documentary_context']['fingerprint']))['values'];draft['stock_planning']['acknowledge']=True
        child=self.desk.save(draft);review=self.desk.review(self.dataset,child['proposal_id']);self.assertEqual(review['purchase_agreement']['status'],'NOT_DECLARED')
