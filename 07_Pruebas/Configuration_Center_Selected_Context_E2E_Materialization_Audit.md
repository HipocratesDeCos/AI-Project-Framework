# EIOS — Configuration Center Selected-Context E2E — Materialization Audit

**Fecha:** 2026-09-14  
**Baseline funcional:** `main @ 4399f22c605c057690e643e3429ef016c74049c4`  
**Materialización auditada:** `b4d9ee642598296acfda6b59168cd0a931f427a8`  
**Dictamen:** CONFORME — PENDIENTE DE CI

## 1. Objeto materializado

Se añadió un único test de integración E2E:

- `tests/test_configuration_center_selected_context_e2e.py`

No se modificó código de producción.

## 2. Puertos de prueba

El test materializa exclusivamente los tres puertos previstos por `ParameterConfigurationCenter`:

- `E2ECatalogue` → implementación de `ParameterCatalogue`;
- `MutableAuthorization` → implementación de `ConfigurationAuthorization`;
- `E2ERepository` → implementación de `ConfigurationRepository`.

El repositorio E2E usa `effective_now` local y determinista, repite el control de solape dentro de `apply_change_atomically`, registra `atomic_apply_calls` e incluye una operación de inyección externa limitada al test.

No se mockean ni sustituyen:

- `ParameterConfigurationCenter`;
- `ConfigurationCenterUIController`;
- `ConfigurationCenterSelectedWorkflow`;
- `ConfigurationCenterScreen` / builder Slice 2;
- `present_configuration_center_snapshot`.

## 3. Escenario positivo

El test parte de repositorio vacío y verifica:

- refresh real con `data_ready=True`;
- configuración actual ausente e histórico válido vacío;
- preparación y confirmación reales;
- exactamente una llamada atómica;
- `APPLIED` con la configuración devuelta por backend;
- histórico inmediatamente posterior todavía vacío y `history_stale=True`;
- refresh posterior que incorpora una entrada real de histórico;
- preservación de empresa, parámetro, actor, motivo y valor;
- serialización JSON del payload de Slice 4.

No se introduce edición in-place ni cierre automático de vigencias.

## 4. Revocación de autorización

El test prepara con autorización válida, revoca el puerto antes de confirmar y verifica conjuntamente:

- `FORBIDDEN / UNAUTHORIZED_CHANGE`;
- `atomic_apply_calls == 0`;
- cero configuraciones persistidas;
- histórico vacío;
- pending consumido;
- propuesta local consumida;
- confirmación ausente;
- formulario retenido;
- contexto seleccionado preservado;
- payload JSON-safe.

La prueba demuestra no escritura, no solo un estado visual.

## 5. Conflicto concurrente

El test prepara sin conflicto, inyecta una única configuración externa solapada y confirma. Verifica:

- `CONFLICT / CONFLICTING_ACTIVE_CONFIGURATION`;
- contador atómico sin incremento para la solicitud EIOS rechazada;
- única configuración existente = configuración externa;
- histórico EIOS vacío;
- pending y propuesta consumidos;
- formulario retenido;
- payload JSON-safe.

La escritura externa simulada queda diferenciada de la escritura EIOS rechazada.

## 6. Integridad de rama

Comparación posterior a la materialización contra el baseline:

- `ahead = 6`;
- `behind = 0`;
- archivos modificados de producción: **0**;
- cambios funcionales: únicamente nuevo test E2E;
- resto de cambios: documentación de contrato/auditoría/cierre.

## 7. Compatibilidad con CI

La CI vigente ejecuta Python 3.12, instala `.[test]`, corre `python -m pytest -q` y valida los esquemas SQL existentes. La materialización no modifica dependencias, workflow ni SQL.

## 8. Dictamen

**MATERIALIZACIÓN CONFORME — PENDIENTE DE CI.**

No se detecta contradicción que exija reabrir Slices 1–4 o el backend. El siguiente gate obligatorio es reconciliar rama, abrir PR y obtener CI pre-merge `SUCCESS` sobre su HEAD exacto.
