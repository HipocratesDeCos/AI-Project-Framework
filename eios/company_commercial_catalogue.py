"""Explicit, reversible synthetic catalogue references; never invoices or inventory."""
from copy import deepcopy
from datetime import datetime, timezone
from decimal import Decimal
from hashlib import sha256
import json
from pathlib import PurePosixPath
import secrets
import sqlite3
from time import monotonic

from eios.company_tables import read_table, number
from eios.company_proposal_context import _hash

SCHEMA='''CREATE TABLE IF NOT EXISTS company_commercial_catalogue (
 dataset_id TEXT NOT NULL, revision INTEGER NOT NULL, payload TEXT NOT NULL,
 content BLOB NOT NULL, PRIMARY KEY(dataset_id,revision))'''
FIELDS={'article_id':'sku','description':'descripcion','supplier_name':'proveedor',
        'catalogue_unit_cost':'coste','recommended_sale_price':'precio_pvp_recomendado',
        'inactive':'estado_baja','family':'subfama'}


def active(c,dataset):
    if not c.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='company_commercial_catalogue'").fetchone():return None
    row=c.execute('SELECT payload,content FROM company_commercial_catalogue WHERE dataset_id=? ORDER BY revision DESC LIMIT 1',(dataset,)).fetchone()
    if not row:return None
    payload=json.loads(row[0])
    if payload.get('cleared'):return payload
    if sha256(bytes(row[1])).hexdigest()!=payload['source_sha256'] or _hash(payload['articles'])!=payload['articles_sha256']:
        raise ValueError('La integridad del catálogo incorporado no coincide. Revisa o retira la selección.')
    return payload


def catalogue_context(c,dataset):
    payload=active(c,dataset)
    if not payload:return None
    return dict(revision=payload['revision'],fingerprint=_hash(payload),source_sha256=payload.get('source_sha256'),cleared=payload.get('cleared',False))


def apply_catalogue(c,dataset,articles,suppliers):
    payload=active(c,dataset)
    if not payload or payload.get('cleared'):return articles,suppliers,None
    index={a['article_id']:deepcopy(a) for a in articles};parties={s['supplier_id']:deepcopy(s) for s in suppliers}
    for item in payload['articles']:
        sku=item['article_id'];old=index.get(sku)
        if old and old.get('unit_as_documented')!='uds.':raise ValueError('La unidad del catálogo activo ha cambiado. Retira y revisa su incorporación.')
        if old is None:
            supplier=item['supplier_id'];parties.setdefault(supplier,dict(supplier_id=supplier,legal_name=item['supplier_name'],identity_basis='CATALOGUE_NAME_ONLY_NOT_FISCALLY_VERIFIED'))
            old=dict(article_id=sku,description=item['description'],supplier_id=supplier,unit_as_documented='uds.',family=item.get('family'),stock_quantity=None,demand_forecast=None)
        old.update(catalogue_unit_cost=item['catalogue_unit_cost'],commercial_catalogue=dict(filename=payload['filename'],source_sha256=payload['source_sha256'],sheet=payload['sheet'],source_row=item['source_row'],revision=payload['revision'],actor=payload['actor'],unit_basis='EXPLICIT_USER_DECLARATION',currency_basis='EXPLICIT_USER_DECLARATION',validity='NOT_DOCUMENTED',source_as_of_date=None,decision_authority=False))
        # A pre-existing explicitly selected tariff remains authoritative in apply_tariffs.
        old['recommended_sale_price']=item['recommended_sale_price'];old['sale_currency']='EUR'
        index[sku]=old
    return list(index.values()),list(parties.values()),dict(filename=payload['filename'],revision=payload['revision'],source_sha256=payload['source_sha256'],article_count=len(payload['articles']),source_as_of_date=None,unit='uds.',currency='EUR',scope='SYNTHETIC_CATALOGUE_REFERENCES_NOT_HISTORY_OR_INVENTORY',decision_authority=False)


