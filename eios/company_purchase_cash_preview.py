"""Pre-save purchase cash scenarios. Documentary assumptions never grant authority."""
from collections import defaultdict
from copy import deepcopy
from datetime import date,timedelta
from decimal import Decimal,ROUND_FLOOR
from hashlib import sha256
import json
import sqlite3

from eios.company_commercial_terms import commercial_terms
from eios.company_payment_plan import payment_plan


def preview(db,state,data,*,alternatives=True):
    result=dict(schema='PURCHASE-DRAFT-CASH-01',status='PENDING',message='',alternatives=[],
        scope='HYPOTHETICAL_DOCUMENTARY_CASH_ORIENTATION',viability_status='NOT_EVALUATED',decision_authority=False,operational_path='FORBIDDEN')
    def pending(message):result['message']=message;return result
    if state['info'].get('material_nature') not in (None,'SYNTHETIC'):
        return pending('Esta simulación de compra admite únicamente datos ficticios.')
    finance=state.get('sales_financial_context') or {}
    try:
        with sqlite3.connect(db) as c:
            manifest=json.loads(c.execute('SELECT manifest_json FROM documentary_company_snapshot WHERE dataset_id=?',(state['info']['dataset_id'],)).fetchone()[0])
        if manifest.get('material_nature')!='SYNTHETIC':return pending('Esta simulación requiere un expediente marcado como ficticio.')
        from eios.company_purchase_stock_review import review_quantity
        result['quantity_review']=review_quantity(state,data)
        from eios.company_purchase_stock_scenario import calculate as stock_scenario
        result['stock_planning']=stock_scenario(state,data)
        quote=commercial_terms(data)
        article=next((a for a in state['articles'] if a['article_id']==data.get('article_id') and a.get('supplier_id')==data.get('supplier_id')),None)
        if article is None:return pending('Selecciona un artículo del proveedor de esta versión.')
        snapshot=finance.get('financial_snapshot') or {}
        company=state['info']['company']['company_id'];cut=date.fromisoformat(state['info']['as_of_date'])
        if (snapshot.get('company_scope'),snapshot.get('as_of_date'),snapshot.get('currency'))!=(company,cut.isoformat(),'EUR'):
            return pending('Falta un saldo de tesorería de esta empresa, corte y moneda. Revisa caja y bancos del archivo activo.')
        opening=Decimal(str(snapshot['available_treasury']))
        if not opening.is_finite():raise ValueError('Saldo inicial inválido.')
        # A missing calendar must not hide a documented balance overrun.
        total=Decimal(quote['operation_total'] if quote['operation_total'] is not None else quote['total'])
        result['balance_comparison']=dict(opening_balance=str(opening),purchase_amount=str(total),
            excess_over_balance=str(max(Decimal('0'),total-opening)),currency='EUR',cutoff=cut.isoformat(),
            amount_basis='FULL_OPERATION' if quote['operation_total'] is not None else 'MERCHANDISE_ONLY',
            scope='DOCUMENTARY_BALANCE_COMPARISON',includes_forecast=False)
        if quote['operation_total'] is None:return pending('Confirma quién asume los portes para calcular el pago completo.')
        with sqlite3.connect(db) as c:
            if not c.execute("SELECT 1 FROM sqlite_master WHERE name='company_finance_parameter_activation'").fetchone():return pending('Activa horizonte y tesorería mínima para este corte en Parámetros.')
            row=c.execute('SELECT payload FROM company_finance_parameter_activation WHERE company_id=? AND as_of_date=?',(company,cut.isoformat())).fetchone()
        if not row:return pending('Activa horizonte y tesorería mínima para este corte en Parámetros.')
        activation=json.loads(row[0]);minimum=Decimal(activation['values']['P-FIN-002']);days=Decimal(activation['values']['P-FIN-001'])
        if not minimum.is_finite() or minimum<0 or not days.is_finite() or days<=0 or days!=days.to_integral_value():raise ValueError('Parámetros financieros inválidos.')
        end=cut+timedelta(days=int(days))
        if not cut<=date.fromisoformat(data['order_date'])<=end:return pending('La fecha de pedido debe estar dentro del corte y horizonte financiero activado.')
        source=finance.get('cash_flows',[])
        if not source or len(source)!=finance.get('record_counts',{}).get('cash_flow'):return pending('Falta un calendario completo y legible de cobros y pagos para construir el escenario.')
        base=[];ids=set()
        for item in source:
            f=item['canonical'];amount=Decimal(str(f['amount']));when=date.fromisoformat(f['due_date'])
            if not amount.is_finite() or amount<0 or f['flow_type'] not in ('PAYMENT','COLLECTION') or f['currency']!='EUR' or f['flow_id']!=item['record_id'] or f['flow_id'] in ids:raise ValueError('Hay movimientos incompletos, duplicados o de otra moneda.')
            ids.add(f['flow_id'])
            if when<=cut:return pending('Hay movimientos vencidos al corte sin resolver. Actualiza su previsión o contrasta su inclusión en el saldo inicial.')
            if when<=end:base.append((when,amount if f['flow_type']=='COLLECTION' else -amount))
        def candidate(values):
            q=commercial_terms(values)
            p=payment_plan(values,dict(q,proposal_id='DRAFT',currency='EUR'))
            if p['status']=='NOT_DECLARED':
                payments=[(date.fromisoformat(q['due_date']),Decimal(q['total']))]
                freight=q['commercial_terms']['shipping']
                if Decimal(freight['total'])>0:payments.append((date.fromisoformat(freight['due_date']),Decimal(freight['total'])))
            else:payments=[(date.fromisoformat(i['due_date']),Decimal(i['amount'])) for i in p['installments']]
            return q,p,payments
        quote,plan,payments=candidate(data)
        def collision(payments):
            return any(f['canonical']['flow_type']=='PAYMENT' and (date.fromisoformat(f['canonical']['due_date']),Decimal(str(f['canonical']['amount']))) in payments for f in source)
        if any(not cut<=d<=end for d,a in payments):return pending('Todos los pagos deben quedar dentro del horizonte activado; no se evalúan aplazamientos fuera de él.')
        if collision(payments):return pending('Un pago coincide en fecha e importe con la previsión existente. Comprueba su vínculo para no duplicarlo; no se añade automáticamente.')
        def project(extra,excluded_collection=None):
            events=defaultdict(Decimal)
            for d,a in base:events[d]+=a
            for d,a in extra:events[d]-=a
            if excluded_collection:events[date.fromisoformat(excluded_collection['due_date'])]-=Decimal(str(excluded_collection['amount']))
            balance=opening;low=opening;lowdate=cut;first=cut if opening<minimum else None
            points=[dict(date=cut.isoformat(),balance=str(opening))]
            for d in sorted(events):
                balance+=events[d]
                points.append(dict(date=d.isoformat(),balance=str(balance)))
                if balance<low:low=balance;lowdate=d
                if first is None and balance<minimum:first=d
            if points[-1]['date']!=end.isoformat():points.append(dict(date=end.isoformat(),balance=str(balance)))
            return dict(points=points,minimum_balance=str(low),minimum_date=lowdate.isoformat(),first_shortfall_date=first.isoformat() if first else None,deficit=str(max(Decimal(0),minimum-low)),closing_balance=str(balance))
        baseline=project([]);scenario=project(payments)
        result.update(status='SHORTFALL' if Decimal(scenario['deficit'])>0 else 'WITHIN_DECLARED_SCENARIO',message='Déficit en el escenario de pagos propuesto.' if Decimal(scenario['deficit'])>0 else 'El escenario respeta el mínimo de tesorería con las previsiones declaradas; no acredita viabilidad final.',baseline=baseline,scenario=scenario,opening_balance=str(opening),treasury_minimum=str(minimum),horizon_end=end.isoformat(),cutoff=cut.isoformat(),total=quote['operation_total'],payment_basis='DECLARED_INSTALLMENTS' if plan['status']!='NOT_DECLARED' else 'HYPOTHETICAL_SINGLE_PAYMENT_PER_COMPONENT',payments=[dict(due_date=d.isoformat(),amount=str(a)) for d,a in payments],documentary_context=deepcopy(state['documentary_context']),financial_source_fingerprint=finance.get('fingerprint'),parameter_activation=activation,
            assumptions=['Se usan los importes y fechas del archivo financiero activo sin acreditar cobro, pago ni conciliación.','Los movimientos de cada día se compensan al cierre; no se garantiza liquidez dentro del día.','Sin cuotas declaradas se simula un pago único de mercancía y otro de portes, si existen, en sus fechas indicadas. No se registra ese calendario.','No se suman otras propuestas guardadas ni financiación hipotética. El saldo corresponde al corte, no al día actual.'],evidence_pending_count=finance.get('evidence_pending_count'),data_quality_status='NOT_VERIFIED')
        from eios.company_sales_cash_plan import _execute
        with sqlite3.connect(db) as c:
            if c.execute("SELECT 1 FROM sqlite_master WHERE name='company_finance_parameter_configuration'").fetchone():
                rows=[dict(flow_id='PURCHASE-DRAFT-'+str(i),flow_type='PAYMENT',amount=str(a),due_date=d.isoformat(),declaration_ref='HYPOTHETICAL-PURCHASE-PAYMENT',disposition='NEW_DECLARATION') for i,(d,a) in enumerate(payments)]
                result['formal_engine']=_execute(c,dict(proposal_id='PURCHASE-DRAFT'),finance,rows)
        def evaluate(values):
            try:
                q,p,ps=candidate(values)
                if any(not cut<=d<=end for d,a in ps):return None,'Algún pago queda fuera del horizonte financiero activado.'
                if collision(ps):return None,'Un pago coincide en fecha e importe con la previsión: falta resolver su relación para evitar duplicados.'
                sc=project(ps)
                if Decimal(sc['deficit'])>0:return None,'No respeta la reserva mínima: faltan '+sc['deficit']+' EUR.'
                return (q,p,ps,sc),None
            except (ValueError,TypeError,KeyError,ArithmeticError) as error:return None,'Datos o cuotas incompatibles: '+str(error)
        def check(values):return evaluate(values)[0]
        result['current_terms']=dict(quantity=quote['quantity'],unit=article['unit_as_documented'],net_unit_price=quote['unit_price'],total=quote['operation_total'],due_date=quote['due_date'],payments=deepcopy(result['payments']),minimum_balance=scenario['minimum_balance'],minimum_date=scenario['minimum_date'],basis='FULL_OPERATION_WITH_VAT_AND_FREIGHT')
        def add(kind,title,patch,checked,text):
            result['alternatives'].append(dict(kind=kind,title=title,patch=patch,total=checked[0]['operation_total'],minimum_balance=checked[3]['minimum_balance'],quantity=checked[0]['quantity'],unit=article['unit_as_documented'],net_unit_price=checked[0]['unit_price'],minimum_date=checked[3]['minimum_date'],due_date=checked[0]['due_date'],payments=[dict(due_date=d.isoformat(),amount=str(a)) for d,a in checked[2]],negotiation_text=text,status='WITHIN_DECLARED_SCENARIO',decision_authority=False))
        if alternatives and result['status']=='SHORTFALL':
            if plan['status']=='NOT_DECLARED' and Decimal(baseline['deficit'])==0 and data.get('discount_mode')!='LINE_AMOUNT':
                # Search cents using the same discount and tax calculator as the form.
                for field,kind,title,scale in [('unit_price','PRICE','Negociar precio inferior',Decimal('.01')),('quantity','QUANTITY','Reducir cantidad',Decimal(1))]:
                    original=Decimal(str(data[field]))
                    if field=='quantity' and original!=original.to_integral_value():continue
                    lo=1;hi=int((original/scale).to_integral_value(rounding=ROUND_FLOOR));best=None
                    while lo<=hi:
                        mid=(lo+hi)//2;value=str(mid*scale);values=dict(data,**{field:value});tested=check(values)
                        if tested:best=(value,tested);lo=mid+1
                        else:hi=mid-1
                    if best and Decimal(best[0])<original:
                        value,tested=best;add(kind,title,{field:value},tested,('Proponemos un precio de '+value+' EUR por unidad, manteniendo los descuentos indicados.' if field=='unit_price' else 'Proponemos comprar '+value+' '+article['unit_as_documented']+', manteniendo el resto de condiciones.'))
            max_shift=(end-max(d for d,a in payments)).days
            for shift in range(1,max_shift+1):
                patch={'due_date':(date.fromisoformat(data['due_date'])+timedelta(days=shift)).isoformat()}
                if data.get('shipping_due_date'):patch['shipping_due_date']=(date.fromisoformat(data['shipping_due_date'])+timedelta(days=shift)).isoformat()
                if data.get('payment_installments') is not None:patch['payment_installments']=[dict(i,due_date=(date.fromisoformat(i['due_date'])+timedelta(days=shift)).isoformat()) for i in data['payment_installments']]
                tested=check(dict(data,**patch))
                if tested:add('DEFER','Aplazar el calendario de pagos',patch,tested,'Solicitamos desplazar el calendario '+str(shift)+' días. Último vencimiento de mercancía: '+patch['due_date']+'. Sujeto a aceptación del proveedor.');break
            result['capital_measure']=dict(amount=scenario['deficit'],needed_by=scenario['first_shortfall_date'],status='PENDING_APPROVAL_AND_DISBURSEMENT',message='Aportación mínima teórica para cubrir el déficit del escenario si estuviera disponible antes de la primera falta. No se incorpora como liquidez ni acredita que una ampliación de capital sea adecuada.')
        if alternatives:
            from eios.company_purchase_opportunities import opportunities
            suggestions,notes,stock=opportunities(state,data,quote,plan,scenario,end,check)
            target=result.get('stock_planning')
            if target:
                notes=[n for n in notes if not n.startswith('Cantidad sin optimizar:')]
                q=Decimal(target['scenario_quantity'])
                result['alternatives']=[a for a in result['alternatives'] if a['kind']!='QUANTITY' or target['status']!='PRE_DELIVERY_SHORTFALL' and Decimal(a['patch']['quantity'])>=q]
                if target['status']=='PRE_DELIVERY_SHORTFALL':
                    notes.append('La simulación de stock presenta una falta antes de la entrega. Cambiar solo la cantidad de esta compra no la resuelve.')
                elif q==0:
                    notes.append('El objetivo declarado no requiere una compra adicional. No se genera ni se ejecuta automáticamente una cancelación.')
                elif q==Decimal(data['quantity']):
                    notes.append('La cantidad actual coincide con la necesaria para el objetivo hipotético declarado.')
                else:
                    patch={'quantity':str(q)}
                    from eios.company_purchase_opportunities import resized_installments
                    try:
                        revised=commercial_terms(dict(data,**patch))
                        if plan['status']!='NOT_DECLARED':patch['payment_installments']=resized_installments(data,revised,quote)
                        tested=check(dict(data,**patch))
                    except (ValueError,TypeError,ArithmeticError):tested=None
                    if tested:
                        suggestions.append(dict(kind='STOCK_TARGET',title='Ajustar cantidad al objetivo de cobertura declarado',patch=patch,checked=tested,
                            basis='Cantidad calculada para los supuestos de demanda, seguridad, entregas y cobertura que has declarado. No es una cantidad óptima ni una necesidad acreditada. El precio unitario, descuentos, IVA y portes se mantienen según lo declarado; confirma sus condiciones al cambiar el volumen.',
                            source=dict(planning_fingerprint=target['fingerprint'],issue_date=data['order_date'],invoice_number=target['assumptions']['source_reference']),
                            negotiation_text='Proponemos comprar '+str(q)+' '+article['unit_as_documented']+' conforme a nuestro escenario interno de cobertura. Sujeto a disponibilidad y aceptación del proveedor.'))
                    else:notes.append('La cantidad del objetivo hipotético no respeta la reserva de tesorería o el calendario declarado. Revisa conjuntamente stock y pagos.')

            from eios.company_purchase_scenario_search import search,metric_comparison
            combined,search_report=search(state,data,quote,plan,target,end,scenario,evaluate)
            suggestions.extend(combined)
            result['combination_analysis']=search_report
            seen_patches={json.dumps(a['patch'],sort_keys=True) for a in result['alternatives']}
            for suggestion in suggestions:
                key=json.dumps(suggestion['patch'],sort_keys=True)
                if key in seen_patches:continue
                seen_patches.add(key)
                tested=suggestion.pop('checked')
                add(suggestion.pop('kind'),suggestion.pop('title'),suggestion.pop('patch'),tested,suggestion.pop('negotiation_text'))
                result['alternatives'][-1].update(suggestion)
            result['opportunity_notes']=notes
            if target:stock['message']='Inventario documental de referencia. Las cantidades del escenario dependen de supuestos declarados, sin necesidad de compra acreditada.'
            result['stock_context']=stock
            for alternative in result['alternatives']:
                alternative.update(origin='HYPOTHETICAL',supplier_acceptance='NOT_CONFIRMED',
                    savings=str(Decimal(quote['operation_total'])-Decimal(alternative['total'])),
                    minimum_balance_improvement=str(Decimal(alternative['minimum_balance'])-Decimal(scenario['minimum_balance'])),
                    comparison_basis='FULL_OPERATION_WITH_VAT_AND_FREIGHT',
                    stock_effect='QUANTITY_CHANGED_NEED_NOT_VERIFIED' if Decimal(alternative['quantity'])!=Decimal(quote['quantity']) else 'SAME_QUANTITY',
                    operational_path='FORBIDDEN')
                alternative.setdefault('basis','Condición hipotética calculada para respetar la reserva mínima. No acredita necesidad de compra ni aceptación del proveedor.')
            result['combination_analysis']['retained']=sum(a['kind']=='COMBINED' for a in result['alternatives'])
            metric_comparison(result['current_terms'],result['alternatives'])
            incoming=[item['canonical'] for item in source if item['canonical']['flow_type']=='COLLECTION' and Decimal(str(item['canonical']['amount']))>0 and cut<date.fromisoformat(item['canonical']['due_date'])<=end]
            excluded=sorted(incoming,key=lambda f:(-Decimal(str(f['amount'])),f['flow_id']))[0] if incoming else None
            result['collection_sensitivity']=dict(status='CALCULATED' if excluded else 'NO_COLLECTION',excluded_collection=deepcopy(excluded),scope='REMOVE_ONE_LARGEST_IN_HORIZON_COLLECTION_ONLY',message='Hipótesis de tensión: elimina por completo el mayor cobro individual previsto dentro del horizonte. No es una previsión ni prueba otros retrasos, impagos o disponibilidad intradía.')
            for entry in [result['current_terms']]+result['alternatives']:
                if excluded:
                    stress=project([(date.fromisoformat(p['due_date']),Decimal(p['amount'])) for p in entry['payments']],excluded)
                    entry['collection_sensitivity']=dict(minimum_balance=stress['minimum_balance'],deficit=stress['deficit'],first_shortfall_date=stress['first_shortfall_date'],reserve_respected=Decimal(stress['deficit'])==0)
        result['analysis_fingerprint']=sha256(json.dumps(result,sort_keys=True,default=str).encode()).hexdigest()
        return result
    except (ValueError,TypeError,KeyError,ArithmeticError) as error:return pending(str(error))
