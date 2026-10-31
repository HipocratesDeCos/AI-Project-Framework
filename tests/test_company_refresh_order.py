"""Exercise the shipped refresh functions with deliberately reordered responses."""
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from eios.company_app import PAGE


@unittest.skipUnless(shutil.which('node'), 'Node not installed')
class CompanyRefreshOrderTest(unittest.TestCase):
    def test_delayed_state_parameters_errors_and_return_to_same_company(self):
        start = PAGE.index('async function refresh(){')
        refresh = PAGE[start:PAGE.index('\nfunction view(', start)]
        start = PAGE.index('async function loadParameters(){')
        parameters = PAGE[start:PAGE.index('\n', start)]
        script = r'''
const assert=require('node:assert/strict');
let state,companyRefreshSequence=0,parametersSequence=0,parametersState=null;
let commercialDraftSequence=0,printableReview=null,reviewRequest=0;
const elements=new Map(),$=id=>{if(!elements.has(id))elements.set(id,{value:'',textContent:'',replaceChildren(){},append(){}});return elements.get(id)};
const pending=[],renders=[],parameterRenders=[];
function api(url){return new Promise((resolve,reject)=>pending.push({url,resolve,reject}))}
function take(url){const index=pending.findIndex(item=>item.url===url);assert.notEqual(index,-1,'Missing request: '+url);return pending.splice(index,1)[0]}
function snapshot(dataset){return {info:{dataset_id:dataset,company:{legal_name:dataset},as_of_date:'2026-09-30',documents:0},articles:[],pending:[],suppliers:[],purchases:[],data_status:{dataset_id:dataset}}}
function resetSourceIdentity(){}function syncUploadCompanySelection(){}function resetStockArticleScope(){}function resetPortfolioSearch(){}function resetSupplierPurchaseHistory(){}function resetCustomerReceivedHistory(){}function resetCompanyDataStatus(){}
function renderCompanyDataStatus(report){renders.push(report.dataset_id)}function renderSelectedSales(){}function renderSelectedPurchases(){}function renderSelectedInventory(){}function renderCommercialCatalogue(){}function articles(){}function catalogues(){}function resetSalesOffers(){}
function stockDate(value){return value}function renderParameters(){parameterRenders.push(parametersState.dataset_id)}
const tick=()=>new Promise(resolve=>setImmediate(resolve));
function begin(dataset){$('dataset').value=dataset;return refresh()}
async function finish(dataset){take('/api/state?dataset='+dataset).resolve(snapshot(dataset));await tick();take('/api/parameters?dataset='+dataset).resolve({dataset_id:dataset});await tick()}
'''+refresh+'\n'+parameters+r'''
(async()=>{
 // A slow response from the previous company must not start another parameter load.
 const first=begin('one'),second=begin('two');await finish('two');await second;
 take('/api/state?dataset=one').resolve(snapshot('one'));await first;
 assert.equal(state.info.dataset_id,'two');assert.deepEqual(renders,['two']);assert.deepEqual(parameterRenders,['two']);assert.equal(pending.length,0);

 // Invalidate parameters already pending, before the new state response arrives.
 const third=begin('one');take('/api/state?dataset=one').resolve(snapshot('one'));await tick();const oldParameters=take('/api/parameters?dataset=one');
 const fourth=begin('two');assert.equal(parametersState,null);assert.equal($('parameters-save').disabled,true);
 oldParameters.resolve({dataset_id:'one'});await third;assert.deepEqual(parameterRenders,['two']);assert.deepEqual(renders,['two']);
 await finish('two');await fourth;assert.equal(state.info.dataset_id,'two');

 // Company equality alone is insufficient when switching A -> B -> A.
 const oldA=begin('one'),middleB=begin('two'),newA=begin('one');
 const oldARequest=take('/api/state?dataset=one'),newARequest=take('/api/state?dataset=one');
 newARequest.resolve(snapshot('one'));await tick();take('/api/parameters?dataset=one').resolve({dataset_id:'one'});await newA;
 const renderCount=renders.length;oldARequest.resolve(snapshot('one'));take('/api/state?dataset=two').reject(Error('obsolete network error'));await Promise.all([oldA,middleB]);assert.equal(renders.length,renderCount);assert.equal(state.info.dataset_id,'one');assert.equal(pending.length,0);

 // Same-company refreshes must also honor the latest request.
 const oldSame=begin('one'),newSame=begin('one');const oldRequest=take('/api/state?dataset=one');await finish('one');await newSame;oldRequest.reject(Error('obsolete same-company error'));await oldSame;assert.equal(pending.length,0);

 // Latest errors remain visible, and mismatched data is rejected before assignment.
 const latest=begin('two');const latestError=assert.rejects(latest,/current error/);take('/api/state?dataset=two').reject(Error('current error'));await latestError;
 const wrong=begin('two');const wrongError=assert.rejects(wrong,/no corresponden/);take('/api/state?dataset=two').resolve(snapshot('one'));await wrongError;assert.equal(state.info.dataset_id,'one');
 const badParameters=begin('two');take('/api/state?dataset=two').resolve(snapshot('two'));await tick();const paramError=assert.rejects(badParameters,/parameter error/);take('/api/parameters?dataset=two').reject(Error('parameter error'));await paramError;assert.equal(pending.length,0);
 console.log('Refresh ordering and error scenarios passed');
})().catch(error=>{console.error(error);process.exitCode=1});
'''
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'refresh-order.js'
            path.write_text(script, encoding='utf-8')
            result = subprocess.run(['node', str(path)], capture_output=True,
                                    text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Refresh ordering and error scenarios passed', result.stdout)
