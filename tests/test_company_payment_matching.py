import copy
import json
import sqlite3
import unittest

from eios.company_payment_matching import payment_matching
from tests import test_company_financial_context as fixtures


def flow(identity='P-1',amount='242',kind='PAYMENT',currency='EUR',due='2026-11-01'):
    return dict(record_id=identity,canonical=dict(flow_id=identity,flow_type=kind,amount=amount,
        currency=currency,due_date=due,source_ref='DOC-PAY',due_date_evidenced=False,
        evidence_state='NOT_EVIDENCED'),source_refs=[dict(document_ref='DOC-PAY')])


class PaymentMatchingTest(unittest.TestCase):
    def setUp(self):
        self.proposal = dict(proposal_id='PROP',dataset_id='one',payment_plan=dict(
            status='DECLARED_UNVERIFIED',currency='EUR',installments=[
                dict(sequence=1,component='MERCHANDISE',amount='242.00',due_date='2026-11-01')]))
        self.context = dict(dataset_id='one',cash_flows=[],record_counts=dict(cash_flow=0))

    def match(self,flows,record_count=None):
        return payment_matching(self.proposal,dict(self.context,cash_flows=flows,
            record_counts=dict(cash_flow=len(flows) if record_count is None else record_count)))

    def test_unique_candidate_preserves_pending_evidence_without_association(self):
        source=flow()
        before=copy.deepcopy(source)
        result=self.match([source])
        row=result['rows'][0]
        self.assertEqual(row['status'],'ONE_EXACT_CANDIDATE')
        self.assertEqual(row['candidates'][0]['flow_id'],'P-1')
        self.assertEqual(row['candidates'][0]['evidence_state'],'NOT_EVIDENCED')
        self.assertFalse(row['candidates'][0]['due_date_evidenced'])
        self.assertEqual(result['association_status'],'NOT_REVIEWED')
        self.assertFalse(result['included_in_projection'])
        self.assertFalse(result['decision_authority'])
        self.assertEqual(source,before)

    def test_all_three_fields_and_payment_type_are_required(self):
        variants=[flow(amount='241'),flow(kind='COLLECTION'),flow(currency='USD'),flow(due='2026-11-02')]
        result=self.match(variants)
        self.assertEqual(result['rows'][0]['status'],'NO_EXACT_CANDIDATE')
        self.assertEqual(result['rows'][0]['candidates'],[])
        self.assertIn('tampoco se acredita',result['message'])

    def test_multiple_candidates_never_select_one(self):
        result=self.match([flow('P-2'),flow('P-1')])
        row=result['rows'][0]
        self.assertEqual(row['status'],'MULTIPLE_EXACT_CANDIDATES')
        self.assertEqual([c['flow_id'] for c in row['candidates']],['P-1','P-2'])
        self.assertNotIn('selected_flow_id',row)
        self.assertEqual(result['association_status'],'NOT_REVIEWED')

    def test_shared_candidate_between_components_is_visible(self):
        self.proposal['payment_plan']['installments'].append(dict(sequence=2,
            component='FREIGHT',amount='242',due_date='2026-11-01'))
        result=self.match([flow()])
        self.assertTrue(all(r['shared_candidate_ids']==['P-1'] for r in result['rows']))

    def test_bad_inventory_is_explicit_and_duplicate_ids_are_excluded(self):
        for flows,count in [([flow(),flow()],2),([dict(record_id='BAD',canonical={})],1),([flow()],2)]:
            with self.subTest(flows=flows):
                result=self.match(flows,count)
                self.assertEqual(result['status'],'PARTIAL_INVENTORY')
                self.assertTrue(result['issues'])
        mismatch=flow()
        mismatch['record_id']='OTHER'
        self.assertEqual(self.match([mismatch])['rows'][0]['candidates'],[])

    def test_scope_and_legacy(self):
        self.context['dataset_id']='two'
        with self.assertRaises(ValueError):
            self.match([])
        self.context['dataset_id']='one'
        self.proposal.pop('payment_plan')
        self.assertEqual(self.match([])['status'],'NOT_DECLARED')

    def test_evidence_does_not_prove_membership_and_fingerprint_is_deterministic(self):
        f=flow()
        f['canonical'].update(evidence_state='DEMONSTRATED',due_date_evidenced=True)
        first=self.match([f])
        self.assertEqual(first['association_status'],'NOT_REVIEWED')
        self.assertEqual(first,self.match([f]))
        f['canonical']['evidence_state']='CONFLICTING_DATA'
        self.assertNotEqual(first['fingerprint'],self.match([f])['fingerprint'])


class PaymentMatchingPersistenceTest(unittest.TestCase):
    setUp=fixtures.FinancialContextTest.setUp
    tearDown=fixtures.FinancialContextTest.tearDown
    add=fixtures.FinancialContextTest.add

    def test_review_print_freezes_candidate_inventory_without_changing_flows(self):
        item=flow()
        self.add('cash_flow','P-1',dict(canonical=item['canonical']))
        saved=self.desk.save(dict(self.data,shipping_mode='NONE',payment_installments=[
            dict(component='MERCHANDISE',amount='242',due_date='2026-11-01')]))
        report=self.desk.review('one',saved['proposal_id'])
        self.assertEqual(report['version'],'COMPANY-CONTEXT-REVIEW-07')
        matching=report['payment_matching']
        self.assertEqual(matching['rows'][0]['candidates'][0]['flow_id'],'P-1')
        args=('one',saved['proposal_id'],report['review_id'])
        html=self.desk.printable_report(*args)
        self.assertIn('COINCIDENCIAS POR REVISAR',html)
        self.assertIn('P-1',html)
        self.assertIn('Evidencia pendiente',html)
        with sqlite3.connect(self.path) as c:
            original=json.loads(c.execute("SELECT record_json FROM documentary_company_record WHERE kind='cash_flow'").fetchone()[0])
            self.assertEqual(original['data']['canonical'],item['canonical'])
            c.execute("DELETE FROM documentary_company_record WHERE kind='cash_flow'")
        self.assertEqual(self.desk.printable_report(*args),html)
        draft=self.desk.commercial_draft(*args)
        self.assertNotIn('DOC-PAY',draft['body'])
        self.assertNotIn('COINCIDENCIAS POR REVISAR',draft['body'])
