"""Reversible sales references, separate from invoices, collections and inventory."""
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
import json
import secrets
from time import monotonic
import sqlite3

from eios.company_proposal_context import _hash
from eios.company_sales_tariffs import batch
from eios.company_selected_inventory import identity

SCHEMA='''CREATE TABLE IF NOT EXISTS company_sales_history_selection (
 dataset_id TEXT NOT NULL, revision INTEGER NOT NULL, payload TEXT NOT NULL,
 PRIMARY KEY(dataset_id,revision))'''


def latest(c,dataset):
    if not c.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='company_sales_history_selection'").fetchone():return None
    row=c.execute('SELECT payload FROM company_sales_history_selection WHERE dataset_id=? ORDER BY revision DESC LIMIT 1',(dataset,)).fetchone()
    return json.loads(row[0]) if row else None


def selection_context(c,dataset):
    selected=latest(c,dataset)
    if not selected:return None
    sources={}
    for bid in selected.get('batch_ids',[]):
        loaded=batch(c,bid);sources[bid]=dict(fingerprint=loaded[2] if loaded else None,intact=bool(loaded and loaded[3]))
    return dict(revision=selected['revision'],selection_fingerprint=_hash(selected),sources=sources,cleared=selected.get('cleared',False))


def validate(c,dataset,ids):
    from eios.company_commercial_catalogue import apply_catalogue
    scoped=c.execute('SELECT company_id,as_of_date,manifest_json FROM documentary_company_snapshot WHERE dataset_id=?',(dataset,)).fetchone()
    if not scoped:raise ValueError('Empresa documental no encontrada.')
    manifest=json.loads(scoped[2])
    if manifest.get('material_nature')!='SYNTHETIC':raise ValueError('Esta selección admite solo empresas ficticias.')
    rows=[(k,i,json.loads(raw)) for k,i,raw in c.execute("SELECT kind,record_id,record_json FROM documentary_company_record WHERE dataset_id=? AND kind IN ('article','customer','sales_invoice')",(dataset,))]
    articles,_,_=apply_catalogue(c,dataset,[r['data'] for k,_,r in rows if k=='article'],[])
    catalogue={a['article_id']:a for a in articles}
    parties={r['data']['customer_id']:r['data'] for k,_,r in rows if k=='customer'}
    existing={(r['data'].get('customer_id'),r['data'].get('invoice_number') or i) for k,i,r in rows if k=='sales_invoice'}
    entries=[];errors=[];fingerprints={};files=[];seen=set();headers={};total=0
    for bid in sorted(ids):
        loaded=batch(c,bid)
        if not loaded or not loaded[3]:raise ValueError('Algún archivo no está disponible o su integridad ha cambiado.')
        meta,records,fp,_=loaded
        if (meta.get('kind'),meta.get('company_id'),meta.get('legal_name'),meta.get('material_nature'),meta.get('as_of_date'))!=('sales_line',scoped[0],manifest['company'].get('legal_name'),'SYNTHETIC',scoped[1]):raise ValueError('Selecciona solo líneas de venta de la empresa ficticia y corte activos.')
        total+=len(records)
        if total>20000:raise ValueError('Máximo 20.000 líneas entre todos los archivos seleccionados.')
        fingerprints[bid]=fp;files.append(meta['filename'])
        for r in records:
            d=r.get('data',{});sku=d.get('article_id');customer=d.get('customer_id');inv=d.get('invoice_number');problem=None
            if r.get('kind')!='sales_line' or sku not in catalogue:problem='SKU sin ficha en el catálogo activo.'
            elif customer not in parties:problem='Cliente sin ficha activa. Utiliza su código exacto, no su nombre.'
            elif d.get('unit')!=catalogue[sku].get('unit_as_documented'):problem='Unidad distinta de la ficha; no se convierten embalajes.'
            elif not isinstance(inv,str) or not inv.strip():problem='Número de factura vacío o no textual.'
            elif (customer,inv) in existing:problem='Esta factura ya existe para ese cliente en los documentos originales. No se añade de nuevo ni se sustituye parcialmente.'
            elif d.get('currency')!='EUR':problem='Esta selección requiere EUR; no se convierten monedas.'
            try:
                issued=date.fromisoformat(d['issue_date']);quantity=Decimal(d['quantity']);net=Decimal(d['net_amount'])
                if issued.isoformat()>scoped[1] or not quantity.is_finite() or quantity<=0 or not net.is_finite() or net<0:problem='Revisa fecha al corte, cantidad positiva e importe neto no negativo.'
            except (KeyError,ValueError,TypeError,InvalidOperation):problem='Fecha, cantidad o neto no válidos.'
            signature=(customer,inv,Decimal(d['line_number'])) if d.get('line_number') is not None else _hash(d);header=(d.get('issue_date'),d.get('currency'));key=(customer,inv)
            if signature in seen:problem='Línea idéntica repetida. Revisa las partes seleccionadas; no se deduplica automáticamente.'
            if key in headers and headers[key]!=header:problem='Fecha o moneda contradictoria entre líneas de la misma factura y cliente.'
            seen.add(signature);headers[key]=header
            if problem:errors.append(dict(filename=meta['filename'],row=r.get('source_row'),article_id=sku,message=problem));continue
            ref=dict(document_ref='REC-'+bid,filename=meta['filename'],sheet=meta['sheet'],row=r['source_row'],batch_id=bid,source_sha256=meta['source_sha256'])
            entries.append(dict(unit_price_before_discount=d.get('unit_price_before_discount'),description=d.get('description'),discount_percent=d.get('discount_percent'),discount_amount=d.get('discount_amount'),vat_percent=d.get('vat_percent'),vat_amount=d.get('vat_amount'),article_id=sku,customer_id=customer,customer_name=parties[customer].get('legal_name',customer),invoice_number=inv,issue_date=d['issue_date'],quantity=str(quantity),unit=d['unit'],net_amount=str(net),currency='EUR',effective_net_unit_price=str(net/quantity),source_refs=[ref]))
    return entries,errors,fingerprints,files


