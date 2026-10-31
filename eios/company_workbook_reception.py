from contextlib import closing
"""Atomic reception of explicitly mapped workbook sheets; never admission."""
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
import json
import secrets
import sqlite3
import tempfile
from time import monotonic

from eios.company_reception import CompanyReception, canonical, TTL
from eios.company_tables import read_table, FIELDS
from eios.company_dossier import check_dossier

GUIDE = '97_Guia_Carga'
HEADERS = ['Hoja', 'Tipo EIOS', 'Campo EIOS', 'Columna del archivo']


def signature(records):
    return canonical(sorted((canonical(dict(kind=r['kind'], data=r['data'])) for r in records)))


def keys(kind, records):
    fields = {'supplier': ('supplier_id',), 'customer': ('customer_id',),
              'article': ('article_id',), 'inventory': ('article_id', 'unit'),
              'stock_policy': ('article_id', 'unit'), 'balance': ('account_code', 'currency'),
              'cash_flow': ('flow_id',), 'sales_installment': ('installment_ref',),
              'sale_price': ('article_id', 'unit'), 'price_reference': ('article_id','unit'),
              'sales_line': ('customer_id', 'invoice_number'),
              'purchase_line': ('supplier_id', 'invoice_number')}[kind]
    return {tuple(r['data'].get(f) for f in fields) for r in records}


def existing(connection, company):
    if not connection.execute("SELECT 1 FROM sqlite_master WHERE name='received_company_batch'").fetchone():
        return []
    return [(bid, json.loads(meta), json.loads(rows)) for bid, meta, rows in connection.execute(
        'SELECT batch_id,metadata_json,records_json FROM received_company_batch WHERE company_id=? ORDER BY batch_id', (company,))]


def compare(incoming, previous):
    results = []
    for bid, meta, records in incoming:
        same = []; overlaps = []
        for old_id, old_meta, old_records in previous:
            if (meta['legal_name'], meta['material_nature']) != (old_meta['legal_name'], old_meta['material_nature']):
                raise ValueError('El código de empresa ya identifica otra razón social o naturaleza. Datos registrados: '+old_meta['company_id']+' · '+old_meta['legal_name']+' · '+old_meta['material_nature']+'. Selecciona esa empresa en el paso 1; no crees otro código para actualizarla.')
            if (meta['kind'], meta['as_of_date']) != (old_meta['kind'], old_meta['as_of_date']):
                continue
            if signature(records) == signature(old_records):
                same.append(old_id)
            elif keys(meta['kind'], records) & keys(meta['kind'], old_records):
                overlaps.append(old_id)
        results.append(dict(batch_id=bid, sheet=meta['sheet'], kind=meta['kind'], rows=len(records),
                            status='UNCHANGED' if same else 'CONFLICT' if overlaps else 'NEW',
                            existing_batches=sorted(same), conflicting_batches=sorted(overlaps),new_source_version=bool(same and bid not in same)))
    return results


