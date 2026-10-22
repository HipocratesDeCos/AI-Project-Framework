"""Saved synthetic sales offers, separate from invoices and inventory movements."""
from copy import deepcopy
from datetime import date, datetime, timezone
from decimal import Decimal, localcontext
from html import escape
import json
import sqlite3
from uuid import uuid4

from eios.company_commercial_terms import commercial_terms, number
from eios.company_presentation import number_text, date_text
from eios.company_proposal_context import capture_context

SCHEMA = '''CREATE TABLE IF NOT EXISTS manual_sales_proposal (
proposal_id TEXT PRIMARY KEY,dataset_id TEXT NOT NULL,reference TEXT NOT NULL,
created_at TEXT NOT NULL,payload TEXT NOT NULL,UNIQUE(dataset_id,reference))'''


def offers(db, dataset):
    with sqlite3.connect(db) as c:
        c.execute(SCHEMA)
        return [json.loads(r[0]) for r in c.execute(
            'SELECT payload FROM manual_sales_proposal WHERE dataset_id=? ORDER BY created_at DESC,proposal_id', (dataset,))]


def text(value, label, maximum=500):
    if not isinstance(value, str) or not value.strip() or len(value.strip()) > maximum:
        raise ValueError('Indica '+label+' (hasta '+str(maximum)+' caracteres).')
    return value.strip()


def orientation(state, customer, article):
    """A historical reference is comparable only in the exact unit and EUR."""
    sales = []
    unlinked=0
    for invoice in state['sales']['invoices']:
        if invoice['customer_id'] != customer or invoice['currency'] != 'EUR':
            continue
        for line in invoice['lines']:
            if not line['article_id'] or not line['unit']:unlinked+=1
            if (line['article_id'] != article['article_id'] or line['unit'] != article['unit_as_documented']
                    or line['currency'] != 'EUR'):
                continue
            try:
                quantity, net = Decimal(line['quantity']), Decimal(line['net_amount'])
                if not quantity.is_finite() or quantity <= 0 or not net.is_finite() or net < 0:
                    continue
            except (TypeError, ValueError, ArithmeticError):
                continue
            sales.append(dict(invoice=invoice['invoice_number'], date=invoice['issue_date'],
                quantity=str(quantity), net_unit_price=str(net/quantity), unit=line['unit'], currency='EUR',
                source_refs=deepcopy(line['source_refs']),manual_link=deepcopy(line.get('manual_link'))))
    # Multiple latest-day lines are retained; an arbitrary invoice does not become "the last price".
    latest_date = max((s['date'] for s in sales), default=None)
    latest = [s for s in sales if s['date'] == latest_date]
    purchases = [p for p in state['history'].get(article['article_id'], []) if p['comparable']]
    cost_date = max((p['issue_date'] for p in purchases), default=None)
    costs = [deepcopy(p) for p in purchases if p['issue_date'] == cost_date]
    unit_cost = costs[0]['effective_net_unit_price'] if len(costs) == 1 else None
    cost_scope='LAST_COMPARABLE_PURCHASE_EXCLUDES_OTHER_COSTS'
    if not purchases and article.get('commercial_catalogue') and article.get('catalogue_unit_cost') is not None:
        unit_cost=article['catalogue_unit_cost'];cost_scope='EXPLICIT_SYNTHETIC_CATALOGUE_NOT_LAST_PURCHASE'
    inventory = deepcopy(state['inventory'].get(article['article_id']))
    if inventory and inventory.get('unit') != article['unit_as_documented']:
        inventory = None
    return dict(unlinked_customer_sales_lines=unlinked,sales_history=sales,latest_sales=latest, purchase_references=costs, reference_unit_cost=unit_cost,
                inventory=inventory, cost_scope=cost_scope, catalogue_reference=deepcopy(article.get('commercial_catalogue')))


def save_offer(db, state, data, *, persist=True):
    with localcontext() as context:
        context.prec = 60
        return _save_offer(db, state, data, persist)


