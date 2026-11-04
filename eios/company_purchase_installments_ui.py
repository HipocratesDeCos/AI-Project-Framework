"""Payment schedule generator; retains the existing component-aware payment contract."""
CSS = '''
.po-payment-head,.po-payment-row,.po-payment-footer{display:grid;grid-template-columns:minmax(150px,.8fr) minmax(150px,1fr) minmax(180px,1fr) 42px;gap:12px;align-items:center;padding:12px;min-width:590px}
.po-payment-head,.po-payment-footer{background:#e5efff;font-weight:bold}.po-payment-row{border-bottom:1px solid #c7d8ef}#payment-plan-rows .po-payment-row input,#payment-plan-rows .po-payment-row select{font-size:18px;margin:0;height:42px;box-sizing:border-box}.po-payment-scroll{overflow-x:auto}
.po-payment-number{display:flex;align-items:center;gap:12px}.po-payment-number strong{font-size:130%;min-width:22px}.po-payment-number select{flex:1;min-width:0}
.po-payment-row .po-payment-delete{display:flex;align-items:center;justify-content:center;width:38px;height:42px;padding:8px;margin:0;background:#fff0f0;color:#b42318;border:1px solid #efb2ad;border-radius:5px}.po-payment-delete:hover{background:#ffe0df}.po-payment-delete:focus-visible{outline:2px solid #b42318}
.po-payment-date{position:relative;display:block}.po-payment-date>input:first-child{width:100%;padding-right:40px}.po-payment-date .po-payment-calendar{position:absolute;right:2px;top:2px;display:flex;align-items:center;justify-content:center;width:36px;height:38px;padding:6px;margin:0;background:transparent;color:#173e76;border:0}#payment-plan-rows .po-payment-date .po-payment-native{position:absolute;right:0;top:0;width:1px;height:1px;opacity:0;pointer-events:none}.po-payment-footer output{font-size:18px}
'''
JS = r'''
(()=>{
 const editor=$('payment-plan-editor'),rows=$('payment-plan-rows');
 $('proposal-payment-plan').open=true;
 const controls=document.createElement('div');controls.className='files-step';
 controls.innerHTML='<div class="fields"><label>Repartir la deuda por<select id="payment-split-mode"><option value="COUNT">Número de cuotas</option><option value="AMOUNT">Importe de cada cuota</option></select></label><label><span id="payment-split-label">Número de cuotas</span><input id="payment-split-value" type="number" min="1" max="20" step="1" value="3"></label></div><button type="button" id="payment-split-generate">Generar tabla de cuotas</button><p id="payment-split-notice" role="status"></p><small>Importes con IVA. Revisa los vencimientos antes de guardar. Generar sustituye el calendario actual. Si existen portes separados, se conserva su desglose y su acreedor; no se consideran deuda del proveedor los portes facturados por el transportista.</small>';
 editor.prepend(controls);
 const head=document.createElement('div');head.className='po-payment-head';head.innerHTML='<span>Número de cuota</span><span>Importe (IVA incluido)</span><span>Fecha de vencimiento</span><span aria-label="Acciones"></span>';rows.before(head);editor.classList.add('po-payment-scroll');
 const footer=document.createElement('div');footer.className='po-payment-footer';footer.innerHTML='<strong>Total con IVA</strong><output id="payment-plan-total" aria-live="polite">0,00 euros</output><span></span><span></span>';rows.after(footer);
 function updateTotal(){const amounts=Array.from(rows.querySelectorAll('[data-payment-field="amount"]'));let sum=0;const valid=amounts.every(field=>{const value=Number(field.value);if(!field.value||!Number.isFinite(value)||value<=0||Math.abs(value*100-Math.round(value*100))>0.00001||!Number.isSafeInteger(Math.round(value*100)))return false;sum+=Math.round(value*100);return Number.isSafeInteger(sum)});$('payment-plan-total').textContent=valid?money(sum/100)+' euros':'Pendiente: revisa los importes';}
 rows.addEventListener('input',updateTotal);rows.addEventListener('change',updateTotal);
 const oldAdd=addPaymentRow;
 function layout(){Array.from(rows.children).forEach((row,index)=>{
  if(row.dataset.tableRow){row.querySelector('[data-payment-sequence]').textContent=String(index+1);return}
  row.dataset.tableRow='true';row.className='po-payment-row';
  const component=row.querySelector('[data-payment-field="component"]'),amount=row.querySelector('[data-payment-field="amount"]'),date=row.querySelector('[data-payment-field="due_date"]'),remove=row.querySelector('button');
  const number=document.createElement('div'),sequence=document.createElement('strong');sequence.dataset.paymentSequence='';sequence.textContent=String(index+1);number.className='po-payment-number';number.append(sequence,component);
  remove.className='po-payment-delete';remove.textContent='';remove.title='Eliminar cuota';remove.setAttribute('aria-label','Eliminar cuota');remove.innerHTML='<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M3 6h18M9 6V3h6v3M5 6l1 15h12l1-15M10 10v7M14 10v7"/></svg>';
  amount.setAttribute('aria-label','Importe de la cuota');date.setAttribute('aria-label','Fecha de vencimiento');date.setAttribute('data-eios-date','');
  const dateWrap=document.createElement('span');dateWrap.className='po-payment-date';
  const picker=document.createElement('input');picker.type='date';picker.className='po-payment-native';picker.tabIndex=-1;picker.setAttribute('aria-label','Seleccionar vencimiento');
  const calendar=document.createElement('button');calendar.type='button';calendar.className='po-payment-calendar';calendar.setAttribute('aria-label','Abrir calendario de vencimiento');calendar.title='Elegir fecha';calendar.innerHTML='<svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M16 3v4M8 3v4M3 11h18"/></svg>';
  calendar.onclick=()=>{if(date.disabled)return;try{picker.value=inputDateISO(date.value)||''}catch{picker.value=''}if(picker.showPicker){try{picker.showPicker();return}catch{}}picker.focus();picker.click()};picker.onchange=()=>{if(!picker.value)return;date.value=stockDate(picker.value);date.dispatchEvent(new Event('input',{bubbles:true}));date.dispatchEvent(new Event('change',{bubbles:true}))};
  dateWrap.append(date,picker,calendar);row.replaceChildren(number,amount,dateWrap,remove);
 });updateTotal();}
 addPaymentRow=function(){oldAdd();layout()};$('payment-plan-add').onclick=addPaymentRow;
 new MutationObserver(layout).observe(rows,{childList:true});layout();
 const mode=$('payment-split-mode'),value=$('payment-split-value'),notice=$('payment-split-notice');
 mode.onchange=()=>{const count=mode.value==='COUNT';$('payment-split-label').textContent=count?'Número de cuotas':'Importe de cada cuota (euros, IVA incluido)';value.min=count?'1':'0.01';value.step=count?'1':'0.01';value.max=count?'20':'1000000000000000000';value.value='';notice.textContent='';};
 function cents(raw){const n=Number(raw);if(!Number.isFinite(n)||n<0||!Number.isSafeInteger(Math.round(n*100)))throw Error('El importe está fuera del rango admitido.');return Math.round(n*100)}
 $('payment-split-generate').onclick=()=>{try{
  const quote=commercialQuote;if(!quote||quote.operation_total===null)throw Error('Completa precio, cantidad, IVA y portes y espera al cálculo del total.');
  const total=cents(quote.operation_total),merch=cents(quote.total),freight=total-merch;
  if(total<=0||freight<0)throw Error('La deuda debe ser positiva y estar calculada.');
  const raw=Number(value.value),count=mode.value==='COUNT';if(!value.value||!Number.isFinite(raw)||raw<=0||(count&&!Number.isInteger(raw))||(!count&&Math.abs(raw*100-Math.round(raw*100))>0.00001))throw Error('Indica un número entero de cuotas o un importe positivo con un máximo de dos decimales.');
  const fixed=count?0:cents(raw),n=count?raw:Math.ceil(total/fixed);if(n<1||n>20||n>total)throw Error('El calendario admite entre 1 y 20 cuotas de importe positivo.');
  const allocations=[];let remaining=total,remainingMerch=merch;
  for(let i=0;i<n;i++){const amount=count?Math.floor(total/n)+(i===n-1?total%n:0):Math.min(fixed,remaining);const m=i===n-1?remainingMerch:Math.max(0,amount-(remaining-remainingMerch),Math.min(amount,remainingMerch,Math.round(amount*merch/total)));const f=amount-m;allocations.push({m,f});remaining-=amount;remainingMerch-=m;}
  const records=allocations.flatMap((a,i)=>[['MERCHANDISE',a.m],['FREIGHT',a.f]].filter(x=>x[1]>0).map(([component,amount])=>({component,amount,index:i})));
  if(records.length>20)throw Error('El desglose de mercancía y portes supera las 20 líneas admitidas. Reduce el número de cuotas.');
  rows.replaceChildren();for(const item of records){addPaymentRow();const row=rows.lastElementChild;row.querySelector('[data-payment-field="component"]').value=item.component;row.querySelector('[data-payment-field="amount"]').value=(item.amount/100).toFixed(2);row.querySelector('[data-payment-field="due_date"]').value=item.index===n-1?$('form').elements[item.component==='MERCHANDISE'?'due_date':'shipping_due_date'].value:'';}
  updateTotal();
  notice.textContent='Total distribuido: '+money(total/100)+' euros · '+n+' cuotas'+(freight?' con desglose de mercancía y portes':'')+'. Completa y revisa cada vencimiento. La última fecha de cada concepto debe coincidir con su vencimiento acordado.';
  $('form').dispatchEvent(new Event('change',{bubbles:true}));
 }catch(error){notice.textContent=error.message}};
})();
'''
