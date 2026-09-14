# EIOS — Configuration Center Selected-Context E2E Conformance Contract v0.1

**Estado:** 🔒 CERRADO — MATERIALIZADO — CI VALIDADA  
**Fecha:** 2026-09-14  
**Baseline funcional:** `main @ 4399f22c605c057690e643e3429ef016c74049c4`  
**Objeto:** verificación E2E sin nueva funcionalidad  
**Estado posterior de integración:** PR #140 · CI #771/#772 SUCCESS · merge `4ca4b1e9bf029b5a138b11c9b16d1188582a4231`

## 1. Propósito

Verificar de extremo a extremo el subconjunto ejecutable **selected-context** del Configuration Center ya cerrado, atravesando sus fronteras reales desde `ParameterConfigurationCenter` hasta el payload JSON-safe de aplicación.

Esta unidad no añade un nuevo slice, no modifica producción y no amplía autoridad.

## 2. Cadena bajo prueba

```text
ParameterCatalogue test port
ConfigurationAuthorization test port
ConfigurationRepository test port
             ↓
ParameterConfigurationCenter          — backend real
             ↓
ConfigurationCenterUIController       — Slice 1 real
             ↓
ConfigurationCenterSelectedWorkflow   — Slice 3 real
             ↓
ConfigurationCenterScreen             — Slice 2 real
             ↓
present_configuration_center_snapshot — Slice 4 real
             ↓
Mapping JSON-safe
```

Los únicos dobles permitidos son los tres puertos expresamente previstos por `eios/parameters/center.py`:

- catálogo;
- autorización;
- repositorio.

No se mockean Slices 1–4 ni `ParameterConfigurationCenter`. No se monkeypatchan métodos privados o públicos de producción.

## 3. Contexto de prueba

El contexto seleccionado será fijo y explícito:

- `company_id = "COMP-001"`;
- `parameter_id = "PRE-001"`;
- `actor = "USER-001"`.

Este contexto es un fixture de prueba, no una demostración de autenticación ni de enumeración de empresas.

## 4. Puerto de catálogo

El catálogo de prueba expone únicamente:

```text
PRE-001
value_type = DECIMAL
unit = EUR
restricted = False
```

Puede incorporar una validación mínima de valor para comprobar propagación de errores, pero no crea catálogo global ni descubrimiento.

## 5. Puerto de autorización

La autorización de prueba debe ser **mutable** para simular:

- autorización válida durante `prepare()`;
- revocación antes de `confirm()`.

El test no interpreta por qué se revoca; solo demuestra que la revalidación de Slice 1 impide escritura posterior.

## 6. Puerto de repositorio E2E

Se implementará un repositorio local del propio test, independiente de `FakeRepository` y de constantes globales de otros tests.

Debe implementar el protocolo real:

- `get_current`;
- `get_at`;
- `get_history`;
- `has_overlapping_configuration`;
- `apply_change_atomically`.

Además debe:

- recibir un `effective_now` explícito e inmutable por escenario;
- usar ese instante para determinar configuración vigente y marcas temporales de las escrituras del escenario;
- conservar aislamiento por empresa/parámetro;
- preservar histórico;
- repetir el control de conflicto dentro de `apply_change_atomically`;
- exponer `atomic_apply_calls` para demostrar si la escritura atómica llegó o no a invocarse;
- disponer de `inject_external_configuration(...)` exclusivamente para simular una escritura concurrente externa entre `prepare()` y `confirm()`;
- no añadir histórico EIOS por esa inyección externa;
- no implementar cierre automático, sustitución implícita ni edición in-place de configuraciones vigentes.

La inyección concurrente pertenece únicamente al doble de persistencia de prueba; no modifica ni sustituye comportamiento de producción.

## 7. Escenario E2E positivo

Partida sin configuración ni histórico para `COMP-001 / PRE-001`.

La creación positiva representa **la primera configuración** del contexto. No representa edición o sustitución de una configuración activa.

Flujo:

1. fijar un `effective_now` determinista;
2. construir puertos de prueba + `ParameterConfigurationCenter` real + Slices 1–4 reales;
3. `workflow.refresh()`;
4. comprobar `data_ready=True`, configuración actual `None`, histórico válido vacío y payload JSON-safe;
5. preparar cambio con `valid_from == effective_now` y `valid_to` futuro;
6. comprobar `AWAITING_CONFIRMATION` y confirmación visible;
7. `workflow.confirm()`;
8. comprobar `APPLIED`, configuración real devuelta y `history_stale=True`;
9. comprobar que el snapshot inmediatamente posterior conserva el histórico previo vacío y **no inventa** la entrada recién escrita;
10. comprobar que `atomic_apply_calls == 1`;
11. `workflow.refresh()`;
12. comprobar configuración vigente real, histórico con una entrada, actor/motivo/valor preservados y `history_stale=False`;
13. comprobar que empresa y parámetro permanecen `COMP-001 / PRE-001` en detalle, configuración e histórico;
14. serializar el payload final con `json.dumps(...)`.

