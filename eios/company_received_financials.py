"""Read-only received cash flows and account balances, without solvency conclusions."""
from collections import defaultdict
from decimal import Decimal, localcontext
import json

from eios.company_dossier import selected_batches


def exact_total(values):
    amounts = [Decimal(value) for value in values]
    # Retain documented decimal places rather than rounding at the default precision.
    with localcontext() as context:
        context.prec = max(len(x.as_tuple().digits) + abs(x.as_tuple().exponent) for x in amounts) + len(str(len(amounts))) + 5
        return format(sum(amounts, Decimal(0)), 'f')


def received_financials(db, batch_ids):
    batches = selected_batches(db, batch_ids)
    metadata = batches[0][1]
    result = {key:metadata[key] for key in ('company_id', 'legal_name', 'material_nature', 'as_of_date')}
    flows, balances, support = [], [], []
    for bid, meta, records in batches:
        if meta['kind'] == 'document':
            support.append(dict(batch_id=bid, filename=meta['filename']))
        for record in records:
            if record['kind'] not in ('cash_flow', 'balance'):
                continue
            entry = dict(data=record['data'], source=dict(batch_id=bid, filename=meta['filename'], sheet=meta['sheet'], row=record['source_row']))
            (flows if record['kind'] == 'cash_flow' else balances).append(entry)
    references = defaultdict(list)
    for entry in flows:
        references[entry['data']['flow_id']].append(entry)
    for entries in references.values():
        variants = {json.dumps(entry['data'], sort_keys=True) for entry in entries}
        status = 'UNIQUE_REFERENCE' if len(entries) == 1 else 'CONFLICTING_REFERENCE' if len(variants) > 1 else 'REPEATED_REFERENCE'
        for entry in entries:
            entry['reference_status'] = status
            entry['maturity'] = 'BY_CUTOFF' if entry['data']['due_date'] <= metadata['as_of_date'] else 'AFTER_CUTOFF'
    groups = defaultdict(list)
    for entry in flows:
        d = entry['data']
        groups[(d['currency'], d['direction'], entry['maturity'])].append(entry)
    summaries = []
    for (currency, direction, maturity), entries in sorted(groups.items()):
        ambiguous = any(entry['reference_status'] != 'UNIQUE_REFERENCE' for entry in entries)
        summaries.append(dict(currency=currency, direction=direction, maturity=maturity,
            row_count=len(entries), status='AMBIGUOUS_REFERENCES' if ambiguous else 'DOCUMENTED_SUM',
            amount=None if ambiguous else exact_total([entry['data']['amount'] for entry in entries])))
    accounts = defaultdict(list)
    for entry in balances:
        accounts[(entry['data']['account_code'], entry['data']['currency'])].append(entry)
    account_summaries = []
    for (account, currency), entries in sorted(accounts.items()):
        variants = {json.dumps(entry['data'], sort_keys=True) for entry in entries}
        status = 'DOCUMENTED_BALANCE' if len(entries) == 1 else 'CONFLICTING_BALANCE' if len(variants) > 1 else 'REPEATED_BALANCE'
        account_summaries.append(dict(account_code=account, currency=currency, status=status,
            balance=entries[0]['data']['balance'] if len(entries) == 1 else None,
            sources=[entry['source'] for entry in entries]))
        for entry in entries:
            entry['reference_status'] = status
    flows.sort(key=lambda entry:(entry['data']['due_date'],entry['data']['flow_id'],entry['source']['batch_id'],entry['source']['row']))
    balances.sort(key=lambda entry:(entry['data']['account_code'],entry['data']['currency'],entry['source']['batch_id'],entry['source']['row']))
    result.update(batch_ids=sorted(batch_ids), flows=flows, flow_summaries=summaries, balances=balances,
        account_summaries=account_summaries, support_documents=support,
        source_warning_count=sum(meta.get('warning_count', 0) for _,meta,_ in batches),
        admission_status='PENDING', operational_path='FORBIDDEN', decision_authority=False,
        scope='Consulta de los archivos seleccionados, pendientes de admisión. Los vencimientos no acreditan que un importe siga pendiente de pago o cobro. Las sumas son nominales, separadas por moneda y sentido; no son una previsión de liquidez ni determinan capacidad de compra. Los saldos se consultan por cuenta, sin sumar cuentas padre e hijas ni conciliarlos con movimientos o PDFs.')
    return result
