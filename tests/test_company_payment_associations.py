import json
import sqlite3
import unittest

from tests import test_company_financial_context as fixture


class PaymentAssociationsTest(unittest.TestCase):
    tearDown=fixture.FinancialContextTest.tearDown
    add=fixture.FinancialContextTest.add

    def setUp(self):
        fixture.FinancialContextTest.setUp(self)
        with sqlite3.connect(self.path) as c:
            c.execute('ALTER TABLE documentary_source ADD COLUMN document_ref TEXT')
            c.execute('ALTER TABLE documentary_source ADD COLUMN content BLOB')
            c.execute('INSERT INTO documentary_source VALUES(?,?,?)',('one','DOC-PAY',b'Synthetic payment document'))
        self.add('cash_flow','P-1',dict(canonical=dict(flow_id='P-1',flow_type='PAYMENT',
            amount='242',currency='EUR',due_date='2026-11-01',due_date_evidenced=False,
            evidence_state='NOT_EVIDENCED',source_ref='DOC-PAY')))
        # Preserve the existing fixture add() carrier, but explicitly bind this source.
        with sqlite3.connect(self.path) as c:
            row=c.execute("SELECT record_json FROM documentary_company_record WHERE kind='cash_flow'").fetchone()
            value=json.loads(row[0]);value['source_refs']=[dict(document_ref='DOC-PAY')]
            c.execute("UPDATE documentary_company_record SET record_json=? WHERE kind='cash_flow'",(json.dumps(value),))
        self.saved=self.desk.save(dict(self.data,shipping_mode='NONE',
            payment_installments=[dict(component='MERCHANDISE',amount='242',due_date='2026-11-01')]))
        self.report=self.desk.review('one',self.saved['proposal_id'])
        self.payload=dict(dataset_id='one',proposal_id=self.saved['proposal_id'],review_id=self.report['review_id'],
            revision=0,sequence=1,action='BIND',flow_id='P-1',
            locator=dict(document_ref='DOC-PAY',page=1,section='Condiciones de pago'),
            actor='Responsable local',reason='Correspondencia declarada para la prueba sintética')

    def test_declaration_is_preserved_without_promoting_evidence_or_changing_old_print(self):
        args=('one',self.saved['proposal_id'],self.report['review_id'])
        old=self.desk.printable_report(*args)
        result=self.desk.declare_payment_association(self.payload)
        self.assertEqual(result['revision'],1)
        self.assertEqual(result['rows'][0]['binding']['flow_id'],'P-1')
        self.assertEqual(result['documentary_review_status'],'NOT_PERFORMED')
        self.assertFalse(result['included_in_projection'])
        self.assertEqual(self.desk.printable_report(*args),old)
        current=self.desk.review('one',self.saved['proposal_id'])
        self.assertEqual(current['version'],'COMPANY-CONTEXT-REVIEW-11')
        self.assertEqual(current['payment_associations'],result)
        html=self.desk.printable_report('one',self.saved['proposal_id'],current['review_id'])
        self.assertIn('ASOCIACIONES DECLARADAS',html)
        self.assertIn('Condiciones de pago',html)
        self.assertEqual(current['financial_context']['cash_flows'][0]['canonical']['evidence_state'],'NOT_EVIDENCED')
        self.assertIsNone(current['finance_execution']['finance_result'])

    def test_invalid_fields_and_foreign_sources_never_write(self):
        for patch in [dict(actor=''),dict(reason=''),dict(sequence=2),dict(sequence=True),
                      dict(action='CONFIRMED'),dict(flow_id='FOREIGN'),dict(revision=True),
                      dict(locator=dict(document_ref='FOREIGN',page=1,section='X')),
                      dict(locator=dict(document_ref='DOC-PAY',page=True,section='X')),
                      dict(locator=dict(document_ref='DOC-PAY',page=0,section='X')),
                      dict(locator=dict(document_ref='DOC-PAY',page=1,section=''))]:
            with self.subTest(patch=patch):
                with self.assertRaises(ValueError):
                    self.desk.declare_payment_association(dict(self.payload,**patch))
        with sqlite3.connect(self.path) as c:
            self.assertEqual(c.execute('SELECT count(*) FROM company_payment_association_event').fetchone()[0],0)

    def test_stale_revision_and_clear_keep_history(self):
        self.desk.declare_payment_association(self.payload)
        with self.assertRaises(ValueError):
            self.desk.declare_payment_association(self.payload)
        result=self.desk.declare_payment_association(dict(self.payload,revision=1,action='CLEAR',locator=None))
        self.assertEqual(result['revision'],2)
        self.assertEqual(result['rows'][0]['action'],'CLEAR')
        self.assertIsNone(result['rows'][0]['binding'])
        with sqlite3.connect(self.path) as c:
            self.assertEqual(c.execute('SELECT count(*) FROM company_payment_association_event').fetchone()[0],2)

    def test_changed_documentary_content_rejects_declaration(self):
        with sqlite3.connect(self.path) as c:
            c.execute("UPDATE documentary_source SET content=?",(b'changed',))
        with self.assertRaises(ValueError):
            self.desk.declare_payment_association(self.payload)

    def test_wrong_review_scope_and_missing_plan_rejected(self):
        with self.assertRaises(ValueError):
            self.desk.declare_payment_association(dict(self.payload,dataset_id='two'))
        saved=self.desk.save(dict(self.data,reference='NO-PLAN'))
        review=self.desk.review('one',saved['proposal_id'])
        with self.assertRaises(ValueError):
            self.desk.declare_payment_association(dict(self.payload,proposal_id=saved['proposal_id'],review_id=review['review_id']))

    def test_same_payment_cannot_be_reused_between_installments(self):
        from eios.company_payment_associations import save_association
        import copy
        report=copy.deepcopy(self.report)
        second=copy.deepcopy(report['payment_matching']['rows'][0]);second['sequence']=2
        report['payment_matching']['rows'].append(second)
        installment=copy.deepcopy(report['proposal']['payment_plan']['installments'][0])
        installment['sequence']=2
        installment['canonical_candidate']['flow_id']='candidate-2'
        report['proposal']['payment_plan']['installments'].append(installment)
        save_association(self.path,report,self.payload)
        with self.assertRaises(ValueError):
            save_association(self.path,report,dict(self.payload,sequence=2,revision=1))

    def test_print_escapes_declared_text_and_draft_excludes_internal_findings(self):
        self.desk.declare_payment_association(dict(self.payload,actor='<script>local</script>'))
        review=self.desk.review('one',self.saved['proposal_id'])
        args=('one',self.saved['proposal_id'],review['review_id'])
        html=self.desk.printable_report(*args)
        self.assertIn('&lt;script&gt;local&lt;/script&gt;',html)
        self.assertNotIn('<script>local</script>',html)
        draft=self.desk.commercial_draft(*args)
        self.assertNotIn('DOC-PAY',draft['body'])
        self.assertNotIn('Responsable local',draft['body'])

    def test_coverage_counts_amounts_before_binding_after_binding_and_clear(self):
        coverage=self.report['payment_associations']['declared_calendar_coverage']
        self.assertEqual(coverage['status'],'PENDING_DECLARATIONS')
        self.assertEqual((coverage['associated_count'],coverage['pending_count']),(0,1))
        self.assertEqual(coverage['pending_total'],'242.00')
        saved=self.desk.declare_payment_association(self.payload)
        coverage=saved['declared_calendar_coverage']
        self.assertEqual(coverage['status'],'ALL_INSTALLMENTS_DECLARED_NOT_REVIEWED')
        self.assertEqual(coverage['associated_total'],'242.00')
        self.assertEqual(coverage['pending_total'],'0.00')
        self.assertEqual(coverage['required_installment_coverage_status'],'NOT_EXECUTED')
        self.assertFalse(coverage['evidence_complete'])
        cleared=self.desk.declare_payment_association(dict(self.payload,revision=1,action='CLEAR'))
        coverage=cleared['declared_calendar_coverage']
        self.assertEqual(coverage['rows'][0]['state'],'LEFT_PENDING')
        self.assertEqual(coverage['pending_total'],'242.00')

    def test_same_version_cross_proposal_reuse_is_blocked_and_clear_releases(self):
        self.desk.declare_payment_association(self.payload)
        other=self.desk.save(dict(self.data,reference='SECOND',shipping_mode='NONE',
            payment_installments=[dict(component='MERCHANDISE',amount='242',due_date='2026-11-01')]))
        report=self.desk.review('one',other['proposal_id'])
        payload=dict(self.payload,proposal_id=other['proposal_id'],review_id=report['review_id'])
        with self.assertRaisesRegex(ValueError,'otra propuesta'):
            self.desk.declare_payment_association(payload)
        self.desk.declare_payment_association(dict(self.payload,revision=1,action='CLEAR'))
        result=self.desk.declare_payment_association(payload)
        self.assertEqual(result['declared_calendar_coverage']['associated_count'],1)

    def test_coverage_print_is_frozen_and_no_declaration_remains_pending(self):
        args=('one',self.saved['proposal_id'],self.report['review_id'])
        old=self.desk.printable_report(*args)
        self.assertIn('COBERTURA DE LAS DECLARACIONES DE PAGO',old)
        self.assertIn('242,00 EUR',old)
        self.desk.declare_payment_association(self.payload)
        self.assertEqual(self.desk.printable_report(*args),old)
        report=self.desk.review('one',self.saved['proposal_id'])
        html=self.desk.printable_report('one',self.saved['proposal_id'],report['review_id'])
        self.assertIn('Todas las cuotas declaradas',html)
        self.assertIn('revisión documental pendiente',html)

    def test_pending_other_proposal_and_other_dataset_do_not_reserve_payment(self):
        from eios.company_payment_associations import _other_bindings
        self.desk.declare_payment_association(dict(self.payload,action='CLEAR'))
        other=self.desk.save(dict(self.data,reference='OTHER',shipping_mode='NONE',
            payment_installments=[dict(component='MERCHANDISE',amount='242',due_date='2026-11-01')]))
        report=self.desk.review('one',other['proposal_id'])
        with sqlite3.connect(self.path) as c:
            fp=report['proposal']['documentary_context_at_save']['fingerprint']
            self.assertEqual(_other_bindings(c,report,fp),[])
            self.assertEqual(_other_bindings(c,dict(report,dataset_id='two'),fp),[])
