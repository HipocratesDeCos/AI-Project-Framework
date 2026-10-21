"""Local synthetic financial activation through the existing Parameter Centre."""
from dataclasses import asdict
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal, InvalidOperation
from hashlib import sha256
import json
import sqlite3

from eios.parameters.center import (ParameterConfigurationCenter, ParameterDefinition,
    Configuration, HistoryEntry, ChangeRequest, ParameterConfigurationError)

IDS=('P-FIN-001','P-FIN-002')
SCHEMA="""
CREATE TABLE IF NOT EXISTS company_finance_parameter_configuration (
 configuration_id INTEGER PRIMARY KEY AUTOINCREMENT, parameter_id TEXT NOT NULL,
 company_id TEXT NOT NULL, value TEXT NOT NULL, value_type TEXT, unit TEXT,
 valid_from TEXT NOT NULL, valid_to TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS company_finance_parameter_history (
 configuration_id INTEGER NOT NULL, parameter_id TEXT NOT NULL, company_id TEXT NOT NULL,
 previous_value TEXT, new_value TEXT NOT NULL, changed_by TEXT NOT NULL,
 changed_at TEXT NOT NULL, change_reason TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS company_finance_parameter_activation (
 company_id TEXT NOT NULL, as_of_date TEXT NOT NULL, payload TEXT NOT NULL,
 PRIMARY KEY(company_id,as_of_date));
"""


def _number(value, positive=False):
    try:
        value=Decimal(value)
        if not value.is_finite() or value<0 or (positive and (value<=0 or value!=value.to_integral_value())):
            raise ValueError()
        return None
    except (ValueError,TypeError,InvalidOperation):
        return 'INVALID_VALUE'


class Catalogue:
    def get_parameter(self, parameter_id):
        if parameter_id not in IDS:
            return None
        horizon=parameter_id==IDS[0]
        return ParameterDefinition(parameter_id, 'INTEGER' if horizon else 'DECIMAL',
            'días' if horizon else 'EUR', lambda value:_number(value,horizon), restricted=True)


class Authorization:
    def __init__(self, company=None, actor=None):
        self.company,self.actor=company,actor
    def can_modify(self, company_id, parameter_id, actor):
        return self.company is not None and company_id==self.company and actor==self.actor and parameter_id in IDS


class Repository:
    def __init__(self, connection):
        self.connection=connection

    def get_at(self, company_id, parameter_id, effective_at):
        rows=self.connection.execute('SELECT * FROM company_finance_parameter_configuration WHERE company_id=? AND parameter_id=?',
                                     (company_id,parameter_id)).fetchall()
        found=[]
        for row in rows:
            item=Configuration(*row[:6],*(datetime.fromisoformat(value) if value else None for value in row[6:]))
            if item.valid_from<=effective_at and (item.valid_to is None or effective_at<item.valid_to):
                found.append(item)
        if len(found)>1:
            raise ParameterConfigurationError('CONFLICTING_ACTIVE_CONFIGURATION','Configuraciones solapadas.')
        return found[0] if found else None

    def get_current(self, company_id, parameter_id):
        return self.get_at(company_id,parameter_id,datetime.now(timezone.utc))

    def get_history(self, company_id, parameter_id):
        rows=self.connection.execute('SELECT * FROM company_finance_parameter_history WHERE company_id=? AND parameter_id=? ORDER BY changed_at,configuration_id',
                                     (company_id,parameter_id)).fetchall()
        return tuple(HistoryEntry(*row[:6],datetime.fromisoformat(row[6]),row[7]) for row in rows)

    def has_overlapping_configuration(self,company_id,parameter_id,valid_from,valid_to):
        rows=self.connection.execute('SELECT valid_from,valid_to FROM company_finance_parameter_configuration WHERE company_id=? AND parameter_id=?',
                                     (company_id,parameter_id)).fetchall()
        return any((valid_to is None or datetime.fromisoformat(start)<valid_to) and
                   (end is None or valid_from<datetime.fromisoformat(end)) for start,end in rows)

    def apply_change_atomically(self, request):
        # The caller owns one BEGIN IMMEDIATE transaction for the entire pair.
        if not self.connection.in_transaction:
            raise ValueError('La escritura requiere una transacción explícita.')
        if self.has_overlapping_configuration(request.company_id,request.parameter_id,request.valid_from,request.valid_to):
            raise ParameterConfigurationError('CONFLICTING_ACTIVE_CONFIGURATION','Ya existe configuración para esta vigencia.')
        definition=Catalogue().get_parameter(request.parameter_id)
        if definition is None or definition.validate_value(request.value):
            raise ValueError('Configuración no válida.')
        now=datetime.now(timezone.utc)
        previous=self.get_at(request.company_id,request.parameter_id,request.valid_from)
        cursor=self.connection.execute('INSERT INTO company_finance_parameter_configuration(parameter_id,company_id,value,value_type,unit,valid_from,valid_to,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?)',
            (request.parameter_id,request.company_id,request.value,definition.value_type,definition.unit,
             request.valid_from.isoformat(),request.valid_to.isoformat() if request.valid_to else None,now.isoformat(),now.isoformat()))
        configuration=Configuration(cursor.lastrowid,request.parameter_id,request.company_id,request.value,
            definition.value_type,definition.unit,request.valid_from,request.valid_to,now,now)
        self.connection.execute('INSERT INTO company_finance_parameter_history VALUES(?,?,?,?,?,?,?,?)',
            (configuration.configuration_id,request.parameter_id,request.company_id,previous.value if previous else None,
             request.value,request.actor,now.isoformat(),request.reason))
        return configuration


