"""Read-only documentary purchase invoices; no orders, payments or stock inferred."""
from copy import deepcopy
from datetime import date
from eios.company_sales import _amount


def documented_purchases(store,dataset,cutoff):
    limit=date.fromisoformat(cutoff)
    suppliers={r['data']['supplier_id']:r['data'] for r in store.records(dataset,'supplier')}
    included={};excluded=[]
    for record in store.records(dataset,'purchase_invoice'):
        data=record['data'];key=record['record_id'];reason=None
        try:issued=date.fromisoformat(data['issue_date'])
        except (KeyError,TypeError,ValueError):issued=None
        if not issued:reason='Fecha documental no válida.'
        elif issued>limit:reason='Factura posterior al corte.'
        elif data.get('supplier_id') not in suppliers:reason='Proveedor no vinculado en esta versión.'
        elif data.get('invoice_id')!=key:reason='Identificador de factura inconsistente.'
        if reason:
            excluded.append(dict(record_id=key,reason=reason));continue
        invoice=dict(record_id=key,invoice_number=data.get('invoice_number') or key,
            supplier_id=data['supplier_id'],supplier_name=suppliers[data['supplier_id']].get('legal_name') or data['supplier_id'],
            issue_date=issued.isoformat(),currency=data.get('currency'),documented_status=data.get('status'),
            source_refs=deepcopy(record.get('source_refs',[])),lines=[],warnings=[])
        for field in ('net_amount','vat_amount','gross_amount'):invoice[field]=_amount(data.get(field))
        included[key]=invoice
    ignored=0
    for record in store.records(dataset,'purchase_invoice_line'):
        data=record['data'];invoice=included.get(data.get('invoice_id'))
        if not invoice:ignored+=1;continue
        if data.get('supplier_id')!=invoice['supplier_id']:
            ignored+=1;invoice['warnings'].append('Una línea declara otro proveedor y no se muestra.');continue
        line=dict(record_id=record['record_id'],line=data.get('line'),article_id=data.get('article_id'),
            description=data.get('description'),unit=data.get('unit_as_documented'),currency=data.get('currency'),
            source_refs=deepcopy(record.get('source_refs',[])))
        for field in ('quantity','unit_price','net_amount'):line[field]=_amount(data.get(field))
        if line['currency']!=invoice['currency']:invoice['warnings'].append('Moneda de línea distinta o sin documentar: '+record['record_id'])
        invoice['lines'].append(line)
    for invoice in included.values():invoice['lines'].sort(key=lambda line:(line['line'] if isinstance(line['line'],int) else 10**9,line['record_id']))
    return dict(invoices=sorted(included.values(),key=lambda x:(x['issue_date'],x['record_id']),reverse=True),
                excluded=excluded,ignored_lines=ignored,as_of_date=cutoff)
