"""Printable internal report from a persisted descriptive review only."""
from html import escape
import json
from eios.company_presentation import number_text, date_text


def _text(value):
    return escape('Sin datos' if value is None else str(value), quote=True)


def _rows(items):
    numeric = {'Cantidad', 'Tipo de IVA declarado (%)', 'Línea antes de descuentos', 'Descuento de línea',
               'Valor de descuento declarado', 'Neto', 'IVA', 'Total', 'Cantidad histórica',
               'Precio neto histórico', 'Diferencia por unidad', 'Variación (%)', 'Físico',
               'Reservado', 'Disponible', 'Cobertura (días)', 'Mínimo', 'Falta hasta mínimo',
               'Disponible al guardar', 'Documentos identificados', 'Registros identificados'}
    dates = {'Fecha de corte', 'Fecha del pedido', 'Propuesta guardada el', 'Revisión guardada el',
             'Vencimiento mercancía', 'Vencimiento', 'Fecha', 'Fecha del inventario',
             'Fecha del inventario guardado', 'Capturado el'}
    items = [(key, date_text(value) if key in dates else number_text(value) if key in numeric else value)
             for key, value in items]
    return '<dl>' + ''.join('<div><dt>' + _text(k) + '</dt><dd>' + _text(v) + '</dd></div>' for k, v in items) + '</dl>'


def _detail(value):
    return '<pre>' + _text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2)) + '</pre>'




def _payment_plan(plan):
    if not plan or plan.get('status') == 'NOT_DECLARED':
        return '<h3>CALENDARIO DE PAGOS SIN DECLARAR</h3><p>No se deducen cuotas del total.</p>'
    html = '<h3>CALENDARIO DECLARADO · PENDIENTE DE REVISIÓN</h3>'
    html += '<table><thead><tr><th>Cuota</th><th>Concepto</th><th>Vencimiento</th><th>Importe con IVA</th></tr></thead><tbody>'
    for row in plan['installments']:
        values = [row['sequence'], 'Mercancía' if row['component']=='MERCHANDISE' else 'Portes',
                  date_text(row['due_date']), number_text(row['amount'],2)+' '+plan['currency']]
        html += '<tr>'+''.join('<td>'+_text(value)+'</td>' for value in values)+'</tr>'
    return html+'</tbody></table><p>Cuotas cuadradas con los costes declarados. Soporte, otros gastos y duplicados con tesorería pendientes de revisión. No incorporadas a la proyección.</p>'



def _payment_matching(matching):
    if not matching or matching['status'] == 'NOT_DECLARED':
        return ''
    html = '<h3>CUOTAS Y TESORERÍA · COINCIDENCIAS POR REVISAR</h3><p>'+_text(matching['message'])+'</p>'
    html += '<table><thead><tr><th>Cuota / concepto</th><th>Vencimiento</th><th>Importe</th><th>Pagos con los mismos datos</th><th>Coincidencia compartida</th></tr></thead><tbody>'
    for row in matching['rows']:
        values = [str(row['sequence'])+' · '+('Mercancía' if row['component']=='MERCHANDISE' else 'Portes'),
                  date_text(row['due_date']), number_text(row['amount'],2)+' '+row['currency'],
                  ' | '.join(c['flow_id']+' · '+{'DEMONSTRATED':'Evidencia declarada demostrada',
                      'NOT_EVIDENCED':'Evidencia pendiente','CONFLICTING_DATA':'Datos contradictorios'}[c['evidence_state']]
                      for c in row['candidates']) or 'Sin coincidencia exacta',
                  ', '.join(row['shared_candidate_ids']) or 'Ninguna en las coincidencias listadas']
        html += '<tr>'+''.join('<td>'+_text(value)+'</td>' for value in values)+'</tr>'
    html += '</tbody></table><p>No se comprueba proveedor, factura ni correspondencia documental. Una coincidencia única requiere revisión; su ausencia no acredita un pago nuevo. No se confirma duplicación ni conciliación.</p>'
    return html+'<ul>'+''.join('<li>'+_text(issue)+'</li>' for issue in matching['issues'])+'</ul>'



def _payment_associations(associations):
    if not associations or not associations.get('rows'):
        return ''
    html='<h3>ASOCIACIONES DECLARADAS · REVISIÓN DOCUMENTAL PENDIENTE</h3>'
    for event in associations['rows']:
        binding=event['binding']
        html+=_rows([('Cuota',event['sequence']),('Acción','Asociación declarada' if binding else 'Dejada pendiente'),
                     ('Pago',binding['flow_id'] if binding else None),('Responsable declarado',event['actor']),
                     ('Motivo',event['reason']),('Declarado el',date_text(event['created_at'])),
                     ('Revisión de declaraciones',event['revision'])])
        if binding:
            for locator in binding['locators']:
                html+=_rows([('Documento',locator['document_ref']),('Página',locator['page']),('Sección',locator['section'])])
    return html+'<p>Declaraciones locales: no autentican al responsable ni validan el soporte. No completan los controles documentales ni modifican los flujos o la proyección.</p>'