class CompanyWorkbookReception:
    def __init__(self, db, clock=monotonic):
        self.db = db
        self.clock = clock
        self.checked = None

    def preview(self, content, filename, options):
        self.checked = None
        if not isinstance(options, dict):
            raise ValueError('Indica los datos de la empresa y el corte.')
        if not filename.lower().endswith('.xlsx'):
            raise ValueError('La carga conjunta requiere un XLSX con la hoja 97_Guia_Carga.')
        try:
            guide = read_table(content, filename, sheet=GUIDE)
        except Exception as error:
            raise ValueError('No se puede leer la guía del libro: ' + str(error)[:300]) from None
        if guide['headers'] != HEADERS:
            raise ValueError('La guía debe contener: ' + ', '.join(HEADERS))
        plans = {}
        for row in guide['rows']:
            sheet, kind, field, header = row['values']
            if any(not isinstance(v, str) or not v.strip() for v in (sheet, kind, field, header)):
                raise ValueError('La guía requiere nombres fijos, sin fórmulas ni campos vacíos.')
            if sheet == GUIDE or sheet not in guide['sheets'] or kind not in FIELDS or kind == 'document':
                raise ValueError('Hoja o tipo de contenido no válido en la guía.')
            plan = plans.setdefault(sheet, dict(kind=kind, headers={}))
            if plan['kind'] != kind or field in plan['headers'] or field not in {f[0] for f in FIELDS[kind]}:
                raise ValueError('La guía contiene campos repetidos o incompatibles.')
            plan['headers'][field] = header
        if '08_Referencias_Precios' in guide['sheets'] and '08_Referencias_Precios' not in plans:
            from eios.company_workbook_fields import REFERENCE_FIELDS, header_index
            table=read_table(content,filename,sheet='08_Referencias_Precios')
            explicit={}
            for key,label,required in REFERENCE_FIELDS:
                try: explicit[key]=table['headers'][header_index(table['headers'],label)]
                except ValueError:
                    if required:raise
            plans['08_Referencias_Precios']=dict(kind='price_reference',headers=explicit)
        if not 1 <= len(plans) <= 20:
            raise ValueError('Selecciona entre 1 y 20 hojas en la guía.')
        reports = []; staged = []
        with tempfile.TemporaryDirectory(prefix='eios-workbook-') as folder:
            temporary = folder + '/review.sqlite3'
            reception = CompanyReception(temporary)
            for sheet, plan in plans.items():
                read = reception.read(content, filename, sheet=sheet)
                mapping = {}
                for field, header in plan['headers'].items():
                    from eios.company_workbook_fields import header_index
                    mapping[field] = header_index(read['headers'],header)
                from eios.company_workbook_fields import enrich_plan
                mapping=enrich_plan(read['headers'],plan['kind'],mapping)
                report = reception.preview(dict(options, upload=read['upload'], kind=plan['kind'], mapping=mapping))
                reports.append(dict(sheet=sheet, kind=plan['kind'], rows=report['rows'],
                                    error_count=report['error_count'], errors=report['errors'], warnings=report['warnings']))
                if report['ticket']:
                    reception.commit(report['ticket'])
            if any(r['error_count'] for r in reports):
                return dict(ticket=None, sheets=reports, status='INVALID', decision_authority=False, operational_path='FORBIDDEN')
            with closing(sqlite3.connect(temporary)) as c, c:
                staged = existing(c, reports and options['company_id'].strip())
            dossier = check_dossier(temporary, [r[0] for r in staged])
        with closing(sqlite3.connect(self.db)) as c, c:
            prior = existing(c, options['company_id'].strip())
        revision=options.get('preserve_revision',False)
        if type(revision) is not bool:raise ValueError('La opción de nueva recepción debe ser verdadera o falsa.')
        comparison = compare(staged, prior)
        # Check cross-sheet collisions as well as existing receptions.
        within = compare(staged, [])
        for i, item in enumerate(staged):
            within[i] = compare([item], staged[:i])[0]
        blocking = [i for i in dossier['issues'] if i['code'] not in ('OUTSIDE_SCOPE', 'SOURCE_WARNINGS')]
        blocked = bool(blocking or any(r['status'] == 'CONFLICT' for r in comparison) and not revision
                       or any(r['status'] != 'NEW' for r in within))
        ticket = None if blocked else secrets.token_urlsafe(32)
        if ticket:
            self.checked = dict(ticket=ticket, at=self.clock(), staged=deepcopy(staged),
                                previous=canonical(prior), content=bytes(content), preserve_revision=revision)
        if revision:
            for item in comparison:
                if item['status']=='CONFLICT':item['status']='NEW_REVISION'
        return dict(ticket=ticket, status='CONFLICT' if blocked else 'READY', sheets=reports,
                    comparison=comparison, reference_issues=dossier['issues'],
                    ignored_sheets=[s for s in guide['sheets'] if s not in plans],
                    financial_reconciliation='NOT_PERFORMED', admission_status='PENDING',
                    decision_authority=False, operational_path='FORBIDDEN')

    def commit(self, ticket):
        check = self.checked
        if not check or not isinstance(ticket, str) or not secrets.compare_digest(ticket, check['ticket']):
            raise ValueError('Comprueba de nuevo el libro antes de guardar.')
        self.checked = None
        if self.clock() - check['at'] > TTL:
            raise ValueError('La revisión ha caducado.')
        staged = check['staged']; meta = staged[0][1]; saved = []; unchanged = []
        with closing(sqlite3.connect(self.db)) as c, c:
            c.execute('PRAGMA foreign_keys=ON')
            c.executescript('''CREATE TABLE IF NOT EXISTS received_company (
                company_id TEXT PRIMARY KEY, legal_name TEXT NOT NULL, material_nature TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS received_company_batch (
                batch_id TEXT PRIMARY KEY, company_id TEXT NOT NULL REFERENCES received_company(company_id),
                received_at TEXT NOT NULL, metadata_json TEXT NOT NULL, content BLOB NOT NULL, records_json TEXT NOT NULL);''')
            c.execute('BEGIN IMMEDIATE')
            prior = existing(c, meta['company_id'])
            if canonical(prior) != check['previous']:
                raise ValueError('El expediente ha cambiado; vuelve a comprobar el libro.')
            identity = c.execute('SELECT legal_name,material_nature FROM received_company WHERE company_id=?', (meta['company_id'],)).fetchone()
            if identity and identity != (meta['legal_name'], meta['material_nature']):
                raise ValueError('El código de empresa identifica otros datos.')
            c.execute('INSERT OR IGNORE INTO received_company VALUES(?,?,?)',
                      (meta['company_id'], meta['legal_name'], meta['material_nature']))
            comparison = compare(staged, prior)
            for (bid, report, records), result in zip(staged, comparison):
                if result['status'] == 'UNCHANGED' and bid in result['existing_batches']:
                    unchanged.append(bid); continue
                if result['status']=='CONFLICT' and check.get('preserve_revision'):
                    report['supersedes_received_batches']=result['conflicting_batches']
                elif result['status'] not in ('NEW','UNCHANGED'):
                    raise ValueError('Conflicto con un archivo recibido.')
                c.execute('INSERT INTO received_company_batch VALUES(?,?,?,?,?,?)',
                          (bid, meta['company_id'], datetime.now(timezone.utc).isoformat(),
                           canonical(report), check['content'], canonical(records)))
                saved.append(bid)
        return dict(status='RECEIVED' if saved else 'UNCHANGED', batch_ids=saved,
                    unchanged_batch_ids=sorted(set(unchanged)), admission_status='PENDING',
                    decision_authority=False, operational_path='FORBIDDEN')
