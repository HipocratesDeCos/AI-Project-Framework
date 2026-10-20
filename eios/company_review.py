"""Dated descriptive review of a saved proposal; no decision or rule authority."""
from copy import deepcopy
from datetime import date
from decimal import Decimal
import hashlib
import json

VERSION = 'COMPANY-CONTEXT-REVIEW-01'


def review_proposal(proposal, info, history, inventory, planning):
    """Freeze the saved operation and dated context without generating a verdict."""
    proposal = deepcopy(proposal)
    ordered = date.fromisoformat(proposal['order_date'])
    cutoff = date.fromisoformat(info['as_of_date'])
    horizon = min(ordered, cutoff)
    rows = [deepcopy(r) for r in history if date.fromisoformat(r['issue_date']) <= horizon]
    rows.sort(key=lambda r: (r['issue_date'], r.get('invoice_number', '')), reverse=True)
    latest = [r for r in rows if r['issue_date'] == rows[0]['issue_date']] if rows else []
    price = dict(status='UNAVAILABLE', message='Sin compra histórica anterior o igual a la fecha del pedido.')
    if len(latest) > 1:
        price['message'] = 'Varias líneas en la última fecha: no hay una referencia única.'
    elif latest:
        r = latest[0]
        if r.get('comparable') and r.get('unit') == proposal['unit'] and r.get('currency') == proposal['currency']:
            previous = Decimal(r['effective_net_unit_price'])
            current = Decimal(proposal['unit_price'])
            if previous.is_finite() and previous > 0 and current.is_finite() and current > 0:
                price = dict(status='COMPARABLE', reference=deepcopy(r),
                             proposed_net_unit_price=str(current), difference_per_unit=str(current-previous),
                             difference_percent=str(((current-previous)/previous*100).quantize(Decimal('.01'))),
                             message='Comparación descriptiva de precios netos; no determina si conviene comprar.')
        if price['status'] == 'UNAVAILABLE':
            price['message'] = 'La última compra no permite comparar moneda, unidad o precio neto.'
    stock = dict(status='UNAVAILABLE', message='Falta inventario compatible anterior o igual a la fecha del pedido.')
    if inventory and all(inventory.get(k) == proposal.get(v) for k,v in
                         [('dataset_id','dataset_id'),('article_id','article_id'),('unit','unit')]):
        stock_date = date.fromisoformat(inventory['as_of_date'])
        if stock_date <= horizon:
            stock = dict(status='DATED_SYNTHETIC_CONTEXT', inventory=deepcopy(inventory),
                         message='Existencias sintéticas a la fecha indicada. No acreditan el stock actual ni incluyen esta propuesta.')
            if (planning and planning.get('status') in ('FINITE','UNBOUNDED')
                    and planning.get('as_of_date') == inventory['as_of_date']
                    and planning.get('unit') == proposal['unit']):
                stock['coverage'] = deepcopy(planning)
                stock['forecast_applicable_on_order_date'] = stock_date <= ordered <= date.fromisoformat(planning['valid_to'])
    report = dict(version=VERSION, dataset_id=proposal['dataset_id'], proposal_id=proposal['proposal_id'],
                  reference=proposal['reference'], company_id=info['company']['company_id'],
                  documentary_cutoff=info['as_of_date'], operation_date=proposal['order_date'],
                  proposal=proposal, price=price, stock=stock,
                  status='PARTIAL_CONTEXT_REVIEW', title='REVISIÓN PARCIAL · EVALUACIÓN COMPLETA PENDIENTE',
                  reason='Puedes consultar precio y existencias de referencia. Falta la evaluación financiera y la conexión con el decisor.',
                  finance=dict(status='NOT_EVALUATED', message='No se ha calculado el efecto de esta propuesta sobre la tesorería y sus vencimientos.'),
                  pending=['Evaluación financiera de la operación y mandato de tesorería.',
                           ('Portes pendientes de confirmar, otros gastos y condiciones completas de pago.'
                            if proposal.get('operation_total') is None else
                            'Otros gastos y condiciones completas de pago; portes declarados conservados en la propuesta.'),
                           'Pedidos pendientes de recibir y vigencia del inventario.',
                           'Evaluación de reglas y conclusión del decisor.'],
                  material_nature='SYNTHETIC', decision_authority=False, operational_path='FORBIDDEN')
    encoded=json.dumps(report,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
    report['review_id']=hashlib.sha256(encoded).hexdigest()
    return report