def _save_offer(db, state, data, persist):
    if data.get('context_fingerprint') != state['documentary_context']['fingerprint']:
        raise ValueError('La versión documental ha cambiado. Recarga la pantalla.')
    if state['documentary_context']['material_nature'] != 'SYNTHETIC':
        raise ValueError('Esta primera versión requiere una empresa sintética de pruebas.')
    expected = data.get('commercial_parameter_revision')
    if expected is not None and (type(expected) is not int or expected != state.get('sales_parameters',{}).get('revision',0)):
        raise ValueError('Los parámetros comerciales han cambiado. Recarga la pantalla.')
    customer = next((c for c in state['customers'] if c['customer_id'] == data.get('customer_id')), None)
    if customer is None:
        raise ValueError('Selecciona un cliente de esta empresa y versión.')
    missing=[]
    def document_text(key,label,maximum=500):
        if not persist and data.get(key) in (None,''):
            missing.append(label);return None
        return text(data.get(key),label,maximum)
    reference = document_text('reference','referencia',100)
    dates = {}
    for key in ('offer_date', 'valid_until', 'delivery_date', 'due_date'):
        if not persist and key in ('valid_until','delivery_date') and data.get(key) in (None,''):
            dates[key]=None;missing.append('fecha de vigencia' if key=='valid_until' else 'fecha de entrega');continue
        try:
            dates[key] = date.fromisoformat(data[key]).isoformat()
        except (KeyError, ValueError, TypeError):
            raise ValueError('Indica fechas válidas de oferta, vigencia, entrega y cobro.') from None
    if any(dates[k] is not None and dates[k] < dates['offer_date'] for k in ('valid_until','delivery_date','due_date')):
        raise ValueError('Vigencia, entrega y cobro no pueden preceder a la oferta.')
    raw = data.get('lines')
    if not isinstance(raw, list) or not 1 <= len(raw) <= 30:
        raise ValueError('Añade entre 1 y 30 líneas de artículos.')
    lines = []
    for item in raw:
        if not isinstance(item, dict):
            raise ValueError('Línea de artículo inválida.')
        article = next((a for a in state['articles'] if a['article_id'] == item.get('article_id')), None)
        if article is None:
            raise ValueError('Cada artículo debe pertenecer a esta versión.')
        tax_known=item.get('vat_percent') not in (None,'')
        if not tax_known and persist:raise ValueError('Indica el IVA de cada línea antes de guardar.')
        if not tax_known:missing.append('IVA de '+article['article_id'])
        # Zero is only an arithmetic placeholder for the net-price helper. It is
        # never exposed or conserved as a supplied tax when the tax is missing.
        terms = commercial_terms(dict(item, vat_percent=item.get('vat_percent') if tax_known else '0', pricing_mode='BEFORE_DISCOUNT', discount_mode='PERCENT',
            order_date=dates['offer_date'], due_date=dates['due_date'], shipping_mode='NONE'))
        basis = orientation(state, customer['customer_id'], article)
        net = Decimal(terms['net'])
        cost = basis['reference_unit_cost']
        reference_margin = None
        if cost is not None and net > 0:
            reference_margin = str(((net-Decimal(cost)*Decimal(str(item['quantity'])))/net*100).quantize(Decimal('.01')))
        lines.append(dict(article_id=article['article_id'], description=article.get('description') or article['article_id'],
            unit=article['unit_as_documented'], quantity=str(number(item,'quantity')),
            unit_price=str(number(item,'unit_price')), discount_percent=str(number(item,'discount_value',Decimal(100))),
            vat_percent=str(number(item,'vat_percent',Decimal(100))) if tax_known else None,tax_status='SUPPLIED' if tax_known else 'NOT_SUPPLIED',
            net_amount=terms['net'], vat_amount=terms['tax'] if tax_known else None,total=terms['total'] if tax_known else None,
            orientation=basis, reference_margin_percent=reference_margin))
    freight = number(data,'freight_net')
    if freight != freight.quantize(Decimal('.01')):
        raise ValueError('Los portes facturados admiten dos decimales.')
    freight_vat = number(data,'freight_vat_percent',Decimal(100)) if data.get('freight_vat_percent') not in (None,'') else None
    if freight>0 and freight_vat is None:
        if persist:raise ValueError('Indica el IVA de los portes facturados antes de guardar.')
        missing.append('IVA de los portes')
    freight_tax = (freight*freight_vat/100).quantize(Decimal('.01')) if freight_vat is not None else Decimal(0) if freight==0 else None
    net = sum((Decimal(l['net_amount']) for l in lines), freight)
    tax = sum((Decimal(l['vat_amount']) for l in lines),freight_tax) if freight_tax is not None and all(l['vat_amount'] is not None for l in lines) else None
    warnings = []
    requested = {}
    for line in lines:
        key = line['article_id']
        requested[key] = requested.get(key,Decimal(0))+Decimal(line['quantity'])
    for key, quantity in requested.items():
        inventory = next(l['orientation']['inventory'] for l in lines if l['article_id']==key)
        if inventory is None:
            warnings.append(key+': sin stock comparable; disponibilidad pendiente de comprobar.')
        elif quantity > Decimal(str(inventory['available'])):
            warnings.append(key+': la cantidad total supera el stock disponible de referencia a '+inventory['as_of_date']+'.')
    payload = dict(warnings=warnings,schema='COMPANY-SALES-OFFER-01', proposal_id=str(uuid4()), dataset_id=data['dataset_id'],
        reference=reference, created_at=datetime.now(timezone.utc).isoformat(), **dates,
        company=deepcopy(state['info']['company']), customer=deepcopy(customer),
        delivery_location=document_text('delivery_location','lugar de entrega'),
        payment_terms=document_text('payment_terms','condiciones de cobro'),
        currency='EUR', lines=lines, freight_net=str(freight), freight_vat_percent=str(freight_vat) if freight_vat is not None else None,
        freight_tax=str(freight_tax) if freight_tax is not None else None,net_amount=str(net),vat_amount=str(tax) if tax is not None else None,total=str(net+tax) if tax is not None else None,
        documentary_context=deepcopy(state['documentary_context']),
        status='SAVED_SYNTHETIC_OFFER', decision_authority=False, operational_path='FORBIDDEN')
    payload['document_completion_missing']=missing
    payload['document_ready']=not missing and tax is not None
    from eios.company_sales_negotiation import analyze_offer
    payload['negotiation']=analyze_offer(payload,state,data)
    if data['dataset_id'] != state['documentary_context']['dataset_id']:
        raise ValueError('La empresa y versión no coinciden.')
    if not persist:
        payload['status'] = 'PREVIEW_SYNTHETIC_OFFER'
        return payload
    with sqlite3.connect(db) as c:
        c.execute(SCHEMA)
        c.execute('BEGIN IMMEDIATE')
        if capture_context(c,data['dataset_id'])['fingerprint'] != data['context_fingerprint']:
            raise ValueError('La documentación ha cambiado. Recarga la pantalla.')
        row=c.execute('SELECT revision FROM company_parameter_request WHERE company_id=? ORDER BY revision DESC LIMIT 1',(state['info']['company']['company_id'],)).fetchone()
        if (row[0] if row else 0) != state.get('sales_parameters',{}).get('revision',0):
            raise ValueError('Los parámetros comerciales han cambiado. Recarga la pantalla.')
        try:
            c.execute('INSERT INTO manual_sales_proposal VALUES(?,?,?,?,?)',
                (payload['proposal_id'],data['dataset_id'],reference,payload['created_at'],json.dumps(payload,ensure_ascii=False,allow_nan=False)))
        except sqlite3.IntegrityError as exc:
            raise ValueError('Ya existe una propuesta con esta referencia en la versión seleccionada.') from exc
    return payload


