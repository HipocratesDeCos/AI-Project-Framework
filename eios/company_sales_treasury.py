"""Explicit, reversible source selection for synthetic sales financial inputs."""
from copy import deepcopy
from datetime import datetime, timezone
from decimal import Decimal
import json
import sqlite3
import unicodedata
import re
from contextlib import closing
from eios.company_proposal_context import _hash
from eios.company_selected_inventory import source
from eios.finance.models import FinancialSnapshot, CashFlow

TABLE='''CREATE TABLE IF NOT EXISTS company_sales_treasury_selection (
dataset_id TEXT NOT NULL,revision INTEGER NOT NULL,payload TEXT NOT NULL,fingerprint TEXT NOT NULL,
PRIMARY KEY(dataset_id,revision))'''


def latest(c,dataset):
    if not c.execute("SELECT 1 FROM sqlite_master WHERE name='company_sales_treasury_selection'").fetchone():return None
    row=c.execute('SELECT payload,fingerprint FROM company_sales_treasury_selection WHERE dataset_id=? ORDER BY revision DESC LIMIT 1',(dataset,)).fetchone()
    if not row:return None
    value=json.loads(row[0])
    if _hash(value)!=row[1]:raise ValueError('La selección de tesorería no coincide con su huella.')
    return value


def scope(c,dataset):
    row=c.execute('SELECT company_id,as_of_date,manifest_json FROM documentary_company_snapshot WHERE dataset_id=?',(dataset,)).fetchone()
    if not row:raise ValueError('Empresa no encontrada.')
    manifest=json.loads(row[2])
    return row[0],manifest['company'].get('legal_name',row[0]),manifest.get('material_nature'),row[1]


def identity_status(meta,target):
    company,name,nature,cutoff=target
    if meta.get('material_nature')!='SYNTHETIC' or nature!='SYNTHETIC' or meta.get('as_of_date')!=cutoff:return 'INCOMPATIBLE'
    if (meta.get('company_id'),meta.get('legal_name'))==(company,name):return 'EXACT'
    def normalized(value):
        value=unicodedata.normalize('NFKD',str(value))
        return re.sub(r'[^a-z0-9]','',value.encode('ascii','ignore').decode().lower())
    return 'CONFIRM_IDENTITY' if normalized(meta.get('legal_name'))==normalized(name) else 'INCOMPATIBLE'


def checked_source(c,dataset,bid,kind,confirm_identity=False,cutoff=None):
    meta,records,fp,intact=source(c,bid)
    target=scope(c,dataset)
    identity=identity_status(meta,(*target[:3],cutoff or target[3]))
    if not intact or identity=='INCOMPATIBLE' or (identity=='CONFIRM_IDENTITY' and confirm_identity is not True) or meta.get('kind')!=kind:
        raise ValueError('Revisa empresa, corte e integridad. Si los códigos de empresa difieren, confirma expresamente que la razón social del archivo corresponde a la empresa activa.')
    if len(records)>20000:raise ValueError('Demasiadas filas para esta selección financiera.')
    return meta,records,fp


