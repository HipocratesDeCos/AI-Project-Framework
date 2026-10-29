"""Search the active company's customer list without changing the sales proposal."""

HTML = '''<div class="files-subpanel"><label>Buscar cliente por código o razón social<input id="so-customer-query" type="search" autocomplete="off" placeholder="Escribe varias palabras para afinar"></label><p id="so-customer-count" role="status"></p><button id="so-customer-search-clear" type="button">Limpiar búsqueda de clientes</button></div>'''

JS = r'''
function resetSalesCustomerSearch(){$('so-customer-query').value='';$('so-customer').value='';renderSalesCustomerOptions()}
function renderSalesCustomerOptions(){
 const query=$('so-customer-query'),select=$('so-customer'),clear=$('so-customer-search-clear'),current=state?.info?.dataset_id===$('dataset').value;
 query.disabled=select.disabled=clear.disabled=!current;if(!current){$('so-customer-count').textContent='Actualizando los clientes de la empresa seleccionada…';return}
 const selected=select.value,customers=state.customers||[],normalize=value=>String(value??'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase('es'),terms=normalize(query.value.trim()).split(/\s+/).filter(Boolean),matches=customers.filter(customer=>{const text=normalize(customer.customer_id+' '+(customer.legal_name||''));return terms.every(term=>text.includes(term))}).sort((a,b)=>String(a.legal_name||a.customer_id).localeCompare(String(b.legal_name||b.customer_id),'es',{numeric:true,sensitivity:'base'})||a.customer_id.localeCompare(b.customer_id,'es')),visible=matches.slice(0,200),customer=customers.find(item=>item.customer_id===selected),retained=customer&&!visible.some(item=>item.customer_id===selected);
 select.replaceChildren();option(select,'','Selecciona un cliente');visible.forEach(item=>option(select,item.customer_id,item.customer_id+' · '+(item.legal_name||item.customer_id)));if(retained){const group=document.createElement('optgroup');group.label='Cliente ya seleccionado · conservado fuera de estos resultados';option(group,customer.customer_id,customer.customer_id+' · '+(customer.legal_name||customer.customer_id));select.append(group)}select.value=customer?selected:'';
 if(selected&&!customer){invalidateSalesProposal();Array.from($('so-lines').children).forEach(row=>{row.soRequest=(row.soRequest||0)+1;row.soLoading=false;salesLineField(row,'unit_price').value='';row.soHint?.replaceChildren()});syncSalesProposalActions()}
 $('so-customer-count').textContent=stockNumber(matches.length)+' de '+stockNumber(customers.length)+' clientes · mostrando '+stockNumber(visible.length)+'.'+(matches.length>200?' Afina la búsqueda para ver los demás resultados.':'')+(retained?' El cliente elegido se conserva aparte de los resultados visibles.':'')+(!matches.length?' No hay coincidencias; limpia o cambia la búsqueda.':'');clear.disabled=!query.value;
}
for(const name of ['input','change'])$('so-customer-query').addEventListener(name,event=>{event.stopPropagation();renderSalesCustomerOptions()});
$('so-customer-query').addEventListener('keydown',event=>{if(event.key==='Enter'){event.preventDefault();event.stopPropagation()}});
$('so-customer-search-clear').onclick=()=>{$('so-customer-query').value='';renderSalesCustomerOptions();$('so-customer-query').focus()};
$('so-customer').addEventListener('change',renderSalesCustomerOptions);
'''
