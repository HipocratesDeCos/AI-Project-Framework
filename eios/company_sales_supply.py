"""Supply orientation from the active inventory; no reservation or purchase execution."""
from decimal import Decimal

CONDITION='PRECIO Y ENTREGA PENDIENTES DE CONFIRMACIÓN. Calculados con referencias documentales; sujetos a confirmar coste, disponibilidad y condiciones del proveedor.'


def assess(inventory, quantity, unit):
    qty=Decimal(str(quantity)) if quantity not in (None,'') else None
    available=None
    if inventory and inventory.get('unit')==unit and inventory.get('available') is not None:
        try:
            candidate=Decimal(str(inventory['available']))
            if candidate.is_finite():available=candidate
        except (ValueError,ArithmeticError):pass
    code='UNKNOWN' if available is None else 'NONE' if available<=0 else 'SHORT' if qty is not None and qty>available else 'DOCUMENTED'
    titles={'UNKNOWN':'DISPONIBILIDAD SIN CONFIRMAR','NONE':'SIN STOCK DISPONIBLE','SHORT':'STOCK INSUFICIENTE','DOCUMENTED':'STOCK DOCUMENTADO AL CORTE'}
    return dict(status=code,title=titles[code],requested=None if qty is None else str(qty),available=None if available is None else str(available),shortage=str(max(Decimal(0),qty-max(Decimal(0),available))) if qty is not None and available is not None else None,unit=unit,as_of_date=(inventory or {}).get('as_of_date'),conditional=code!='DOCUMENTED',condition=CONDITION if code!='DOCUMENTED' else 'Referencia al corte; no confirma existencias actuales ni reserva mercancía.')


def proposal_supply(lines,state,reference,delivery):
    result=[]
    for sku in dict.fromkeys(l['article_id'] for l in lines):
        group=[l for l in lines if l['article_id']==sku];line=group[0]
        qty=sum(Decimal(l['quantity']) for l in group)
        item=dict(article_id=sku,**assess(line['orientation'].get('inventory'),qty,line['unit']))
        article=next(a for a in state['articles'] if a['article_id']==sku)
        supplier=next((s for s in state['suppliers'] if s['supplier_id']==article.get('supplier_id')),None)
        if item['conditional']:
            rid=reference+' / '+sku
            request=(f'Consulta de aprovisionamiento {rid}\nArtículo: {sku} · {line["description"]}\nCantidad solicitada al cliente: {qty} {line["unit"]}\nCantidad a consultar al proveedor: {item["shortage"] if item["shortage"] is not None else qty} {line["unit"]}\nEntrega requerida: {delivery}\nConfirmar disponibilidad, precio neto por unidad, descuentos, portes, impuestos aplicables, plazo de entrega, condiciones de pago y validez de la oferta. No constituye un pedido.')
            item['procurement_request']=dict(reference=rid,supplier_id=article.get('supplier_id'),supplier_name=(supplier or {}).get('legal_name'),status='DRAFT_NOT_SENT',text=request)
        result.append(item)
    return dict(conditional=any(i['conditional'] for i in result),items=result,decision_authority=False,operational_path='FORBIDDEN')