def build(c,dataset,bid,codes,flow_bid=None,confirm_identity=False,cutoff=None):
    if not isinstance(bid,str) or len(bid)!=64 or (flow_bid is not None and (not isinstance(flow_bid,str) or len(flow_bid)!=64)):raise ValueError('Selecciona archivos financieros recibidos válidos.')
    meta,records,fp=checked_source(c,dataset,bid,'balance',confirm_identity,cutoff)
    if not isinstance(codes,list) or not codes or len(codes)>1000 or any(not isinstance(x,str) for x in codes) or len(set(codes))!=len(codes):raise ValueError('Selecciona cuentas distintas de caja y bancos.')
    if any(not code.isdigit() or not code.startswith(('570','572')) for code in codes):raise ValueError('Solo se admiten cuentas 570 y 572 o sus subcuentas, expresadas como códigos numéricos.')
    if any(a!=b and b.startswith(a) for a in codes for b in codes):raise ValueError('No sumes una cuenta padre y sus subcuentas. Elige un único nivel de detalle.')
    amounts=[];sources=[]
    for code in codes:
        matches=[r for r in records if r['kind']=='balance' and r['data']['account_code']==code]
        if len(matches)!=1:raise ValueError('Cada cuenta seleccionada debe aparecer una sola vez en el archivo.')
        record=matches[0];d=record['data'];amount=Decimal(d['balance'])
        if d.get('currency')!='EUR' or d.get('observation_date',meta['as_of_date']) not in (None,meta['as_of_date']) or not amount.is_finite() or amount<0:raise ValueError('Revisa moneda EUR, fecha y saldo no negativo de caja/bancos. No se compensan descubiertos automáticamente.')
        amounts.append(amount);sources.append(dict(account_code=code,balance=str(amount),filename=meta['filename'],sheet=meta['sheet'],row=record['source_row'],batch_id=bid))
    total=sum(amounts,Decimal(0));fingerprints={bid:fp};identities={bid:dict(company_id=meta['company_id'],legal_name=meta['legal_name'])};flows=None
    if flow_bid:
        flowmeta,rows,flowfp=checked_source(c,dataset,flow_bid,'cash_flow',confirm_identity,meta['as_of_date']);fingerprints[flow_bid]=flowfp;identities[flow_bid]=dict(company_id=flowmeta['company_id'],legal_name=flowmeta['legal_name']);flows=[];seen=set()
        for r in rows:
            d=r['data']
            if r['kind']!='cash_flow' or d['flow_id'] in seen or d.get('currency')!='EUR':raise ValueError('Los movimientos deben ser únicos y estar expresados en EUR.')
            seen.add(d['flow_id'])
            model=CashFlow(flow_id=d['flow_id'],flow_type={'COBRO':'COLLECTION','PAGO':'PAYMENT'}[d['direction']],amount=d['amount'],currency='EUR',due_date=d['due_date'],due_date_evidenced=False,source_ref='RECEIVED:'+flow_bid+':'+str(r['source_row']),evidence_state='NOT_EVIDENCED')
            flows.append(dict(record_id=d['flow_id'],canonical=model.model_dump(mode='json'),source_refs=[dict(filename=flowmeta['filename'],sheet=flowmeta['sheet'],row=r['source_row'],batch_id=flow_bid)]))
        if not flows:raise ValueError('El calendario seleccionado está vacío.')
    return dict(amount=str(total),as_of_date=meta['as_of_date'],accounts=sources,flows=flows,source_identities=identities,source_fingerprints=fingerprints)


def selection_context(c,dataset):
    from eios.company_sales_treasury_policy import effective
    selected=effective(c,dataset)
    if not selected:return None
    current={}
    for bid in selected.get('source_fingerprints',{}):
        try:
            _,_,fp,intact=source(c,bid);current[bid]=dict(fingerprint=fp,intact=intact)
        except ValueError:current[bid]=dict(fingerprint=None,intact=False)
    return dict(selection_fingerprint=_hash(selected),sources=current)


