import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from eios.company_stock_save_ui import JS


@unittest.skipUnless(shutil.which('node'), 'Node not installed')
class StockSaveOrderTest(unittest.TestCase):
    def test_bound_responses_busy_inputs_and_drafts(self):
        script = r'''
const assert=require('node:assert/strict');
let state,companyRefreshSequence=0,inputs=[],renders=0;
const token='test',fields={dataset:{value:'one'},'stock-minimum-save':{},'stock-minimum-notice':{}},$=id=>fields[id];
const document={querySelectorAll:()=>inputs},pending=[];
function api(url,options){return new Promise((resolve,reject)=>pending.push({url,options,resolve,reject}))}
function take(url){const index=pending.findIndex(item=>item.url===url);assert.notEqual(index,-1,url);return pending.splice(index,1)[0]}
function snapshot(dataset){return {info:{dataset_id:dataset},stock_minimums:{A:{value:0,draft:'0',unit:'uds.',revision:1},B:{value:'2',draft:'3',unit:'uds.',revision:4}}}}
function input(id,value){return {dataset:{article:id},value,disabled:false,checkValidity:()=>true,reportValidity(){}}}
function renderStock(){renders++;inputs=[input('A','0')];syncStockMinimumSave()}function renderArticleMinimum(){}
const tick=()=>new Promise(resolve=>setImmediate(resolve));
'''+JS+r'''
(async()=>{
 state=snapshot('one');inputs=[input('A','0')];
 const first=$('stock-minimum-save').onclick(),postOne=take('/api/stock/minimums');
 const payload=JSON.parse(postOne.options.body);assert.equal(payload.dataset_id,'one');assert.deepEqual(payload.changes,[{article_id:'B',unit:'uds.',value:'3',revision:4}]);assert.equal(inputs[0].disabled,true);
 inputs=[input('B','3')];syncStockMinimumSave();assert.equal(inputs[0].disabled,true);await $('stock-minimum-save').onclick();assert.equal(pending.length,0);

 // An obsolete save must not unlock the next company's in-flight save.
 $('dataset').value='two';companyRefreshSequence++;state=snapshot('two');syncStockMinimumSave();const second=$('stock-minimum-save').onclick(),postTwo=take('/api/stock/minimums');
 postOne.resolve({message:'old success'});await first;assert.equal(pending.length,0);assert.equal($('stock-minimum-save').disabled,true);assert.equal(inputs[0].disabled,true);
 postTwo.resolve({message:'saved two'});await tick();const getTwo=take('/api/state?dataset=two');const savedTwo=snapshot('two');delete savedTwo.stock_minimums.B.draft;getTwo.resolve(savedTwo);await second;
 assert.equal(state,savedTwo);assert.equal(renders,1);assert.equal($('stock-minimum-save').disabled,false);assert.equal($('stock-minimum-notice').textContent,'saved two');

 // A state response arriving after a same-company refresh cannot replace it.
 state=snapshot('two');inputs=[];const oldRead=$('stock-minimum-save').onclick();take('/api/stock/minimums').resolve({message:'old read'});await tick();const getOld=take('/api/state?dataset=two');companyRefreshSequence++;const newest=snapshot('two');state=newest;getOld.resolve(snapshot('two'));await oldRead;assert.equal(state,newest);assert.equal(renders,1);

 // A -> B -> A invalidates the original operation even if the dataset matches.
 state=snapshot('one');$('dataset').value='one';inputs=[];const oldA=$('stock-minimum-save').onclick(),oldPost=take('/api/stock/minimums');$('dataset').value='two';companyRefreshSequence++;$('dataset').value='one';companyRefreshSequence++;const beforeError=$('stock-minimum-notice').textContent;oldPost.reject(Error('obsolete error'));await oldA;assert.equal($('stock-minimum-notice').textContent,beforeError);

 // Current failures preserve edits and release live inputs.
 const failed=$('stock-minimum-save').onclick();take('/api/stock/minimums').reject(Error('current failure'));await failed;assert.equal(state.stock_minimums.B.draft,'3');assert.equal($('stock-minimum-save').disabled,false);assert.equal($('stock-minimum-notice').textContent,'current failure');
 const wrong=$('stock-minimum-save').onclick();take('/api/stock/minimums').resolve({message:'saved'});await tick();const beforeWrong=state;take('/api/state?dataset=one').resolve(snapshot('two'));await wrong;assert.equal(state,beforeWrong);assert.match($('stock-minimum-notice').textContent,/no corresponde/);

 // Existing guards: no edits, over 100 edits, and a mismatched company.
 state=snapshot('one');delete state.stock_minimums.B.draft;await $('stock-minimum-save').onclick();assert.equal(pending.length,0);assert.match($('stock-minimum-notice').textContent,/No hay cambios/);
 state.stock_minimums=Object.fromEntries(Array.from({length:101},(_,i)=>['X'+i,{value:'0',draft:'1',unit:'uds.',revision:0}]));await $('stock-minimum-save').onclick();assert.equal(pending.length,0);assert.match($('stock-minimum-notice').textContent,/hasta 100/);
 $('dataset').value='two';await $('stock-minimum-save').onclick();assert.equal(pending.length,0);
 console.log('Minimum save ordering scenarios passed');
})().catch(error=>{console.error(error);process.exitCode=1});
'''
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'stock-save-order.js'
            path.write_text(script, encoding='utf-8')
            result = subprocess.run(['node', str(path)], capture_output=True,
                                    text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Minimum save ordering scenarios passed', result.stdout)
