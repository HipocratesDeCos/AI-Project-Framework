import sqlite3
import unittest
from eios.company_parameters import read_parameters,save_parameters,BY_ID
from tests import test_company_purchase_screen as fixture


class CompanyParametersTest(unittest.TestCase):
    setUp=fixture.PurchaseScreenTest.setUp
    tearDown=fixture.PurchaseScreenTest.tearDown

    def data(self, **patch):
        value=dict(dataset_id='one',revision=0,actor='Andrés',reason='Política de prueba',
                   profile={},values={'P-FIN-001':'90','P-FIN-002':'5000'},references={},critical_acknowledged=True)
        value.update(patch)
        return value

    def test_save_reopen_isolation_and_no_silent_defaults(self):
        initial=read_parameters(self.path,self.desk.store,'one')
        self.assertEqual(initial['current']['values'],{})
        saved=save_parameters(self.path,self.desk.store,self.data())
        self.assertEqual(saved['current']['values']['P-FIN-002'],'5000')
        self.assertEqual(saved['current']['revision'],1)
        self.assertEqual(read_parameters(self.path,self.desk.store,'two')['current']['values'],{})
        self.assertEqual(saved['current']['status'],'PENDING_ENGINE_ACTIVATION')
        self.assertFalse(saved['current']['decision_authority'])
        self.assertEqual(saved['current']['operational_path'],'FORBIDDEN')
        self.assertTrue(all(item['sector_range'] is None for item in initial['catalogue']))

    def test_changes_keep_history_and_stale_requests_fail(self):
        save_parameters(self.path,self.desk.store,self.data())
        changed=save_parameters(self.path,self.desk.store,self.data(revision=1,values={'P-FIN-001':'120','P-FIN-002':'6000'}))
        self.assertEqual(len(changed['history']),2)
        self.assertEqual(changed['current']['previous_values']['P-FIN-002'],'5000')
        self.assertEqual(changed['history'][1]['values']['P-FIN-002'],'5000')
        with self.assertRaises(ValueError):
            save_parameters(self.path,self.desk.store,self.data())

    def test_financial_acknowledgement_and_guardrails(self):
        for patch in [dict(critical_acknowledged=False),
                      dict(values={'P-FIN-002':'-1'}),dict(values={'P-FIN-001':'0'}),
                      dict(values={'P-FIN-001':'1.5'}),dict(values={'P-PRE-001':'NaN'}),
                      dict(values={'P-RGL-004':'No'}),dict(values={'P-FIN-005':'No'}),
                      dict(values={'P-DAT-004':'Sí'}),dict(values={'P-STK-001':'20'}),
                      dict(values={'UNKNOWN':'1'}),dict(actor=''),dict(reason=''),
                      dict(values={'P-STK-003':'90','P-STK-004':'30'})]:
            with self.assertRaises(ValueError):
                save_parameters(self.path,self.desk.store,self.data(**patch))
        self.assertEqual(read_parameters(self.path,self.desk.store,'one')['history'],[])

    def test_sector_reference_needs_explicit_source_and_profile(self):
        reference=dict(lower='30',upper='60',source='Estudio de prueba',period='2025',
                       definition='Ventana de planificación en días; referencia de prueba, no recomendación')
        with self.assertRaises(ValueError):
            save_parameters(self.path,self.desk.store,self.data(references={'P-FIN-001':reference}))
        profile=dict(activity='Comercio',iae='TEST-IAE',size='Tramo de prueba',country='España')
        saved=save_parameters(self.path,self.desk.store,self.data(profile=profile,references={'P-FIN-001':reference}))
        band=saved['current']['references']['P-FIN-001']
        self.assertEqual(band['status'],'USER_DECLARED_NOT_VERIFIED')
        self.assertEqual(band['profile'],profile)
        self.assertEqual(saved['current']['values']['P-FIN-001'],'90')

    def test_sector_reference_validation(self):
        profile=dict(activity='Comercio',cnae='TEST',cnae_version='CNAE-2025',size='Prueba',country='ES')
        for reference in [dict(lower='60',upper='30',source='Fuente',period='2025',definition='Días'),
                          dict(lower='30',upper='60',source='',period='2025',definition='Días'),
                          dict(lower='NaN',upper='60',source='Fuente',period='2025',definition='Días')]:
            with self.assertRaises(ValueError):
                save_parameters(self.path,self.desk.store,self.data(profile=profile,references={'P-FIN-001':reference}))

    def test_catalogue_explains_effects_and_does_not_activate_rules(self):
        self.assertGreaterEqual(len(BY_ID),40)
        self.assertTrue(all(item['effect'] and item['unit'] for item in BY_ID.values()))
        self.assertFalse(BY_ID['P-RGL-004']['editable'])
        self.assertFalse(BY_ID['P-DAT-004']['editable'])
        self.assertFalse(BY_ID['P-STK-001']['editable'])
        self.assertEqual(BY_ID['P-FIN-001']['standard'],'30')
        state=save_parameters(self.path,self.desk.store,self.data())
        with sqlite3.connect(self.path) as c:
            self.assertEqual(c.execute('SELECT count(*) FROM manual_purchase_proposal').fetchone()[0],0)
