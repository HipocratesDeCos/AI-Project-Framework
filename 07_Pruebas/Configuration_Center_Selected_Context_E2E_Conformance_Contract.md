# EIOS — Configuration Center Selected-Context E2E Conformance Contract v0.1

**Estado:** DISEÑO  
**Fecha:** 2026-09-14  
**Baseline:** `main @ 4399f22c605c057690e643e3429ef016c74049c4`  
**Objeto:** verificación E2E sin nueva funcionalidad

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

No se mockean Slices 1–4 ni `ParameterConfigurationCenter`.

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

## 6. Puerto de repositorio

El repositorio de prueba implementará el protocolo real:

- `get_current`;
- `get_at`;
- `get_history`;
- `has_overlapping_configuration`;
- `apply_change_atomically`.

Debe:

- conservar aislamiento por empresa/parámetro;
- preservar histórico;
- repetir el control de conflicto dentro de `apply_change_atomically`;
- permitir inyectar una configuración concurrente entre `prepare()` y `confirm()` para verificar conflicto anti-stale;
- no implementar semántica adicional de cierre automático de configuraciones activas.

## 7. Escenario E2E positivo

Partida sin configuración ni histórico para `COMP-001 / PRE-001`.

Flujo:

1. construir backend real + Slices 1–4;
2. `workflow.refresh()`;
3. comprobar `data_ready=True`, configuración actual `None`, histórico vacío y payload JSON-safe;
4. preparar cambio con intervalo válido que empiece en el instante de referencia de prueba;
5. comprobar `AWAITING_CONFIRMATION` y confirmación visible;
6. `workflow.confirm()`;
7. comprobar `APPLIED`, configuración real devuelta y `history_stale=True`;
8. comprobar que el snapshot inmediatamente posterior no inventa histórico nuevo;
9. `workflow.refresh()`;
10. comprobar configuración vigente real, histórico con una entrada, actor/motivo/valor preservados y `history_stale=False`;
11. serializar el payload final con `json.dumps(...)`.

## 8. Revocación de autorización

Flujo:

1. carga válida;
2. `prepare()` con autorización permitida;
3. cambiar únicamente el puerto de autorización a denegado;
4. `confirm()`;
5. esperar `FORBIDDEN / UNAUTHORIZED_CHANGE`;
6. confirmar que repositorio e histórico siguen sin escritura;
7. confirmar que no existe panel de confirmación pendiente;
8. confirmar que el formulario permanece disponible como borrador corregible;
9. payload final JSON-safe.

Este escenario demuestra que la validación inicial no se reutiliza como autorización permanente.

## 9. Conflicto concurrente

Flujo:

1. carga válida;
2. `prepare()` sobre repositorio sin conflicto;
3. insertar directamente en el puerto de repositorio una configuración solapada antes de `confirm()` para simular escritura concurrente externa;
4. `confirm()`;
5. esperar `CONFLICT / CONFLICTING_ACTIVE_CONFIGURATION` antes de la escritura solicitada;
6. comprobar que no se añade una segunda configuración/histórico por el cambio rechazado;
7. confirmar que no queda pending oculto.

La inyección se realiza en el **doble de persistencia de prueba**, no en producción, y representa una carrera externa que el contrato debe detectar.

## 10. Aislamiento de contexto

Debe verificarse que a través de toda la cadena:

- empresa sigue siendo `COMP-001`;
- parámetro sigue siendo `PRE-001`;
- actor de histórico sigue siendo `USER-001`;
- ninguna operación acepta identificadores alternativos durante preparación/confirmación;
- el payload de Slice 4 refleja esos mismos identificadores.

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
- decisiones de compra.

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
5. payload final es JSON-safe;
6. no se modifica producción;
7. suite completa CI queda verde.

## 14. Método

```text
DISEÑAR       ✅
AUDITAR       ⏳
DEPURAR       ⏳
AUDITAR 2     ⏳
CERRAR        ⏳
MATERIALIZAR  ⏳ tests solamente
CI            ⏳
```
