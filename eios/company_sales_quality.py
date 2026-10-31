"""Source-bound technical checks and recorded human review for synthetic sales.

Matching references and a review declaration never upgrade core financial evidence.
"""
from collections import defaultdict
from contextlib import closing
from datetime import datetime, timezone
from decimal import Decimal
import json
import sqlite3

from eios.company_proposal_context import _hash
from eios.company_sales_treasury import scope,identity_status
from eios.company_selected_inventory import source

TABLE='''CREATE TABLE IF NOT EXISTS company_sales_quality_review (
dataset_id TEXT NOT NULL,revision INTEGER NOT NULL,payload TEXT NOT NULL,fingerprint TEXT NOT NULL,
PRIMARY KEY(dataset_id,revision))'''
KINDS={'sales_line','sales_installment','purchase_line','document'}
TOLERANCE=Decimal('.01')


def latest(c,dataset):
    if not c.execute("SELECT 1 FROM sqlite_master WHERE name='company_sales_quality_review'").fetchone():return None
    row=c.execute('SELECT payload,fingerprint FROM company_sales_quality_review WHERE dataset_id=? ORDER BY revision DESC LIMIT 1',(dataset,)).fetchone()
    if not row:return None
    result=json.loads(row[0])
    if _hash(result)!=row[1]:raise ValueError('La revisión de calidad no coincide con su huella.')
    return result


def support_inventory(c,dataset):
    from eios.company_sales_treasury_policy import effective
    target=scope(c,dataset);selected=effective(c,dataset);cutoff=(selected or {}).get('as_of_date',target[3]);groups={};invalid=[]
    if c.execute("SELECT 1 FROM sqlite_master WHERE name='received_company_batch'").fetchone():
        for bid,received,order,raw in c.execute('SELECT batch_id,received_at,rowid,metadata_json FROM received_company_batch'):
            try:meta=json.loads(raw)
            except (ValueError,TypeError):continue
            from eios.company_exclusive_workbook import allowed
            if not isinstance(meta,dict) or not allowed(c,dataset,meta,bid):continue
            if meta.get('kind') not in KINDS or identity_status(meta,(*target[:3],cutoff))=='INCOMPATIBLE':continue
            # One version per sheet; distinct files of standalone supports remain distinct.
            key=(meta['kind'],meta.get('sheet') or meta['filename'])
            rank=(received,order)
            if key not in groups or rank>groups[key][0]:groups[key]=(rank,bid,meta)
    entries=[];fingerprints={};total=0
    for _,bid,meta in groups.values():
        try:
            _,records,fp,intact=source(c,bid);fingerprints[bid]=fp
            if not intact:invalid.append(meta['filename']);continue
        except (ValueError,TypeError):invalid.append(meta['filename']);fingerprints[bid]=None;continue
        total+=len(records)
        if total>20000:raise ValueError('La revisión admite hasta 20.000 filas de soporte; acota el expediente.')
        if meta['kind']=='document':records=[dict(source_row=0,data=dict(document_ref=bid))]
        for r in records:
            locator=dict(batch_id=bid,company_id=meta['company_id'],filename=meta['filename'],sheet=meta.get('sheet'),row=r['source_row'],source_sha256=meta.get('source_sha256'))
            entries.append(dict(source_id=_hash(locator),kind=meta['kind'],source=locator,data=r['data']))
    # Canonical financial supports are eligible only for the same declared cutoff.
    if cutoff==target[3]:
        for kind,rid,raw in c.execute("SELECT kind,record_id,record_json FROM documentary_company_record WHERE dataset_id=? AND kind IN ('purchase_installment','sales_installment','bank_statement_entry','cash_count','treasury_balances')",(dataset,)):
            record=json.loads(raw);locator=dict(record_id=rid,filename='Documento canónico '+rid,sheet=kind,row=None)
            entries.append(dict(source_id=_hash(dict(kind=kind,record_id=rid)),kind=kind,source=locator,data=record['data']))
            fingerprints['canonical:'+kind+':'+rid]=_hash(record)
    return dict(as_of_date=cutoff,entries=entries,source_fingerprints=fingerprints,invalid_sources=invalid)


