"""Record explicit local findings through the existing documentary review builder."""
from datetime import datetime, timezone
from hashlib import sha256
import json
import sqlite3
from uuid import uuid4

from eios.company_payment_documents import captured_document
from eios.company_finance_parameters import Catalogue, Authorization, Repository
from eios.parameters.center import ParameterConfigurationCenter
from eios.core.models import DecisionContext, Evidence, PurchaseOperation
from eios.finance.models import FinanceBasicInput
from eios.core.finance_decision_input_package import build_finance_decision_input_package
from eios.core.documentary_payment_capture import (DocumentaryMaterial, DocumentaryLocator,
    DocumentaryPaymentBinding, build_documentary_payment_capture)
from eios.core.documentary_payment_review import (DocumentaryReviewFinding,
    build_documentary_payment_human_review)

SCHEMA="""CREATE TABLE IF NOT EXISTS company_payment_human_review (
capture_fingerprint TEXT NOT NULL, dataset_id TEXT NOT NULL, proposal_id TEXT NOT NULL,
revision INTEGER NOT NULL, fingerprint TEXT NOT NULL, payload TEXT NOT NULL,
PRIMARY KEY(capture_fingerprint,revision))"""


def _fingerprint(payload):
    return sha256(json.dumps(payload,ensure_ascii=False,sort_keys=True,separators=(',',':'),
                             allow_nan=False).encode()).hexdigest()


def _latest(c,report):
    capture=report['finance_execution']['documentary_capture']
    row=c.execute('SELECT revision,fingerprint,payload FROM company_payment_human_review WHERE capture_fingerprint=? AND dataset_id=? AND proposal_id=? ORDER BY revision DESC LIMIT 1',
        (capture.get('fingerprint'),report['dataset_id'],report['proposal_id'])).fetchone()
    if row is None:
        return None
    payload=json.loads(row[2])
    if (_fingerprint(payload)!=row[1] or payload['capture_fingerprint']!=capture['fingerprint']
            or _fingerprint(payload['capture'])!=capture['fingerprint']):
        raise ValueError('La revisión documental conservada no coincide con su huella.')
    return row[0],row[1],payload


def _summary(row):
    if row is None:
        return dict(status='NO_FINDINGS',revision=0,findings=[],pending_controls=[],
                    confirmed_count=0,not_confirmed_count=0,conflict_count=0,
                    reviewer_identity_status='LOCAL_DECLARATION_NOT_AUTHENTICATED',
                    decision_authority=False,operational_path='FORBIDDEN')
    revision,fingerprint,payload=row
    findings=payload['findings']
    return dict(status='FINDINGS_RECORDED',revision=revision,fingerprint=fingerprint,
        review_ref=payload['review_ref'],reviewer_ref=payload['reviewer_ref'],
        reviewed_at=payload['reviewed_at'],previous_review_ref=payload['previous_review_ref'],
        findings=findings,pending_controls=payload['pending_controls'],
        pending_control_count=len(payload['pending_controls']),control_count=len(payload['control_inventory']),
        confirmed_count=sum(f['outcome']=='CONFIRMED_BY_REVIEW' for f in findings),
        not_confirmed_count=sum(f['outcome']=='NOT_CONFIRMED' for f in findings),
        conflict_count=sum(f['outcome']=='CONFLICT_REPORTED' for f in findings),
        scope='DECLARED_LISTED_INSTALLMENT_ASSOCIATIONS_ONLY',
        calendar_check_scope='SEPARATE_CALENDAR_COVERAGE',evidence_upgrade_status='NOT_PERFORMED',
        reviewer_identity_status='LOCAL_DECLARATION_NOT_AUTHENTICATED',
        decision_authority=False,operational_path='FORBIDDEN')


def read_documentary_review(db,report):
    if report['finance_execution'].get('documentary_capture',{}).get('status')!='CAPTURED_LISTED_ASSOCIATIONS':
        return _summary(None)
    with sqlite3.connect(db) as c:
        c.execute(SCHEMA)
        return _summary(_latest(c,report))