def read_finance_activation(db,company,cutoff):
    with sqlite3.connect(db) as c:
        c.executescript(SCHEMA)
        row=c.execute('SELECT payload FROM company_finance_parameter_activation WHERE company_id=? AND as_of_date=?',
                      (company,cutoff)).fetchone()
    return json.loads(row[0]) if row else None


def activate_finance_parameters(db,store,data):
    from eios.company_parameters import read_parameters
    dataset=data['dataset_id']
    info=store.describe(dataset)
    read_parameters(db,store,dataset)
    company=info['company']['company_id']
    actor=data.get('actor')
    reason=data.get('reason')
    if not isinstance(actor,str) or not actor.strip() or len(actor)>128 or not isinstance(reason,str) or not reason.strip() or len(reason)>512:
        raise ValueError('Indica responsable y motivo de la activación.')
    if data.get('acknowledge') is not True:
        raise ValueError('Confirma expresamente la activación para esta empresa y fecha de corte.')
    if type(data.get('revision')) is not int:
        raise ValueError('Recarga la revisión de parámetros.')
    start=datetime.combine(date.fromisoformat(info['as_of_date']),time.min,timezone.utc)
    end=start+timedelta(days=1)
    with sqlite3.connect(db) as c:
        c.executescript(SCHEMA)
        c.execute('BEGIN IMMEDIATE')
        row=c.execute('SELECT company_id,as_of_date,manifest_json FROM documentary_company_snapshot WHERE dataset_id=?',(dataset,)).fetchone()
        if row is None or row[0]!=company or row[1]!=info['as_of_date'] or json.loads(row[2]).get('material_nature')!='SYNTHETIC':
            raise ValueError('Esta activación local solo está habilitada para la empresa sintética y corte seleccionados.')
        selected=c.execute('SELECT revision,payload FROM company_parameter_request WHERE company_id=? ORDER BY revision DESC LIMIT 1',(company,)).fetchone()
        if selected is None or selected[0]!=data['revision']:
            raise ValueError('La configuración preparada ha cambiado. Recarga antes de activar.')
        request=json.loads(selected[1])
        if not request.get('critical_acknowledged'):
            raise ValueError('Falta la revisión expresa de los parámetros financieros preparados.')
        values=request['values']
        if not all(key in values for key in IDS):
            raise ValueError('Prepara y guarda horizonte financiero y tesorería mínima antes de activar.')
        if _number(values[IDS[0]],True) or _number(values[IDS[1]]):
            raise ValueError('Los valores financieros no cumplen el catálogo.')
        try:
            date.fromisoformat(info['as_of_date'])+timedelta(days=int(Decimal(values[IDS[0]])))
        except (OverflowError,ValueError):
            raise ValueError('El horizonte excede el calendario representable.') from None
        previous=c.execute('SELECT payload FROM company_finance_parameter_activation WHERE company_id=? AND as_of_date=?',(company,info['as_of_date'])).fetchone()
        if previous:
            existing=json.loads(previous[0])
            if existing['values']!={key:values[key] for key in IDS}:
                raise ValueError('Este corte ya tiene una activación conservada. No se sobrescribe su histórico; la solicitud modificada queda pendiente.')
        else:
            center=ParameterConfigurationCenter(Catalogue(),Authorization(company,actor.strip()),Repository(c))
            configs=[center.apply_change(ChangeRequest(company,key,values[key],start,end,actor.strip(),reason.strip())) for key in IDS]
            def encode(item):
                return {key:value.isoformat() if isinstance(value,datetime) else value for key,value in asdict(item).items()}
            result=dict(company_id=company,as_of_date=info['as_of_date'],dataset_id=dataset,
                request_revision=request['revision'],values={key:values[key] for key in IDS},
                configurations=[encode(item) for item in configs],actor=actor.strip(),reason=reason.strip(),
                activated_at=datetime.now(timezone.utc).isoformat(),scope='LOCAL_SYNTHETIC_FINANCE_PARAMETERS_AT_CUTOFF',
                decision_authority=False,operational_path='FORBIDDEN')
            result['fingerprint']=sha256(json.dumps(result,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
            c.execute('INSERT INTO company_finance_parameter_activation VALUES(?,?,?)',(company,info['as_of_date'],json.dumps(result,ensure_ascii=False)))
    return read_parameters(db,store,dataset)
