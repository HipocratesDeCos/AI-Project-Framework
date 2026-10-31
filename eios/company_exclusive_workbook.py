"""Source-exclusive synthetic snapshots from one received guided workbook.

A new immutable dataset is built from the selected bytes only. No older records,
manual references, stock assumptions or saved proposals are copied into it.
"""
from collections import Counter,defaultdict
from contextlib import closing
from copy import deepcopy
from datetime import datetime,timezone
from decimal import Decimal
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
import tempfile
import zipfile

from eios.company_data import CompanyDataStore,SCHEMA
from eios.company_proposal_context import _hash
from eios.company_selected_inventory import source

ACTIVE_TABLE='''CREATE TABLE IF NOT EXISTS company_active_workbook (
company_id TEXT PRIMARY KEY,dataset_id TEXT NOT NULL,activated_at TEXT NOT NULL)'''


def binding(c,dataset):
    row=c.execute('SELECT manifest_json FROM documentary_company_snapshot WHERE dataset_id=?',(dataset,)).fetchone()
    return json.loads(row[0]).get('exclusive_workbook') if row else None


def allowed(c,dataset,meta,batch_id=None):
    selected=binding(c,dataset)
    return not selected or ((batch_id is None or batch_id in selected.get('batch_ids',[])) and meta.get('source_sha256')==selected['source_sha256'] and meta.get('company_id')==selected['company_id'] and meta.get('as_of_date')==selected['as_of_date'])


def options(db,dataset):
    from eios.company_sales_treasury import scope,identity_status
    with closing(sqlite3.connect(db)) as c:
        target=scope(c,dataset);groups={}
        if c.execute("SELECT 1 FROM sqlite_master WHERE name='received_company_batch'").fetchone():
            for bid,at,ordinal,raw in c.execute('SELECT batch_id,received_at,rowid,metadata_json FROM received_company_batch'):
                try:meta=json.loads(raw)
                except (ValueError,TypeError):continue
                if not isinstance(meta,dict) or not str(meta.get('filename','')).lower().endswith('.xlsx'):continue
                cut=meta.get('as_of_date')
                if not cut or identity_status(meta,(*target[:3],cut))=='INCOMPATIBLE':continue
                key=(meta['company_id'],cut,meta.get('source_sha256'))
                if key not in groups or (at,ordinal)>groups[key]['rank']:
                    groups[key]=dict(batch_id=bid,filename=meta['filename'],as_of_date=cut,company_id=meta['company_id'],legal_name=meta['legal_name'],source_sha256=meta['source_sha256'],rank=(at,ordinal))
        rows=sorted(groups.values(),key=lambda x:(x['as_of_date'],x['rank']),reverse=True)
        for r in rows:r.pop('rank')
        return dict(files=rows,current=binding(c,dataset),dataset_id=dataset)


