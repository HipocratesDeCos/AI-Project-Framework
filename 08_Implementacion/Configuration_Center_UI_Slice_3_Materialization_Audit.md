# EIOS — Configuration Center UI Slice 3 — Materialization Audit

**Fecha:** 2026-09-13  
**Estado:** DEPURADA — SIN BLOQUEADORES CONOCIDOS, PENDIENTE DE CI

## 1. Objeto

Auditar la implementación materializada del workflow seleccionado contra el contrato cerrado y los invariantes de Slice 1 + Slice 2.

## 2. Hallazgo M1 — binding del resultado `APPLIED` al contexto seleccionado

El diseño exigía una `Configuration` real para `APPLIED`, pero la primera materialización podía aceptar una configuración retornada con `company_id` o `parameter_id` distintos del detalle seleccionado.

### Corrección

Antes de sustituir el detalle local, Slice 3 exige:

- `result.configuration.company_id == detail.company_id`;
- `result.configuration.parameter_id == detail.parameter_id`.

Una discrepancia produce `ConfigurationWorkflowError` y no modifica el snapshot.

## 3. Hallazgo M2 — representabilidad tras incoherencia técnica

La primera materialización consumía la propuesta local inmediatamente después de `confirm_and_apply()`. Si un controlador incoherente conservaba pending o devolvía `APPLIED` sin configuración, podía quedar un estado interno difícil de representar de forma segura.

### Corrección

- Si el controlador conserva pending después de confirmación, Slice 3 conserva también la propuesta local y falla técnicamente; no oculta una operación todavía pendiente.
- Si `APPLIED` llega sin configuración, con detalle ausente o con identidad distinta, se elimina la propuesta ya consumida por el controlador, se registra estado visual `ERROR` y no se modifica detalle/histórico.
- Las incoherencias de `prepare()` registran igualmente `ERROR` técnico sin inventar código de dominio.

## 4. Carga y frescura

Verificado:

- refresh con pending o borrador activo falla antes de alterar snapshots;
- un refresh nuevo invalida datos previos antes de leer;
- fallo de detalle impide leer histórico;
- fallo de histórico no conserva el histórico anterior;
- histórico vacío sigue siendo válido;
- tras `APPLIED` el histórico anterior se conserva únicamente con `history_stale=True`;
- un refresh posterior satisfactorio sustituye histórico y limpia `history_stale`.

## 5. Delegación

La implementación:

- solo utiliza la API cerrada de `ConfigurationCenterUIController` para lectura/preparación/cancelación/confirmación;
- solo utiliza `build_configuration_center_screen` para composición visual;
- no accede directamente a `ParameterConfigurationCenter`, catálogo, autorización, repositorio o SQL;
- no crea empresas, parámetros, actores, reglas, excepciones, simulaciones o decisiones.

## 6. Pruebas materializadas

La suite cubre carga completa/parcial, histórico vacío, borradores, coherencia pending, preparación válida/fallida, refresh bloqueado, cancelación, aplicación, stale history, refresh post-apply, identidad de configuración aplicada e incoherencias técnicas.

## 7. Dictamen

**MATERIALIZACIÓN DEPURADA Y COHERENTE — SIN BLOQUEADORES CONOCIDOS.**

El cierre físico continúa condicionado a CI SUCCESS pre-merge, reconciliación con `main`, merge protegido por SHA y CI SUCCESS postintegración.