def context(c,dataset):
    inventory=support_inventory(c,dataset);review=latest(c,dataset)
    if not inventory['source_fingerprints'] and not review:return None
    return dict(support_fingerprints=inventory['source_fingerprints'],review_fingerprint=_hash(review) if review else None)


def _number(value):
    try:
        result=Decimal(str(value))
        return result if result.is_finite() else None
    except (ValueError,TypeError,ArithmeticError):return None


def _report(c,dataset,finance):
    inventory=support_inventory(c,dataset);entries=inventory['entries'];index={e['source_id']:e for e in entries}
    basis=_hash(dict(finance=finance,supports=inventory['source_fingerprints'],invalid=inventory['invalid_sources']))
    saved=latest(c,dataset);current=saved if saved and saved['basis_fingerprint']==basis else None
    manual={x['flow_id']:x for x in current.get('movement_links',[])} if current else {}
    selected=finance.get('treasury_selection') or {};flow_batch=selected.get('flow_batch');raw_flows={};origins={}
    if flow_batch:
        try:
            meta,records,_,intact=source(c,flow_batch)
            if intact:
                for r in records:
                    if r['kind']=='cash_flow':
                        fid=r['data']['flow_id'];raw_flows[fid]=r['data'];origins[fid]=dict(batch_id=flow_batch,company_id=meta['company_id'],filename=meta['filename'],sheet=meta.get('sheet'),row=r['source_row'],data=r['data'])
        except (ValueError,TypeError):pass
    quota_refs=defaultdict(list);quota_flows=defaultdict(list)
    for entry in entries:
        if entry['kind'] in ('sales_installment','purchase_installment'):
            q=entry['data'];ref=q.get('installment_ref') or entry['source'].get('record_id')
            if ref:quota_refs[(entry['kind'],ref)].append(entry)
            if q.get('flow_id'):quota_flows[(entry['kind'],q['flow_id'])].append(entry)
    counts=defaultdict(int);rows=[];seen=set();used_support={}
    for flow in finance.get('cash_flows',[]):
        f=flow['canonical'];fid=f['flow_id'];d=raw_flows.get(fid,{})
        direction='COBRO' if f['flow_type']=='COLLECTION' else 'PAGO';issues=[];matches=[]
        if fid in seen:issues.append('Referencia de movimiento repetida.')
        seen.add(fid)
        if _number(f.get('amount')) is None or not f.get('due_date') or not f.get('currency'):issues.append('Falta importe, moneda o vencimiento utilizable.')
        ref=d.get('installment_ref');invoice=d.get('invoice_number');party=d.get('customer_id') if direction=='COBRO' else d.get('supplier_id')
        wanted='sales_installment' if direction=='COBRO' else 'purchase_installment'
        candidates={e['source_id']:e for e in quota_refs.get((wanted,ref),[])+quota_flows.get((wanted,fid),[])}
        for e in candidates.values():
            q=e['data']
            if invoice and q.get('invoice_number')!=invoice:continue
            if party and q.get('customer_id' if direction=='COBRO' else 'supplier_id')!=party:continue
            matches.append(e)
        # Same reference in two exports is one support only when all comparable facts agree.
        variants={_hash(dict(party=e['data'].get('customer_id') or e['data'].get('supplier_id'),invoice=e['data'].get('invoice_number'),currency=e['data'].get('currency'),due=e['data'].get('due_date') or e['data'].get('revised_due_date') or e['data'].get('original_due_date'),amount=str(_number(e['data'].get('pending_amount',e['data'].get('pending'))).normalize()) if _number(e['data'].get('pending_amount',e['data'].get('pending'))) is not None else None)) for e in matches}
        status='PENDING';message='No hay una cuota vinculada inequívoca. Relaciona el soporte o revisa las referencias; no se presupone que el movimiento esté mal.'
        if len(variants)>1:issues.append('Los soportes de la misma referencia tienen importes, fechas o identidades diferentes.')
        elif matches:
            q=matches[0]['data'];pending=q.get('pending_amount',q.get('pending'))
            # A purchase quota amount is original, not necessarily outstanding; never infer pending.
            due=q.get('due_date') or q.get('revised_due_date') or q.get('original_due_date');amount=_number(pending)
            if amount is None or not q.get('currency'):message='Cuota localizada, pero falta el pendiente al corte o su moneda; no se presupone el importe original ni la moneda.'
            elif q.get('currency')!=f['currency'] or due!=f['due_date'] or abs(amount-(_number(f['amount']) or Decimal(0)))>TOLERANCE:
                issues.append('El movimiento y la cuota no coinciden en importe pendiente, moneda o vencimiento.')
            else:
                key=(wanted,ref or matches[0]['source_id'])
                if key in used_support:issues.append('Una misma cuota se ha asociado a dos movimientos.')
                else:used_support[key]=fid;status='MATCHED';message='Referencia, importe pendiente, moneda y vencimiento coinciden. Coherencia entre registros; no acredita cobro o pago.'
        if not issues and status!='MATCHED' and fid in manual:
            status='DECLARED_REVIEWED';message='Soporte vinculado y revisado por '+current['actor']+'. Declaración humana conservada; no verificada automáticamente.'
        if issues:status='DISCREPANCY';message=' '.join(issues)
        counts[status]+=1
        rows.append(dict(flow_id=fid,direction=direction,amount=f.get('amount'),currency=f.get('currency'),due_date=f.get('due_date'),status=status,message=message,source=origins.get(fid),support_ids=[e['source_id'] for e in matches],manual_link=manual.get(fid)))
    account_sources=selected.get('accounts') or [];reconciliation=[]
    for a in account_sources:
        observed=next((r for r in current.get('account_observations',[]) if r['account_code']==a['account_code']),None) if current else None
        status='PENDING'
        if observed:status='DECLARED_MATCH' if abs(Decimal(observed['observed_balance'])-Decimal(a['balance']))<=TOLERANCE else 'DIFFERENCE'
        reconciliation.append(dict(account_code=a['account_code'],balance=a['balance'],source=a,status=status,observation=observed))
    coverage=current.get('coverage','NOT_REVIEWED') if current else 'NOT_REVIEWED'
    gaps=[];quota_seen=set()
    linked_refs={r.get('installment_ref') for r in raw_flows.values()}
    linked_ids=set(raw_flows)
    for e in entries:
        q=e['data'];ref=q.get('installment_ref') or e['source'].get('record_id');due=q.get('due_date') or q.get('revised_due_date') or q.get('original_due_date')
        if e['kind'] not in ('sales_installment','purchase_installment') or not ref or (e['kind'],ref) in quota_seen:continue
        quota_seen.add((e['kind'],ref));pending=_number(q.get('pending_amount',q.get('pending')))
        if pending==0:continue
        if ref not in linked_refs and q.get('flow_id') not in linked_ids:gaps.append(dict(reference=ref,due_date=due,pending_amount=str(pending) if pending is not None else None,source_id=e['source_id']))
    summary=dict(total=len(rows),matched=counts['MATCHED'],declared_reviewed=counts['DECLARED_REVIEWED'],discrepancies=counts['DISCREPANCY'],pending=counts['PENDING'])
    status='DISCREPANCIES' if summary['discrepancies'] or any(r['status']=='DIFFERENCE' for r in reconciliation) else 'RECORDED_WITH_LIMITS' if current else 'PENDING_REVIEW'
    history=[]
    if saved:
        for raw,fp in c.execute('SELECT payload,fingerprint FROM company_sales_quality_review WHERE dataset_id=? ORDER BY revision DESC LIMIT 10',(dataset,)):
            item=json.loads(raw)
            if _hash(item)!=fp:raise ValueError('Una revisión histórica no coincide con su huella.')
            history.append({k:item.get(k) for k in ('revision','actor','created_at','coverage','basis_fingerprint','source_refs')})
    return dict(history=history,dataset_id=dataset,as_of_date=finance['as_of_date'],basis_fingerprint=basis,review_revision=saved['revision'] if saved else 0,review_status='CURRENT' if current else 'STALE' if saved else 'NOT_RECORDED',review=current,summary=summary,rows=rows,accounts=reconciliation,coverage=coverage,sources=entries,quota_gaps=gaps,invalid_sources=inventory['invalid_sources'],status=status,evidence_pending_count=finance.get('evidence_pending_count',0),quality_evaluation_status='NOT_EXECUTED',decision_authority=False,operational_path='FORBIDDEN')