def _material(staged,meta):
    """Map validated table facts; unknown values remain unknown."""
    cut=meta['as_of_date'];company=meta['company_id'];records={};inventories=[];bykind=defaultdict(list)
    def add(kind,rid,data,refs):
        item=dict(kind=kind,record_id=str(rid),data=data,source_refs=refs);key=(kind,str(rid))
        old=records.get(key)
        if old and old['data']!=data:raise ValueError('Referencias contradictorias en el libro: '+kind+' / '+str(rid))
        if old:old['source_refs'].extend(ref for ref in refs if ref not in old['source_refs'])
        else:records[key]=item
    for bid,report,rows in staged:
        for row in rows:
            d=deepcopy(row['data']);ref=dict(document_ref='WORKBOOK',filename=meta['filename'],sheet=report['sheet'],row=row['source_row'],batch_id=bid,source_sha256=meta['source_sha256'])
            bykind[row['kind']].append((d,[ref]))
            add('source_sheet_row',report['sheet']+':'+str(row['source_row']),dict(table_kind=row['kind'],values=d),[ref])
    bookref=[dict(document_ref='WORKBOOK',filename=meta['filename'])]
    add('company_identity',company,dict(company_id=company,legal_name=meta['legal_name']),bookref)
    for kind,key in [('supplier','supplier_id'),('customer','customer_id')]:
        for d,refs in bykind[kind]:add(kind,d[key],d,refs)
    supplier_ids={d['supplier_id'] for d,_ in bykind['supplier']};customer_ids={d['customer_id'] for d,_ in bykind['customer']}
    for d,refs in bykind['article']:
        if d.get('supplier_id') and d['supplier_id'] not in supplier_ids:raise ValueError('Proveedor del SKU no incluido en este libro: '+d['article_id'])
        item=dict(d,unit_as_documented=d['unit'],stock_quantity=None,demand_forecast=None)
        if not item.get('supplier_id'):item.pop('supplier_id',None)
        add('article',d['article_id'],item,refs)
    for d,refs in bykind['inventory']:
        if ('article',d['article_id']) not in records:raise ValueError('Inventario sin ficha en el libro: '+d['article_id'])
        reserved=d.get('reserved');physical=Decimal(d['physical'])
        inventories.append(dict(article_id=d['article_id'],unit=d['unit'],as_of_date=cut,physical=str(physical),reserved=reserved,available=str(physical-Decimal(reserved)) if reserved is not None else None,source='EXCLUSIVE_RECEIVED_WORKBOOK',source_ref=refs[0],material_nature='SYNTHETIC',basis='RECEIVED_WORKBOOK_REFERENCE_NOT_CURRENT_STOCK',accounting_reconciliation='NOT_RECONCILED',demand_forecast=None,safety_stock=d.get('safety_stock'),minimum_stock=d.get('minimum_stock'),reorder_point=d.get('reorder_point'),lead_time_days=d.get('lead_time_days'),operational_path='FORBIDDEN',decision_authority=False))
    # Price references without validity remain labelled references, not active tariffs.
    for d,refs in bykind['price_reference']:
        article=records.get(('article',d['article_id']))
        if not article or d.get('unit')!=article['data']['unit_as_documented']:continue
        if d.get('currency')!='EUR':continue
        a=article['data'];a.update(catalogue_unit_cost=d['reference_cost'],recommended_sale_price=d['reference_price'],sale_currency='EUR',commercial_catalogue=dict(filename=meta['filename'],sheet=refs[0]['sheet'],source_row=refs[0]['row'],source_sha256=meta['source_sha256'],scope='WORKBOOK_PRICE_REFERENCE_WITHOUT_DOCUMENTED_VALIDITY',decision_authority=False))
    for kind,party,invoicekind,linekind in [('purchase_line','supplier_id','purchase_invoice','purchase_invoice_line'),('sales_line','customer_id','sales_invoice','sales_invoice_line')]:
        groups=defaultdict(list)
        for d,refs in bykind[kind]:groups[(d[party],d['invoice_number'])].append((d,refs))
        for (owner,invoice),lines in groups.items():
            if owner not in (supplier_ids if party=='supplier_id' else customer_ids):raise ValueError('Contraparte ausente en el libro: '+owner)
            if len({(d['issue_date'],d['currency']) for d,_ in lines})!=1:raise ValueError('Fecha o moneda contradictoria en '+invoice)
            rid=owner+'|'+invoice if kind=='purchase_line' else invoice
            header=dict(invoice_number=invoice,issue_date=lines[0][0]['issue_date'],currency=lines[0][0]['currency'],**{party:owner})
            if kind=='purchase_line':header['invoice_id']=rid
            else:header['economic_position']='ISSUED_BY_CUTOFF'
            header['net_amount']=str(sum(Decimal(d['net_amount']) for d,_ in lines))
            vats=[d.get('vat_amount') for d,_ in lines]
            if all(v is not None for v in vats):header['vat_amount']=str(sum(Decimal(v) for v in vats))
            totals={d['invoice_total'] for d,_ in lines if d.get('invoice_total') is not None}
            if len(totals)>1:raise ValueError('Total de factura contradictorio: '+invoice)
            if totals:header['gross_amount']=next(iter(totals))
            add(invoicekind,rid,header,[ref for _,refs in lines for ref in refs])
            for ordinal,(d,refs) in enumerate(lines,1):
                if ('article',d['article_id']) not in records:raise ValueError('Línea sin SKU del libro: '+d['article_id'])
                item=dict(d,unit_as_documented=d['unit'],line=ordinal,unit_price=str(Decimal(d['net_amount'])/Decimal(d['quantity'])))
                if kind=='purchase_line':item['invoice_id']=rid
                add(linekind,rid+'#'+str(ordinal),item,refs)
    for d,refs in bykind['sales_installment']:
        if d['customer_id'] not in customer_ids:raise ValueError('Cuota sin cliente de este libro: '+d['installment_ref'])
        if ('sales_invoice',d['invoice_number']) not in records:
            add('missing_or_conflicting','QUOTA:'+d['installment_ref'],dict(code='RECEIVED_QUOTA_WITHOUT_MATCHING_INVOICE',customer_id=d['customer_id'],installment_ref=d['installment_ref'],invoice_number=d['invoice_number'],message='Cuota conservada en su hoja de origen, sin factura coincidente dentro del Excel activo. No se crea una factura ni se busca en otro expediente.'),refs)
            continue
        invoice=records[('sales_invoice',d['invoice_number'])]['data']
        if invoice['customer_id']!=d['customer_id']:raise ValueError('Cliente de cuota distinto de factura: '+d['installment_ref'])
        item=dict(d,pending=d.get('pending_amount'),original_due_date=d['due_date'],revised_due_date=None)
        add('sales_installment',d['installment_ref'],item,refs)
    for d,refs in bykind['balance']:add('account_balance',d['account_code'],d,refs)
    from eios.finance.models import CashFlow,FinancialSnapshot
    for d,refs in bykind['cash_flow']:
        model=CashFlow(flow_id=d['flow_id'],flow_type={'COBRO':'COLLECTION','PAGO':'PAYMENT'}[d['direction']],amount=d['amount'],currency=d['currency'],due_date=d['due_date'],due_date_evidenced=False,source_ref='WORKBOOK:'+refs[0]['sheet']+':'+str(refs[0]['row']),evidence_state='NOT_EVIDENCED')
        add('cash_flow',d['flow_id'],dict(canonical=model.model_dump(mode='json')) ,refs)
    # No opening balance is inferred without an unambiguous bank-account selection.
    balances=[d for d,_ in bykind['balance'] if d['account_code'].startswith('572')]
    bank=None
    if balances and all(d['currency']=='EUR' and Decimal(d['balance'])>=0 for d in balances):
        codes=[d['account_code'] for d in balances]
        if len(codes)==len(set(codes)) and not any(a!=b and b.startswith(a) for a in codes for b in codes):bank=str(sum(Decimal(d['balance']) for d in balances))
    snap=FinancialSnapshot(company_scope=company,as_of_date=cut,data_snapshot_id=meta['source_sha256'],currency='EUR',available_treasury=bank,treasury_evidence_ref='WORKBOOK:bank-accounts' if bank is not None else None)
    add('financial_snapshot','WORKBOOK-FINANCE',snap.model_dump(mode='json'),bookref)
    return list(records.values()),inventories