## 8. Revocación de autorización

Flujo:

1. repositorio vacío y autorización permitida;
2. `refresh()` válido;
3. `prepare()` válido;
4. cambiar únicamente el puerto de autorización a denegado;
5. `confirm()`;
6. esperar `FORBIDDEN / UNAUTHORIZED_CHANGE`;
7. demostrar simultáneamente que no hubo escritura:
   - `atomic_apply_calls == 0`;
   - configuraciones del repositorio vacías;
   - histórico vacío;
8. comprobar `controller.has_pending_confirmation == False`;
9. comprobar confirmación ausente;
10. comprobar formulario retenido como borrador corregible;
11. comprobar que contexto y payload siguen reflejando `COMP-001 / PRE-001 / USER-001`;
12. serializar el payload final con `json.dumps(...)`.

Este escenario demuestra que la validación inicial no se reutiliza como autorización permanente y que el fallo visual corresponde a ausencia efectiva de persistencia.

## 9. Conflicto concurrente

Flujo:

1. repositorio inicialmente sin conflicto;
2. `refresh()` válido;
3. `prepare()` válido;
4. registrar el valor de `atomic_apply_calls` tras `prepare()`;
5. usar `inject_external_configuration(...)` para insertar una única configuración externa solapada antes de `confirm()`;
6. `confirm()`;
7. esperar `CONFLICT / CONFLICTING_ACTIVE_CONFIGURATION`;
8. comprobar que la única configuración existente es la externa inyectada;
9. comprobar que `atomic_apply_calls` **no aumenta** por la solicitud EIOS rechazada cuando la revalidación previa detecta el conflicto;
10. comprobar que no se genera ninguna entrada de histórico atribuible a la solicitud EIOS rechazada;
11. comprobar `controller.has_pending_confirmation == False` y confirmación ausente;
12. comprobar formulario retenido como borrador corregible;
13. serializar el payload final con `json.dumps(...)`.

El test distingue explícitamente la escritura externa simulada de una eventual escritura EIOS: la presencia de la configuración externa no puede interpretarse como éxito del cambio solicitado.

## 10. Aislamiento de contexto

Debe verificarse que a través de toda la cadena:

- empresa sigue siendo `COMP-001`;
- parámetro sigue siendo `PRE-001`;
- actor de histórico sigue siendo `USER-001`;
- ninguna operación de preparación/confirmación admite identificadores alternativos, porque estos no forman parte del formulario/propuesta;
- el payload de Slice 4 refleja los mismos identificadores cuando están presentes.

No se probará selección libre de empresa/parámetro porque dicha capacidad no existe.

## 11. No alcance

Esta unidad no prueba ni implementa:

- autenticación;
- resolución de identidad;
- enumeración de empresas;
- listado/búsqueda global de parámetros;
- tecnología web;
- reglas/CRC;
- simulación de impacto;
- QTG;
- decisiones de compra;
- cierre automático de vigencias;
- sustitución in-place de configuraciones activas.

## 12. Materialización autorizada

Únicamente:

- tests E2E nuevos en `tests/`;
- documentos de diseño/auditoría/cierre en `07_Pruebas/`.

**No se autoriza modificar código de producción.**

Si la prueba descubre una contradicción en producción, la unidad E2E se detiene como hallazgo y cualquier corrección exige ciclo propio.

## 13. Criterios de éxito

La conformidad puede cerrarse solo si:

1. los cuatro slices se atraviesan realmente sin mocks internos;
2. el backend usado es `ParameterConfigurationCenter` real;
3. positivo, revocación y conflicto pasan;
4. histórico/frescura se comportan según contratos cerrados;
5. las dos rutas rechazadas demuestran ausencia efectiva de escritura EIOS;
6. el conflicto distingue inequívocamente la configuración externa de la solicitud rechazada;
7. payloads finales son JSON-safe;
8. no se modifica producción;
9. suite completa CI queda verde.

**Estado reconciliado:** todos estos gates quedaron satisfechos por la materialización test-only, PR #140, CI pre-merge #771 y CI post-merge #772.

## 14. Método

```text
DISEÑAR       ✅
AUDITAR       ✅ Audit 1 — 4 precisiones, 0 bloqueos
DEPURAR       ✅ A1–A4 incorporados
AUDITAR 2     ✅ 0 bloqueos
CERRAR        ✅
MATERIALIZAR  ✅ tests solamente
CI            ✅ PR #140 · #771/#772 SUCCESS
```

La referencia funcional `main @ 4399f22c605c057690e643e3429ef016c74049c4` se conserva como baseline histórico de diseño de esta unidad; el merge posterior `4ca4b1e9bf029b5a138b11c9b16d1188582a4231` demuestra su integración, no reemplaza retroactivamente ese punto de partida.
