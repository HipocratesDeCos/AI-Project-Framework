"""Immutable, explicit synthetic purchase comparisons; no acceptance authority."""
from copy import deepcopy
from datetime import datetime, timezone, date
from decimal import Decimal
from hashlib import sha256
import json
import sqlite3
from uuid import uuid4

from eios.company_purchase_cash_preview import preview
from eios.company_proposal_context import capture_context

FIELDS = {'unit_price', 'pricing_mode', 'discount_mode', 'discount_value', 'due_date',
          'shipping_due_date', 'payment_installments', 'vat_percent', 'shipping_mode',
          'shipping_net', 'shipping_vat_percent', 'shipping_billed_by'}
TABLE = '''CREATE TABLE IF NOT EXISTS purchase_condition_comparison (
 comparison_id TEXT PRIMARY KEY, dataset_id TEXT NOT NULL, proposal_id TEXT NOT NULL,
 created_at TEXT NOT NULL, payload TEXT NOT NULL,
 FOREIGN KEY(proposal_id) REFERENCES manual_purchase_proposal(proposal_id))'''


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def original_input(proposal):
    t = proposal['commercial_terms']; s = t['shipping']
    data = {k: proposal[k] for k in ('article_id','supplier_id','quantity','vat_percent','order_date','due_date')}
    data.update(unit_price=t['entered_unit_price'], pricing_mode=t['pricing_mode'],
                discount_mode=t['discount_mode'], shipping_mode=s['mode'])
    if t['discount_value'] is not None: data['discount_value'] = t['discount_value']
    if s['mode'] == 'BUYER':
        data.update(shipping_net=s['net'], shipping_vat_percent=s['vat_percent'],
                    shipping_billed_by=s['billed_by'], shipping_due_date=s['due_date'])
    plan = proposal.get('payment_plan', {})
    if plan.get('status') != 'NOT_DECLARED' and plan.get('installments'):
        data['payment_installments'] = [{k:i[k] for k in ('component','amount','due_date')} for i in plan['installments']]
    return data


def condition(value):
    if not isinstance(value,dict) or set(value)-{'origin','source_reference','acceptance','acceptance_reference','valid_until'}:
        raise ValueError('Metadatos de condición no válidos.')
    origin=value.get('origin'); acceptance=value.get('acceptance','PENDING')
    if origin not in ('DOCUMENTED','HYPOTHETICAL','UNCONFIRMED') or acceptance not in ('PENDING','DECLARED_ACCEPTED'):
        raise ValueError('Origen o aceptación no válidos.')
    result=dict(origin=origin,acceptance=acceptance,evidence_status='DECLARED_UNVERIFIED')
    for field in ('source_reference','acceptance_reference','valid_until'):
        item=value.get(field)
        if item is not None and (not isinstance(item,str) or len(item)>256): raise ValueError('Referencia de condición no válida.')
        result[field]=item
    if origin=='DOCUMENTED' and not result['source_reference']: raise ValueError('La condición documentada requiere referencia de soporte.')
    if acceptance=='DECLARED_ACCEPTED' and (origin!='DOCUMENTED' or not result['acceptance_reference']):
        raise ValueError('Declarar aceptación requiere condición documentada y soporte propio; no acredita aceptación verificada.')
    if result['valid_until']: date.fromisoformat(result['valid_until'])
    return result


