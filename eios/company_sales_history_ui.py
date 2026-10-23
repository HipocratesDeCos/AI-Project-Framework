"""Shared source-backed display of historical sales terms; never reapplies them."""
CSS='''
.sales-history-article{min-width:12rem;max-width:24rem;white-space:normal;overflow-wrap:anywhere}
.sales-history-article small{display:block;color:#506075;margin-top:.3rem}
.sales-history-conditions{min-width:15rem;max-width:28rem;white-space:normal;overflow-wrap:anywhere}
.sales-history-conditions summary{cursor:pointer;font-weight:600;color:#164a8a;padding:.4rem 0}
.sales-history-conditions dl{display:grid;grid-template-columns:minmax(8rem,1fr) minmax(7rem,1fr);gap:.4rem .7rem;margin:.7rem 0}
.sales-history-conditions dt{color:#506075;font-size:.85rem}
.sales-history-conditions dd{margin:0;font-weight:600;font-variant-numeric:tabular-nums}
.sales-history-conditions p{font-size:.85rem;line-height:1.45;margin:.6rem 0}
.sales-history-conditions .sales-history-origin{border-top:1px solid #d8e2ef;padding-top:.6rem;color:#506075}
'''
JS=r'''
function historicalSalesValue(value,suffix){return value===null||value===undefined||value===''?'No aportado':money(value)+suffix}
function historicalSalesConditions(item){
 const details=document.createElement('details');details.className='sales-history-conditions';
 const summary=document.createElement('summary');summary.textContent='Ver condiciones y origen';details.append(summary);
 const terms=document.createElement('dl');
 const fields=[['Precio unitario antes de descuento, sin IVA',historicalSalesValue(item.unit_price_before_discount,' EUR')],['Descuento de línea (%)',historicalSalesValue(item.discount_percent,' %')],['Descuento total de línea',historicalSalesValue(item.discount_amount,' EUR')],['Neto de línea, sin IVA',historicalSalesValue(item.net_amount,' EUR')],['Tipo de IVA declarado',historicalSalesValue(item.vat_percent,' %')],['IVA documentado de línea',historicalSalesValue(item.vat_amount,' EUR')]];
 fields.forEach(([label,value])=>{const dt=document.createElement('dt'),dd=document.createElement('dd');dt.textContent=label;dd.textContent=value;terms.append(dt,dd)});details.append(terms);
 const note=document.createElement('p');note.textContent='El precio neto ya incorpora el descuento. El porcentaje y el importe describen el mismo descuento; no se suman ni se aplican de nuevo. El IVA no se incorpora al precio neto de negociación.';details.append(note);
 const refs=Array.isArray(item.source_refs)?item.source_refs:[];
 refs.forEach(source=>{const p=document.createElement('p');p.className='sales-history-origin';p.textContent=[source.filename||source.document_ref||'Fuente sin nombre',source.sheet?'Hoja '+source.sheet:null,source.row!==null&&source.row!==undefined?'Fila '+source.row:null,source.page!==null&&source.page!==undefined?'Página '+source.page:null].filter(Boolean).join(' · ');details.append(p)});
 if(!refs.length){const p=document.createElement('p');p.className='sales-history-origin';p.textContent='Origen no aportado.';details.append(p)}
 return details;
}
'''
