"""Source-preserving company reception, isolated from admitted decision datasets."""
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import PurePosixPath
import re
import secrets
import sqlite3
from time import monotonic

from eios.company_tables import read_table, normalize, source_date, FIELDS

TTL = 600


def canonical(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)


class CompanyReception:
    def __init__(self, db, clock=monotonic):
        self.db=db
        self.clock=clock
        self.file=None
        self.checked=None

    def read(self, content, filename, **options):
        self.file=None;self.checked=None
        filename=PurePosixPath(filename.replace('\\','/')).name[:200]
        try:
            table=read_table(content,filename,**options)
        except Exception as error:
            # Untrusted file parsing has no database side effects. Convert parser
            # failures into a visible rejection rather than a dropped request.
            raise ValueError('No se puede leer el archivo: '+str(error)[:300]) from None
        upload=secrets.token_urlsafe(32)
        self.file=dict(upload=upload,content=bytes(content),filename=filename,table=deepcopy(table),at=self.clock())
        return dict(upload=upload,filename=filename,format=table['format'],sheets=table['sheets'],sheet=table['sheet'],
                    headers=table['headers'],sample=table['rows'][:5],rows=len(table['rows']),
                    fields={kind:[dict(key=k,label=label,required=required) for k,label,required in fields] for kind,fields in FIELDS.items()})

    def preview(self, data):
        self.checked=None
        if not isinstance(data,dict): raise ValueError('Datos de revisión no válidos.')
        file=self.file
        if not file or data.get('upload')!=file['upload'] or self.clock()-file['at']>TTL:
            raise ValueError('El archivo ha cambiado o ha caducado. Vuelve a leerlo.')
        if not isinstance(data.get('company_id'),str) or not isinstance(data.get('legal_name'),str):
            raise ValueError('El código y la razón social deben ser texto.')
        company_id=data['company_id'].strip()
        legal_name=data['legal_name'].strip()
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,79}',company_id):
            raise ValueError('Indica un código de empresa de hasta 80 letras, números, puntos o guiones.')
        if not legal_name or len(legal_name)>200: raise ValueError('Indica la razón social, hasta 200 caracteres.')
        material=data.get('material_nature')
        if material not in ('REAL','SYNTHETIC'): raise ValueError('Indica si los datos son reales o sintéticos.')
        cutoff=source_date(data.get('as_of_date',''))
        kind=data.get('kind')
        convention=data.get('number_format')
        if convention not in ('ES','EN'): raise ValueError('Selecciona el formato numérico.')
        if file['table']['format']=='pdf':
            if kind!='document': raise ValueError('El PDF se conserva como documento de soporte; no se extraen cifras automáticamente.')
            result=dict(records=[],errors=[],error_count=0,warnings=['PDF conservado como soporte. Sus cifras aún no se han extraído ni verificado.'])
        else:
            result=normalize(file['table'],kind,data.get('mapping'),cutoff,convention)
        report=dict(company_id=company_id,legal_name=legal_name,material_nature=material,as_of_date=cutoff,
                    kind=kind,filename=file['filename'],source_sha256=sha256(file['content']).hexdigest(),
                    sheet=file['table']['sheet'],header_row=file['table']['header_row'],mapping=data.get('mapping',{}),
                    number_format=convention,rows=len(file['table']['rows']),record_count=len(result['records']),
                    preview=result['records'][:20],errors=result['errors'][:100],error_count=result['error_count'],
                    warnings=result['warnings'][:100],warning_count=len(result['warnings']),
                    admission_status='PENDING',operational_path='FORBIDDEN',decision_authority=False)
        if not result['errors']:
            ticket=secrets.token_urlsafe(32)
            self.checked=dict(ticket=ticket,report=deepcopy(report),records=deepcopy(result['records']),content=file['content'],at=self.clock())
            return dict(report,ticket=ticket)
        return dict(report,ticket=None)

    def commit(self, ticket):
        checked=self.checked
        if not checked or not isinstance(ticket,str) or not secrets.compare_digest(ticket,checked['ticket']):
            raise ValueError('Revisa y valida de nuevo los datos antes de guardarlos.')
        if self.clock()-checked['at']>TTL:
            self.checked=None
            raise ValueError('La revisión ha caducado. Vuelve a comprobar los datos.')
        report=dict(checked['report'])
        identity=dict(report)
        identity.pop('preview');identity.pop('errors');identity.pop('warnings')
        batch=sha256(canonical(dict(metadata=identity,records=checked['records'])).encode()).hexdigest()
        received=datetime.now(timezone.utc).isoformat()
        with sqlite3.connect(self.db) as c:
            c.execute('PRAGMA foreign_keys=ON')
            c.executescript('''CREATE TABLE IF NOT EXISTS received_company (
                company_id TEXT PRIMARY KEY, legal_name TEXT NOT NULL, material_nature TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS received_company_batch (
                batch_id TEXT PRIMARY KEY, company_id TEXT NOT NULL REFERENCES received_company(company_id),
                received_at TEXT NOT NULL, metadata_json TEXT NOT NULL, content BLOB NOT NULL, records_json TEXT NOT NULL);''')
            existing=c.execute('SELECT legal_name,material_nature FROM received_company WHERE company_id=?',(report['company_id'],)).fetchone()
            if existing and existing!=(report['legal_name'],report['material_nature']):
                raise ValueError('Ese código ya identifica otra razón social o naturaleza de datos. Revisa el código de empresa.')
            duplicate=c.execute('SELECT 1 FROM received_company_batch WHERE batch_id=?',(batch,)).fetchone()
            if not duplicate:
                c.execute('INSERT OR IGNORE INTO received_company VALUES(?,?,?)',(report['company_id'],report['legal_name'],report['material_nature']))
                c.execute('INSERT INTO received_company_batch VALUES(?,?,?,?,?,?)',(batch,report['company_id'],received,canonical(report),checked['content'],canonical(checked['records'])))
        self.checked=None
        return dict(status='UNCHANGED' if duplicate else 'RECEIVED',batch_id=batch,company_id=report['company_id'],admission_status='PENDING',operational_path='FORBIDDEN',decision_authority=False)

    def batches(self):
        with sqlite3.connect(self.db) as c:
            if not c.execute("SELECT 1 FROM sqlite_master WHERE name='received_company_batch' AND type='table'").fetchone(): return []
            rows=c.execute('SELECT batch_id,received_at,metadata_json FROM received_company_batch ORDER BY received_at DESC,batch_id').fetchall()
        return [dict(json.loads(raw),batch_id=batch,received_at=when,fields=[dict(key=k,label=label) for k,label,_ in FIELDS[json.loads(raw)['kind']]]) for batch,when,raw in rows]
