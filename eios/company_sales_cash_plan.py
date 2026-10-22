"""Explicit cash schedules for saved synthetic offers; no duplicate collections."""
from datetime import date, datetime, time, timezone
from dataclasses import asdict
from decimal import Decimal
import json
import sqlite3
from uuid import uuid4

from eios.company_sales_proposals import offers, text
from eios.company_commercial_terms import number
from eios.company_proposal_context import capture_context
from eios.company_payment_review import _fingerprint
from eios.company_finance_parameters import SCHEMA as FINANCE_SCHEMA, Catalogue, Authorization, Repository, IDS
from eios.parameters.center import ParameterConfigurationCenter
from eios.parameters import resolve_configuration_for_context
from eios.core.models import DecisionContext
from eios.finance.models import CashFlow, FinancialSnapshot, FinanceBasicInput, WorkingCapitalInput
from eios.finance.provenance import run_provenanced_finance_basic

SCHEMA = '''CREATE TABLE IF NOT EXISTS company_sales_cash_plan (
dataset_id TEXT NOT NULL,proposal_id TEXT NOT NULL,revision INTEGER NOT NULL,
fingerprint TEXT NOT NULL,payload TEXT NOT NULL,PRIMARY KEY(dataset_id,proposal_id,revision))'''


def _latest(c, dataset, proposal):
    row=c.execute('SELECT revision,fingerprint,payload FROM company_sales_cash_plan WHERE dataset_id=? AND proposal_id=? ORDER BY revision DESC LIMIT 1',(dataset,proposal)).fetchone()
    if row is None:return None
    payload=json.loads(row[2])
    if _fingerprint(payload)!=row[1]:raise ValueError('El plan conservado no coincide con su huella.')
    return row[0],row[1],payload


def offer_for(db,dataset,proposal):
    offer=next((p for p in offers(db,dataset) if p['proposal_id']==proposal),None)
    if offer is None:raise ValueError('Oferta no encontrada en esta versión.')
    return offer


def read_plan(db,state,proposal):
    offer=offer_for(db,state['documentary_context']['dataset_id'],proposal)
    with sqlite3.connect(db) as c:
        c.execute(SCHEMA)
        latest=_latest(c,offer['dataset_id'],proposal)
    if latest and latest[2]['offer_fingerprint']!=_fingerprint(offer):
        raise ValueError('La oferta guardada no coincide con el plan conservado.')
    current=offer['documentary_context']['fingerprint']==state['documentary_context']['fingerprint']
    return dict(offer=offer,revision=latest[0] if latest else 0,fingerprint=latest[1] if latest else None,
        plan=latest[2] if latest else None,can_edit=current,
        documentary_context_fingerprint=state['documentary_context']['fingerprint'],
        documented_flows=state['sales_financial_context']['cash_flows'])


