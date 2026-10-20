"""Immutable named selections and reference-check snapshots; never an admission."""
from datetime import datetime, timezone
from hashlib import sha256
import json
import sqlite3

from eios.company_dossier import selected_batches, check_dossier
from eios.company_reception import canonical

SCHEMA = 'EIOS-RECEIVED-DOSSIER-01/v0.1'


def save_version(db, batch_ids, name):
    if not isinstance(name, str) or not 1 <= len(name.strip()) <= 120 or any(ord(ch) < 32 for ch in name):
        raise ValueError('Indica un nombre de versión de 1 a 120 caracteres, sin saltos de línea.')
    name = name.strip()
    batches = selected_batches(db, batch_ids)
    meta = batches[0][1]
    manifest = {key:meta[key] for key in ('company_id','legal_name','material_nature','as_of_date')}
    manifest.update(schema=SCHEMA, batch_ids=sorted(batch_ids),
        files=[dict(batch_id=bid,filename=m['filename'],sheet=m['sheet'],kind=m['kind'],source_sha256=m['source_sha256']) for bid,m,_ in batches],
        admission_status='PENDING', operational_path='FORBIDDEN', decision_authority=False)
    check = check_dossier(db, batch_ids)
    check['check_schema'] = 'EIOS-RECEIVED-REFERENCE-CHECK-01/v0.1'
    manifest['check_sha256'] = sha256(canonical(check).encode()).hexdigest()
    dossier_id = sha256(canonical(manifest).encode()).hexdigest()
    created = datetime.now(timezone.utc).isoformat()
    with sqlite3.connect(db) as c:
        c.execute('''CREATE TABLE IF NOT EXISTS received_company_dossier (
            dossier_id TEXT PRIMARY KEY, company_id TEXT NOT NULL, as_of_date TEXT NOT NULL,
            name TEXT NOT NULL, created_at TEXT NOT NULL, manifest_json TEXT NOT NULL, check_json TEXT NOT NULL,
            UNIQUE(company_id,as_of_date,name))''')
        c.execute('BEGIN IMMEDIATE')
        existing_name = c.execute('SELECT dossier_id FROM received_company_dossier WHERE company_id=? AND as_of_date=? AND name=?',(meta['company_id'],meta['as_of_date'],name)).fetchone()
        if existing_name and existing_name[0] != dossier_id:
            raise ValueError('Ese nombre ya identifica otra selección de archivos. Usa un nombre de versión distinto.')
        existing = c.execute('SELECT name,created_at FROM received_company_dossier WHERE dossier_id=?',(dossier_id,)).fetchone()
        if existing:
            return dict(status='UNCHANGED', dossier_id=dossier_id, name=existing[0], created_at=existing[1], admission_status='PENDING', operational_path='FORBIDDEN', decision_authority=False)
        c.execute('INSERT INTO received_company_dossier VALUES(?,?,?,?,?,?,?)',(dossier_id,meta['company_id'],meta['as_of_date'],name,created,canonical(manifest),canonical(check)))
    return dict(status='SAVED',dossier_id=dossier_id,name=name,created_at=created,admission_status='PENDING',operational_path='FORBIDDEN',decision_authority=False)


def versions(db):
    with sqlite3.connect(db) as c:
        if not c.execute("SELECT 1 FROM sqlite_master WHERE name='received_company_dossier' AND type='table'").fetchone():
            return []
        rows = c.execute('SELECT dossier_id,name,created_at,manifest_json,check_json FROM received_company_dossier ORDER BY created_at DESC,dossier_id').fetchall()
    result = []
    for identifier,name,created,raw,check_raw in rows:
        manifest, check = json.loads(raw), json.loads(check_raw)
        result.append(dict(dossier_id=identifier,name=name,created_at=created,company_id=manifest['company_id'],legal_name=manifest['legal_name'],material_nature=manifest['material_nature'],as_of_date=manifest['as_of_date'],file_count=len(manifest['batch_ids']),issue_count=check['issue_count'],admission_status='PENDING',operational_path='FORBIDDEN',decision_authority=False))
    return result


def version(db, dossier_id):
    if not isinstance(dossier_id, str) or len(dossier_id) != 64:
        raise ValueError('Identificación de versión no válida.')
    with sqlite3.connect(db) as c:
        if not c.execute("SELECT 1 FROM sqlite_master WHERE name='received_company_dossier' AND type='table'").fetchone():
            raise ValueError('Versión no disponible.')
        row = c.execute('SELECT name,created_at,manifest_json,check_json FROM received_company_dossier WHERE dossier_id=?',(dossier_id,)).fetchone()
    if not row:
        raise ValueError('Versión no disponible.')
    manifest = json.loads(row[2])
    if sha256(canonical(manifest).encode()).hexdigest() != dossier_id:
        raise ValueError('La integridad de la versión no coincide.')
    if sha256(canonical(json.loads(row[3])).encode()).hexdigest() != manifest['check_sha256']:
        raise ValueError('La integridad de la comprobación guardada no coincide.')
    selected_batches(db, manifest['batch_ids'])
    return dict(dossier_id=dossier_id,name=row[0],created_at=row[1],manifest=manifest,check=json.loads(row[3]))
