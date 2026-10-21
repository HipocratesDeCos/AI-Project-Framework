"""Capture an explicit proposal payment schedule without certifying its evidence."""
from datetime import date
from decimal import Decimal, InvalidOperation

from eios.finance.models import CashFlow

MAX_INSTALLMENTS = 20


def payment_plan(data, proposal):
    """Validate declared costs and final maturities; never infer installments."""
    rows = data.get('payment_installments')
    if rows is None:
        return dict(schema='COMPANY-PROPOSAL-PAYMENT-PLAN-01', status='NOT_DECLARED',
                    installments=[], decision_authority=False, operational_path='FORBIDDEN')
    if not isinstance(rows, list) or not 1 <= len(rows) <= MAX_INSTALLMENTS:
        raise ValueError('Indica entre 1 y 20 cuotas o deja el calendario sin declarar.')
    if proposal.get('operation_total') is None:
        raise ValueError('Confirma los portes antes de declarar el calendario completo.')
    shipping = proposal['commercial_terms']['shipping']
    totals = {'MERCHANDISE': Decimal(proposal['total']),
              'FREIGHT': Decimal(shipping['total'])}
    last = {'MERCHANDISE': proposal['due_date'], 'FREIGHT': shipping['due_date']}
    sums = {key: Decimal(0) for key in totals}
    dates = {key: [] for key in totals}
    installments = []
    for sequence, row in enumerate(rows, 1):
        if not isinstance(row, dict) or set(row) != {'component','amount','due_date'}:
            raise ValueError('Cada cuota requiere únicamente concepto, importe y vencimiento.')
        component = row['component']
        if not isinstance(component, str) or component not in totals:
            raise ValueError('El concepto de cada cuota debe ser mercancía o portes.')
        try:
            if isinstance(row['amount'], bool) or not isinstance(row['amount'], (str,int,float,Decimal)):
                raise ValueError()
            amount = Decimal(str(row['amount']))
            if not amount.is_finite() or amount <= 0 or amount > Decimal('1000000000000000000000'):
                raise ValueError()
            if amount != amount.quantize(Decimal('.01')):
                raise ValueError()
            due = date.fromisoformat(row['due_date'])
            if due.isoformat() != row['due_date'] or due < date.fromisoformat(proposal['order_date']):
                raise ValueError()
        except (ValueError, TypeError, InvalidOperation):
            raise ValueError('Cada cuota requiere importe positivo con hasta dos decimales y fecha válida posterior o igual al pedido.') from None
        if totals[component] == 0:
            raise ValueError('No declares cuotas para un concepto sin importe.')
        if dates[component] and due <= dates[component][-1]:
            raise ValueError('Ordena las cuotas de cada concepto por fechas estrictamente crecientes.')
        sums[component] += amount
        dates[component].append(due)
        # The identifier names a declared candidate, never a documented company cash flow.
        flow = CashFlow(flow_id='PROPOSAL-' + proposal['proposal_id'] + '-' + str(sequence),
                        flow_type='PAYMENT', amount=amount, currency=proposal['currency'],
                        due_date=due, due_date_evidenced=False, source_ref=None,
                        evidence_state='NOT_EVIDENCED')
        installments.append(dict(sequence=sequence, component=component,
                                 amount=format(amount,'.2f'), due_date=due.isoformat(),
                                 canonical_candidate=flow.model_dump(mode='json')))
    for key in totals:
        if sums[key] != totals[key]:
            raise ValueError('Las cuotas de ' + ('mercancía' if key=='MERCHANDISE' else 'portes') + ' no cuadran con su total, IVA incluido.')
        if dates[key] and dates[key][-1].isoformat() != last[key]:
            raise ValueError('El último vencimiento de cada concepto debe coincidir con el declarado en la propuesta.')
    return dict(schema='COMPANY-PROPOSAL-PAYMENT-PLAN-01',
                status='DECLARED_UNVERIFIED', installments=installments,
                total=format(sum(sums.values()),'.2f'), currency=proposal['currency'],
                scope='DECLARED_PROPOSAL_COSTS_ONLY',
                cash_flow_membership_status='NOT_REVIEWED',
                completeness_status='OTHER_COSTS_NOT_ESTABLISHED',
                included_in_documentary_projection=False,
                decision_authority=False, operational_path='FORBIDDEN')