def _execute(c,offer,finance,rows):
    result=dict(status='NOT_EXECUTED',message='Activa horizonte y tesorería mínima para este corte en Parámetros.',
        baseline=None,with_declared_plan=None,viability_status='NOT_EVALUATED',
        evidence_upgrade_status='NOT_PERFORMED',decision_authority=False,operational_path='FORBIDDEN')
    try:
        raw=finance.get('financial_snapshot')
        if raw is None:raise ValueError('Falta una situación financiera canónica única.')
        snapshot=FinancialSnapshot.model_validate(raw)
        if (snapshot.company_scope!=finance['company_id'] or snapshot.as_of_date.isoformat()!=finance['as_of_date']
                or snapshot.currency!='EUR'):raise ValueError('La situación financiera no coincide con empresa, corte o moneda.')
        flows=tuple(CashFlow.model_validate(f['canonical']) for f in finance['cash_flows'])
        if (not flows or len(flows)!=finance['record_counts']['cash_flow']
                or any(f.flow_id!=r['record_id'] for f,r in zip(flows,finance['cash_flows']))):
            raise ValueError('No se ejecuta un inventario vacío, parcial o con identidades inconsistentes.')
        effective=datetime.combine(snapshot.as_of_date,time.min,timezone.utc)
        center=ParameterConfigurationCenter(Catalogue(),Authorization(),Repository(c))
        configs=[center.get_configuration_at(snapshot.company_scope,key,effective) for key in IDS]
        if any(config is None for config in configs):return result
        selected=[asdict(config) for config in configs]
        serial=json.loads(json.dumps(selected,default=lambda x:x.isoformat()))
        version=_fingerprint(serial)
        context=DecisionContext(decision_id=offer['proposal_id'],scenario_id='SALES-DECLARED-CASH-PLAN',
            rules_version='NOT_EXECUTED',parameters_version=version,data_snapshot_id=snapshot.data_snapshot_id)
        horizon=resolve_configuration_for_context(configs[0],context,effective)
        capital=WorkingCapitalInput.model_validate(finance['working_capital_input']) if finance.get('working_capital_input') else None
        base=FinanceBasicInput(context=context,snapshot=snapshot,cash_flows=flows,
            horizon_days=int(Decimal(configs[0].value)),treasury_minimum=configs[1].value,working_capital_input=capital)
        prospective=tuple(CashFlow(flow_id=r['flow_id'],flow_type=r['flow_type'],amount=r['amount'],currency='EUR',
            due_date=r['due_date'],due_date_evidenced=False,source_ref=r['declaration_ref'],evidence_state='NOT_EVIDENCED')
            for r in rows if r['disposition']=='NEW_DECLARATION')
        combined=FinanceBasicInput(**dict(base.model_dump(mode='python'),cash_flows=flows+prospective))
        before=run_provenanced_finance_basic(base,horizon)
        after=run_provenanced_finance_basic(combined,horizon)
        result.update(status='EXECUTED',baseline=before.finance_result.model_dump(mode='json'),
            with_declared_plan=after.finance_result.model_dump(mode='json'),finance_input=combined.model_dump(mode='json'),
            parameter_configurations=serial,horizon_configuration_ref=horizon.configuration_ref,
            new_flow_count=len(prospective),reused_flow_count=sum(r['disposition']=='ALREADY_DOCUMENTED' for r in rows),
            message='Motor financiero ejecutado con los flujos conservados y las declaraciones nuevas sin validar. Los movimientos ya documentados no se añaden otra vez. Calidad, conciliación y completitud siguen pendientes.')
    except (ValueError,TypeError,KeyError,ArithmeticError) as error:
        result['message']='Ejecución pendiente: '+str(error)
    return result


