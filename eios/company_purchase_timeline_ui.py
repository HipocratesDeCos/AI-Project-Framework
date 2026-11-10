"""Accessible, centered timeline for the existing synthetic purchase preview and saved comparisons."""
CSS = """
.eios-timeline{margin:18px 0;padding:18px;border:1px solid #b7cee8;border-radius:14px;background:#f0f6ff;color:#17314f}
.eios-timeline *{box-sizing:border-box}.eios-timeline h3,.eios-timeline p{text-align:center;margin:6px 0}
.eios-timeline .etl-lead{font-size:13px;color:#426080}
.eios-timeline .etl-scroll{display:flex;overflow-x:auto;gap:9px;padding:14px 2px;scroll-snap-type:x proximity}
.eios-timeline .etl-day{min-width:112px;flex:1;border:1px solid #bad0e7;background:white;border-radius:9px;padding:12px 8px;text-align:center;scroll-snap-align:center;cursor:pointer;color:#17436b}
.eios-timeline .etl-day[aria-pressed=true]{outline:3px solid #3476c8;outline-offset:1px;background:#e3efff}
.eios-timeline .etl-day b{display:block;font-size:14px}.eios-timeline .etl-day small{display:block;font-size:11px}
.eios-timeline .etl-day .etl-dot{width:9px;height:9px;border-radius:50%;display:block;background:#6185ab;margin:5px auto}
.eios-timeline .etl-day.etl-risk .etl-dot{background:#b42318}.eios-timeline .etl-day.etl-buy .etl-dot{background:#2358b3}
.eios-timeline .etl-result{border:1px solid #bfd1e6;border-radius:10px;background:#fff;padding:16px;margin-top:8px}
.eios-timeline .etl-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
.eios-timeline .etl-metric{border-radius:8px;background:#f4f8fd;padding:13px 8px;text-align:center}
.eios-timeline .etl-metric small{display:block;font-size:12px;color:#46617d}.eios-timeline .etl-metric strong{font-size:30px;font-variant-numeric:tabular-nums;overflow-wrap:anywhere}
.eios-timeline .etl-description{text-align:center;line-height:1.45;margin:12px 0}
.eios-timeline .etl-movements{padding-left:0;list-style:none;margin:12px auto;max-width:720px}
.eios-timeline .etl-movements li{text-align:center;border-top:1px solid #dce6f2;padding:9px}
.eios-timeline .etl-source{display:inline-block;border-bottom:1px dotted #69819c;cursor:help;font-size:12px;color:#426080}
.eios-timeline .etl-source:focus{outline:2px solid #3476c8}
.eios-timeline .etl-warning{color:#9c321e;font-weight:700;text-align:center}
@media(max-width:700px){.eios-timeline .etl-grid{grid-template-columns:1fr}.eios-timeline .etl-metric strong{font-size:30px}}
"""
JS = r"""
function renderPurchaseTimeline(host,result){
  const prior=host.querySelector('.eios-timeline');if(prior)prior.remove();
  const data=result&&result.timeline;if(!data||!Array.isArray(data.rows)||!data.rows.length)return;
  const root=document.createElement('section');root.className='eios-timeline';root.setAttribute('aria-label','Línea de tiempo financiera de la propuesta');
  const head=document.createElement('h3');head.textContent='LÍNEA DE TIEMPO FINANCIERA';
  const timing=result&&result.timing_assessment;
  const timingCard=document.createElement('section');timingCard.className='etl-result';timingCard.setAttribute('aria-label','Conclusión de vencimiento');
  if(timing){
    timingCard.append(elemTimelineHeading());
    function elemTimelineHeading(){const e=document.createElement('h3');e.textContent=timing.status==='NEGOTIATE_DEFERMENT'?'FECHA PROPUESTA PARA NEGOCIAR':timing.status==='KEEP_DECLARED_DATES'?'MANTENER VENCIMIENTO DECLARADO':timing.status==='SEARCH_NOT_REQUESTED'?'BÚSQUEDA DE FECHAS NO REALIZADA':'NO SE HA ENCONTRADO FECHA ADECUADA';return e}
    const dateLine=document.createElement('p');dateLine.className='etl-description';dateLine.textContent=timing.suggested_last_due_date?'Último vencimiento: '+timing.suggested_last_due_date.split('-').reverse().join('/'):'No hay nueva fecha';
    const reason=document.createElement('p');reason.className='etl-description';reason.textContent=timing.reason;
    const provenance=document.createElement('span');provenance.className='etl-source';provenance.textContent='Calculado desde previsión declarada';provenance.title='Se utilizan los flujos y parámetros financieros activos, sin confirmar cobros o aceptación de condiciones.';provenance.tabIndex=0;
    timingCard.append(dateLine,reason,provenance);
  }

  const lead=document.createElement('p');lead.className='etl-lead';lead.textContent='Cobros y pagos del archivo activo, más el pago hipotético de esta compra · Cifras al cierre de cada día';
  const scroller=document.createElement('div');scroller.className='etl-scroll';scroller.setAttribute('role','group');scroller.setAttribute('aria-label','Fechas con movimientos');
  const details=document.createElement('div');details.className='etl-result';details.setAttribute('aria-live','polite');
  const dateFmt=d=>{const x=String(d).split('-');return x.length===3?x[2]+'/'+x[1]+'/'+x[0]:d};
  const euros=n=>new Intl.NumberFormat('es-ES',{style:'currency',currency:'EUR'}).format(Number(n));
  const prov={DECLARED_FORECAST:'Movimiento de la previsión del libro activo. No acredita un cobro o pago efectivo.',HYPOTHETICAL_PURCHASE:'Pago hipotético de la propuesta de compra. No consta aceptado ni realizado.'};
  const kind={COLLECTION:'Cobro previsto',PAYMENT:'Pago previsto',PURCHASE_PAYMENT:'Pago de esta propuesta'};
  function elem(tag,cl,value){const e=document.createElement(tag);if(cl)e.className=cl;if(value!==undefined)e.textContent=value;return e}
  function metric(label,value){const e=elem('div','etl-metric');e.append(elem('small','',label),elem('strong','',euros(value)));return e}
  const buttons=[];
  function select(idx){
    const row=data.rows[idx];
    buttons.forEach((b,i)=>b.setAttribute('aria-pressed',i===idx?'true':'false'));
    details.replaceChildren(elem('h3','',dateFmt(row.date)));
    const grid=elem('div','etl-grid');
    for(const [label,value] of [['Saldo anterior',row.balance_before],['Cobros previstos',row.collections],['Pagos previstos',row.payments],['Saldo al cierre',row.balance_after]])grid.append(metric(label,value));
    details.append(grid);
    let explanation=Number(row.collections)-Number(row.payments);
    details.append(elem('p','etl-description',(explanation<0?'El dinero disponible disminuye ':explanation>0?'El dinero disponible aumenta ':'El saldo se mantiene ')+
      (explanation===0?'en esta fecha.':'en '+euros(Math.abs(explanation))+'.')+
      ' Se calcula compensando los movimientos del día; no confirma disponibilidad dentro de la jornada.'));
    if(row.below_minimum)details.append(elem('p','etl-warning','El saldo de cierre queda por debajo del mínimo financiero activado.'));
    const list=elem('ul','etl-movements');
    for(const mov of row.movements){
      const li=elem('li','');
      li.append(elem('strong','',kind[mov.kind]||'Movimiento'),document.createTextNode(' · '+euros(mov.amount)+' · '+mov.reference+' · '));
      const source=elem('span','etl-source',mov.origin==='HYPOTHETICAL_PURCHASE'?'Hipótesis':'Previsión del libro');
      source.title=prov[mov.origin]||'Origen sin identificar';source.tabIndex=0;source.setAttribute('aria-label',source.textContent+': '+source.title);
      li.append(source);list.append(li);
    }
    details.append(list);
  }
  for(const [i,row] of data.rows.entries()){
    const b=elem('button','etl-day'+(row.below_minimum?' etl-risk':'')+(row.movements.some(x=>x.kind==='PURCHASE_PAYMENT')?' etl-buy':''));b.type='button';
    b.append(elem('b','',dateFmt(row.date)),elem('span','etl-dot'),elem('small','',row.movements.length+' mov.'),elem('small','',euros(row.balance_after)));
    b.onclick=()=>select(i);buttons.push(b);scroller.append(b);
  }
  root.append(head,lead);if(timing)root.append(timingCard);root.append(scroller,details,elem('p','etl-lead','Escenario orientativo ficticio. No acredita conciliación, aceptación del proveedor ni autoridad de compra.'));
  host.append(root);select(data.rows.findIndex(x=>x.below_minimum)>=0?data.rows.findIndex(x=>x.below_minimum):data.rows.length-1);
}
// Integrate without replacing existing risk assessment, options or save behavior.
const renderPurchaseCashBeforeTimeline=renderPurchaseCash;
renderPurchaseCash=function(box,result,editable){
  renderPurchaseCashBeforeTimeline(box,result,editable);
  renderPurchaseTimeline(box,result);
};
"""