def options(db,dataset):
    from eios.company_sales_treasury_policy import candidates,effective
    with closing(sqlite3.connect(db)) as c:
        company,name,nature,cutoff=scope(c,dataset);batches=[];excluded=[]
        for row in candidates(c,dataset):
            meta=row['metadata'];identity=identity_status(meta,(company,name,nature,meta['as_of_date']))
            if not row['intact']:
                excluded.append(dict(filename=meta['filename'],company_id=meta['company_id'],legal_name=meta['legal_name'],as_of_date=meta['as_of_date'],reason='Integridad no coincidente.'));continue
            batches.append(dict(company_id=meta['company_id'],legal_name=meta['legal_name'],requires_identity_confirmation=identity=='CONFIRM_IDENTITY',batch_id=row['batch_id'],kind=meta['kind'],filename=meta['filename'],sheet=meta['sheet'],fingerprint=row['fingerprint'],as_of_date=meta['as_of_date'],received_at=row['received_at'],receipt_order=row['receipt_order'],accounts=[dict(code=r['data']['account_code'],balance=r['data']['balance'],currency=r['data']['currency']) for r in row['records'] if r['kind']=='balance' and r['data']['account_code'].startswith(('570','572'))]))
        current=effective(c,dataset)
        if current and not current.get('resolution_error'):
            try:current=dict(current,**build(c,dataset,current['balance_batch'],current['account_codes'],current.get('flow_batch'),current.get('confirm_identity',False),current.get('as_of_date',cutoff)))
            except (ValueError,TypeError,KeyError,ArithmeticError) as error:current=dict(current,resolution_error=str(error))
        if c.execute("SELECT 1 FROM sqlite_master WHERE name='received_company_batch'").fetchone():
            compatible={r['batch_id'] for r in candidates(c,dataset)}
            for bid,raw in c.execute('SELECT batch_id,metadata_json FROM received_company_batch'):
                try:meta=json.loads(raw)
                except (ValueError,TypeError):
                    excluded.append(dict(filename='Recepción '+bid[:12],company_id='Sin identificar',legal_name='Metadatos ilegibles',as_of_date=None,reason='Revisar la identificación de la recepción.'));continue
                if not isinstance(meta,dict):continue
                if bid not in compatible and meta.get('kind') in ('balance','cash_flow'):excluded.append(dict(filename=meta['filename'],company_id=meta.get('company_id'),legal_name=meta.get('legal_name'),as_of_date=meta.get('as_of_date'),reason='Empresa o naturaleza no compatibles.'))
        return dict(batches=batches,excluded=excluded,company_id=company,current=current,company_name=name,as_of_date=current.get('as_of_date',cutoff) if current else cutoff,base_as_of_date=cutoff)


def save(db,data):
    from eios.company_proposal_context import capture_context
    dataset=data.get('dataset_id')
    with closing(sqlite3.connect(db)) as c,c:
        c.execute(TABLE);c.execute('BEGIN IMMEDIATE');ctx=capture_context(c,dataset)
        if ctx['material_nature']!='SYNTHETIC' or ctx['fingerprint']!=data.get('context_fingerprint'):raise ValueError('La empresa o los datos han cambiado. Recarga y revisa la selección.')
        actor=data.get('actor');reason=data.get('reason')
        if any(not isinstance(x,str) or not x.strip() or len(x)>500 for x in (actor,reason)):raise ValueError('Indica responsable y motivo, hasta 500 caracteres.')
        previous=latest(c,dataset);revision=(previous['revision'] if previous else 0)+1
        if data.get('clear') is True:computed=dict(source_fingerprints={})
        else:
            if data.get('acknowledge') is not True:raise ValueError('Confirma que las cuentas seleccionadas corresponden a saldos disponibles para esta simulación, sin duplicados ni importes restringidos.')
            if not isinstance(data.get('balance_batch'),str) or len(data['balance_batch'])!=64:raise ValueError('Selecciona un archivo de saldos válido.')
            meta,_,_,_=source(c,data.get('balance_batch'))
            computed=build(c,dataset,data.get('balance_batch'),data.get('account_codes'),data.get('flow_batch'),data.get('confirm_identity') is True,meta['as_of_date'])
            if computed['source_fingerprints']!=data.get('source_fingerprints'):raise ValueError('Los archivos han cambiado. Revisa de nuevo los orígenes.')
        payload=dict(mode='MANUAL',confirm_identity=data.get('confirm_identity') is True,dataset_id=dataset,revision=revision,actor=actor.strip(),reason=reason.strip(),created_at=datetime.now(timezone.utc).isoformat(),cleared=data.get('clear') is True,balance_batch=data.get('balance_batch'),account_codes=data.get('account_codes'),flow_batch=data.get('flow_batch'),**computed)
        c.execute('INSERT INTO company_sales_treasury_selection VALUES(?,?,?,?)',(dataset,revision,json.dumps(payload,ensure_ascii=False),_hash(payload)))
    return dict(status='CLEARED' if payload['cleared'] else 'SELECTED',revision=revision,decision_authority=False)


