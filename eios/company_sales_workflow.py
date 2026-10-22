"""Source-backed sales starting position and explicit proposal prechecks.

NI/Ladder and Rules are not replaced or claimed as executed by this adapter.
"""
from datetime import date
from decimal import Decimal

PROTOCOL_REFERENCES = ['05_Motor/Negotiation_Intelligence.md','05_Motor/Negotiation_Ladder.md',
    '08_Implementacion/Negotiation_Intelligence_Implementation_Contract.md',
    '08_Implementacion/Negotiation_C0_Trace_Binding_Contract_v0.1.md']


def customer_credit(store,dataset,customer,cutoff):
    from eios.company_sales import documented_sales
    invoices={r['invoice_number'] for r in documented_sales(store,dataset,cutoff)['invoices'] if r['customer_id']==customer}
    arrears=[];unresolved=[];checked=0
    for r in store.records(dataset,'sales_installment'):
        d=r['data']
        if d.get('customer_id')!=customer:continue
        if d.get('invoice_number') not in invoices:
            unresolved.append(r['record_id']);continue
        try:
            pending=Decimal(str(d['pending']))
            due=date.fromisoformat(d.get('revised_due_date') or d['original_due_date'])
            if not pending.is_finite() or pending<0:raise ValueError()
        except (KeyError,TypeError,ValueError,ArithmeticError):
            unresolved.append(r['record_id']);continue
        checked+=1
        if pending>0 and due.isoformat()<cutoff:
            arrears.append(dict(installment_ref=r['record_id'],invoice_number=d['invoice_number'],
                due_date=due.isoformat(),pending=str(pending),source_refs=r.get('source_refs',[])))
    return dict(status='DOCUMENTED_OVERDUE_BALANCES' if arrears else 'NO_OVERDUE_FOUND_IN_CHECKED_RECORDS' if checked and not unresolved else 'UNKNOWN',
        as_of_date=cutoff,overdue_installments=arrears,checked_installments=checked,unresolved=unresolved,
        completeness_status='NOT_ESTABLISHED',default_history_status='NOT_VERIFIED',
        message='Saldos vencidos al corte documental; no equivalen por sí solos a un historial de impagos ni acreditan la situación actual.')


def proposal_precheck(payload,state,data,analysis):
    credit=state.get('sales_customer_credit') or dict(status='UNKNOWN',overdue_installments=[])
    minimum=state.get('sales_parameters',{}).get('values',{}).get('P-MGE-001')
    absolute=state.get('sales_parameters',{}).get('values',{}).get('P-MGE-004')
    reasons=[];pending=[]
    margin=analysis.get('contribution_margin_exact',analysis['contribution_margin_percent'])
    if minimum is None or margin is None:
        pending.append('Faltan margen mínimo o costes comparables para contrastar la propuesta.')
    elif Decimal(margin)<Decimal(str(minimum)):
        reasons.append(dict(code='MARGIN_BELOW_MINIMUM',message='El margen de la propuesta queda por debajo del mínimo preparado.'))
    if absolute is not None:
        net=Decimal(payload['net_amount'])
        costs=[l['orientation']['reference_unit_cost'] for l in payload['lines']]
        if all(c is not None for c in costs) and analysis['seller_freight_cost'] is not None:
            contribution=net-sum(Decimal(c)*Decimal(l['quantity']) for c,l in zip(costs,payload['lines']))-Decimal(analysis['seller_freight_cost'])-Decimal(analysis['gift_cost'])
            if contribution<Decimal(str(absolute)):
                reasons.append(dict(code='CONTRIBUTION_BELOW_MINIMUM',message='La contribución en euros queda por debajo del mínimo absoluto preparado.'))
        else:pending.append('No puede contrastarse el margen mínimo absoluto por falta de costes.')
    deferred=payload['due_date']>payload['offer_date']
    if credit['overdue_installments'] and deferred:
        reasons.append(dict(code='OVERDUE_CUSTOMER_DEFERRED_COLLECTION',message='El cliente tiene saldos vencidos documentados al corte: no se propone financiar otra venta sin revisión de crédito. Negocia cobro previo.'))
    capital=analysis['financial_context'].get('working_capital')
    if capital is not None and Decimal(capital)<0 and deferred:
        reasons.append(dict(code='WORKING_CAPITAL_RISK',message='Fondo de maniobra negativo al corte y cobro aplazado: revisar la exposición antes de financiar.'))
    if credit['status']=='UNKNOWN' or credit.get('unresolved'):
        pending.append('Historial de cobro insuficiente o con cuotas sin interpretar; no se presupone buen pagador.')
    motive=data.get('negotiation_reason','INITIAL')
    if motive not in ('INITIAL','PRICE','CLIENT_STOCK','PAYMENT_TERMS','OTHER'):
        raise ValueError('Selecciona el motivo de la negociación.')
    origin=data.get('proposal_origin','SALESPERSON')
    if origin not in ('SALESPERSON','CUSTOMER'):raise ValueError('Indica quién plantea la propuesta.')
    note=data.get('negotiation_note','')
    if not isinstance(note,str) or len(note)>1000:raise ValueError('La explicación admite hasta 1.000 caracteres.')
    if motive=='OTHER' and not note.strip():raise ValueError('Explica el motivo de la negociación.')
    if motive=='CLIENT_STOCK':pending.append('El cliente declara que tiene stock: confirmar necesidad, cantidad y fecha antes de proponer un pedido.')
    pending.extend(['Integración de ventas con evaluación autorizada, crédito, calidad y efecto completo de tesorería pendiente.'])
    return dict(status='NOT_APPROPRIATE_AS_PROPOSED' if reasons else 'PENDING_VALIDATION',
        reasons=reasons,pending=pending,customer_credit=credit,
        negotiation_reason=motive,proposal_origin=origin,negotiation_note=note.strip(),
        protocol_references=PROTOCOL_REFERENCES,protocol_execution_status='SALES_BINDING_PENDING',
        commercial_precheck_only=True,automatic_acceptance=False,decision_authority=False)