def _financial_context(context, execution=None):
    if not context:
        return ''
    snapshot = context.get('financial_snapshot') or {}
    capital = context.get('working_capital_input') or {}
    html = _rows([('Fecha de corte', context['as_of_date']),
                  ('Tesorería declarada', number_text(snapshot.get('available_treasury'), 2) + ' ' + str(snapshot.get('currency') or '')),
                  ('Activo corriente documentado', number_text(capital.get('current_assets'), 2) + ' ' + str(capital.get('currency') or '')),
                  ('Pasivo corriente documentado', number_text(capital.get('current_liabilities'), 2) + ' ' + str(capital.get('currency') or '')),
                  ('Movimientos vinculados', number_text(len(context['cash_flows']))),
                  ('Pendientes de validar', number_text(context['evidence_pending_count']))])
    html += '<p>Datos documentales vinculados; no acreditan conciliación, completitud ni viabilidad de la compra.</p>'
    html += '<table><thead><tr><th>Referencia</th><th>Vencimiento</th><th>Tipo</th><th>Importe / moneda</th><th>Validación</th></tr></thead><tbody>'
    for item in context['cash_flows']:
        f = item['canonical']
        state = {'DEMONSTRATED':'Evidencia declarada demostrada', 'NOT_EVIDENCED':'Pendiente de validar', 'CONFLICTING_DATA':'Datos contradictorios'}[f['evidence_state']]
        values = [item['record_id'], date_text(f['due_date']), 'Cobro' if f['flow_type'] == 'COLLECTION' else 'Pago',
                  number_text(f['amount'], 2) + ' ' + str(f['currency'] or ''), state]
        html += '<tr>' + ''.join('<td>' + _text(value) + '</td>' for value in values) + '</tr>'
    html += '</tbody></table><ul>'
    html += ''.join('<li>' + _text(item) + '</li>' for item in context['issues'] + [message for message in context['integration_pending'] if not (execution and len(execution.get('parameter_configurations',[]))==2 and message.startswith('Conectar horizonte'))])
    return html + '</ul>'



def _finance_execution(execution):
    if not execution:
        return ''
    html='<h3>PROYECCIÓN DOCUMENTAL · COMPRA SIN EVALUAR</h3><p>'+_text(execution['message'])+'</p>'
    for config in execution.get('parameter_configurations',[]):
        html+=_rows([('Horizonte activo' if config['parameter_id']=='P-FIN-001' else 'Tesorería mínima activa',
                      number_text(config['value'])+' '+config['unit'])])
    result=execution.get('finance_result')
    if result:
        p=result['projection']
        html+=_rows([('Estado de proyección','Calculada' if p['status']=='DETERMINED' else 'No determinable'),
                     ('Fin del horizonte',date_text(p['horizon_end'])),
                     ('Mínimo saldo previsto en los flujos suministrados',number_text(p['financial_capacity_forecast'],2)+' '+result['currency'])])
        html+='<p>Movimientos sin resolver: '+_text(', '.join(p['unresolved_flow_ids']) or 'Ninguno señalado por el motor')+'</p>'
    html+='<ul>'+''.join('<li>'+_text(message)+'</li>' for message in execution['limitations'])+'</ul>'
    return html


