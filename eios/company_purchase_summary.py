"""Descriptive synthesis of existing purchase results; no new decision authority."""
from decimal import Decimal, ROUND_FLOOR


def summarize(result):
    status=result['status'];scenario=result.get('scenario') or {};terms=result.get('current_terms') or {}
    stock=result.get('stock_planning');review=result.get('quantity_review') or {}
    summary=dict(schema='PURCHASE-SUMMARY-01',status=status,
        title={'PENDING':'COMPLETA LA SIMULACIÓN','SHORTFALL':'LA PROPUESTA NO RESPETA LA RESERVA',
               'WITHIN_DECLARED_SCENARIO':'LA PROPUESTA RESPETA LA RESERVA PREVISTA'}[status],
        explanation=result.get('message',''),facts=[],pending=[],alternatives=[],
        decision_authority=False,operational_path='FORBIDDEN',
        scope='Síntesis descriptiva del escenario de prueba. No confirma una compra ni la aceptación del proveedor.')
    def fact(label,value,source):summary['facts'].append(dict(label=label,value=value,source=source))
    total=terms.get('total') or (result.get('balance_comparison') or {}).get('purchase_amount')
    if total is not None:
        basis=(result.get('balance_comparison') or {}).get('amount_basis')
        fact('Total mercancía con IVA' if basis=='MERCHANDISE_ONLY' else 'Total con IVA y portes',total,'commercial_terms')
    if scenario:
        fact('Saldo mínimo previsto',scenario['minimum_balance'],'scenario.minimum_balance')
        fact('Reserva mínima',result['treasury_minimum'],'parameter_activation.P-FIN-002')
        if status=='SHORTFALL':fact('Falta para respetar la reserva',scenario['deficit'],'scenario.deficit')
    if stock:
        safety=Decimal(stock['assumptions']['safety_stock'])
        after=[Decimal(p['with_current_purchase']) for p in stock['points'] if p['date']>=stock['arrival_date']]
        enough=bool(after) and min(after)>=safety
        if stock['status']=='PRE_DELIVERY_SHORTFALL':
            text='Falta stock antes de la entrega prevista; cambiar solo la cantidad recibida no resuelve ese tramo.'
        elif enough:text='La cantidad actual mantiene la seguridad declarada desde la recepción hasta el final de la cobertura objetivo.'
        else:text='La cantidad actual no mantiene la seguridad declarada durante toda la cobertura objetivo.'
        summary['stock']=dict(status=stock['status'],message=text,current_meets_target=stock['status']!='PRE_DELIVERY_SHORTFALL' and enough,
            scenario_quantity=stock['scenario_quantity'],source=stock['fingerprint'],
            limitation='Resultado condicionado al consumo, las entradas y los plazos declarados; necesidad de compra sin acreditar.')
        if stock['status']=='PRE_DELIVERY_SHORTFALL' or not enough:summary['pending'].append('Revisa stock libre, consumo y entregas; contrasta la cantidad objetivo y el tramo anterior a la recepción.')
    elif (result.get('reference_stock_coverage') or review.get('coverage')):
        ref=result.get('reference_stock_coverage') or review['coverage']
        days=str(Decimal(ref['coverage_days']).to_integral_value(rounding=ROUND_FLOOR)) if ref.get('status')=='FINITE' else None
        summary['stock']=dict(status='REFERENCE_ONLY',coverage_days=days,as_of_date=ref['as_of_date'],
            current_meets_target=None,source='reference_stock_coverage',
            message=('Cobertura de referencia: '+days+' días al '+ref['as_of_date']+'.') if days is not None else 'Sin consumo previsto en la referencia.',
            limitation='No incluye esta compra. Revisa y confirma la planificación del libro para evaluar cantidad y entrega.')
        summary['pending'].append('Revisa y confirma la planificación del libro para evaluar la cantidad y la entrega de esta compra.')
    else:
        summary['stock']=dict(status='NOT_ASSESSED',message='La necesidad y la cobertura de esta cantidad no están justificadas.',
            source='quantity_review',limitation='El inventario histórico y el mínimo de stock no sustituyen una previsión aplicable.')
        summary['pending'].append('Completa los supuestos de stock: disponible al pedido, consumo, plazo, entradas, seguridad y cobertura objetivo.')
        summary['stock']['missing']=[dict(item) for item in review.get('missing',[])]
    for option in result.get('alternatives',[]):
        summary['alternatives'].append(dict(reference=option.get('comparison_id'),title=option['title'],
            quantity=option['quantity'],unit=option['unit'],total=option['total'],savings=option['savings'],
            minimum_balance=option['minimum_balance'],same_quantity=option.get('stock_effect')=='SAME_QUANTITY',
            basis=option['basis'],source=option.get('source'),supplier_acceptance='NOT_CONFIRMED'))
    stress=terms.get('collection_sensitivity');excluded=(result.get('collection_sensitivity') or {}).get('excluded_collection')
    if stress and excluded:
        summary['sensitivity']=dict(flow_id=excluded['flow_id'],amount=excluded['amount'],due_date=excluded['due_date'],**stress)
    if status=='PENDING':
        summary['next_action']=result.get('message') or 'Completa los datos indicados para recalcular.'
    elif status=='SHORTFALL':
        summary['next_action']='Compara las alternativas calculadas y contrasta sus condiciones con el proveedor; después aplica una hipótesis y recalcula.' if summary['alternatives'] else 'Revisa el calendario, los importes y las previsiones: no hay una alternativa comprobada que respete la reserva.'
    elif summary['pending']:summary['next_action']=summary['pending'][0]
    else:summary['next_action']='Contrasta precio, portes, vencimientos y disponibilidad con el proveedor; conserva el soporte de las condiciones acordadas.'
    if scenario:summary['pending'].append('Contrasta los cobros, pagos y saldos con su soporte y resuelve posibles duplicados antes de utilizar el estudio para decidir.')
    summary['references']=dict(documentary_context_fingerprint=(result.get('documentary_context') or {}).get('fingerprint'),
        financial_source_fingerprint=result.get('financial_source_fingerprint'))
    return summary
