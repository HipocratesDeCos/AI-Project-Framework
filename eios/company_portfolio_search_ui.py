"""Search and bounded rendering of the active company's commercial portfolios."""


def controls(kind: str) -> str:
    """Return labelled controls for one of the two fixed portfolio views."""
    if kind not in {"supplier", "customer"}:
        raise ValueError("Unknown portfolio")
    label = ("Buscar por código, razón social, contacto o lugar de entrega"
             if kind == "supplier" else "Buscar por código o razón social")
    noun = "proveedores" if kind == "supplier" else "clientes"
    return f'''<div class="files-subpanel"><label>{label}<input id="{kind}-portfolio-query" type="search" autocomplete="off" aria-controls="{'suppliers' if kind == 'supplier' else 'customers'}-table"></label><p id="{kind}-portfolio-count" role="status" aria-live="polite"></p><p id="{kind}-portfolio-empty" hidden></p><div class="files-actions"><button id="{kind}-portfolio-clear" type="button">Limpiar búsqueda</button><button id="{kind}-portfolio-prev" type="button" aria-label="Página anterior de {noun}">Anterior</button><button id="{kind}-portfolio-next" type="button" aria-label="Página siguiente de {noun}">Siguiente</button></div></div>'''


JS = r'''
const portfolioPages={supplier:0,customer:0};
function portfolioText(value){return String(value??'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase('es')}
function resetPortfolioSearch(){
 for(const kind of ['supplier','customer']){portfolioPages[kind]=0;$(kind+'-portfolio-query').value='';$(kind+'-portfolio-query').disabled=true;$(kind+'-portfolio-count').textContent='Actualizando la cartera de la empresa seleccionada…';$(kind+'-portfolio-empty').hidden=true;$(kind+'-portfolio-prev').disabled=true;$(kind+'-portfolio-next').disabled=true;$(kind+'-portfolio-clear').disabled=true}
 $('suppliers-table').replaceChildren();$('customers-table').replaceChildren();
}
function portfolioRows(kind,records){
 const current=state?.info?.dataset_id===$('dataset').value,query=portfolioText($(kind+'-portfolio-query').value.trim()),terms=query.split(/\s+/).filter(Boolean),id=kind==='supplier'?'supplier_id':'customer_id',noun=kind==='supplier'?'proveedores':'clientes';
 const rows=current?records.filter(record=>{const text=portfolioText([record[id],record.legal_name,...(kind==='supplier'?[record.contact_name,record.contact_person,record.delivery_location,record.delivery_address]:[])].join(' '));return terms.every(term=>text.includes(term))}).slice().sort((a,b)=>String(a.legal_name||a[id]).localeCompare(String(b.legal_name||b[id]),'es',{sensitivity:'base',numeric:true})||String(a[id]).localeCompare(String(b[id]),'es',{numeric:true})):[];
 const pages=Math.max(1,Math.ceil(rows.length/50));portfolioPages[kind]=Math.max(0,Math.min(portfolioPages[kind],pages-1));const first=portfolioPages[kind]*50,page=rows.slice(first,first+50);
 $(kind+'-portfolio-count').textContent=current?stockNumber(rows.length)+' de '+stockNumber(records.length)+' '+noun+' · mostrando '+(page.length?stockNumber(first+1)+'–'+stockNumber(first+page.length):'0')+' · página '+stockNumber(portfolioPages[kind]+1)+' de '+stockNumber(pages)+'. Orden: razón social.':'Actualizando la cartera de la empresa seleccionada…';
 $(kind+'-portfolio-empty').hidden=!current||rows.length>0;$(kind+'-portfolio-empty').textContent=records.length?'No hay '+noun+' que coincidan. Limpia la búsqueda para ver toda la cartera.':'No hay '+noun+' en la versión activa de esta empresa.';
 $(kind+'-portfolio-query').disabled=!current;$(kind+'-portfolio-prev').disabled=!current||portfolioPages[kind]===0;$(kind+'-portfolio-next').disabled=!current||portfolioPages[kind]+1>=pages;$(kind+'-portfolio-clear').disabled=!current||!query;
 return page;
}
function closePortfolioDetail(kind){if(kind==='supplier')resetSupplierPurchaseHistory();else{resetCustomerReceivedHistory();$('customer-sales').hidden=true;$('sale-lines').hidden=true}}
for(const kind of ['supplier','customer']){
 const render=()=>{closePortfolioDetail(kind);if(kind==='supplier')supplierPortfolio();else customerPortfolio()};
 $(kind+'-portfolio-query').addEventListener('input',()=>{portfolioPages[kind]=0;render()});
 $(kind+'-portfolio-clear').onclick=()=>{$(kind+'-portfolio-query').value='';portfolioPages[kind]=0;render();$(kind+'-portfolio-query').focus()};
 $(kind+'-portfolio-prev').onclick=()=>{portfolioPages[kind]--;render()};$(kind+'-portfolio-next').onclick=()=>{portfolioPages[kind]++;render()};
}
'''
