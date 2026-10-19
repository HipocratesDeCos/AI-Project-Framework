"""Local company viewer and persistent synthetic purchase proposal entry."""
from __future__ import annotations

import argparse
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from pathlib import Path
import secrets
import sqlite3
from uuid import uuid4

from eios.company_data import CompanyDataStore
from eios.purchase_history import purchase_history
from eios.company_inventory import read_inventory
from eios.company_planning import planning_context


class PurchaseDesk:
    def __init__(self, db):
        self.db = Path(db)
        if not self.db.is_file():
            raise ValueError('Primero carga el paquete documental en la base indicada.')
        self.store = CompanyDataStore(self.db)
        with sqlite3.connect(self.db) as c:
            c.execute('SELECT dataset_id FROM documentary_company_snapshot LIMIT 1')
            c.execute('''CREATE TABLE IF NOT EXISTS manual_purchase_proposal (
                proposal_id TEXT PRIMARY KEY, dataset_id TEXT NOT NULL,
                created_at TEXT NOT NULL, payload TEXT NOT NULL,
                FOREIGN KEY(dataset_id) REFERENCES documentary_company_snapshot(dataset_id))''')

    def state(self, dataset):
        info = self.store.describe(dataset)
        with sqlite3.connect(self.db) as c:
            proposals = [json.loads(r[0]) for r in c.execute(
                'SELECT payload FROM manual_purchase_proposal WHERE dataset_id=? ORDER BY created_at DESC', (dataset,))]
        return dict(info=info, customers=[r['data'] for r in self.store.records(dataset, 'customer')], suppliers=[r['data'] for r in self.store.records(dataset, 'supplier')],
                    articles=[r['data'] for r in self.store.records(dataset, 'article')],
                    pending=[r['data'] for r in self.store.records(dataset, 'missing_or_conflicting')],
                    purchases=proposals, inventory=read_inventory(self.db, dataset),
                    planning=planning_context(self.db, dataset, info['company']['company_id'], self.store.records(dataset, 'article')),
                    history={a['data']['article_id']: purchase_history(self.store, dataset, a['data'], info['as_of_date'])
                             for a in self.store.records(dataset, 'article')})

    def save(self, data):
        dataset = str(data['dataset_id'])
        state = self.state(dataset)
        supplier = str(data['supplier_id'])
        article = next((a for a in state['articles'] if a['article_id'] == data['article_id']), None)
        if supplier not in {s['supplier_id'] for s in state['suppliers']} or not article or article['supplier_id'] != supplier:
            raise ValueError('El artículo debe pertenecer al proveedor seleccionado.')
        try:
            qty, price, vat = [Decimal(str(data[k])) for k in ('quantity', 'unit_price', 'vat_percent')]
            if not all(v.is_finite() for v in (qty, price, vat)) or qty <= 0 or price <= 0 or not 0 <= vat <= 100:
                raise ValueError('Cantidad y precio deben ser positivos; IVA entre 0 y 100.')
            if qty > Decimal('1000000000') or price > Decimal('1000000000'):
                raise ValueError('Cantidad o precio fuera de rango.')
            ordered = date.fromisoformat(data['order_date'])
            due = date.fromisoformat(data['due_date'])
            if due < ordered:
                raise ValueError('El vencimiento no puede ser anterior al pedido.')
        except (InvalidOperation, TypeError):
            raise ValueError('Revisa los importes.') from None
        reference = str(data.get('reference', '')).strip()
        if not reference or len(reference) > 100:
            raise ValueError('Indica una referencia de hasta 100 caracteres.')
        net = (qty * price).quantize(Decimal('.01'))
        tax = (net * vat / 100).quantize(Decimal('.01'))
        result = dict(proposal_id=str(uuid4()), dataset_id=dataset, reference=reference,
                      supplier_id=supplier, article_id=article['article_id'], unit=article['unit_as_documented'],
                      quantity=str(qty), unit_price=str(price), vat_percent=str(vat), net=str(net), tax=str(tax),
                      total=str(net + tax), currency='EUR', order_date=ordered.isoformat(), due_date=due.isoformat(),
                      status='PENDIENTE_DE_EVALUACION', decision_authority=False, operational_path='FORBIDDEN',
                      created_at=datetime.now(timezone.utc).isoformat())
        with sqlite3.connect(self.db) as c:
            c.execute('PRAGMA foreign_keys=ON')
            if c.execute('SELECT 1 FROM manual_purchase_proposal WHERE dataset_id=? AND json_extract(payload,?)=?',
                         (dataset, '$.reference', reference)).fetchone():
                raise ValueError('Esta referencia ya está registrada en esta versión de empresa.')
            c.execute('INSERT INTO manual_purchase_proposal VALUES(?,?,?,?)',
                      (result['proposal_id'], dataset, result['created_at'], json.dumps(result)))
        return result


