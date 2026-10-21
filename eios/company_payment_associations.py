"""Local declared bindings, pending documentary review and financial integration."""
from datetime import datetime, timezone
from hashlib import sha256
import json
import sqlite3

from eios.company_proposal_context import capture_context
from eios.core.documentary_payment_capture import DocumentaryLocator, DocumentaryPaymentBinding

SCHEMA = """CREATE TABLE IF NOT EXISTS company_payment_association_event (
proposal_id TEXT NOT NULL, dataset_id TEXT NOT NULL, revision INTEGER NOT NULL,
review_id TEXT NOT NULL, matching_fingerprint TEXT NOT NULL,
documentary_fingerprint TEXT NOT NULL, payload TEXT NOT NULL,
PRIMARY KEY(proposal_id,revision))"""


def _text(value, label, maximum):
    if not isinstance(value,str) or not value.strip() or len(value.strip())>maximum:
        raise ValueError('Indica '+label+' válido.')
    return value.strip()


def _scope(report):
    matching=report.get('payment_matching')
    context=report['proposal'].get('documentary_context_at_save')
    if not matching or matching['status']=='NOT_DECLARED' or not context:
        raise ValueError('Primero declara las cuotas y revisa la propuesta con su contexto documental.')
    return matching,context


def _read(c,report):
    matching=report.get('payment_matching') or {}
    context=report['proposal'].get('documentary_context_at_save') or {}
    events=[json.loads(row[0]) for row in c.execute(
        'SELECT payload FROM company_payment_association_event WHERE proposal_id=? AND dataset_id=? ORDER BY revision',
        (report['proposal_id'],report['dataset_id']))]
    current={}
    for event in events:
        if (event['matching_fingerprint']==matching.get('fingerprint')
                and event['documentary_fingerprint']==context.get('fingerprint')):
            current[event['sequence']]=event
    return dict(schema='COMPANY-PAYMENT-DECLARED-ASSOCIATIONS-01',
        revision=max((e['revision'] for e in events),default=0),
        rows=[current[key] for key in sorted(current)],
        status='DECLARED_ASSOCIATIONS_PENDING_REVIEW' if current else 'NO_DECLARATIONS',
        actor_identity_status='LOCAL_DECLARATION_NOT_AUTHENTICATED',
        documentary_review_status='NOT_PERFORMED',included_in_projection=False,
        decision_authority=False, operational_path='FORBIDDEN')


def read_associations(db,report):
    with sqlite3.connect(db) as c:
        c.execute(SCHEMA)
        return _read(c,report)


def save_association(db,report,data):
    matching,context=_scope(report)
    if matching['status']!='CANDIDATES_LISTED':
        raise ValueError('Corrige el inventario de movimientos antes de declarar asociaciones.')
    actor=_text(data.get('actor'),'responsable',200)
    reason=_text(data.get('reason'),'motivo de la declaración',2000)
    sequence=data.get('sequence')
    if type(sequence) is not int:
        raise ValueError('Selecciona una cuota válida.')
    target=next((row for row in matching['rows'] if row['sequence']==sequence),None)
    if target is None:
        raise ValueError('La cuota no pertenece a esta revisión.')
    action=data.get('action')
    if action not in ('BIND','CLEAR'):
        raise ValueError('Selecciona asociación o dejar pendiente.')
    binding=None
    if action=='BIND':
        flow_id=_text(data.get('flow_id'),'pago de tesorería',128)
        candidate=next((item for item in target['candidates'] if item['flow_id']==flow_id),None)
        if candidate is None:
            raise ValueError('El pago no figura entre las coincidencias de esta cuota.')
        raw=data.get('locator')
        if not isinstance(raw,dict):
            raise ValueError('Indica documento, página y sección de soporte.')
        locator=DocumentaryLocator.model_validate(raw)
        _text(locator.document_ref,'referencia documental',256)
        _text(locator.section,'sección del soporte',500)
        if locator.document_ref!=locator.document_ref.strip() or locator.section!=locator.section.strip():
            raise ValueError('Documento y sección no admiten espacios exteriores.')
        sources=[s for s in context['sources'] if s.get('document_ref')==locator.document_ref]
        if len(sources)!=1 or not sources[0].get('stored_bytes_sha256'):
            raise ValueError('El documento debe estar conservado de forma única en esta versión.')
        if locator.document_ref not in {s.get('document_ref') for s in candidate['source_refs']}:
            raise ValueError('El soporte no está vinculado al pago documental seleccionado.')
        installment=next(i for i in report['proposal']['payment_plan']['installments'] if i['sequence']==sequence)
        binding=DocumentaryPaymentBinding(
            installment_ref=installment['canonical_candidate']['flow_id'],
            flow_id=flow_id,locators=(locator,)).model_dump(mode='json')
    with sqlite3.connect(db) as c:
        c.execute(SCHEMA)
        c.execute('BEGIN IMMEDIATE')
        if capture_context(c,report['dataset_id'])!=context:
            raise ValueError('Los documentos han cambiado. Prepara una propuesta con la versión revisada.')
        current=_read(c,report)
        if type(data.get('revision')) is not int or data['revision']!=current['revision']:
            raise ValueError('Las declaraciones han cambiado. Vuelve a revisar la propuesta.')
        if binding and any(e['sequence']!=sequence and e['action']=='BIND' and
                           e['binding']['flow_id']==binding['flow_id'] for e in current['rows']):
            raise ValueError('Este pago ya está declarado en otra cuota. Revisa o retira esa asociación.')
        event=dict(schema='COMPANY-PAYMENT-ASSOCIATION-EVENT-01',
            proposal_id=report['proposal_id'],dataset_id=report['dataset_id'],
            review_id=report['review_id'],matching_fingerprint=matching['fingerprint'],
            documentary_fingerprint=context['fingerprint'],revision=current['revision']+1,
            sequence=sequence,action=action,binding=binding,actor=actor,reason=reason,
            created_at=datetime.now(timezone.utc).isoformat(),
            documentary_review_status='NOT_PERFORMED',decision_authority=False)
        event['fingerprint']=sha256(json.dumps(event,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
        c.execute('INSERT INTO company_payment_association_event VALUES(?,?,?,?,?,?,?)',
            (event['proposal_id'],event['dataset_id'],event['revision'],event['review_id'],
             event['matching_fingerprint'],event['documentary_fingerprint'],json.dumps(event)))
        return _read(c,report)
