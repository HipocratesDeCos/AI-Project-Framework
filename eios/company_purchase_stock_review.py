"""Purchase quantity readiness from existing inventory, minimums and STK coverage.

Descriptive adapter only: no new replenishment rule or justified-need authority.
"""
from copy import deepcopy
from datetime import date
from decimal import Decimal, InvalidOperation


def _number(value):
    if value is None or isinstance(value,bool) or value=='':return None
    try:
        n=Decimal(str(value))
        return n if n.is_finite() and n>=0 else None
    except (InvalidOperation,ValueError,TypeError):return None


def review_quantity(state,data):
    result=dict(schema='PURCHASE-QUANTITY-READINESS-01',status='MISSING_DATA',quantity_assessment='NOT_DETERMINED',
        inventory=None,minimum=None,coverage=None,missing=[],decision_authority=False,operational_path='FORBIDDEN',
        message='La cantidad no está justificada automáticamente. Consulta las referencias y los datos pendientes.')
    def missing(code,message):result['missing'].append(dict(code=code,message=message))
    article=next((a for a in state.get('articles',[]) if a['article_id']==data.get('article_id') and a.get('supplier_id')==data.get('supplier_id')),None)
    if article is None:
        missing('ARTICLE','Selecciona un artículo del proveedor en esta versión.');return result
    key=article['article_id'];unit=article['unit_as_documented'];quantity=_number(data.get('quantity'))
    result.update(article_id=key,unit=unit,purchase_quantity=None if quantity is None else str(quantity),dataset_id=state['info']['dataset_id'])
    if quantity is None or quantity<=0:missing('QUANTITY','Indica una cantidad de compra positiva.')
    inventory=state.get('inventory',{}).get(key) or {};available=_number(inventory.get('available'))
    physical=_number(inventory.get('physical'));reserved=_number(inventory.get('reserved'))
    try:
        when=date.fromisoformat(inventory['as_of_date'])
        cutoff=date.fromisoformat(state['info']['as_of_date'])
        current=date.fromisoformat(data['order_date'])
        compatible=((state.get('selected_inventory') or {}).get('status')!='STALE' and inventory.get('unit')==unit and inventory.get('article_id',key)==key and inventory.get('dataset_id',state['info']['dataset_id'])==state['info']['dataset_id'] and when<=cutoff and when<=current)
    except (ValueError,TypeError,KeyError):compatible=False
    if available is None or physical is None or reserved is None or physical-reserved!=available or not compatible:
        missing('INVENTORY','Vincula un inventario con fecha válida, misma unidad y disponible igual a físico menos reservado.')
    else:
        result['status']='REFERENCE_AVAILABLE'
        result['inventory']=dict(available=str(available),physical=str(physical),reserved=str(reserved),as_of_date=inventory['as_of_date'],source=inventory.get('source'),source_refs=deepcopy(inventory.get('source_refs',[])))
        if when<current:missing('INVENTORY_MOVEMENTS','El inventario es anterior al pedido: confirma las entradas, salidas y reservas desde '+when.isoformat()+' hasta '+current.isoformat()+'. No se supone que siga intacto.')
    minimum=state.get('stock_minimums',{}).get(key) or {};value=_number(minimum.get('value'))
    if value is not None and minimum.get('unit')==unit:
        result['minimum']=dict(value=str(value),source=minimum.get('source'),revision=minimum.get('revision'),automatic=deepcopy(minimum.get('automatic')),
            gap_at_inventory=str(max(Decimal(0),value-available)) if result['inventory'] else None,
            scope='DOCUMENTARY_MINIMUM_REFERENCE_NOT_PURCHASE_TARGET')
        if minimum.get('source')=='AUTOMATIC':missing('AUTOMATIC_MINIMUM','El mínimo es una referencia automática del historial, no una cantidad óptima ni una política de reposición aprobada.')
    else:missing('MINIMUM','Configura o documenta el mínimo del artículo en Stock; el mínimo no basta para justificar el tamaño de la compra.')
    plan=state.get('planning',{}).get(key) or {}
    try:
        applicable=(result['inventory'] is not None and plan.get('engine')=='eios.stock.engine.calculate_coverage' and plan.get('unit')==unit and plan['as_of_date']==inventory['as_of_date'] and date.fromisoformat(plan['as_of_date'])<=current<=date.fromisoformat(plan['valid_to']))
    except (KeyError,ValueError,TypeError,UnboundLocalError):applicable=False
    if applicable and plan.get('status') in ('FINITE','UNBOUNDED'):
        daily=_number(plan.get('daily_demand'));coverage=_number(plan.get('coverage_days'))
        if daily is not None and ((plan['status']=='FINITE' and daily>0 and coverage is not None) or (plan['status']=='UNBOUNDED' and daily==0)):
            result['coverage']=deepcopy({k:plan.get(k) for k in ('status','coverage_days','daily_demand','lead_time_days','safety_stock','as_of_date','valid_to','unit','engine','material_nature')})
            result['coverage']['scope']='INVENTORY_DATE_ONLY_NOT_AFTER_PURCHASE'
            if plan['status']=='UNBOUNDED':missing('ZERO_DEMAND','La previsión indica consumo cero: no equivale a recomendar una compra ni a demostrar cobertura futura ilimitada.')
    if result['coverage'] is not None:
        lead=_number(plan.get('lead_time_days'))
        cov=_number(plan.get('coverage_days'))
        if lead is not None and cov is not None:
            result['coverage']['covers_lead_time_at_inventory']=cov>=lead
    if result['coverage'] is None:missing('DEMAND','Falta una previsión de consumo aplicable a este artículo, unidad, inventario y fecha de pedido. Las ventas históricas no se convierten automáticamente en demanda futura.')
    if not applicable or _number(plan.get('lead_time_days')) is None:missing('DELIVERY','Falta un plazo de entrega documentado para analizar la disponibilidad antes de recibir la compra.')
    missing('RECEIPTS_AND_DEMAND','Contrasta pedidos de compra pendientes de recibir y demanda comprometida, con cantidades, fechas y reservas, para no contarlos dos veces.')
    missing('PURCHASE_TARGET','Falta un criterio de reposición autorizado (por ejemplo, cobertura objetivo y límites aplicables). EIOS no transforma el mínimo de stock en una orden de compra.')
    return result


def attach_simulation_readiness(review, planning):
    """Keep documentary gaps separate from a complete, validated hypothesis."""
    if planning is None:
        review['simulation_readiness']='MISSING_ASSUMPTIONS'
        return review
    review['simulation_readiness']='COMPLETE_HYPOTHETICAL'
    review['simulation_source']=planning['fingerprint']
    review['simulation_covered']=[
        'Stock libre declarado al inicio del pedido, con reservas ya descontadas.',
        'Consumo diario adicional a las reservas declarado para el período.',
        'Plazo de recepción declarado y falta anterior a la entrega comprobada.',
        'Todas las entradas pendientes declaradas, incluida lista vacía si no hay.',
        'Cobertura objetivo, seguridad y múltiplo de compra declarados.']
    review['message']='Los cinco grupos de datos están completos para simular la cantidad. Son hipótesis declaradas; la comprobación documental se muestra por separado.'
    return review
