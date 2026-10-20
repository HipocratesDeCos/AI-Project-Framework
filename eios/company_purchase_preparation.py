"""Received-version adapter to the existing PurchaseOperation contract, not a DIP."""
from collections import defaultdict
from datetime import date
from decimal import Decimal, InvalidOperation, localcontext
from hashlib import sha256

from pydantic import ValidationError

from eios.core.models import PurchaseOperation
from eios.company_dossier import selected_batches
from eios.company_dossier_versions import version
from eios.company_received_articles import received_article
from eios.company_reception import canonical

SCHEMA = 'EIOS-RECEIVED-PURCHASE-PREPARATION-01/v0.1'


def preparation_options(db, dossier_id):
    saved = version(db, dossier_id)
    collected = {kind:defaultdict(list) for kind in ('article','supplier')}
    for bid,meta,records in selected_batches(db, saved['manifest']['batch_ids']):
        for record in records:
            kind = record['kind']
            if kind in collected:
                collected[kind][record['data'][kind+'_id']].append(dict(data=record['data'],source=dict(batch_id=bid,filename=meta['filename'],sheet=meta['sheet'],row=record['source_row'])))
    result = dict(dossier_id=dossier_id,name=saved['name'],company_id=saved['manifest']['company_id'],legal_name=saved['manifest']['legal_name'],as_of_date=saved['manifest']['as_of_date'],material_nature=saved['manifest']['material_nature'],articles=[],suppliers=[],blocked=[])
    for kind,index in collected.items():
        for identifier,entries in sorted(index.items()):
            variants = {canonical(entry['data']) for entry in entries}
            if len(variants)!=1 or len(identifier)>64:
                result['blocked'].append(dict(kind=kind,identifier=identifier,reason='Ficha contradictoria o identificador incompatible con el contrato de compra.'))
            else:
                result['articles' if kind=='article' else 'suppliers'].append(dict(entries[0]['data'],sources=[entry['source'] for entry in entries]))
    result.update(admission_status='PENDING',operational_path='FORBIDDEN',decision_authority=False)
    return result