PAGE = '''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>EIOS · Propuestas</title>
<style>
*{box-sizing:border-box}body{margin:0;font:15px system-ui,sans-serif;background:#f4f6f9;color:#15213c}button,input,select{font:inherit}button{cursor:pointer}button:focus-visible,a:focus-visible,input:focus-visible,select:focus-visible{outline:3px solid #548bed;outline-offset:3px}
.sidebar{position:fixed;inset:0 auto 0 0;width:248px;background:#0a1128;color:white;padding:26px 12px;z-index:2}.brand{font-size:40px;font-weight:750;padding:0 14px;margin-bottom:48px}.nav{display:flex;align-items:center;gap:16px;width:100%;padding:17px 12px;margin:6px 0;border:0;border-radius:9px;color:#a0abbe;background:transparent;text-align:left;font-size:14px}.nav svg{width:26px;height:26px;flex-shrink:0;stroke:white;fill:none;stroke-width:1.7;stroke-linecap:round;stroke-linejoin:round}.nav[aria-current=page]{background:#152c56;color:white;font-weight:650}.topbar{margin-left:248px;min-height:72px;background:#050b1a;color:white;display:flex;align-items:center;gap:24px;padding:12px 24px}.topbar input{width:100%;border:0;background:#152c56;color:white;padding:13px 16px;border-radius:12px}.topbar input::placeholder{color:#b4bfd3}.searchbox{position:relative;flex:1;max-width:520px}.search-results{position:absolute;top:48px;left:0;right:0;max-height:300px;overflow:auto;z-index:4;background:white;color:#15213c;box-shadow:0 4px 18px #0003}.search-results button{display:block;width:100%;background:white;border:0;border-bottom:1px solid #ddd;text-align:left;padding:12px}.topbar span{font-size:14px}main{margin-left:248px;padding:24px 30px;max-width:1450px}.context{display:flex;justify-content:space-between;align-items:center;gap:16px;margin-bottom:24px}.context h1{font-size:20px;margin:0 0 5px}.context p{margin:0;color:#68748a;font-size:13px}.context select{max-width:250px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:20px}.card{border:1px solid #dce2eb;background:white;border-radius:8px;padding:22px;margin-bottom:20px}h2{font-size:20px;font-weight:550;color:#13346f;margin:0 0 18px}h3{font-size:15px;color:#13346f}label{display:block;font-size:14px;margin-bottom:14px}input,select{display:block;width:100%;padding:10px;border:1px solid #c9d9e9;border-radius:4px;background:#e1effb;color:#15213c;margin-top:5px;min-width:0}input[readonly]{color:#4e5e73;background:#edf3f8}small{display:block;color:#68748a;line-height:1.5}p{line-height:1.5}.fields{display:grid;grid-template-columns:1fr 1fr;gap:0 16px}.metric{background:#e1effb;border-radius:4px;padding:12px;min-height:68px;margin-bottom:14px}.metric span{display:block;font-size:12px;color:#52647a;margin-bottom:5px}.metric strong{font-size:17px;font-weight:600}.primary{background:#0a369d;color:white;padding:14px 30px;border:0;border-radius:7px}.actions{text-align:center;margin:20px 0}.scroll{overflow:auto}table{width:100%;border-collapse:collapse;font-size:13px}td,th{padding:12px 8px;text-align:left;border-bottom:1px solid #e1e7ef}th{color:#52647a}details{margin:16px 0}summary{cursor:pointer;color:#13346f}#notice{white-space:pre-wrap;padding:12px;color:#13346f}pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:12px}.badge{font-size:12px;color:#65748b}button:disabled{opacity:.6;cursor:wait}[hidden]{display:none!important}
@media(max-width:1000px){.sidebar{width:210px}.topbar,main{margin-left:210px}.topbar span{display:none}.nav{font-size:12px;gap:10px}.context{align-items:flex-start;flex-direction:column}main{padding:20px}.grid{gap:14px}}
@media(max-width:700px){.sidebar{position:static;width:auto;padding:12px}.brand{font-size:26px;margin-bottom:10px}.sidebar nav{display:flex;overflow:auto}.nav{width:auto;flex-shrink:0;padding:10px}.nav svg{width:20px;height:20px}.topbar,main{margin-left:0}.grid,.fields{grid-template-columns:1fr}.topbar{padding:12px}.context select{max-width:100%}}
</style></head><body><aside class="sidebar"><div class="brand">EIOS</div><nav aria-label="Menú principal"><button type="button" class="nav" data-nav="inicio"><svg viewBox="0 0 24 26" aria-hidden="true"><path d="M3 11 12 3l9 8M5 10v11h5v-7h4v7h5V10"/></svg>Inicio</button><button type="button" class="nav" data-nav="propuestas" aria-current="page"><svg viewBox="0 0 24 26" aria-hidden="true"><path d="M13 3H4v18h10M8 7h5M8 11h3M15 12l4-4 3 3-8 8-4 1 1-4z"/></svg>Propuestas</button><button type="button" class="nav" data-nav="proveedores"><svg viewBox="0 0 24 26" aria-hidden="true"><path d="M2 5h13v12H2zM15 9h4l3 4v4h-7"/><circle cx="6" cy="18" r="2"/><circle cx="18" cy="18" r="2"/></svg>Cartera de Proveedores</button><button type="button" class="nav" data-nav="clientes"><svg viewBox="0 0 24 26" aria-hidden="true"><circle cx="9" cy="7" r="4"/><path d="M2 21v-4a7 7 0 0 1 14 0v4zM17 4a4 4 0 0 1 0 8M19 15q3 1 3 6h-3"/></svg>Cartera de Clientes</button><button type="button" class="nav" data-nav="stock"><svg viewBox="0 0 24 26" aria-hidden="true"><path d="m12 2 6 3v7l-6 3-6-3V5zM6 5l6 3 6-3M12 8v7M6 12l-5 3v6l5 3 6-3 6 3 5-3v-6l-5-3M1 15l5 3 6-3 6 3 5-3M6 18v6M18 18v6"/></svg>Stock</button><button type="button" class="nav" data-nav="archivos"><svg viewBox="0 0 24 26" aria-hidden="true"><path d="M14 2H4v20h16V8zM14 2v6h6M12 19V11m-4 4 4-4 4 4"/></svg>Carga de archivos</button></nav></aside>
<header class="topbar"><div class="searchbox"><input id="search" aria-label="Buscar cliente, proveedor o artículo" placeholder="Busca cliente, proveedor, artículo, SKU" autocomplete="off"><div id="search-results" class="search-results" hidden></div></div><span>Enterprise Intelligent Operations System</span></header>
<main><div class="context"><div><h1 id="company">Empresa</h1><p id="summary"></p><span class="badge">Empresa ficticia · Datos documentados y supuestos identificados</span></div><label>Versión documental<select id="dataset"></select></label></div>
<div data-view="inicio" hidden><section class="card"><h2>Inicio</h2><p>Consulta los datos de la empresa o prepara una propuesta de compra desde el menú lateral.</p><p id="overview"></p><details><summary>Datos pendientes de completar</summary><pre id="pending"></pre></details></section></div>
<div data-view="propuestas"><form id="form"><div class="grid"><section class="card"><h2>Artículo</h2><label>SKU<input id="sku" readonly></label><label>Descripción<select name="article_id" id="article" required></select></label><div class="fields"><label>Familia<input readonly value="Sin datos"></label><label>Unidad<input id="article-unit" readonly></label></div><small id="unit"></small></section>
<section class="card"><h2>Proveedor</h2><label>Código de proveedor<input id="supplier-code" readonly></label><label>Razón social<select name="supplier_id" id="supplier" required></select></label><div class="fields"><label>Localidad<input readonly value="Sin datos"></label><label>Estado comercial<input readonly value="Sin datos"></label></div><small>Selecciona el proveedor para consultar sus artículos.</small></section></div>
<div class="grid"><section class="card"><h2>Datos del artículo</h2><div class="fields"><div class="metric"><span>Precio neto última compra</span><strong id="last-price">Sin datos</strong></div><div class="metric"><span>Cantidad última compra</span><strong id="last-quantity">Sin datos</strong></div><div class="metric"><span>Fecha última compra</span><strong id="last-date">Sin datos</strong></div><div class="metric"><span>Stock disponible</span><strong id="available">Sin datos</strong></div></div><small id="last-source"></small><p id="stock"></p><details><summary>Cobertura y planificación</summary><p id="planning"></p><small>Simulación a la fecha de corte. Los pedidos pendientes de recibir no están confirmados; todavía no se calcula una cantidad recomendada.</small></details><details><summary>HISTORIAL DOCUMENTADO DEL ARTÍCULO</summary><div class="scroll"><table><thead><tr><th>Fecha / factura</th><th>Cantidad</th><th>Precio documentado</th><th>Precio neto efectivo</th><th>Fuente</th></tr></thead><tbody id="history"></tbody></table></div></details></section>
<section class="card"><h2>Propuesta</h2><label>Referencia de la propuesta<input name="reference" required maxlength="100" placeholder="Ej.: PROP-2026-001"></label><div class="fields"><label>Precio neto por unidad (€)<input name="unit_price" type="number" min="0.000001" step="any" required></label><label>Cantidad<input name="quantity" type="number" min="0.000001" step="any" required></label><label>IVA (%)<input name="vat_percent" type="number" min="0" max="100" step="any" required></label><label>Fecha del pedido<input name="order_date" type="date" required></label><label>Vencimiento<input name="due_date" type="date" required></label></div><small>Precio sin IVA y después de descuentos. Portes, otros gastos y cuotas de pago todavía no se incorporan a esta propuesta.</small><p id="comparison" role="status"></p></section></div>
<div class="actions"><button class="primary" id="save">Guardar propuesta</button><p><small>Queda pendiente de evaluación. No genera un pedido ni modifica el stock o la tesorería.</small></p></div></form><section class="card"><h2>Propuestas guardadas</h2><div class="scroll"><table><thead><tr><th>Referencia</th><th>Artículo</th><th>Total €</th><th>Vencimiento</th><th>Estado</th></tr></thead><tbody id="rows"></tbody></table></div></section></div>
<div data-view="proveedores" hidden><section class="card"><h2>Cartera de Proveedores</h2><div class="scroll"><table><thead><tr><th>Código</th><th>Razón social</th><th>Artículos</th></tr></thead><tbody id="suppliers-table"></tbody></table></div></section></div>
<div data-view="clientes" hidden><section class="card"><h2>Cartera de Clientes</h2><div class="scroll"><table><thead><tr><th>Código</th><th>Razón social</th></tr></thead><tbody id="customers-table"></tbody></table></div></section></div>
<div data-view="stock" hidden><section class="card"><h2>Stock</h2><p>Inventario sintético del caso ficticio. Las existencias no se deducen de las facturas de compra.</p><div class="scroll"><table><thead><tr><th>SKU / artículo</th><th>Físico</th><th>Reservado</th><th>Disponible</th><th>Unidad</th><th>Fecha</th></tr></thead><tbody id="stock-table"></tbody></table></div></section></div>
<div data-view="archivos" hidden><section class="card"><h2>Carga de archivos</h2><p>La carga desde esta pantalla todavía no está habilitada. La empresa visible procede del paquete documental importado en la base de datos.</p><p id="document-summary"></p></section></div><p id="notice" role="status"></p></main>
<script>
let state; const $=id=>document.getElementById(id); const token=TOKEN;
function option(select,value,label){let o=document.createElement('option');o.value=value;o.textContent=label;select.append(o)}
async function api(path,opts){let r=await fetch(path,opts);let d=await r.json();if(!r.ok)throw Error(d.error);return d}
function articles(){ $('article').replaceChildren();state.articles.filter(a=>a.supplier_id===$('supplier').value).forEach(a=>option($('article'),a.article_id,a.description));unit() }
function money(v){if(v===null||v===undefined)return 'Sin datos';let n=Number(v);return Number.isFinite(n)?n.toLocaleString('es-ES',{minimumFractionDigits:2,maximumFractionDigits:4}):'Sin datos'}
function unit(){
 let a=state.articles.find(a=>a.article_id===$('article').value);
 $('unit').textContent=a?'Unidad: '+a.unit_as_documented:'';
 let stock=a?state.inventory[a.article_id]:null;
 $('stock').textContent=stock?'INVENTARIO SINTÉTICO A '+stock.as_of_date+' · Físico: '+stock.physical+' · Reservado: '+stock.reserved+' · Disponible: '+stock.available+' '+stock.unit+'. Supuestos del caso ficticio; sin conciliación con el balance.':'STOCK: SIN DATOS DE INVENTARIO';

 let plan=a?state.planning[a.article_id]:null;
 $('planning').textContent=plan&&plan.status!=='MISSING_DATA'?
 'PLANIFICACIÓN SINTÉTICA · Fecha: '+plan.as_of_date+' · Demanda adicional: '+plan.daily_demand+' '+plan.unit+'/día · Plazo de entrega supuesto: '+plan.lead_time_days+' días · Stock de seguridad supuesto: '+plan.safety_stock+' '+plan.unit+' · Cobertura del disponible (motor STK): '+(plan.coverage_days!==null?money(plan.coverage_days)+' días':plan.status==='UNBOUNDED'?'sin consumo previsto':'no determinable')+'. Previsión válida hasta '+plan.valid_to+'.':
 'DEMANDA, ENTREGA Y SEGURIDAD: SIN PLANIFICACIÓN CARGADA';
 $('history').replaceChildren();
 let rows=a?(state.history[a.article_id]||[]):[];
 rows.forEach(r=>{let tr=document.createElement('tr');
 [r.issue_date+' · '+r.invoice_number,(r.quantity??'Sin datos')+' '+(r.unit||''),money(r.unit_price)+' '+(r.currency||''),money(r.effective_net_unit_price)+' '+(r.currency||'')+' sin IVA',r.source_refs.map(s=>s.document_ref+(s.page?' · pág. '+s.page:'')).join('; ')].forEach(v=>{let td=document.createElement('td');td.textContent=v;tr.append(td)});$('history').append(tr)});
 if(!rows.length){let tr=document.createElement('tr');let td=document.createElement('td');td.colSpan=5;td.textContent='Sin compras facturadas vinculadas a este artículo hasta la fecha de corte.';tr.append(td);$('history').append(tr)}
 articleSummary(a,rows,stock);compare();
}
function compare(){
 let a=state.articles.find(a=>a.article_id===$('article').value);
 let rows=a?(state.history[a.article_id]||[]):[];
 let target=$('comparison');target.textContent='Introduce un precio neto por unidad, sin IVA y después de descuentos, para compararlo.';
 if(!rows.length){target.textContent='No hay una compra histórica documentada con la que comparar.';return}
 let latest=rows.filter(r=>r.issue_date===rows[0].issue_date);
 if(latest.length!==1){target.textContent='Hay varias líneas en la fecha más reciente. Consulta el historial; no se selecciona una automáticamente.';return}
 let r=latest[0],old=Number(r.effective_net_unit_price);
 if(!r.comparable||!Number.isFinite(old)||old<=0){target.textContent='Precios no comparables: revisa moneda, unidad e importe neto.';return}
 let raw=$('form').elements.unit_price.value,price=Number(raw);
 if(!raw||!Number.isFinite(price)||price<=0)return;
 let delta=price-old,pct=delta/old*100;
 target.textContent='Respecto a la última compra documentada ('+r.issue_date+', '+r.invoice_number+'): '+(delta>=0?'+':'')+money(delta)+' €/unidad · '+(pct>=0?'+':'')+money(pct)+' %. Comparación orientativa de precios netos; no es una recomendación de compra.';
}
async function refresh(){state=await api('/api/state?dataset='+encodeURIComponent($('dataset').value));$('company').textContent=state.info.company.legal_name||JSON.stringify(state.info.company);$('summary').textContent='Corte: '+state.info.as_of_date+' · Documentos: '+state.info.documents+' · Artículos: '+state.articles.length;$('pending').textContent=state.pending.map(x=>JSON.stringify(x,null,2)).join('\\n');$('supplier').replaceChildren();state.suppliers.forEach(s=>option($('supplier'),s.supplier_id,s.legal_name));articles();catalogues();$('rows').replaceChildren();state.purchases.forEach(p=>{let tr=document.createElement('tr');[p.reference,p.article_id,p.total,p.due_date,'PENDIENTE DE EVALUACIÓN'].forEach(v=>{let td=document.createElement('td');td.textContent=v;tr.append(td)});$('rows').append(tr)})}

function view(name){document.querySelectorAll('[data-view]').forEach(el=>el.hidden=el.dataset.view!==name);document.querySelectorAll('[data-nav]').forEach(el=>{if(el.dataset.nav===name)el.setAttribute('aria-current','page');else el.removeAttribute('aria-current')});document.title='EIOS · '+({inicio:'Inicio',propuestas:'Propuestas',proveedores:'Proveedores',clientes:'Clientes',stock:'Stock',archivos:'Carga de archivos'}[name]);$('notice').textContent=''}
function tableRows(id,rows){$(id).replaceChildren();rows.forEach(values=>{let tr=document.createElement('tr');values.forEach(value=>{let td=document.createElement('td');td.textContent=value??'Sin datos';tr.append(td)});$(id).append(tr)})}
function catalogues(){tableRows('suppliers-table',state.suppliers.map(s=>[s.supplier_id,s.legal_name,state.articles.filter(a=>a.supplier_id===s.supplier_id).length]));tableRows('customers-table',(state.customers||[]).map(c=>[c.customer_id,c.legal_name]));tableRows('stock-table',state.articles.map(a=>{let i=state.inventory[a.article_id];return [a.article_id+' · '+a.description,i?.physical,i?.reserved,i?.available,i?.unit||a.unit_as_documented,i?.as_of_date]}));$('overview').textContent=state.suppliers.length+' proveedores · '+(state.customers||[]).length+' clientes · '+state.articles.length+' artículos · '+state.purchases.length+' propuestas guardadas.';$('document-summary').textContent=state.info.documents+' documentos en la versión seleccionada. Fecha de corte: '+state.info.as_of_date;search()}
function articleSummary(a,rows,stock){$('sku').value=a?.article_id||'';$('article-unit').value=a?.unit_as_documented||'';$('supplier-code').value=$('supplier').value;$('available').textContent=stock?stock.available+' '+stock.unit:'Sin inventario';let latest=rows.length?rows.filter(r=>r.issue_date===rows[0].issue_date):[];let r=latest.length===1?latest[0]:null;$('last-price').textContent=r&&r.comparable?money(r.effective_net_unit_price)+' € / '+r.unit:'Sin referencia única';$('last-quantity').textContent=r?(r.quantity??'Sin datos')+' '+(r.unit||''):'Sin referencia única';$('last-date').textContent=rows[0]?.issue_date||'Sin compras';$('last-source').textContent=r?'Factura '+r.invoice_number+' · Precio neto efectivo, sin IVA.':latest.length>1?'Varias líneas en la última fecha: consulta el historial.':'Sin compra histórica documentada.';}
function search(){let target=$('search-results'),q=$('search').value.trim().toLocaleLowerCase('es');target.replaceChildren();target.hidden=!q;if(!q||!state)return;let items=[...state.articles.map(a=>({text:a.article_id+' · '+a.description,go:()=>{$('supplier').value=a.supplier_id;articles();$('article').value=a.article_id;unit();view('propuestas')}})),...state.suppliers.map(s=>({text:s.supplier_id+' · '+s.legal_name,go:()=>{$('supplier').value=s.supplier_id;articles();view('propuestas')}})),...(state.customers||[]).map(c=>({text:c.customer_id+' · '+c.legal_name,go:()=>view('clientes')}))].filter(x=>x.text.toLocaleLowerCase('es').includes(q)).slice(0,20);if(!items.length)target.textContent='Sin resultados';items.forEach(item=>{let b=document.createElement('button');b.type='button';b.textContent=item.text;b.onclick=()=>{item.go();target.hidden=true;$('search').value=''};target.append(b)})}
document.querySelectorAll('[data-nav]').forEach(b=>b.onclick=()=>view(b.dataset.nav));$('search').addEventListener('input',search);$('search').addEventListener('keydown',e=>{if(e.key==='Escape')$('search-results').hidden=true});

$('form').elements.unit_price.addEventListener('input',compare);
$('supplier').onchange=articles;$('article').onchange=unit;$('dataset').onchange=()=>refresh().catch(e=>$('notice').textContent=e.message);
$('form').onsubmit=async e=>{e.preventDefault();$('save').disabled=true;try{let d=Object.fromEntries(new FormData(e.target));d.dataset_id=$('dataset').value;await api('/api/purchases',{method:'POST',headers:{'Content-Type':'application/json','X-EIOS-Token':token},body:JSON.stringify(d)});e.target.reset();await refresh();$('notice').textContent='PROPUESTA GUARDADA · Pendiente de evaluación.'}catch(e){$('notice').textContent=e.message}finally{$('save').disabled=false}};
api('/api/datasets').then(ds=>{ds.forEach(d=>option($('dataset'),d.dataset_id,d.company_id+' · '+d.as_of_date+' · '+d.dataset_id.slice(0,8)));return refresh()}).catch(e=>$('notice').textContent=e.message);
</script></body></html>'''


