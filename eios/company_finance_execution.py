"""Execute documentary cash-flow analytics using cutoff-bound Centre parameters."""
from datetime import date, datetime, time, timezone
from hashlib import sha256
from decimal import Decimal
import json
import sqlite3

from pydantic import ValidationError
from eios.core.models import DecisionContext, PurchaseOperation
from eios.core.finance_decision_input_package import build_finance_decision_input_package
from eios.finance.models import FinanceBasicInput, FinancialSnapshot, CashFlow, WorkingCapitalInput
from eios.finance.provenance import run_provenanced_finance_basic
from eios.parameters.center import ParameterConfigurationCenter
from eios.company_finance_parameters import Catalogue,Authorization,Repository,SCHEMA,IDS
from eios.company_finance_activation_guard import (
    LocalFinanceActivationError, verify_local_finance_activation,
)
from eios.company_cash_flow_inventory_guard import (
    CashFlowInventoryError, verify_local_cash_flow_inventory,
)
from eios.company_flow_documentary_coverage import (
    audit_local_flow_documentary_coverage,
)


def execute_documentary_finance(db,proposal,documentary,associations=None):
    result=dict(schema='COMPANY-DOCUMENTARY-FINANCE-EXECUTION-01',
        scope='SUPPLIED_DOCUMENTARY_CASH_FLOWS_ONLY',status='NOT_EXECUTED',
        message='Activa el horizonte y la tesorería mínima para este corte desde Parámetros.',
        documentary_capture=dict(status='NOT_CAPTURED',message='Faltan los requisitos de ejecución financiera o las asociaciones declaradas.'),
        limitations=[],finance_result=None,parameter_configurations=[],
        parameter_source_status='NOT_VERIFIED',parameter_activation_ref=None,
        cash_flow_inventory_status='NOT_VERIFIED',
        flow_documentary_coverage=dict(status='NOT_AUDITED',
            documentary_content_review='NOT_PERFORMED',
            invoice_and_bank_reconciliation='NOT_PERFORMED',
            decision_authority=False,operational_path='FORBIDDEN'),
        purchase_effect_status='NOT_EVALUATED',viability_status='NOT_EVALUATED',
        decision_authority=False,operational_path='FORBIDDEN')
    def finish():
        result['fingerprint']=sha256(json.dumps(result,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
        return result
    if documentary['financial_snapshot'] is None:
        result['message']='Falta una situación financiera canónica única para ejecutar la proyección; revisa los soportes ya vinculados.'
        return finish()
    try:
        if proposal['dataset_id']!=documentary['dataset_id']:
            raise ValueError('La propuesta y los datos financieros pertenecen a versiones distintas.')
        snapshot=FinancialSnapshot.model_validate(documentary['financial_snapshot'])
        if snapshot.company_scope!=documentary['company_id'] or snapshot.as_of_date.isoformat()!=documentary['as_of_date']:
            raise ValueError('La situación financiera pertenece a otra empresa o fecha de corte.')
        effective=datetime.combine(snapshot.as_of_date,time.min,timezone.utc)
        with sqlite3.connect(db) as c:
            c.executescript(SCHEMA)
            c.execute('BEGIN')
            row=c.execute('SELECT company_id,manifest_json FROM documentary_company_snapshot WHERE dataset_id=?',(documentary['dataset_id'],)).fetchone()
            if row is None or row[0]!=snapshot.company_scope or json.loads(row[1]).get('material_nature')!='SYNTHETIC':
                raise ValueError('Esta ejecución local solo admite material sintético; no acredita admisión operacional.')
            center=ParameterConfigurationCenter(Catalogue(),Authorization(),Repository(c))
            configs=[center.get_configuration_at(snapshot.company_scope,key,effective) for key in IDS]
            if any(item is None for item in configs):
                return finish()
            admission=verify_local_finance_activation(
                connection=c,company_id=snapshot.company_scope,
                dataset_id=documentary['dataset_id'],
                as_of_date=documentary['as_of_date'],effective_at=effective,
                configurations=tuple(configs),
            )
            result['parameter_source_status']=admission.status
            result['parameter_activation_ref']=admission.activation_fingerprint
            selected=[{key:value.isoformat() if isinstance(value,datetime) else value for key,value in item.__dict__.items()} for item in configs]
            version=sha256(json.dumps(selected,sort_keys=True,separators=(',',':')).encode()).hexdigest()
            context=DecisionContext(decision_id=proposal['proposal_id'],scenario_id='DOCUMENTARY-CASH-FLOWS',
                rules_version='NOT_EXECUTED',parameters_version=version,data_snapshot_id=snapshot.data_snapshot_id)
            purchase=PurchaseOperation(decision_id=context.decision_id,scenario_id=context.scenario_id,
                article_id=proposal['article_id'],supplier_id=proposal['supplier_id'],quantity=proposal['quantity'],
                unit_price=proposal['unit_price'],currency=proposal['currency'],operation_date=proposal['order_date'])
            flows, inventory_receipt = verify_local_cash_flow_inventory(
                connection=c, dataset_id=documentary['dataset_id'],
                recorded_count=documentary['record_counts']['cash_flow'],
                captured_flows=documentary['cash_flows'],
            )
            result['cash_flow_inventory_status']=inventory_receipt.status
            result['cash_flow_inventory_fingerprint']=inventory_receipt.recorded_fingerprint
            # Check evidence coverage only after F3.8 confirms the full source
            # inventory. A byte match never confirms the content of invoices
            # or promotes the declared evidence state.
            result['flow_documentary_coverage']=audit_local_flow_documentary_coverage(
                connection=c, dataset_id=documentary['dataset_id'],
                flows=flows, captured_flows=documentary['cash_flows'],
                proposal_context=proposal.get('documentary_context_at_save'),
            )
            capital=WorkingCapitalInput.model_validate(documentary['working_capital_input']) if documentary['working_capital_input'] else None
            # The low-level engine can label a foreign balance NOT_EVALUABLE,
            # but this company documentary consumer must not publish an
            # EXECUTED package assembled from another company/cutoff/currency.
            if capital is not None and (
                capital.company_scope != snapshot.company_scope
                or capital.as_of_date != snapshot.as_of_date
                or capital.currency != snapshot.currency
            ):
                raise ValueError('Las magnitudes del balance no corresponden a la empresa, fecha o moneda de la situación financiera.')
            finance=FinanceBasicInput(context=context,snapshot=snapshot,cash_flows=flows,
                horizon_days=int(Decimal(configs[0].value)),treasury_minimum=configs[1].value,working_capital_input=capital)
            package=build_finance_decision_input_package(purchase=purchase,context=context,evidence=(),
                finance_input=finance,company_id=snapshot.company_scope,effective_at=effective,
                requested_parameter_ids=IDS,center=center)
            from eios.company_payment_capture import capture_listed_payments
            result['documentary_capture']=capture_listed_payments(c,package,proposal,associations)
        execution=run_provenanced_finance_basic(package.finance_input,package.horizon_resolution)
        output=execution.finance_result.model_dump(mode='json')
        result.update(status='EXECUTED',finance_result=output,
                      parameter_configurations=selected,
                      finance_package_fingerprint=package.fingerprint,
                      parameter_version=context.parameters_version,
                      finance_input=package.finance_input.model_dump(mode='json'))
        result['message']=('Proyección de los movimientos documentados calculada. El efecto de la nueva compra todavía no se ha incorporado.'
                           if output['projection']['status']=='DETERMINED' else
                           'Motor financiero ejecutado: la proyección no es determinable con el estado actual de los datos. Se conserva su validación documental.')
        result['limitations']=['No se ha comprobado conciliación ni completitud del inventario de flujos.',
            'No se ha establecido qué flujos corresponden a esta propuesta ni incorporado sus pagos y cuotas.',
            'No se ha ejecutado QTG, Rules ni el decisor: esta salida no acredita viabilidad de compra.']
    except CashFlowInventoryError as error:
        result['cash_flow_inventory_status']='REJECTED'
        result['cash_flow_inventory_issue']=error.code
        result['message']='El inventario de cobros y pagos no coincide con los registros conservados: '+str(error)
        result['limitations']=['No se publica un cálculo basado en un inventario incompleto o modificado. La conciliación contable sigue pendiente.']
    except LocalFinanceActivationError as error:
        result['parameter_source_status']='REJECTED'
        result['parameter_source_issue']=error.code
        result['message']='No se utilizan los parámetros financieros: '+str(error)
        result['limitations']=['La selección no coincide con la activación local sintética registrada. No se publica un cálculo parcial.']
    except (ValueError,TypeError,KeyError,ArithmeticError) as error:
        result['message']='No se ha podido ejecutar la proyección financiera: '+str(error)
        result['limitations']=['Revisar el contrato de datos o parámetros indicado; no se publica un cálculo parcial.']
    return finish()
