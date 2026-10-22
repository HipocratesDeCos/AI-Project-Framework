"""Explicit, reversible historical SKU links. Original documentary rows stay intact."""
from copy import deepcopy
from datetime import datetime, timezone
import json
import sqlite3

from eios.company_proposal_context import capture_context, _hash

SCHEMA = '''CREATE TABLE IF NOT EXISTS company_sales_line_link (
 dataset_id TEXT NOT NULL,line_id TEXT NOT NULL,revision INTEGER NOT NULL,
 payload TEXT NOT NULL,PRIMARY KEY(dataset_id,line_id,revision))'''


def latest_links(connection, dataset):
    if not connection.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='company_sales_line_link'").fetchone():
        return {}
    return {line:json.loads(raw) for line,raw in connection.execute(
        'SELECT line_id,payload FROM company_sales_line_link WHERE dataset_id=? ORDER BY revision', (dataset,))}


def save_link(db, store, data):
    dataset=data.get('dataset_id');line_id=data.get('line_id')
    actor=data.get('actor');reason=data.get('reason')
    if any(not isinstance(v,str) or not v.strip() or len(v)>500 for v in (actor,reason)):
        raise ValueError('Indica responsable y motivo del vínculo (hasta 500 caracteres).')
    if not isinstance(line_id,str) or not line_id:
        raise ValueError('Selecciona una línea de venta.')
    with sqlite3.connect(db) as c:
        c.execute(SCHEMA);c.execute('BEGIN IMMEDIATE')
        context=capture_context(c,dataset)
        if context['material_nature']!='SYNTHETIC':
            raise ValueError('La vinculación está habilitada para el expediente sintético de pruebas.')
        if data.get('context_fingerprint')!=context['fingerprint']:
            raise ValueError('La documentación o sus vínculos han cambiado. Recarga la pantalla.')
        def record(kind, identity):
            row=c.execute('SELECT record_json FROM documentary_company_record WHERE dataset_id=? AND kind=? AND record_id=?',(dataset,kind,identity)).fetchone()
            if row is None:raise ValueError('Referencia documental no encontrada en esta versión.')
            return json.loads(row[0])
        line=record('sales_invoice_line',line_id)
        old=latest_links(c,dataset).get(line_id)
        revision=(old['revision'] if old else 0)+1
        article_id=data.get('article_id')
        payload=dict(line_id=line_id,revision=revision,actor=actor.strip(),reason=reason.strip(),
            created_at=datetime.now(timezone.utc).isoformat(),article_id=article_id,
            source_fingerprint=_hash(line),source_refs=deepcopy(line.get('source_refs',[])),
            origin='MANUAL_EXPLICIT_LINK',decision_authority=False,operational_path='FORBIDDEN')
        if article_id is not None:
            if not isinstance(article_id,str) or not article_id:
                raise ValueError('Selecciona un SKU válido.')
            matches=[json.loads(r[0]) for r in c.execute('SELECT record_json FROM documentary_company_record WHERE dataset_id=? AND kind=?',(dataset,'article'))]
            matches=[r for r in matches if r['data'].get('article_id')==article_id]
            if len(matches)!=1:raise ValueError('El SKU debe tener una referencia de catálogo única en esta versión.')
            article=matches[0]
            if line['data'].get('article_id') and line['data']['article_id']!=article_id:
                raise ValueError('La línea ya documenta otro SKU; no se sustituye mediante este vínculo.')
            unit=article['data'].get('unit_as_documented')
            original_unit=line['data'].get('unit_as_documented')
            if not unit or original_unit and original_unit!=unit:
                raise ValueError('La unidad documental no coincide con la del artículo.')
            if data.get('acknowledge_unit') is not True:
                raise ValueError('Confirma que la cantidad histórica está expresada en la unidad del artículo.')
            payload.update(unit=unit,article_fingerprint=_hash(article))
        elif not old or old.get('article_id') is None:
            raise ValueError('No hay un vínculo activo que retirar.')
        c.execute('INSERT INTO company_sales_line_link VALUES(?,?,?,?)',
            (dataset,line_id,revision,json.dumps(payload,ensure_ascii=False,allow_nan=False)))
    return payload


def apply_links(db, store, dataset, sales):
    """Apply only explicit links whose exact source and catalogue have not changed."""
    result=deepcopy(sales)
    with sqlite3.connect(db) as c:links=latest_links(c,dataset)
    if not links:return result
    originals={r['record_id']:r for r in store.records(dataset,'sales_invoice_line')}
    catalog=store.records(dataset,'article')
    articles={r['data']['article_id']:r for r in catalog if sum(x['data'].get('article_id')==r['data']['article_id'] for x in catalog)==1}
    for invoice in result['invoices']:
        for line in invoice['lines']:
            link=links.get(line['record_id'])
            if not link or link.get('article_id') is None:continue
            original=originals.get(line['record_id']);article=articles.get(link['article_id'])
            valid=original is not None and article is not None and _hash(original)==link['source_fingerprint'] and _hash(article)==link['article_fingerprint']
            line['manual_link']=dict(link,status='ACTIVE' if valid else 'STALE')
            if valid:
                line['article_id']=link['article_id'];line['unit']=link['unit']
            invoice['warnings'].append('Línea '+line['record_id']+': vínculo manual '+('activo' if valid else 'invalidado por cambio documental')+'. La factura original no se ha modificado.')
    return result
