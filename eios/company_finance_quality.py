"""Prepare presented quality material with existing contracts, without judging it."""
from datetime import datetime, timezone
import base64
import json
import sqlite3

from eios.company_payment_review import _rebuild_capture, _latest, _finding, _fingerprint
from eios.company_reviewer_designation import rebuild_reviewer_designation
from eios.company_required_calendar import _read as read_calendar, text
from eios.core.documentary_payment_review import build_documentary_payment_human_review
from eios.core.required_installment_coverage import RequiredInstallmentCalendar, check_required_installment_coverage
from eios.core.finance_quality_preparation import PresentedQualityCriteria, build_finance_quality_preparation

SCHEMA = """CREATE TABLE IF NOT EXISTS company_finance_quality_preparation (
capture_fingerprint TEXT NOT NULL,dataset_id TEXT NOT NULL,proposal_id TEXT NOT NULL,
revision INTEGER NOT NULL,fingerprint TEXT NOT NULL,payload TEXT NOT NULL,
prepared_by TEXT NOT NULL,created_at TEXT NOT NULL,
PRIMARY KEY(capture_fingerprint,revision))"""


def _read(c, report):
    capture = report['finance_execution'].get('documentary_capture') or {}
    row = c.execute('SELECT revision,fingerprint,payload,prepared_by,created_at FROM company_finance_quality_preparation WHERE capture_fingerprint=? AND dataset_id=? AND proposal_id=? ORDER BY revision DESC LIMIT 1',
                    (capture.get('fingerprint'), report['dataset_id'], report['proposal_id'])).fetchone()
    if row is None:
        return dict(status='NOT_PREPARED', revision=0, decision_authority=False)
    revision, fingerprint, raw, actor, created = row
    payload = json.loads(raw)
    if _fingerprint(payload) != fingerprint or payload['capture_fingerprint'] != capture['fingerprint']:
        raise ValueError('La preparación conservada no coincide con su huella.')
    current_calendar = report.get('required_calendar_coverage') or {}
    current_review = report.get('payment_documentary_review') or {}
    current = (payload['coverage_fingerprint'] == current_calendar.get('fingerprint')
               and payload['review_fingerprint'] == current_review.get('fingerprint')
               and (payload['designation_fingerprint'] is None or
                    (payload['designation_fingerprint'] == (report.get('reviewer_designation') or {}).get('fingerprint')
                     and (report.get('reviewer_designation') or {}).get('status') == 'PRESENTED_DECLARATIONS_ONLY')))
    return dict(status='PREPARED_PRESENTED_MATERIAL_ONLY' if current else 'PREVIOUS_MATERIAL_PREPARATION',
                revision=revision, fingerprint=fingerprint, prepared_by=actor, created_at=created,
                criteria=[{key: item[key] for key in ('reference', 'version', 'sha256')}
                          for item in payload['presented_criteria']],
                coverage_fingerprint=payload['coverage_fingerprint'],
                review_fingerprint=payload['review_fingerprint'],
                designation_fingerprint=payload['designation_fingerprint'],
                designation_status='BOUND_PRESENTED_NOT_VERIFIED' if payload['designation'] is not None else 'NOT_SUPPLIED', treasury_support_scope='SEPARATE_TREASURY_SUPPORT',
                quality_evaluation_status='NOT_EXECUTED', viability_status='NOT_EVALUATED',
                decision_authority=False, operational_path='FORBIDDEN')


def read_quality_preparation(db, report):
    with sqlite3.connect(db) as c:
        c.execute(SCHEMA)
        return _read(c, report)


def rebuild_quality_preparation(c, db, report):
    """Reproduce the exact selected preparation through public core factories."""
    expected = report.get('finance_quality_preparation') or {}
    current = _read(c, report)
    if (expected.get('status') != 'PREPARED_PRESENTED_MATERIAL_ONLY'
            or current.get('fingerprint') != expected.get('fingerprint')):
        raise ValueError('Prepara de nuevo el material de calidad de esta revisión.')
    calendar_state = read_calendar(c, report)
    latest = _latest(c, report)
    if (calendar_state.get('fingerprint') != expected['coverage_fingerprint']
            or (latest[1] if latest else None) != expected['review_fingerprint']):
        raise ValueError('El calendario o la revisión documental han cambiado. Vuelve a revisar y preparar el material.')
    raw = c.execute('SELECT payload FROM company_finance_quality_preparation WHERE fingerprint=? AND dataset_id=? AND proposal_id=? ORDER BY revision DESC LIMIT 1',
                    (expected['fingerprint'], report['dataset_id'], report['proposal_id'])).fetchone()
    payload = json.loads(raw[0])
    capture = _rebuild_capture(c, db, report)
    calendar = RequiredInstallmentCalendar.model_validate_json(json.dumps(payload['calendar']))
    coverage = check_required_installment_coverage(capture=capture, calendar=calendar)
    if coverage.fingerprint != payload['coverage_fingerprint']:
        raise ValueError('La cobertura conservada no se reproduce exactamente.')
    review = None
    if payload['review'] is not None:
        source = payload['review']
        review = build_documentary_payment_human_review(capture=capture,
            review_ref=source['review_ref'], reviewer_ref=source['reviewer_ref'],
            reviewed_at=datetime.fromisoformat(source['reviewed_at']),
            findings=tuple(_finding(item) for item in source['findings']),
            previous_review_ref=source['previous_review_ref'])
    designation = None
    if payload['designation'] is not None:
        designation = rebuild_reviewer_designation(c, report, review, capture)
        if designation.fingerprint != payload['designation_fingerprint']:
            raise ValueError('La designación ha cambiado. Prepara de nuevo el material.')
    criteria = tuple(PresentedQualityCriteria(reference=item['reference'], version=item['version'],
        content=base64.b64decode(item['content_base64'], validate=True)) for item in payload['presented_criteria'])
    result = build_finance_quality_preparation(capture=capture, calendar=calendar,
        coverage=coverage, criteria=criteria, review=review, designation=designation)
    if result.fingerprint != expected['fingerprint'] or result.to_payload() != payload:
        raise ValueError('La preparación conservada no se reproduce exactamente.')
    return result