def save_plan(db,state,data):
    dataset=state['documentary_context']['dataset_id']
    proposal=text(data.get('proposal_id'),'oferta',128)
    offer=offer_for(db,dataset,proposal)
    actor=text(data.get('actor'),'responsable del plan',128)
    if data.get('acknowledge') is not True:
        raise ValueError('Confirma que los cobros y costes son declaraciones pendientes de validar.')
    if (offer['documentary_context']['material_nature']!='SYNTHETIC'
            or data.get('documentary_context_fingerprint')!=state['documentary_context']['fingerprint']
            or offer['documentary_context']['fingerprint']!=state['documentary_context']['fingerprint']):
        raise ValueError('La documentación de la oferta ha cambiado. Crea una oferta con el contexto actual.')
    raw=data.get('rows')
    if not isinstance(raw,list) or not 1<=len(raw)<=30:raise ValueError('Declara entre 1 y 30 movimientos.')
    rows=[];used=set();collection=Decimal(0);plan_ref='SALES-PLAN-'+str(uuid4())
    existing={f['record_id']:f for f in state['sales_financial_context']['cash_flows']}
    for index,item in enumerate(raw):
        if not isinstance(item,dict):raise ValueError('Movimiento inválido.')
        kind=item.get('flow_type');disposition=item.get('disposition')
        if kind not in ('COLLECTION','PAYMENT') or disposition not in ('NEW_DECLARATION','ALREADY_DOCUMENTED'):
            raise ValueError('Selecciona tipo y presencia en la previsión.')
        amount=number(item,'amount')
        if amount<=0 or amount!=amount.quantize(Decimal('.01')):raise ValueError('Cada importe debe ser positivo con dos decimales.')
        try:due=date.fromisoformat(item['due_date'])
        except (KeyError,TypeError,ValueError):raise ValueError('Indica un vencimiento válido.') from None
        if due.isoformat()<=state['info']['as_of_date'] or due.isoformat()<offer['offer_date']:
            raise ValueError('El movimiento debe ser posterior al corte y no preceder a la oferta.')
        note=text(item.get('note'),'concepto y fundamento del movimiento')
        refs=[];linked=None
        if disposition=='ALREADY_DOCUMENTED':
            linked=item.get('existing_flow_id');found=existing.get(linked)
            if found is None or linked in used:raise ValueError('Movimiento documentado ausente o repetido en el plan.')
            f=found['canonical']
            if (f['flow_type']!=kind or f['currency']!='EUR' or f['due_date']!=due.isoformat()
                    or f['amount'] is None or Decimal(f['amount'])!=amount):
                raise ValueError('El movimiento debe coincidir exactamente en tipo, moneda, importe y fecha.')
            used.add(linked);refs=found['source_refs']
        elif item.get('existing_flow_id') not in (None,''):
            raise ValueError('Un movimiento nuevo no puede declarar una vinculación existente.')
        matches=[]
        if disposition=='NEW_DECLARATION':
            matches=[key for key,value in existing.items() if value['canonical']['flow_type']==kind
                and value['canonical'].get('currency')=='EUR' and value['canonical'].get('due_date')==due.isoformat()
                and value['canonical'].get('amount') is not None and Decimal(value['canonical']['amount'])==amount]
            if matches and item.get('separate_movement_acknowledged') is not True:
                raise ValueError('Hay movimientos coincidentes en la previsión: '+', '.join(matches)+'. Vincula el existente o declara expresamente que es otro movimiento, explicándolo en el concepto.')
        if kind=='COLLECTION':collection+=amount
        rows.append(dict(flow_type=kind,amount=str(amount),currency='EUR',due_date=due.isoformat(),
            disposition=disposition,existing_flow_id=linked,flow_id=linked or plan_ref+'#'+str(index+1),
            note=note,source_refs=refs,coincident_existing_flow_ids=matches,
            separate_movement_acknowledged=item.get('separate_movement_acknowledged') is True,declaration_ref=plan_ref+'#'+str(index+1)))
    if collection!=Decimal(offer['total']):
        raise ValueError('Los cobros declarados deben sumar exactamente el total con IVA de la oferta.')
    with sqlite3.connect(db) as c:
        c.execute(SCHEMA)
        c.executescript(FINANCE_SCHEMA)
        c.execute('BEGIN IMMEDIATE')
        current=_latest(c,dataset,proposal)
        revision=current[0] if current else 0
        if type(data.get('revision')) is not int or data['revision']!=revision:
            raise ValueError('El plan ha cambiado. Vuelve a abrirlo.')
        if capture_context(c,dataset)['fingerprint']!=state['documentary_context']['fingerprint']:
            raise ValueError('La documentación ha cambiado. Recarga la pantalla.')
        other=c.execute('SELECT proposal_id,MAX(revision) FROM company_sales_cash_plan WHERE dataset_id=? AND proposal_id<>? GROUP BY proposal_id',(dataset,proposal)).fetchall()
        for other_id,_ in other:
            latest=_latest(c,dataset,other_id)
            linked={r['existing_flow_id'] for r in latest[2]['rows'] if r['existing_flow_id']}
            if used & linked:raise ValueError('Un movimiento ya está vinculado al plan vigente de otra oferta de esta versión.')
        payload=dict(schema='SALES-CASH-PLAN-01',plan_ref=plan_ref,dataset_id=dataset,proposal_id=proposal,
            offer_fingerprint=_fingerprint(offer),revision=revision+1,actor=actor,
            created_at=datetime.now(timezone.utc).isoformat(),rows=rows,
            documentary_context_fingerprint=state['documentary_context']['fingerprint'],
            financial_context=state['sales_financial_context'],
            execution=_execute(c,offer,state['sales_financial_context'],rows),
            cost_inventory_status='COMPLETENESS_NOT_ESTABLISHED',identity_status='LOCAL_ACTOR_NOT_AUTHENTICATED',
            decision_authority=False,operational_path='FORBIDDEN',viability_status='NOT_EVALUATED')
        fingerprint=_fingerprint(payload)
        c.execute('INSERT INTO company_sales_cash_plan VALUES(?,?,?,?,?)',(dataset,proposal,revision+1,fingerprint,json.dumps(payload,ensure_ascii=False,sort_keys=True,separators=(',',':'))))
    return dict(revision=revision+1,fingerprint=fingerprint,plan=payload)