class CommercialCatalogue:
    def __init__(self,db,clock=monotonic):self.db=db;self.clock=clock;self.pending=None

    def preview(self,content,filename,data):
        from eios.company_proposal_context import capture_context
        self.pending=None
        dataset=data.get('dataset_id')
        if data.get('acknowledge_synthetic_units_eur_net') is not True:
            raise ValueError('Confirma datos ficticios, venta por unidades, EUR y coste/PVP sin IVA.')
        with sqlite3.connect(self.db) as c:
            ctx=capture_context(c,dataset)
            if ctx.get('exclusive_workbook'):raise ValueError('Esta versión usa exclusivamente su Excel. Recibe y activa una nueva versión del libro para cambiar el catálogo.')
            if ctx['material_nature']!='SYNTHETIC':raise ValueError('Esta incorporación admite solo empresas ficticias.')
            if data.get('context_fingerprint')!=ctx['fingerprint']:raise ValueError('La empresa o sus referencias han cambiado. Recarga la pantalla.')
            base=[json.loads(r[0])['data'] for r in c.execute("SELECT record_json FROM documentary_company_record WHERE dataset_id=? AND kind='article'",(dataset,))]
        table=read_table(content,filename,sheet=data.get('sheet') or None,max_rows=20000)
        columns={};mapping=data.get('mapping')
        if mapping is not None and not isinstance(mapping,dict):raise ValueError('Mapeo no válido.')
        for key,header in FIELDS.items():
            if mapping is None:
                matches=[i for i,h in enumerate(table['headers']) if h.strip().casefold()==header]
                if len(matches)!=1:raise ValueError('Falta una cabecera única: '+header)
                col=matches[0]
            else:col=mapping.get(key)
            if type(col) is not int or not 0<=col<len(table['headers']):raise ValueError('Selecciona la columna '+header)
            columns[key]=col
        if len(set(columns.values()))!=len(columns):raise ValueError('Una columna no puede tener dos destinos.')
        base_index={a['article_id']:a for a in base};seen=set();articles=[];errors=[];inactive=0;pending_prices=0
        for row in table['rows']:
            values={key:row['values'][col] for key,col in columns.items()};line=row['row']
            try:
                for key in ('article_id','description','supplier_name'):
                    value=values[key]
                    if not isinstance(value,str) or not value.strip() or len(value.strip())>(64 if key=='article_id' else 500):raise ValueError('Revisa '+FIELDS[key]+': texto obligatorio y SKU de hasta 64 caracteres.')
                    values[key]=value.strip()
                sku=values['article_id']
                if sku in seen:raise ValueError('SKU repetido después de quitar espacios exteriores.')
                seen.add(sku)
                flag=str(values['inactive']).strip().casefold()
                if flag not in ('true','false','1','0'):raise ValueError('estado_baja debe indicar True/False o 1/0.')
                if flag in ('true','1'):inactive+=1;continue
                if sku in base_index and base_index[sku].get('unit_as_documented')!='uds.':raise ValueError('SKU existente con otra unidad. No se convierte automáticamente.')
                cost=number(values['catalogue_unit_cost'],data.get('number_format','ES'))
                if cost<0:raise ValueError('Coste negativo no admitido.')
                raw=values['recommended_sale_price'];price=None
                if raw is None or raw=='' or isinstance(raw,dict):pending_prices+=1
                else:
                    price=number(raw,data.get('number_format','ES'))
                    if price<0:raise ValueError('PVP negativo no admitido.')
                family=values['family']
                if isinstance(family,dict):raise ValueError('Familia con fórmula; aporta texto.')
                party='CAT-SUP-'+sha256((ctx['company_id']+'\0'+values['supplier_name']).encode()).hexdigest()[:24]
                articles.append(dict(article_id=sku,description=values['description'],supplier_id=party,supplier_name=values['supplier_name'],catalogue_unit_cost=str(cost),recommended_sale_price=None if price is None else str(price),family=str(family).strip() if family is not None else None,source_row=line))
            except (ValueError,ArithmeticError) as e:errors.append(dict(row=line,message=str(e)))
        existing=sum(a['article_id'] in base_index for a in articles)
        digest=sha256(content).hexdigest()
        payload=dict(filename=PurePosixPath(filename.replace('\\','/')).name[:200],sheet=table['sheet'],source_sha256=digest,articles=articles,articles_sha256=_hash(articles))
        report=dict(dataset_id=dataset,company_name=ctx['company_name'],cutoff=ctx['documentary_cutoff'],filename=payload['filename'],rows=len(table['rows']),new_articles=len(articles)-existing,updated_articles=existing,inactive_excluded=inactive,pending_prices=pending_prices,error_count=len(errors),errors=errors[:50],sample=articles[:8],mapping=columns,headers=table['headers'],source_sha256=digest,stock='UNCHANGED_NO_INVENTORY_IN_FILE',supplier_policy='PROPOSED_IDS_FROM_EXACT_NAMES_NOT_MERGED_WITH_EXISTING_SUPPLIERS',price_policy='FIXED_NET_EUR_VALUES_ONLY_FORMULAS_LEFT_PENDING_NO_VALIDITY_DOCUMENTED',decision_authority=False)
        if not errors and articles:
            ticket=secrets.token_urlsafe(32);self.pending=dict(ticket=ticket,dataset=dataset,context=ctx['fingerprint'],payload=payload,content=bytes(content),at=self.clock());report['ticket']=ticket
        else:report['ticket']=None
        return report

    def commit(self,data):
        from eios.company_proposal_context import capture_context
        p=self.pending
        if not p or data.get('ticket')!=p['ticket'] or self.clock()-p['at']>600:raise ValueError('La vista previa ha cambiado o caducado. Comprueba el archivo de nuevo.')
        actor,reason=data.get('actor'),data.get('reason')
        if any(not isinstance(v,str) or not v.strip() or len(v)>500 for v in (actor,reason)):raise ValueError('Indica responsable y motivo, hasta 500 caracteres.')
        with sqlite3.connect(self.db) as c:
            c.execute(SCHEMA);c.execute('BEGIN IMMEDIATE');ctx=capture_context(c,p['dataset'])
            if ctx['fingerprint']!=p['context']:raise ValueError('Las referencias han cambiado desde la vista previa. Comprueba de nuevo.')
            previous=active(c,p['dataset'])
            if previous and not previous.get('cleared') and previous['source_sha256']==p['payload']['source_sha256'] and previous['articles_sha256']==p['payload']['articles_sha256']:
                self.pending=None;return dict(status='UNCHANGED',dataset_id=p['dataset'],revision=previous['revision'])
            payload=dict(p['payload'],revision=(previous['revision'] if previous else 0)+1,actor=actor.strip(),reason=reason.strip(),created_at=datetime.now(timezone.utc).isoformat(),material_nature='SYNTHETIC',decision_authority=False,operational_path='FORBIDDEN')
            c.execute('INSERT INTO company_commercial_catalogue VALUES(?,?,?,?)',(p['dataset'],payload['revision'],json.dumps(payload,ensure_ascii=False),p['content']))
        self.pending=None
        return dict(status='SELECTED',dataset_id=p['dataset'],revision=payload['revision'],article_count=len(payload['articles']),decision_authority=False)

    def clear(self,data):
        from eios.company_proposal_context import capture_context
        if any(not isinstance(data.get(k),str) or not data[k].strip() or len(data[k])>500 for k in ('actor','reason')):raise ValueError('Indica responsable y motivo, hasta 500 caracteres.')
        with sqlite3.connect(self.db) as c:
            c.execute(SCHEMA);c.execute('BEGIN IMMEDIATE');ctx=capture_context(c,data['dataset_id'])
            if data.get('context_fingerprint')!=ctx['fingerprint']:raise ValueError('La empresa o sus referencias han cambiado.')
            previous=active(c,data['dataset_id'])
            if not previous or previous.get('cleared'):raise ValueError('No hay catálogo seleccionado que retirar.')
            payload=dict(revision=previous['revision']+1,cleared=True,actor=data['actor'].strip(),reason=data['reason'].strip(),created_at=datetime.now(timezone.utc).isoformat())
            c.execute('INSERT INTO company_commercial_catalogue VALUES(?,?,?,?)',(data['dataset_id'],payload['revision'],json.dumps(payload),b''))
        self.pending=None
        return dict(status='CLEARED',dataset_id=data['dataset_id'],decision_authority=False)
