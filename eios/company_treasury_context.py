"""Conserve explicit contextual declarations using the existing treasury contract."""
from datetime import datetime, timezone
import json
import sqlite3

from eios.company_payment_review import _fingerprint
from eios.company_required_calendar import text
from eios.company_treasury_support import rebuild_treasury_support
from eios.core.treasury_contextual_assessment import (
    TreasuryContextualDeclaration, build_treasury_contextual_assessment)

SCHEMA = """CREATE TABLE IF NOT EXISTS company_treasury_contextual_assessment (
proposal_id TEXT NOT NULL,dataset_id TEXT NOT NULL,revision INTEGER NOT NULL,
fingerprint TEXT NOT NULL,payload TEXT NOT NULL,PRIMARY KEY(proposal_id,revision))"""


def _latest(c, report):
    row = c.execute('SELECT revision,fingerprint,payload FROM company_treasury_contextual_assessment WHERE proposal_id=? AND dataset_id=? ORDER BY revision DESC LIMIT 1',
                    (report['proposal_id'], report['dataset_id'])).fetchone()
    if row is None:
        return None
    payload = json.loads(row[2])
    if _fingerprint(payload) != row[1]:
        raise ValueError('La valoración contextual no coincide con su huella.')
    return row[0], row[1], payload


def _summary(row, report):
    if row is None:
        return dict(status='NOT_RECORDED', revision=0, declarations=[], decision_authority=False)
    revision, fingerprint, payload = row
    support = report.get('treasury_documentary_support') or {}
    current = (support.get('status') == 'DECLARATION_BOUND_NOT_VALIDATED'
               and support.get('fingerprint') == payload['treasury_support_fingerprint'])
    return dict(status='BOUND_DECLARATIONS_ONLY' if current else 'PREVIOUS_MATERIAL_ASSESSMENT',
        revision=revision, fingerprint=fingerprint, assessment_ref=payload['assessment_ref'],
        preparation_fingerprint=payload['preparation_fingerprint'],
        treasury_support_fingerprint=payload['treasury_support_fingerprint'],
        declarations=payload['declarations'], pending_conditions=payload['pending_conditions'],
        reviewer_ref=payload['reviewer_ref'], reviewed_at=payload['reviewed_at'],
        quality_evaluation_status='NOT_EXECUTED', viability_status='NOT_EVALUATED',
        decision_authority=False, operational_path='FORBIDDEN')


def read_treasury_context(db, report):
    with sqlite3.connect(db) as c:
        c.execute(SCHEMA)
        return _summary(_latest(c, report), report)


def save_treasury_context(db, report, data):
    reviewer = text(data.get('reviewer'), 'responsable de la valoración')
    reference = text(data.get('assessment_ref'), 'referencia de la valoración')
    raw = data.get('declaration')
    if not isinstance(raw, dict):
        raise ValueError('Indica una declaración contextual explícita.')
    for key in ('applicability_reason', 'necessity_reason', 'impact_reason', 'support_reason'):
        if not isinstance(raw.get(key), str) or not raw[key].strip() or len(raw[key]) > 2000:
            raise ValueError('Explica aplicabilidad, necesidad, impacto y suficiencia (hasta 2.000 caracteres por campo).')
    declaration = TreasuryContextualDeclaration.model_validate_json(json.dumps(raw))
    with sqlite3.connect(db) as c:
        c.execute(SCHEMA)
        c.execute('BEGIN IMMEDIATE')
        latest = _latest(c, report)
        revision = latest[0] if latest else 0
        if type(data.get('revision')) is not int or data['revision'] != revision:
            raise ValueError('La valoración ha cambiado. Vuelve a revisar la propuesta.')
        preparation, support = rebuild_treasury_support(c, db, report)
        prior = latest[2] if latest and latest[2]['treasury_support_fingerprint'] == support.fingerprint else None
        declarations = [TreasuryContextualDeclaration.model_validate_json(json.dumps(d))
            for d in prior['declarations'] if d['condition'] != declaration.condition] if prior else []
        declarations.append(declaration)
        result = build_treasury_contextual_assessment(preparation=preparation, treasury_support=support,
            assessment_ref=reference, declarations=tuple(declarations), reviewer_ref=reviewer,
            reviewed_at=datetime.now(timezone.utc))
        c.execute('INSERT INTO company_treasury_contextual_assessment VALUES(?,?,?,?,?)',
            (report['proposal_id'], report['dataset_id'], revision+1, result.fingerprint,
             json.dumps(result.to_payload(),ensure_ascii=False,sort_keys=True,separators=(',',':'))))
        return _summary((revision+1,result.fingerprint,result.to_payload()), report)
