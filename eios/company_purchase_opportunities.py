"""Source-backed purchase hypotheses using existing quotes and cash checks.

No price authority, quantity policy, supplier acceptance or operational decision.
"""
from copy import deepcopy
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation, ROUND_HALF_EVEN, localcontext


def opportunities(state, data, quote, plan, scenario, end, check):
    from eios.company_commercial_terms import commercial_terms
    notes=[]; candidates=[]
    article=next(a for a in state['articles'] if a['article_id']==data['article_id'])
    rows=state.get('history',{}).get(data['article_id'],[])
    horizon=min(data['order_date'],state['info']['as_of_date'])
    rows=[r for r in rows if r.get('issue_date','')<=horizon]
    latest=max((r.get('issue_date','') for r in rows),default=None)
    refs=[r for r in rows if r.get('issue_date')==latest]
    stale=(state.get('selected_purchase_history') or {}).get('status')=='STALE'
    ref=refs[0] if len(refs)==1 and not stale else None
    if ref and ref.get('comparable') and ref.get('unit')==article['unit_as_documented'] and ref.get('currency')=='EUR':
        try:
            price=Decimal(str(ref['effective_net_unit_price']))
            if not price.is_finite() or price<=0:raise ValueError()
            if price<Decimal(quote['unit_price']):
                patch=dict(unit_price=str(price),pricing_mode='NET',discount_mode='NONE',discount_value=None)
                if plan['status']!='NOT_DECLARED':
                    revised=commercial_terms(dict(data,**patch))
                    with localcontext() as ctx:
                        ctx.prec=60
                        schedule=deepcopy(data['payment_installments'])
                        merchandise=[r for r in schedule if r['component']=='MERCHANDISE']
                        remaining=Decimal(revised['total']);old=Decimal(quote['total'])
                        for index,row in enumerate(merchandise):
                            amount=remaining if index==len(merchandise)-1 else (Decimal(row['amount'])*Decimal(revised['total'])/old).quantize(Decimal('.01'),rounding=ROUND_HALF_EVEN)
                            if amount<=0 or amount>remaining:raise ValueError()
                            row['amount']=format(amount,'.2f');remaining-=amount
                    patch['payment_installments']=schedule
                tested=check(dict(data,**patch))
                if tested and Decimal(tested[0]['operation_total'])<Decimal(quote['operation_total']):
                    candidates.append(dict(kind='HISTORICAL_PRICE',title='Negociar el precio neto de la última compra comparable',patch=patch,checked=tested,
                        basis='Última compra única comparable de este artículo y proveedor, en la misma unidad y moneda. Es una referencia histórica; no acredita una oferta vigente.',
                        source=dict(issue_date=ref['issue_date'],invoice_number=ref.get('invoice_number'),source_refs=deepcopy(ref.get('source_refs',[])),net_unit_price=str(price)),
                        negotiation_text='Solicitamos mantener el precio neto histórico de '+str(price)+' EUR por '+article['unit_as_documented']+'. Sujeto a confirmación del proveedor; sin aplicar de nuevo el descuento histórico.'))
                else:notes.append('La referencia histórica no ofrece una reducción final del coste compatible con la reserva y el calendario actual.')
            else:notes.append('La referencia histórica comparable no mejora el precio neto que has introducido.')
        except (ValueError,TypeError,KeyError,InvalidOperation,ArithmeticError):
            notes.append('No se puede trasladar el precio histórico al calendario declarado sin generar cuotas inválidas.')
    else:notes.append('Para proponer un precio falta una última compra única comparable y vigente como fuente, con proveedor, unidad y moneda coincidentes.')
    last=max(date.fromisoformat(r['due_date']) for r in plan.get('installments',[])) if plan['status']!='NOT_DECLARED' else max(date.fromisoformat(data['due_date']),date.fromisoformat(data.get('shipping_due_date') or data['due_date']))
    collections=sorted({date.fromisoformat(f['canonical']['due_date']) for f in state['sales_financial_context']['cash_flows'] if f['canonical']['flow_type']=='COLLECTION' and Decimal(str(f['canonical']['amount']))>0 and last<date.fromisoformat(f['canonical']['due_date'])<=end})
    for target in collections[:64]:
        shift=(target-last).days
        patch={'due_date':(date.fromisoformat(data['due_date'])+timedelta(days=shift)).isoformat()}
        if data.get('shipping_due_date'):patch['shipping_due_date']=(date.fromisoformat(data['shipping_due_date'])+timedelta(days=shift)).isoformat()
        if plan['status']!='NOT_DECLARED':patch['payment_installments']=[dict(r,due_date=(date.fromisoformat(r['due_date'])+timedelta(days=shift)).isoformat()) for r in data['payment_installments']]
        tested=check(dict(data,**patch))
        if tested and Decimal(tested[3]['minimum_balance'])>Decimal(scenario['minimum_balance']):
            candidates.append(dict(kind='COLLECTION_ALIGNED_PAYMENT',title='Negociar pagos después de un cobro previsto',patch=patch,checked=tested,
                basis='Desplazamiento del calendario hasta una fecha de cobro ya incluida en la previsión. Mejora el saldo mínimo; no reduce el coste ni garantiza ese cobro.',
                source=dict(collection_date=target.isoformat(),shift_days=shift,flow_ids=[f['canonical']['flow_id'] for f in state['sales_financial_context']['cash_flows'] if f['canonical']['flow_type']=='COLLECTION' and f['canonical']['due_date']==target.isoformat()]),
                negotiation_text='Solicitamos desplazar el calendario '+str(shift)+' días, manteniendo los importes. Sujeto a aceptación del proveedor y confirmación de cobros.'))
            break
    if not any(c['kind']=='COLLECTION_ALIGNED_PAYMENT' for c in candidates):notes.append('No se ha encontrado, entre las primeras 64 fechas de cobro posteriores disponibles, un aplazamiento que mejore el saldo mínimo y respete la reserva dentro del horizonte.')
    notes.append('Cantidad sin optimizar: no se reduce por ahorro de caja sin justificar demanda, existencias, entregas y cobertura.')
    stock=state.get('inventory',{}).get(data['article_id'])
    stock_context=dict(status='NOT_DETERMINED',message='Sin inventario comparable; no se acredita la necesidad de compra.')
    if stock and stock.get('unit')==article['unit_as_documented'] and stock.get('available') is not None:
        stock_context=dict(status='DOCUMENTARY_REFERENCE',available=str(stock['available']),purchase_quantity=str(data['quantity']),unit=article['unit_as_documented'],as_of_date=stock.get('as_of_date'),message='Stock documental disponible. Las alternativas mantienen la cantidad; no acreditan cobertura futura ni necesidad de compra.')
    return candidates,notes,stock_context
