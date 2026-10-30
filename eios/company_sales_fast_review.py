"""Automatic commercial orientation; never grants financial or operational authority."""
from collections import defaultdict
from decimal import Decimal
import sqlite3


def cash_preview(db,payload,finance):
    from eios.company_sales_cash_plan import _execute
    result=dict(status='NOT_EXECUTED',message='Falta el total con IVA para simular el cobro.',decision_authority=False,operational_path='FORBIDDEN')
    if payload.get('total') is None:return result
    def amount(value):
        try:
            number=Decimal(str(value));return number if number.is_finite() else None
        except (ValueError,ArithmeticError):return None
    if any(f['canonical'].get('flow_type')=='COLLECTION' and f['canonical'].get('due_date')==payload['due_date'] and amount(f['canonical'].get('amount'))==Decimal(payload['total']) for f in finance.get('cash_flows',[])):
        result['message']='Existe un cobro con el mismo importe y vencimiento. Administración debe comprobar su relación para evitar duplicarlo.';return result
    # A preview is a separate hypothetical scenario, never a stored collection.
    row=dict(flow_id='SALES-PREVIEW-'+payload['proposal_id'],flow_type='COLLECTION',amount=payload['total'],due_date=payload['due_date'],declaration_ref='PROPOSED-COLLECTION:'+payload['proposal_id'],disposition='NEW_DECLARATION')
    with sqlite3.connect(db) as c:
        if not c.execute("SELECT 1 FROM sqlite_master WHERE name='company_finance_parameter_configuration'").fetchone():
            result['message']='Administración debe activar horizonte y mínimo financiero para el corte.';return result
        result=_execute(c,payload,finance,[row])
    result.update(scope='HYPOTHETICAL_SINGLE_COLLECTION_ONLY',assumptions=['Cobro único propuesto del total con IVA en el vencimiento indicado. No acredita recepción del dinero.','No se añaden pagos de mercancía, logística o regalos sin importes brutos y fechas documentadas. El margen incorpora sus costes declarados; el calendario de pagos requiere datos distintos.','Escenario separado: no modifica el calendario recibido ni suma otras ofertas guardadas. Si este cobro ya figura en la previsión, debe asociarse antes de interpretar el escenario.'],decision_authority=False,operational_path='FORBIDDEN')
    return result


def stock_check(payload):
    requested=defaultdict(Decimal);inventories={};issues=[];missing=[]
    for line in payload['lines']:
        sku=line['article_id'];requested[sku]+=Decimal(line['quantity']);inventories[sku]=line['orientation'].get('inventory')
    for sku,qty in requested.items():
        inv=inventories[sku]
        if not inv or inv.get('available') is None:missing.append(sku);continue
        available=Decimal(str(inv['available']))
        if qty>available:issues.append(dict(code='INSUFFICIENT_DOCUMENTED_STOCK',message=f'{sku}: se proponen {qty} unidades y constan {available} disponibles al corte {inv.get("as_of_date")}. Ajusta cantidad o confirma reposición.'))
    return dict(code='STOCK',title='Disponibilidad de los artículos',status='REVIEW' if issues else 'PENDING' if missing else 'CHECKED',message=' '.join(i['message'] for i in issues) if issues else 'Sin stock comparable para: '+', '.join(missing) if missing else 'Cantidad conjunta de cada artículo dentro del stock disponible documentado. Es una referencia al corte; no reserva mercancía.',action='CONDITIONS',issues=issues)


def conclusion(payload,state,analysis,checks,reasons,pending):
    commercial=[c for c in checks if c['code'] in ('MARGIN','CREDIT','STOCK')]
    missing=[c['message'] for c in commercial if c['status']=='PENDING']
    if payload.get('total') is None:missing.append('Completa el IVA para conocer el total a cobrar.')
    deferred=payload['due_date']>payload['offer_date']
    if deferred:
        missing.append('El cobro aplazado exige comprobar la cobertura financiera y de crédito de esta operación; no se presume resuelta por disponer de archivos.')
    if state.get('sales_negotiation_reason')=='CLIENT_STOCK':missing.append('Confirma con el cliente cantidad y fecha necesarias.')
    status='RENEGOTIATE' if reasons else 'MISSING_OPERATION_DATA' if missing else 'WITHIN_CHECKED_LIMITS'
    return dict(status=status,title={'RENEGOTIATE':'RENEGOCIAR ESTAS CONDICIONES','MISSING_OPERATION_DATA':'FALTAN DATOS PARA ESTA OPERACIÓN','WITHIN_CHECKED_LIMITS':'CONDICIONES DENTRO DE LOS LÍMITES COMPROBADOS'}[status],
        message='Puedes seguir preparando la oferta con las comprobaciones comerciales mostradas. No confirma viabilidad financiera ni aceptación; conserva el cobro a la vista acordado y comprueba su recepción según la entrega pactada.' if status=='WITHIN_CHECKED_LIMITS' else 'Revisa los motivos y las alternativas de esta propuesta.' if reasons else 'Se indica únicamente la información que afecta a esta operación.',
        missing=missing,reasons=reasons,total=payload.get('total'),due_date=payload['due_date'],deferred=deferred,scope='COMMERCIAL_ORIENTATION_ONLY',decision_authority=False,operational_path='FORBIDDEN')
