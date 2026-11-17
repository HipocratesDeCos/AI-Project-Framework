"""Append-only local agreement declarations, never purchase authorization."""
from datetime import date, datetime, timezone
from hashlib import sha256
import json
import sqlite3

from eios.company_proposal_context import capture_context
from eios.company_purchase_comparison import condition
from eios.company_purchase_draft import fingerprint

SCHEMA='''CREATE TABLE IF NOT EXISTS company_purchase_agreement_event (
dataset_id TEXT NOT NULL,proposal_id TEXT NOT NULL,revision INTEGER NOT NULL,
payload TEXT NOT NULL,fingerprint TEXT NOT NULL,
PRIMARY KEY(dataset_id,proposal_id,revision))'''


def digest(value):
    return sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()


def _read(connection,report):
    events=[]
    if connection.execute("SELECT 1 FROM sqlite_master WHERE name='company_purchase_agreement_event'").fetchone():
        for raw,stamp in connection.execute('SELECT payload,fingerprint FROM company_purchase_agreement_event WHERE dataset_id=? AND proposal_id=? ORDER BY revision',(report['dataset_id'],report['proposal_id'])):
            event=json.loads(raw)
            if digest(event)!=stamp or event['revision']!=len(events)+1 or event['proposal_fingerprint']!=fingerprint(report['proposal']) or (event['dataset_id'],event['proposal_id'])!=(report['dataset_id'],report['proposal_id']) or event.get('previous_event_fingerprint')!=(digest(events[-1]) if events else None):
                raise ValueError('El historial de acuerdos no coincide con el estudio conservado.')
            events.append(event)
    return dict(schema='PURCHASE-AGREEMENT-DECLARATIONS-01',revision=len(events),status='DECLARED_UNVERIFIED' if events and events[-1]['action']=='DECLARE' else 'RETRACTED' if events else 'NOT_DECLARED',
        events=events,decision_authority=False,operational_path='FORBIDDEN',purchase_authorized=False,
        scope='Declaración local sobre las condiciones y cuotas de este estudio. No acredita aceptación, no autoriza compras ni registra pagos.')


def read(db,report):
    with sqlite3.connect(db) as connection:return _read(connection,report)


def save(db,report,data):
    def text(field,maximum=256):
        value=data.get(field)
        if not isinstance(value,str) or not value.strip() or len(value.strip())>maximum:raise ValueError('Completa '+field+' (hasta '+str(maximum)+' caracteres).')
        return value.strip()
    if data.get('acknowledge') is not True:raise ValueError('Confirma que declaras un acuerdo de estas condiciones, sin autorizar la compra.')
    actor=text('actor');reference=text('source_reference');action=data.get('action')
    if action not in ('DECLARE','RETRACT'):raise ValueError('Acción de acuerdo no válida.')
    reason=text('reason') if action=='RETRACT' else None
    try:when=date.fromisoformat(data['agreement_date'])
    except (ValueError,KeyError,TypeError):raise ValueError('Indica una fecha válida para la declaración.') from None
    proposal=report['proposal'];context=proposal.get('documentary_context_at_save')
    if not context or not proposal.get('commercial_terms'):raise ValueError('Este estudio no conserva las condiciones y el contexto necesarios.')
    if when<date.fromisoformat(proposal['order_date']):raise ValueError('La fecha declarada no puede ser anterior al pedido de este estudio.')
    with sqlite3.connect(db) as connection:
        connection.execute('BEGIN IMMEDIATE');connection.execute(SCHEMA)
        if capture_context(connection,report['dataset_id'])!=context:raise ValueError('El contexto documental ha cambiado. No se registra el acuerdo sobre otra versión.')
        row=connection.execute('SELECT payload FROM manual_purchase_proposal WHERE dataset_id=? AND proposal_id=?',(report['dataset_id'],report['proposal_id'])).fetchone()
        if not row or fingerprint(json.loads(row[0]))!=fingerprint(proposal):raise ValueError('El estudio original no coincide con la revisión.')
        current=_read(connection,report)
        if type(data.get('revision')) is not int or data['revision']!=current['revision']:raise ValueError('El acuerdo ha cambiado. Revisa el estudio antes de registrar otra declaración.')
        if action=='RETRACT' and current['status']!='DECLARED_UNVERIFIED':raise ValueError('No hay una declaración vigente que dejar sin efecto.')
        if action=='DECLARE' and current['status']=='DECLARED_UNVERIFIED':raise ValueError('Ya existe una declaración vigente. Déjala sin efecto antes de sustituirla.')
        metadata=condition(dict(origin='DOCUMENTED',source_reference=reference,acceptance='DECLARED_ACCEPTED',acceptance_reference=reference)) if action=='DECLARE' else None
        event=dict(dataset_id=report['dataset_id'],proposal_id=report['proposal_id'],review_id=report['review_id'],proposal_fingerprint=fingerprint(proposal),revision=current['revision']+1,action=action,
            actor=actor,agreement_date=when.isoformat(),source_reference=reference,reason=reason,condition=metadata,recorded_at=datetime.now(timezone.utc).isoformat(),
            previous_event_fingerprint=digest(current['events'][-1]) if current['events'] else None,
            decision_authority=False,purchase_authorized=False,operational_path='FORBIDDEN')
        connection.execute('INSERT INTO company_purchase_agreement_event VALUES(?,?,?,?,?)',(event['dataset_id'],event['proposal_id'],event['revision'],json.dumps(event,ensure_ascii=False),digest(event)))
        return _read(connection,report)
