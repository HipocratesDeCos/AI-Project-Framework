"""Explicit purchase lifecycle actions; no changes to decision authority or storage."""
CSS='''
#po-lifecycle{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;margin:12px 0;padding:12px 16px;border:1px solid var(--guide-border,#dce3ef);border-radius:12px;background:var(--guide-surface,#fff)}#po-lifecycle p{margin:0;font:inherit}#po-lifecycle-actions{display:flex;gap:8px;flex-wrap:wrap}#po-lifecycle button{font:inherit;padding:9px 12px;border:1px solid var(--guide-border,#bfd2ed);border-radius:8px;background:var(--guide-soft,#f4f6fb);color:var(--guide-ink,#102748);cursor:pointer}#po-new-purchase{background:#1553f0!important;color:white!important}#po-lifecycle-help{font-size:12px!important;color:var(--guide-muted,#55627a)}
'''
JS=r'''
(function(){
 const form=$('form'),page=form.closest('[data-view=propuestas]'),bar=document.createElement('section');bar.id='po-lifecycle';bar.setAttribute('aria-label','Acciones de la propuesta');
 const labels=document.createElement('div'),status=document.createElement('p'),help=document.createElement('p');status.setAttribute('role','status');help.id='po-lifecycle-help';labels.append(status,help);const actions=document.createElement('div');actions.id='po-lifecycle-actions';bar.append(labels,actions);page.querySelector('.po-intro').after(bar);
 let dirty=false,report=null,starting=false;
 window.purchaseWorkflowState=()=>Object.freeze({mode:document.body.dataset.purchaseMode==='saved'?'saved':'draft',hasWorkingDraft:dirty,reference:report?.proposal?.reference||null,agreement:report?.purchase_agreement?.status||'NOT_DECLARED',choiceCurrent:!!window.purchaseChoiceIsCurrent?.()});
 function button(id,label,action){const b=document.createElement('button');b.id=id;b.type='button';b.textContent=label;b.onclick=action;actions.append(b);return b}
 const fresh=button('po-new-purchase','Nueva propuesta desde cero',async()=>{
  if(starting||$('save').getAttribute('aria-busy')==='true')return;
  if(dirty&&!window.confirm('Hay un borrador sin guardar. ¿Quieres descartarlo y empezar una propuesta nueva? Los estudios guardados se conservan.'))return;
  starting=true;fresh.disabled=true;
  try{form.dispatchEvent(new Event('input',{bubbles:true}));clearPurchaseSummary();clearPurchaseAlternativesTable();form.reset();await Promise.resolve();
   for(const name of ['reference','quantity','order_date','delivery_location'])form.elements[name].value='';
   $('payment-plan-enabled').checked=false;$('payment-plan-rows').replaceChildren();paymentRowsEnabled();$('supplier').value='';articles();$('article').value='';
   printableReview=null;report=null;$('notice').textContent='';form.dispatchEvent(new Event('change',{bubbles:true}));await Promise.resolve();dirty=false;purchaseGuideNavigate('po-selection',true);render();$('supplier').focus();
  }finally{starting=false;render()}
 });
 const resume=button('po-resume-purchase','Retomar borrador',()=>{const back=$('po-return-draft');if(back?.onclick){back.onclick();queueMicrotask(()=>{purchaseGuideNavigate('po-selection',true);render()})}});
 const copy=button('po-copy-purchase','Crear versión desde este estudio',()=>{if(dirty&&!window.confirm('Esta copia sustituirá el borrador sin guardar. ¿Quieres continuar? El estudio original se conserva.'))return;$('po-create-study-draft')?.click()});
 button('po-consult-purchases','Consultar estudios guardados',()=>{const list=$('po-saved');list.tabIndex=-1;list.focus({preventScroll:true});list.scrollIntoView({block:'start'})});
 function render(){const state=window.purchaseWorkflowState(),saved=state.mode==='saved';status.textContent=saved?'Estudio guardado · '+(state.reference||'Consulta'):dirty?'Borrador en edición':'Nueva propuesta';help.textContent=saved?'Solo lectura. El acuerdo registrado es una declaración del usuario.':dirty?'Los cambios de este borrador aún no están guardados.':'Empieza eligiendo proveedor y artículo.';resume.hidden=!saved;resume.disabled=!dirty;resume.title=dirty?'Recupera el formulario que estabas editando.':'No hay un borrador pendiente en esta sesión.';copy.hidden=!saved;fresh.disabled=starting||$('save').getAttribute('aria-busy')==='true';}
 for(const type of ['input','change'])form.addEventListener(type,()=>{if(!starting&&document.body.dataset.purchaseMode!=='saved')dirty=true;render()});form.addEventListener('reset',()=>{dirty=false;queueMicrotask(render)});$('dataset').addEventListener('change',()=>{dirty=false;report=null;render()});
 const finance=renderFinancialContext;renderFinancialContext=function(value){finance(value);report=value;render()};
 new MutationObserver(render).observe(document.body,{attributes:true,attributeFilter:['data-purchase-mode']});new MutationObserver(render).observe($('save'),{attributes:true,attributeFilter:['aria-busy']});render();
})();
'''
