"""Conserve listed payment bindings and source bytes using DOC-PAY-CAP-01."""
from hashlib import sha256
import json

from eios.company_proposal_context import capture_context
from eios.core.documentary_payment_capture import (
    DocumentaryMaterial, DocumentaryLocator, DocumentaryPaymentBinding, build_documentary_payment_capture)
from eios.core.documentary_payment_review import GLOBAL_CONDITIONS, INSTALLMENT_CONDITIONS

SCHEMA = """CREATE TABLE IF NOT EXISTS company_payment_documentary_capture (
fingerprint TEXT PRIMARY KEY, dataset_id TEXT NOT NULL, proposal_id TEXT NOT NULL,
finance_package_fingerprint TEXT NOT NULL, payload TEXT NOT NULL)"""


def capture_listed_payments(c, package, proposal, associations):
    summary=dict(schema='COMPANY-PAYMENT-CAPTURE-SUMMARY-01',status='NOT_CAPTURED',
        message='Sin asociaciones declaradas que capturar.',
        scope='DECLARED_LISTED_INSTALLMENT_ASSOCIATIONS_ONLY',
        fingerprint=None,document_count=0,binding_count=0,pending_review_control_count=None,
        required_calendar_status='NOT_SUPPLIED',documentary_review_status='NOT_PERFORMED',
        decision_authority=False,operational_path='FORBIDDEN')
    events=[e for e in (associations or {}).get('rows',[]) if e['action']=='BIND']
    if not events:
        return summary
    try:
        context=proposal.get('documentary_context_at_save')
        if not context or capture_context(c,proposal['dataset_id'])!=context:
            raise ValueError('Los documentos difieren del contexto conservado en la propuesta.')
        bindings=[]
        flows={f.flow_id:f for f in package.finance_input.cash_flows}
        plan=proposal['payment_plan']
        for event in events:
            if (event['proposal_id']!=proposal['proposal_id'] or event['dataset_id']!=proposal['dataset_id']
                    or event['documentary_fingerprint']!=context['fingerprint']):
                raise ValueError('Una declaración pertenece a otro material.')
            raw=event['binding']
            binding=DocumentaryPaymentBinding(installment_ref=raw['installment_ref'],flow_id=raw['flow_id'],
                locators=tuple(DocumentaryLocator.model_validate(locator) for locator in raw['locators']))
            installment=next((i for i in plan['installments'] if i['sequence']==event['sequence']),None)
            flow=flows.get(binding.flow_id)
            if (not installment or installment['canonical_candidate']['flow_id']!=binding.installment_ref
                    or flow is None or flow.amount is None):
                raise ValueError('La asociación no identifica una cuota y pago conservados.')
            from decimal import Decimal
            if (flow.amount!=Decimal(installment['amount']) or flow.currency!=plan['currency']
                    or flow.due_date is None or flow.due_date.isoformat()!=installment['due_date']):
                raise ValueError('La cuota y el pago ya no coinciden en importe, moneda y fecha.')
            bindings.append(binding)
        references=sorted({locator.document_ref for binding in bindings for locator in binding.locators})
        cursor=c.execute('SELECT * FROM documentary_source WHERE dataset_id=?',(proposal['dataset_id'],))
        columns=[column[0] for column in cursor.description]
        sources=[dict(zip(columns,row)) for row in cursor]
        documents=[]
        for reference in references:
            found=[source for source in sources if source.get('document_ref')==reference]
            conserved=[source for source in context['sources'] if source.get('document_ref')==reference]
            if len(found)!=1 or len(conserved)!=1 or not isinstance(found[0].get('content'),bytes):
                raise ValueError('Faltan bytes conservados únicos para el documento '+reference+'.')
            content=found[0]['content']
            if sha256(content).hexdigest()!=conserved[0].get('stored_bytes_sha256'):
                raise ValueError('La huella del documento no coincide.')
            documents.append(DocumentaryMaterial(document_ref=reference,content=content))
        capture=build_documentary_payment_capture(package=package,documents=tuple(documents),
            bindings=tuple(bindings),case_kind='SYNTHETIC',operation_ref=proposal['proposal_id'])
        payload=json.dumps(capture.to_payload(),ensure_ascii=False,sort_keys=True,separators=(',',':'))
        c.execute(SCHEMA)
        c.execute('INSERT OR IGNORE INTO company_payment_documentary_capture VALUES(?,?,?,?,?)',
            (capture.fingerprint,proposal['dataset_id'],proposal['proposal_id'],package.fingerprint,payload))
        stored=c.execute('SELECT payload FROM company_payment_documentary_capture WHERE fingerprint=?',
                         (capture.fingerprint,)).fetchone()[0]
        if stored!=payload:
            raise ValueError('La captura existente no coincide con el material construido.')
        summary.update(status='CAPTURED_LISTED_ASSOCIATIONS',fingerprint=capture.fingerprint,
            finance_package_fingerprint=package.fingerprint,document_count=len(documents),
            binding_count=len(bindings),
            pending_review_control_count=len(GLOBAL_CONDITIONS)+len(INSTALLMENT_CONDITIONS)*len(bindings),
            association_revisions=[event['revision'] for event in events],
            message='Documentos y asociaciones conservados con el paquete financiero. Revisión documental y calendario requerido pendientes.')
    except (ValueError,KeyError,TypeError) as error:
        summary['message']='Captura documental pendiente: '+str(error)
    return summary
