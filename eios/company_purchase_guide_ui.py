"""Guided purchase presentation; reuse existing fields, quotes and saved records."""
CSS = '''
[data-view=propuestas].po-guided{--guide-ink:#0f1b33;--guide-muted:#55627a;--guide-surface:#fff;--guide-soft:#f4f6fb;--guide-border:#dce3ef;--guide-accent:#1553f0;color:var(--guide-ink)}
[data-theme=dark] [data-view=propuestas].po-guided{--guide-ink:#e7eefc;--guide-muted:#b5c5df;--guide-surface:#121f33;--guide-soft:#0b1525;--guide-border:#415675;--guide-accent:#91b9ff}
[data-view=propuestas].po-guided .po-intro h2{font-size:clamp(26px,3vw,40px);margin-bottom:8px}
[data-view=propuestas].po-guided .po-nav{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:8px;margin:18px 0}
[data-view=propuestas].po-guided .po-nav a{display:flex;flex-direction:column;justify-content:center;gap:5px;min-height:64px;box-sizing:border-box;padding:10px;border:1px solid var(--guide-border);border-radius:12px;background:var(--guide-surface);color:var(--guide-ink);font-size:13px;text-align:left}
[data-view=propuestas].po-guided .po-nav a[aria-current=step]{border-color:var(--guide-accent);box-shadow:inset 0 -3px var(--guide-accent)}
[data-view=propuestas].po-guided .po-nav a small{font-size:11px;color:var(--guide-muted);font-weight:400}
[data-view=propuestas].po-guided .po-guide-facts{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin:16px 0}
[data-view=propuestas].po-guided .po-guide-facts>div{padding:12px;border:1px solid var(--guide-border);border-radius:10px;background:var(--guide-soft);min-width:0}
[data-view=propuestas].po-guided .po-guide-facts dt{font-size:13px;color:var(--guide-muted);margin-bottom:5px}
[data-view=propuestas].po-guided .po-guide-facts dd{margin:0;font-size:16px;overflow-wrap:anywhere;font-variant-numeric:tabular-nums}
[data-view=propuestas].po-guided .po-guide-saved-actions{display:flex;flex-wrap:wrap;gap:10px;margin:18px 0}
[data-view=propuestas].po-guided .po-guide-snapshot .scroll{overflow:auto;max-width:100%}
@media(max-width:600px){[data-view=propuestas].po-guided .po-guide-facts{grid-template-columns:minmax(0,1fr)}}
[data-view=propuestas].po-guided .po-guide-help{font-size:14px;color:var(--guide-muted);line-height:1.55;margin:10px 0}
[data-view=propuestas].po-guided .po-guide-result{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;padding:16px 0 0;margin:16px 0 0;border-top:1px solid var(--guide-border)}
[data-view=propuestas].po-guided .po-guide-result p{margin:0;max-width:65ch;font-size:14px;color:var(--guide-muted)}
[data-view=propuestas].po-guided .po-guide-result button{min-height:44px;background:var(--guide-accent);color:#fff;border:0;border-radius:10px;padding:12px 18px;font:inherit;font-weight:600}
[data-theme=dark] [data-view=propuestas].po-guided .po-guide-result button{color:#0a1a3c}
[data-view=propuestas].po-guided .po-guide-state{display:inline-block;border-radius:20px;padding:5px 10px;background:var(--guide-soft);color:var(--guide-muted);font:500 12px var(--eios-font)}
[data-view=propuestas].po-guided .po-guide-state[data-status=complete]{background:#e3f4ee;color:#0b5c4a}
[data-view=propuestas].po-guided .po-guide-state[data-status=attention]{background:#fff1dc;color:#7a3e00}
[data-view=propuestas].po-guided .po-guide-state[data-status=current]{background:#eaf0ff;color:#1642a2}
[data-view=propuestas].po-guided .po-workspace{grid-template-columns:minmax(0,1fr) minmax(280px,340px);gap:20px}
[data-view=propuestas].po-guided .po-context{position:sticky;top:210px;max-height:calc(100vh - 230px);overflow:auto}
[data-view=propuestas].po-guided .po-context:empty{display:none}
[data-view=propuestas].po-guided .po-step{scroll-margin-top:220px}
[data-view=propuestas].po-guided .po-negotiation-scroll{position:relative;overflow-x:auto;max-width:100%;min-width:0}
[data-view=propuestas].po-guided .po-nav a[aria-disabled=true]{opacity:.65}
[data-view=propuestas].po-guided .po-heading>span{display:grid;border-radius:50%;background:#0a1a3c;color:white;min-width:40px;height:40px}
[data-view=propuestas].po-guided .po-guide-error{color:#a82d24;font-size:13px}
[data-theme=dark] [data-view=propuestas].po-guided .po-guide-error{color:#ffb8af}
[data-view=propuestas].po-guided #po-guide-to-agreement{background:transparent;color:var(--guide-accent);border:1px solid var(--guide-accent)}
[data-view=propuestas].po-guided #po-references .po-shared-conditions input{font-size:18px}
[data-view=propuestas].po-guided #po-references .po-shared-conditions{margin:16px 0}
[data-view=propuestas].po-guided #po-guide-agreement{border:1px solid var(--guide-border);background:var(--guide-surface);color:var(--guide-ink);padding:22px;border-radius:18px;margin-top:20px}
[data-view=propuestas].po-guided #po-guide-agreement button{min-height:44px;font:inherit;padding:10px 16px;cursor:pointer}
[data-view=propuestas].po-guided #po-guide-live{position:absolute;width:1px;height:1px;padding:0;border:0;margin:-1px;overflow:hidden;clip-path:inset(50%);white-space:nowrap}
[data-view=propuestas].po-guided :is(a,button,input,select,textarea):focus-visible{outline:3px solid var(--guide-accent);outline-offset:3px}
[data-view=propuestas].po-guided #po-guide-agreement[hidden]{display:none}
@media(max-width:1100px){[data-view=propuestas].po-guided .po-workspace{grid-template-columns:minmax(0,1fr)}[data-view=propuestas].po-guided .po-context{position:static;max-height:none}}
@media(max-width:900px){[data-view=propuestas].po-guided .po-nav{grid-template-columns:repeat(3,minmax(0,1fr))}[data-view=propuestas].po-guided .po-context{position:static}}
@media(max-width:500px){[data-view=propuestas].po-guided .po-nav{grid-template-columns:repeat(2,minmax(0,1fr))}[data-view=propuestas].po-guided .po-guide-result button{width:100%}}
'''

