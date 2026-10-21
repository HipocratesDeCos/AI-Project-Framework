"""Preserve presented designation support; never authenticate a reviewer."""
from datetime import datetime
import json
import sqlite3

from eios.company_payment_review import _fingerprint, _latest as latest_review, _rebuild_capture, _finding
from eios.company_required_calendar import text
from eios.core.documentary_payment_capture import DocumentaryMaterial
from eios.core.documentary_payment_review import build_documentary_payment_human_review
from eios.core.documentary_reviewer_designation import (
    DesignationDeclaration, DesignationObservation, build_documentary_reviewer_designation_link)

SCHEMA = """CREATE TABLE IF NOT EXISTS company_reviewer_designation (
proposal_id TEXT NOT NULL,dataset_id TEXT NOT NULL,revision INTEGER NOT NULL,
fingerprint TEXT NOT NULL,payload TEXT NOT NULL,PRIMARY KEY(proposal_id,revision))"""


def _latest(c, report):
    row = c.execute('SELECT revision,fingerprint,payload FROM company_reviewer_designation WHERE proposal_id=? AND dataset_id=? ORDER BY revision DESC LIMIT 1',
                    (report['proposal_id'], report['dataset_id'])).fetchone()
    if row is None:
        return None
    payload = json.loads(row[2])
    if _fingerprint(payload) != row[1]:
        raise ValueError('La designación conservada no coincide con su huella.')
    return row[0], row[1], payload


def _summary(row, report):
    base = dict(decision_authority=False, operational_path='FORBIDDEN',
                identity_status='NOT_AUTHENTICATED', authority_status='NOT_VERIFIED',
                quality_integration_status='AVAILABLE_FOR_EXPLICIT_INCLUSION')
    if row is None:
        return dict(base, status='NOT_RECORDED', revision=0, declarations=[])
    revision, fingerprint, payload = row
    current = payload['review_fingerprint'] == (report.get('payment_documentary_review') or {}).get('fingerprint')
    return dict(base, status='PRESENTED_DECLARATIONS_ONLY' if current else 'PREVIOUS_REVIEW_DESIGNATION',
                revision=revision, fingerprint=fingerprint, review_fingerprint=payload['review_fingerprint'],
                link_ref=payload['link_ref'], designation_ref=payload['designation_ref'],
                designation_kind=payload['designation_kind'], reviewer_ref=payload['reviewer_ref'],
                company_scope=payload['company_scope'], declarations=payload['declarations'], observations=payload['observations'],
                pending_controls=payload['pending_controls'])


def read_reviewer_designation(db, report):
    with sqlite3.connect(db) as c:
        c.execute(SCHEMA)
        return _summary(_latest(c, report), report)


def save_reviewer_designation(db, report, data):
    if data.get('acknowledge') is not True:
        raise ValueError('Confirma que el registro no acredita identidad ni autoridad.')
    reference = text(data.get('link_ref'), 'referencia del registro')
    document_ref = text(data.get('designation_ref'), 'documento de designación')
    raw = data.get('declarations')
    if not isinstance(raw, list) or not 1 <= len(raw) <= 7:
        raise ValueError('Aporta entre una y siete transcripciones explícitas.')
    if any(not isinstance(d, dict) or not isinstance(d.get('text'), str) or len(d['text']) > 2000 for d in raw):
        raise ValueError('Cada transcripción admite hasta 2.000 caracteres.')
    declarations = tuple(DesignationDeclaration.model_validate_json(json.dumps(d)) for d in raw)
    with sqlite3.connect(db) as c:
        c.execute(SCHEMA)
        c.execute('BEGIN IMMEDIATE')
        prior = _latest(c, report)
        revision = prior[0] if prior else 0
        if type(data.get('revision')) is not int or data['revision'] != revision:
            raise ValueError('La designación ha cambiado. Vuelve a revisar la propuesta.')
        current = latest_review(c, report)
        expected = (report.get('payment_documentary_review') or {}).get('fingerprint')
        if current is None or current[1] != expected:
            raise ValueError('Falta la revisión documental actual o ha cambiado.')
        source = current[2]
        capture = _rebuild_capture(c, db, report)
        review = build_documentary_payment_human_review(capture=capture,
            review_ref=source['review_ref'], reviewer_ref=source['reviewer_ref'],
            reviewed_at=datetime.fromisoformat(source['reviewed_at']),
            findings=tuple(_finding(f) for f in source['findings']), previous_review_ref=source['previous_review_ref'])
        if review.fingerprint != current[1]:
            raise ValueError('La revisión no puede reproducirse exactamente.')
        # Only already conserved capture bytes are selectable in this first step.
        refs = {document_ref} | {loc.document_ref for d in declarations for loc in d.locators}
        try:
            documents = tuple(DocumentaryMaterial(document_ref=ref, content=capture.document_bytes(ref)) for ref in sorted(refs))
        except KeyError as exc:
            raise ValueError('El documento debe estar conservado en esta captura.') from exc
        result = build_documentary_reviewer_designation_link(review=review, link_ref=reference,
            designation_ref=document_ref, designation_kind=data.get('designation_kind'),
            reviewer_ref=data.get('reviewer_ref'), company_scope=data.get('company_scope'),
            documents=documents, declarations=declarations, observations=())
        payload = result.to_payload()
        c.execute('INSERT INTO company_reviewer_designation VALUES(?,?,?,?,?)',
            (report['proposal_id'], report['dataset_id'], revision+1, result.fingerprint,
             json.dumps(payload,ensure_ascii=False,sort_keys=True,separators=(',',':'))))
        return _summary((revision+1,result.fingerprint,payload), report)


