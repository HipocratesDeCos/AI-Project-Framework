"""Arithmetic checks on declared invoice values; no tax-rate inference."""
from decimal import Decimal, localcontext, ROUND_HALF_EVEN

CENT=Decimal('.01')

def validate_line(d,warnings,row):
    errors=[]
    with localcontext() as ctx:
        ctx.prec=60
        def dec(k):return None if d.get(k) is None else Decimal(d[k])
        price,percent,discount,vat,vat_amount,total,line=(dec(k) for k in ('unit_price_before_discount','discount_percent','discount_amount','vat_percent','vat_amount','invoice_total','line_number'))
        for label,value in [('Precio unitario',price),('Descuento en euros',discount),('IVA documentado',vat_amount),('Total de factura',total)]:
            if value is not None and value<0:errors.append(label+': no se admiten importes negativos.')
        if line is not None and (line<1 or line!=line.to_integral_value()):errors.append('Número de línea: indica un entero positivo.')
        for label,value in [('Descuento',percent),('Tipo de IVA',vat)]:
            if value is not None and not 0<=value<=100:errors.append(label+': el porcentaje debe estar entre 0 y 100.')
        net=Decimal(d['net_amount']);qty=Decimal(d['quantity'])
        gross=None if price is None else price*qty
        if gross is not None and discount is not None and discount>gross+CENT:errors.append('El descuento de línea supera su importe antes de descuento.')
        if gross is not None and (percent is not None or discount is not None) and not errors:
            computed=None if percent is None else (gross*percent/100).quantize(CENT,rounding=ROUND_HALF_EVEN)
            if discount is not None and computed is not None and abs(discount-computed)>CENT:errors.append('El descuento en euros no coincide con el porcentaje declarado.')
            effective=discount if discount is not None else computed
            expected=(gross-effective).quantize(CENT,rounding=ROUND_HALF_EVEN)
            if abs(net-expected)>CENT:errors.append('El neto de línea no coincide con precio, cantidad y descuento. No vuelvas a descontar un neto ya calculado.')
        elif (percent is not None or discount is not None) and price is None:
            warnings.append('Fila '+str(row)+': descuento conservado, sin precio previo para comprobarlo; no se descuenta de nuevo el neto.')
        if vat is not None and vat_amount is not None and 0<=vat<=100:
            expected=(net*vat/100).quantize(CENT,rounding=ROUND_HALF_EVEN)
            if abs(vat_amount-expected)>CENT:errors.append('El IVA documentado no coincide con el neto y el tipo declarado (tolerancia de un céntimo).')
    return errors


def effective_vat(d):
    if d.get('vat_amount') is not None:return Decimal(d['vat_amount']),'DOCUMENTED'
    if d.get('vat_percent') is not None:
        with localcontext() as ctx:
            ctx.prec=60
            return (Decimal(d['net_amount'])*Decimal(d['vat_percent'])/100).quantize(CENT,rounding=ROUND_HALF_EVEN),'CALCULATED_FROM_DECLARED_RATE'
    return None,'UNKNOWN'
