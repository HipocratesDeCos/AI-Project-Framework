"""Source-linked article consultation over received files; no operational admission."""
from collections import defaultdict
from decimal import Decimal, localcontext
import json

from eios.company_dossier import selected_batches


ARTICLE_KINDS = {'article', 'inventory', 'stock_policy', 'purchase_line', 'sales_line'}


def unit_price(data):
    # Net line amount divided by documented quantity. No tax or currency conversion.
    with localcontext() as ctx:
        ctx.prec = 50
        return format(Decimal(data['net_amount']) / Decimal(data['quantity']), 'f')


def received_article(db, batch_ids, article_id=None):
    if article_id is not None and (not isinstance(article_id, str) or not article_id.strip()):
        raise ValueError('Selecciona un SKU documentado.')
    batches = selected_batches(db, batch_ids)
    meta = batches[0][1]
    result = {key:meta[key] for key in ('company_id', 'legal_name', 'material_nature', 'as_of_date')}
    result.update(batch_ids=sorted(batch_ids), admission_status='PENDING', operational_path='FORBIDDEN', decision_authority=False,
        scope='Consulta de los archivos seleccionados, pendientes de admisión. Precio neto efectivo = importe neto de línea / cantidad. No determina necesidad de compra ni actualiza existencias con las ventas.')
    entries = defaultdict(list)
    suppliers = defaultdict(list)
    for bid, metadata, records in batches:
        for record in records:
            kind, data = record['kind'], record['data']
            source = dict(batch_id=bid, filename=metadata['filename'], sheet=metadata['sheet'], row=record['source_row'])
            if kind == 'supplier':
                suppliers[data['supplier_id']].append(data)
            if kind in ARTICLE_KINDS:
                entries[data['article_id']].append(dict(kind=kind, data=dict(data), source=source))
    if article_id is None:
        result['articles'] = []
        for identifier in sorted(entries):
            catalog = [entry for entry in entries[identifier] if entry['kind'] == 'article']
            variants = {json.dumps(entry['data'], sort_keys=True) for entry in catalog}
            state = 'MISSING_CATALOG' if not catalog else 'CONFLICTING_CATALOG' if len(variants) > 1 else 'DOCUMENTED_CATALOG'
            result['articles'].append(dict(article_id=identifier, description=catalog[0]['data']['description'] if len(variants) == 1 else None, catalog_status=state))
        return result
    if article_id not in entries:
        raise ValueError('Ese SKU no aparece en los archivos seleccionados.')
    rows = entries[article_id]
    catalog = [entry for entry in rows if entry['kind'] == 'article']
    variants = {json.dumps(entry['data'], sort_keys=True) for entry in catalog}
    catalog_status = 'MISSING_CATALOG' if not catalog else 'CONFLICTING_CATALOG' if len(variants) > 1 else 'DOCUMENTED_CATALOG'
    documented_unit = catalog[0]['data']['unit'] if catalog_status == 'DOCUMENTED_CATALOG' else None
    purchases, sales, inventory, policies = [], [], [], []
    for entry in rows:
        data = entry['data']
        if entry['kind'] in ('purchase_line', 'sales_line'):
            entry['net_unit_price'] = unit_price(data)
            entry['unit_matches_catalog'] = data['unit'] == documented_unit if documented_unit is not None else None
            (purchases if entry['kind'] == 'purchase_line' else sales).append(entry)
        elif entry['kind'] == 'inventory':
            # Never interpret a missing reservation as zero, or sum alternative snapshots.
            data['available'] = format(Decimal(data['physical']) - Decimal(data['reserved']), 'f') if data.get('reserved') is not None else None
            inventory.append(entry)
        elif entry['kind'] == 'stock_policy':
            policies.append(entry)
    purchases.sort(key=lambda e:(e['data']['issue_date'],e['data']['invoice_number'],e['source']['batch_id'],e['source']['row']), reverse=True)
    sales.sort(key=lambda e:(e['data']['issue_date'],e['data']['invoice_number'],e['source']['batch_id'],e['source']['row']), reverse=True)
    grouped = defaultdict(list)
    for entry in purchases:
        d = entry['data']
        grouped[(d['supplier_id'], d['unit'], d['currency'])].append(entry)
    headers = defaultdict(set)
    for entry in purchases:
        d = entry['data']
        headers[(d['supplier_id'], d['invoice_number'])].add((d['issue_date'], d['currency']))
    latest = []
    for (supplier, unit, currency), values in sorted(grouped.items()):
        latest_date = max(entry['data']['issue_date'] for entry in values)
        candidates = [entry for entry in values if entry['data']['issue_date'] == latest_date]
        supplier_variants = {json.dumps(d, sort_keys=True) for d in suppliers.get(supplier, [])}
        status = catalog_status if catalog_status != 'DOCUMENTED_CATALOG' else 'MISSING_SUPPLIER' if not supplier_variants else 'CONFLICTING_SUPPLIER' if len(supplier_variants) > 1 else 'UNIT_MISMATCH' if unit != documented_unit else 'INVOICE_CONFLICT' if any(len(headers[(supplier, entry['data']['invoice_number'])]) > 1 for entry in candidates) else 'AMBIGUOUS_LAST_DATE' if len(candidates) != 1 else 'DOCUMENTED_LAST_LINE'
        last = candidates[0] if status == 'DOCUMENTED_LAST_LINE' else None
        latest.append(dict(supplier_id=supplier, unit=unit, currency=currency, date=latest_date,
            status=status, candidate_count=len(candidates), quantity=last['data']['quantity'] if last else None,
            net_unit_price=last['net_unit_price'] if last else None, sources=[entry['source'] for entry in candidates]))
    stock_status = catalog_status if catalog_status != 'DOCUMENTED_CATALOG' else 'NO_INVENTORY' if not inventory else 'AMBIGUOUS_INVENTORY' if len(inventory) != 1 else 'UNIT_MISMATCH' if inventory[0]['data']['unit'] != documented_unit else 'DOCUMENTED_INVENTORY'
    stock = inventory[0]['data'] if stock_status == 'DOCUMENTED_INVENTORY' else None
    result.update(article_id=article_id, catalog_status=catalog_status, catalog=catalog,
        last_purchases=latest, purchases=purchases, sales=sales, inventory=inventory, policies=policies,
        stock=dict(status=stock_status, physical=stock['physical'] if stock else None,
                   reserved=stock.get('reserved') if stock else None, available=stock.get('available') if stock else None,
                   unit=documented_unit, sources=[entry['source'] for entry in inventory]))
    return result