def rebuild_reviewer_designation(c, report, review, capture):
    """Reproduce the explicitly selected designation using conserved capture bytes."""
    expected = report.get('reviewer_designation') or {}
    c.execute(SCHEMA)
    latest = _latest(c, report)
    if (expected.get('status') != 'PRESENTED_DECLARATIONS_ONLY' or latest is None
            or latest[1] != expected.get('fingerprint')):
        raise ValueError('La designación ha cambiado o falta. Vuelve a revisar la propuesta.')
    payload = latest[2]
    if review is None or payload['review_fingerprint'] != review.fingerprint:
        raise ValueError('La designación corresponde a otra revisión documental.')
    try:
        documents = tuple(DocumentaryMaterial(document_ref=d['document_ref'],
            content=capture.document_bytes(d['document_ref'])) for d in payload['documents'])
    except KeyError as exc:
        raise ValueError('El soporte de designación no pertenece a esta captura.') from exc
    result = build_documentary_reviewer_designation_link(review=review,
        **{key: payload[key] for key in ('link_ref','designation_ref','designation_kind','reviewer_ref','company_scope')},
        documents=documents,
        declarations=tuple(DesignationDeclaration.model_validate_json(json.dumps(d)) for d in payload['declarations']),
        observations=tuple(DesignationObservation.model_validate_json(json.dumps(o)) for o in payload['observations']))
    if result.fingerprint != latest[1] or result.to_payload() != payload:
        raise ValueError('La designación conservada no puede reproducirse exactamente.')
    return result


def save_designation_observation(db, report, data):
    """Append an explicit finding to the exact designation, retaining its material."""
    if data.get('acknowledge') is not True:
        raise ValueError('Confirma que la comprobación declarada no acredita identidad ni autoridad.')
    raw = data.get('observation')
    if not isinstance(raw, dict) or not isinstance(raw.get('note'), str) or not raw['note'].strip() or len(raw['note']) > 2000:
        raise ValueError('Aporta una comprobación explícita y una nota de hasta 2.000 caracteres.')
    observation = DesignationObservation.model_validate_json(json.dumps(raw))
    with sqlite3.connect(db) as c:
        c.execute(SCHEMA)
        c.execute('BEGIN IMMEDIATE')
        latest = _latest(c, report)
        if (latest is None or type(data.get('revision')) is not int
                or latest[0] != data['revision']):
            raise ValueError('La designación falta o ha cambiado. Vuelve a revisar la propuesta.')
        human = latest_review(c, report)
        if human is None or human[1] != (report.get('payment_documentary_review') or {}).get('fingerprint'):
            raise ValueError('La revisión documental ha cambiado o falta.')
        capture = _rebuild_capture(c, db, report)
        source = human[2]
        review = build_documentary_payment_human_review(capture=capture,
            review_ref=source['review_ref'], reviewer_ref=source['reviewer_ref'],
            reviewed_at=datetime.fromisoformat(source['reviewed_at']),
            findings=tuple(_finding(f) for f in source['findings']), previous_review_ref=source['previous_review_ref'])
        if review.fingerprint != human[1]:
            raise ValueError('La revisión documental no se reproduce exactamente.')
        designation = rebuild_reviewer_designation(c, report, review, capture)
        payload = designation.to_payload()
        observations = tuple(DesignationObservation.model_validate_json(json.dumps(o))
            for o in payload['observations'] if o['condition'] != observation.condition) + (observation,)
        result = build_documentary_reviewer_designation_link(review=review,
            **{key: payload[key] for key in ('link_ref','designation_ref','designation_kind','reviewer_ref','company_scope')},
            documents=tuple(DocumentaryMaterial(document_ref=d['document_ref'],
                content=designation.document_bytes(d['document_ref'])) for d in payload['documents']),
            declarations=tuple(DesignationDeclaration.model_validate_json(json.dumps(d)) for d in payload['declarations']),
            observations=observations)
        c.execute('INSERT INTO company_reviewer_designation VALUES(?,?,?,?,?)',
            (report['proposal_id'], report['dataset_id'], latest[0]+1, result.fingerprint,
             json.dumps(result.to_payload(),ensure_ascii=False,sort_keys=True,separators=(',',':'))))
        return _summary((latest[0]+1,result.fingerprint,result.to_payload()), report)
