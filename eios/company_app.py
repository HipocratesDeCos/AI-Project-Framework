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
        return dict(info=info, suppliers=[r['data'] for r in self.store.records(dataset, 'supplier')],
                    articles=[r['data'] for r in self.store.records(dataset, 'article')],
                    pending=[r['data'] for r in self.store.records(dataset, 'missing_or_conflicting')],
                    purchases=proposals)

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


PAGE = '''<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>EIOS · Empresa y compras</title><style>
body{font:16px system-ui;background:#edf5fc;color:#16324b;max-width:1100px;margin:32px auto;padding:20px}
section{background:white;padding:24px;border-radius:14px;margin:20px 0}h1,h2{margin-top:0}
label{display:inline-block;margin:10px 14px 10px 0}input,select,button{font:inherit;padding:10px;border:1px solid #bacbda;border-radius:6px;max-width:95%}
button{background:#175b93;color:white;cursor:pointer}table{width:100%;border-collapse:collapse}td,th{text-align:left;padding:10px;border-bottom:1px solid #dde6ed}#notice{white-space:pre-wrap}small{display:block} .scroll{overflow:auto}
</style><h1>EIOS · EMPRESA Y COMPRAS</h1><p>Empresa ficticia · Propuestas para evaluación</p>
<label>Versión documental <select id="dataset"></select></label><section><h2 id="company">Empresa</h2><p id="summary"></p><details><summary>Datos pendientes</summary><pre id="pending" style="white-space:pre-wrap"></pre></details></section>
<section><h2>INTRODUCIR COMPRA</h2><p>Introduce el precio de la oferta que quieres comprobar. Los precios históricos no se aplican automáticamente.</p>
<form id="form"><label>Referencia<br><input name="reference" required maxlength="100"></label>
<label>Proveedor<br><select name="supplier_id" id="supplier" required></select></label>
<label>Artículo<br><select name="article_id" id="article" required></select></label><small id="unit"></small>
<label>Cantidad<br><input name="quantity" type="number" min="0.000001" step="any" required></label>
<label>Precio por unidad (€)<br><input name="unit_price" type="number" min="0.000001" step="any" required></label>
<label>IVA (%)<br><input name="vat_percent" type="number" min="0" max="100" step="any" required></label>
<label>Fecha del pedido<br><input name="order_date" type="date" required></label>
<label>Vencimiento<br><input name="due_date" type="date" required></label>
<p><button id="save">Guardar propuesta</button></p></form><p id="notice" role="status"></p>
<p>Una propuesta guardada queda pendiente de evaluación. No genera un pedido al proveedor ni modifica existencias o saldos.</p></section>
<section><h2>PROPUESTAS GUARDADAS</h2><div class="scroll"><table><thead><tr><th>Referencia</th><th>Artículo</th><th>Total €</th><th>Vencimiento</th><th>Estado</th></tr></thead><tbody id="rows"></tbody></table></div></section>
<script>
let state; const $=id=>document.getElementById(id); const token=TOKEN;
function option(select,value,label){let o=document.createElement('option');o.value=value;o.textContent=label;select.append(o)}
async function api(path,opts){let r=await fetch(path,opts);let d=await r.json();if(!r.ok)throw Error(d.error);return d}
function articles(){ $('article').replaceChildren();state.articles.filter(a=>a.supplier_id===$('supplier').value).forEach(a=>option($('article'),a.article_id,a.description));unit() }
function unit(){let a=state.articles.find(a=>a.article_id===$('article').value);$('unit').textContent=a?'Unidad: '+a.unit_as_documented+' · Stock y demanda: sin datos confirmados.':''}
async function refresh(){state=await api('/api/state?dataset='+encodeURIComponent($('dataset').value));$('company').textContent=state.info.company.legal_name||JSON.stringify(state.info.company);$('summary').textContent='Corte: '+state.info.as_of_date+' · Documentos: '+state.info.documents+' · Artículos: '+state.articles.length;$('pending').textContent=state.pending.map(x=>JSON.stringify(x,null,2)).join('\\n');$('supplier').replaceChildren();state.suppliers.forEach(s=>option($('supplier'),s.supplier_id,s.legal_name));articles();$('rows').replaceChildren();state.purchases.forEach(p=>{let tr=document.createElement('tr');[p.reference,p.article_id,p.total,p.due_date,'PENDIENTE DE EVALUACIÓN'].forEach(v=>{let td=document.createElement('td');td.textContent=v;tr.append(td)});$('rows').append(tr)})}
$('supplier').onchange=articles;$('article').onchange=unit;$('dataset').onchange=()=>refresh().catch(e=>$('notice').textContent=e.message);
$('form').onsubmit=async e=>{e.preventDefault();$('save').disabled=true;try{let d=Object.fromEntries(new FormData(e.target));d.dataset_id=$('dataset').value;await api('/api/purchases',{method:'POST',headers:{'Content-Type':'application/json','X-EIOS-Token':token},body:JSON.stringify(d)});e.target.reset();await refresh();$('notice').textContent='PROPUESTA GUARDADA · Pendiente de evaluación.'}catch(e){$('notice').textContent=e.message}finally{$('save').disabled=false}};
api('/api/datasets').then(ds=>{ds.forEach(d=>option($('dataset'),d.dataset_id,d.company_id+' · '+d.as_of_date+' · '+d.dataset_id.slice(0,8)));return refresh()}).catch(e=>$('notice').textContent=e.message);
</script></html>'''


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
