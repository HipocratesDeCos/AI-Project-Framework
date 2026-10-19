"""Receipt coverage by company and cutoff, without inferring admission or completeness."""
import json
import sqlite3

from eios.company_tables import FIELDS, STOCK_PARAMETER_KEYS


def dossier_overviews(db):
    groups = {}
    with sqlite3.connect(db) as c:
        if not c.execute("SELECT 1 FROM sqlite_master WHERE name='received_company_batch' AND type='table'").fetchone():
            return []
        rows = c.execute('SELECT batch_id,metadata_json,records_json FROM received_company_batch ORDER BY batch_id')
        for batch_id, raw_metadata, raw_records in rows:
            meta, records = json.loads(raw_metadata), json.loads(raw_records)
            key = (meta['company_id'], meta['legal_name'], meta['material_nature'], meta['as_of_date'])
            if key not in groups:
                groups[key] = dict(company_id=key[0], legal_name=key[1], material_nature=key[2], as_of_date=key[3],
                    batch_ids=[], file_count=0, record_count=0,
                    categories={kind:dict(file_count=0, record_count=0, batch_ids=[]) for kind in FIELDS},
                    parameter_rows={field:0 for field in sorted(STOCK_PARAMETER_KEYS)},
                    source_warning_count=0, admission_status='PENDING', operational_path='FORBIDDEN', decision_authority=False)
            group = groups[key]
            group['batch_ids'].append(batch_id)
            group['file_count'] += 1
            group['record_count'] += len(records)
            group['source_warning_count'] += meta.get('warning_count', 0)
            category = group['categories'][meta['kind']]
            category['file_count'] += 1
            category['record_count'] += len(records)
            category['batch_ids'].append(batch_id)
            if meta['kind'] in ('inventory', 'stock_policy'):
                for record in records:
                    for field in STOCK_PARAMETER_KEYS:
                        if record['data'].get(field) is not None:
                            group['parameter_rows'][field] += 1
    result = []
    for key in sorted(groups):
        group = groups[key]
        for kind, category in group['categories'].items():
            category['status'] = ('SUPPORT_ONLY' if kind == 'document' else 'RECEIVED_ROWS' if category['record_count'] else 'EMPTY_FILE') if category['file_count'] else 'NO_FILES'
        group['missing_categories'] = [kind for kind, category in group['categories'].items() if not category['file_count']]
        group['scope'] = 'Archivos recibidos individualmente. Los recuentos son filas guardadas, no entidades únicas ni prueba de integridad del expediente. Los paquetes ZIP de la empresa activa se consultan en Inicio.'
        result.append(group)
    return result
