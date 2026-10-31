"""Explicit received-inventory references for a synthetic documentary company."""
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import json
import sqlite3
from hashlib import sha256
from time import monotonic
import secrets

from eios.company_proposal_context import _hash

SOURCE='RECEIVED-INVENTORY-SELECTION-01'
SCHEMA='''CREATE TABLE IF NOT EXISTS company_inventory_selection (
 dataset_id TEXT NOT NULL,revision INTEGER NOT NULL,payload TEXT NOT NULL,
 PRIMARY KEY(dataset_id,revision))'''


def latest(c,dataset):
    if not c.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='company_inventory_selection'").fetchone():return None
    row=c.execute('SELECT payload FROM company_inventory_selection WHERE dataset_id=? ORDER BY revision DESC LIMIT 1',(dataset,)).fetchone()
    return json.loads(row[0]) if row else None


def source(c,batch_id):
    if not c.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='received_company_batch'").fetchone():raise ValueError('No hay inventarios recibidos.')
    row=c.execute('SELECT metadata_json,records_json,content FROM received_company_batch WHERE batch_id=?',(batch_id,)).fetchone()
    if not row:raise ValueError('Algún inventario ya no está disponible.')
    meta,records=json.loads(row[0]),json.loads(row[1]);digest=sha256(bytes(row[2])).hexdigest()
    return meta,records,_hash(dict(metadata=meta,records=records,source_sha256=digest)),digest==meta.get('source_sha256')


def selection_context(c,dataset):
    selected=latest(c,dataset)
    if not selected:return None
    sources={}
    for bid in selected.get('batch_ids',[]):
        try:
            meta,rows,fingerprint,intact=source(c,bid)
            sources[bid]=dict(fingerprint=fingerprint,intact=intact)
        except ValueError:sources[bid]=dict(fingerprint=None,intact=False)
    return dict(revision=selected['revision'],selection_fingerprint=_hash(selected),sources=sources,cleared=selected.get('cleared',False))


def selected_rows(c,dataset):
    selected=latest(c,dataset)
    if not selected or selected.get('cleared'):return selected,[],True
    scope=c.execute('SELECT company_id,as_of_date,manifest_json FROM documentary_company_snapshot WHERE dataset_id=?',(dataset,)).fetchone()
    if not scope:return selected,[],False
    manifest=json.loads(scope[2]);rows=[]
    if manifest.get('material_nature')!='SYNTHETIC':return selected,[],False
    for bid in selected['batch_ids']:
        try:meta,records,fingerprint,intact=source(c,bid)
        except ValueError:return selected,[],False
        if not intact or fingerprint!=selected['source_fingerprints'][bid] or meta.get('kind')!='inventory' or (meta.get('company_id'),meta.get('legal_name'),meta.get('material_nature'),meta.get('as_of_date'))!=(scope[0],manifest['company'].get('legal_name'), 'SYNTHETIC',scope[1]):return selected,[],False
        rows.extend(dict(data=r['data'],source_row=r['source_row'],batch_id=bid,filename=meta['filename'],sheet=meta['sheet'],source_sha256=meta['source_sha256']) for r in records)
    return selected,rows,True


def inventory_status(c,dataset):
    selected,rows,intact=selected_rows(c,dataset)
    if not selected:return None
    return dict(revision=selected['revision'],status='CLEARED' if selected.get('cleared') else 'SELECTED' if intact else 'STALE',
        article_count=len(rows) if intact else None,batch_ids=selected.get('batch_ids',[]),actor=selected['actor'],reason=selected['reason'],decision_authority=False,
        message='Selección retirada; se recuperan las referencias anteriores.' if selected.get('cleared') else 'Inventario recibido seleccionado. Solo referencias al corte; no acredita admisión ni stock actual.' if intact else 'El origen seleccionado ha cambiado o no está disponible. No se muestran existencias de esta selección ni se recuperan automáticamente cifras anteriores.')