def printable_offer(db, dataset, proposal_id):
    payload = next((p for p in offers(db,dataset) if p['proposal_id'] == proposal_id), None)
    if payload is None:
        raise ValueError('Propuesta no encontrada en esta versión.')
    esc = lambda value: escape(str(value), quote=True)
    money = lambda value: esc(number_text(value,2))+' €'
    html = ['<!doctype html><html lang="es"><meta charset="utf-8"><title>Propuesta de venta</title>',
        '<style>body{font:15px Arial;color:#172b49;max-width:1000px;margin:35px auto;padding:15px}h1{color:#0a369d}table{width:100%;border-collapse:collapse}th,td{padding:9px;text-align:left;border-bottom:1px solid #ccd7e4}th{background:#edf4fc}p{line-height:1.5}@media print{button{display:none}body{margin:0}tr{break-inside:avoid}}</style>',
        '<button onclick="window.print()">Imprimir / Guardar PDF</button><h1>PROPUESTA DE VENTA · PRUEBA SINTÉTICA</h1>',
        '<p>'+esc(payload['company'].get('legal_name','Empresa'))+' · '+esc(payload['reference'])+'</p>',
        '<p>Cliente: '+esc(payload['customer'].get('legal_name',payload['customer']['customer_id']))+'</p>',
        '<p>Fecha: '+esc(date_text(payload['offer_date']))+' · Válida hasta: '+esc(date_text(payload['valid_until']))+'</p>',
        '<table><thead><tr>'+''.join('<th>'+s+'</th>' for s in ('Artículo / unidad','Cantidad','Precio','Dto. %','IVA %','Neto'))+'</tr></thead><tbody>']
    for line in payload['lines']:
        html.append('<tr>'+''.join('<td>'+v+'</td>' for v in (esc(line['article_id']+' · '+line['description']+' / '+line['unit']),esc(number_text(line['quantity'])),money(line['unit_price']),esc(number_text(line['discount_percent'])),esc(number_text(line['vat_percent'])),money(line['net_amount'])))+'</tr>')
    html.extend(['</tbody></table><p>Portes facturados al cliente (sin IVA): '+money(payload['freight_net'])+(' · IVA '+esc(number_text(payload['freight_vat_percent']))+' %' if payload['freight_vat_percent'] is not None else ' · Sin cargo de portes')+'</p>',
        '<p>Base imponible: '+money(payload['net_amount'])+' · IVA: '+money(payload['vat_amount'])+' · <strong>TOTAL: '+money(payload['total'])+'</strong></p>',
        '<p>Entrega prevista: '+esc(date_text(payload['delivery_date']))+' · '+esc(payload['delivery_location'])+'</p>',
        '<p>Cobro previsto: '+esc(date_text(payload['due_date']))+' · '+esc(payload['payment_terms'])+'</p>',
        '<p>Oferta sintética para pruebas. No acredita aceptación ni reserva de mercancía.</p></html>'])
    return ''.join(html)
