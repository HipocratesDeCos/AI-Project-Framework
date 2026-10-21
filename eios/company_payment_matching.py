"""Find documentary payment candidates; numerical coincidence is not association."""
from collections import Counter
from decimal import Decimal
from hashlib import sha256
import json

from eios.finance.models import CashFlow


def payment_matching(proposal, documentary):
    result = dict(schema='COMPANY-PAYMENT-CANDIDATES-01',
                  dataset_id=proposal['dataset_id'], proposal_id=proposal['proposal_id'],
                  status='NOT_DECLARED', rows=[], issues=[],
                  scope='AMOUNT_CURRENCY_DUE_DATE_COINCIDENCE_ONLY',
                  inventory_completeness='NOT_ESTABLISHED',
                  association_status='NOT_REVIEWED',
                  included_in_projection=False, decision_authority=False,
                  operational_path='FORBIDDEN')
    def finish():
        result['fingerprint'] = sha256(json.dumps(result,sort_keys=True,ensure_ascii=False,
                                                separators=(',',':')).encode()).hexdigest()
        return result
    if documentary['dataset_id'] != proposal['dataset_id']:
        raise ValueError('El calendario y la tesorería pertenecen a versiones distintas.')
    plan = proposal.get('payment_plan')
    if not plan or plan['status'] == 'NOT_DECLARED':
        return finish()
    if plan['status'] != 'DECLARED_UNVERIFIED':
        raise ValueError('Calendario de pagos no compatible.')
    candidates = []
    for item in documentary['cash_flows']:
        try:
            f = CashFlow.model_validate(item['canonical'])
            if f.flow_id != item['record_id']:
                raise ValueError('identity')
            candidates.append((item,f))
        except (ValueError,KeyError,TypeError):
            result['issues'].append('Un movimiento tiene formato o identidad incompatible; no se usa como candidato.')
    identities = Counter(f.flow_id for _,f in candidates)
    duplicates = {key for key,count in identities.items() if count > 1}
    if duplicates:
        result['issues'].append('Hay identidades de movimiento duplicadas; se excluyen de las coincidencias.')
    if len(candidates) != documentary['record_counts']['cash_flow']:
        result['issues'].append('No se ha podido examinar el inventario completo de movimientos registrados.')
    candidates = [(item,f) for item,f in candidates if f.flow_id not in duplicates]
    for installment in plan['installments']:
        found = []
        for item,f in candidates:
            if (f.flow_type == 'PAYMENT' and f.amount == Decimal(installment['amount'])
                    and f.currency == plan['currency']
                    and f.due_date is not None and f.due_date.isoformat() == installment['due_date']):
                found.append(dict(flow_id=f.flow_id, evidence_state=f.evidence_state,
                                  due_date_evidenced=f.due_date_evidenced,
                                  source_ref=f.source_ref, source_refs=item.get('source_refs',[])))
        found.sort(key=lambda item:item['flow_id'])
        result['rows'].append(dict(sequence=installment['sequence'],
            component=installment['component'], amount=installment['amount'],
            currency=plan['currency'], due_date=installment['due_date'],
            status='NO_EXACT_CANDIDATE' if not found else 'ONE_EXACT_CANDIDATE' if len(found)==1 else 'MULTIPLE_EXACT_CANDIDATES',
            candidates=found, shared_candidate_ids=[]))
    usage = Counter(c['flow_id'] for row in result['rows'] for c in row['candidates'])
    for row in result['rows']:
        row['shared_candidate_ids'] = [c['flow_id'] for c in row['candidates'] if usage[c['flow_id']] > 1]
    result['status'] = 'PARTIAL_INVENTORY' if result['issues'] else 'CANDIDATES_LISTED'
    result['message'] = ('Coincidir en importe, moneda y fecha no demuestra que un pago corresponda a esta compra. '
                         'Sin coincidencia tampoco se acredita que el pago sea nuevo. '
                         'No se han asociado ni añadido movimientos a la proyección.')
    return finish()