def activate(db,dataset,batch_id):
    eligible=options(db,dataset)
    previous_info=CompanyDataStore(db).describe(dataset)
    related_companies=set((previous_info.get('exclusive_workbook') or {}).get('linked_company_ids',[]))|{previous_info['company']['company_id']}
    if batch_id not in {r['batch_id'] for r in eligible['files']}:raise ValueError('Selecciona un Excel recibido de esta empresa.')
    with closing(sqlite3.connect(db)) as c:
        meta,_,fp,intact=source(c,batch_id)
        if not intact:raise ValueError('La integridad del libro no coincide. Recíbelo de nuevo.')
        content=bytes(c.execute('SELECT content FROM received_company_batch WHERE batch_id=?',(batch_id,)).fetchone()[0])
    if meta['material_nature']!='SYNTHETIC':raise ValueError('Esta activación admite solo datos ficticios.')
    # Re-read every guided sheet from exactly these bytes, including sheets whose
    # reception had been deduplicated against an older version of the workbook.
    from eios.company_workbook_reception import CompanyWorkbookReception
    with tempfile.TemporaryDirectory(prefix='eios-exclusive-') as folder:
        tempdb=Path(folder)/'check.sqlite3';sqlite3.connect(tempdb).close()
        reader=CompanyWorkbookReception(tempdb)
        preview=reader.preview(content,meta['filename'],{k:meta[k] for k in ('company_id','legal_name','material_nature','as_of_date','number_format')})
        if not preview.get('ticket'):raise ValueError('El libro no puede activarse: revisa sus hojas y relaciones. '+json.dumps(preview.get('reference_issues',preview.get('sheets',[])),ensure_ascii=False)[:1200])
        staged=reader.checked['staged'];records,inventory=_material(staged,meta)
        doc=dict(document_ref='WORKBOOK',path='documents/workbook.xlsx',filename=meta['filename'],bytes=len(content),sha256=sha256(content).hexdigest())
        raw=json.dumps(records,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
        manifest=dict(schema_version=SCHEMA,company=dict(company_id=meta['company_id'],legal_name=meta['legal_name']),as_of_date=meta['as_of_date'],material_nature='SYNTHETIC',operational_path='FORBIDDEN',decision_authority=False,records=dict(path='records.json',sha256=sha256(raw).hexdigest()),record_counts=dict(Counter(r['kind'] for r in records)),documents=[doc],exclusive_workbook=dict({k:meta[k] for k in ('company_id','as_of_date','source_sha256','filename')},batch_ids=sorted(bid for bid,_,_ in staged),linked_company_ids=sorted(related_companies|{meta['company_id']})))
        package=Path(folder)/'isolated.zip'
        with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED) as z:
            z.writestr('company_manifest.json',json.dumps(manifest,ensure_ascii=False));z.writestr('records.json',raw);z.writestr(doc['path'],content)
        # Validate everything before any change to the live database.
        from eios.company_data import read_dataset
        _,_,_,new_id=read_dataset(package)
        with closing(sqlite3.connect(db)) as c,c:
            c.execute('BEGIN IMMEDIATE')
            _,_,current,intact=source(c,batch_id)
            if current!=fp or not intact:raise ValueError('El libro cambió durante la activación.')
            c.execute(ACTIVE_TABLE)
            # Same transactional import schema as CompanyDataStore, without nested connections.
            exists=c.execute('SELECT 1 FROM documentary_company_snapshot WHERE dataset_id=?',(new_id,)).fetchone()
            if not exists:
                c.execute('INSERT INTO documentary_company_snapshot VALUES(?,?,?,?)',(new_id,meta['company_id'],meta['as_of_date'],json.dumps(manifest,ensure_ascii=False)))
                c.execute('INSERT INTO documentary_source VALUES(?,?,?,?)',(new_id,'WORKBOOK',json.dumps(doc),content))
                c.executemany('INSERT INTO documentary_company_record VALUES(?,?,?,?)',[(new_id,r['kind'],r['record_id'],json.dumps(r,ensure_ascii=False)) for r in records])
                from eios.company_inventory import TABLE
                c.execute(TABLE)
                c.executemany('INSERT INTO synthetic_planning_inventory VALUES(?,?,?)',[(new_id,r['article_id'],json.dumps(dict(r,dataset_id=new_id))) for r in inventory])
            for bid,report,rows in staged:
                c.execute('INSERT OR IGNORE INTO received_company_batch VALUES(?,?,?,?,?,?)',(bid,meta['company_id'],datetime.now(timezone.utc).isoformat(),json.dumps(report,ensure_ascii=False),content,json.dumps(rows,ensure_ascii=False)))
            c.execute('INSERT OR REPLACE INTO company_active_workbook VALUES(?,?,?)',(meta['company_id'],new_id,datetime.now(timezone.utc).isoformat()))
    return dict(status='ACTIVATED_EXCLUSIVELY',dataset_id=new_id,filename=meta['filename'],as_of_date=meta['as_of_date'],record_counts=manifest['record_counts'],decision_authority=False,operational_path='FORBIDDEN')