def apply(db,dataset,finance):
    result=deepcopy(finance)
    with closing(sqlite3.connect(db)) as c:
        from eios.company_sales_treasury_policy import effective
        selected=effective(c,dataset)
        if not selected:return result
        try:
            if selected.get('resolution_error'):raise ValueError(selected['resolution_error'])
            computed=build(c,dataset,selected['balance_batch'],selected['account_codes'],selected.get('flow_batch'),selected.get('confirm_identity',False),selected.get('as_of_date',result['as_of_date']))
            if computed['source_fingerprints']!=selected['source_fingerprints']:raise ValueError('El origen seleccionado ha cambiado.')
            base_snapshot=result.get('financial_snapshot') or {}
            if computed['as_of_date']!=result['as_of_date']:
                base_snapshot={}
                result['working_capital_input']=None
                result['cash_flows']=[];result['record_counts']['cash_flow']=0;result['evidence_pending_count']=0
                result['issues'].append('El corte financiero es más reciente que el balance canónico de base; no se mezclan sus magnitudes de fondo de maniobra ni sus movimientos.')
            result['as_of_date']=computed['as_of_date']
            raw=dict(base_snapshot,company_scope=result['company_id'],as_of_date=result['as_of_date'],data_snapshot_id=_hash(selected)[:64],currency='EUR',available_treasury=computed['amount'],treasury_evidence_ref='SALES-TREASURY-DECLARATION:'+_hash(selected))
            result['financial_snapshot']=FinancialSnapshot.model_validate(raw).model_dump(mode='json')
            result['record_counts']['financial_snapshot']=1
            if computed['flows'] is not None:
                result['cash_flows']=computed['flows'];result['record_counts']['cash_flow']=len(computed['flows']);result['evidence_pending_count']=len(computed['flows'])
                result['issues']=[x for x in result['issues'] if not any(fragment in x for fragment in ('movimientos canónicos','Un movimiento','Existen movimientos','identidad de movimiento','movimientos documentales'))]
                result['issues'].append('Los movimientos recibidos seleccionados permanecen sin evidencia validada; su cobertura completa no está acreditada.')
            result['treasury_selection']=dict(mode=selected.get('mode','MANUAL'),as_of_date=computed['as_of_date'],balance_batch=selected['balance_batch'],flow_batch=selected.get('flow_batch'),status='AUTO_SELECTED_NOT_RECONCILED' if selected.get('mode')=='AUTO' else 'SELECTED_DECLARATION_NOT_RECONCILED',revision=selected['revision'],accounts=computed['accounts'],actor=selected['actor'],amount=computed['amount'])
        except (ValueError,KeyError,TypeError,ArithmeticError) as error:
            result['as_of_date']=selected.get('as_of_date',result['as_of_date'])
            result['financial_snapshot']=None;result['cash_flows']=[];result['record_counts']['cash_flow']=0;result['evidence_pending_count']=0
            result['treasury_selection']=dict(mode=selected.get('mode','MANUAL'),as_of_date=selected.get('as_of_date'),status='STALE',message=str(error),revision=selected['revision'])
        result['opening_treasury_reconciled']=None
        result['issues']=[x for x in result['issues'] if 'situación financiera' not in x and 'tesorería disponible' not in x]
        result['issues'].append('Selección de caja/bancos declarada para simulación; conciliación y disponibilidad no verificadas automáticamente.' if result['financial_snapshot'] else 'Selección financiera no utilizable; revisar y vincular de nuevo.')
        result['fingerprint']=_hash({k:v for k,v in result.items() if k!='fingerprint'})
    return result