def _rebuild_capture(c,db,report):
    summary=report['finance_execution']['documentary_capture']
    row=c.execute('SELECT payload FROM company_payment_documentary_capture WHERE fingerprint=? AND dataset_id=? AND proposal_id=?',
        (summary['fingerprint'],report['dataset_id'],report['proposal_id'])).fetchone()
    if row is None:
        raise ValueError('No se encuentra la captura de esta revisión.')
    payload=json.loads(row[0])
    if _fingerprint(payload)!=summary['fingerprint']:
        raise ValueError('La huella de la captura no coincide.')
    finance_payload=payload['finance_package']
    base=finance_payload['decision_input_package']
    # Rebuild through public factories and the real read-only Centre ports.
    # Never instantiate opaque objects or manufacture imported configurations.
    center=ParameterConfigurationCenter(Catalogue(),Authorization(),Repository(c))
    package=build_finance_decision_input_package(
        purchase=PurchaseOperation.model_validate(base['purchase']),
        context=DecisionContext.model_validate(base['context']),
        evidence=tuple(Evidence.model_validate(item) for item in base['evidence']),
        finance_input=FinanceBasicInput.model_validate(finance_payload['finance_input']),
        company_id=base['company_id'],effective_at=datetime.fromisoformat(base['effective_at']),
        requested_parameter_ids=tuple(base['requested_parameter_ids']),center=center)
    if package.fingerprint!=payload['finance_package_fingerprint']:
        raise ValueError('Los parámetros conservados no pueden reproducirse exactamente; no se registra la revisión.')
    documents=tuple(DocumentaryMaterial(document_ref=item['document_ref'],
        content=captured_document(db,report,item['document_ref'])['content']) for item in payload['documents'])
    bindings=tuple(DocumentaryPaymentBinding(installment_ref=item['installment_ref'],
        flow_id=item['flow_id'],locators=tuple(DocumentaryLocator.model_validate(loc) for loc in item['locators']))
        for item in payload['bindings'])
    capture=build_documentary_payment_capture(package=package,documents=documents,bindings=bindings,
        **{key:payload[key] for key in ('case_kind','operation_ref','order_ref','order_version',
                                      'confirmation_ref','external_review_ref')})
    if capture.fingerprint!=summary['fingerprint']:
        raise ValueError('La captura documental no se reproduce exactamente.')
    return capture


def _finding(raw):
    data=dict(raw)
    data['locators']=tuple(DocumentaryLocator.model_validate(item) for item in data.get('locators',[]))
    return DocumentaryReviewFinding.model_validate(data)


def save_documentary_review(db,report,data):
    if report['finance_execution'].get('documentary_capture',{}).get('status')!='CAPTURED_LISTED_ASSOCIATIONS':
        raise ValueError('Primero genera una captura documental de pagos.')
    reviewer=data.get('reviewer')
    if not isinstance(reviewer,str) or not reviewer.strip() or len(reviewer.strip())>200:
        raise ValueError('Indica el responsable de la revisión.')
    raw=data.get('finding')
    if not isinstance(raw,dict) or not isinstance(raw.get('note'),str) or len(raw['note'])>2000:
        raise ValueError('Indica una comprobación y una nota de hasta 2.000 caracteres.')
    finding=_finding(raw)
    if any(len(loc.document_ref)>256 or len(loc.section)>500 for loc in finding.locators):
        raise ValueError('La referencia o sección del soporte es demasiado larga.')
    with sqlite3.connect(db) as c:
        c.execute(SCHEMA)
        c.execute('BEGIN IMMEDIATE')
        current=_latest(c,report)
        revision=current[0] if current else 0
        if type(data.get('revision')) is not int or data['revision']!=revision:
            raise ValueError('La revisión documental ha cambiado. Vuelve a revisar la propuesta.')
        capture=_rebuild_capture(c,db,report)
        findings=[_finding(item) for item in current[2]['findings']] if current else []
        key=(finding.condition,finding.installment_ref)
        findings=[item for item in findings if (item.condition,item.installment_ref)!=key]+[finding]
        result=build_documentary_payment_human_review(capture=capture,review_ref=str(uuid4()),
            reviewer_ref=reviewer.strip(),reviewed_at=datetime.now(timezone.utc),
            findings=tuple(findings),previous_review_ref=current[2]['review_ref'] if current else None)
        payload=result.to_payload()
        c.execute('INSERT INTO company_payment_human_review VALUES(?,?,?,?,?,?)',
            (capture.fingerprint,report['dataset_id'],report['proposal_id'],revision+1,result.fingerprint,
             json.dumps(payload,ensure_ascii=False,sort_keys=True,separators=(',',':'))))
        return _summary((revision+1,result.fingerprint,payload))