def render_report(report):
    """Render captured values; never calculate indicators, hydrate data or decide."""
    p = report['proposal']
    context = p.get('documentary_context_at_save')
    terms = p.get('commercial_terms') or {}
    price = report['price']
    stock = report['stock']
    currency = p.get('currency')
    def amount(key):
        value = p.get(key)
        return 'Pendiente / sin datos' if value is None else number_text(value, 2) + ' ' + str(currency)
    pieces = ['<!doctype html><html lang="es"><head><meta charset="utf-8">',
              '<meta name="viewport" content="width=device-width,initial-scale=1">',
              '<title>EIOS · Informe de propuesta · ' + _text(report['reference']) + '</title>',
              '<style>body{font:14px system-ui,sans-serif;color:#15213c;background:#edf3fa;margin:0}main{max-width:950px;margin:24px auto;padding:32px;background:white}h1{font-size:25px;color:#13346f}h2{font-size:17px;color:#13346f;margin-top:26px}p,li{line-height:1.5}.status{padding:16px;background:#fff5df;border-left:5px solid #ad790f}.status strong{display:block}dl{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}dl>div{padding:10px;background:#f1f6fc;break-inside:avoid}dt{font-size:12px;color:#52647a}dd{margin:4px 0 0;font-weight:600}pre,dd,td{overflow-wrap:anywhere;white-space:pre-wrap}pre{font-size:11px}table{border-collapse:collapse;width:100%;table-layout:fixed}td,th{padding:8px;border:1px solid #ccd7e4;text-align:left;vertical-align:top}thead{display:table-header-group}button{padding:12px 20px;background:#0a369d;color:white;border:0;border-radius:5px;cursor:pointer}footer{border-top:1px solid #ccd7e4;padding-top:12px;font-size:11px;overflow-wrap:anywhere}@page{size:A4;margin:16mm}@media print{body{background:white}main{margin:0;padding:0;max-width:none}.toolbar{display:none}h2,h3{break-after:avoid}tr{break-inside:avoid}pre{white-space:pre-wrap}.status{border:1px solid #ad790f;border-left:5px solid #ad790f}a{color:inherit}}</style></head><body><main>',
              '<div class="toolbar"><button type="button" onclick="window.print()">Imprimir / Guardar como PDF</button><p>Para descargarlo, selecciona «Guardar como PDF» en el diálogo de impresión.</p></div>',
              '<h1>EIOS · INFORME INTERNO DE PROPUESTA</h1>',
              '<div class="status"><strong>' + _text(report['title']) + '</strong><p>' + _text(report['reason']) + '</p><p>Material sintético de prueba. No constituye aceptación al proveedor ni autorización de compra.</p></div>',
              '<h2>1. IDENTIFICACIÓN Y FECHAS</h2>',
              _rows([('Referencia', report['reference']), ('Empresa', context.get('company_name') if context else report['company_id']),
                     ('Código de empresa', report['company_id']), ('Versión documental', report['dataset_id']),
                     ('Fecha de corte', report['documentary_cutoff']), ('Fecha del pedido', p.get('order_date')),
                     ('Propuesta guardada el', p.get('created_at')), ('Revisión guardada el', report.get('reviewed_at')),
                     ('Código del proveedor', p.get('supplier_id')), ('Razón social del proveedor', (p.get('supplier_commercial_at_save') or {}).get('legal_name')),
                     ('Persona de contacto', (p.get('supplier_commercial_at_save') or {}).get('contact_name')), ('Lugar de entrega', p.get('delivery_location')), ('Código del artículo', p.get('article_id'))]),
              '<h2>2. IMPORTES Y CONDICIONES DECLARADAS</h2>',
              _rows([('Cantidad', p.get('quantity')), ('Unidad', p.get('unit')),
                     ('Precio neto unitario', amount('unit_price')), ('Mercancía neta', amount('net')),
                     ('IVA de mercancía', amount('tax')), ('Tipo de IVA declarado (%)', p.get('vat_percent')), ('Total mercancía', amount('total')),
                     ('Total operación', amount('operation_total')), ('Vencimiento mercancía', p.get('due_date'))])]
    if terms:
        labels = {'pricing_mode': 'Modalidad de precio', 'gross_line': 'Línea antes de descuentos',
                  'discount_mode': 'Modalidad de descuento', 'discount_amount': 'Descuento de línea',
                  'discount_value': 'Valor de descuento declarado'}
        pieces.append(_rows([(label, terms.get(key)) for key, label in labels.items()]))
        shipping = terms.get('shipping') or {}
        pieces.append('<h3>Portes declarados</h3>' + _rows([
            ('Modalidad', {'BUYER':'A cargo de la empresa', 'SUPPLIER':'A cargo del proveedor', 'INCLUDED':'Incluidos en precio', 'NONE':'Sin portes', 'PENDING':'Pendientes de confirmar'}.get(shipping.get('mode'), 'Sin datos')),
            ('Neto', shipping.get('net')), ('IVA', shipping.get('tax')), ('Total', shipping.get('total')),
            ('Moneda', currency), ('Emisor', shipping.get('billed_by')), ('Vencimiento', shipping.get('due_date'))]))
    else:
        pieces.append('<p>Sin desglose comercial conservado en esta propuesta.</p>')
    pieces.append(_payment_plan(p.get('payment_plan')))
    pieces.extend(['<h2>3. COMPARACIÓN CON LA ÚLTIMA COMPRA</h2>', '<p>' + _text(price.get('message')) + '</p>'])
    if price.get('status') == 'COMPARABLE':
        ref = price['reference']
        pieces.append(_rows([('Factura histórica', ref.get('invoice_number')), ('Fecha', ref.get('issue_date')),
                             ('Cantidad histórica', ref.get('quantity')), ('Unidad', ref.get('unit')),
                             ('Precio neto histórico', ref.get('effective_net_unit_price')), ('Moneda', ref.get('currency')),
                             ('Diferencia por unidad', price.get('difference_per_unit')), ('Variación (%)', price.get('difference_percent'))]))
        pieces.append('<p>Las condiciones de la referencia histórica se conservan en la revisión identificada al final del informe.</p>')
    pieces.extend(['<h2>4. STOCK, COBERTURA Y MÍNIMO</h2>', '<p>' + _text(stock.get('message')) + '</p>'])
    inventory = stock.get('inventory')
    if inventory:
        pieces.append(_rows([('Fecha del inventario', inventory.get('as_of_date')), ('Unidad', inventory.get('unit')),
                             ('Físico', inventory.get('physical')), ('Reservado', inventory.get('reserved')), ('Disponible', inventory.get('available'))]))
    coverage = stock.get('coverage')
    if coverage:
        pieces.append(_rows([('Cobertura (días)', coverage.get('coverage_days')),
                             ('Previsión aplicable en fecha del pedido', 'Sí' if stock.get('forecast_applicable_on_order_date') else 'No')]))
        pieces.append('<p>La cobertura procede de la planificación sintética conservada en esta revisión.</p>')
    else:
        pieces.append('<p>Cobertura: sin cálculo disponible en esta revisión.</p>')
    minimum = p.get('stock_context_at_save')
    pieces.append('<h3>Mínimo al guardar la propuesta</h3>')
    if minimum:
        m = minimum.get('minimum') or {}
        inv = minimum.get('inventory') or {}
        pieces.append(_rows([('Mínimo', m.get('value')), ('Unidad del mínimo', m.get('unit')),
                             ('Origen', {'AUTOMATIC':'Automático: 10 % de última compra', 'MANUAL':'Manual'}.get(m.get('source'), 'Sin configurar')),
                             ('Estado', m.get('label')), ('Falta hasta mínimo', m.get('shortage')),
                             ('Disponible al guardar', inv.get('available')), ('Fecha del inventario guardado', inv.get('as_of_date')),
                             ('Capturado el', minimum.get('captured_at'))]))
    else:
        pieces.append('<p>Sin captura anterior; no se reconstruye con datos actuales.</p>')
    pieces.extend(['<p>Necesidad de reposición, rotación y cantidad recomendada: pendientes de evaluación. Las referencias de stock y planificación son sintéticas y fechadas.</p>',
                   '<h2>5. TESORERÍA Y DECISIÓN</h2>', _payment_matching(report.get('payment_matching')), _payment_associations(report.get('payment_associations')), _financial_context(report.get('financial_context'),report.get('finance_execution')), _finance_execution(report.get('finance_execution')), '<p>' + _text(report['finance'].get('message')) + '</p>',
                   '<p>Evaluación financiera: PENDIENTE. Reglas y conclusión del decisor: PENDIENTES. Decisión humana: no registrada en esta revisión.</p>',
                   '<h2>6. COMPROBACIONES PENDIENTES</h2><ul>',
                   *['<li>' + _text(item) + '</li>' for item in report.get('pending', [])], '</ul>',
                   '<h2>7. FUENTES Y TRAZABILIDAD</h2>'])
    if context:
        pieces.append(_rows([('Material declarado', context.get('material_nature')),
                             ('Documentos identificados', len(context.get('sources', []))),
                             ('Registros identificados', len(context.get('records', []))),
                             ('Huella del contexto documental', context.get('fingerprint'))]))
        pieces.append('<p>El listado identifica el conjunto documental vinculado; no significa que todos los documentos hayan intervenido en cada cálculo. Las huellas identifican contenido y no acreditan su suficiencia o admisión.</p>')
        pieces.append('<table><thead><tr><th>Referencia</th><th>Documento y metadatos conservados</th></tr></thead><tbody>')
        for source in context.get('sources', []):
            pieces.append('<tr><td>' + _text(source.get('document_ref')) + '</td><td>' + _detail(source) + '</td></tr>')
        pieces.append('</tbody></table>')
    else:
        pieces.append('<p>SIN CAPTURA DOCUMENTAL: propuesta anterior. No se atribuyen fuentes retrospectivamente.</p>')
    pieces.append('<footer>' + _rows([('Identificador de propuesta', report['proposal_id']), ('Identificador de revisión', report['review_id']),
                                     ('Versión de revisión', report['version']), ('Ruta operacional', report['operational_path'])]) +
                  '<p>Informe interno de la revisión guardada. No consulta datos actuales ni ejecuta una nueva evaluación. Puede contener información interna de la empresa.</p></footer></main></body></html>')
    return ''.join(pieces)
