"""Conditional commercial scenarios, without activating Rules or financial authority."""
from datetime import date
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR
from eios.company_commercial_terms import number


def margin_policy(parameters):
    values = parameters.get('values', {})
    def read(key):
        raw = values.get(key)
        if raw is None:
            return None
        value = Decimal(str(raw))
        return value if value.is_finite() and 0 <= value < 100 else None
    minimum, target = read('P-MGE-001'), read('P-MGE-002')
    if minimum is not None and target is not None and target < minimum:
        target = None
    return dict(revision=parameters.get('revision', 0), minimum=minimum, target=target)


def price_reference(basis, parameters, article=None, on_date=None):
    policy = margin_policy(parameters)
    cost = basis['reference_unit_cost']
    target = policy['target']
    recommended = (Decimal(cost)/(1-target/100)).quantize(Decimal('.01'), rounding=ROUND_CEILING) if cost is not None and target is not None else None
    price_source='CALCULATED_FROM_PREPARED_TARGET'
    declared=(article or {}).get('recommended_sale_price')
    if declared is not None:
        try: candidate=Decimal(str(declared))
        except (ValueError,ArithmeticError): candidate=Decimal('NaN')
        if not candidate.is_finite() or candidate<0 or (article or {}).get('sale_currency')!='EUR':
            recommended=None;price_source='INVALID_OR_INCOMPATIBLE_CATALOGUE_PRICE'
        else:
            recommended=candidate;price_source='DOCUMENTED_CATALOGUE_RECOMMENDED_SALE_PRICE'
    tariff=(article or {}).get('received_sale_tariff')
    if tariff:
        selected=tariff['selection'];recommended=None
        price_source='RECEIVED_TARIFF_STALE'
        if tariff['status']=='ACTIVE':
            price_source='RECEIVED_TARIFF_DATE_REQUIRED'
            try:when=date.fromisoformat(on_date)
            except (ValueError,TypeError):when=None
            if when is not None:
                price_source='RECEIVED_TARIFF_OUTSIDE_VALIDITY'
                if selected['valid_from']<=when.isoformat()<=selected['valid_until']:
                    recommended=Decimal(selected['price']);price_source='EXPLICIT_RECEIVED_TARIFF'
    discount = None
    if recommended is not None and recommended>0 and policy['minimum'] is not None:
        floor = Decimal(cost)/(1-policy['minimum']/100) if cost is not None else None
        discount = max(Decimal(0),(1-floor/recommended)*100).quantize(Decimal('.01'),rounding=ROUND_FLOOR) if floor is not None else None
    return dict(tariff_reference=tariff,recommended_unit_price=str(recommended) if recommended is not None else None,
                recommended_margin_percent=str(((recommended-Decimal(cost))/recommended*100).quantize(Decimal('.01'))) if recommended is not None and recommended>0 and cost is not None else None,
                price_source=price_source,maximum_reference_discount_percent=str(discount) if discount is not None else None,
                target_margin_percent=str(target) if target is not None else None,
                minimum_margin_percent=str(policy['minimum']) if policy['minimum'] is not None else None,
                parameter_revision=policy['revision'],
                basis='RECEIVED_TARIFF_PENDING_ADMISSION' if tariff else 'DOCUMENTED_CATALOGUE_PRICE' if price_source=='DOCUMENTED_CATALOGUE_RECOMMENDED_SALE_PRICE' else 'HISTORICAL_PURCHASE_AND_EXPLICIT_PREPARED_MARGIN',
                authority_status='COMMERCIAL_SIMULATION_ONLY')