def main():
    parser = argparse.ArgumentParser(description='EIOS: empresa y entrada local de propuestas de compra')
    parser.add_argument('--db', type=Path, required=True)
    parser.add_argument('--port', type=int, default=8765)
    args = parser.parse_args()
    desk = PurchaseDesk(args.db)
    token = secrets.token_urlsafe(32)

    class Handler(BaseHTTPRequestHandler):
        def send(self, status, data, html=False):
            body = data.encode() if html else json.dumps(data, ensure_ascii=False).encode()
            self.send_response(status)
            self.send_header('Content-Type', 'text/html; charset=utf-8' if html else 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            from urllib.parse import urlparse, parse_qs
            if self.headers.get('Host') not in {f'127.0.0.1:{args.port}', f'localhost:{args.port}'}:
                return self.send(403, dict(error='Host no permitido'))
            path = urlparse(self.path)
            try:
                if path.path == '/':
                    return self.send(200, PAGE.replace('TOKEN', json.dumps(token)), True)
                if path.path == '/api/datasets':
                    with sqlite3.connect(args.db) as c:
                        rows = c.execute('SELECT dataset_id,company_id,as_of_date FROM documentary_company_snapshot ORDER BY as_of_date DESC,dataset_id').fetchall()
                    return self.send(200, [dict(zip(('dataset_id','company_id','as_of_date'), r)) for r in rows])
                if path.path == '/api/state':
                    return self.send(200, desk.state(parse_qs(path.query)['dataset'][0]))
                self.send(404, dict(error='No encontrado'))
            except (KeyError, ValueError):
                self.send(400, dict(error='Versión documental no válida'))

        def do_POST(self):
            if self.headers.get('X-EIOS-Token') != token:
                return self.send(403, dict(error='Sesión no válida. Recarga la pantalla.'))
            if self.path != '/api/purchases':
                return self.send(404, dict(error='No encontrado'))
            try:
                size = int(self.headers.get('Content-Length', '0'))
                if not 0 < size <= 16384:
                    raise ValueError('Solicitud demasiado grande o vacía.')
                data = json.loads(self.rfile.read(size))
                self.send(201, desk.save(data))
            except (ValueError, KeyError, TypeError) as error:
                self.send(400, dict(error=str(error)))

    server = HTTPServer(('127.0.0.1', args.port), Handler)
    print(f'EIOS: abre http://127.0.0.1:{args.port} · Ctrl+C para cerrar', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
