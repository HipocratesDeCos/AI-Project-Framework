"""Read-only preflight for the explicit stock-planning workbook template.

Not called by reception/activation yet. No database writes or purchase authority.
"""
from datetime import date, timedelta
from decimal import Decimal
from hashlib import sha256

from eios.company_tables import read_table, normalize, number, source_date

PLAN_HEADERS = ['SKU','Unidad','Consumo / día','Vigente desde','Vigente hasta',
                'Entrega (días)','Objetivo (días)','Múltiplo compra','Recepciones',
                'Responsable','Referencia','Estado']
RECEIPT_HEADERS = ['Referencia','SKU','Unidad','Cantidad pendiente','Fecha prevista',
                   'Responsable','Soporte','Naturaleza']


def _text(value):
    if not isinstance(value, str) or not value.strip() or len(value) > 256:
        raise ValueError('Completa los textos de planificación con valores fijos.')
    return value.strip()


def _number(value, positive=False, integer=False):
    n = number(value, 'ES')
    if n < 0 or n > Decimal('1000000000') or positive and n == 0 or integer and n != int(n):
        raise ValueError('Cantidad de planificación fuera de rango.')
    return n


def preview(content, filename, cutoff):
    """Validate a single byte source; return a source-bound, non-active draft."""
    cut = source_date(cutoff)
    guide = read_table(content, filename, sheet='97_Guia_Carga')
    if guide['headers'] != ['Hoja','Tipo EIOS','Campo EIOS','Columna del archivo']:
        raise ValueError('Guía de carga incompatible.')
    sources = {}
    for kind in ('article', 'inventory'):
        entries = [r['values'] for r in guide['rows'] if r['values'][1] == kind]
        if len({r[0] for r in entries}) != 1:
            raise ValueError('Se requiere una sola hoja de artículos y de inventario.')
        table = read_table(content, filename, sheet=entries[0][0])
        mapping = {}
        for _, _, field, header in entries:
            if field in mapping or table['headers'].count(header) != 1:
                raise ValueError('Mapeo repetido o ambiguo en la guía.')
            mapping[field] = table['headers'].index(header)
        result = normalize(table, kind, mapping, cut, 'ES')
        if result['errors']:
            raise ValueError('Revisa artículos o inventario: '+str(result['errors'])[:500])
        sources[kind] = {r['data']['article_id']:r['data'] for r in result['records']}
        if len(sources[kind]) != len(result['records']):
            raise ValueError('SKU duplicado en la fuente.')
    plans_table = read_table(content, filename, sheet='013_Planificacion_Stock', header_row=26)
    if plans_table['headers'] != PLAN_HEADERS:
        raise ValueError('Cabecera de planificación incompatible con esta plantilla.')
    plans = {}
    expected = 27
    plan_rows = plans_table['rows']
    for row in plan_rows:
        if row['row'] != expected:
            break  # Template data block ends at the first physical blank row.
        expected += 1
        v = row['values']
        sku, unit = _text(v[0]), _text(v[1])
        stock = sources['inventory'].get(sku)
        article = sources['article'].get(sku)
        if sku in plans or not stock or not article or stock['unit'] != unit or article['unit'] != unit:
            raise ValueError('SKU o unidad incompatible en planificación: '+sku)
        if stock.get('observation_date') != cut or stock['reserved'] is None:
            raise ValueError('Inventario sin fecha o reservas aplicables al corte: '+sku)
        start, end = source_date(v[3]), source_date(v[4])
        if not start <= cut <= end:
            raise ValueError('Previsión no vigente al corte: '+sku)
        daily = _number(v[2]); lead = _number(v[5], integer=True)
        target = _number(v[6], positive=True, integer=True); step = _number(v[7], positive=True)
        if lead > 365 or target > 365 or date.fromisoformat(cut)+timedelta(days=int(lead+target)) > date.fromisoformat(end):
            raise ValueError('La vigencia no cubre entrega y objetivo: '+sku)
        state = _text(v[8])
        if state not in ('DESCONOCIDAS','NINGUNA DECLARADA','VER TABLA PENDIENTES') or v[11] != 'SUPUESTO DE PRUEBA':
            raise ValueError('Estado de prueba o recepciones incompatible: '+sku)
        if stock.get('safety_stock') is None:
            raise ValueError('Falta stock de seguridad: '+sku)
        plans[sku] = dict(article_id=sku, unit=unit, as_of_date=cut, valid_from=start, valid_to=end,
                          daily_demand=str(daily), lead_time_days=int(lead), target_days=int(target),
                          purchase_step=str(step), available_at_order=stock['available'],
                          safety_stock=stock['safety_stock'], pending_receipts_state=state,
                          actor=_text(v[9]), source_reference=_text(v[10]), receipts=[],
                          demand_basis='ADDITIONAL_DEMAND_EXCLUDES_EXISTING_RESERVATIONS')
    if set(plans) != set(sources['article']):
        raise ValueError('Falta planificación de algún artículo del libro.')
    if any(any(v is not None for v in r['values'][1:]) for r in plan_rows if r['row'] >= expected):
        raise ValueError('Hay datos fuera del bloque continuo de planificación.')
    table = read_table(content, filename, sheet='014_Recepciones_Pendientes')
    if table['headers'] != RECEIPT_HEADERS:
        raise ValueError('Cabecera de recepciones incompatible.')
    seen = set(); expected = 2
    for row in table['rows']:
        if row['row'] != expected:
            break
        expected += 1
        ref, sku, unit, qty, when, actor, support, nature = row['values']
        ref = _text(ref)
        if ref in seen or sku not in plans or plans[sku]['unit'] != unit or nature != 'SYNTHETIC_TEST':
            raise ValueError('Recepción duplicada o incompatible: '+ref)
        seen.add(ref); p = plans[sku]; when = source_date(when)
        if not cut < when <= p['valid_to']:
            raise ValueError('Recepción fuera del periodo posterior al corte: '+ref)
        if p['pending_receipts_state'] != 'VER TABLA PENDIENTES':
            raise ValueError('Recepción contradice el estado declarado: '+sku)
        _text(actor); _text(support)
        p['receipts'].append(dict(reference=ref, date=when, quantity=str(_number(qty, positive=True))))
    for p in plans.values():
        if p['pending_receipts_state'] == 'VER TABLA PENDIENTES' and not p['receipts']:
            raise ValueError('Estado con entradas pero sin detalle: '+p['article_id'])
    if any(any(v is not None for v in r['values'][1:]) for r in table['rows'] if r['row'] >= expected):
        raise ValueError('Hay recepciones fuera del bloque continuo.')
    return dict(schema='WORKBOOK-STOCK-PREFLIGHT-01', source_sha256=sha256(content).hexdigest(),
                as_of_date=cut, plans=plans, status='VALIDATED_NOT_ACTIVE',
                material_nature='SYNTHETIC', decision_authority=False, operational_path='FORBIDDEN')
