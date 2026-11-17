"""Bounded combination of sourced hypotheses and descriptive metric comparison.

Not the canonical Scenario Engine, a decision ranking, or a new parameter authority.
"""
from copy import deepcopy
from datetime import date,timedelta
from decimal import Decimal
from itertools import product
from .company_commercial_terms import commercial_terms
from .company_purchase_opportunities import historical_reference,resized_installments

LIMIT=64


def search(state,data,quote,plan,target,end,scenario,evaluate):
    report=dict(schema='PURCHASE-COMBINATION-SEARCH-01',limit=LIMIT,evaluated=0,accepted=0,rejected=[],truncated=False,decision_authority=False,operational_path='FORBIDDEN')
    article=next(a for a in state['articles'] if a['article_id']==data['article_id'])
    prices=[None];quantities=[None];shifts=[None]
    ref=historical_reference(state,data,article)
    if ref:
        try:
            p=Decimal(str(ref['effective_net_unit_price']))
            if p.is_finite() and 0<p<Decimal(quote['unit_price']):prices.append((p,deepcopy(ref)))
        except (ValueError,TypeError,ArithmeticError):report['rejected'].append(dict(axes=1,changes=['precio histórico'],reason='Referencia de precio no válida.'))
    if target and target['status']=='CALCULATED' and 0<Decimal(target['scenario_quantity'])!=Decimal(data['quantity']):quantities.append(target)
    last=max(due for due in [date.fromisoformat(data['due_date'])]+[date.fromisoformat(r['due_date']) for r in data.get('payment_installments') or []]+([date.fromisoformat(data['shipping_due_date'])] if data.get('shipping_due_date') else []))
    dates={}
    for row in state['sales_financial_context']['cash_flows']:
        f=row['canonical'];when=date.fromisoformat(f['due_date'])
        if f['flow_type']=='COLLECTION' and Decimal(str(f['amount']))>0 and last<when<=end:dates.setdefault(when,[]).append(f['flow_id'])
    for day,ids in sorted(dates.items())[:64]:shifts.append((day,ids))
    accepted=[]
    combinations=list(product(prices,quantities,shifts))
    combinations.sort(key=lambda c:('' if c[2] is None else c[2][0].isoformat(),-sum(v is not None for v in c)))
    for price,quantity,shift in combinations:
        axes=sum(v is not None for v in (price,quantity,shift))
        if axes<2:continue
        if report['evaluated']>=LIMIT:report['truncated']=True;break
        report['evaluated']+=1;patch={};labels=[];sources=[]
        try:
            if target and target['status']=='PRE_DELIVERY_SHORTFALL':raise ValueError('La falta de stock anterior a la entrega requiere revisar su fecha, no combinar solo precio y pagos.')
            if price:
                patch.update(unit_price=str(price[0]),pricing_mode='NET',discount_mode='NONE',discount_value=None);labels.append('precio histórico');sources.append(dict(kind='HISTORICAL_PRICE',invoice_number=price[1].get('invoice_number'),issue_date=price[1]['issue_date'],source_refs=price[1].get('source_refs',[])))
            if quantity:
                patch['quantity']=quantity['scenario_quantity'];labels.append('cantidad objetivo');sources.append(dict(kind='STOCK_TARGET',planning_fingerprint=quantity['fingerprint'],reference=quantity['assumptions']['source_reference']))
            if target and Decimal(patch.get('quantity',data['quantity']))<Decimal(target['scenario_quantity']):raise ValueError('La cantidad queda por debajo del objetivo de stock declarado.')
            q=commercial_terms(dict(data,**patch))
            if plan['status']!='NOT_DECLARED' and (price or quantity):patch['payment_installments']=resized_installments(data,q,quote)
            if shift:
                delta=timedelta(days=(shift[0]-last).days);labels.append('pago tras cobro previsto');sources.append(dict(kind='COLLECTION_ALIGNED_PAYMENT',date=shift[0].isoformat(),flow_ids=shift[1]))
                patch['due_date']=(date.fromisoformat(data['due_date'])+delta).isoformat()
                if data.get('shipping_due_date'):patch['shipping_due_date']=(date.fromisoformat(data['shipping_due_date'])+delta).isoformat()
                if plan['status']!='NOT_DECLARED':patch['payment_installments']=[dict(r,due_date=(date.fromisoformat(r['due_date'])+delta).isoformat()) for r in patch.get('payment_installments',data['payment_installments'])]
            checked,reason=evaluate(dict(data,**patch))
            if not checked:raise ValueError(reason)
            if Decimal(checked[0]['operation_total'])>=Decimal(quote['operation_total']) and Decimal(checked[3]['minimum_balance'])<=Decimal(scenario['minimum_balance']) and not quantity:
                raise ValueError('No mejora coste ni saldo mínimo respecto a la propuesta activa.')
            accepted.append(dict(kind='COMBINED',title='Combinar '+', '.join(labels),patch=patch,checked=checked,
                basis='Combinación de hipótesis con fuentes identificadas. Precio, disponibilidad, descuentos y portes por volumen requieren confirmación; el cobro previsto no está garantizado.',
                source=dict(components=sources,invoice_number=' + '.join(str(s.get('invoice_number') or s.get('reference') or ', '.join(s.get('flow_ids',[]))) for s in sources),issue_date=data['order_date']),
                negotiation_text='Solicitamos estudiar conjuntamente estas condiciones: '+', '.join(labels)+'. Cantidad '+checked[0]['quantity']+' '+article['unit_as_documented']+', precio neto unitario '+checked[0]['unit_price']+' EUR, vencimiento de mercancía '+checked[0]['due_date']+'. Sujeto a confirmación y aceptación expresa.'))
        except (ValueError,TypeError,ArithmeticError) as error:report['rejected'].append(dict(axes=axes,changes=labels,reason=str(error)))
    report['accepted']=len(accepted)
    return accepted,report


def metric_comparison(current,alternatives):
    rows=[dict(id='CURRENT',**current)]+[dict(a,id='ALT-'+str(i)) for i,a in enumerate(alternatives,1)]
    for r in rows:
        dominators=[]
        for other in rows:
            if r['id']==other['id'] or Decimal(r['quantity'])!=Decimal(other['quantity']):continue
            cost,liquid=Decimal(r['total']),Decimal(r['minimum_balance']);oc,ol=Decimal(other['total']),Decimal(other['minimum_balance'])
            if oc<=cost and ol>=liquid and (oc<cost or ol>liquid):dominators.append(other['id'])
        r['metric_comparison']=dict(status='OTHER_OPTION_IMPROVES_METRICS' if dominators else 'NO_OTHER_OPTION_IMPROVES_BOTH',compared_with_same_quantity_only=True,dominated_by=dominators,scope='TOTAL_COST_AND_MINIMUM_BALANCE_ONLY_NOT_BUSINESS_PREFERENCE')
    current['metric_comparison']=rows[0]['metric_comparison']
    for r,a in zip(rows[1:],alternatives):a['comparison_id']=r['id'];a['metric_comparison']=r['metric_comparison']
