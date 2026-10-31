"""Describe consulted references and scoped receipts without admitting any data."""
from collections import Counter
import json
from pathlib import Path
import sqlite3

from eios.company_presentation import number_text


def describe_status(db,state):
    info=state['info'];context=state['documentary_context'];counts=info.get('record_counts',{})
    receipts=Counter();unclassified=0
    identity=(info['company']['company_id'],info['company'].get('legal_name'),context['material_nature'],info['as_of_date'])
    with sqlite3.connect(Path(db).resolve().as_uri()+'?mode=ro',uri=True) as c:
        if c.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='received_company_batch'").fetchone():
            for bid,raw in c.execute('SELECT batch_id,metadata_json FROM received_company_batch WHERE company_id=?',(identity[0],)):
                try:
                    meta=json.loads(raw)
                    if not isinstance(meta,dict):raise ValueError()
                    from eios.company_exclusive_workbook import allowed
                    if info.get('exclusive_workbook') and not allowed(c,info['dataset_id'],meta,bid):continue
                    if tuple(meta.get(k) for k in ('company_id','legal_name','material_nature','as_of_date'))==identity:
                        receipts[meta['kind']]+=1
                except (ValueError,TypeError,KeyError):unclassified+=1
    blocks=[]
    def add(key,title,status,metrics,description,destination,receipt_kinds,files=None):
        blocks.append(dict(key=key,title=title,status=status,metrics=[dict(label=k,value=v) for k,v in metrics],description=description,destination=destination,received_file_count=sum(receipts[k] for k in receipt_kinds),source_files=sorted(set(files or []))))
    def mode(selection,baseline,kinds):
        if selection:return selection['status']
        return 'BASELINE' if baseline else 'RECEIVED_ONLY' if any(receipts[k] for k in kinds) else 'MISSING'
    articles=state.get('articles',[]);catalogue=state.get('commercial_catalogue');tariffs=[a['received_sale_tariff'] for a in articles if a.get('received_sale_tariff')]
    add('catalogue','CATÁLOGO Y PRECIOS','STALE' if any(t.get('status')=='STALE' for t in tariffs) else 'SELECTED' if catalogue or any(t.get('status')=='ACTIVE' for t in tariffs) else 'BASELINE' if articles else 'RECEIVED_ONLY' if receipts['article'] else 'MISSING',
        [('Artículos consultables',len(articles)),('Tarifas recibidas vinculadas',len(tariffs))],
        ('Catálogo adicional: '+catalogue['filename']+'. ' if catalogue else 'Catálogo de la versión documental. ')+(number_text(sum(t.get('status')=='STALE' for t in tariffs))+' tarifas con origen pendiente de revisión. ' if any(t.get('status')=='STALE' for t in tariffs) else '')+'La vigencia y el precio se comprueban para cada propuesta. Recibir una ficha de artículo no la incorpora por sí solo al catálogo.',
        'propuestas-ventas',['article','sale_price'],([catalogue['filename']] if catalogue else [])+[(t.get('selection') or {})['filename'] for t in tariffs if t.get('status')=='ACTIVE' and (t.get('selection') or {}).get('filename')])
    inventory=state.get('inventory',{});matching=[inventory[a['article_id']] for a in articles if a.get('unit_as_documented') and a['article_id'] in inventory and inventory[a['article_id']].get('unit')==a.get('unit_as_documented') and inventory[a['article_id']].get('physical') is not None]
    sel=state.get('selected_inventory')
    add('inventory','EXISTENCIAS',mode(sel,matching,['inventory','stock_policy']),[('Artículos con físico comparable',len(matching)),('Con disponible calculable',sum(v.get('available') is not None for v in matching))],
        (sel['message'] if sel else 'Se consultan las referencias originales del corte.')+' '+number_text(len(articles)-len(matching))+' artículos del catálogo sin físico comparable. Sin reservas declaradas no se presume disponible. No acredita stock actual.',
        'stock',['inventory','stock_policy'],[v['source_ref']['filename'] for v in matching if v.get('source_ref',{}).get('filename')])
    for key,title,selection_key,received_key,invoice_key,destination,kinds in [
        ('purchases','COMPRAS HISTÓRICAS','selected_purchase_history','received_purchase_lines','purchase_documents','compras',['purchase_line']),
        ('sales','VENTAS HISTÓRICAS','selected_sales_history','received_sales_lines','sales','ventas',['sales_line'])]:
        invoices=state.get(invoice_key,{}).get('invoices',[]);lines=state.get(received_key,[]);selection=state.get(selection_key)
        description=selection['message'] if selection else 'Se consultan las facturas originales de esta versión. Los archivos recibidos necesitan selección expresa para utilizarlos como referencia comercial.'
        description+= ' Las comparaciones exigen cliente o proveedor, SKU, unidad y moneda compatibles; no se crean facturas, movimientos de stock ni cobros/pagos.'
        add(key,title,mode(selection,invoices,kinds),[('Facturas originales consultables',len(invoices)),('Líneas recibidas seleccionadas',len(lines))],description,destination,kinds,[ref['filename'] for line in lines for ref in line.get('source_refs',[]) if ref.get('filename')])
    add('parties','CLIENTES Y PROVEEDORES','BASELINE' if state.get('customers') or state.get('suppliers') else 'RECEIVED_ONLY' if receipts['customer'] or receipts['supplier'] else 'MISSING',
        [('Clientes en fichas consultadas',len(state.get('customers',[]))),('Proveedores en fichas consultadas',len(state.get('suppliers',[])))],
        'Las fichas recibidas no sustituyen automáticamente las de la versión documental. El catálogo adicional puede aportar nombres y códigos de proveedor declarados, sin validación fiscal.', 'clientes',['customer','supplier'])
    financial=sum(counts.get(k,0) for k in ('financial_snapshot','working_capital','account_balance','cash_flow','treasury_balances','bank_statement_entry','cash_count','daily_treasury_forecast'))
    add('finance','BALANCE Y TESORERÍA','BASELINE' if financial else 'RECEIVED_ONLY' if any(receipts[k] for k in ('balance','cash_flow','sales_installment')) else 'MISSING',
        [('Registros originales de saldo contable',counts.get('account_balance',0)),('Registros originales de cobro/pago',counts.get('cash_flow',0))],
        'Recuento de registros documentales, no de importes validados. Recibir saldos, previsiones o cuotas no los incorpora automáticamente al análisis financiero. La conciliación, evidencia, horizonte y evaluación se revisan en cada propuesta.', 'propuestas',['balance','cash_flow','sales_installment'])
    exclusive=info.get('exclusive_workbook')
    if exclusive:
        for block in blocks:
            block['description']='Fuente exclusiva: '+exclusive['filename']+'. Se consultan solo los registros de esta versión del Excel; lo ausente no se completa con datos anteriores. '+('Las cifras siguen siendo referencias al corte, sin acreditación de conciliación o disponibilidad actual.' if block['key']=='finance' else '')
            block['source_files']=[exclusive['filename']]
    return dict(exclusive_workbook=exclusive,dataset_id=info['dataset_id'],company_id=identity[0],legal_name=identity[1],material_nature=identity[2],as_of_date=identity[3],context_fingerprint=context['fingerprint'],ordinary_received_file_count=sum(receipts.values()),unclassified_company_file_count=unclassified,blocks=blocks,scope='DISPLAYED_REFERENCES_AND_RECEIPTS_ONLY',decision_authority=False,operational_path='FORBIDDEN')
