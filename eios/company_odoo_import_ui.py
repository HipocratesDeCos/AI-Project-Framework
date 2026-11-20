"""Odoo purchase.order visual preview in the company file workspace.

Client-side display only. Orders, suppliers and products are not written to EIOS.
"""

HTML = '''
<section class="card files-section" id="odoo-purchase-import">
  <h2>ODOO · PEDIDOS DE COMPRA</h2>
  <p>Comprueba una exportación de solicitudes de presupuesto o pedidos de Odoo antes de incorporarla a EIOS.
     Esta pantalla no registra compras ni modifica los datos de la empresa.</p>
  <div class="files-step">
    <h3>1. Selecciona la exportación</h3>
    <p class="files-hint">Utiliza el código y la razón social de empresa indicados en «Identifica la empresa».
       La correspondencia entre empresas todavía no se ha verificado.</p>
    <label class="files-drop">Archivo de Odoo (.xlsx o .csv, máximo 10 MiB)
      <input id="odoo-purchase-file" type="file" accept=".xlsx,.csv">
    </label>
    <button type="button" class="primary" id="odoo-purchase-check">Comprobar pedidos</button>
    <p id="odoo-purchase-status" role="status" aria-live="polite">Selecciona el archivo que has exportado de Odoo.</p>
  </div>
  <div id="odoo-purchase-preview" hidden>
    <div class="odoo-preview-facts" id="odoo-purchase-facts"></div>
    <div class="odoo-preview-metrics" id="odoo-purchase-metrics"></div>
    <p id="odoo-purchase-gate" class="odoo-preview-gate" role="status"></p>
    <div id="odoo-purchase-errors" class="odoo-preview-errors"></div>
    <h3>2. Revisa los pedidos</h3>
    <div class="scroll" id="odoo-purchase-orders"></div>
    <details>
      <summary>Saber más · Líneas, cantidades y precios</summary>
      <div class="scroll" id="odoo-purchase-lines"></div>
    </details>
    <details>
      <summary>Saber más · Avisos y comprobaciones pendientes</summary>
      <div id="odoo-purchase-warnings"></div>
      <p>La coincidencia con las fichas maestras de proveedores y productos de Odoo aún no está verificada.
         Tampoco se han comprobado las unidades, los cambios de documentos ni los duplicados entre importaciones.</p>
    </details>
    <p class="odoo-preview-readonly">Solo vista previa. No hay guardado, admisión documental ni autorización para decisiones.
       Las solicitudes de presupuesto (SdP) no son facturas ni compras confirmadas.</p>
  </div>
</section>
'''

CSS = '''
#odoo-purchase-import .files-hint{font-size:13px;color:#52647a}
.odoo-preview-facts{padding:14px;background:#edf4fc;border:1px solid #c9d9e9;border-radius:7px;margin:16px 0;font-size:13px;overflow-wrap:anywhere}
.odoo-preview-facts p{margin:6px 0}
.odoo-preview-facts code{overflow-wrap:anywhere;font-size:12px}
.odoo-preview-metrics{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin:14px 0}
.odoo-preview-metrics>div{background:#eaf2fd;border:1px solid #c9d9e9;border-radius:7px;padding:14px;min-width:0}
.odoo-preview-metrics span{display:block;font-size:12px;color:#52647a}
.odoo-preview-metrics strong{font-size:22px;font-variant-numeric:tabular-nums;overflow-wrap:anywhere}
.odoo-preview-metrics .odoo-ok{border-left:4px solid #16805d}
.odoo-preview-metrics .odoo-pending{border-left:4px solid #d69b29}
.odoo-preview-metrics .odoo-error{border-left:4px solid #b42318}
.odoo-preview-gate{padding:12px 14px;border-left:4px solid #d69b29;background:#fff8e8;color:#805b0c}
.odoo-preview-errors:not(:empty){padding:12px;border-left:4px solid #b42318;background:#fff0ee;color:#842619}
.odoo-preview-readonly{font-size:13px;color:#805b0c;padding:12px;background:#fff8e8}
#odoo-purchase-import table{min-width:780px}
@media(max-width:700px){.odoo-preview-metrics{grid-template-columns:repeat(2,minmax(0,1fr))}}
'''