def dataset_options(db,rows):
    with closing(sqlite3.connect(db)) as c:
        active=set()
        if c.execute("SELECT 1 FROM sqlite_master WHERE name='company_active_workbook'").fetchone():active={r[0] for r in c.execute('SELECT dataset_id FROM company_active_workbook')}
        manifests={did:json.loads(raw) for did,raw in c.execute('SELECT dataset_id,manifest_json FROM documentary_company_snapshot')}
        active_companies={r[1] for r in rows if r[0] in active}
        for did in active:
            active_companies.update((manifests.get(did,{}).get('exclusive_workbook') or {}).get('linked_company_ids',[]))
        result=[]
        for did,company,cut in rows:
            manifest=manifests[did];selected=manifest.get('exclusive_workbook')
            archived=company in active_companies
            result.append(dict(dataset_id=did,company_id=company,as_of_date=cut,active_workbook=did in active,historical=archived and did not in active,filename=selected['filename'] if selected else None))
    return sorted(result,key=lambda r:(r['active_workbook'],r['as_of_date']),reverse=True)


def require_active(db,dataset):
    with closing(sqlite3.connect(db)) as c:
        if not c.execute("SELECT 1 FROM sqlite_master WHERE name='company_active_workbook'").fetchone():return
        rows=c.execute('SELECT dataset_id,company_id,as_of_date FROM documentary_company_snapshot').fetchall()
    if any(r['dataset_id']==dataset and r['historical'] for r in dataset_options(db,rows)):
        raise ValueError('Esta versión es histórica. Selecciona el expediente ACTIVO para preparar una propuesta nueva.')
