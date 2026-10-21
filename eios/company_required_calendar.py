"""Explicit required calendars and canonical structural coverage, without admission."""
from datetime import date, datetime, timezone
from decimal import Decimal
import json
import sqlite3

from eios.company_payment_review import _rebuild_capture, _fingerprint
from eios.core.documentary_payment_capture import DocumentaryLocator
from eios.core.required_installment_coverage import (
    RequiredInstallment, RequiredInstallmentCalendar, check_required_installment_coverage)

SCHEMA="""CREATE TABLE IF NOT EXISTS company_required_payment_calendar (
capture_fingerprint TEXT NOT NULL,dataset_id TEXT NOT NULL,proposal_id TEXT NOT NULL,
revision INTEGER NOT NULL,fingerprint TEXT NOT NULL,payload TEXT NOT NULL,
declared_by TEXT NOT NULL,created_at TEXT NOT NULL,
PRIMARY KEY(capture_fingerprint,revision))"""


def text(value,label):
    if not isinstance(value,str) or not value.strip() or len(value.strip())>256:
        raise ValueError('Indica '+label+' (hasta 256 caracteres).')
    return value.strip()


def document_references(data):
    keys=('order_ref','order_version','confirmation_ref')
    values={key:data.get('document_'+key) for key in keys}
    for key,value in values.items():
        if value is not None and not isinstance(value,str):
            raise ValueError('Las referencias documentales deben ser texto.')
        values[key]=value.strip() if value else None
    if any(values.values()):
        values={key:text(value,'pedido, versión y confirmación completos') for key,value in values.items()}
    return values


def _read(c,report):
    capture=(report.get('finance_execution') or {}).get('documentary_capture') or {}
    row=c.execute('SELECT revision,fingerprint,payload,declared_by,created_at FROM company_required_payment_calendar WHERE capture_fingerprint=? AND dataset_id=? AND proposal_id=? ORDER BY revision DESC LIMIT 1',
        (capture.get('fingerprint'),report['dataset_id'],report['proposal_id'])).fetchone()
    if row is None:
        return dict(status='NOT_CHECKED',revision=0,decision_authority=False)
    revision,fingerprint,raw,actor,created=row
    payload=json.loads(raw)
    if _fingerprint(payload)!=fingerprint or payload['capture_fingerprint']!=capture['fingerprint']:
        raise ValueError('La comprobación del calendario no coincide con su huella.')
    return dict(status='STRUCTURAL_MATCH' if payload['required_calendar_matches'] else 'STRUCTURAL_DIFFERENCES',
        revision=revision,fingerprint=fingerprint,declared_by=actor,created_at=created,
        calendar=payload['calendar'],reference_mismatches=payload['reference_mismatches'],
        observations=payload['observations'],unexpected_installment_refs=payload['unexpected_installment_refs'],
        unassociated_payment_flow_ids=payload['unassociated_payment_flow_ids'],
        assurance_scope=payload['assurance_scope'],decision_authority=False,operational_path='FORBIDDEN')


def read_required_calendar(db,report):
    with sqlite3.connect(db) as c:
        c.execute(SCHEMA)
        return _read(c,report)


def save_required_calendar(db,report,data):
    if (report['finance_execution'].get('documentary_capture') or {}).get('status')!='CAPTURED_LISTED_ASSOCIATIONS':
        raise ValueError('Primero genera la captura documental de pagos.')
    refs=report['proposal'].get('operation_document_references') or {}
    if not all(refs.get(key) for key in ('order_ref','order_version','confirmation_ref')):
        raise ValueError('Esta propuesta no conserva pedido, versión y confirmación. Prepara una nueva propuesta con esas referencias; no se rellenan retrospectivamente.')
    if data.get('acknowledge') is not True:
        raise ValueError('Confirma expresamente el calendario exigible y sus soportes.')
    actor=text(data.get('actor'),'responsable declarante')
    declaration=text(data.get('declaration_ref'),'referencia de la declaración')
    authority=text(data.get('authority_ref'),'referencia de quien establece el calendario')
    rows=data.get('installments')
    if not isinstance(rows,list) or not 1<=len(rows)<=20:
        raise ValueError('El calendario requiere entre 1 y 20 cuotas explícitas.')
    try:
        if not isinstance(data.get('total_due'),str):
            raise ValueError()
        total=Decimal(data['total_due'])
        if not total.is_finite() or total<=0 or total!=Decimal(report['proposal']['operation_total']):
            raise ValueError()
        installments=[]
        for row in rows:
            if not isinstance(row['amount'],str):
                raise ValueError()
            locators=tuple(DocumentaryLocator.model_validate(loc) for loc in row['locators'])
            if any(len(loc.document_ref)>256 or len(loc.section)>500 for loc in locators):
                raise ValueError()
            installments.append(RequiredInstallment(installment_ref=text(row['installment_ref'],'referencia de cuota'),
                sequence=row['sequence'],amount=Decimal(row['amount']),currency=row['currency'],
                due_date=date.fromisoformat(row['due_date']),locators=locators))
    except (ValueError,TypeError,KeyError,ArithmeticError) as error:
        raise ValueError('Revisa las cuotas: importes, moneda, fechas, soportes y total declarado de la operación.') from error
    calendar=RequiredInstallmentCalendar(declaration_ref=declaration,authority_ref=authority,
        case_kind='SYNTHETIC',operation_ref=report['proposal_id'],
        total_due=total,currency=report['proposal']['currency'],installments=tuple(installments),**refs)
    with sqlite3.connect(db) as c:
        c.execute(SCHEMA)
        c.execute('BEGIN IMMEDIATE')
        current=_read(c,report)
        if type(data.get('revision')) is not int or data['revision']!=current['revision']:
            raise ValueError('El calendario ha cambiado. Vuelve a revisar la propuesta.')
        capture=_rebuild_capture(c,db,report)
        document_refs={doc['document_ref'] for doc in capture.to_payload()['documents']}
        if any(loc.document_ref not in document_refs for item in installments for loc in item.locators):
            raise ValueError('El soporte requerido no está conservado en la captura.')
        try:
            coverage=check_required_installment_coverage(capture=capture,calendar=calendar)
        except ValueError as error:
            raise ValueError('El calendario no cumple el contrato: fechas estrictamente crecientes, cuotas únicas y suma exacta. '+str(error)) from error
        payload=coverage.to_payload()
        c.execute('INSERT INTO company_required_payment_calendar VALUES(?,?,?,?,?,?,?,?)',
            (capture.fingerprint,report['dataset_id'],report['proposal_id'],current['revision']+1,
             coverage.fingerprint,json.dumps(payload,ensure_ascii=False,sort_keys=True,separators=(',',':')),
             actor,datetime.now(timezone.utc).isoformat()))
        return _read(c,report)
