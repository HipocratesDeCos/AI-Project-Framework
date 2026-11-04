"""Explicit proposal pricing and buyer freight; no tax classification or decisions."""
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_EVEN, localcontext

CENT = Decimal('.01')


def number(data,field,maximum=Decimal('1000000000')):
    value=data.get(field)
    try:
        if isinstance(value,bool) or value is None or str(value).strip()=='': raise ValueError()
        result=Decimal(str(value))
        if not result.is_finite() or result<0 or result>maximum: raise ValueError()
        return result
    except (ValueError,TypeError,InvalidOperation):
        raise ValueError('Revisa '+field+': importe no negativo, finito y dentro de rango.') from None


def commercial_terms(data, *, require_dates=True):
    with localcontext() as context:
        context.prec=60
        return _calculate(data, require_dates=require_dates)


def _calculate(data, *, require_dates=True):
    qty=number(data,'quantity')
    if qty<=0: raise ValueError('La cantidad debe ser positiva.')
    entered=number(data,'unit_price')
    vat=number(data,'vat_percent',Decimal(100))
    schedule_issues=[]
    def read_date(field,message):
        try:
            return date.fromisoformat(data[field]) if require_dates or data.get(field) else None
        except (ValueError,TypeError,KeyError):
            if require_dates: raise ValueError(message) from None
            schedule_issues.append(message)
            return None
    ordered=read_date('order_date','Indica fecha de pedido válida.')
    due=read_date('due_date','Indica vencimiento de mercancía válido.')
    if due is not None and ordered is not None and due<ordered:
        message='El vencimiento no puede ser anterior al pedido.'
        if require_dates: raise ValueError(message)
        schedule_issues.append(message)
    pricing=data.get('pricing_mode','NET')
    discount_mode=data.get('discount_mode','NONE')
    if pricing not in ('NET','BEFORE_DISCOUNT') or discount_mode not in ('NONE','PERCENT','LINE_AMOUNT'):
        raise ValueError('Selecciona un modo válido de precio y descuento.')
    discount=Decimal(0)
    supplied=data.get('discount_value') not in (None,'')
    gross=(qty*entered).quantize(CENT,rounding=ROUND_HALF_EVEN)
    if pricing=='NET' and (discount_mode!='NONE' or supplied):
        raise ValueError('Un precio ya neto no admite otro descuento. Cambia a precio antes de descuentos.')
    if discount_mode=='NONE':
        if supplied: raise ValueError('Elimina el valor de descuento o selecciona su modalidad.')
        effective=entered
        net=gross
        value=None
    else:
        value=number(data,'discount_value',Decimal(100) if discount_mode=='PERCENT' else Decimal('1000000000000000000'))
        discount=(gross*value/100).quantize(CENT,rounding=ROUND_HALF_EVEN) if discount_mode=='PERCENT' else value
        if discount_mode=='LINE_AMOUNT' and value!=value.quantize(CENT,rounding=ROUND_HALF_EVEN):
            raise ValueError('El descuento en euros por línea admite hasta dos decimales.')
        if discount>gross: raise ValueError('El descuento no puede superar el importe de la mercancía.')
        net=gross-discount
        effective=net/qty
    tax=(net*vat/100).quantize(CENT,rounding=ROUND_HALF_EVEN)
    total=net+tax
    mode=data.get('shipping_mode','PENDING')
    if mode not in ('PENDING','BUYER','SUPPLIER','INCLUDED','NONE'):
        raise ValueError('Selecciona quién asume los portes.')
    shipping_fields=('shipping_net','shipping_vat_percent','shipping_billed_by','shipping_due_date')
    freight=dict(mode=mode,net=None,tax=None,total=None,vat_percent=None,billed_by=None,due_date=None)
    if mode=='BUYER':
        shipping_net=number(data,'shipping_net')
        if shipping_net!=shipping_net.quantize(CENT,rounding=ROUND_HALF_EVEN):
            raise ValueError('El importe neto de portes admite hasta dos decimales.')
        shipping_vat=number(data,'shipping_vat_percent',Decimal(100))
        billed=data.get('shipping_billed_by')
        if billed not in ('SUPPLIER','CARRIER'): raise ValueError('Indica si factura los portes el proveedor o el transportista.')
        shipping_due=read_date('shipping_due_date','Indica el vencimiento propio de los portes.')
        if shipping_due is not None and ordered is not None and shipping_due<ordered:
            message='El vencimiento de portes no puede ser anterior al pedido.'
            if require_dates: raise ValueError(message)
            schedule_issues.append(message)
        shipping_tax=(shipping_net*shipping_vat/100).quantize(CENT,rounding=ROUND_HALF_EVEN)
        freight.update(net=format(shipping_net.quantize(CENT),'f'),tax=format(shipping_tax,'f'),total=format(shipping_net+shipping_tax,'f'),vat_percent=format(shipping_vat,'f'),billed_by=billed,due_date=shipping_due.isoformat() if shipping_due else None)
    else:
        if any(data.get(key) not in (None,'') for key in shipping_fields):
            raise ValueError('Los importes, factura y vencimiento de portes solo corresponden a portes a cargo del comprador.')
        if mode!='PENDING': freight.update(net='0.00',tax='0.00',total='0.00')
    operation_net=None if freight['net'] is None else format(net+Decimal(freight['net']),'f')
    operation_tax=None if freight['tax'] is None else format(tax+Decimal(freight['tax']),'f')
    operation_total=None if freight['total'] is None else format(total+Decimal(freight['total']),'f')
    result = dict(quantity=format(qty,'f'),unit_price=format(effective,'f'),vat_percent=format(vat,'f'),net=format(net,'f'),tax=format(tax,'f'),total=format(total,'f'),
        commercial_terms=dict(schema='EIOS-PROPOSAL-COMMERCIAL-01/v0.1',pricing_mode=pricing,entered_unit_price=format(entered,'f'),discount_mode=discount_mode,discount_value=None if value is None else format(value,'f'),discount_amount=format(discount.quantize(CENT),'f'),gross_line=format(gross,'f'),shipping=freight,rounding='ROUND_HALF_EVEN; monetary lines rounded to cents'),
        operation_net=operation_net,operation_tax=operation_tax,operation_total=operation_total,
        cost_status='PENDING_SHIPPING' if mode=='PENDING' else 'DECLARED_COSTS',
        order_date=ordered.isoformat() if ordered else None,due_date=due.isoformat() if due else None)
    if not require_dates:
        result['schedule_issues']=schedule_issues
        result['schedule_status']='INVALID_DATES' if schedule_issues else 'PENDING_DATES' if ordered is None or due is None or mode=='BUYER' and freight['due_date'] is None else 'DATES_PRESENT'
    return result
