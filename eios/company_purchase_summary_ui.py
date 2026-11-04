"""Plain-language purchase synthesis from the server snapshot."""
CSS='''
.po-purchase-summary{margin:16px 0;padding:18px;border:1px solid #bfd2ed;border-radius:8px;background:#f1f6ff;color:#142e52}.po-purchase-summary h3{font-size:17px!important;margin:0 0 12px}.po-purchase-summary p,.po-purchase-summary li{font-size:14px;line-height:1.5}.po-purchase-summary .verdict{border-left:5px solid #6483ac;padding:8px 12px;background:#e4edfc}.po-purchase-summary[data-status="SHORTFALL"] .verdict{border-color:#b32828;background:#fff0ef}.po-purchase-summary[data-status="WITHIN_DECLARED_SCENARIO"] .verdict{border-color:#238545;background:#eaf8ee}.po-purchase-summary dl{display:flex;flex-wrap:wrap;gap:12px}.po-purchase-summary dl div{flex:1;min-width:145px}.po-purchase-summary dd{margin:6px 0;font-size:20px;font-weight:bold}.po-purchase-summary dt{font-size:13px}.po-purchase-summary summary{font-size:14px;font-weight:bold}
'''
JS=r'''
(function(){
 const live=document.createElement('section');live.id='po-purchase-summary';$('po-alternatives-table').before(live);
 function paragraph(box,text){const p=document.createElement('p');p.textContent=text;box.append(p)}
 function render(box,r,saved){box.replaceChildren();box.className='po-purchase-summary';const h=document.createElement('h3');h.textContent=saved?'SÍNTESIS DE LA COMPRA GUARDADA':'SÍNTESIS DE LA COMPRA';box.append(h);const s=r?.purchase_summary;
 if(!s){box.dataset.status='PENDING';paragraph(box,saved?'Este estudio anterior no conserva una síntesis. Consulta sus resultados guardados; no se reconstruye con datos actuales.':r?.message||'Recalculando con las condiciones actuales…');return}
 box.dataset.status=s.status;const verdict=document.createElement('p');verdict.className='verdict';const strong=document.createElement('strong');strong.textContent=s.title;verdict.append(strong);box.append(verdict);paragraph(box,s.explanation);
 const metrics=document.createElement('dl');for(const f of s.facts){const item=document.createElement('div'),label=document.createElement('dt'),value=document.createElement('dd');label.textContent=f.label;value.textContent=money(f.value)+' EUR';item.append(label,value);metrics.append(item)}box.append(metrics);
 paragraph(box,'Stock: '+s.stock.message+' '+s.stock.limitation);
 if(s.sensitivity){const stress=s.sensitivity;paragraph(box,'Prueba sin el cobro '+stress.flow_id+' ('+money(stress.amount)+' EUR · '+stockDate(stress.due_date)+'): '+(stress.reserve_respected?'se mantiene la reserva prevista.':'faltan '+money(stress.deficit)+' EUR para la reserva.')+' Es una hipótesis, no una previsión de impago.')}
 const next=document.createElement('p'),label=document.createElement('strong');label.textContent=saved?'SIGUIENTE ACCIÓN AL GUARDAR: ':'SIGUIENTE ACCIÓN: ';next.append(label,document.createTextNode(s.next_action));box.append(next);
 const details=document.createElement('details'),title=document.createElement('summary');title.textContent='Alternativas, comprobaciones pendientes y fuentes';details.append(title);
 for(const a of s.alternatives){paragraph(details,(a.reference||'Alternativa')+' · '+a.title+' · '+stockNumber(a.quantity)+' '+a.unit+' · Total '+money(a.total)+' EUR · Diferencia de desembolso frente a la activa: '+money(-Number(a.savings))+' EUR. '+(a.same_quantity?'Mantiene la cantidad.':'Cambia la cantidad: la diferencia no es solo una mejora de precio.')+' Aceptación del proveedor sin confirmar.');paragraph(details,a.basis)}
 if(!s.alternatives.length)paragraph(details,s.status==='PENDING'?'Las alternativas requieren completar la simulación.':'No se han conservado alternativas comprobadas en este estudio.');
 const list=document.createElement('ul');for(const text of s.pending){const li=document.createElement('li');li.textContent=text;list.append(li)}details.append(list);
 for(const text of s.stock.missing||[])paragraph(details,text.message);
 paragraph(details,'Fuentes de los importes: cálculo comercial, escenario de tesorería y reserva activada. Stock: '+s.stock.source+'.');paragraph(details,'Versión documental: '+(s.references.documentary_context_fingerprint||'Sin referencia')+' · Fuente financiera: '+(s.references.financial_source_fingerprint||'Sin referencia')+' · Huella del estudio: '+(r.analysis_fingerprint||'Sin huella'));box.append(details);paragraph(box,s.scope);
 }
 window.renderPurchaseSummary=(box,r,editable)=>{if(editable)render(live,r,false);else{const section=document.createElement('section');render(section,r,true);box.append(section)}};
 window.clearPurchaseSummary=()=>render(live,{message:'Recalculando con las condiciones actuales…'},false);
})();
'''