def analyze_offer(payload, state, data):
    parameters = state.get('sales_parameters', {})
    policy = margin_policy(parameters)
    logistics = None if data.get('seller_freight_cost') in (None, '') else number(data,'seller_freight_cost')
    label = data.get('gift_description','')
    if not isinstance(label,str) or len(label)>300:
        raise ValueError('Describe el merchandising en un máximo de 300 caracteres.')
    label = label.strip()
    gift = number(data,'gift_cost') if data.get('gift_cost') not in (None,'') else Decimal(0)
    if label and data.get('gift_cost') in (None,''):
        raise ValueError('Indica el coste explícito del merchandising.')
    if not label and gift != 0:
        raise ValueError('Describe el merchandising antes de indicar su coste.')
    merchandise_cost = Decimal(0)
    complete = True
    references = []
    for line in payload['lines']:
        basis = line['orientation']
        article=next((a for a in state['articles'] if a['article_id']==line['article_id']),{})
        anchor = price_reference(basis, parameters,article,payload['offer_date'])
        references.append(dict(article_id=line['article_id'], **anchor))
        unit = basis['reference_unit_cost']
        if unit is None:
            complete = False
        else:
            merchandise_cost += Decimal(unit)*Decimal(line['quantity'])
    revenue = Decimal(payload['net_amount'])
    total_cost = merchandise_cost + (logistics or 0) + gift
    known = complete and logistics is not None
    actual_margin = ((revenue-total_cost)/revenue*100).quantize(Decimal('.01')) if known and revenue>0 else None
    minimum = policy['minimum']
    raw_absolute=parameters.get('values',{}).get('P-MGE-004')
    absolute=Decimal(str(raw_absolute)) if raw_absolute is not None else None
    budget = max(Decimal(0), revenue*(1-minimum/100)-merchandise_cost-(logistics or 0)) if known and minimum is not None else None
    if budget is not None and absolute is not None:
        budget=max(Decimal(0),min(budget,revenue-merchandise_cost-(logistics or 0)-absolute))
    finance = state.get('sales_financial_context') or {}
    snapshot, capital = finance.get('financial_snapshot') or {}, finance.get('working_capital_input') or {}
    identity = (snapshot.get('company_scope') == finance.get('company_id')
                and snapshot.get('as_of_date') == finance.get('as_of_date') and snapshot.get('currency') == 'EUR')
    capital_identity = (capital.get('company_scope') == finance.get('company_id')
                and capital.get('as_of_date') == finance.get('as_of_date') and capital.get('currency') == 'EUR')
    treasury = Decimal(snapshot['available_treasury']) if identity and snapshot.get('available_treasury') is not None else None
    working_capital = (Decimal(capital['current_assets'])-Decimal(capital['current_liabilities'])
        if capital_identity and capital.get('current_assets') is not None and capital.get('current_liabilities') is not None else None)
    payments = Decimal(0)
    collections = Decimal(0)
    partial = False
    for row in finance.get('cash_flows', []):
        flow = row['canonical']
        when = flow.get('due_date')
        if when is None or flow.get('amount') is None or flow.get('currency') != 'EUR':
            partial = True
            continue
        if finance['as_of_date'] < when < payload['due_date']:
            if flow['flow_type']=='PAYMENT': payments += Decimal(flow['amount'])
            else: collections += Decimal(flow['amount'])
    pressure = (working_capital is not None and working_capital<0) or (treasury is not None and payments>treasury+collections)
    # Totals describe existing documentary maturities only. No sale collection is added,
    # and aggregate coverage is never presented as a daily cash projection.
    finance_summary = dict(as_of_date=finance.get('as_of_date'), treasury=str(treasury) if treasury is not None else None,
        working_capital=str(working_capital) if working_capital is not None else None,
        payments_before_collection=str(payments), collections_before_collection=str(collections),
        partial=partial, pressure_indicator=pressure, evidence_pending_count=finance.get('evidence_pending_count'),
        issues=finance.get('issues', []), forecast_status='NOT_EXECUTED',
        scope='DOCUMENTARY_MATURITY_TOTALS_NOT_DAILY_PROJECTION',
        message='Balance y vencimientos documentados: conciliación, completitud y efecto de la venta pendientes. Las alternativas no garantizan liquidez ni viabilidad.')
    block_credit=bool((state.get('sales_customer_credit') or {}).get('overdue_installments'))
    block_deferred=block_credit or (working_capital is not None and working_capital<0)
    scenarios = []
    if known and minimum is not None:
        target = policy['target']
        def scenario(name, cost, freight, include_gift, due, wording, desired):
            net_required = max(cost/(1-desired/100),cost+absolute if absolute is not None else Decimal(0)).quantize(Decimal('.01'),rounding=ROUND_CEILING)
            merchandise_net = max(Decimal(0),net_required-freight)
            current_merchandise = sum(Decimal(l['net_amount']) for l in payload['lines'])
            factor = merchandise_net/current_merchandise if current_merchandise>0 else None
            adjusted = []
            for line in payload['lines']:
                unit = (Decimal(line['net_amount'])/Decimal(line['quantity'])*factor).quantize(Decimal('.01'),rounding=ROUND_CEILING) if factor is not None else None
                adjusted.append(dict(article_id=line['article_id'], quantity=line['quantity'],net_unit_price=str(unit) if unit is not None else None))
            actual_net = sum(Decimal(l['net_unit_price'])*Decimal(l['quantity']) for l in adjusted) + freight if factor is not None else None
            percentage = ((actual_net-cost)/actual_net*100).quantize(Decimal('.01')) if actual_net is not None and actual_net>0 else None
            scenarios.append(dict(title=name, lines=adjusted,freight_charged=str(freight),include_gift=include_gift,
                suggested_due_date=due, collection_terms=wording, margin_percent=str(percentage) if percentage is not None else None,
                threshold_status='MEETS_DECLARED_MARGIN_ONLY' if percentage is not None and percentage>=minimum else 'NOT_CALCULABLE',
                message='Precios netos, sin otro descuento. Requiere confirmar costes completos, impuestos, crédito y tesorería. No se aplica automáticamente.'))
        if target is not None:
            scenario('1. Mantener el objetivo de origen',total_cost,Decimal(payload['freight_net']),bool(label),
                payload['offer_date'] if pressure or block_credit else payload['due_date'],
                'Proponer cobro anticipado antes de entregar.' if pressure or block_credit else payload['payment_terms'] or 'Proponer cobro al vencimiento indicado.',target)
        else:
            scenarios.append(dict(title='1. Precio de origen pendiente',message='Configura el margen objetivo en Parámetros; no se adopta uno por defecto.'))
        scenario('2. Reducir concesiones y cobrar en la entrega',merchandise_cost+(logistics or 0),logistics or Decimal(0),False,
            payload['offer_date'] if block_deferred else payload['delivery_date'],
            'Proponer pago anticipado y repercutir el coste logístico al cliente.' if block_deferred else 'Proponer pago en la entrega y repercutir el coste logístico al cliente.',minimum)
        scenario('3. Mantener merchandising con cobro anticipado',total_cost,Decimal(0),bool(label),payload['offer_date'],
            'Proponer pago íntegro antes de la entrega; portes incluidos en el precio.',minimum)
    result = dict(schema='SALES-CONDITIONAL-NEGOTIATION-01', parameters_revision=policy['revision'],
        parameters_scope='EXPLICIT_PREPARED_VALUES_NOT_RULES_ACTIVATION',
        policy_snapshot={key:parameters.get('values',{}).get(key) for key in ('P-MGE-001','P-MGE-002')},origin_prices=references,
        seller_freight_cost=str(logistics) if logistics is not None else None,
        gift_description=label,gift_cost=str(gift),gift_budget=str(budget.quantize(Decimal('.01'))) if budget is not None else None,
        gift_scope='INTERNAL_OPTION_NOT_COMMITTED_OR_TAX_CLASSIFIED',
        contribution_margin_exact=str((revenue-total_cost)/revenue*100) if known and revenue>0 else None,
        contribution_margin_percent=str(actual_margin) if actual_margin is not None else None,
        cost_scope='HISTORICAL_MERCHANDISE_PLUS_DECLARED_LOGISTICS_AND_GIFT_NOT_COMPLETE_COST',
        below_declared_minimum=(revenue-total_cost)/revenue*100<minimum if known and revenue>0 and minimum is not None else None,
        financial_context=finance_summary, financial_inputs=finance, financial_context_fingerprint=finance.get('fingerprint'),scenarios=scenarios,
        pending=[] if scenarios else ['Configura margen mínimo y objetivo en Parámetros y declara el coste logístico. Se requieren compras comparables únicas para todos los artículos.'],
        viability_status='NOT_EVALUATED',decision_authority=False,operational_path='FORBIDDEN')

    from eios.company_sales_workflow import proposal_precheck
    result['proposal_evaluation']=proposal_precheck(payload,state,data,result)
    result['alternatives_trigger']='AFTER_UNAPPROPRIATE_PROPOSAL_ONLY'
    result['scenarios']=scenarios if result['proposal_evaluation']['reasons'] else []
    return result
