# EIOS — Vertical MVP QTG Provenance Quarantine Contract v0.1

**Estado:** DISEÑO — PENDIENTE DE AUDITORÍA 1  
**Baseline:** `main @ fe03a6da407490705207f579bcd45a4b384d8bc2`  
**Ámbito:** frontera de composición QTG ↔ Vertical MVP.

## 1. Propósito

Cerrar una contradicción de procedencia en las fronteras genéricas del Vertical MVP mientras QTG continúa bloqueado por ausencia de un `Decision Input Package` físico, agregado y trazable.

Esta unidad **no implementa QTG**, **no crea el Decision Input Package ausente**, **no modifica la semántica de Quality & Trust** y **no añade autoridad decisional**. Su único efecto autorizado es impedir que un `CapabilityInvoker` genérico pueda hacer aparecer `QTG` como ejecutado dentro del Vertical MVP sin un productor QTG provenance-safe previamente materializado y autorizado.

## 2. Hallazgo objetivo

En el baseline indicado:

- `run_mvp_execution(...)` acepta `quality_invoker: CapabilityInvoker | None`;
- `run_vertical_mvp_support(...)` expone el mismo parámetro y lo reenvía;
- cualquier callable compatible puede devolver un `CapabilityExecution(capability="QTG", status=COMPLETED, ...)`;
- la propia frontera documenta que la mera presencia de un invocador no constituye prueba de procedencia;
- el contrato cerrado de Quality & Trust exige como entrada una representación de `Decision Input Package` ya identificada y trazable;
- `EIOS-BL-003` mantiene QTG objetivamente bloqueado mientras no exista un `Decision Input Package` físico, agregado y trazable;
- no existe en el baseline un productor físico autorizado que reconstruya QTG desde ese paquete y vincule el resultado a la compra y al `DecisionContext` actuales.

Por tanto, la frontera genérica puede publicar una capacidad QTG que el baseline aún no autoriza a producir.

## 3. Precedente que esta unidad completa

`Vertical_MVP_Opaque_Result_Provenance_Quarantine_Contract_v0.1.md` eliminó correctamente `quality_result` desprendido y lo sustituyó provisionalmente por `quality_invoker`, dejando expresamente para una unidad posterior la construcción de un invocador QTG realmente provenance-safe.

Desde entonces otras capacidades han recibido productores/invocadores contextualmente seguros donde existía material suficiente. QTG no lo ha recibido porque sigue faltando su entrada física agregada. Esta unidad cierra la provisionalidad de la frontera genérica sin fingir ese productor.

## 4. Diseño autorizado

### 4.1 `run_mvp_execution(...)`

La firma genérica deja de aceptar:

- `quality_invoker`.

El servicio deja de registrar un invocador arbitrario bajo la clave `QTG`.

Se conservan sin modificación conceptual los invocadores ya autorizados para las demás capacidades.

### 4.2 `run_vertical_mvp_support(...)`

La fachada pública deja de aceptar:

- `quality_invoker`.

La fachada deja de reenviar dicho parámetro al servicio core.

### 4.3 Orden canónico

`MVP_CAPABILITY_ORDER` conserva `QTG` en su posición canónica.

La ausencia temporal de un productor autorizado no elimina QTG de la arquitectura ni redefine su orden. Cuando exista un `Decision Input Package` físico y se diseñe un productor provenance-safe, una unidad posterior podrá reabrir exclusivamente la integración QTG con evidencia suficiente.

### 4.4 Fail-closed

No se mantiene un alias legacy, no se ignora silenciosamente `quality_invoker` y no se intenta inspeccionar un `CapabilityExecution` para inferir una procedencia que no transporta.

Un consumidor que intente seguir suministrando `quality_invoker` encontrará que el parámetro ya no pertenece a la firma. Este cambio es deliberadamente fail-closed y hace visible la incompatibilidad en vez de publicar un QTG no acreditado.

## 5. Fronteras preservadas

Esta unidad no modifica:

- modelos ni evaluador de Quality & Trust;
- estados funcionales `APTO`, `APTO_CON_ADVERTENCIAS`, `NO_APTO`;
- niveles de confianza;
- `MVP_CAPABILITY_ORDER`;
- ejecución de PRICE, TCO, C0/Rules, Decision Twin, Scenario Coordination, NI o Ladder;
- `ExecutionOutcome`, `CapabilityExecution` ni `execute_plan(...)`;
- autoridad de reglas, CRC, escenarios, negociación o decisión humana;
- semántica `NOT_EVALUABLE` de otras capas.

No se inventa un estado Vertical `QTG_BLOCKED`, `QTG_NOT_EVALUABLE` ni equivalente. Mientras no exista productor autorizado, QTG simplemente no puede incorporarse a través de estas fachadas genéricas.

## 6. Compatibilidad

La retirada de `quality_invoker` es intencionadamente incompatible para consumidores que dependieran de la frontera insegura.

No se ofrece compatibilidad silenciosa porque conservar el parámetro como passthrough o ignorarlo ocultaría precisamente el defecto que se corrige.

Los consumidores físicos conocidos que deben reconciliarse conjuntamente son las dos fronteras productivas y sus tests de servicio Vertical MVP. La materialización deberá auditar el repositorio para detectar cualquier consumidor adicional antes del cierre.

## 7. Pruebas exigidas

La materialización deberá demostrar como mínimo:

1. `quality_invoker` no figura en la firma de `run_mvp_execution(...)`;
2. `quality_invoker` no figura en la firma de `run_vertical_mvp_support(...)`;
3. intentar pasarlo por keyword falla explícitamente en ambas fronteras;
4. QTG no aparece en `capability_results` de ejecuciones construidas solo con capacidades autorizadas;
5. `MVP_CAPABILITY_ORDER` conserva `QTG` en posición canónica;
6. PRICE/TCO/C0/Decision Twin/Scenario Coordination/NI/Ladder mantienen su composición autorizada;
7. ejecución sin ninguna capacidad sigue fallando cerrada;
8. no se modifica el dominio QTG ni se crea `Decision Input Package`;
9. la suite completa Python + validaciones SQL permanece verde.

## 8. Condición futura de reapertura

La integración QTG solo podrá reabrirse cuando exista evidencia física suficiente para diseñar y auditar un productor provenance-safe que, como mínimo:

- consuma el `Decision Input Package` autorizado y trazable;
- reconstruya/evalúe QTG desde material verificable en vez de aceptar un resultado desprendido;
- vincule la evaluación a la compra y al `DecisionContext` de la ejecución actual;
- preserve evidencia, trazabilidad, incertidumbre y contradicciones según las autoridades cerradas.

Esta cláusula no diseña dicho productor; únicamente fija la evidencia mínima que deberá justificar una unidad posterior.

## 9. Gate de cierre

Solo podrá pasar a `CERRAR` si Audit 1 y Audit 2 confirman que:

- no existe un productor QTG físico ya autorizado que esta unidad esté ocultando;
- retirar `quality_invoker` no rompe una integración QTG legítima existente;
- el cambio queda limitado a la frontera provisional y sus consumidores físicos;
- no se reabre la semántica de Quality & Trust;
- no se altera autoridad decisional;
- no se inventa arquitectura para resolver el `Decision Input Package` ausente.
