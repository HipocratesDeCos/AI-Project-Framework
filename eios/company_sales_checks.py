"""Inspectable sales checks; source availability does not grant decision authority."""
from decimal import Decimal


def sales_checks(payload, state, analysis):
    checks=[]
    def add(key,title,status,message,action):
        checks.append(dict(code=key,title=title,status=status,message=message,action=action))
    minimum=state.get('sales_parameters',{}).get('values',{}).get('P-MGE-001')
    margin=analysis.get('contribution_margin_exact')
    if minimum is None:
        add('MARGIN','Margen mínimo','PENDING','Configura el margen mínimo de esta empresa en Parámetros.','PARAMETERS')
    elif margin is None:
        add('MARGIN','Margen mínimo','PENDING','Falta un coste comparable de algún artículo, el coste logístico declarado o una venta neta positiva. Revisa Ficha e historial y las condiciones.','SOURCES')
    else:
        add('MARGIN','Margen mínimo','REVIEW' if Decimal(margin)<Decimal(str(minimum)) else 'CHECKED',f'Margen calculado {analysis["contribution_margin_percent"]} % frente a mínimo empresarial {minimum} %. Comprobación comercial con los costes disponibles.','CONDITIONS')
    credit=state.get('sales_customer_credit') or {}
    overdue=credit.get('overdue_installments',[])
    add('CREDIT','Crédito del cliente','REVIEW' if overdue else 'PENDING',
        f'{len(overdue)} cuotas vencidas al corte; revisar antes de aplazar el cobro.' if overdue else
        f'{credit.get("checked_installments",0)} cuotas comprobadas al corte. La cobertura completa y el historial de impagos no están acreditados; revisa los vencimientos y saldos del cliente.','SOURCES')
    finance=analysis.get('financial_inputs') or {}
    treasury=analysis.get('financial_context',{}).get('treasury')
    add('TREASURY','Saldo inicial de tesorería','PENDING' if treasury is None else 'CHECKED',
        'La situación financiera vinculada no aporta un saldo de tesorería utilizable para esta empresa, corte y moneda. Revisa el vínculo y los soportes de caja y bancos.' if treasury is None else
        f'Saldo documental vinculado: {treasury} EUR. No acredita por sí solo conciliación ni disponibilidad actual.','TREASURY')
    flows=finance.get('cash_flows') or []
    pending=finance.get('evidence_pending_count',0)
    add('QUALITY','Calidad y cobertura de datos','PENDING',
        f'{len(flows)} movimientos de tesorería vinculados; {pending} con evidencia pendiente. Completitud del calendario y conciliación del saldo inicial pendientes de acreditar. '+ ' '.join(finance.get('issues') or []),'SOURCES')
    add('CASH_PLAN','Efecto de esta venta en tesorería','PENDING',
        'Completa y guarda la oferta. Después abre su plan de cobros y pagos, declara las cuotas y los pagos de costes y señala los movimientos ya documentados para no duplicarlos. El motor requiere horizonte y mínimo de tesorería vigentes.','CASH_PLAN')
    add('AUTHORITY','Validación integral de la venta','PENDING',
        'El circuito integral de ventas con calidad y crédito verificados todavía no está implementado en esta pantalla. Las comprobaciones comerciales y la proyección financiera no autorizan la operación.','NONE')
    return checks