def compare(desk,data):
    dataset=str(data['dataset_id']); proposal_id=str(data['proposal_id'])
    from eios.company_exclusive_workbook import require_active
    require_active(desk.db,dataset)
    state=desk.sales_state(dataset)
    proposal=next((p for p in state['purchases'] if p['proposal_id']==proposal_id),None)
    if proposal is None: raise ValueError('Propuesta no encontrada en esta versión.')
    context=state['documentary_context']
    if data.get('documentary_context_fingerprint')!=context['fingerprint'] or proposal.get('documentary_context_at_save')!=context:
        raise ValueError('La versión documental ha cambiado. Prepara una propuesta vigente.')
    if context.get('material_nature')!='SYNTHETIC': raise ValueError('Solo se comparan propuestas sintéticas.')
    actor=data.get('actor'); variants=data.get('alternatives')
    if not isinstance(actor,str) or not actor.strip() or len(actor)>128: raise ValueError('Indica responsable de la comparación.')
    if not isinstance(variants,list) or not 1<=len(variants)<=10: raise ValueError('Indica entre una y diez alternativas.')
    base=original_input(proposal)
    baseline=preview(desk.db,state,base,alternatives=False)
    if baseline['status']=='PENDING': raise ValueError(baseline['message'])
    rows=[]
    for variant in variants:
        if not isinstance(variant,dict) or set(variant)!={'label','patch','conditions'}: raise ValueError('Cada alternativa requiere nombre, cambios y condiciones.')
        label=variant['label']; patch=variant['patch']; metadata=variant['conditions']
        if not isinstance(label,str) or not label.strip() or len(label)>100: raise ValueError('Nombre de alternativa no válido.')
        if not isinstance(patch,dict) or not patch or set(patch)-FIELDS: raise ValueError('Solo se comparan coste, descuento, IVA, portes y calendario; cantidad y proveedor permanecen fijos.')
        if not isinstance(metadata,dict) or set(metadata)!=set(patch): raise ValueError('Identifica el origen de cada condición modificada.')
        conditions={k:condition(v) for k,v in metadata.items()}
        values=deepcopy(base);values.update(patch)
        result=preview(desk.db,state,values,alternatives=False)
        if result['status']!='PENDING' and (result['parameter_activation']!=baseline['parameter_activation'] or result['financial_source_fingerprint']!=baseline['financial_source_fingerprint']):
            raise ValueError('El contexto financiero cambió entre alternativas. Recalcula.')
        for item in conditions.values():
            item['validity_status']='EXPIRED_AT_COMPARISON' if item['valid_until'] and item['valid_until']<datetime.now(timezone.utc).date().isoformat() else 'DECLARED_VALIDITY_NOT_VERIFIED' if item['valid_until'] else 'NOT_DECLARED'
        rows.append(dict(label=label.strip(),input=values,conditions=conditions,result=result,
            saving=None if result['status']=='PENDING' else str(Decimal(baseline['total'])-Decimal(result['total'])),
            original_conditions_status='UNCONFIRMED_UNLESS_SEPARATELY_EVIDENCED'))
    result=dict(schema='PURCHASE-CONDITION-COMPARISON-01',comparison_id=str(uuid4()),dataset_id=dataset,
        proposal_id=proposal_id,company_id=context['company_id'],created_at=datetime.now(timezone.utc).isoformat(),
        actor=actor.strip(),material_nature='SYNTHETIC',documentary_context=context,
        parameter_activation=baseline['parameter_activation'],financial_source_fingerprint=baseline['financial_source_fingerprint'],
        calculation_version='PURCHASE-CONDITION-COMPARISON-01/v1',baseline=baseline,alternatives=rows,
        winner=None,decision_authority=False,operational_path='FORBIDDEN',viability_status='NOT_EVALUATED')
    result['fingerprint']=digest(result)
    with sqlite3.connect(desk.db) as c:
        c.execute('PRAGMA foreign_keys=ON'); c.execute(TABLE);c.execute('BEGIN IMMEDIATE')
        current=capture_context(c,dataset)
        activation=c.execute('SELECT payload FROM company_finance_parameter_activation WHERE company_id=? AND as_of_date=?',
            (context['company_id'],context['documentary_cutoff'])).fetchone()
        if current!=context or not activation or json.loads(activation[0])!=result['parameter_activation']:
            raise ValueError('Fuentes o parámetros han cambiado durante el cálculo. Recalcula.')
        c.execute('INSERT INTO purchase_condition_comparison VALUES(?,?,?,?,?)',
            (result['comparison_id'],dataset,proposal_id,result['created_at'],json.dumps(result)))
    return result


def history(desk,data):
    dataset=str(data['dataset_id']);proposal=str(data['proposal_id'])
    with sqlite3.connect(desk.db) as c:
        c.execute(TABLE)
        context=capture_context(c,dataset)
        activation=c.execute('SELECT payload FROM company_finance_parameter_activation WHERE company_id=? AND as_of_date=?',
            (context['company_id'],context['documentary_cutoff'])).fetchone() if c.execute("SELECT 1 FROM sqlite_master WHERE name='company_finance_parameter_activation'").fetchone() else None
        items=[json.loads(row[0]) for row in c.execute('SELECT payload FROM purchase_condition_comparison WHERE dataset_id=? AND proposal_id=? ORDER BY created_at',(dataset,proposal))]
    for item in items:
        payload={k:v for k,v in item.items() if k!='fingerprint'}
        if item.get('fingerprint')!=digest(payload):
            raise ValueError('El estudio guardado no conserva su integridad.')
    return dict(comparisons=[dict(record=r,stale=r['documentary_context']!=context or not activation or r['parameter_activation']!=json.loads(activation[0])) for r in items])
