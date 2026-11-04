"""Payment schedule generator; retains the existing component-aware payment contract."""
CSS = '''
.po-payment-head,.po-payment-row{display:grid;grid-template-columns:minmax(130px,.8fr) minmax(150px,1fr) minmax(180px,1fr);gap:12px;align-items:start;padding:12px}
.po-payment-head{background:#e5efff;font-weight:bold}.po-payment-row{border-bottom:1px solid #c7d8ef}.po-payment-row input,.po-payment-row select{font-size:18px}.po-payment-row small{display:block}.po-payment-scroll{overflow-x:auto}.po-payment-head,.po-payment-row{min-width:530px}
'''
JS = r'''
(()=>{
 const editor=$('payment-plan-editor'),rows=$('payment-plan-rows');
 const controls=document.createElement('div');controls.className='files-step';
 controls.innerHTML='<div class="fields"><label>Repartir la deuda por<select id="payment-split-mode"><option value="COUNT">Número de cuotas</option><option value="AMOUNT">Importe de cada cuota</option></select></label><label><span id="payment-split-label">Número de cuotas</span><input id="payment-split-value" type="number" min="1" max="20" step="1" value="3"></label></div><button type="button" id="payment-split-generate">Generar tabla de cuotas</button><p id="payment-split-notice" role="status"></p><small>Importes con IVA. Revisa los vencimientos antes de guardar. Generar sustituye el calendario actual. Si existen portes separados, se conserva su desglose y su acreedor; no se consideran deuda del proveedor los portes facturados por el transportista.</small>';
 editor.prepend(controls);
 const head=document.createElement('div');head.className='po-payment-head';head.innerHTML='<span>Número de cuota</span><span>Importe (IVA incluido)</span><span>Fecha de vencimiento</span>';rows.before(head);editor.classList.add('po-payment-scroll');
 const oldAdd=addPaymentRow;
 function layout(){Array.from(rows.children).forEach((row,index)=>{
  if(row.dataset.tableRow){row.querySelector('[data-payment-sequence]').textContent=String(index+1);return}
  row.dataset.tableRow='true';row.className='po-payment-row';
  const component=row.querySelector('[data-payment-field="component"]'),amount=row.querySelector('[data-payment-field="amount"]'),date=row.querySelector('[data-payment-field="due_date"]'),remove=row.querySelector('button');
  const number=document.createElement('div'),sequence=document.createElement('strong');sequence.dataset.paymentSequence='';sequence.textContent=String(index+1);number.append(sequence,component,remove);
  amount.setAttribute('aria-label','Importe de la cuota');date.setAttribute('aria-label','Fecha de vencimiento');date.setAttribute('data-eios-date','');
  row.replaceChildren(number,amount,date);
 });}
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
  notice.textContent='Total distribuido: '+money(total/100)+' euros · '+n+' cuotas'+(freight?' con desglose de mercancía y portes':'')+'. Completa y revisa cada vencimiento. La última fecha de cada concepto debe coincidir con su vencimiento acordado.';
  $('form').dispatchEvent(new Event('change',{bubbles:true}));
 }catch(error){notice.textContent=error.message}};
})();
'''
