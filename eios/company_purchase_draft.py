"""Prepare an unsaved copy of a source-bound study; never mutate its original."""
from copy import deepcopy
from hashlib import sha256
import json

from eios.company_purchase_comparison import original_input


def fingerprint(proposal):
    return sha256(json.dumps(proposal,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()


def source_reference(state,proposal_id):
    proposal=next((p for p in state['purchases'] if p['proposal_id']==proposal_id),None)
    if proposal is None:raise ValueError('Estudio no encontrado en la versión seleccionada.')
    saved=proposal.get('documentary_context_at_save')
    if not saved or saved.get('fingerprint')!=state['documentary_context']['fingerprint']:
        raise ValueError('El contexto del estudio ha cambiado o no se conserva. No se copian sus supuestos a otra versión documental.')
    return proposal,dict(schema='PURCHASE-DRAFT-SOURCE-01',dataset_id=state['info']['dataset_id'],proposal_id=proposal_id,reference=proposal['reference'],proposal_fingerprint=fingerprint(proposal))


def validate_source(state,data):
    raw=data.get('draft_source')
    if raw is None:return None
    if not isinstance(raw,dict):raise ValueError('Origen del borrador no válido.')
    proposal,expected=source_reference(state,raw.get('proposal_id'))
    if raw!=expected or (data.get('article_id'),data.get('supplier_id'))!=(proposal['article_id'],proposal['supplier_id']):
        raise ValueError('El origen del borrador no coincide con este artículo, proveedor o estudio.')
    return expected


def prepare(desk,data):
    from eios.company_exclusive_workbook import require_active
    dataset=str(data['dataset_id']);require_active(desk.db,dataset)
    state=desk.state(dataset)
    if data.get('documentary_context_fingerprint')!=state['documentary_context']['fingerprint']:
        raise ValueError('La versión documental ha cambiado. Recarga antes de crear el borrador.')
    proposal,source=source_reference(state,str(data['proposal_id']))
    if not proposal.get('commercial_terms'):raise ValueError('Este estudio antiguo no conserva las condiciones necesarias para copiarlo.')
    values=original_input(proposal)
    values.update(dataset_id=dataset,documentary_context_fingerprint=state['documentary_context']['fingerprint'],delivery_location=proposal.get('delivery_location'),draft_source=source)
    used={p['reference'] for p in state['purchases']};stem=proposal['reference'][:80]+'-BORRADOR';reference=stem;index=2
    while reference in used:reference=stem+'-'+str(index);index+=1
    values['reference']=reference
    variants=deepcopy((proposal.get('negotiation_at_save') or {}).get('alternatives') or [])
    if variants:
        values['negotiation_alternatives']=[dict(slot=v['slot'],patch=v['patch'],condition=dict(origin=v['condition']['origin'],source_reference=v['condition'].get('source_reference'),acceptance='PENDING')) for v in variants]
    else:
        keys={'unit_price','pricing_mode','discount_mode','discount_value','due_date','vat_percent','shipping_mode','shipping_net','shipping_vat_percent','shipping_billed_by','shipping_due_date'}
        patch={k:values.get(k) for k in keys};patch.setdefault('discount_value',None)
        values['negotiation_alternatives']=[dict(slot='mine',patch=patch,condition=dict(origin='HYPOTHETICAL',source_reference=proposal['reference'],acceptance='PENDING'))]
    stock=deepcopy(proposal.get('stock_planning_at_save'))
    if stock:
        raw=stock['assumptions']
        if (raw['dataset_id'],raw['article_id'],raw['unit'],raw['documentary_fingerprint'],raw['order_date'])!=(dataset,proposal['article_id'],proposal['unit'],state['documentary_context']['fingerprint'],proposal['order_date']):
            raise ValueError('Los supuestos conservados no corresponden al estudio. No se copian.')
        raw['acknowledge']=False;values['stock_planning']=raw
    return dict(schema='PURCHASE-STUDY-TO-DRAFT-01',values=values,decision_authority=False,operational_path='FORBIDDEN',
        message='Borrador nuevo, sin guardar. Revisa las condiciones y confirma los supuestos de stock copiados. El estudio original permanece intacto.')
