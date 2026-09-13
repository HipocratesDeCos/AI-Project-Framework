# EIOS — Vertical MVP Scenario Coordination Opaque Result Quarantine Contract v0.1

## Estado

**CERRADO PARA IMPLEMENTACIÓN**

Baseline autorizado: `main @ 533fa47ad087e44a90f8d5b5cac4549ca9f58bb2`.

## 1. Propósito

Eliminar de las fronteras públicas del Vertical MVP la conversión implícita de resultados de Scenario Coordination ya producidos en capacidad ejecutable mediante snapshots que ignoran los `PurchaseOperation` y `DecisionContext` recibidos en runtime.

Esta unidad es una **cuarentena de composición**, no una certificación genérica de procedencia de Scenario Coordination.

## 2. Hallazgo objetivo

En el baseline:

1. `run_mvp_execution(...)` acepta `scenario_coordination_result: O2SupportPackage | None`.
2. El core valida solo la identidad contextual del paquete y después lo convierte mediante `_snapshot_invoker(...)` en un invocador que no usa la compra ni el contexto runtime.
3. `run_vertical_mvp_support(...)` acepta `scenario_evaluation_results`, construye un `O2SupportPackage` desde resultados O3 desprendidos y lo entrega al core como `SCENARIO_COORDINATION`.
4. La frontera posterior `Scenario_Stage2_Provenance_Boundary_Contract_v0.1` establece que el transporte interno y los resultados ya producidos no constituyen por sí solos prueba de procedencia, y que las afirmaciones E2E de escenarios deben atravesar la frontera provenance-safe.

Por tanto, la composición Vertical no puede fabricar procedencia aparente a partir de un `O2SupportPackage` o de una secuencia O3 desprendida.

## 3. Principio de seguridad

Un **invocador explícito** separa responsabilidad de composición y responsabilidad de producción. Su presencia **no significa** que el invocador sea provenance-safe.

La capa Vertical:

- puede ejecutar un invocador que recibe la `PurchaseOperation` y el `DecisionContext` reales;
- no puede transformar internamente un resultado opaco en invocador snapshot;
- no puede afirmar cómo se produjo un resultado que no puede reconstruir o verificar;
- no puede introducir aliases legacy para conservar el camino inseguro.

## 4. Cambios autorizados

### 4.1 `run_mvp_execution`

Sustituir:

`scenario_coordination_result: O2SupportPackage | None`

por:

`scenario_coordination_invoker: CapabilityInvoker | None`.

Cuando exista, el invocador se registra directamente bajo `SCENARIO_COORDINATION` y recibe la compra/contexto runtime mediante la frontera E2E existente.

Eliminar del core:

- la validación específica del paquete Scenario Coordination como argumento público;
- la creación de snapshot invoker para Scenario Coordination;
- imports auxiliares que queden sin uso.

No cambia `MVP_CAPABILITY_ORDER`.

### 4.2 `run_vertical_mvp_support`

Eliminar `scenario_evaluation_results` de la firma pública.

Añadir `scenario_coordination_invoker: CapabilityInvoker | None = None` y trasladarlo sin reinterpretación a `run_mvp_execution`.

El façade genérico no construirá `O2SupportPackage` desde O3 desprendido. En esta ruta `scenario_support` permanece `None`, salvo que otra frontera especializada autorizada lo produzca explícitamente.

No se admite alias ni fallback a `scenario_evaluation_results`.

### 4.3 `run_vertical_mvp_from_orchestration`

Se mantiene como frontera especializada capaz de conservar `scenario_support` para presentación.

Debe dejar de entregar un `O2SupportPackage` crudo a `run_mvp_execution`.

Debe construir un invocador explícito de Scenario Coordination que:

1. congele una copia inmutable de `O4O2O3OrchestrationResult`;
2. exija que el `DecisionContext` runtime coincida exactamente con `orchestration_result.preparation.context`;
3. reconstruya el `O2SupportPackage` mediante `build_o2_support_from_orchestration(...)` usando la `PurchaseOperation` runtime;
4. adapte ese paquete con `adapt_scenario_coordination(...)`;
5. no ejecute O4, O2 materialization, O3, reglas, Viability Frontier ni lógica decisional.

La salida detallada `scenario_support` se sigue construyendo desde la orquestación para presentación, sin cambiar su contrato.

Este invocador **no certifica por sí mismo** que el objeto `O4O2O3OrchestrationResult` haya sido producido mediante la frontera provenance-safe. Las afirmaciones E2E provenance-safe siguen dependiendo de `complete_provenanced_o4_o2_o3_orchestration(...)`.

## 5. Invariantes preservados

- `SCENARIO_COORDINATION` permanece entre `DECISION_TWIN` y `NEGOTIATION_INTELLIGENCE`.
- `O2SupportPackage`, O2, O3 y sus adaptadores no cambian.
- Scenario Stage 2 no se reabre ni se modifica.
- La presentación de `scenario_support` no se modifica.
- `NOT_EVALUABLE`, `PARTIALLY_COMPLETED` y `FAILED` conservan su semántica técnica.
- No se crean score, ranking, recomendación, selección, aprobación ni rechazo.
- La autoridad decisional humana permanece intacta.
- Inputs públicos se copian/consumen sin mutación.
- Ausencia de Scenario Coordination no crea capacidad sintética.

## 6. Prohibiciones

Queda prohibido:

- restaurar `scenario_coordination_result` como parámetro público;
- restaurar `scenario_evaluation_results` en el façade genérico;
- envolver un `O2SupportPackage` ya producido en un snapshot invoker que ignore runtime;
- afirmar que cualquier invocador de Scenario Coordination es provenance-safe por el mero hecho de ser invocador;
- modificar contratos cerrados de O2/O3/Stage 2 para facilitar esta migración;
- crear un sistema paralelo de identidad, versión o trazabilidad.

## 7. Criterios de aceptación

La implementación solo podrá cerrarse si:

1. las firmas públicas no aceptan `scenario_coordination_result` ni `scenario_evaluation_results`;
2. `run_mvp_execution` acepta `scenario_coordination_invoker` y le entrega los objetos runtime reales;
3. la ruta desde orquestación conserva `scenario_support` y produce exactamente una capacidad `SCENARIO_COORDINATION`;
4. la ruta desde orquestación falla si la compra o el contexto no son compatibles con la preparación;
5. los estados técnicos y la presentación siguen siendo deterministas y no decisionales;
6. no hay fallback legacy;
7. el diff permanece limitado al alcance autorizado;
8. CI completo de PR y CI post-merge finalizan en `SUCCESS` sobre los SHA exactos validados.

## 8. Dictamen de cierre de diseño

**DISEÑAR → COMPLETADO**  
**AUDITAR → COMPLETADO**  
**DEPURAR → COMPLETADO**  
**AUDITAR 2 DE DISEÑO → SUPERADA — SIN BLOQUEADORES**

Se autoriza MATERIALIZAR exclusivamente dentro de este contrato.
