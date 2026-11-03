"""Three-column negotiation while entering conditions; authoritative quote endpoint."""
CSS = '''
#po-conditions .po-heading{margin-bottom:14px}
.po-shared-conditions{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;padding:12px;background:#edf4ff;border:1px solid #c4d6ee;border-radius:8px;margin-bottom:14px}
.po-shared-conditions label{margin:0!important;font-size:12px!important}
.po-draft-column details{font-size:12px}
.po-draft-column summary{font-size:12px}
@media(max-width:760px){.po-shared-conditions{grid-template-columns:1fr}}
[data-view=propuestas] #po-cash .po-cash-grid{grid-template-columns:repeat(2,minmax(0,1fr))}
[data-view=propuestas] #po-cash .po-cash-grid strong{font-size:16px}
[data-view=propuestas] #po-cash .po-cash-grid>div{padding:9px}
.po-draft-negotiation{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));grid-template-rows:repeat(9,auto);column-gap:12px;row-gap:0;align-items:stretch}
.po-draft-column{min-width:0;border:1px solid #bfd2ed;border-radius:10px;background:#f7faff;display:grid;grid-template-rows:subgrid;grid-row:span 9;padding:14px}
.po-draft-column h3{font-size:14px;margin:0 0 6px!important;color:#132e57}
.po-draft-column>p{font-size:12px;line-height:1.5;min-height:36px;margin:0 0 14px;color:#4b6380}
.po-draft-column .po-subsection{border:0;background:transparent;padding:0;margin:0}
.po-draft-column .po-subsection>h3{display:none}
.po-draft-column .fields{grid-template-columns:1fr!important;gap:0}
.po-draft-column label{font-size:12px!important;margin-bottom:6px!important}.po-draft-column header p{font-size:12px;line-height:1.5;color:#49617b;margin:6px 0;min-height:36px}.po-aligned-cell{padding:8px 0;border-top:1px solid #e0e9f6}.po-aligned-cell[data-condition-row=discount] .fields{display:grid;grid-template-columns:1fr!important;gap:0}.po-aligned-cell[data-condition-row=cost] label{min-height:72px}.po-draft-column .po-column-total{padding:12px;margin-top:10px}
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


#po-conditions{font-family:Arial,Helvetica,sans-serif!important}
#po-conditions .po-draft-column *,#po-conditions h2,#po-conditions h3,#po-conditions input,#po-conditions select,#po-conditions button,#po-conditions strong{font-family:inherit!important}
.po-negotiation-scroll{max-width:100%;overflow:auto;border:1px solid #bfd2ed;border-radius:9px;background:#fbfdff}
#po-conditions .po-draft-negotiation{grid-template-columns:minmax(145px,.7fr) repeat(3,minmax(0,1fr));min-width:760px;column-gap:0}
#po-conditions .po-draft-column{border:0;border-right:1px solid #d6e2f2;border-radius:0;background:transparent;padding:8px 12px}
#po-conditions .po-draft-column:last-child{border-right:0}
#po-conditions .po-draft-column>header{background:#edf3fd;padding:8px;border-radius:6px;margin-bottom:4px}
#po-conditions .po-draft-column h3{font-size:15px;font-weight:800;line-height:1.3}
#po-conditions .po-draft-column header p{font-size:12px;min-height:36px}
#po-conditions .po-label-column{background:#f0f5fc}
#po-conditions .po-label-column>header{background:transparent;font-size:14px;font-weight:800;align-content:center}
#po-conditions .po-row-label{display:flex;align-items:center;font-size:16px;font-weight:700;line-height:1.35;color:#142b49}
#po-conditions .po-aligned-cell{min-height:48px;padding:6px 0;align-content:center}
#po-conditions .po-aligned-cell[data-condition-row=cost] label{min-height:0}
#po-conditions .po-draft-column label{margin:0!important}
#po-conditions .po-draft-column input:not([type=checkbox]),#po-conditions .po-draft-column select{font-size:18px!important;font-weight:500;min-height:40px!important;height:40px;padding:6px 9px!important;font-variant-numeric:tabular-nums;background:white}
#po-conditions .po-draft-column .po-net{font-size:18px;font-weight:700;margin:0}
#po-conditions .po-aligned-cell[data-condition-row=discount]{display:flex;gap:6px;align-items:center}
#po-conditions .po-aligned-cell[data-condition-row=discount] .fields{display:flex!important;gap:6px;width:100%}
#po-conditions .po-aligned-cell[data-condition-row=discount] label:first-child{flex:0 0 74px;min-width:0}
#po-conditions .po-aligned-cell[data-condition-row=discount] label:last-child{flex:1;min-width:0}
#po-conditions .po-aligned-cell[data-condition-row=discount] select{font-size:14px!important;padding:6px!important}
#po-conditions .po-column-total{background:#dfebff;border:0;border-radius:5px;margin:0!important;padding:10px!important}
#po-conditions .po-column-total>span{display:none}
#po-conditions .po-column-total strong{font-size:23px;font-weight:800;margin:0}
#po-conditions .po-row-label[data-condition-row=total]{background:#dfebff;border-radius:5px;padding:10px;font-size:16px}
.po-field-caption{position:absolute!important;width:1px;height:1px;padding:0!important;margin:-1px!important;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}
#po-conditions .po-condition-date{position:relative;display:block;width:100%}
#po-conditions .po-condition-date>input{width:100%;padding-right:36px!important}
#po-conditions .po-condition-native{position:absolute;right:0;top:0;width:1px!important;height:1px!important;opacity:0;pointer-events:none}
#po-conditions .po-condition-calendar,#po-conditions .po-calendar-button{position:absolute;right:3px;top:2px;display:flex;align-items:center;justify-content:center;width:32px;height:36px;min-height:0;margin:0!important;padding:0!important;border:0;background:transparent;color:#274b79}
#po-conditions .po-date-field>input{margin-top:0}
#po-conditions .po-condition-calendar:focus-visible{outline:2px solid #2869d2}
#po-conditions .po-condition-calendar:disabled{opacity:.4}
#po-conditions .po-column-details{margin:0;font-size:12px}
@media(max-width:1100px){#po-conditions .po-draft-column{grid-template-rows:subgrid;grid-row:span 9;margin:0}}
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
 const form=$('form'),conditions=$('po-conditions'),heading=conditions.querySelector('.po-heading');
 heading.querySelector('h2').textContent='NEGOCIAR CONDICIONES DE COMPRA';heading.querySelector('p').textContent='Compara la oferta original, tu propuesta y la respuesta recibida, manteniendo la misma cantidad.';
 const original={};for(const name of ['unit_price','pricing_mode','quantity','vat_percent','order_date','due_date','discount_mode','discount_value','shipping_mode','shipping_net','shipping_vat_percent','shipping_billed_by','shipping_due_date'])original[name]=form.elements[name];
 const shared=document.createElement('div');shared.className='po-shared-conditions';shared.append(original.quantity.closest('label'),original.order_date.closest('label'));heading.after(shared);
 const grid=document.createElement('div');grid.id='po-draft-negotiation';grid.className='po-draft-negotiation';const scroll=document.createElement('div');scroll.className='po-negotiation-scroll';scroll.setAttribute('role','region');scroll.setAttribute('aria-label','Tabla de condiciones de compra. Desplaza horizontalmente si es necesario.');scroll.tabIndex=0;shared.after(scroll);scroll.append(grid);
 const fields={};let identity=null,sequence=0,timer;
 function header(area,title,help,enabled,slot){const box=document.createElement('header'),h=document.createElement('h3'),p=document.createElement('p');h.textContent=title;p.textContent=help;box.append(h,p);const label=document.createElement('label');label.className='po-check';if(enabled){label.append(enabled,document.createTextNode(slot==='mine'?'Preparar mi propuesta':'Añadir respuesta recibida'))}else label.textContent='Referencia de la operación';box.append(label);area.append(box)}
 function cell(area,key){const box=document.createElement('div');box.className='po-aligned-cell';box.dataset.conditionRow=key;area.append(box);return box}
 function relabel(control,text){const label=control.closest('label');for(const n of Array.from(label.childNodes))if(n.nodeType===3)n.remove();const span=label.querySelector(':scope>span:not(.po-date-field)');if(span)span.textContent=text;else label.prepend(document.createTextNode(text));return label}
 function total(area){const box=cell(area,'total');box.classList.add('po-column-total');const label=document.createElement('span'),value=document.createElement('strong'),detail=document.createElement('small');label.textContent='TOTAL CON IVA Y PORTES';value.textContent='Pendiente';box.append(label,value,detail);return {value,detail}}
 const area=document.createElement('section');area.className='po-draft-column';area.setAttribute('aria-label','Oferta original');grid.append(area);header(area,'OFERTA ORIGINAL','Condiciones recibidas. Se conservarán al guardar.');
 cell(area,'cost').append(relabel(original.unit_price,'Coste de adquisición (euros/unidad, sin IVA)'));
 const discountCell=cell(area,'discount');discountCell.append($('proposal-discount-fields'));relabel(original.discount_mode,'Descuento');
 const originalNet=cell(area,'net');originalNet.classList.add('po-net');
 cell(area,'shipping').append(relabel(original.shipping_mode,'Portes'));
 cell(area,'due').append(relabel(original.due_date,'Vencimiento de propuesta'));const originalCalendar=original.due_date.closest('label').querySelector('.po-calendar-button');if(originalCalendar)originalCalendar.setAttribute('aria-label','Abrir calendario: Vencimiento de propuesta de OFERTA ORIGINAL');
 cell(area,'vat').append(relabel(original.vat_percent,'IVA de la mercancía (%)'));
 const originalDetails=cell(area,'details'),freightDetails=document.createElement('details'),freightSummary=document.createElement('summary');freightSummary.textContent='Detalle de portes';freightDetails.append(freightSummary,$('proposal-shipping-fields'),$('proposal-shipping-note'));originalDetails.append(freightDetails);const modeLabel=original.pricing_mode.closest('label');modeLabel.hidden=true;originalDetails.append(modeLabel);const originalTotal=total(area);
 // Prices are acquisition amounts before discount; no price-mode selector is shown.
 function initialPricing(){if(original.unit_price.value===''||original.pricing_mode.value==='NET'){original.pricing_mode.value='BEFORE_DISCOUNT';original.discount_mode.value='PERCENT';original.discount_value.value='0'}updateCommercialForm()}
 initialPricing();
 function column(slot,title,help,originDefault){const area=document.createElement('section');area.className='po-draft-column';area.setAttribute('aria-label',title);grid.append(area);const controls={enabled:document.createElement('input')};controls.enabled.type='checkbox';header(area,title,help,controls.enabled,slot);
 function field(box,key,labelText,type='number',options){const label=document.createElement('label'),input=document.createElement(options?'select':'input');label.textContent=labelText;input.id='po-neg-'+slot+'-'+key;if(options){for(const [value,text] of options){const option=document.createElement('option');option.value=value;option.textContent=text;input.append(option)}}else{input.type=type;if(type==='number'){input.min='0';input.step='any'}if(type==='text')input.maxLength=256}input.disabled=true;label.append(input);if(key==='due_date'){input.type='text';input.placeholder='DD/MM/YYYY';input.maxLength=10;const picker=document.createElement('input');picker.type='date';picker.id=input.id+'-picker';picker.className='po-condition-native';picker.tabIndex=-1;picker.setAttribute('aria-hidden','true');const wrap=document.createElement('span'),button=document.createElement('button');wrap.className='po-condition-date';input.before(wrap);wrap.append(input);button.type='button';button.className='po-condition-calendar';button.setAttribute('aria-label','Abrir calendario: Vencimiento de propuesta de '+title);button.innerHTML='<svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M16 3v4M8 3v4M3 11h18M8 15h2M14 15h2M8 18h2"/></svg>';button.disabled=true;button.onclick=()=>{if(input.disabled)return;try{picker.value=inputDateISO(input.value)||''}catch{picker.value=''}if(typeof picker.showPicker==='function'){try{picker.showPicker();return}catch{}}picker.focus();picker.click()};picker.addEventListener('change',()=>{if(!picker.value)return;input.value=stockDate(picker.value);input.dispatchEvent(new Event('change',{bubbles:true}))});wrap.append(picker,button);controls.dueCalendar=button;controls.duePicker=picker}box.append(label);controls[key]=input;return input}
 const cost=cell(area,'cost');field(cost,'unit_price','Coste de adquisición (euros/unidad, sin IVA)');controls.pricing_mode=document.createElement('input');controls.pricing_mode.type='hidden';controls.pricing_mode.value='BEFORE_DISCOUNT';
 const discount=cell(area,'discount');field(discount,'discount_mode','Descuento','select',[['PERCENT','Porcentaje'],['NONE','Sin descuento'],['LINE_AMOUNT','Euros sobre la línea']]);field(discount,'discount_value','Valor del descuento');
 controls.net=cell(area,'net');controls.net.classList.add('po-net');
 field(cell(area,'shipping'),'shipping_mode','Portes','select',[['PENDING','Pendiente de confirmar'],['BUYER','Empresa compradora'],['SUPPLIER','Proveedor'],['INCLUDED','Incluidos en el precio'],['NONE','Sin portes']]);
 field(cell(area,'due'),'due_date','Vencimiento de propuesta','date');field(cell(area,'vat'),'vat_percent','IVA de la mercancía (%)');controls.vat_percent.max='100';
 const extra=cell(area,'details'),freight=document.createElement('details'),fs=document.createElement('summary');fs.textContent='Detalle de portes';freight.append(fs);extra.append(freight);
 field(freight,'shipping_net','Portes netos (euros)');field(freight,'shipping_vat_percent','IVA de portes (%)');controls.shipping_vat_percent.max='100';field(freight,'shipping_billed_by','Quién factura los portes','select',[['','Selecciona…'],['SUPPLIER','Proveedor'],['CARRIER','Transportista']]);field(freight,'shipping_due_date','Vencimiento de portes','date');
 const provenance=document.createElement('details'),summary=document.createElement('summary');summary.textContent='Origen y soporte';provenance.append(summary);field(provenance,'origin','Origen de las condiciones','select',[['HYPOTHETICAL','Hipótesis para negociar'],['UNCONFIRMED','Sin confirmar'],['DOCUMENTED','Oferta documentada, sin verificar']]).value=originDefault;field(provenance,'source_reference','Referencia del soporte','text');extra.append(provenance);
 controls.total=total(area);fields[slot]=controls;
 controls.enabled.addEventListener('change',()=>{if(controls.enabled.checked){for(const key of ['vat_percent','shipping_mode','shipping_net','shipping_vat_percent','shipping_billed_by'])controls[key].value=original[key].value;for(const key of ['due_date','shipping_due_date']){try{const iso=inputDateISO(original[key].value);controls[key].value=iso?(key==='due_date'?stockDate(iso):iso):''}catch{controls[key].value=''}}controls.discount_mode.value='PERCENT';controls.discount_value.value='0';controls.unit_price.value=''}sync(controls);schedule()});for(const key of ['discount_mode','shipping_mode'])controls[key].addEventListener('change',()=>sync(controls));
 }
 function sync(f){for(const [key,input] of Object.entries(f))if(input instanceof HTMLInputElement||input instanceof HTMLSelectElement){if(key==='enabled')continue;input.disabled=!f.enabled.checked}f.discount_value.disabled=!f.enabled.checked||f.discount_mode.value==='NONE';if(f.discount_value.disabled)f.discount_value.value='';for(const key of ['shipping_net','shipping_vat_percent','shipping_billed_by','shipping_due_date'])f[key].disabled=!f.enabled.checked||f.shipping_mode.value!=='BUYER';if(f.dueCalendar)f.dueCalendar.disabled=f.due_date.disabled;}
 column('mine','MI PROPUESTA','Editable. Hipótesis para negociar.','HYPOTHETICAL');column('response','RESPUESTA DEL PROVEEDOR','Condición recibida, sin aceptación verificada.','UNCONFIRMED');

 const labels=document.createElement('section');labels.className='po-draft-column po-label-column';labels.setAttribute('aria-label','Campos de la negociación');const labelHeader=document.createElement('header');labelHeader.textContent='CONDICIONES';labels.append(labelHeader);for(const [key,text] of [['cost','Coste de adquisición'],['discount','Descuento'],['net','Coste neto unitario'],['shipping','Portes'],['due','Vencimiento de propuesta'],['vat','IVA de la mercancía (%)'],['details','Detalle y fuentes'],['total','TOTAL CON IVA Y PORTES']]){const item=cell(labels,key);item.classList.add('po-row-label');item.textContent=text;item.id='po-condition-label-'+key}grid.prepend(labels);
 for(const column of grid.querySelectorAll('.po-draft-column:not(.po-label-column)')){const name=column.getAttribute('aria-label');for(const cell of column.querySelectorAll('.po-aligned-cell')){const key=cell.dataset.conditionRow;cell.setAttribute('aria-labelledby','po-condition-label-'+key);if(['cost','discount','shipping','due','vat'].includes(key)){for(const label of cell.querySelectorAll('label')){for(const node of Array.from(label.childNodes)){if(node.nodeType===3&&node.textContent.trim()){const caption=document.createElement('span');caption.className='po-field-caption';node.before(caption);caption.append(node)}}for(const span of label.querySelectorAll(':scope>span:not(.po-date-field):not(.po-condition-date)'))span.classList.add('po-field-caption')}}}const detailsCell=column.querySelector('[data-condition-row=details]'),fold=document.createElement('details'),title=document.createElement('summary');fold.className='po-column-details';title.textContent='Detalles';fold.append(title,...Array.from(detailsCell.childNodes));detailsCell.append(fold);const detail=column.querySelector('.po-column-total small');if(detail)fold.append(detail)}
 for(const select of [original.discount_mode,fields.mine.discount_mode,fields.response.discount_mode])for(const option of select.options){option.title=option.textContent;option.textContent={PERCENT:'%',NONE:'Sin dto.',LINE_AMOUNT:'€ / línea'}[option.value]||option.textContent}
 const breakdown=document.createElement('details'),summary=document.createElement('summary');summary.textContent='Detalle de importes, impuestos y redondeos';breakdown.append(summary,$('po-totals'),$('proposal-cost-summary'));scroll.after(breakdown);breakdown.after($('po-cash-alert'),$('comparison'));conditions.querySelector('.po-discount-help').hidden=true;
 // Empty legacy containers are removed after moving every original field.
 for(const section of Array.from(conditions.querySelectorAll(':scope>.po-subsection')))if(!section.querySelector('input,select'))section.remove();
 const note=document.createElement('p');note.className='po-condition-note';note.textContent='Coste de adquisición: importe unitario antes del descuento y sin IVA. Los portes se detallan por separado. Las tres columnas se conservan al guardar, sin aceptar una oferta ni ejecutar una compra.';scroll.after(note);
 function values(f){const data={unit_price:f.unit_price.value,pricing_mode:'BEFORE_DISCOUNT',discount_mode:f.discount_mode.value,discount_value:f.discount_value.disabled?null:f.discount_value.value,due_date:f.due_date.value,vat_percent:f.vat_percent.value,shipping_mode:f.shipping_mode.value};for(const key of ['shipping_net','shipping_vat_percent','shipping_billed_by','shipping_due_date'])data[key]=f[key].disabled?null:f[key].value;return data}
 purchaseNegotiationDraft=()=>Object.entries(fields).filter(([k,f])=>f.enabled.checked).map(([slot,f])=>({slot,patch:values(f),condition:{origin:f.origin.value,source_reference:f.source_reference.value.trim()||null,acceptance:'PENDING'}}));
 function show(total,net,quote){if(!quote){total.value.textContent='Pendiente';net.textContent='Pendiente';total.detail.textContent='Completa coste, descuento, fechas, IVA y portes.';return}total.value.textContent=quote.operation_total==null?'Portes pendientes':money(quote.operation_total)+' euros';net.textContent=money(quote.unit_price)+' euros';total.detail.textContent='Mercancía neta '+money(quote.net)+' · IVA '+money(quote.tax)+' · Portes con IVA '+money(quote.commercial_terms.shipping.total)+' euros';}
 function resetColumns(){for(const f of Object.values(fields)){f.enabled.checked=false;for(const key of ['unit_price','discount_value','due_date','source_reference'])f[key].value='';sync(f)}}
 function schedule(){const current=[$('dataset').value,$('supplier').value,$('article').value].join('|');if(identity!==null&&current!==identity)resetColumns();identity=current;const seq=++sequence;clearTimeout(timer);show(originalTotal,originalNet,commercialQuote);for(const f of Object.values(fields)){show(f.total,f.net,null);if(!f.enabled.checked)f.total.detail.textContent='Sin alternativa declarada.'}timer=setTimeout(async()=>{const base=Object.fromEntries(new FormData(form));await Promise.all(Object.values(fields).filter(f=>f.enabled.checked).map(async f=>{try{const quote=await api('/api/purchases/quote',{method:'POST',headers:{'Content-Type':'application/json','X-EIOS-Token':token},body:JSON.stringify({...base,...values(f)})});if(seq===sequence)show(f.total,f.net,quote)}catch(error){if(seq===sequence)f.total.detail.textContent=error.message}}))},250)}
 form.addEventListener('input',schedule);form.addEventListener('change',schedule);form.addEventListener('reset',()=>{resetColumns();queueMicrotask(()=>{initialPricing();schedule()})});$('dataset').addEventListener('change',()=>{resetColumns();schedule()});new MutationObserver(schedule).observe($('proposal-cost-summary'),{childList:true,subtree:true,characterData:true});schedule();
})();
'''
