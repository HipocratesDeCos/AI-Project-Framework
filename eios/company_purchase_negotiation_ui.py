"""Three-column negotiation while entering conditions; authoritative quote endpoint."""
CSS = '''
#po-conditions .po-heading{margin-bottom:14px}
.po-shared-conditions{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;padding:12px;background:#edf4ff;border:1px solid #c4d6ee;border-radius:8px;margin-bottom:14px}
.po-shared-conditions label{margin:0!important;font-size:12px!important}
.po-draft-column details{font-size:12px}
.po-draft-column summary{font-size:12px}
@media(max-width:760px){.po-shared-conditions{grid-template-columns:1fr}}
[data-view=propuestas] #po-cash .po-cash-grid{grid-template-columns:repeat(2,minmax(0,1fr))}
[data-view=propuestas] #po-cash .po-cash-grid strong{font-size:16px}
[data-view=propuestas] #po-cash .po-cash-grid>div{padding:9px}
.po-draft-negotiation{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;align-items:stretch}
.po-draft-column{min-width:0;border:1px solid #bfd2ed;border-radius:10px;background:#f7faff;display:flex;flex-direction:column;padding:14px}
.po-draft-column h3{font-size:14px;margin:0 0 6px!important;color:#132e57}
.po-draft-column>p{font-size:12px;line-height:1.5;min-height:36px;margin:0 0 14px;color:#4b6380}
.po-draft-column .po-subsection{border:0;background:transparent;padding:0;margin:0}
.po-draft-column .po-subsection>h3{display:none}
.po-draft-column .fields{grid-template-columns:1fr!important;gap:0}
.po-draft-column label{font-size:12px!important;margin-bottom:10px!important}
.po-draft-column input:not([type=checkbox]),.po-draft-column select{min-height:36px!important;padding:7px!important;font-size:13px!important}
.po-draft-column small{font-size:11px!important}
.po-draft-column .po-column-fields{flex:1}
.po-column-total{margin-top:14px;padding:12px;border:1px solid #9bbbea;border-radius:7px;background:#e1edff;font-size:11px;color:#28496d}
.po-column-total strong{display:block;font-size:23px;color:#102a50;margin-top:5px;font-variant-numeric:tabular-nums;overflow-wrap:anywhere}
.po-column-total small{display:block;margin:5px 0 0!important;line-height:1.5}
.po-workspace .po-draft-column label.po-check{display:flex;flex-direction:row;gap:8px;align-items:center;min-height:28px}
.po-draft-column .po-check input{width:16px;min-width:16px;height:16px}
.po-draft-column .po-net{font-size:12px;min-height:22px;color:#214d7d;margin:8px 0}
#po-conditions>.po-discount-help{margin-top:14px}
#po-conditions #po-totals{grid-template-columns:repeat(2,minmax(0,1fr))}
.po-treasury-chart{margin:10px 0 16px;background:white;border:1px solid #c3d5ee;border-radius:8px;padding:10px}
.po-treasury-chart svg{display:block;width:100%;height:auto;overflow:visible}
.po-treasury-chart figcaption{font-size:11px;line-height:1.5;color:#49617b}
.po-treasury-chart .chart-legend{display:flex;gap:12px;flex-wrap:wrap;font-size:11px;margin:6px 0}
.po-treasury-chart .chart-legend span:first-child{color:#165ce1}.po-treasury-chart .chart-legend span:last-child{color:#22804d}
.po-condition-note{font-size:12px;color:#49617b;line-height:1.5}
@media(min-width:1101px){[data-view=propuestas]:has(#po-conditions:not([hidden])) .po-workspace{grid-template-columns:minmax(0,1fr) minmax(280px,.32fr)}}
@media(max-width:1250px){.po-draft-negotiation{grid-template-columns:1fr}.po-draft-column>p{min-height:0}}
'''
JS = r'''
function renderPurchaseTreasuryChart(box,r){
 const points=r.scenario?.points;if(!points?.length)return;
 const figure=document.createElement('figure');figure.className='po-treasury-chart';figure.style.marginLeft='0';figure.style.marginRight='0';
 const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');svg.setAttribute('viewBox','0 0 420 235');svg.setAttribute('role','img');svg.setAttribute('aria-label','Tesorería prevista de la oferta original al cierre de cada fecha y reserva mínima');
 function node(tag,attrs,text){const n=document.createElementNS(svg.namespaceURI,tag);for(const [k,v] of Object.entries(attrs))n.setAttribute(k,v);if(text!==undefined)n.textContent=text;svg.append(n);return n}
 const minimum=Number(r.treasury_minimum),balances=points.map(p=>Number(p.balance));let low=Math.min(0,minimum,...balances),high=Math.max(minimum,...balances);const pad=Math.max((high-low)*.1,1);low-=pad;high+=pad;
 const start=Date.parse(r.cutoff),end=Date.parse(r.horizon_end),x=d=>62+((Date.parse(d)-start)/Math.max(1,end-start))*344,y=v=>180-(v-low)/(high-low)*160;
 for(let i=0;i<4;i++){const value=low+(high-low)*i/3,at=y(value);node('line',{x1:62,x2:406,y1:at,y2:at,stroke:'#e0e8f2'});node('text',{x:56,y:at+3,'text-anchor':'end',fill:'#506680','font-size':9},new Intl.NumberFormat('es-ES',{maximumFractionDigits:0}).format(value))}
 node('line',{x1:62,x2:406,y1:y(minimum),y2:y(minimum),stroke:'#22804d','stroke-width':1.5,'stroke-dasharray':'5 4'});
 // Step path: closing balances do not imply a linear cash movement between dates.
 let path='M '+x(points[0].date)+' '+y(balances[0]);for(let i=1;i<points.length;i++)path+=' H '+x(points[i].date)+' V '+y(balances[i]);
 node('path',{d:path,fill:'none',stroke:'#165ce1','stroke-width':2.5});for(const p of points){const circle=node('circle',{cx:x(p.date),cy:y(Number(p.balance)),r:2.8,fill:'#165ce1'});const title=document.createElementNS(svg.namespaceURI,'title');title.textContent=stockDate(p.date)+': '+money(p.balance)+' euros';circle.append(title)}
 node('text',{x:62,y:202,fill:'#506680','font-size':10},stockDate(r.cutoff));node('text',{x:406,y:202,'text-anchor':'end',fill:'#506680','font-size':10},stockDate(r.horizon_end));node('text',{x:62,y:14,fill:'#506680','font-size':10},'Saldo previsto · euros');
 const legend=document.createElement('div');legend.className='chart-legend';for(const text of ['━ Oferta original','┄ Reserva mínima: '+money(r.treasury_minimum)+' euros']){const span=document.createElement('span');span.textContent=text;legend.append(span)}const caption=document.createElement('figcaption');caption.textContent='Oferta original · Saldos al cierre del día según el escenario declarado. No incluye las alternativas todavía sin comparar.';figure.append(svg,legend,caption);box.append(figure);
}
let purchaseNegotiationDraft=()=>[];
(function conditionsNegotiation(){
 const form=$('form'),conditions=$('po-conditions'),grid=document.createElement('div');grid.id='po-draft-negotiation';grid.className='po-draft-negotiation';
 const heading=conditions.querySelector('.po-heading');heading.querySelector('h2').textContent='NEGOCIAR CONDICIONES DE COMPRA';heading.querySelector('p').textContent='Prepara y compara los importes de la misma cantidad. La oferta original se conserva al guardar.';
 const original=document.createElement('section');original.className='po-draft-column';original.setAttribute('aria-label','Oferta original');original.innerHTML='<h3>OFERTA ORIGINAL</h3><p>Introduce las condiciones recibidas. Se conservarán al guardar.</p>';
 const originalFields=document.createElement('div');originalFields.className='po-column-fields';original.append(originalFields);
 const sharedControls=Object.fromEntries(['quantity','vat_percent','order_date'].map(name=>[name,form.elements[name]]));const pricing=form.elements.pricing_mode.closest('label'),priceGroup=conditions.querySelector('.po-subsection');originalFields.append(pricing,priceGroup);
 originalFields.append(form.elements.due_date.closest('label'));const shared=document.createElement('div');shared.className='po-shared-conditions';for(const name of ['quantity','vat_percent','order_date'])shared.append(sharedControls[name].closest('label'));heading.after(shared);for(const small of Array.from(priceGroup.querySelectorAll('small'))){const details=document.createElement('details'),summary=document.createElement('summary');summary.textContent='Cómo se aplica el descuento';details.append(summary,small);originalFields.append(details)}
 const originalNet=document.createElement('p');originalNet.className='po-net';originalFields.append(originalNet);
 const totals=[];function total(column){const box=document.createElement('div');box.className='po-column-total';const label=document.createElement('span'),value=document.createElement('strong'),detail=document.createElement('small');label.textContent='TOTAL CON IVA Y PORTES';value.textContent='Pendiente';box.append(label,value,detail);column.append(box);const result={box,value,detail};totals.push(result);return result}const originalTotal=total(original);grid.append(original);shared.after(grid);
 const fields={};let identity=null,sequence=0,timer;
 function column(slot,title,help,originDefault){const area=document.createElement('section');area.className='po-draft-column';area.setAttribute('aria-label',title);const h=document.createElement('h3'),p=document.createElement('p');h.textContent=title;p.textContent=help;area.append(h,p);const body=document.createElement('div');body.className='po-column-fields';area.append(body);const enabled=document.createElement('input');enabled.type='checkbox';const label=document.createElement('label');label.className='po-check';label.append(enabled,document.createTextNode(slot==='mine'?'Preparar mi propuesta':'Añadir respuesta recibida'));body.append(label);const controls={enabled};
 function field(key,title,options){const l=document.createElement('label'),i=document.createElement(options?'select':'input');l.textContent=title;i.id='po-neg-'+slot+'-'+key;if(options){for(const [value,text] of options){const o=document.createElement('option');o.value=value;o.textContent=text;i.append(o)}}else{i.type=key==='due_date'?'date':['unit_price','discount_value'].includes(key)?'number':'text';if(i.type==='number'){i.min='0';i.step='any'}if(i.type==='text')i.maxLength=256}l.append(i);body.append(l);controls[key]=i;i.disabled=true;return i}
 field('pricing_mode','Modo de precio',[['BEFORE_DISCOUNT','Precio antes de descuentos'],['NET','Precio neto ya negociado']]);field('unit_price','Precio por unidad (euros sin IVA)');field('discount_mode','Modalidad de descuento',[['NONE','Sin descuento'],['PERCENT','Porcentaje'],['LINE_AMOUNT','Euros sobre la línea']]);field('discount_value','Descuento');field('due_date','Vencimiento de mercancía');field('origin','Origen de las condiciones',[['HYPOTHETICAL','Hipótesis para negociar'],['UNCONFIRMED','Sin confirmar'],['DOCUMENTED','Oferta documentada, sin verificar']]).value=originDefault;field('source_reference','Referencia del soporte');const provenance=document.createElement('details'),provenanceTitle=document.createElement('summary');provenanceTitle.textContent='Origen y soporte de la condición';provenance.append(provenanceTitle,controls.origin.closest('label'),controls.source_reference.closest('label'));body.append(provenance);
 const net=document.createElement('p');net.className='po-net';body.append(net);controls.net=net;controls.total=total(area);const shared=document.createElement('small');shared.textContent='Misma cantidad, IVA y portes que la oferta original. Calendario de cuotas: revisar después de guardar.';body.append(shared);fields[slot]=controls;grid.append(area);
 enabled.addEventListener('change',()=>{for(const key of ['unit_price','pricing_mode','discount_mode','discount_value','due_date','origin','source_reference'])controls[key].disabled=!enabled.checked;if(enabled.checked){controls.pricing_mode.value='BEFORE_DISCOUNT';controls.discount_mode.value='NONE';controls.discount_value.value='';controls.unit_price.value='';try{controls.due_date.value=inputDateISO(form.elements.due_date.value)||''}catch{controls.due_date.value=''}}sync(controls);schedule()});
 for(const key of ['pricing_mode','discount_mode'])controls[key].addEventListener('change',()=>{if(key==='pricing_mode'&&controls.pricing_mode.value==='NET'){controls.discount_mode.value='NONE';controls.discount_value.value='';}sync(controls)});
 }
 function sync(f){const active=f.enabled.checked,before=f.pricing_mode.value==='BEFORE_DISCOUNT';f.discount_mode.disabled=!active||!before;f.discount_value.disabled=!active||!before||f.discount_mode.value==='NONE';if(f.discount_value.disabled)f.discount_value.value='';}
 column('mine','MI PROPUESTA','Editable · Hipótesis para negociar.','HYPOTHETICAL');column('response','RESPUESTA DEL PROVEEDOR','Editable · Condición recibida, sin aceptación verificada.','UNCONFIRMED');
 const breakdown=document.createElement('details'),summary=document.createElement('summary');summary.textContent='Detalle de importes, impuestos y redondeos de la oferta original';breakdown.append(summary,$('po-totals'),$('proposal-cost-summary'));grid.after(breakdown);breakdown.after($('po-cash-alert'),$('comparison'));
 const note=document.createElement('p');note.className='po-condition-note';note.textContent='Los totales se calculan con el motor comercial de EIOS. Si faltan fechas, IVA o portes, se muestran pendientes. Guardar conserva las tres columnas; no acepta una oferta ni ejecuta la compra.';grid.after(note);
 function values(f){return {unit_price:f.unit_price.value,pricing_mode:f.pricing_mode.value,discount_mode:f.pricing_mode.value==='NET'?'NONE':f.discount_mode.value,discount_value:f.discount_value.disabled?null:f.discount_value.value,due_date:f.due_date.value}}
 purchaseNegotiationDraft=()=>Object.entries(fields).filter(([k,f])=>f.enabled.checked).map(([slot,f])=>({slot,patch:values(f),condition:{origin:f.origin.value,source_reference:f.source_reference.value.trim()||null,acceptance:'PENDING'}}));
 function show(total,net,quote){if(!quote){total.value.textContent='Pendiente';net.textContent='Precio neto: pendiente';total.detail.textContent='Completa precio, fechas, IVA y portes.';return}total.value.textContent=quote.operation_total==null?'Portes pendientes':money(quote.operation_total)+' euros';net.textContent='Precio neto por unidad: '+money(quote.unit_price)+' euros';total.detail.textContent='Mercancía neta '+money(quote.net)+' · IVA '+money(quote.tax)+' · Portes con IVA '+money(quote.commercial_terms.shipping.total)+' euros';}
 function resetColumns(){for(const f of Object.values(fields)){f.enabled.checked=false;for(const key of ['unit_price','discount_value','due_date','source_reference'])f[key].value='';for(const key of ['unit_price','pricing_mode','discount_mode','discount_value','due_date','origin','source_reference'])f[key].disabled=true;}}
 function schedule(){const current=[ $('dataset').value,$('supplier').value,$('article').value].join('|');if(identity!==null&&current!==identity)resetColumns();identity=current;const seq=++sequence;clearTimeout(timer);show(originalTotal,originalNet,commercialQuote);for(const f of Object.values(fields)){show(f.total,f.net,null);if(!f.enabled.checked)f.total.detail.textContent='Sin alternativa declarada.'}timer=setTimeout(async()=>{const base=Object.fromEntries(new FormData(form));await Promise.all(Object.entries(fields).filter(([k,f])=>f.enabled.checked).map(async([slot,f])=>{try{const quote=await api('/api/purchases/quote',{method:'POST',headers:{'Content-Type':'application/json','X-EIOS-Token':token},body:JSON.stringify({...base,...values(f)})});if(seq!==sequence)return;show(f.total,f.net,quote)}catch(error){if(seq===sequence)f.total.detail.textContent=error.message}}))},250)}
 form.addEventListener('input',schedule);form.addEventListener('change',schedule);form.addEventListener('reset',()=>{resetColumns();queueMicrotask(schedule)});$('dataset').addEventListener('change',()=>{resetColumns();schedule()});new MutationObserver(schedule).observe($('proposal-cost-summary'),{childList:true,subtree:true,characterData:true});schedule();
})();
'''
