"""Bind an explicit treasury declaration to conserved bytes, without validation."""
import base64
from datetime import date, datetime, timezone
from decimal import Decimal
from hashlib import sha256
import json
import sqlite3

from eios.company_finance_quality import rebuild_quality_preparation
from eios.company_payment_review import _fingerprint
from eios.company_required_calendar import text
from eios.core.documentary_payment_capture import DocumentaryLocator, DocumentaryMaterial
from eios.core.treasury_documentary_support import TreasuryDeclaration, TreasuryObservation, build_treasury_documentary_support

SCHEMA = """CREATE TABLE IF NOT EXISTS company_treasury_documentary_support (
proposal_id TEXT NOT NULL,dataset_id TEXT NOT NULL,revision INTEGER NOT NULL,
preparation_fingerprint TEXT NOT NULL,fingerprint TEXT NOT NULL,payload TEXT NOT NULL,
PRIMARY KEY(proposal_id,revision))"""


def _read(c, report):
    row = c.execute('SELECT revision,fingerprint,payload FROM company_treasury_documentary_support WHERE proposal_id=? AND dataset_id=? ORDER BY revision DESC LIMIT 1',
                    (report['proposal_id'], report['dataset_id'])).fetchone()
    if row is None:
        return dict(status='NOT_RECORDED', revision=0, decision_authority=False)
    revision, fingerprint, raw = row
    payload = json.loads(raw)
    if _fingerprint(payload) != fingerprint:
        raise ValueError('El soporte de tesorería no coincide con su huella.')
    preparation = report.get('finance_quality_preparation') or {}
    current = (preparation.get('status') == 'PREPARED_PRESENTED_MATERIAL_ONLY'
               and preparation.get('fingerprint') == payload['preparation_fingerprint'])
    return dict(status='DECLARATION_BOUND_NOT_VALIDATED' if current else 'PREVIOUS_MATERIAL_SUPPORT',
        revision=revision, fingerprint=fingerprint, preparation_fingerprint=payload['preparation_fingerprint'],
        record_ref=payload['record_ref'], declaration=payload['declaration'],
        documents=[{key:item[key] for key in ('document_ref','sha256')} for item in payload['documents']],
        technical_comparisons=payload['technical_comparisons'], pending_controls=payload['pending_controls'],
        observations=payload['observations'],
        reviewer_ref=payload['reviewer_ref'], reviewed_at=payload['reviewed_at'],
        quality_evaluation_status='NOT_EXECUTED', viability_status='NOT_EVALUATED',
        decision_authority=False, operational_path='FORBIDDEN')


def read_treasury_support(db, report):
    with sqlite3.connect(db) as c:
        c.execute(SCHEMA)
        return _read(c, report)


def rebuild_treasury_support(c, db, report):
    expected = report.get('treasury_documentary_support') or {}
    current = _read(c, report)
    if (expected.get('status') != 'DECLARATION_BOUND_NOT_VALIDATED'
            or current.get('fingerprint') != expected.get('fingerprint')):
        raise ValueError('El soporte ha cambiado o corresponde a otro material. Vuelve a revisar la propuesta.')
    preparation = rebuild_quality_preparation(c, db, report)
    row = c.execute('SELECT payload FROM company_treasury_documentary_support WHERE proposal_id=? AND dataset_id=? AND revision=?',
        (report['proposal_id'], report['dataset_id'], current['revision'])).fetchone()
    payload = json.loads(row[0])
    result = build_treasury_documentary_support(preparation=preparation,
        record_ref=payload['record_ref'], target_company_scope=payload['target_company_scope'],
        case_kind=payload['case_kind'], documents=tuple(DocumentaryMaterial(document_ref=d['document_ref'],
            content=base64.b64decode(d['content_base64'], validate=True)) for d in payload['documents']),
        declaration=TreasuryDeclaration.model_validate_json(json.dumps(payload['declaration'])),
        observations=tuple(TreasuryObservation.model_validate_json(json.dumps(o)) for o in payload['observations']),
        reviewer_ref=payload['reviewer_ref'], reviewed_at=datetime.fromisoformat(payload['reviewed_at']))
    if result.fingerprint != current['fingerprint'] or result.to_payload() != payload:
        raise ValueError('El soporte de tesorería no se reproduce exactamente.')
    return preparation, result