JS = r'''
let odooPurchaseRevision=0,odooPurchaseBusy=false;
const odooPurchaseMoney=value=>{
 if(value===null||value===undefined||value==='')return 'Sin dato';
 const n=Number(value);
 return Number.isFinite(n)?new Intl.NumberFormat('es-ES',{minimumFractionDigits:2,maximumFractionDigits:2}).format(n)+' €':String(value);
};
function odooPurchaseReset(){
 odooPurchaseRevision++;
 $('odoo-purchase-preview').hidden=true;
 $('odoo-purchase-facts').replaceChildren();
 $('odoo-purchase-metrics').replaceChildren();
 $('odoo-purchase-errors').replaceChildren();
 $('odoo-purchase-orders').replaceChildren();
 $('odoo-purchase-lines').replaceChildren();
 $('odoo-purchase-warnings').replaceChildren();
 $('odoo-purchase-status').textContent='Archivo pendiente de comprobar. No se ha guardado nada.';
}
['odoo-purchase-file','reception-company-id','reception-company-name'].forEach(id=>$(id).addEventListener('input',odooPurchaseReset));
function odooPurchaseFact(label,value){
 const p=document.createElement('p'),strong=document.createElement('strong');
 strong.textContent=label+': ';
 p.append(strong);
 if(label==='SHA-256'){const code=document.createElement('code');code.textContent=value;p.append(code)}
 else p.append(document.createTextNode(value));
 $('odoo-purchase-facts').append(p);
}
function odooPurchaseMetric(label,value,category){
 const box=document.createElement('div'),span=document.createElement('span'),strong=document.createElement('strong');
 if(category)box.classList.add('odoo-'+category);
 span.textContent=label;strong.textContent=value;box.append(span,strong);
 $('odoo-purchase-metrics').append(box);
}
function odooPurchaseMessages(id,issues){
 const root=$(id);root.replaceChildren();
 if(!issues.length){root.textContent='Sin incidencias de este tipo.';return}
 const list=document.createElement('ul');
 issues.forEach(issue=>{
  const li=document.createElement('li');
  li.textContent=(issue.reference?issue.reference+' · ':'')+(issue.source_row?'Fila '+issue.source_row+': ':'')+(issue.message||issue.code||'Incidencia sin descripción');
  list.append(li);
 });
 root.append(list);
}
function odooPurchaseRender(data,company){
 const summary=data.summary||{},orders=data.orders_preview||[],pending=data.pending_orders||[];
 const all=[...orders.map(o=>({...o,complete:true})),...pending.map(o=>({...o,complete:false}))].sort((a,b)=>String(a.reference).localeCompare(String(b.reference),'es'));
 odooPurchaseFact('Empresa indicada',company||'Sin identificar: completa el paso 1');
 odooPurchaseFact('Archivo',data.filename||'Sin nombre');
 odooPurchaseFact('Perfil','Odoo purchase.order · '+(data.errors.length?'Exportación no reconocida o incorrecta':'v0.2 reconocido'));
 odooPurchaseFact('Fecha de comprobación',data.checked_at||'Sin dato');
 odooPurchaseFact('Fecha de recepción','No recibido (solo lectura)');
 odooPurchaseFact('SHA-256',data.sha256||'Sin huella');
 odooPurchaseMetric('Pedidos con líneas',String(summary.complete_orders||0),'ok');
 odooPurchaseMetric('Pendientes',String(summary.pending_orders||0),'pending');
 odooPurchaseMetric('Errores',String(data.errors.length),'error');
 odooPurchaseMetric('Total revisable, impuestos incluidos',odooPurchaseMoney(summary.total||'0'),'');
 $('odoo-purchase-gate').textContent=data.errors.length?'NO APTO · El archivo contiene errores. Ningún pedido puede utilizarse.':
   pending.length?'REVISIÓN PENDIENTE · Hay pedidos sin líneas. No se guardará una parte del lote automáticamente.':
   'VISTA PREVIA CORRECTA · No hay guardado. Falta verificar los maestros, la identidad y la recepción.';
 odooPurchaseMessages('odoo-purchase-errors',data.errors);
 receptionTable('odoo-purchase-orders',
  ['Revisión','Pedido','Proveedor','Estado en Odoo','Líneas','Base','Impuestos','Total'],
  all.map(o=>[
   o.complete?'Con líneas · revisar':'Pendiente · sin líneas',
   o.reference,o.supplier_name,o.status,
   o.complete?String(o.lines.length):'0',
   o.complete?odooPurchaseMoney(o.base):'No computable',
   o.complete?(o.tax_amount===null?'No exportados':odooPurchaseMoney(o.tax_amount)):'No computable',
   o.complete?odooPurchaseMoney(o.total):'No computable'
  ]));
 receptionTable('odoo-purchase-lines',
  ['Pedido','ID externo de línea','SKU','Producto','Cantidad','Precio unitario','Subtotal'],
  orders.flatMap(o=>o.lines.map(l=>[o.reference,l.external_line_id||'No exportado',l.sku,l.product_display,l.quantity,odooPurchaseMoney(l.unit_price),odooPurchaseMoney(l.subtotal)])));
 odooPurchaseMessages('odoo-purchase-warnings',data.warnings||[]);
 $('odoo-purchase-preview').hidden=false;
}
$('odoo-purchase-check').onclick=async()=>{
 if(odooPurchaseBusy)return;
 odooPurchaseReset();
 const revision=odooPurchaseRevision,file=$('odoo-purchase-file').files[0];
 if(!file||!/\.(xlsx|csv)$/i.test(file.name)||!file.size||file.size>10*1024*1024){
  $('odoo-purchase-status').textContent='Selecciona un Excel o CSV de Odoo válido, hasta 10 MiB.';return;
 }
 const company=$('reception-company-id').value.trim();
 const legalName=$('reception-company-name').value.trim();
 const companyText=(company||legalName)?[company,legalName].filter(Boolean).join(' · '):'';
 odooPurchaseBusy=true;$('odoo-purchase-check').disabled=true;
 $('odoo-purchase-status').textContent='Comprobando el archivo. Ningún dato se guarda.';
 try{
  const data=await api('/api/odoo/purchase-orders/preview',{
   method:'POST',
   headers:{'Content-Type':'application/octet-stream','X-EIOS-Token':token,'X-EIOS-Filename':encodeURIComponent(file.name)},
   body:file
  });
  if(revision!==odooPurchaseRevision)return;
  odooPurchaseRender(data,companyText);
  $('odoo-purchase-status').textContent=(data.errors.length?'Archivo con errores · ':data.pending_orders.length?'Archivo con pedidos pendientes · ':'Comprobación terminada · ')+'solo vista previa, sin guardar.';
 }catch(error){
  if(revision===odooPurchaseRevision)$('odoo-purchase-status').textContent='NO SE HA GUARDADO · '+error.message;
 }finally{
  odooPurchaseBusy=false;$('odoo-purchase-check').disabled=false;
 }
};
'''
