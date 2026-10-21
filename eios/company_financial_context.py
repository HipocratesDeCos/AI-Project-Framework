"""Capture existing documentary financial carriers without promoting evidence."""
from hashlib import sha256
import json

from pydantic import ValidationError
from eios.finance.models import CashFlow, FinancialSnapshot, WorkingCapitalInput


def financial_context(store, dataset, info):
    issues = []
    kinds = ('financial_snapshot', 'working_capital', 'cash_flow', 'treasury_balances',
             'account_balance', 'bank_statement_entry', 'cash_count', 'daily_treasury_forecast')
    records = {kind: list(store.records(dataset, kind)) for kind in kinds}
    snapshot = None
    capital = None
    snapshots = records['financial_snapshot']
    if len(snapshots) != 1:
        issues.append('Debe vincularse una única situación financiera de esta versión.')
    else:
        try:
            model = FinancialSnapshot.model_validate(snapshots[0]['data'])
            snapshot = model.model_dump(mode='json')
            if model.company_scope != info['company']['company_id'] or model.as_of_date.isoformat() != info['as_of_date']:
                issues.append('La situación financiera no coincide con la empresa o fecha de corte.')
            if model.available_treasury is None:
                issues.append('La situación financiera no contiene un importe de tesorería disponible; revisar los soportes de caja/bancos ya cargados.')
        except (ValidationError, KeyError, TypeError):
            issues.append('La situación financiera requiere corregir su vínculo o formato canónico.')
    if len(records['working_capital']) == 1:
        try:
            model = WorkingCapitalInput.model_validate(records['working_capital'][0]['data'])
            capital = model.model_dump(mode='json')
            if model.company_scope != info['company']['company_id'] or model.as_of_date.isoformat() != info['as_of_date']:
                issues.append('Las magnitudes del balance no coinciden con la empresa o corte.')
            if snapshot and model.currency != snapshot['currency']:
                issues.append('La moneda de las magnitudes del balance difiere de la situación financiera.')
        except (ValidationError, KeyError, TypeError):
            issues.append('Las magnitudes del balance requieren corregir su formato canónico.')
    else:
        issues.append('Las magnitudes de activo/pasivo corriente no están vinculadas de forma única.')
    flows = []
    ids = set()
    for record in records['cash_flow']:
        try:
            flow = CashFlow.model_validate(record['data']['canonical'])
            if flow.flow_id != record['record_id']:
                issues.append('Un movimiento tiene una identidad distinta de su registro documental.')
            if flow.flow_id in ids:
                issues.append('Se ha detectado una identidad de movimiento duplicada; revisar antes de proyectar.')
            ids.add(flow.flow_id)
            if snapshot and flow.currency and flow.currency != snapshot['currency']:
                issues.append('Existen movimientos con moneda distinta de la situación financiera.')
            flows.append(dict(record_id=record['record_id'], canonical=flow.model_dump(mode='json'),
                              source_refs=record.get('source_refs', [])))
        except (ValidationError, KeyError, TypeError):
            issues.append('Un movimiento de tesorería requiere corregir su formato canónico.')
    if not records['cash_flow']:
        issues.append('No hay movimientos canónicos de cobro/pago vinculados a esta versión.')
    pending = sum(item['canonical']['evidence_state'] != 'DEMONSTRATED' for item in flows)
    if pending:
        issues.append('Hay movimientos documentales cuya evidencia todavía no está validada para el motor financiero.')
    flows.sort(key=lambda item: (item['canonical']['due_date'] or '9999-12-31', item['record_id']))
    # These are integration gaps, not assertions that the user's files are absent.
    integration_pending = [
        'Conectar horizonte y mínimo de tesorería vigentes desde el Centro de Parametrización.',
        'Comprobar suficiencia y conciliación del saldo inicial y del inventario completo de cobros/pagos.',
        'Vincular pagos y cuotas de esta propuesta sin duplicarlos con movimientos existentes.',
        'Completar paquete de entrada, calidad y ejecución financiera antes de emitir viabilidad.',
    ]
    result = dict(schema='COMPANY-DOCUMENTARY-FINANCE-CONTEXT-01',
                  dataset_id=dataset, company_id=info['company']['company_id'],
                  as_of_date=info['as_of_date'], financial_snapshot=snapshot,
                  working_capital_input=capital, cash_flows=flows,
                  record_counts={kind:len(items) for kind,items in records.items()},
                  source_records=records, issues=list(dict.fromkeys(issues)),
                  integration_pending=integration_pending, status='DOCUMENTARY_INPUTS_LINKED',
                  execution_status='NOT_EXECUTED', viability_status='NOT_EVALUATED',
                  evidence_pending_count=pending, cash_flow_inventory_complete=None,
                  opening_treasury_reconciled=None, decision_authority=False, operational_path='FORBIDDEN')
    result['fingerprint'] = sha256(json.dumps(result,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
    return result
