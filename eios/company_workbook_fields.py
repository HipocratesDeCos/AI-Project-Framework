"""Explicit optional workbook fields; price references are never active tariffs."""
EXTENSIONS = {
 'supplier':[('email','Correo electrónico'),],
 'customer':[('address','Dirección'),('province','Provincia'),('postal_code','C.P'),('country','País')],
 'article':[('subfamily','Subfamilia'),('provenance','Procedencia')],
 'purchase_line':[('unit_price','Precio unitario neto'),('description','Descripción'),('order_date','Fecha pedido'),('delivery_date','Fecha entrega'),('origin','Origen'),('order_ref','Referencia pedido'),('delivery_ref','Referencia albarán')],
 'sales_line':[('origin','Origen')],
 'cash_flow':[('supplier_id','Cod.Proveedor'),('counterparty_type','Tipo de contraparte'),('support_ref','Referencia soporte'),('support_type','Tipo de soporte'),('not_applicable_reason','Motivo de campos no aplicables'),('contractual_due_date','Vencimiento contractual')],
}
REFERENCE_FIELDS=[('article_id','Sku',True),('reference_cost','Coste fuente',True),('reference_price','PVP fuente',True),('unit','Unidad',False),('cost_origin','Origen del coste',False),('price_origin','Origen del PVP',False),('reference_date','Fecha de referencia',False),('source_document','Fuente',False),('scope','Alcance',False),('target_margin','Margen objetivo supuesto',False),('currency','Moneda',False)]
CACHED_PRICE_FIELDS={'purchase_line':{'unit_price'},'price_reference':{'reference_cost','reference_price'}}


def header_index(headers,name):
    from eios.company_table_profiles import clean
    aliases=[{'Coste fuente','Coste de compra de referencia'},{'PVP fuente','Precio de venta recomendado'}]
    accepted=next(({clean(v) for v in group} for group in aliases if clean(name) in {clean(v) for v in group}),{clean(name)})
    matches=[i for i,h in enumerate(headers) if clean(h) in accepted]
    if len(matches)!=1:raise ValueError('Columna ausente o ambigua: '+str(name))
    return matches[0]


def enrich_plan(headers,kind,mapping):
    """Only declared optional fields; never reinterpret existing guide mappings."""
    from eios.company_table_profiles import clean
    result=dict(mapping)
    for key,label in EXTENSIONS.get(kind,[]):
        if key in result:continue
        matches=[i for i,h in enumerate(headers) if clean(h) in {clean(key),clean(label)}]
        if len(matches)>1:raise ValueError('Columna ambigua: '+label)
        if matches and matches[0] not in result.values():result[key]=matches[0]
    return result
