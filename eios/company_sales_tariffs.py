"""Source-bound tariff selection, without promoting received files to admitted evidence."""
from copy import deepcopy
from datetime import date, datetime, timezone
from decimal import Decimal
from hashlib import sha256
import json
import sqlite3

from eios.company_proposal_context import _hash, capture_context

SCHEMA='''CREATE TABLE IF NOT EXISTS company_sales_tariff (
 dataset_id TEXT NOT NULL,article_id TEXT NOT NULL,revision INTEGER NOT NULL,
 payload TEXT NOT NULL,PRIMARY KEY(dataset_id,article_id,revision))'''


def latest(c,dataset):
    if not c.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='company_sales_tariff'").fetchone():return {}
    return {sku:json.loads(raw) for sku,raw in c.execute('SELECT article_id,payload FROM company_sales_tariff WHERE dataset_id=? ORDER BY revision',(dataset,))}


def batch(c,identity):
    if not c.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='received_company_batch'").fetchone():return None
    row=c.execute('SELECT metadata_json,records_json,content FROM received_company_batch WHERE batch_id=?',(identity,)).fetchone()
    if not row:return None
    meta,records=json.loads(row[0]),json.loads(row[1]);digest=sha256(bytes(row[2])).hexdigest()
    return meta,records,_hash(dict(metadata=meta,records=records,bytes_sha256=digest)),digest==meta.get('source_sha256')


def context(c,dataset):
    result={}
    for sku,link in latest(c,dataset).items():
        source=batch(c,link['batch_id']) if link.get('batch_id') else None
        result[sku]=dict(binding=_hash(link),source=source[2] if source else None)
    return result


def candidates(c,documentary,article):
    if not c.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='received_company_batch'").fetchone():return []
    result=[]
    for (bid,) in c.execute('SELECT batch_id FROM received_company_batch WHERE company_id=? ORDER BY batch_id',(documentary['company_id'],)).fetchall():
        loaded=batch(c,bid)
        meta,records,fingerprint,intact=loaded
        if not intact or meta.get('kind')!='sale_price':continue
        if (meta.get('company_id'),meta.get('legal_name'),meta.get('material_nature'),meta.get('as_of_date'))!=(documentary['company_id'],documentary['company_name'],documentary['material_nature'],documentary['documentary_cutoff']):continue
        for row in records:
            data=row['data']
            if row.get('kind')!='sale_price' or data.get('article_id')!=article['article_id'] or data.get('unit')!=article['unit_as_documented'] or data.get('currency')!='EUR':continue
            try:
                price=Decimal(data['recommended_sale_price'])
                start,end=date.fromisoformat(data['valid_from']),date.fromisoformat(data['valid_until'])
                if not price.is_finite() or price<0 or end<start:continue
            except (ValueError,TypeError,KeyError,ArithmeticError):continue
            result.append(dict(batch_id=bid,source_row=row['source_row'],filename=meta['filename'],sheet=meta['sheet'],
                source_sha256=meta['source_sha256'],source_fingerprint=fingerprint,price=str(price),unit=data['unit'],currency='EUR',
                valid_from=start.isoformat(),valid_until=end.isoformat(),admission_status='PENDING'))
    return result


def save_tariff(db,data):
    actor,reason=data.get('actor'),data.get('reason')
    if any(not isinstance(v,str) or not v.strip() or len(v)>500 for v in (actor,reason)):
        raise ValueError('Indica responsable y motivo de la selección (hasta 500 caracteres).')
    dataset,sku=data.get('dataset_id'),data.get('article_id')
    if not isinstance(sku,str) or not sku:raise ValueError('Selecciona un artículo.')
    with sqlite3.connect(db) as c:
        c.execute(SCHEMA);c.execute('BEGIN IMMEDIATE');documentary=capture_context(c,dataset)
        if documentary['material_nature']!='SYNTHETIC':raise ValueError('Esta selección está habilitada para el expediente sintético de pruebas.')
        if data.get('context_fingerprint')!=documentary['fingerprint']:raise ValueError('El expediente o la tarifa han cambiado. Recarga la pantalla.')
        articles=[json.loads(r[0]) for r in c.execute("SELECT record_json FROM documentary_company_record WHERE dataset_id=? AND kind='article'",(dataset,))]
        articles=[r for r in articles if r['data'].get('article_id')==sku]
        if len(articles)!=1:raise ValueError('El SKU debe tener un catálogo único en esta versión.')
        article=articles[0];old=latest(c,dataset).get(sku);selection=None
        if data.get('clear') is True:
            if not old or old.get('selection') is None:raise ValueError('No hay una tarifa seleccionada que retirar.')
        else:
            if data.get('acknowledge_net_unit') is not True:raise ValueError('Confirma que el PVP es por unidad y sin IVA.')
            selection=next((r for r in candidates(c,documentary,article['data']) if r['batch_id']==data.get('batch_id') and type(data.get('source_row')) is int and r['source_row']==data['source_row']),None)
            if selection is None:raise ValueError('Selecciona una fila de tarifa compatible de esta empresa, corte, SKU, unidad y moneda.')
            if data.get('source_fingerprint')!=selection['source_fingerprint']:raise ValueError('La fila de tarifa ha cambiado desde su consulta. Vuelve a revisarla.')
        payload=dict(article_id=sku,revision=(old['revision'] if old else 0)+1,selection=selection,
            batch_id=selection['batch_id'] if selection else None,article_fingerprint=_hash(article),
            actor=actor.strip(),reason=reason.strip(),created_at=datetime.now(timezone.utc).isoformat(),
            origin='EXPLICIT_RECEIVED_TARIFF_SELECTION',admission_status='PENDING',decision_authority=False,operational_path='FORBIDDEN')
        c.execute('INSERT INTO company_sales_tariff VALUES(?,?,?,?)',(dataset,sku,payload['revision'],json.dumps(payload,ensure_ascii=False,allow_nan=False)))
        reply=dict(payload,context_fingerprint=capture_context(c,dataset)['fingerprint'])
    return reply


def apply_tariffs(db,store,dataset,articles):
    result=deepcopy(articles)
    originals=store.records(dataset,'article')
    with sqlite3.connect(db) as c:
        links=latest(c,dataset)
        for article in result:
            link=links.get(article['article_id'])
            if not link or link['selection'] is None:continue
            source=batch(c,link['batch_id'])
            original=[r for r in originals if r['data'].get('article_id')==article['article_id']]
            valid=source is not None and source[3] and source[2]==link['selection']['source_fingerprint'] and len(original)==1 and _hash(original[0])==link['article_fingerprint']
            article['received_sale_tariff']=dict(link,status='ACTIVE' if valid else 'STALE')
    return result
