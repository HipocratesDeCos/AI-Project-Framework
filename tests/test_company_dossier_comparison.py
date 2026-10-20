from pathlib import Path
import tempfile
import unittest

from eios.company_dossier_comparison import compare_versions
from eios.company_dossier_versions import save_version
from eios.company_reception import CompanyReception


class DossierComparisonTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db=Path(self.tmp.name)/'company.db'
        self.reception=CompanyReception(self.db)

    def receive(self,rows,company='A',cutoff='2026-09-30'):
        content=('Codigo;Nombre\n'+rows).encode()
        uploaded=self.reception.read(content,'suppliers.csv',delimiter=';')
        checked=self.reception.preview(dict(upload=uploaded['upload'],company_id=company,legal_name='Empresa '+company,material_nature='REAL',as_of_date=cutoff,kind='supplier',number_format='ES',mapping=dict(supplier_id=0,legal_name=1)))
        return self.reception.commit(checked['ticket'])['batch_id']

    def save(self,ids,name):
        return save_version(self.db,ids,name)['dossier_id']

    def test_added_removed_shared_and_data_change_without_row_count_change(self):
        original=self.receive('S1;Original\n')
        corrected=self.receive('S1;Corregido\n')
        shared=self.receive('S2;Compartido\n')
        before=self.save([original,shared],'V1')
        after=self.save([corrected,shared],'V2')
        report=compare_versions(self.db,before,after)
        self.assertEqual([x['batch_id'] for x in report['added_files']],[corrected])
        self.assertEqual([x['batch_id'] for x in report['removed_files']],[original])
        self.assertEqual([x['batch_id'] for x in report['shared_files']],[shared])
        category=next(x for x in report['categories'] if x['kind']=='supplier')
        self.assertEqual(category['before_rows'],2)
        self.assertEqual(category['after_rows'],2)
        self.assertEqual(category['added_exact_rows'],1)
        self.assertEqual(category['removed_exact_rows'],1)

    def test_order_changes_file_identity_but_not_normalized_row_content(self):
        a=self.receive('S1;Uno\nS2;Dos\n')
        b=self.receive('S2;Dos\nS1;Uno\n')
        before=self.save([a],'V1');after=self.save([b],'V2')
        report=compare_versions(self.db,before,after)
        self.assertEqual(len(report['added_files']),1)
        self.assertEqual(len(report['removed_files']),1)
        self.assertTrue(all(x['added_exact_rows']==x['removed_exact_rows']==0 for x in report['categories']))

    def test_multiplicity_not_deduplicated_and_retired_source_not_claimed_as_improvement(self):
        a=self.receive('S1;Uno\n')
        # Different filename gives a separate batch with identical normalized data.
        content=b'Codigo;Nombre\nS1;Uno\n'
        uploaded=self.reception.read(content,'copy.csv',delimiter=';')
        checked=self.reception.preview(dict(upload=uploaded['upload'],company_id='A',legal_name='Empresa A',material_nature='REAL',as_of_date='2026-09-30',kind='supplier',number_format='ES',mapping=dict(supplier_id=0,legal_name=1)))
        b=self.reception.commit(checked['ticket'])['batch_id']
        before=self.save([a,b],'Duplicada');after=self.save([a],'Solo original')
        report=compare_versions(self.db,before,after)
        category=next(x for x in report['categories'] if x['kind']=='supplier')
        self.assertEqual(category['removed_exact_rows'],1)
        self.assertEqual(report['before']['issue_count'],1)
        self.assertEqual(report['after']['issue_count'],0)
        self.assertIn('no acredita mejora',report['scope'])
        self.assertEqual(report['check_counts'][0]['code'],'REPEATED_ID')
        self.assertEqual(report['check_counts'][0]['delta'],-1)
        self.assertFalse(report['decision_authority'])

    def test_reverse_and_same_version_and_no_database_changes(self):
        a=self.receive('S1;Uno\n');b=self.receive('S2;Dos\n')
        before=self.save([a],'V1');after=self.save([a,b],'V2')
        snapshot=self.db.read_bytes()
        reverse=compare_versions(self.db,after,before)
        self.assertEqual(len(reverse['added_files']),0)
        self.assertEqual(len(reverse['removed_files']),1)
        same=compare_versions(self.db,before,before)
        self.assertEqual(same['added_files'],same['removed_files'])
        self.assertEqual(len(same['shared_files']),1)
        self.assertEqual(snapshot,self.db.read_bytes())
        self.assertEqual(same['admission_status'],'PENDING')
        self.assertEqual(same['operational_path'],'FORBIDDEN')

    def test_same_company_and_cutoff_required(self):
        a=self.receive('S1;Uno\n')
        b=self.receive('S1;Uno\n',company='B')
        c=self.receive('S1;Uno\n',cutoff='2026-08-31')
        first=self.save([a],'V1')
        for other in [self.save([b],'Otra empresa'),self.save([c],'Otro corte')]:
            with self.assertRaisesRegex(ValueError,'misma empresa'):
                compare_versions(self.db,first,other)
        with self.assertRaises(ValueError):compare_versions(self.db,first,'x'*64)

    def test_all_rows_beyond_preview(self):
        rows=''.join('S'+str(i)+';Proveedor\n' for i in range(25))
        a=self.receive(rows+'LAST;Original\n')
        b=self.receive(rows+'LAST;Corregido\n')
        report=compare_versions(self.db,self.save([a],'V1'),self.save([b],'V2'))
        category=next(x for x in report['categories'] if x['kind']=='supplier')
        self.assertEqual(category['before_rows'],26)
        self.assertEqual(category['after_rows'],26)
        self.assertEqual(category['added_exact_rows'],1)
        self.assertEqual(category['removed_exact_rows'],1)
