from copy import deepcopy
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

from eios.company_app import PurchaseDesk
from eios.company_purchase_demo import build_demo
from eios.company_purchase_draft import prepare


class StudyDraftTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.path=Path(self.tmp.name)/'demo.sqlite3';self.dataset=build_demo(self.path)['dataset_id'];self.desk=PurchaseDesk(self.path);self.state=self.desk.state(self.dataset)
    def tearDown(self):self.tmp.cleanup()
    def request(self,reference='DEMO-BASE'):
        proposal=next(p for p in self.state['purchases'] if p['reference']==reference)
        return dict(dataset_id=self.dataset,proposal_id=proposal['proposal_id'],documentary_context_fingerprint=self.state['documentary_context']['fingerprint'])
    def test_preparation_copies_terms_plan_and_assumptions_without_saving(self):
        before=deepcopy(self.state['purchases']);values=prepare(self.desk,self.request('DEMO-CUOTAS'))['values']
        self.assertEqual(values['quantity'],'500');self.assertEqual(values['unit_price'],'14.80')
        self.assertEqual(len(values['payment_installments']),2);self.assertEqual(values['stock_planning']['receipts'],[dict(date='2026-11-18',quantity='50')])
        self.assertFalse(values['stock_planning']['acknowledge']);self.assertEqual(values['reference'],'DEMO-CUOTAS-BORRADOR')
        self.assertEqual(before,self.desk.state(self.dataset)['purchases'])
        self.assertTrue(all(v['condition']['acceptance']=='PENDING' for v in values['negotiation_alternatives']))
    def test_save_creates_new_identity_and_keeps_original_with_lineage(self):
        before=deepcopy(self.state['purchases']);values=prepare(self.desk,self.request())['values'];values['stock_planning']['acknowledge']=True
        saved=self.desk.save(values);self.assertNotEqual(saved['proposal_id'],values['draft_source']['proposal_id']);self.assertEqual(saved['draft_source'],values['draft_source'])
        self.assertEqual(saved['total'],'8954.00');self.assertFalse(saved['decision_authority'])
        after=self.desk.state(self.dataset)['purchases'];self.assertEqual([p for p in after if p['proposal_id'] in {s['proposal_id'] for s in before}],before)
        review=self.desk.review(self.dataset,saved['proposal_id']);html=self.desk.printable_report(self.dataset,saved['proposal_id'],review['review_id']);self.assertIn('Borrador creado desde el estudio',html);self.assertIn(values['draft_source']['proposal_id'],html)
        again=prepare(self.desk,self.request())['values'];self.assertEqual(again['reference'],'DEMO-BASE-BORRADOR-2')
    def test_stale_context_foreign_source_or_tampering_cannot_be_saved(self):
        for patch in [dict(proposal_id='FOREIGN'),dict(documentary_context_fingerprint='stale')]:
            with self.assertRaises(ValueError):prepare(self.desk,dict(self.request(),**patch))
        values=prepare(self.desk,self.request())['values'];values['stock_planning']['acknowledge']=True
        for field in ['proposal_fingerprint','dataset_id','reference']:
            bad=deepcopy(values);bad['draft_source'][field]='tampered'
            with self.assertRaises(ValueError):self.desk.save(bad)
        self.assertEqual(len(self.desk.state(self.dataset)['purchases']),5)
    def test_two_negotiation_columns_copied_without_declared_acceptance(self):
        from eios.company_purchase_negotiation import capture
        values=prepare(self.desk,self.request())['values'];values['stock_planning']['acknowledge']=True
        entries=values['negotiation_alternatives'];response=deepcopy(entries[0]);response['slot']='response';response['patch']['unit_price']='14.50';entries.append(response)
        source=self.desk.save(values);copied=prepare(self.desk,dict(self.request(),proposal_id=source['proposal_id']))['values']
        self.assertEqual({v['slot'] for v in copied['negotiation_alternatives']},{'mine','response'})
        self.assertEqual(capture(copied,copied['negotiation_alternatives'])['acceptance_status'],'UNVERIFIED')
    def test_legacy_missing_context_is_rejected_without_guessing(self):
        request=self.request();proposal=next(p for p in self.state['purchases'] if p['proposal_id']==request['proposal_id']);proposal.pop('documentary_context_at_save')
        with sqlite3.connect(self.path) as c:c.execute('UPDATE manual_purchase_proposal SET payload=? WHERE proposal_id=?',(json.dumps(proposal),proposal['proposal_id']))
        with self.assertRaisesRegex(ValueError,'no se conserva'):prepare(self.desk,request)
