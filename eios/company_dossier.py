"""Read-only reference checks over explicitly selected received source batches."""
import json
import sqlite3
from collections import defaultdict
from decimal import Decimal
from hashlib import sha256


def check_dossier(db, batch_ids):
    if (not isinstance(batch_ids, list) or not 1 <= len(batch_ids) <= 100
            or any(not isinstance(x, str) or len(x) != 64 for x in batch_ids)
            or len(set(batch_ids)) != len(batch_ids)):
        raise ValueError('Selecciona entre 1 y 100 archivos distintos del mismo expediente y fecha de corte.')
    with sqlite3.connect(db) as c:
        if not c.execute("SELECT 1 FROM sqlite_master WHERE name='received_company_batch'").fetchone():
            raise ValueError('No hay archivos recibidos.')
        rows = c.execute('SELECT batch_id,metadata_json,records_json FROM received_company_batch WHERE batch_id IN (' + ','.join('?' for _ in batch_ids) + ')', batch_ids).fetchall()
    if len(rows) != len(batch_ids):
        raise ValueError('Algún archivo seleccionado ya no está disponible.')
    batches = [(bid, json.loads(meta), json.loads(records)) for bid, meta, records in sorted(rows)]
    contexts = {(m['company_id'], m['legal_name'], m['material_nature'], m['as_of_date']) for _, m, _ in batches}
    if len(contexts) != 1:
        raise ValueError('Selecciona archivos de una sola empresa, naturaleza de datos y fecha de corte.')
    company, name, nature, cutoff = contexts.pop()
    entries = []
    issues = []
    def issue(code, message, source, field='', related=None):
        issues.append(dict(code=code, message=message, field=field, source=source, related=related))
    for bid, meta, records in batches:
        for record in records:
            source = dict(batch_id=bid, filename=meta['filename'], sheet=meta['sheet'], row=record['source_row'])
            entries.append((record['kind'], record['data'], source))
        if meta['kind'] in ('document', 'balance', 'cash_flow'):
            issue('OUTSIDE_SCOPE', 'Este archivo no se concilia financieramente en esta revisión de referencias.', dict(batch_id=bid, filename=meta['filename'], sheet=meta['sheet'], row=None))
        if meta.get('warning_count', 0):
            issue('SOURCE_WARNINGS', 'La recepción conserva avisos que deben revisarse: ' + str(meta['warning_count']), dict(batch_id=bid, filename=meta['filename'], sheet=meta['sheet'], row=None))
    catalog = {kind: defaultdict(list) for kind in ('supplier', 'customer', 'article')}
    for kind, data, source in entries:
        if kind in catalog:
            catalog[kind][data[kind + '_id']].append((data, source))
    for kind, index in catalog.items():
        for identifier, values in index.items():
            first, origin = values[0]
            for data, source in values[1:]:
                conflict = data != first
                issue('CONFLICTING_ID' if conflict else 'REPEATED_ID', ('Datos distintos para ' if conflict else 'Referencia repetida: ') + identifier, source, kind + '_id', origin)
    for kind, data, source in entries:
        references = []
        if kind == 'article' and data.get('supplier_id'):
            references.append(('supplier', 'supplier_id'))
        if kind == 'purchase_line':
            references.extend((('supplier', 'supplier_id'), ('article', 'article_id')))
        if kind == 'sales_line':
            references.extend((('customer', 'customer_id'), ('article', 'article_id')))
        if kind in ('inventory', 'stock_policy'):
            references.append(('article', 'article_id'))
        for target, field in references:
            identifier = data.get(field)
            matches = catalog[target].get(identifier, [])
            if not matches:
                issue('MISSING_REFERENCE', 'No se encuentra ' + str(identifier) + ' en el catálogo seleccionado de ' + {'supplier':'proveedores', 'customer':'clientes', 'article':'artículos'}[target] + '.', source, field)
            elif target == 'article' and data.get('unit'):
                # Exact documented units only. No description-based or unit conversion guesses.
                for article, origin in matches:
                    if article.get('unit') != data['unit']:
                        issue('UNIT_MISMATCH', 'Unidad ' + data['unit'] + ' distinta de la del catálogo: ' + str(article.get('unit')), source, 'unit', origin)
    stock = defaultdict(list)
    invoice_headers = {}
    movements = {}
    for kind, data, source in entries:
        if kind in ('inventory', 'stock_policy'):
            key = (data['article_id'], data['unit'])
            for previous_kind, previous, origin in stock[key]:
                fields = ('physical', 'reserved') if kind == previous_kind == 'inventory' else ()
                fields += ('minimum_stock', 'safety_stock', 'reorder_point', 'lead_time_days')
                for field in fields:
                    if data.get(field) is not None and previous.get(field) is not None and Decimal(data[field]) != Decimal(previous[field]):
                        issue('STOCK_CONFLICT', 'Valores de stock o parámetros incompatibles para ' + data['article_id'], source, field, origin)
            stock[key].append((kind, data, source))
        if kind in ('purchase_line', 'sales_line'):
            signature = (kind, json.dumps(data, sort_keys=True))
            if signature in movements:
                issue('REPEATED_LINE', 'Línea idéntica repetida; comprueba si corresponde a una duplicación documental.', source, 'invoice_number', movements[signature])
            else:
                movements[signature] = source
            party = 'supplier_id' if kind == 'purchase_line' else 'customer_id'
            key = (kind, data[party], data['invoice_number'])
            header = (data['issue_date'], data['currency'])
            if key in invoice_headers and invoice_headers[key][0] != header:
                issue('INVOICE_CONFLICT', 'Fecha o moneda contradictoria en líneas de la misma factura.', source, 'invoice_number', invoice_headers[key][1])
            else:
                invoice_headers[key] = (header, source)
    return dict(company_id=company, legal_name=name, material_nature=nature, as_of_date=cutoff,
                batch_ids=sorted(batch_ids), review_id=sha256(json.dumps(sorted(batch_ids)).encode()).hexdigest(),
                record_count=len(entries), issue_count=len(issues), issues=issues,
                result='REFERENCES_PENDING' if issues else 'NO_REFERENCE_CONFLICTS_FOUND',
                scope='Referencias y unidades de los archivos seleccionados. No acredita integridad documental, saldos, impuestos ni admisión operativa.',
                admission_status='PENDING', operational_path='FORBIDDEN', decision_authority=False)