def selected(c,dataset):
    previous=latest(c,dataset)
    if not previous or previous.get('cleared'):return previous,[],True
    try:
        entries,errors,fingerprints,_=validate(c,dataset,previous['batch_ids'])
        return previous,entries,not errors and fingerprints==previous['source_fingerprints']
    except ValueError:return previous,[],False


def history_status(c,dataset):
    previous,entries,intact=selected(c,dataset)
    if not previous:return None,[]
    if previous.get('cleared'):return dict(status='CLEARED',revision=previous['revision'],message='Selección retirada. Se conserva el historial documental original.'),[]
    status=dict(status='SELECTED' if intact else 'STALE',revision=previous['revision'],actor=previous['actor'],line_count=len(entries) if intact else None,decision_authority=False,message='Líneas de venta recibidas seleccionadas como referencias comerciales al corte; no acreditan cobro ni modifican existencias.' if intact else 'El historial de ventas seleccionado ha cambiado o es incompatible. No se ofrece un precio histórico por defecto hasta revisarlo o retirarlo.')
    return status,entries if intact else []


class SalesHistorySelection:
    def __init__(self,db,clock=monotonic):self.db=db;self.clock=clock;self.pending=None

    def preview(self,data):
        from eios.company_proposal_context import capture_context
        self.pending=None;dataset=data.get('dataset_id');ids=data.get('batch_ids')
        if not isinstance(ids,list) or not 1<=len(ids)<=100 or any(not isinstance(x,str) or len(x)!=64 for x in ids) or len(set(ids))!=len(ids):raise ValueError('Selecciona entre 1 y 100 archivos de líneas de venta distintos.')
        with sqlite3.connect(self.db) as c:
            ctx=capture_context(c,dataset)
            if data.get('context_fingerprint')!=ctx['fingerprint']:raise ValueError('La empresa o sus referencias han cambiado. Recarga antes de comprobar.')
            entries,errors,fingerprints,files=validate(c,dataset,ids)
            previous=latest(c,dataset)
        report=dict(dataset_id=dataset,company_name=ctx['company_name'],as_of_date=ctx['documentary_cutoff'],files=files,line_count=len(entries),error_count=len(errors),errors=errors[:100],sample=entries[:100],replaces_previous_selection=bool(previous and not previous.get('cleared')),decision_authority=False,ticket=None)
        if entries and not errors:
            report['ticket']=secrets.token_urlsafe(32);self.pending=dict(ticket=report['ticket'],dataset=dataset,context=ctx['fingerprint'],batch_ids=sorted(ids),source_fingerprints=fingerprints,at=self.clock())
        return report

    def commit(self,data):
        from eios.company_proposal_context import capture_context
        p=self.pending
        if not p or data.get('ticket')!=p['ticket'] or self.clock()-p['at']>600:raise ValueError('Comprueba de nuevo las ventas: la vista previa ha cambiado o caducado.')
        actor,reason=identity(data)
        if data.get('acknowledge_references') is not True:raise ValueError('Confirma la revisión de estas líneas y su alcance de referencia al corte.')
        with sqlite3.connect(self.db) as c:
            c.execute(SCHEMA);c.execute('BEGIN IMMEDIATE');ctx=capture_context(c,p['dataset'])
            if ctx['fingerprint']!=p['context']:raise ValueError('El contexto ha cambiado. Comprueba de nuevo.')
            _,errors,fps,_=validate(c,p['dataset'],p['batch_ids'])
            if errors or fps!=p['source_fingerprints']:raise ValueError('Los archivos o sus relaciones han cambiado. Comprueba de nuevo.')
            old=latest(c,p['dataset'])
            if old and not old.get('cleared') and old['batch_ids']==p['batch_ids'] and old['source_fingerprints']==fps:
                self.pending=None;return dict(status='UNCHANGED',dataset_id=p['dataset'])
            payload=dict(batch_ids=p['batch_ids'],source_fingerprints=fps,revision=(old['revision'] if old else 0)+1,actor=actor,reason=reason,created_at=datetime.now(timezone.utc).isoformat(),decision_authority=False,operational_path='FORBIDDEN')
            c.execute('INSERT INTO company_sales_history_selection VALUES(?,?,?)',(p['dataset'],payload['revision'],json.dumps(payload)))
        self.pending=None;return dict(status='SELECTED',dataset_id=p['dataset'],decision_authority=False)

    def clear(self,data):
        from eios.company_proposal_context import capture_context
        actor,reason=identity(data);dataset=data.get('dataset_id')
        with sqlite3.connect(self.db) as c:
            c.execute(SCHEMA);c.execute('BEGIN IMMEDIATE');ctx=capture_context(c,dataset)
            if ctx['fingerprint']!=data.get('context_fingerprint'):raise ValueError('El contexto ha cambiado. Recarga la pantalla.')
            old=latest(c,dataset)
            if not old or old.get('cleared'):raise ValueError('No hay historial recibido seleccionado que retirar.')
            payload=dict(revision=old['revision']+1,cleared=True,actor=actor,reason=reason,created_at=datetime.now(timezone.utc).isoformat())
            c.execute('INSERT INTO company_sales_history_selection VALUES(?,?,?)',(dataset,payload['revision'],json.dumps(payload)))
        self.pending=None;return dict(status='CLEARED',dataset_id=dataset,decision_authority=False)