def save_quality_preparation(db, report, data):
    if (report['finance_execution'].get('documentary_capture') or {}).get('status') != 'CAPTURED_LISTED_ASSOCIATIONS':
        raise ValueError('Primero conserva la captura documental de pagos.')
    expected_calendar = report.get('required_calendar_coverage') or {}
    if expected_calendar.get('status') not in ('STRUCTURAL_MATCH', 'STRUCTURAL_DIFFERENCES'):
        raise ValueError('Primero declara y comprueba el calendario exigible.')
    if type(data.get('include_designation', False)) is not bool:
        raise ValueError('Indica expresamente si quieres incluir la designación.')
    actor = text(data.get('actor'), 'responsable de la preparación')
    if data.get('acknowledge') is not True:
        raise ValueError('Confirma el origen y la versión de los criterios aportados.')
    raw = data.get('criteria')
    if not isinstance(raw, list) or not 1 <= len(raw) <= 5:
        raise ValueError('Aporta entre uno y cinco criterios con referencia, versión y texto.')
    criteria = []
    size = 0
    for item in raw:
        if not isinstance(item, dict) or not isinstance(item.get('content'), str) or not item['content'].strip():
            raise ValueError('Cada criterio requiere su texto completo; no se genera automáticamente.')
        content = item['content'].encode('utf-8')
        size += len(content)
        if size > 8000:
            raise ValueError('El texto de los criterios admite hasta 8.000 bytes en esta ruta.')
        criteria.append(PresentedQualityCriteria(reference=text(item.get('reference'), 'referencia del criterio'),
                                                version=text(item.get('version'), 'versión del criterio'), content=content))
    with sqlite3.connect(db) as c:
        c.execute(SCHEMA)
        c.execute('BEGIN IMMEDIATE')
        current = _read(c, report)
        if type(data.get('revision')) is not int or data['revision'] != current['revision']:
            raise ValueError('La preparación ha cambiado. Vuelve a revisar la propuesta.')
        calendar_state = read_calendar(c, report)
        if calendar_state.get('fingerprint') != expected_calendar.get('fingerprint'):
            raise ValueError('El calendario ha cambiado. Vuelve a revisar la propuesta.')
        latest = _latest(c, report)
        expected_review = (report.get('payment_documentary_review') or {}).get('fingerprint')
        if (latest[1] if latest else None) != expected_review:
            raise ValueError('La revisión documental ha cambiado. Vuelve a revisar la propuesta.')
        capture = _rebuild_capture(c, db, report)
        calendar = RequiredInstallmentCalendar.model_validate_json(json.dumps(calendar_state['calendar']))
        coverage = check_required_installment_coverage(capture=capture, calendar=calendar)
        if coverage.fingerprint != calendar_state['fingerprint']:
            raise ValueError('La cobertura del calendario no se reproduce exactamente.')
        review = None
        if latest:
            source = latest[2]
            review = build_documentary_payment_human_review(capture=capture,
                review_ref=source['review_ref'], reviewer_ref=source['reviewer_ref'],
                reviewed_at=datetime.fromisoformat(source['reviewed_at']),
                findings=tuple(_finding(item) for item in source['findings']),
                previous_review_ref=source['previous_review_ref'])
            if review.fingerprint != latest[1]:
                raise ValueError('La revisión documental no se reproduce exactamente.')
        designation = rebuild_reviewer_designation(c, report, review, capture) if data.get('include_designation', False) else None
        prepared = build_finance_quality_preparation(capture=capture, calendar=calendar,
            coverage=coverage, criteria=tuple(criteria), review=review, designation=designation)
        payload = prepared.to_payload()
        c.execute('INSERT INTO company_finance_quality_preparation VALUES(?,?,?,?,?,?,?,?)',
                  (capture.fingerprint, report['dataset_id'], report['proposal_id'], current['revision'] + 1,
                   prepared.fingerprint, json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(',', ':')),
                   actor, datetime.now(timezone.utc).isoformat()))
        return _read(c, report)