def apply_inventory(c,dataset,baseline):
    selected,rows,intact=selected_rows(c,dataset)
    if not selected or selected.get('cleared'):return baseline
    if not intact:return {} # Fail closed; never silently restore an older quantity.
    result=dict(baseline)
    for row in rows:
        d=row['data'];physical=Decimal(d['physical']);reserved=None if d.get('reserved') is None else Decimal(d['reserved'])
        result[d['article_id']]=dict(dataset_id=dataset,article_id=d['article_id'],unit=d['unit'],as_of_date=d['as_of_date'],physical=str(physical),reserved=None if reserved is None else str(reserved),available=None if reserved is None else str(physical-reserved),
            source=SOURCE,source_ref={key:row[key] for key in ('batch_id','filename','sheet','source_row','source_sha256')},selection_revision=selected['revision'],material_nature='SYNTHETIC',basis='EXPLICIT_RECEIVED_SELECTION',accounting_reconciliation='NOT_RECONCILED',demand_forecast=None,safety_stock=None,decision_authority=False,operational_path='FORBIDDEN')
    return result


class InventorySelection:
    def __init__(self,db,clock=monotonic):self.db=db;self.clock=clock;self.pending=None

    def preview(self,data):
        from eios.company_proposal_context import capture_context
        from eios.company_commercial_catalogue import apply_catalogue
        from eios.company_inventory import read_inventory
        self.pending=None;dataset=data.get('dataset_id');ids=data.get('batch_ids')
        if not isinstance(ids,list) or not 1<=len(ids)<=100 or any(not isinstance(i,str) or len(i)!=64 for i in ids) or len(set(ids))!=len(ids):raise ValueError('Selecciona entre 1 y 100 archivos de inventario distintos.')
        with sqlite3.connect(self.db) as c:
            ctx=capture_context(c,dataset)
            if ctx['material_nature']!='SYNTHETIC':raise ValueError('La selección está habilitada solo para empresas ficticias.')
            if data.get('context_fingerprint')!=ctx['fingerprint']:raise ValueError('La empresa o sus referencias han cambiado. Recarga antes de comprobar.')
            articles=[json.loads(r[0])['data'] for r in c.execute("SELECT record_json FROM documentary_company_record WHERE dataset_id=? AND kind='article'",(dataset,))]
            suppliers=[json.loads(r[0])['data'] for r in c.execute("SELECT record_json FROM documentary_company_record WHERE dataset_id=? AND kind='supplier'",(dataset,))]
            articles,_,_=apply_catalogue(c,dataset,articles,suppliers);catalogue={a['article_id']:a for a in articles}
            rows=[];fingerprints={};seen=set();errors=[];files=[];unknown=0;total_rows=0
            for bid in sorted(ids):
                meta,records,fp,intact=source(c,bid)
                from eios.company_exclusive_workbook import allowed
                if not allowed(c,dataset,meta,bid):raise ValueError('El inventario no pertenece al Excel activo.')
                if not intact:raise ValueError('La integridad de un archivo no coincide.')
                if (meta.get('kind'),meta.get('company_id'),meta.get('legal_name'),meta.get('material_nature'),meta.get('as_of_date'))!=('inventory',ctx['company_id'],ctx['company_name'],'SYNTHETIC',ctx['documentary_cutoff']):raise ValueError('Usa solo inventarios de la misma empresa ficticia, razón social y fecha de corte activas.')
                total_rows+=len(records)
                if total_rows>20000:raise ValueError('Selecciona como máximo 20.000 filas de inventario entre todos los archivos.')
                fingerprints[bid]=fp;files.append(meta['filename'])
                for r in records:
                    d=r.get('data',{});sku=d.get('article_id');issue=None
                    if r.get('kind')!='inventory' or not isinstance(sku,str) or sku not in catalogue:issue='SKU sin ficha en el catálogo activo.'
                    elif sku in seen:issue='SKU repetido entre los inventarios seleccionados. No se suman almacenes automáticamente.'
                    elif d.get('unit')!=catalogue[sku].get('unit_as_documented'):issue='Unidad distinta de la ficha activa.'
                    elif d.get('as_of_date')!=ctx['documentary_cutoff']:issue='Fecha de inventario distinta del corte activo.'
                    try:
                        p=Decimal(d['physical']);q=None if d.get('reserved') is None else Decimal(d['reserved'])
                        if not p.is_finite() or p<0 or (q is not None and (not q.is_finite() or q<0)):issue='Físico y reservado deben ser finitos y no negativos.'
                    except (KeyError,InvalidOperation,TypeError,ValueError):issue='Revisa las cantidades del inventario.'
                    if issue:errors.append(dict(filename=meta['filename'],row=r.get('source_row'),article_id=sku,message=issue));continue
                    seen.add(sku);unknown+=q is None
                    rows.append(dict(article_id=sku,physical=str(p),reserved=None if q is None else str(q),available=None if q is None else str(p-q),unit=d['unit'],filename=meta['filename'],source_row=r['source_row']))
        current=read_inventory(self.db,dataset)
        for row in rows:
            old=current.get(row['article_id'])
            row['previous_physical']=old.get('physical') if old else None;row['previous_reserved']=old.get('reserved') if old else None;row['previous_available']=old.get('available') if old else None
        with sqlite3.connect(self.db) as c:
            previous,prior_rows,_=selected_rows(c,dataset)
        reverted=len({r['data']['article_id'] for r in prior_rows}-seen)
        report=dict(reverted_articles=reverted,dataset_id=dataset,company_name=ctx['company_name'],as_of_date=ctx['documentary_cutoff'],files=files,article_count=len(rows),unknown_reservations=unknown,error_count=len(errors),errors=errors[:100],sample=rows[:100],sample_count=min(100,len(rows)),replaces_previous_selection=bool(previous and not previous.get('cleared')),scope='DATED_RECEIVED_INVENTORY_REFERENCES_ONLY',decision_authority=False,ticket=None)
        if rows and not errors:
            ticket=secrets.token_urlsafe(32);report['ticket']=ticket
            self.pending=dict(ticket=ticket,dataset=dataset,context=ctx['fingerprint'],batch_ids=sorted(ids),source_fingerprints=fingerprints,at=self.clock())
        return report

    def commit(self,data):
        from eios.company_proposal_context import capture_context
        p=self.pending
        if not p or data.get('ticket')!=p['ticket'] or self.clock()-p['at']>600:raise ValueError('Vuelve a comprobar los inventarios: la vista previa ha cambiado o caducado.')
        actor,reason=identity(data)
        if data.get('acknowledge_dated_reference') is not True:raise ValueError('Confirma que revisas referencias al corte, sin activar reglas ni acreditar stock actual.')
        with sqlite3.connect(self.db) as c:
            c.execute(SCHEMA);c.execute('BEGIN IMMEDIATE');ctx=capture_context(c,p['dataset'])
            if ctx['fingerprint']!=p['context']:raise ValueError('El contexto o un origen ha cambiado. Vuelve a comprobar los inventarios.')
            for bid,fp in p['source_fingerprints'].items():
                _,_,current,intact=source(c,bid)
                if not intact or current!=fp:raise ValueError('Un inventario ha cambiado desde su comprobación.')
            previous=latest(c,p['dataset'])
            if previous and not previous.get('cleared') and previous['batch_ids']==p['batch_ids'] and previous['source_fingerprints']==p['source_fingerprints']:
                self.pending=None;return dict(status='UNCHANGED',dataset_id=p['dataset'])
            payload=dict(batch_ids=p['batch_ids'],source_fingerprints=p['source_fingerprints'],revision=(previous['revision'] if previous else 0)+1,actor=actor,reason=reason,created_at=datetime.now(timezone.utc).isoformat(),decision_authority=False,operational_path='FORBIDDEN')
            c.execute('INSERT INTO company_inventory_selection VALUES(?,?,?)',(p['dataset'],payload['revision'],json.dumps(payload)))
        self.pending=None;return dict(status='SELECTED',dataset_id=p['dataset'],revision=payload['revision'],decision_authority=False)

    def clear(self,data):
        from eios.company_proposal_context import capture_context
        actor,reason=identity(data);dataset=data.get('dataset_id')
        with sqlite3.connect(self.db) as c:
            c.execute(SCHEMA);c.execute('BEGIN IMMEDIATE');ctx=capture_context(c,dataset)
            if ctx['fingerprint']!=data.get('context_fingerprint'):raise ValueError('El contexto ha cambiado. Recarga la pantalla.')
            previous=latest(c,dataset)
            if not previous or previous.get('cleared'):raise ValueError('No hay una selección de inventario que retirar.')
            payload=dict(revision=previous['revision']+1,cleared=True,actor=actor,reason=reason,created_at=datetime.now(timezone.utc).isoformat())
            c.execute('INSERT INTO company_inventory_selection VALUES(?,?,?)',(dataset,payload['revision'],json.dumps(payload)))
        self.pending=None;return dict(status='CLEARED',dataset_id=dataset,decision_authority=False)


def identity(data):
    values=[data.get('actor'),data.get('reason')]
    if any(not isinstance(v,str) or not v.strip() or len(v)>500 for v in values):raise ValueError('Indica responsable y motivo, hasta 500 caracteres.')
    return tuple(v.strip() for v in values)

