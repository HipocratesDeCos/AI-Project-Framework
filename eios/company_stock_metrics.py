"""Source-bound stock display context, without inferring turnover or suppliers."""
from datetime import date


def stock_metrics(store,dataset,cutoff):
    limit=date.fromisoformat(cutoff)
    suppliers={r['data']['supplier_id']:r['data'].get('legal_name') or r['data']['supplier_id'] for r in store.records(dataset,'supplier')}
    articles={r['data']['article_id']:r['data'] for r in store.records(dataset,'article')}
    result={key:dict(suppliers={},rotation=dict(status='MISSING_DATA',value=None,
        message='Se necesitan salidas/ventas vinculadas al SKU y stock medio de un mismo período. No se calcula con el stock actual ni con la demanda supuesta.')) for key in articles}
    for key,a in articles.items():
        supplier=a.get('supplier_id')
        if supplier:
            result[key]['suppliers'][supplier]=dict(supplier_id=supplier,name=suppliers.get(supplier,supplier),basis=['Catálogo'],source_refs=[])
    invoices={r['record_id']:r['data'] for r in store.records(dataset,'purchase_invoice')}
    for record in store.records(dataset,'purchase_invoice_line'):
        line=record['data'];key=line.get('article_id');header=invoices.get(line.get('invoice_id'))
        if key not in articles or not header:continue
        try:issued=date.fromisoformat(header['issue_date'])
        except (KeyError,TypeError,ValueError):continue
        supplier=line.get('supplier_id')
        if issued>limit or not supplier or supplier!=header.get('supplier_id') or line.get('unit_as_documented')!=articles[key].get('unit_as_documented'):continue
        item=result[key]['suppliers'].setdefault(supplier,dict(supplier_id=supplier,name=suppliers.get(supplier,supplier),basis=[],source_refs=[]))
        if 'Compra documentada' not in item['basis']:item['basis'].append('Compra documentada')
        item['source_refs'].extend(record.get('source_refs',[]))
    for item in result.values():item['suppliers']=list(item['suppliers'].values())
    return result