JS = r'''
(function purchaseGuide(){
 const form=$('form'),page=form.closest('[data-view=propuestas]'),nav=page.querySelector('.po-nav');
 page.classList.add('po-guided');nav.setAttribute('aria-label','Progreso de la propuesta de compra');
 const steps=[
  ['po-selection','Elegir la compra','¿A quién compro y qué artículo necesito?','Elige el proveedor y uno de sus artículos.'],
  ['po-references','Revisar la necesidad','¿Cuánto necesito y en qué datos me apoyo?','Indica cantidad y fecha del pedido. Consulta las referencias y, si lo necesitas, declara un escenario de stock.'],
  ['po-conditions','Negociar condiciones','¿Qué cambia entre las tres condiciones?','Compara los importes. Editar una hipótesis no significa que el proveedor la haya aceptado.'],
  ['po-payments','Organizar los pagos','¿Cuánto pagaré y cuándo?','Revisa entrega, portes y vencimientos. Si repartes la deuda, comprueba cada cuota.'],
  ['po-save','Guardar y estudiar opciones','¿Qué resultado tiene esta propuesta?','Guarda para conservar el estudio. Después podrás consultar sus resultados y alternativas.'],
  ['po-guide-agreement','Registrar el acuerdo','¿Qué condiciones hemos acordado y dónde consta?','Declara el acuerdo sobre un estudio guardado e identifica su soporte. No autoriza una compra.']
 ];
 function heading(box,index){const row=document.createElement('div');row.className='po-heading';const number=document.createElement('span');number.textContent=index;const text=document.createElement('div'),h=document.createElement('h2'),p=document.createElement('p');h.textContent=steps[index][1].toUpperCase();p.textContent=steps[index][2];text.append(h,p);row.append(number,text);box.prepend(row);return row}
 const refs=document.createElement('section');refs.id='po-references';refs.className='card po-step';$('po-selection').after(refs);heading(refs,1);
 const aside=page.querySelector('.po-context');for(const detail of Array.from(aside.children))if(detail.tagName==='DETAILS')refs.append(detail);
 const shared=$('po-conditions').querySelector('.po-shared-conditions');if(shared)refs.querySelector('.po-heading').after(shared);
 const assumptions=$('po-stock-assumptions');if(assumptions)refs.append(assumptions);
 const agreement=document.createElement('section');agreement.id='po-guide-agreement';agreement.hidden=true;heading(agreement,5);const content=document.createElement('div');content.id='po-guide-agreement-content';agreement.append(content);$('review-panel').after(agreement);
 const saveFields=document.createElement('div');saveFields.id='po-guide-save-fields';for(const child of Array.from($('po-save').children))if(!child.classList.contains('po-heading'))saveFields.append(child);$('po-save').append(saveFields);
 const live=document.createElement('p');live.id='po-guide-live';live.setAttribute('role','status');live.setAttribute('aria-live','polite');page.querySelector('.po-intro').append(live);
 const analysis=document.createElement('details');analysis.id='po-guide-analysis';const analysisTitle=document.createElement('summary');analysisTitle.textContent='Ver análisis, estado y alternativas del borrador';analysis.append(analysisTitle);$('po-conditions').querySelector('.po-negotiation-scroll').after(analysis);
 const technical=document.createElement('details'),technicalTitle=document.createElement('summary');technicalTitle.textContent='Cómo se comparan los importes y sus referencias';technical.append(technicalTitle);$('po-conditions').append(technical);for(const node of Array.from($('po-conditions').children))if(node.matches('.po-condition-note,#comparison'))technical.append(node);
 const markers=new Map();for(const id of ['po-study-state','po-purchase-summary','po-alternatives-table']){const node=$(id);if(node){const marker=document.createComment('draft location '+id);analysis.append(marker,node);markers.set(node,marker)}}
 let active='po-references',lastMode=document.body.dataset.purchaseMode,report=null,lastField=null,invalidQueued=false;
 const links=new Map(),states=new Map(),results=new Map(),editors=new Map(),snapshots=new Map(),headings=new Map();nav.replaceChildren();
 const nextLabels=['Continuar con este artículo','Revisar las condiciones','Elegir condiciones para los pagos','Ver resumen antes de guardar',null,null];
 for(const [index,step] of steps.entries()){
  const [id,title,,instruction]=step,box=$(id),h=box.querySelector('.po-heading');h.querySelector('span').textContent=index;
  if(index!==2)h.querySelector('h2').textContent=index===1?title:title.toUpperCase();h.querySelector('p').textContent=step[2];
  const help=document.createElement('p');help.className='po-guide-help';help.textContent=instruction;h.after(help);
  const status=document.createElement('span');status.className='po-guide-state';h.querySelector('div').append(status);states.set(id,status);
  const link=document.createElement('a'),caption=document.createElement('strong'),small=document.createElement('small');link.href='#'+id;caption.textContent=title;link.dataset.number=String(index);link.append(caption,small);link.onclick=e=>{e.preventDefault();navigate(id,true)};if(index>0)nav.append(link);links.set(id,link);
  const footer=document.createElement('div');footer.className='po-guide-result';const result=document.createElement('p');footer.append(result);results.set(id,result);
  if(nextLabels[index]){const next=document.createElement('button');next.dataset.guideNext=String(index);next.type='button';next.textContent=nextLabels[index];next.onclick=()=>{if(saved()){navigate(steps[index+1][0],true);return}if(index===1&&(!$('supplier').value||!$('article').value)){openField(!$('supplier').value?$('supplier'):$('article'));return}if(index===2){$('po-option-studies').scrollIntoView({block:'center'});$('po-option-studies').querySelector('button')?.focus();return}if(index===3){try{const rows=declaredPaymentRows();if(rows&&(!rows.length||rows.length>20))throw Error('Este calendario necesita entre 1 y 20 cuotas. Genera las cuotas o desmarca su declaración.')}catch(error){$('payment-split-notice').textContent=error.message;$('payment-split-notice').setAttribute('role','alert');$('payment-split-generate').focus();return}}const invalid=invalidFields(box)[0];if(invalid){openField(invalid);invalid.reportValidity();return}navigate(steps[index+1][0],true)};footer.append(next)}
  if(index<4){
   const editable=document.createElement('div');editable.className='po-guide-editable';
   for(const child of Array.from(box.children))if(child!==h&&child!==help)editable.append(child);
   box.append(editable);editors.set(id,editable);headings.set(id,h.querySelector('h2').textContent);
   const snapshot=document.createElement('section');snapshot.className='po-guide-snapshot';snapshot.id=id+'-saved';snapshot.hidden=true;box.append(snapshot);snapshots.set(id,snapshot);
  }
  box.append(footer);
 }
 function saved(){return document.body.dataset.purchaseMode==='saved'}
 function invalidFields(box){return Array.from(box.querySelectorAll('input,select,textarea')).filter(n=>n.willValidate&&!n.validity.valid)}
 function setStatus(id,kind,text){const badge=states.get(id);badge.dataset.status=kind;badge.textContent=({complete:'✓ ',attention:'! ',current:'● ',pending:'○ '}[kind]||'')+text;links.get(id).dataset.progress=kind;links.get(id).querySelector('small').textContent=id==='po-selection'&&kind==='complete'?$('article').value:text}
 function update(){
  const historical=saved(),mode=historical?'saved':'draft';
  for(const error of form.querySelectorAll('.po-guide-error')){const field=$(error.dataset.field);if(!field||!field.willValidate||field.validity.valid){error.textContent='';field?.removeAttribute('aria-invalid')}}
  if(!historical)$('po-conditions').querySelector('.po-heading p').textContent=steps[2][2];
  if(mode!==lastMode){lastMode=mode;for(const [node,marker] of markers){if(historical)$('po-save').querySelector('.po-guide-result').before(node);else marker.after(node)}if(!historical){report=null;content.replaceChildren();analysis.open=false;active='po-references'}else active='po-save'}
  for(const [id] of steps){const box=$(id),isActive=id===active;box.hidden=id==='po-selection'||!isActive;links.get(id).setAttribute('aria-current',isActive?'step':'false');links.get(id).removeAttribute('aria-disabled')}
  for(const [index,[id]] of steps.entries())if(index<4){
   editors.get(id).hidden=historical;snapshots.get(id).hidden=!historical;
   const heading=$(id).querySelector('.po-heading');heading.querySelector('h2').textContent=historical?['PROVEEDOR Y ARTÍCULO GUARDADOS','NECESIDAD Y REFERENCIAS GUARDADAS','CONDICIONES GUARDADAS','PAGOS Y ENTREGA GUARDADOS'][index]:headings.get(id);
   $(id).querySelector('.po-guide-help').textContent=historical?'Consulta los datos conservados en este estudio. Para cambiarlos, crea un borrador o vuelve a tu formulario.':steps[index][3];
   $(id).querySelector('[data-guide-next]').textContent=historical?'Consultar el siguiente paso':nextLabels[index];
  }
  saveFields.hidden=historical;analysis.hidden=historical;
  if(historical){$('po-save').hidden=active!=='po-save';$('review-panel').hidden=active!=='po-save'}else $('review-panel').hidden=true;
  const picked=!!($('supplier').value&&$('article').value),quantity=form.elements.quantity.value.trim(),date=form.elements.order_date.value.trim();
  const complete=[picked,!!(picked&&quantity&&date&&!invalidFields(refs).length),!!commercialQuote&&!!window.purchaseChoiceIsCurrent?.(),!!commercialQuote&&!!window.purchaseChoiceIsCurrent?.()&&!invalidFields($('po-payments')).length,historical,report?.purchase_agreement?.status==='DECLARED_UNVERIFIED'];
  for(const [index,[id]] of steps.entries()){
   if(historical&&index<4){setStatus(id,id===active?'current':'complete','Consulta · solo lectura');continue}
   const bad=!historical&&invalidFields($(id)).length>0,kind=complete[index]?'complete':id===active?'current':'pending';
   if(index===1&&!historical&&$('po-stock-enabled')?.checked&&!$('po-stock-ack').checked){setStatus(id,'attention','Confirma los supuestos');continue}
   setStatus(id,lastField&&$(id).contains(lastField)&&bad?'attention':kind,complete[index]?(index===4?'Estudio guardado':index===5?'Acuerdo registrado':historical?'Referencia del borrador':'Datos disponibles'):id===active?'En curso':'Pendiente');
  }
  if(!historical&&picked)links.get('po-selection').querySelector('small').textContent=$('article').value;
  if(!historical&&complete[1])links.get('po-references').querySelector('small').textContent='✓ '+quantity+' · '+date;
  results.get('po-selection').textContent=picked?'Proveedor y artículo elegidos. Puedes revisar la cantidad.':'Selecciona proveedor y artículo para identificar la compra.';
  results.get('po-references').textContent=complete[1]?'Cantidad y fecha introducidas. Los supuestos de stock son una hipótesis que debes revisar.':'Completa cantidad y fecha. No se supone que el inventario histórico siga intacto.';
  results.get('po-conditions').textContent=commercialQuote?'Importes calculados según las condiciones introducidas. Revisa los pagos antes de guardar.':'Completa las condiciones y consulta los mensajes de cálculo. No se ha guardado ningún estudio.';
  results.get('po-payments').textContent='Continuar no confirma las cuotas. El guardado comprobará importes, fechas y coherencia del calendario.';
  results.get('po-save').textContent=historical?'Resultado conservado. Para cambiar sus condiciones, crea un borrador desde este estudio.':'Guardar conserva y abre el estudio; no confirma un pedido ni autoriza la compra.';
  results.get('po-guide-agreement').textContent=report?.purchase_agreement?.status==='DECLARED_UNVERIFIED'?'Acuerdo registrado por el usuario. EIOS conserva la declaración; no verifica automáticamente la aceptación del proveedor.':'Primero guarda y revisa las condiciones que correspondan al acuerdo.';
  if(historical)for(const [id] of steps.slice(0,4))results.get(id).textContent='Estudio '+(report?.proposal?.reference||'guardado')+' · Datos conservados. Consultar no modifica el estudio ni tu borrador.';
  live.textContent=(historical?'ESTUDIO GUARDADO · ':'BORRADOR · ')+steps.findIndex(s=>s[0]===active)+' de 5 · '+steps.find(s=>s[0]===active)[1]+(historical?' · Consulta de resultados conservados.':' · Los cambios no se guardan automáticamente.');
 }
 function navigate(id,focus=false){if(id==='po-selection')id='po-references';if(!steps.some(s=>s[0]===id))return;active=id;update();if(focus){const box=$(id);box.tabIndex=-1;box.focus({preventScroll:true});box.scrollIntoView({block:'start',behavior:'instant'})}}
 window.purchaseGuideNavigate=navigate;
 $('po-draft-ribbons').querySelector('.po-ribbon-meta button').onclick=()=>{navigate('po-references',true);for(const detail of refs.querySelectorAll(':scope>details,.po-need-inputs>details'))if(detail!==assumptions)detail.open=true};
 function validationText(field){const v=field.validity;return v.valueMissing?(field.type==='checkbox'?'Marca esta confirmación para continuar.':'Completa este campo.'):v.rangeUnderflow?'Introduce un valor igual o superior a '+field.min+'.':v.rangeOverflow?'Introduce un valor igual o inferior a '+field.max+'.':v.customError?field.validationMessage:'Revisa el valor y el formato de este campo.'}
 function showError(field){if(!field.id)field.id='po-guide-field-'+Array.from(form.elements).indexOf(field);const id=field.id+'-guide-error';let error=$(id);if(!error){error=document.createElement('small');error.id=id;error.className='po-guide-error';error.dataset.field=field.id;field.closest('label')?.append(error);const described=field.getAttribute('aria-describedby')||'';field.setAttribute('aria-describedby',(described+' '+id).trim())}error.textContent=validationText(field);field.setAttribute('aria-invalid','true')}
 function openField(field){if(saved())return;if($('po-selection').contains(field)){navigate('po-references');const picker=$('po-draft-ribbons').querySelector(field.id==='supplier'||field.id==='supplier-code'?'.po-ribbon-supplier-picker:not([data-field])':'[data-field=description]');picker?.focus();picker?.scrollIntoView({block:'center'});return;}for(let parent=field.parentElement;parent&&parent!==page;parent=parent.parentElement)if(parent.tagName==='DETAILS')parent.open=true;const step=steps.find(([id])=>$(id).contains(field));if(step)navigate(step[0]);field.focus({preventScroll:true});field.scrollIntoView({block:'center'})}
 window.purchaseGuideOpenField=openField;
 form.addEventListener('invalid',event=>{event.preventDefault();showError(event.target);if(invalidQueued)return;invalidQueued=true;queueMicrotask(()=>{invalidQueued=false;const field=invalidFields(form)[0];if(field){lastField=field;openField(field)}})},true);
 for(const type of ['input','change','purchasechoice'])form.addEventListener(type,event=>{lastField=event.target;const error=$(event.target.id+'-guide-error');if(error&&event.target.validity){error.textContent=event.target.validity.valid?'':validationText(event.target);event.target.setAttribute('aria-invalid',event.target.validity.valid?'false':'true')}update()});
 form.addEventListener('reset',()=>queueMicrotask(()=>{lastField=null;active='po-references';update()}));
 $('dataset').addEventListener('change',()=>{lastField=null;active='po-references';report=null;content.replaceChildren();update()});
 new MutationObserver(update).observe(document.body,{attributes:true,attributeFilter:['data-purchase-mode']});
 for(const id of ['summary','proposal-cost-summary'])new MutationObserver(update).observe($(id),{childList:true,subtree:true,characterData:true});
 const oldFinance=renderFinancialContext;renderFinancialContext=function(value){oldFinance(value);report=value;renderSavedSteps(value.proposal);const explain=$('po-saved-ribbons')?.querySelector('.po-ribbon-meta button');if(explain)explain.onclick=()=>{navigate('po-save');const target=$('review-documentary-context');for(let parent=target.parentElement;parent&&parent!==page;parent=parent.parentElement)if(parent.tagName==='DETAILS')parent.open=true;target.scrollIntoView({block:'center'})};const box=$('po-agreement');if(box){content.replaceChildren(box);box.open=true}update();navigate('po-save')};

 function renderSavedSteps(proposal){
  const p=proposal||{},terms=p.commercial_terms||{},inventory=p.stock_context_at_save?.inventory,planning=p.stock_planning_at_save,unit=p.unit||'',currency=p.currency||'EUR';
  const known=value=>value!==null&&value!==undefined&&value!=='';
  const text=value=>known(value)?String(value):'No conservado en este estudio';
  const amount=value=>known(value)?money(value)+' '+currency:'No conservado en este estudio';
  const dated=value=>known(value)?stockDate(value):'No conservada en este estudio';
  const count=value=>known(value)?stockNumber(value)+' '+unit:'No conservado en este estudio';
  const shipping=value=>({SUPPLIER:'A cargo del proveedor',INCLUDED:'Incluidos',NONE:'Sin portes declarados',BUYER:'A cargo del comprador',PENDING:'Pendientes de confirmar'}[value]||text(value));
  function facts(parent,rows){const list=document.createElement('dl');list.className='po-guide-facts';for(const [label,value] of rows){const item=document.createElement('div'),dt=document.createElement('dt'),dd=document.createElement('dd');dt.textContent=label;dd.textContent=value;item.append(dt,dd);list.append(item)}parent.append(list)}
  for(const box of snapshots.values())box.replaceChildren();
  const supplier=p.supplier_commercial_at_save||{};
  facts(snapshots.get('po-selection'),[['Referencia del estudio',text(p.reference)],['Código del proveedor',text(p.supplier_id)],['Razón social guardada',text(supplier.legal_name)],['Contacto guardado',text(supplier.contact_name)],['SKU',text(p.article_id)],['Descripción guardada',text(p.article_description_at_save)],['Unidad',text(p.unit)]]);
  const reference=p.price_reference_at_save||{};
  facts(snapshots.get('po-references'),[['Cantidad estudiada',count(p.quantity)],['Fecha del pedido',dated(p.order_date)],['Inventario de referencia al',dated(inventory?.as_of_date)],['Stock físico de referencia',count(inventory?.physical)],['Reservado de referencia',count(inventory?.reserved)],['Disponible de referencia',count(inventory?.available)],['Precio neto de referencia guardado',amount(reference.unit_price)],['Fecha de la referencia de precio',dated(reference.issue_date)],['Mínimo de stock guardado',count(p.stock_context_at_save?.minimum?.value)]]);
  if(planning?.assumptions){const a=planning.assumptions;facts(snapshots.get('po-references'),[['Supuestos de stock','Hipótesis conservadas, sin verificar'],['Consumo supuesto por día',count(a.daily_demand)],['Plazo de recepción supuesto',text(a.lead_time_days)+' días'],['Cobertura objetivo supuesta',text(a.target_days)+' días'],['Stock de seguridad supuesto',count(a.safety_stock)],['Cantidad calculada para ese escenario',count(planning.scenario_quantity)],['Responsable de los supuestos',text(a.actor)],['Referencia de los supuestos',text(a.source_reference)]]);}else{const note=document.createElement('p');note.textContent='Este estudio no conserva un escenario de stock declarado. No se reconstruye con los datos actuales.';snapshots.get('po-references').append(note)}
  function quote(parent,label,q){const title=document.createElement('h3');title.textContent=label;parent.append(title);const t=q.commercial_terms||{},discount=t.discount_mode==='NONE'?'Sin descuento adicional':known(t.discount_value)?stockNumber(t.discount_value)+(t.discount_mode==='PERCENT'?' %':' '+currency+' sobre la línea'):'No conservado en este estudio';facts(parent,[['Coste de adquisición declarado',amount(t.entered_unit_price)],['Descuento declarado',discount],['Coste neto unitario',amount(q.unit_price)],['Base de mercancía',amount(q.net)],['IVA de mercancía',amount(q.tax)],['Tipo de IVA',known(q.vat_percent)?stockNumber(q.vat_percent)+' %':'No conservado en este estudio'],['Total mercancía con IVA',amount(q.total)],['Portes',shipping(t.shipping?.mode)],['Total portes con IVA',amount(t.shipping?.total)],['Total de la operación con IVA y portes',amount(q.operation_total)],['Vencimiento de mercancía',dated(q.due_date)]]);}
  quote(snapshots.get('po-conditions'),'Condiciones de este estudio',p);
  for(const variant of p.negotiation_at_save?.alternatives||[]){const detail=document.createElement('details'),title=document.createElement('summary');title.textContent=variant.label+' · Condiciones conservadas';detail.append(title);quote(detail,variant.label,variant.quote||{});facts(detail,[['Origen declarado',({HYPOTHETICAL:'Hipótesis para negociar',DOCUMENTED:'Condición documentada, sin verificar',UNCONFIRMED:'Sin confirmar'}[variant.condition?.origin]||'No conservado')],['Referencia del soporte',text(variant.condition?.source_reference)]]);snapshots.get('po-conditions').append(detail)}
  const pay=snapshots.get('po-payments');facts(pay,[['Fecha del pedido',dated(p.order_date)],['Lugar de entrega',text(p.delivery_location)],['Vencimiento de mercancía',dated(p.due_date)],['Portes',shipping(terms.shipping?.mode)],['Vencimiento propio de portes',dated(terms.shipping?.due_date)],['Quién factura los portes',({SUPPLIER:'Proveedor',CARRIER:'Transportista'}[terms.shipping?.billed_by]||'No consta un facturador separado')]]);
  const installments=p.payment_plan?.installments||[];
  if(installments.length){const scroll=document.createElement('div');scroll.className='scroll';const table=document.createElement('table'),head=document.createElement('thead'),row=document.createElement('tr');for(const label of ['Cuota','Concepto','Importe con IVA','Vencimiento']){const th=document.createElement('th');th.textContent=label;th.scope='col';row.append(th)}head.append(row);table.append(head);const body=document.createElement('tbody');for(const installment of installments){const row=document.createElement('tr');for(const value of [text(installment.sequence),({MERCHANDISE:'Mercancía',FREIGHT:'Portes'}[installment.component]||text(installment.component)),amount(installment.amount),dated(installment.due_date)]){const cell=document.createElement('td');cell.textContent=value;row.append(cell)}body.append(row)}table.append(body);scroll.append(table);pay.append(scroll);}else{const note=document.createElement('p');note.textContent='Sin reparto de cuotas conservado. Consulta el vencimiento declarado; no se genera otro calendario.';pay.append(note)}
  const supplierDetails=document.createElement('details'),supplierTitle=document.createElement('summary');supplierTitle.textContent='Proveedor y artículo del estudio guardado';supplierDetails.append(supplierTitle,...Array.from(snapshots.get('po-selection').children));snapshots.get('po-references').prepend(supplierDetails);
  for(const [id,box] of snapshots){const notice=document.createElement('p');notice.setAttribute('role','status');const actions=document.createElement('div');actions.className='po-guide-saved-actions';for(const [label,sourceId] of [['Crear borrador desde este estudio','po-create-study-draft'],['Volver a mi formulario','po-return-draft']]){const button=document.createElement('button');button.type='button';button.textContent=label;button.onclick=async()=>{if(!saved()||report?.proposal?.proposal_id!==p.proposal_id)return;const source=$(sourceId);if(!source||source.disabled||typeof source.onclick!=='function')return;button.disabled=true;notice.textContent=sourceId==='po-return-draft'?'Volviendo a tu formulario…':'Preparando el borrador…';try{await source.onclick();if(sourceId==='po-return-draft')navigate(id,true);else if(saved())notice.textContent=$('po-draft-copy-notice')?.textContent||'No se ha aplicado la copia. Revisa el estudio.'}catch(error){notice.textContent=error.message}finally{button.disabled=false}};actions.append(button)}box.append(actions,notice)}
 }
 const backToStudy=document.createElement('button');backToStudy.id='po-guide-back-to-study';backToStudy.type='button';backToStudy.textContent='Volver al estudio y comparar alternativas';backToStudy.onclick=()=>{navigate('po-save',true);if(saved())$('po-alternatives-table').scrollIntoView({block:'start'})};$('po-guide-agreement').querySelector('.po-guide-result').append(backToStudy);
 const toAgreement=document.createElement('button');toAgreement.type='button';toAgreement.id='po-guide-to-agreement';toAgreement.textContent='Ir al registro del acuerdo';toAgreement.onclick=()=>navigate('po-guide-agreement',true);$('po-save').querySelector('.po-guide-result').append(toAgreement);
 const placeholder=document.createElement('p');placeholder.textContent='Guarda y abre un estudio para registrar una declaración vinculada a sus condiciones y cuotas.';content.append(placeholder);
 update();
})();
'''

CSS += "[data-view=propuestas] #po-selection{display:none!important}[data-view=propuestas].po-guided .po-nav{grid-template-columns:repeat(5,minmax(0,1fr))}@media(max-width:900px){[data-view=propuestas].po-guided .po-nav{grid-template-columns:repeat(3,minmax(0,1fr))}}@media(max-width:500px){[data-view=propuestas].po-guided .po-nav{grid-template-columns:repeat(2,minmax(0,1fr))}}"
