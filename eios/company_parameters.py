"""Company-scoped parameter requests; no activation or parallel rule authority."""
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import json
import sqlite3

# Authorized identities/units from Catalogo_Parametros_MVP_v0.3.md.
# Standards are documentary starting points, never applied as defaults.
CATALOGUE = []
def _add(group, code, name, unit, standard, effect, kind='number', editable=True):
    CATALOGUE.append(dict(group=group, parameter_id=code, name=name, unit=unit,
        standard=standard, effect=effect, kind=kind, editable=editable,
        consumer_status='PENDING_ENGINE_BINDING',
        sector_range=None, sector_note='Sin rango sectorial contrastado para este parámetro.'))

_add('Finanzas','P-FIN-001','Horizonte de pagos','días','30','Ampliarlo incluye más vencimientos en el análisis y exige previsiones que cubran ese periodo.','integer')
_add('Finanzas','P-FIN-002','Tesorería mínima','EUR',None,'Elevarla exige conservar más liquidez y puede reducir la capacidad de compra.')
_add('Finanzas','P-FIN-003','Fondo de maniobra mínimo','EUR',None,'Elevarlo exige una posición mayor de activo corriente frente al pasivo corriente.')
_add('Finanzas','P-FIN-004','Margen mínimo de seguridad financiera','%','10','Elevarlo exige mayor holgura sobre el mínimo de tesorería; no equivale al margen comercial.')
_add('Finanzas','P-FIN-005','Considerar pagos futuros','Sí/No','Sí','Excluir pagos no puede utilizarse para eludir una restricción financiera crítica.','boolean',False)
_add('Finanzas','P-FIN-006','Considerar cobros previstos','Sí/No','Sí','Los cobros requieren su evidencia y vencimiento; este control no valida ni garantiza su cobro.','boolean',False)
for n,name,unit,standard,effect,kind in [
 (1,'Periodo principal de comparación','meses','3','Ampliarlo utiliza un historial más largo y puede incluir precios menos recientes.','integer'),
 (2,'Periodo ampliado de comparación','meses','12','Ampliarlo aumenta el historial disponible para el análisis.','integer'),
 (3,'Antigüedad máxima de referencia','meses','12','Ampliarla permite referencias más antiguas; no resuelve diferencias de unidad o condiciones.','integer'),
 (4,'Alerta de diferencia de precio','%','5','Reducirla hace que diferencias menores de precio alcancen el umbral de alerta.','number'),
 (5,'Alerta crítica de precio','%','10','Reducirla hace más exigente el umbral de diferencia crítica; no cambia la regla.','number'),
 (6,'Compras comparables mínimas','operaciones','2','Elevarlo exige más observaciones comparables antes de sostener la referencia.','integer')]:
    _add('Precios',f'P-PRE-{n:03}',name,unit,standard,effect,kind)
_add('Stock','P-STK-001','Stock mínimo por artículo','unidades',None,'Se configura por artículo y unidad en Stock; no se aplica una cantidad común a todo el catálogo.','number',False)
for n,name,unit,std,effect,kind in [
 (2,'Stock de seguridad','% del consumo','15','Elevarlo aumenta la reserva frente a variaciones de consumo. No equivale a una cantidad fija de unidades.','number'),
 (3,'Cobertura mínima','días','30','Elevarla exige más días de suministro y puede aumentar la necesidad de reposición.','integer'),
 (4,'Cobertura máxima','días','90','Reducirla hace más exigente el límite de acumulación de existencias.','integer'),
 (5,'Tolerancia de exceso','%','10','Elevarla permite más desviación sobre el límite de cobertura cuando la regla lo autorice.','number'),
 (6,'Periodo de consumo histórico','meses','12','Cambiarlo modifica la ventana de ventas o consumo utilizada como referencia.','integer')]:
    _add('Stock',f'P-STK-{n:03}',name,unit,std,effect,kind)
_add('Proyección','P-PYE-001','Horizonte de proyección de stock','días','90','Ampliarlo observa un periodo mayor y requiere previsiones compatibles.','integer')
for n,name,effect in [(2,'Considerar pedidos pendientes','Su consideración requiere pedidos identificados; activar el valor no demuestra recepción.'),
 (3,'Considerar compras en tránsito','Su consideración requiere cantidades y fechas documentadas; no se suman sin comprobar su estado.'),
 (4,'Considerar plazo de entrega','Permite estudiar cuándo llegaría la mercancía y si evita la rotura.'),
 (5,'Considerar ventas históricas','Permite usar ventas compatibles con el artículo y unidad; el valor no corrige códigos incompatibles.')]:
    _add('Proyección',f'P-PYE-{n:03}',name,'Sí/No','Sí',effect,'boolean')
