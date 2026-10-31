"""Display exact selected and evaluated source identities, without activating data."""
from contextlib import closing
import json
import sqlite3
from eios.company_exclusive_workbook import dataset_options


def source_status(db,dataset):
    with closing(sqlite3.connect(db)) as c:
        rows=c.execute('SELECT dataset_id,company_id,as_of_date FROM documentary_company_snapshot').fetchall()
        row=c.execute('SELECT manifest_json FROM documentary_company_snapshot WHERE dataset_id=?',(dataset,)).fetchone()
        if not row:raise ValueError('Versión documental no encontrada.')
        manifest=json.loads(row[0])
    versions=dataset_options(db,rows);selected=next(r for r in versions if r['dataset_id']==dataset)
    workbook=manifest.get('exclusive_workbook')
    mode='ACTIVE' if selected['active_workbook'] else 'HISTORICAL' if selected['historical'] else 'UNACTIVATED' if workbook else 'BASELINE'
    return dict(status=mode,dataset_id=dataset,version_id=dataset,company_id=manifest['company']['company_id'],legal_name=manifest['company'].get('legal_name'),as_of_date=manifest['as_of_date'],filename=workbook.get('filename') if workbook else None,source_sha256=workbook.get('source_sha256') if workbook else None,message={'ACTIVE':'Este es el Excel activo que se consulta para preparar propuestas.','HISTORICAL':'Versión histórica: no se utiliza para preparar propuestas nuevas. Selecciona el expediente activo.','UNACTIVATED':'Libro cargado, pero no activado como expediente de trabajo.','BASELINE':'Se consulta el expediente documental base. No hay un Excel exclusivo seleccionado en esta versión.'}[mode])


def mark_received(db,batches):
    active={}
    with closing(sqlite3.connect(db)) as c:
        if c.execute("SELECT 1 FROM sqlite_master WHERE name='company_active_workbook'").fetchone():
            for did,raw in c.execute('SELECT s.dataset_id,s.manifest_json FROM documentary_company_snapshot s JOIN company_active_workbook a ON a.dataset_id=s.dataset_id'):
                manifest=json.loads(raw);book=manifest.get('exclusive_workbook') or {}
                for bid in book.get('batch_ids',[]):active.setdefault(bid,[]).append(dict(dataset_id=did,filename=book.get('filename'),as_of_date=manifest['as_of_date'],legal_name=manifest['company'].get('legal_name')))
    return [dict(batch,workbook_usage='ACTIVE' if batch['batch_id'] in active else 'RECEIVED',active_workbooks=active.get(batch['batch_id'],[])) for batch in batches]
