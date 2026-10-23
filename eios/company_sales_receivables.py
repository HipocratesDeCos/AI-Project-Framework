"""Source-bound reconciliation and draft collection export; no financial admission."""
from collections import defaultdict
import base64
import csv
from decimal import Decimal, localcontext
from hashlib import sha256
from io import StringIO
import json
import secrets
import sqlite3
from time import monotonic

from eios.company_dossier import selected_batches
from eios.company_proposal_context import _hash
from eios.company_sales_tariffs import batch
from eios.company_sales_receipt_math import effective_vat

TOLERANCE=Decimal('.01')
EXPORT_FIELDS=['flow_id','direction','amount','currency','due_date','counterparty','customer_id','invoice_number','installment_ref','payment_method']


def reconcile(db,ids):
    batches=selected_batches(db,ids);meta=batches[0][1]
    lines=defaultdict(list);quotas=defaultdict(list);flows=[];sources={};total_rows=0
    def key(d):return d['customer_id'],d['invoice_number'],d['currency']
    with sqlite3.connect(db) as c:
        for bid,m,records in batches:
            loaded=batch(c,bid)
            if not loaded or not loaded[3]:raise ValueError('Un origen no está disponible o su integridad ha cambiado.')
            if m['kind'] not in ('sales_line','sales_installment','cash_flow'):raise ValueError('Marca solo ventas, vencimientos de venta y previsiones de cobros/pagos del mismo expediente.')
            total_rows+=len(records)
            if total_rows>20000:raise ValueError('La comprobación admite hasta 20.000 filas seleccionadas.')
            sources[bid]=loaded[2]
            for r in records:
                e=dict(data=r['data'],source=dict(batch_id=bid,filename=m['filename'],sheet=m['sheet'],row=r['source_row']))
                if r['kind']=='sales_line':lines[key(r['data'])].append(e)
                elif r['kind']=='sales_installment':quotas[key(r['data'])].append(e)
                elif r['kind']=='cash_flow':flows.append(e)
        # Existing documentary collection references for this exact company/cutoff.
        canonical_sources=[]
        if c.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='documentary_company_snapshot'").fetchone():
            for dataset,manifest in c.execute('SELECT dataset_id,manifest_json FROM documentary_company_snapshot WHERE company_id=? AND as_of_date=?',(meta['company_id'],meta['as_of_date'])).fetchall():
                manifest=json.loads(manifest)
                if manifest.get('company',{}).get('legal_name')!=meta['legal_name'] or manifest.get('material_nature')!=meta['material_nature']:continue
                for record_id,raw in c.execute("SELECT record_id,record_json FROM documentary_company_record WHERE dataset_id=? AND kind='cash_flow'",(dataset,)).fetchall():
                    record=json.loads(raw);canonical_sources.append(dict(dataset_id=dataset,record_id=record_id,fingerprint=_hash(record)))
                    d=record['data'].get('canonical',{})
                    if d.get('flow_type')=='COLLECTION':flows.append(dict(data=dict(flow_id=d['flow_id'],direction='COBRO',amount=d.get('amount'),currency=d.get('currency'),due_date=d.get('due_date')),source=dict(dataset_id=dataset,record_id=record_id)))
    invoices=[];candidates=[];used_flows={};quota_refs=defaultdict(list);quota_flows=defaultdict(list);invoice_currencies=defaultdict(set)
    for k in set(lines)|set(quotas):invoice_currencies[k[:2]].add(k[2])
    for k,entries in quotas.items():
        for e in entries:
            quota_refs[e['data']['installment_ref']].append(k)
            if e['data'].get('flow_id'):quota_flows[e['data']['flow_id']].append(e['data']['installment_ref'])
    # Stable IDs detect same prepared quota already in a received forecast.
    for k in sorted(set(lines)|set(quotas)):
        customer,invoice,currency=k;ls=lines[k];qs=quotas[k];issues=[];net=Decimal(0);vat=Decimal(0);vat_known=True;declared=set();seen_lines=set();dates=set();vat_basis=[]
        def issue(code,message):issues.append(dict(code=code,message=message))
        if len(invoice_currencies[k[:2]])>1:issue('INVOICE_CURRENCY_CONFLICT','La misma factura y cliente tienen monedas distintas entre líneas o cuotas.')
        with localcontext() as context:
            context.prec=60
            for e in ls:
                d=e['data'];dates.add(d['issue_date']);signature=('LINE',Decimal(d['line_number'])) if d.get('line_number') is not None else ('CONTENT',_hash(d))
                if signature in seen_lines:issue('REPEATED_SALES_LINE','Línea de venta repetida o número de línea duplicado. Revisa la selección.')
                seen_lines.add(signature);net+=Decimal(d['net_amount']);v,basis=effective_vat(d);vat_basis.append(basis)
                if v is None:vat_known=False
                else:vat+=v
                if d.get('invoice_total') is not None:declared.add(Decimal(d['invoice_total']))
            if not ls:issue('MISSING_SALES_LINES','Faltan las líneas de venta de esta factura, cliente y moneda.')
            if len(dates)>1:issue('CONFLICTING_INVOICE_DATE','Las líneas de la factura tienen fechas distintas.')
            if not vat_known:issue('MISSING_VAT','Falta importe de IVA o tipo declarado en alguna línea. No se presupone IVA cero.')
            if len(declared)!=1:issue('INVOICE_TOTAL_NOT_UNIQUE','Indica un total de factura documentado único, aunque figure solo en una de sus líneas.')
            gross=net+vat if ls and vat_known else None;invoice_total=next(iter(declared)) if len(declared)==1 else None
            if gross is not None and invoice_total is not None and abs(gross-invoice_total)>TOLERANCE:issue('LINES_TOTAL_MISMATCH','La suma de netos e IVA no coincide con el total documentado. Revisa líneas y otros conceptos de factura.')
            quota_total=sum((Decimal(e['data']['amount']) for e in qs),Decimal(0))
            if not qs:issue('MISSING_INSTALLMENTS','Falta el calendario de cuotas de esta factura.')
            if invoice_total is not None and qs and abs(quota_total-invoice_total)>TOLERANCE:issue('INSTALLMENTS_TOTAL_MISMATCH','La suma de importes originales de las cuotas no coincide con el total documentado de factura.')
            numbers=set();quota_results=[];local_candidates=[]
            for e in qs:
                q=e['data'];ref=q['installment_ref'];n=Decimal(q['installment_number']);proposed='EIOS-COBRO-'+sha256((meta['company_id']+'\0'+customer+'\0'+invoice+'\0'+ref).encode()).hexdigest()[:24]
                row=dict(q,source=e['source'],status='REVIEW_REQUIRED',proposed_flow_id=proposed)
                if q.get('flow_id') and len(quota_flows[q['flow_id']])>1:issue('FLOW_REUSED','Una referencia de cobro se ha vinculado a más de una cuota.')
                if n in numbers:issue('DUPLICATE_INSTALLMENT_NUMBER','Número de cuota repetido para esta factura y cliente.')
                numbers.add(n)
                if len(quota_refs[ref])>1:issue('DUPLICATE_INSTALLMENT_REF','Referencia de cuota repetida entre archivos o facturas.')
                pending=q.get('pending_amount')
                if pending is None:
                    issue('PENDING_AMOUNT_UNKNOWN','Cuota '+ref+': declara su pendiente al corte; no se presume que siga íntegra sin cobrar.');quota_results.append(row);continue
                pending=Decimal(pending)
                if pending==0:row['status']='NO_PENDING_COLLECTION';quota_results.append(row);continue
                explicit=q.get('flow_id');matches=[f for f in flows if f['data'].get('flow_id')==(explicit or proposed) or (not explicit and f['data'].get('installment_ref')==ref)]
                if matches:
                    if len(matches)!=1:issue('DUPLICATE_FLOW_REFERENCE','Cuota '+ref+': la referencia de cobro aparece más de una vez. Selecciona una previsión única.');quota_results.append(row);continue
                    f=matches[0];d=f['data'];fid=d['flow_id']
                    compatible=d.get('direction')=='COBRO' and d.get('currency')==currency and d.get('due_date')==q['due_date'] and d.get('amount') is not None and abs(Decimal(d['amount'])-pending)<=TOLERANCE and all(d.get(field) in (None,'',value) for field,value in [('customer_id',customer),('invoice_number',invoice),('installment_ref',ref),('payment_method',q['payment_method'])])
                    if not compatible:issue('FLOW_MISMATCH','Cuota '+ref+': el cobro vinculado no coincide en sentido, fecha, moneda, pendiente o referencias.');quota_results.append(row);continue
                    if fid in used_flows:issue('FLOW_REUSED','El mismo cobro no puede cubrir dos cuotas.');quota_results.append(row);continue
                    used_flows[fid]=ref;row.update(status='ALREADY_IN_FORECAST',flow_id=fid,forecast_source=f['source']);quota_results.append(row);continue
                if explicit:issue('FLOW_NOT_FOUND','Cuota '+ref+': no se encuentra el cobro indicado. Incluye su previsión en la selección o revisa la referencia.');quota_results.append(row);continue
                possible=[f for f in flows if f['data'].get('direction')=='COBRO' and f['data'].get('currency')==currency and f['data'].get('due_date')==q['due_date'] and f['data'].get('amount') is not None and abs(Decimal(f['data']['amount'])-pending)<=TOLERANCE and f['data'].get('customer_id') in (None,'',customer)]
                if possible:issue('POSSIBLE_DUPLICATE_COLLECTION','Cuota '+ref+': hay cobros con la misma fecha, moneda e importe. Vincula su referencia expresamente antes de preparar otro.');row['possible_flow_ids']=[f['data']['flow_id'] for f in possible];quota_results.append(row);continue
                row['status']='NEW_DRAFT_COLLECTION';quota_results.append(row);local_candidates.append(dict(flow_id=proposed,direction='COBRO',amount=str(pending),currency=currency,due_date=q['due_date'],counterparty='Factura '+invoice+' · cuota '+str(q['installment_number']),customer_id=customer,invoice_number=invoice,installment_ref=ref,payment_method=q['payment_method']))
            if not issues:candidates.extend(local_candidates)
            else:
                for row in quota_results:
                    if row['status']=='NEW_DRAFT_COLLECTION':row['status']='BLOCKED_BY_INVOICE_REVIEW'
            invoices.append(dict(customer_id=customer,invoice_number=invoice,currency=currency,line_count=len(ls),net_amount=str(net),vat_amount=str(vat) if vat_known else None,vat_basis=sorted(set(vat_basis)),computed_gross_total=str(gross) if gross is not None else None,documented_invoice_total=str(invoice_total) if invoice_total is not None else None,installment_total=str(quota_total),status='RECONCILED' if not issues else 'REVIEW_REQUIRED',issues=issues,quotas=quota_results,line_sources=[e['source'] for e in ls]))
    issues_count=sum(len(i['issues']) for i in invoices)
    return dict(company_id=meta['company_id'],legal_name=meta['legal_name'],as_of_date=meta['as_of_date'],material_nature=meta['material_nature'],batch_ids=sorted(ids),source_fingerprints=sources,documentary_flow_sources=canonical_sources,invoices=invoices,invoice_count=len(invoices),issue_count=issues_count,candidate_count=len(candidates),draft_collections=candidates,result='PARTIAL_DRAFT' if candidates and issues_count else 'READY_FOR_DRAFT_EXPORT' if candidates else 'REVIEW_REQUIRED' if issues_count or not invoices else 'NO_NEW_COLLECTIONS',scope='RECEIVED_RECONCILIATION_AND_DRAFT_ONLY',decision_authority=False,operational_path='FORBIDDEN')