def prepare_purchase(db, dossier_id, operation):
    allowed = {'reference','article_id','supplier_id','unit','quantity','unit_price','currency','operation_date'}
    if not isinstance(operation,dict) or set(operation)!=allowed:
        raise ValueError('Completa referencia, artículo, proveedor, unidad, cantidad, precio neto, moneda y fecha de la operación.')
    if not isinstance(operation['reference'],str) or not 1<=len(operation['reference'].strip())<=100 or any(ord(ch)<32 for ch in operation['reference']):
        raise ValueError('Indica una referencia de hasta 100 caracteres, sin saltos de línea.')
    options = preparation_options(db,dossier_id)
    article = next((item for item in options['articles'] if item['article_id']==operation['article_id']),None)
    supplier = next((item for item in options['suppliers'] if item['supplier_id']==operation['supplier_id']),None)
    if article is None or supplier is None:
        raise ValueError('Selecciona un artículo y proveedor con ficha única en esta versión.')
    if operation['unit']!=article['unit']:
        raise ValueError('La unidad debe coincidir exactamente con la ficha del artículo; no se convierten embalajes.')
    try:
        ordered = date.fromisoformat(operation['operation_date'])
        if any(isinstance(operation[field],bool) for field in ('quantity','unit_price')):
            raise ValueError()
        qty,price = (Decimal(str(operation[field])) for field in ('quantity','unit_price'))
        if not qty.is_finite() or not price.is_finite() or qty>Decimal('1000000000') or price>Decimal('1000000000'):
            raise ValueError()
    except (ValueError,TypeError,InvalidOperation):
        raise ValueError('Revisa fecha ISO, cantidad y precio finitos, de hasta 1.000.000.000.') from None
    identity = dict(dossier_id=dossier_id,reference=operation['reference'].strip(),article_id=operation['article_id'],supplier_id=operation['supplier_id'],quantity=format(qty,'f'),unit_price=format(price,'f'),unit=operation['unit'],currency=operation['currency'],operation_date=ordered.isoformat())
    digest = sha256(canonical(identity).encode()).hexdigest()
    try:
        purchase = PurchaseOperation(decision_id='prep_'+digest[:56],scenario_id='base_'+digest[:56],article_id=operation['article_id'],supplier_id=operation['supplier_id'],quantity=qty,unit_price=price,currency=operation['currency'],operation_date=ordered)
    except ValidationError as error:
        raise ValueError('Contrato de compra no válido: '+ '; '.join('.'.join(str(x) for x in item['loc'])+': '+item['msg'] for item in error.errors())) from None
    saved = version(db,dossier_id)
    source = received_article(db,saved['manifest']['batch_ids'],purchase.article_id)
    horizon = min(ordered,date.fromisoformat(source['as_of_date']))
    rows = [entry for entry in source['purchases'] if entry['data']['supplier_id']==purchase.supplier_id and entry['data']['currency']==purchase.currency and date.fromisoformat(entry['data']['issue_date'])<=horizon]
    latest_date = max((entry['data']['issue_date'] for entry in rows),default=None)
    latest = [entry for entry in rows if entry['data']['issue_date']==latest_date]
    headers = defaultdict(set)
    for entry in source['purchases']:
        d=entry['data']
        headers[(d['supplier_id'],d['invoice_number'])].add((d['issue_date'],d['currency']))
    reference = dict(status='NO_ELIGIBLE_HISTORY',message='Sin compra anterior o igual a la operación y corte, para este proveedor y moneda.',date=latest_date,quantity=None,unit=operation['unit'],currency=purchase.currency,net_unit_price=None,difference_per_unit=None,difference_percent=None,sources=[entry['source'] for entry in latest])
    if latest:
        if any(len(headers[(entry['data']['supplier_id'],entry['data']['invoice_number'])])>1 for entry in latest):
            reference.update(status='CONFLICTING_INVOICE',message='La última factura presenta fecha o moneda contradictorias.')
        elif any(entry['data']['unit']!=operation['unit'] for entry in latest):
            reference.update(status='UNIT_MISMATCH',message='La última fecha contiene una unidad distinta; no se sustituye por una compra anterior.')
        elif len(latest)!=1:
            reference.update(status='AMBIGUOUS_LAST_DATE',message='Varias líneas en la última fecha; no se elige ni suma una referencia.')
        else:
            previous = Decimal(latest[0]['net_unit_price'])
            with localcontext() as context:
                context.prec=max(50,len(str(previous))+len(str(price))+10)
                difference=price-previous
                percent=None if previous==0 else format((difference/previous*100).quantize(Decimal('.01')),'f')
            reference.update(status='DOCUMENTED_REFERENCE',message='Referencia descriptiva por proveedor, moneda y fecha; no evalúa reglas de precio.',quantity=latest[0]['data']['quantity'],net_unit_price=format(previous,'f'),difference_per_unit=format(difference,'f'),difference_percent=percent)
    stock=dict(source['stock'],as_of_date=source['as_of_date'])
    if stock['status']=='DOCUMENTED_INVENTORY' and date.fromisoformat(source['as_of_date'])>ordered:
        stock.update(status='SNAPSHOT_AFTER_OPERATION',physical=None,reserved=None,available=None)
    stock['message']='Referencia a su fecha documentada; no acredita stock actual, demanda prevista ni necesidad de compra.'
    pending=[
        dict(code='CONTEXT_BINDING',message='Vincular las versiones de reglas, parámetros y snapshot para construir DecisionContext.'),
        dict(code='EVIDENCE_BINDING',message='Vincular evidencias y procedencia aceptadas; las filas recibidas son referencias documentales.'),
        dict(code='FINANCE_INPUT',message='Completar tesorería sustentada, vencimientos/cuotas, IVA, portes y otros costes de la operación.'),
        dict(code='PARAMETER_CENTER',message='Resolver el horizonte financiero y los parámetros aplicables desde el Centro, con fecha y versión.'),
        dict(code='STOCK_CONTEXT',message='Confirmar vigencia de inventario, pedidos pendientes, demanda y justificación de necesidad.'),
        dict(code='ADMISSION_AND_EXECUTION',message='Completar el proceso de admisión y la entrada canónica antes de ejecutar reglas y decisor.'),
    ]
    result=dict(schema=SCHEMA,dossier_id=dossier_id,version_name=saved['name'],company_id=source['company_id'],legal_name=source['legal_name'],material_nature=source['material_nature'],as_of_date=source['as_of_date'],reference=identity['reference'],unit=operation['unit'],purchase_operation=purchase.model_dump(mode='json'),contract='eios.core.models.PurchaseOperation',operation_contract_valid=True,
        price_reference=reference,stock_reference=stock,source_links=dict(article=article['sources'],supplier=supplier['sources']),
        saved_check_issue_count=saved['check']['issue_count'],saved_check_sha256=saved['manifest']['check_sha256'],
        decision_context=None,evidence=None,financial_input=None,decision_input_package=None,pending=pending,
        preparation_status='PARTIAL_INPUT',evaluation_status='NOT_EXECUTED',admission_status='PENDING',operational_path='FORBIDDEN',decision_authority=False,
        scope='Operación validada con el contrato existente y vinculada a una versión recibida. Preparación parcial: no ejecuta QTG, reglas o decisor ni constituye un paquete DIP completo.')
    result['preparation_id']=sha256(canonical(result).encode()).hexdigest()
    return result
