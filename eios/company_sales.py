"""Read-only, cutoff-scoped sales invoice browsing with original source links."""
from copy import deepcopy
from datetime import date
from decimal import Decimal, InvalidOperation


def _amount(value):
    try:
        number=Decimal(str(value))
        return str(number) if number.is_finite() else None
    except (InvalidOperation,ValueError,TypeError):
        return None


def documented_sales(store, dataset, cutoff):
    when=date.fromisoformat(cutoff)
    customers={r['data']['customer_id'] for r in store.records(dataset,'customer')}
    included={};excluded=[]
    for record in store.records(dataset,'sales_invoice'):
        data=record['data'];identity=record['record_id']
        try: issued=date.fromisoformat(data.get('issue_date_pdf') or data.get('issue_date'))
        except (ValueError,TypeError): issued=None
        reason=None
        if data.get('invoice_number')!=identity: reason='La referencia de factura no coincide con su identificador.'
        elif data.get('customer_id') not in customers: reason='Cliente no vinculado en esta versión documental.'
        elif data.get('economic_position')!='ISSUED_BY_CUTOFF': reason='No consta como factura emitida a la fecha de corte.'
        elif issued is None: reason='Falta una fecha de emisión documental válida.'
        elif issued>when: reason='Factura posterior a la fecha de corte.'
        if reason:
            excluded.append(dict(invoice_number=data.get('invoice_number'),customer_id=data.get('customer_id'),reason=reason))
            continue
        invoice=dict(record_id=identity,invoice_number=data['invoice_number'],customer_id=data['customer_id'],
                     issue_date=issued.isoformat(),currency=data.get('currency'),
                     source_refs=deepcopy(record.get('source_refs',[])),lines=[],warnings=[])
        for field in ('net_amount','vat_amount','gross_amount','collected_at_cutoff','pending'):
            invoice[field]=_amount(data.get(field))
        included[identity]=invoice
    ignored_lines=0
    for record in store.records(dataset,'sales_invoice_line'):
        data=record['data'];invoice=included.get(data.get('invoice_number'))
        if invoice is None:
            ignored_lines+=1;continue
        if data.get('customer_id') is not None and data['customer_id']!=invoice['customer_id']:
            ignored_lines+=1
            invoice['warnings'].append('Una línea declara otro cliente y no se ha incluido.')
            continue
        line=dict(record_id=record['record_id'],line=data.get('line'),article_id=data.get('article_id'),
                  description=data.get('description'),unit=data.get('unit_as_documented'),currency=data.get('currency'),
                  source_refs=deepcopy(record.get('source_refs',[])))
        for field in ('quantity','unit_price','net_amount'): line[field]=_amount(data.get(field))
        for field in ('unit_price_before_discount','discount_percent','discount_amount','vat_percent','vat_amount'):
            if field in data:line[field]=_amount(data[field])
        if line['currency'] and invoice['currency'] and line['currency']!=invoice['currency']:
            invoice['warnings'].append('Una línea tiene moneda distinta de la cabecera: '+record['record_id'])
        invoice['lines'].append(line)
    for invoice in included.values():
        invoice['lines'].sort(key=lambda row:(row['line'] if isinstance(row['line'],int) else 10**9,row['record_id']))
    invoices=sorted(included.values(),key=lambda row:(row['issue_date'],row['invoice_number']),reverse=True)
    return dict(invoices=invoices,excluded=excluded,ignored_lines=ignored_lines,as_of_date=cutoff)
