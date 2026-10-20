import sqlite3
import unittest
from tests import test_company_purchase_screen as fixture
from eios.company_stock_minimum import alert, read_minimums, save_minimums

class StockMinimumTest(unittest.TestCase):
    setUp=fixture.PurchaseScreenTest.setUp
    tearDown=fixture.PurchaseScreenTest.tearDown
    def save(self,value,revision=0,dataset='one'):
        return save_minimums(self.path,self.desk.store,dict(dataset_id=dataset,changes=[dict(article_id='A',unit='palets',value=value,revision=revision)]))
    def row(self,dataset='one'):
        return self.desk.state(dataset)['stock_minimums']['A']
    def test_empty_zero_and_reopen(self):
        self.assertIsNone(self.row()['value'])
        self.save('0')
        self.assertEqual(self.row()['value'],'0')
        self.assertEqual(self.row('two')['value'],None)
        self.save('',1)
        self.assertIsNone(self.row()['value'])
        with sqlite3.connect(self.path) as c:
            rows=c.execute('SELECT old_value,new_value FROM company_stock_minimum_history ORDER BY id').fetchall()
        self.assertEqual(rows,[(None,'0'),('0',None)])
    def test_states_and_shortage(self):
        for available,minimum,status,gap in [('0','2','EMPTY','2'),('-1','2','EMPTY','3'),('1','2','LOW','1'),('2','2','LIMIT','0'),('3','2','OK','0')]:
            result=alert(dict(available=available,unit='uds'),minimum,'uds')
            self.assertEqual((result['status'],result['shortage']),(status,gap))
    def test_missing_invalid_or_wrong_unit_unknown(self):
        for inventory,minimum in [(None,'1'),(dict(available='0',unit='uds'),None),(dict(available='NaN',unit='uds'),'1'),(dict(available='2',unit='kg'),'1')]:
            self.assertEqual(alert(inventory,minimum,'uds')['status'],'UNKNOWN')
    def test_invalid_input_does_not_write(self):
        for value in ('-1','NaN','Infinity',True,'1000000001','abc'):
            with self.assertRaises(ValueError):self.save(value)
        self.assertIsNone(self.row()['value'])
    def test_conflict_does_not_overwrite(self):
        self.save('3')
        with self.assertRaises(ValueError):self.save('4')
        self.assertEqual(self.row()['value'],'3')
    def test_atomic_batch(self):
        self.save('3')
        with self.assertRaises(ValueError):
            save_minimums(self.path,self.desk.store,dict(dataset_id='one',changes=[dict(article_id='A',unit='palets',value='4',revision=1),dict(article_id='missing',unit='palets',value='5',revision=0)]))
        self.assertEqual(self.row()['value'],'3')
    def test_unit_and_article_validation(self):
        for patch in (dict(unit='uds'),dict(article_id='MISSING'),dict(revision=True)):
            change=dict(article_id='A',unit='palets',value='4',revision=0);change.update(patch)
            with self.assertRaises(ValueError): save_minimums(self.path,self.desk.store,dict(dataset_id='one',changes=[change]))
    def test_same_company_new_snapshot_reuses_setting(self):
        import json
        self.save('4')
        with sqlite3.connect(self.path) as c:
            raw=c.execute('SELECT manifest_json FROM documentary_company_snapshot WHERE dataset_id=?',('two',)).fetchone()[0]
            manifest=json.loads(raw);manifest['company']['company_id']='one'
            c.execute('UPDATE documentary_company_snapshot SET manifest_json=? WHERE dataset_id=?',(json.dumps(manifest),'two'))
        self.assertEqual(self.row('two')['value'],'4')
    def test_different_unit_does_not_reuse_setting(self):
        self.save('4')
        rows=read_minimums(self.path,'one',[dict(article_id='A',unit_as_documented='uds')],{})
        self.assertIsNone(rows['A']['value'])
    def test_noop_does_not_create_history(self):
        self.save('4');self.save('4',1)
        self.assertEqual(self.row()['revision'],1)
        with sqlite3.connect(self.path) as c:self.assertEqual(c.execute('SELECT count(*) FROM company_stock_minimum_history').fetchone()[0],1)

class AutomaticMinimumTest(unittest.TestCase):
    def history(self,quantity='40',unit='uds.'):
        return [dict(issue_date='2026-09-30',quantity=quantity,unit=unit,invoice_number='INV-1',source_refs=[dict(document_ref='DOC-1')])]
    def test_exact_ten_percent(self):
        from eios.company_stock_minimum import automatic_minimum
        self.assertEqual(automatic_minimum(self.history(),'uds.')['value'],'4')
        self.assertEqual(automatic_minimum(self.history('4','palets'),'palets')['value'],'0.4')
    def test_indivisible_rounds_up(self):
        from eios.company_stock_minimum import automatic_minimum
        result=automatic_minimum(self.history('15'),'uds.')
        self.assertEqual(result['value'],'2')
        self.assertEqual(result['rounding'],'CEILING_WHOLE_UNIT')
    def test_absent_invalid_ambiguous_and_wrong_unit(self):
        from eios.company_stock_minimum import automatic_minimum
        for rows in ([],self.history('0'),self.history('-1'),self.history('NaN'),self.history(unit='kg'),self.history()*2):
            self.assertIsNone(automatic_minimum(rows,'uds.'))
    def test_latest_not_largest_and_no_older_fallback(self):
        from eios.company_stock_minimum import automatic_minimum
        rows=self.history('15')+[dict(issue_date='2026-08-01',quantity='100',unit='uds.')]
        self.assertEqual(automatic_minimum(rows,'uds.')['value'],'2')
        rows[0]['quantity']=None
        self.assertIsNone(automatic_minimum(rows,'uds.'))

class AutomaticMinimumPersistenceTest(unittest.TestCase):
    setUp=fixture.PurchaseScreenTest.setUp
    tearDown=fixture.PurchaseScreenTest.tearDown
    def test_manual_zero_precedence_and_reset_to_automatic(self):
        from eios.company_stock_minimum import read_minimums
        articles=[dict(article_id='A',unit_as_documented='palets')]
        history={'A':[dict(issue_date='2026-09-30',quantity='4',unit='palets')]}
        def read():return read_minimums(self.path,'one',articles,{},history)['A']
        self.assertEqual((read()['value'],read()['source']),('0.4','AUTOMATIC'))
        def save(value,revision):save_minimums(self.path,self.desk.store,dict(dataset_id='one',changes=[dict(article_id='A',unit='palets',value=value,revision=revision)]))
        save('0',0)
        self.assertEqual((read()['value'],read()['source']),('0','MANUAL'))
        save('',1)
        self.assertEqual((read()['value'],read()['source']),('0.4','AUTOMATIC'))
