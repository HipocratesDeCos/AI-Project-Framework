"""Explicit hypothetical replenishment target; never an STK002 need authority.

Closing-day sensitivity model with constant declared demand and dated receipts.
"""
from copy import deepcopy
from datetime import date,timedelta
from decimal import Decimal,InvalidOperation,ROUND_CEILING,localcontext
from hashlib import sha256
import json

FIELDS={'dataset_id','article_id','unit','documentary_fingerprint','order_date','available_at_order','daily_demand','lead_time_days','target_days','safety_stock','purchase_step','receipts','actor','source_reference','acknowledge'}


def calculate(state,data):
    raw=data.get('stock_planning')
    if raw is None:return None
    if not isinstance(raw,dict) or set(raw)!=FIELDS:raise ValueError('Completa los supuestos de planificación de stock.')
    article=next((a for a in state['articles'] if a['article_id']==data.get('article_id') and a['supplier_id']==data.get('supplier_id')),None)
    if article is None:raise ValueError('Planificación sin artículo y proveedor compatibles.')
    if (raw['dataset_id'],raw['article_id'],raw['unit'],raw['documentary_fingerprint'],raw['order_date'])!=(state['info']['dataset_id'],article['article_id'],article['unit_as_documented'],state['documentary_context']['fingerprint'],data.get('order_date')):
        raise ValueError('Los supuestos de stock no corresponden al artículo, versión o fecha del pedido. Revisa y vuelve a declararlos.')
    if raw['acknowledge'] is not True:raise ValueError('Confirma que estos datos de stock son supuestos de simulación, sin duplicar reservas.')
    for key in ('actor','source_reference'):
        if not isinstance(raw[key],str) or not raw[key].strip() or len(raw[key])>256:raise ValueError('Indica responsable y referencia de la planificación, hasta 256 caracteres.')
    def number(value,label,positive=False):
        try:
            if isinstance(value,bool):raise ValueError()
            n=Decimal(str(value))
            if not n.is_finite() or n<0 or n>Decimal('1000000000') or positive and n<=0:raise ValueError()
            return n
        except (InvalidOperation,ValueError,TypeError):raise ValueError('Revisa '+label+': número finito '+('positivo' if positive else 'no negativo')+'.') from None
    values={k:number(raw[k],k,k in ('purchase_step',)) for k in ('available_at_order','daily_demand','lead_time_days','target_days','safety_stock','purchase_step')}
    lead=values['lead_time_days'];target=values['target_days']
    if lead!=lead.to_integral_value() or target!=target.to_integral_value() or lead>365 or not 1<=target<=365:raise ValueError('Entrega: 0 a 365 días; cobertura objetivo: 1 a 365 días, enteros.')
    start=date.fromisoformat(raw['order_date']);arrival=start+timedelta(days=int(lead));end=arrival+timedelta(days=int(target))
    receipts=raw['receipts']
    if not isinstance(receipts,list) or len(receipts)>20:raise ValueError('Declara hasta 20 entradas pendientes, o una lista vacía si no hay.')
    events={};canonical=[]
    for r in receipts:
        if not isinstance(r,dict) or set(r)!={'date','quantity'}:raise ValueError('Cada entrada requiere fecha y cantidad.')
        try:day=date.fromisoformat(r['date'])
        except (ValueError,TypeError):raise ValueError('Fecha de entrada pendiente no válida.') from None
        if not start<=day<=end:raise ValueError('Las entradas deben quedar entre pedido y fin de la cobertura objetivo.')
        qty=number(r['quantity'],'entrada pendiente',True)
        events[day]=events.get(day,Decimal(0))+qty;canonical.append(dict(date=day.isoformat(),quantity=str(qty)))
    current_qty=number(data['quantity'],'cantidad de compra',True)
    with localcontext() as ctx:
        ctx.prec=60
        balance=values['available_at_order'];needed=Decimal(0);before=[];points=[]
        for offset in range(int(lead+target)+1):
            day=start+timedelta(days=offset)
            if offset:balance-=values['daily_demand']
            balance+=events.get(day,Decimal(0))
            if day<arrival:before.append(balance)
            else:needed=max(needed,values['safety_stock']-balance)
            points.append(dict(date=day.isoformat(),without_purchase=str(balance),with_current_purchase=str(balance+(current_qty if day>=arrival else 0))))
        step=values['purchase_step'];quantity=(max(Decimal(0),needed)/step).to_integral_value(rounding=ROUND_CEILING)*step
        if quantity>Decimal('1000000000'):raise ValueError('La cantidad objetivo supera el rango de compra admitido.')
    before_shortfall=any(v<0 for v in before)
    assumptions=deepcopy(raw);assumptions.update({k:str(v) for k,v in values.items()});assumptions['receipts']=canonical
    result=dict(schema='PURCHASE-STOCK-HYPOTHESIS-01',status='PRE_DELIVERY_SHORTFALL' if before_shortfall else 'CALCULATED',
        assumptions=assumptions,arrival_date=arrival.isoformat(),target_end=end.isoformat(),scenario_quantity=str(quantity),current_quantity=str(current_qty),
        minimum_before_delivery=str(min(before)) if before else None,points=points,
        basis='Stock libre declarado al inicio del pedido; demanda adicional a las reservas ya descontadas; entradas y compra al cierre del día. Objetivo: conservar el stock de seguridad desde la recepción hasta el fin de cobertura.',
        need_authority='NOT_ESTABLISHED',origin='HYPOTHETICAL',decision_authority=False,operational_path='FORBIDDEN',
        limitations=['No acredita demanda futura, entradas confirmadas ni disponibilidad durante el día.','No modifica inventario, parámetros del Centro ni la autoridad STK002.','No se ejecuta una compra ni se registra aceptación del proveedor.'])
    result['fingerprint']=sha256(json.dumps(result,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    return result