def save_treasury_observation(db, report, data):
    reviewer = text(data.get('reviewer'), 'responsable de la comprobación')
    raw = data.get('observation')
    if not isinstance(raw, dict) or not isinstance(raw.get('note'), str) or len(raw['note']) > 2000:
        raise ValueError('Indica la comprobación y su nota (hasta 2.000 caracteres).')
    observation = TreasuryObservation.model_validate_json(json.dumps(raw))
    with sqlite3.connect(db) as c:
        c.execute(SCHEMA)
        c.execute('BEGIN IMMEDIATE')
        current = _read(c, report)
        if type(data.get('revision')) is not int or data['revision'] != current['revision']:
            raise ValueError('Las comprobaciones han cambiado. Vuelve a revisar la propuesta.')
        preparation, support = rebuild_treasury_support(c, db, report)
        payload = support.to_payload()
        observations = [TreasuryObservation.model_validate_json(json.dumps(o))
                        for o in payload['observations'] if o['condition'] != observation.condition]
        observations.append(observation)
        result = build_treasury_documentary_support(preparation=preparation,
            record_ref=payload['record_ref'], target_company_scope=payload['target_company_scope'],
            case_kind=payload['case_kind'], documents=tuple(DocumentaryMaterial(document_ref=d['document_ref'],
                content=support.document_bytes(d['document_ref'])) for d in payload['documents']),
            declaration=TreasuryDeclaration.model_validate_json(json.dumps(payload['declaration'])),
            observations=tuple(observations), reviewer_ref=reviewer, reviewed_at=datetime.now(timezone.utc))
        c.execute('INSERT INTO company_treasury_documentary_support VALUES(?,?,?,?,?,?)',
            (report['proposal_id'], report['dataset_id'], current['revision']+1, preparation.fingerprint,
             result.fingerprint, json.dumps(result.to_payload(),ensure_ascii=False,sort_keys=True,separators=(',',':'))))
        return _read(c, report)


def save_treasury_support(db, report, data):
    if data.get('acknowledge') is not True:
        raise ValueError('Confirma que has identificado el soporte y transcrito sus datos.')
    reviewer = text(data.get('reviewer'), 'responsable de la declaración')
    reference = text(data.get('record_ref'), 'referencia del registro de tesorería')
    company = text(data.get('documentary_company'), 'empresa que figura en el soporte')
    currency = text(data.get('currency'), 'moneda del soporte')
    if len(currency) != 3:
        raise ValueError('Indica una moneda de tres letras.')
    try:
        if not isinstance(data.get('available_amount'), str):
            raise ValueError()
        locator = DocumentaryLocator.model_validate(data['locator'])
        text(locator.document_ref, 'documento de soporte')
        if not locator.section.strip() or len(locator.section) > 500:
            raise ValueError()
        declaration = TreasuryDeclaration(documentary_company=company, currency=currency,
            economic_date=date.fromisoformat(data['economic_date']),
            available_amount=Decimal(data['available_amount']), locators=(locator,))
    except (ValueError, KeyError, TypeError, ArithmeticError) as error:
        raise ValueError('Revisa importe, fecha, documento, página y sección de tesorería.') from error
    with sqlite3.connect(db) as c:
        c.execute(SCHEMA)
        c.execute('BEGIN IMMEDIATE')
        current = _read(c, report)
        if type(data.get('revision')) is not int or data['revision'] != current['revision']:
            raise ValueError('El soporte ha cambiado. Vuelve a revisar la propuesta.')
        preparation = rebuild_quality_preparation(c, db, report)
        context = report['proposal']['documentary_context_at_save']
        sources = [s for s in context['sources'] if s.get('document_ref') == locator.document_ref]
        if len(sources) != 1 or not sources[0].get('stored_bytes_sha256'):
            raise ValueError('El soporte no está conservado de forma única en el contexto de esta propuesta.')
        captured = [d for d in preparation.to_payload()['capture']['documents'] if d['document_ref'] == locator.document_ref]
        if captured:
            content = base64.b64decode(captured[0]['content_base64'], validate=True)
        else:
            cursor = c.execute('SELECT * FROM documentary_source WHERE dataset_id=?', (report['dataset_id'],))
            columns = [column[0] for column in cursor.description]
            found = [dict(zip(columns,row)) for row in cursor]
            found = [s for s in found if s.get('document_ref') == locator.document_ref]
            if len(found) != 1 or not isinstance(found[0].get('content'), bytes):
                raise ValueError('No se encuentran los bytes del soporte seleccionado.')
            content = found[0]['content']
        if sha256(content).hexdigest() != sources[0]['stored_bytes_sha256']:
            raise ValueError('El soporte ha cambiado respecto al documento conservado en la propuesta.')
        snapshot = preparation.to_payload()['capture']['finance_package']['finance_input']['snapshot']
        support = build_treasury_documentary_support(preparation=preparation, record_ref=reference,
            target_company_scope=snapshot['company_scope'], case_kind='SYNTHETIC',
            documents=(DocumentaryMaterial(document_ref=locator.document_ref, content=content),),
            declaration=declaration, observations=(), reviewer_ref=reviewer,
            reviewed_at=datetime.now(timezone.utc))
        c.execute('INSERT INTO company_treasury_documentary_support VALUES(?,?,?,?,?,?)',
            (report['proposal_id'], report['dataset_id'], current['revision']+1, preparation.fingerprint,
             support.fingerprint, json.dumps(support.to_payload(),ensure_ascii=False,sort_keys=True,separators=(',',':'))))
        return _read(c, report)