_add('Proyección','P-PYE-006','Umbral de riesgo de rotura','días','15','Elevarlo advierte con mayor antelación sobre una posible falta de producto.','integer')
_add('Rotación','P-ROT-001','Inactividad de ventas','días',None,'Reducirlo hace que un periodo más corto sin ventas alcance el umbral de inactividad.','integer')
for n,name,unit,std,effect in [(1,'Margen mínimo','%','20','Elevarlo exige más rentabilidad porcentual a las operaciones.'),
 (2,'Margen objetivo','%','30','Elevarlo fija una aspiración mayor de rentabilidad; no sustituye el mínimo.'),
 (3,'Tolerancia de margen','puntos porcentuales','3','Elevarla amplía la desviación contemplada por la regla; no elimina límites críticos.'),
 (4,'Margen mínimo absoluto','EUR','5','Elevarlo exige una contribución mínima mayor en euros; es distinto del margen porcentual.')]:
    _add('Rentabilidad',f'P-MGE-{n:03}',name,unit,std,effect)
for n,name,effect in [(5,'Considerar descuentos','Requiere descuentos documentados y evita aplicarlos dos veces al precio ya neto.'),
 (6,'Considerar rappels','Requiere condiciones y evidencia propias; activar el valor no garantiza obtener el rappel.')]:
    _add('Rentabilidad',f'P-MGE-{n:03}',name,'Sí/No','Sí',effect,'boolean')
for n,name,std,effect in [(1,'Plazo de pago mínimo deseado','60','Elevarlo busca más días para pagar; la fecha debe negociarse y no se da por aceptada.'),
 (2,'Plazo de pago objetivo','90','Elevarlo busca un vencimiento más lejano; requiere aceptación del proveedor.'),
 (3,'Tolerancia de plazo','15','Cambiarla modifica el margen de desviación respecto al plazo definido.')]:
    _add('Pagos y negociación',f'P-PAG-{n:03}',name,'días',std,effect,'integer')
for n,name,effect in [(4,'Considerar plazo en negociación','Permite estudiar el plazo como variable de negociación; no modifica el vencimiento original.'),
 (5,'Considerar pronto pago','Permite estudiar descuentos por anticipar pagos junto con su efecto en liquidez.')]:
    _add('Pagos y negociación',f'P-PAG-{n:03}',name,'Sí/No','Sí',effect,'boolean')
for n,name,unit,std,effect in [(1,'Antigüedad máxima de datos operativos','semanas','6','Reducirla exige información más reciente.'),
 (2,'Antigüedad máxima de referencia de precio','meses','12','Reducirla exige referencias de precio más recientes.'),
 (3,'Registros históricos mínimos','operaciones','2','Elevarlo exige mayor soporte histórico para el análisis.')]:
    _add('Calidad de datos',f'P-DAT-{n:03}',name,unit,std,effect,'integer')
_add('Salvaguardas','P-DAT-004','Decidir con datos incompletos','—','No','No es una capacidad configurable del MVP; la ausencia de evidencia crítica mantiene información insuficiente.','boolean',False)


for n,name,effect in [
 (1,'Reglas de precio','Su activación depende de la autoridad de las reglas de precio.'),
 (2,'Reglas de stock','No se desactivan límites críticos de stock desde esta pantalla.'),
 (3,'Reglas de margen','No se desactivan restricciones críticas de rentabilidad desde esta pantalla.'),
 (4,'Reglas financieras','No se pueden desactivar las salvaguardas financieras críticas.'),
 (5,'Reglas de proveedores','Su activación requiere la autoridad y alcance definidos para proveedores.'),
 (6,'Permitir excepciones','Un valor no puede habilitar excepciones no autorizadas.'),
 (7,'Compra condicionada','Depende del cruce funcional y de las condiciones aprobadas; no autoriza por sí sola una compra.')]:
    _add('Salvaguardas',f'P-RGL-{n:03}',name,'Sí/No','Sí',effect,'boolean',False)