class SalesReceivables:
    def __init__(self,db,clock=monotonic):self.db=db;self.clock=clock;self.pending=None
    def check(self,data):
        self.pending=None;report=reconcile(self.db,data.get('batch_ids'))
        ticket=secrets.token_urlsafe(32) if 0<report['candidate_count']<=5000 else None
        report['export_limit']=5000
        if ticket:self.pending=dict(ticket=ticket,ids=report['batch_ids'],fingerprint=_hash(report),at=self.clock())
        return dict(report,ticket=ticket)
    def export(self,data):
        p=self.pending
        if not p or data.get('ticket')!=p['ticket'] or self.clock()-p['at']>600:raise ValueError('Vuelve a comprobar la conciliación: la preparación ha cambiado o caducado.')
        if data.get('acknowledge_draft') is not True:raise ValueError('Confirma que descargas una previsión preparada para revisión, pendiente de carga y admisión.')
        report=reconcile(self.db,p['ids']);report['export_limit']=5000
        if _hash(report)!=p['fingerprint']:raise ValueError('Los orígenes o las previsiones han cambiado. Comprueba de nuevo antes de descargar.')
        # Never put untrusted invoice/customer text into a CSV spreadsheet formula.
        def safe(value):
            value=str(value)
            return "'"+value if value.lstrip().startswith(('=','+','-','@')) else value
        stream=StringIO(newline='');writer=csv.writer(stream);writer.writerow(EXPORT_FIELDS)
        for row in report['draft_collections']:
            if any(str(row[k]).lstrip().startswith(('=','+','-','@')) for k in ('customer_id','invoice_number','installment_ref')):raise ValueError('Una referencia comienza por un carácter de fórmula. Revisa sus códigos antes de exportarla a una hoja de cálculo.')
            writer.writerow([safe(row[k]) for k in EXPORT_FIELDS])
        content=stream.getvalue().encode('utf-8-sig');self.pending=None
        return dict(filename='EIOS_Cobros_Preparados.csv',content_base64=base64.b64encode(content).decode(),record_count=report['candidate_count'],excluded_invoice_count=sum(i['status']!='RECONCILED' for i in report['invoices']),decision_authority=False,scope='DRAFT_NOT_RECEIVED_OR_ACTIVATED')
