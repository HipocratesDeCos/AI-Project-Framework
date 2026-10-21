"""Commercial draft only: no acceptance, recipient resolution or transmission."""

from eios.company_presentation import number_text, date_text


def commercial_draft(report):
    p = report['proposal']
    terms = p.get('commercial_terms') or {}
    shipping = terms.get('shipping') or {}
    def value(item):
        return 'Pendiente de confirmar' if item is None else str(item)
    currency = value(p.get('currency'))
    def money(key):
        item = p.get(key)
        return value(item) if item is None else number_text(item, 2) + ' ' + currency
    supplier = p.get('supplier_commercial_at_save') or {}
    greeting = supplier.get('contact_name') or supplier.get('legal_name') or 'proveedor'
    lines = [
        'BORRADOR DE PRUEBA · NO ENVIAR',
        '',
        'Estimado ' + greeting + ':',
        '',
        'Solicitamos confirmar las siguientes condiciones comerciales antes de formalizar la compra.',
        '',
        'Referencia: ' + value(p.get('reference')),
        'Código de proveedor: ' + value(p.get('supplier_id')),
        'Código de artículo: ' + value(p.get('article_id')),
        'Cantidad: ' + number_text(p.get('quantity')) + ' ' + value(p.get('unit')),
        'Precio neto unitario: ' + money('unit_price'),
        'Importe neto de mercancía: ' + money('net'),
        'IVA de mercancía: ' + money('tax') + ' (tipo declarado: ' + number_text(p.get('vat_percent')) + ' %)',
        'Total mercancía: ' + money('total'),
        'Descuento aplicado a la línea: ' + number_text(terms.get('discount_amount'), 2) + ' ' + currency,
        'Portes: ' + {'BUYER':'a cargo de la empresa compradora', 'SUPPLIER':'a cargo del proveedor', 'INCLUDED':'incluidos en el precio', 'NONE':'sin portes', 'PENDING':'pendientes de confirmar'}.get(shipping.get('mode'), 'pendientes de confirmar'),
    ]
    if shipping.get('mode') == 'BUYER':
        lines.extend([
            'Portes netos: ' + number_text(shipping.get('net'), 2) + ' ' + currency,
            'IVA de portes: ' + number_text(shipping.get('tax'), 2) + ' ' + currency,
            'Total portes: ' + number_text(shipping.get('total'), 2) + ' ' + currency,
            'Emisor de portes: ' + {'SUPPLIER':'proveedor','CARRIER':'transportista'}.get(shipping.get('billed_by'), 'pendiente'),
            'Vencimiento de portes: ' + date_text(shipping.get('due_date')),
        ])
    plan = p.get('payment_plan')
    if plan and plan.get('status') == 'DECLARED_UNVERIFIED':
        lines.append('Calendario de pagos propuesto, pendiente de confirmación:')
        for row in plan['installments']:
            lines.append(('Mercancía' if row['component']=='MERCHANDISE' else 'Portes') +
                         ': ' + number_text(row['amount'],2) + ' ' + currency +
                         ' · ' + date_text(row['due_date']))
    lines.extend([
        'Total declarado de la operación: ' + money('operation_total'),
        'Vencimiento de mercancía: ' + date_text(p.get('due_date')),
        '',
        'Lugar de entrega: ' + value(p.get('delivery_location')),
        'Fecha de entrega: pendiente de confirmar.',
        'Resto de condiciones de pago y posibles gastos adicionales: pendientes de confirmar.',
        '',
        'Esta comunicación solicita confirmar condiciones; no constituye una aceptación ni un pedido.',
        '',
        'Atentamente,',
        '[Nombre y cargo de la persona responsable]',
        '[Empresa compradora]',
    ])
    return dict(schema='COMPANY-COMMERCIAL-DRAFT-01', dataset_id=report['dataset_id'],
                proposal_id=report['proposal_id'], review_id=report['review_id'],
                supplier_id=p.get('supplier_id'), recipient=None, recipient_status='NOT_VERIFIED',
                subject='BORRADOR DE PRUEBA · Confirmación de condiciones · ' + value(p.get('reference')),
                body='\n'.join(lines), status='LOCAL_DRAFT_ONLY', attachments=[],
                acceptance_status='NOT_RECORDED', sent=False, decision_authority=False,
                operational_path='FORBIDDEN')
