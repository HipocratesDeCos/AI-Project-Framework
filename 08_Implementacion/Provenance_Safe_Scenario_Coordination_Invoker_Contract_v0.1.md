# EIOS — Provenance-Safe Scenario Coordination Invoker Contract v0.1

**Baseline:** `main @ 4367dcb0cb36b754b42efc51061017634e320bd6`  
**Fecha:** 23/09/2026  
**Estado:** DISEÑADO → AUDITADO → MATERIALIZADO EN RAMA / CI PENDIENTE

## 1. Problema

EIOS ya dispone de:

- preparación O4→O2;
- Stage 2 provenance-safe desde `AssessmentTraceBinding`;
- Viability Frontier recomputada;
- O3;
- puente O3→O2 Support;
- adaptador `SCENARIO_COORDINATION`.

Sin embargo, la fachada interna de `vertical_orchestration` construye un
invoker desde un `O4O2O3OrchestrationResult` ya producido y declara
expresamente que esa frontera no certifica por sí sola la provenance del
orchestration object.

Por tanto, no debe reutilizarse como garantía positiva en el caso de referencia.

## 2. Decisión

Se crea:

`build_provenanced_scenario_coordination_invoker(...)`

Su entrada pública es exclusivamente:

- `O4O2O3Preparation`;
- secuencia de `ProvenancedScenarioAnalyticsInput`.

No acepta:

- `O4O2O3OrchestrationResult`;
- `O2SupportPackage`;
- `ScenarioEvaluationResult` raw;
- `ViabilityResult` raw;
- `CapabilityExecution` preconstruida.

## 3. Flujo causal

En cada invocación runtime:

```text
PurchaseOperation + DecisionContext runtime
        ↓
validación completa contra preparation.context
        ↓
ProvenancedScenarioAnalyticsInput[]
        ↓
AssessmentTraceBinding[]
        ↓
validate provenance
        ↓
evaluate_provenanced_viability(...)
        ↓
AuthorizedScenarioAnalytics interno
        ↓
_complete_o4_o2_o3_orchestration(...)
        ↓
O3 ScenarioEvaluationResult[]
        ↓
build_o2_support_from_orchestration(...)
        ↓
adapt_scenario_coordination(...)
        ↓
CapabilityExecution(SCENARIO_COORDINATION)
```

La provenance se reestablece dentro de la misma invocación que produce la
capacidad.

## 4. Binding de contexto raíz

El runtime debe coincidir con la preparación en:

- decision_id;
- scenario_id;
- rules_version;
- parameters_version;
- data_snapshot_id.

PurchaseOperation debe coincidir con DecisionContext en decision_id y
scenario_id.

La semántica scenario-specific continúa delegada al contrato Stage 2 ya cerrado.

## 5. Congelación

El builder conserva copias profundas de:

- preparation;
- todos los inputs;
- todos los AssessmentTraceBinding contenidos.

Mutaciones posteriores del material del caller no pueden alterar el invoker ya
construido.

## 6. Sin nueva autoridad analítica

Esta unidad no:

- evalúa reglas de negocio nuevas;
- crea Assessment;
- crea Evidence;
- crea Viability status por heurística;
- modifica O4/O2/O3;
- rankea escenarios;
- selecciona escenario;
- toma una decisión;
- modifica CRC/O1.

La Viability Frontier se obtiene únicamente del productor provenance-safe
existente.

## 7. AUDITAR

### A1 — orchestration desprendido

Rechazado. No forma parte de la firma pública.

### A2 — support package desprendido

Rechazado. Se construye internamente después de reestablecer provenance.

### A3 — detached Viability

Rechazado. `ProvenancedScenarioAnalyticsInput` no contiene viability_result.

### A4 — Trace manipulada

La recomputación Stage 2 debe fallar antes de adaptar la capacidad.

### A5 — runtime extranjero

Cualquier diferencia en los cinco campos del DecisionContext raíz falla
cerrado.

### A6 — inputs incompletos o duplicados

El builder rechaza input vacío y scenario_id duplicados; la completion Stage 2
exige además cobertura exacta de todos los escenarios O2 VALID.

### A7 — confundir invoker con decisión

`SCENARIO_COORDINATION` representa soporte coordinado, no escenario elegido.

## 8. Superficie pública

Se autoriza exportar:

- `ScenarioCoordinationInvoker`;
- `build_provenanced_scenario_coordination_invoker`.

La antigua función privada de `vertical_orchestration` permanece sin cambios
y no adquiere garantías adicionales por la existencia de esta unidad.

## 9. Materialización

- actualización de `eios/rules/scenario_integration.py`;
- actualización de `eios/rules/__init__.py`;
- `tests/test_scenario_coordination_provenance_invoker.py`;
- actualización de pruebas de cuarentena/superficie pública;
- este contrato.

## 10. Criterio de cierre

CI deberá demostrar:

- reconstrucción Stage 2 desde bindings;
- SCENARIO_COORDINATION `COMPLETED` para cobertura válida;
- compatibilidad directa con `run_mvp_execution`;
- rechazo de runtime extranjero;
- rechazo de Trace manipulada;
- congelación de fuentes;
- rechazo de inputs vacíos/duplicados;
- ausencia de argumentos raw/desprendidos;
- suite completa sin regresión.

## 11. Continuidad

Una vez cerrada esta frontera, `REF-BUSINESS-001` podrá incorporar conjuntamente:

- Decision Twin provenance-safe;
- Scenario Coordination provenance-safe;

usando la misma preparación e inputs Stage 2, sin introducir dos historias
analíticas divergentes.
