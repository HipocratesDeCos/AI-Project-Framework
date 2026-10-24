"""Keep a minimum-save response bound to the state and company that requested it."""

JS = r'''
let stockMinimumSaveContext=null;
function stockMinimumContextCurrent(context){return !!context&&context.dataset===$('dataset').value&&state===context.state&&companyRefreshSequence===context.refreshSequence}
function stockMinimumSaveBusy(){return stockMinimumContextCurrent(stockMinimumSaveContext)}
function syncStockMinimumSave(){const blocked=state?.info?.dataset_id!==$('dataset').value||stockMinimumSaveBusy();$('stock-minimum-save').disabled=blocked;document.querySelectorAll('#stock-table input').forEach(input=>input.disabled=blocked)}
$('stock-minimum-save').onclick=async()=>{
 if(state?.info?.dataset_id!==$('dataset').value||stockMinimumSaveBusy())return;
 const dataset=$('dataset').value,changes=[];
 for(const input of document.querySelectorAll('#stock-table input')){if(!input.checkValidity()){input.reportValidity();return}const minimum=state.stock_minimums[input.dataset.article];if(input.value!==String(minimum.value??''))changes.push({article_id:input.dataset.article,unit:minimum.unit,value:input.value,revision:minimum.revision})}
 for(const [sku,minimum] of Object.entries(state.stock_minimums)){if(!changes.some(change=>change.article_id===sku)&&minimum.draft!==undefined&&String(minimum.draft)!==String(minimum.value??''))changes.push({article_id:sku,unit:minimum.unit,value:minimum.draft,revision:minimum.revision})}
 if(changes.length>100){$('stock-minimum-notice').textContent='Guarda hasta 100 cambios de mínimos por operación.';return}if(!changes.length){$('stock-minimum-notice').textContent='No hay cambios que guardar.';return}
 const context={dataset,state,refreshSequence:companyRefreshSequence};stockMinimumSaveContext=context;syncStockMinimumSave();$('stock-minimum-notice').textContent='Guardando los mínimos de esta empresa…';
 try{
  const result=await api('/api/stock/minimums',{method:'POST',headers:{'Content-Type':'application/json','X-EIOS-Token':token},body:JSON.stringify({dataset_id:dataset,changes})});if(!stockMinimumContextCurrent(context))return;
  const fresh=await api('/api/state?dataset='+encodeURIComponent(dataset));if(!stockMinimumContextCurrent(context))return;if(fresh?.info?.dataset_id!==dataset)throw Error('La respuesta de mínimos no corresponde a la empresa seleccionada. Actualiza sus datos.');
  state=fresh;renderStock();renderArticleMinimum();$('stock-minimum-notice').textContent=result.message;
 }catch(error){if(stockMinimumContextCurrent(context))$('stock-minimum-notice').textContent=error.message}
 finally{if(stockMinimumSaveContext===context)stockMinimumSaveContext=null;syncStockMinimumSave()}
};
'''