def report(db,dataset,finance):
    with closing(sqlite3.connect(db)) as c:return _report(c,dataset,finance)


def save(db,data,finance):
    from eios.company_proposal_context import capture_context
    dataset=data.get('dataset_id')
    with closing(sqlite3.connect(db)) as c,c:
        c.execute(TABLE);c.execute('BEGIN IMMEDIATE');ctx=capture_context(c,dataset)
        if ctx['material_nature']!='SYNTHETIC' or data.get('context_fingerprint')!=ctx['fingerprint']:raise ValueError('La empresa o sus fuentes han cambiado. Repite la revisión.')
        result=_report(c,dataset,finance)
        if data.get('basis_fingerprint')!=result['basis_fingerprint'] or type(data.get('revision')) is not int or data['revision']!=result['review_revision']:raise ValueError('La revisión o las fuentes han cambiado. Comprueba de nuevo.')
        def text(key):
            value=data.get(key)
            if not isinstance(value,str) or not value.strip() or len(value)>1000:raise ValueError('Completa '+key+' con un texto de hasta 1.000 caracteres.')
            return value.strip()
        actor=text('actor');note=text('note')
        if data.get('acknowledge') is not True:raise ValueError('Confirma el alcance documental y sintético de la revisión.')
        sources={s['source_id']:s for s in result['sources']};flows={r['flow_id']:r for r in result['rows']};accounts={r['account_code']:r for r in result['accounts']}
        links=data.get('movement_links',[]);observations=data.get('account_observations',[])
        if not isinstance(links,list) or len(links)>2000 or not isinstance(observations,list) or len(observations)>1000:raise ValueError('Demasiadas observaciones.')
        used=set();used_quotas=set()
        for link in links:
            if not isinstance(link,dict) or link.get('flow_id') not in flows or link['flow_id'] in used or link.get('source_id') not in sources or sources[link['source_id']]['kind'] not in ('document','sales_installment','purchase_installment','sales_line','purchase_line'):raise ValueError('Revisa las asociaciones de movimientos y soportes.')
            if not isinstance(link.get('note'),str) or not link['note'].strip() or len(link['note'])>1000:raise ValueError('Explica la comprobación documental de cada vínculo manual.')
            support=sources[link['source_id']];d=support['data'];flow=flows[link['flow_id']]
            allowed=('sales_installment','sales_line','document') if flow['direction']=='COBRO' else ('purchase_installment','purchase_line','document')
            if support['kind'] not in allowed:raise ValueError('El tipo de soporte no corresponde al cobro o pago revisado.')
            original=(flow.get('source') or {}).get('data',{})
            for key in ('customer_id','supplier_id','invoice_number','installment_ref'):
                if original.get(key) and d.get(key) and original[key]!=d[key]:raise ValueError('El soporte y el movimiento tienen referencias de cliente, proveedor, factura o cuota diferentes.')
            if support['kind'] in ('sales_installment','purchase_installment'):
                if link['source_id'] in used_quotas:raise ValueError('No vincules una cuota a varios movimientos.')
                used_quotas.add(link['source_id'])
                amount=_number(d.get('pending_amount',d.get('pending')));due=d.get('due_date') or d.get('revised_due_date') or d.get('original_due_date')
                if (amount is not None and abs(amount-Decimal(flow['amount']))>TOLERANCE) or (due and due!=flow['due_date']) or (d.get('currency') and d['currency']!=flow['currency']):raise ValueError('La cuota no coincide con importe pendiente, fecha o moneda del movimiento. Corrige el origen; una declaración no sustituye esa corrección.')
            used.add(link['flow_id'])
        used=set()
        for observation in observations:
            if not isinstance(observation,dict) or observation.get('account_code') not in accounts or observation['account_code'] in used or observation.get('source_id') not in sources:raise ValueError('Revisa cuenta y soporte de conciliación.')
            if sources[observation['source_id']]['kind'] not in ('document','bank_statement_entry','cash_count','treasury_balances'):raise ValueError('El saldo no se concilia usando la misma fila contable. Aporta extracto, arqueo u otro soporte independiente.')
            support=sources[observation['source_id']]['source'];account_source=accounts[observation['account_code']]['source']
            if support.get('batch_id') and account_source.get('batch_id'):
                account_meta,_,_,_=source(c,account_source['batch_id'])
                if support.get('source_sha256')==account_meta.get('source_sha256'):raise ValueError('El soporte independiente no puede ser el mismo archivo de saldos contables.')
            support_kind=sources[observation['source_id']]['kind'];code=observation['account_code']
            if (support_kind=='cash_count' and not code.startswith('570')) or (support_kind=='bank_statement_entry' and not code.startswith('572')):raise ValueError('El tipo de soporte no corresponde a caja o bancos de la cuenta seleccionada.')
            known=sources[observation['source_id']]['data']
            if known.get('account_code') and known['account_code']!=code:raise ValueError('El soporte independiente corresponde a otra cuenta.')
            if known.get('currency') and known['currency']!='EUR':raise ValueError('El soporte independiente tiene otra moneda.')
            if known.get('as_of_date') and known['as_of_date']!=result['as_of_date']:raise ValueError('El soporte independiente corresponde a otro corte.')
            amount=_number(observation.get('observed_balance'))
            if amount is None:raise ValueError('Indica el saldo observado en el soporte independiente.')
            if observation.get('currency')!='EUR' or observation.get('as_of_date')!=result['as_of_date']:raise ValueError('La observación debe coincidir en corte y moneda EUR.')
            known_balance=next((_number(known[k]) for k in ('closing_balance','balance','counted_total','cash_total') if k in known),None)
            if known_balance is not None and abs(known_balance-amount)>TOLERANCE:raise ValueError('El saldo observado no coincide con el valor estructurado del soporte seleccionado.')
            observation['observed_balance']=str(amount);used.add(observation['account_code'])
        coverage=data.get('coverage','NOT_REVIEWED');refs=data.get('coverage_sources',[])
        if coverage not in ('NOT_REVIEWED','DECLARED_COMPLETE','DECLARED_INCOMPLETE') or not isinstance(refs,list) or len(refs)>100 or any(ref not in sources for ref in refs):raise ValueError('Revisa la declaración de cobertura y sus fuentes.')
        if coverage!='NOT_REVIEWED' and not refs:raise ValueError('Selecciona las fuentes que fundamentan la declaración de cobertura.')
        until=data.get('coverage_until')
        if coverage=='DECLARED_COMPLETE' and result['summary']['total']==0:raise ValueError('Sin movimientos utilizables no se declara cobertura completa desde esta revisión.')
        if coverage!='NOT_REVIEWED':
            from datetime import date
            try:until=date.fromisoformat(until).isoformat()
            except (ValueError,TypeError):raise ValueError('Indica hasta qué fecha has revisado la cobertura.') from None
            if until<result['as_of_date']:raise ValueError('El periodo de cobertura no puede terminar antes del corte.')
            if coverage=='DECLARED_COMPLETE' and any(not g['due_date'] or g['due_date']<=until for g in result['quota_gaps']):raise ValueError('Hay cuotas sin pendiente conocido o sin referencia en la previsión durante el periodo. Revisa esas filas o registra cobertura incompleta.')
        selected_refs=set(refs)|{x['source_id'] for x in links}|{x['source_id'] for x in observations}
        audit_sources={sid:dict(kind=sources[sid]['kind'],source=sources[sid]['source'],data_fingerprint=_hash(sources[sid]['data'])) for sid in sorted(selected_refs)}
        payload=dict(source_refs=audit_sources,coverage_until=until,dataset_id=dataset,revision=result['review_revision']+1,basis_fingerprint=result['basis_fingerprint'],actor=actor,note=note,created_at=datetime.now(timezone.utc).isoformat(),movement_links=links,account_observations=observations,coverage=coverage,coverage_sources=refs,decision_authority=False,operational_path='FORBIDDEN',quality_evaluation_status='NOT_EXECUTED')
        c.execute('INSERT INTO company_sales_quality_review VALUES(?,?,?,?)',(dataset,payload['revision'],json.dumps(payload,ensure_ascii=False),_hash(payload)))
    return dict(status='RECORDED_WITH_LIMITS',revision=payload['revision'],decision_authority=False)
