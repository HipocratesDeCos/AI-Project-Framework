"""Documentary content binding, without source admission or analytical execution."""
from hashlib import sha256
import json


def _hash(value):
    return sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                             separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def capture_context(connection, dataset):
    """Capture one SQLite read transaction; hashes identify content, not trust."""
    row = connection.execute('SELECT company_id,as_of_date,manifest_json FROM documentary_company_snapshot WHERE dataset_id=?', (dataset,)).fetchone()
    if row is None:
        raise ValueError('Versión documental no encontrada.')
    company, cutoff, manifest_json = row
    manifest = json.loads(manifest_json)
    if manifest['company']['company_id'] != company or manifest['as_of_date'] != cutoff:
        raise ValueError('Identidad o corte documental contradictorio.')
    records = [dict(kind=k, record_id=i, fingerprint=_hash(json.loads(raw))) for k,i,raw in
               connection.execute('SELECT kind,record_id,record_json FROM documentary_company_record WHERE dataset_id=? ORDER BY kind,record_id', (dataset,))]
    cursor = connection.execute('SELECT * FROM documentary_source WHERE dataset_id=?', (dataset,))
    columns = [item[0] for item in cursor.description]
    sources = []
    for values in cursor:
        source = dict(zip(columns, values))
        source.pop('dataset_id', None)
        content = source.pop('content', None)
        if content is not None:
            source['stored_bytes_sha256'] = sha256(content).hexdigest()
        if 'metadata_json' in source:
            source['metadata'] = json.loads(source.pop('metadata_json'))
        sources.append(source)
    sources.sort(key=lambda s: json.dumps(s, sort_keys=True))
    result = dict(schema='COMPANY-PROPOSAL-DOCUMENTARY-CONTEXT-01',
                  dataset_id=dataset, company_id=company,
                  company_name=manifest['company'].get('legal_name', company),
                  documentary_cutoff=cutoff, manifest_fingerprint=_hash(manifest),
                  material_nature=manifest.get('material_nature', 'NOT_DECLARED'),
                  records=records, sources=sources,
                  scope='DOCUMENTARY_CONTENT_ONLY', decision_authority=False)
    result['fingerprint'] = _hash(result)
    return result