_add('Calidad de datos','P-DAT-005','Mostrar fecha de actualización','Sí/No','Sí','La fecha se conserva visible para conocer la antigüedad y trazabilidad de los datos.','boolean',False)
_add('Calidad de datos','P-DAT-006','Mostrar fiabilidad','Sí/No','Sí','La información sobre calidad no se oculta para convertir una entrada insuficiente en favorable.','boolean',False)
_add('Calidad de datos','P-DAT-007','Fiabilidad mínima para recomendar','nivel','Medio','La definición de niveles y su aplicación requiere el contrato de calidad; no se altera aquí.','text',False)

BY_ID = {item['parameter_id']:item for item in CATALOGUE}
PROFILE_KEYS = {'activity','iae','cnae','cnae_version','size','country'}
REFERENCE_KEYS = {'lower','upper','source','period','definition'}
TABLE = """CREATE TABLE IF NOT EXISTS company_parameter_request (
 company_id TEXT NOT NULL, revision INTEGER NOT NULL, dataset_id TEXT NOT NULL,
 created_at TEXT NOT NULL, actor TEXT NOT NULL, reason TEXT NOT NULL,
 payload TEXT NOT NULL, PRIMARY KEY(company_id,revision))"""


def _text(value, limit):
    if not isinstance(value,str) or len(value.strip())>limit:
        raise ValueError('Revisa los campos de texto y su longitud.')
    return value.strip()


def _number(value, kind):
    if isinstance(value,bool) or not isinstance(value,(str,int,float)):
        raise ValueError('Indica un valor numérico.')
    text = str(value).strip()
    if len(text)>80:
        raise ValueError('El número supera la longitud admitida.')
    try:
        number = Decimal(text)
    except InvalidOperation:
        raise ValueError('El valor debe ser numérico.') from None
    if not number.is_finite():
        raise ValueError('El número debe ser finito.')
    if kind=='integer' and (number<0 or number!=number.to_integral_value()):
        raise ValueError('Los periodos y recuentos requieren un entero no negativo.')
    return format(number,'f')


def read_parameters(db,store,dataset):
    info=store.describe(dataset)
    company=info['company']['company_id']
    with sqlite3.connect(db) as c:
        c.execute(TABLE)
        rows=c.execute('SELECT payload FROM company_parameter_request WHERE company_id=? ORDER BY revision DESC',(company,)).fetchall()
    current=json.loads(rows[0][0]) if rows else dict(company_id=company,revision=0,profile={},values={},references={})
    history=[json.loads(row[0]) for row in rows]
    return dict(company_id=company,company_name=info['company'].get('legal_name',company),dataset_id=dataset,
                as_of_date=info['as_of_date'],catalogue=CATALOGUE,current=current,history=history,
                status='COMPANY_CONFIGURATION_REQUEST_ONLY',
                message='Valores empresariales preparados. Su activación y aplicación al motor siguen pendientes; guardar aquí no ejecuta una evaluación.',
                sources=[dict(label='Catálogo EIOS',url='https://github.com/HipocratesDeCos/AI-Project-Framework/blob/main/02_Parametros/Catalogo_Parametros_MVP_v0.3.md'),
                         dict(label='Ratios sectoriales · Banco de España',url='https://www.bde.es/wbe/es/areas-actuacion/central-balances/bases-de-datos-y-aplicaciones/bbdd-datos-publicas-informacion-sectores/'),
                         dict(label='Clasificaciones de actividad · INE',url='https://www.ine.es/Ayudacod/')])


