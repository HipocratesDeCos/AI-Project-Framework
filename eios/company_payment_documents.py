"""Read exact conserved payment support bytes; never fall back to current sources."""
import base64
from hashlib import sha256
import json
import sqlite3


def _hash(value):
    return sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,
                            separators=(',',':'),allow_nan=False).encode()).hexdigest()


def captured_document(db,report,document_ref):
    if not isinstance(document_ref,str) or not document_ref or len(document_ref)>256:
        raise ValueError('Indica una referencia documental válida.')
    execution=report.get('finance_execution') or {}
    summary=execution.get('documentary_capture') or {}
    if summary.get('status')!='CAPTURED_LISTED_ASSOCIATIONS':
        raise ValueError('Esta revisión no conserva una captura documental de pagos.')
    with sqlite3.connect(db) as c:
        if not c.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='company_payment_documentary_capture'").fetchone():
            raise ValueError('No se encuentra la captura conservada.')
        row=c.execute('SELECT finance_package_fingerprint,payload FROM company_payment_documentary_capture WHERE fingerprint=? AND dataset_id=? AND proposal_id=?',
            (summary['fingerprint'],report['dataset_id'],report['proposal_id'])).fetchone()
    if row is None:
        raise ValueError('La captura no pertenece a esta revisión y propuesta.')
    try:
        payload=json.loads(row[1])
        package=payload['finance_package']
        if (_hash(payload)!=summary['fingerprint'] or payload['schema_version']!='DOC-PAY-CAP-01/v0.1'
                or payload['operation_ref']!=report['proposal_id'] or payload['case_kind']!='SYNTHETIC'
                or row[0]!=execution['finance_package_fingerprint']
                or payload['finance_package_fingerprint']!=row[0] or _hash(package)!=row[0]
                or package['finance_input']!=execution['finance_input']):
            raise ValueError('La captura o su paquete financiero no coincide con la revisión guardada.')
        found=[d for d in payload['documents'] if d['document_ref']==document_ref]
        if len(found)!=1 or not any(locator['document_ref']==document_ref
                                   for binding in payload['bindings'] for locator in binding['locators']):
            raise ValueError('El documento no está conservado y asociado en esta captura.')
        content=base64.b64decode(found[0]['content_base64'],validate=True)
        digest=sha256(content).hexdigest()
        if digest!=found[0]['sha256']:
            raise ValueError('La huella del documento conservado no coincide.')
        context=report['proposal'].get('documentary_context_at_save') or {}
        sources=[source for source in context.get('sources',[]) if source.get('document_ref')==document_ref]
        if len(sources)!=1 or sources[0].get('stored_bytes_sha256')!=digest:
            raise ValueError('El documento no coincide con el contexto de la propuesta.')
        source=sources[0]
        metadata=source.get('metadata')
        name=source.get('filename') or (metadata.get('filename') if isinstance(metadata,dict) else None)
        if not isinstance(name,str):
            name='soporte-'+digest[:12]+'.bin'
        name=name.replace(chr(92),'/').rsplit('/',1)[-1]
        name=''.join(ch for ch in name if ord(ch)>=32 and ord(ch)!=127).strip()[:200]
        if name in ('','.','..'):
            name='soporte-'+digest[:12]+'.bin'
        return dict(content=content,filename=name,source_sha256=digest,document_ref=document_ref)
    except (KeyError,TypeError) as error:
        raise ValueError('La captura conservada tiene un formato incompatible.') from error