def save_parameters(db,store,data):
    dataset=_text(data['dataset_id'],128)
    state=read_parameters(db,store,dataset)
    company=state['company_id']
    expected=data.get('revision')
    if type(expected) is not int or expected<0:
        raise ValueError('Recarga la configuración antes de guardar.')
    actor=_text(data.get('actor'),128)
    reason=_text(data.get('reason'),512)
    if not actor or not reason:
        raise ValueError('Indica responsable y motivo del cambio.')
    profile=data.get('profile',{})
    values=data.get('values',{})
    references=data.get('references',{})
    if not all(isinstance(item,dict) for item in (profile,values,references)):
        raise ValueError('Configuración no válida.')
    if set(profile)-PROFILE_KEYS or set(values)-BY_ID.keys() or set(references)-BY_ID.keys():
        raise ValueError('Campo o parámetro no reconocido por el catálogo.')
    profile={key:_text(value,200) for key,value in profile.items()}
    if profile.get('cnae_version','') not in ('','CNAE-2009','CNAE-2025'):
        raise ValueError('Selecciona la clasificación CNAE.')
    if profile.get('cnae') and not profile.get('cnae_version'):
        raise ValueError('Indica si el código pertenece a CNAE-2009 o CNAE-2025.')
    normalized={}
    for key,value in values.items():
        definition=BY_ID[key]
        if not definition['editable']:
            raise ValueError('Este parámetro está protegido o se configura por artículo.')
        if value is None or value=='':
            continue
        if definition['kind']=='boolean':
            if value not in ('Sí','No'):
                raise ValueError('Selecciona Sí o No.')
            normalized[key]=value
        else:
            normalized[key]=_number(value,definition['kind'])
            if key in ('P-FIN-001','P-ROT-001') and Decimal(normalized[key])<=0:
                raise ValueError('El horizonte financiero y la ventana de inactividad requieren días positivos.')
            if key=='P-FIN-002' and Decimal(normalized[key])<0:
                raise ValueError('La tesorería mínima no puede ser negativa.')
    for low,high in [('P-STK-003','P-STK-004'),('P-MGE-001','P-MGE-002'),
                     ('P-PAG-001','P-PAG-002'),('P-PRE-004','P-PRE-005')]:
        if low in normalized and high in normalized and Decimal(normalized[low])>Decimal(normalized[high]):
            raise ValueError('Revisa que el mínimo no supere el máximo u objetivo: '+low+' / '+high)
    if any(key.startswith('P-FIN-') for key in normalized) and data.get('critical_acknowledged') is not True:
        raise ValueError('Confirma expresamente la preparación de los cambios financieros.')
    checked_refs={}
    for key,reference in references.items():
        if not isinstance(reference,dict) or set(reference)-REFERENCE_KEYS:
            raise ValueError('Referencia sectorial no válida.')
        if not any(value not in (None,'') for value in reference.values()):
            continue
        if not profile.get('activity') or not profile.get('size') or not profile.get('country') or not (profile.get('iae') or profile.get('cnae')):
            raise ValueError('Completa actividad, epígrafe/CNAE, tamaño y país para registrar una referencia sectorial.')
        if not BY_ID[key]['editable'] or BY_ID[key]['kind']=='boolean':
            raise ValueError('Este parámetro no admite una banda numérica sectorial.')
        lower=_number(reference.get('lower'),'number')
        upper=_number(reference.get('upper'),'number')
        if Decimal(lower)>Decimal(upper):
            raise ValueError('El límite inferior del rango supera al superior.')
        source=_text(reference.get('source'),500)
        period=_text(reference.get('period'),80)
        definition=_text(reference.get('definition'),500)
        if not source or not period or not definition:
            raise ValueError('Indica fuente, periodo y definición de la referencia sectorial.')
        checked_refs[key]=dict(lower=lower,upper=upper,source=source,period=period,definition=definition,
                               unit=BY_ID[key]['unit'],status='USER_DECLARED_NOT_VERIFIED',
                               profile=dict(profile))
    now=datetime.now(timezone.utc).isoformat()
    result=dict(company_id=company,dataset_id=dataset,revision=expected+1,created_at=now,
        actor=actor,reason=reason,profile=profile,values=normalized,references=checked_refs,
        previous_values=state['current'].get('values',{}),status='PENDING_ENGINE_ACTIVATION',
        critical_acknowledged=data.get('critical_acknowledged') is True,
        decision_authority=False,operational_path='FORBIDDEN')
    with sqlite3.connect(db) as c:
        c.execute('BEGIN IMMEDIATE')
        latest=c.execute('SELECT MAX(revision) FROM company_parameter_request WHERE company_id=?',(company,)).fetchone()[0] or 0
        if latest!=expected:
            raise ValueError('Otra sesión ha modificado los parámetros. Recarga antes de guardar.')
        c.execute('INSERT INTO company_parameter_request VALUES(?,?,?,?,?,?,?)',
                  (company,result['revision'],dataset,now,actor,reason,json.dumps(result,ensure_ascii=False)))
    return read_parameters(db,store,dataset)
