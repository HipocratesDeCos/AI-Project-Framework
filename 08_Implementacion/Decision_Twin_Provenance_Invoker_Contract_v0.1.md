# EIOS — Decision Twin Provenance Invoker Contract v0.1

## Estado

DISEÑADO → AUDITADO → DEPURADO. Pendiente de materialización, Auditoría 2 y CI.

## 1. Propósito

Cerrar la frontera pública entre el Vertical MVP y `Decision Twin` sin volver a aceptar un `DecisionTwinComparison` opaco ni re-etiquetarlo dentro del `DecisionContext` actual.

La unidad no modifica los contratos cerrados de Decision Twin, O3, Viability Frontier, C0 ni la autoridad decisional humana.

## 2. Entrada autorizada

La integración solo puede construir la comparación a partir de:

- una `O4O2O3Preparation` ya materializada;
- dos o más entradas `ProvenancedScenarioAnalyticsInput`;
- una `representation_ref` explícita, no vacía y única para cada alternativa;
- el `PurchaseOperation` y `DecisionContext` reales de la ejecución Vertical.

No se aceptan como frontera de reutilización:

- `DecisionTwinComparison` ya producido;
- `AlternativeRepresentation` arbitraria;
- `ScenarioEvaluationResult` aislado;
- diccionarios de resultados sin procedencia;
- un `scenario_id` reutilizado automáticamente como identidad de alternativa.

## 3. Procedencia

En cada ejecución, la integración debe volver a cruzar la frontera pública `complete_provenanced_o4_o2_o3_orchestration(...)`.

Por tanto:

- Assessment + Trace se validan por la frontera C0 cerrada;
- `ViabilityResult` se valida por la frontera VF → Scenario Analytics cerrada;
- O3 se ejecuta únicamente después de superar esas validaciones;
- la cobertura analítica debe coincidir exactamente con los escenarios `VALID` de la preparación.

Un `O4O2O3OrchestrationResult` construido por otro camino no se considera prueba suficiente de procedencia.

## 4. Contexto raíz

El invocador debe exigir coincidencia exacta entre el `DecisionContext` de la ejecución y `preparation.context` en:

- `decision_id`;
- `scenario_id`;
- `rules_version`;
- `parameters_version`;
- `data_snapshot_id`.

`PurchaseOperation.decision_id` y `PurchaseOperation.scenario_id` deben coincidir con el `DecisionContext` de la ejecución.

No se permite re-etiquetar una preparación extranjera dentro del contexto actual.

## 5. Representación de alternativa

`representation_ref` es una referencia transitoria suministrada por el llamador. Esta integración:

- no la deriva de `scenario_id`;
- no la persiste;
- no la convierte en `Alternative_ID`;
- no le atribuye semántica decisional;
- solo exige que sea no vacía y única dentro de la comparación.

`Scenario_ID ≠ Alternative` permanece intacto.

## 6. Transporte hacia Decision Twin

Tras completar O3 por la frontera provenance-safe, cada alternativa se construye exclusivamente con información ya producida:

- `scenario_id` → del `ScenarioEvaluationResult` validado;
- `viability` → valor literal de `ViabilityResult.status` de la entrada provenanced;
- `results` → estado O3, assessments O3, limitaciones O3 y `failure_reason` ya producidos;
- `trace_refs` → referencias O3 ya producidas;
- `conditions`, `consequences` y `risk_refs` → vacíos mientras no exista una fuente autorizada adicional en esta integración.

No se inventan consecuencias, condiciones, riesgos, scores, rankings ni preferencias.

Los estados de VF se transportan literalmente:

`VIABLE | VIABLE_CON_CONDICIONES | NOT_VIABLE | NOT_EVALUABLE`.

`NOT_EVALUABLE` no se transforma en `NOT_VIABLE`, rechazo ni decisión.

## 7. Comparación e invocador Vertical

La comparación se ejecuta mediante el motor cerrado `compare_alternatives(...)` y se adapta al boundary O1 mediante `adapt_twin(...)`.

El invocador público debe tener la forma:

`(PurchaseOperation, DecisionContext) -> CapabilityExecution`.

La construcción del invocador congela una copia profunda de preparación, entradas provenanced y referencias de representación para impedir mutaciones posteriores del llamador.

## 8. Fail closed

Debe fallar antes de producir una comparación cuando exista cualquiera de estas condiciones:

- menos de dos alternativas;
- `representation_ref` vacía o duplicada;
- `scenario_id` analítico duplicado;
- contexto raíz extranjero;
- PurchaseOperation extranjero;
- cobertura Stage-2 incompleta o sobrante;
- Assessment/Trace no reproducible;
- `ViabilityResult` incoherente con escenario/versiones/snapshot.

No se añadirá compatibilidad que acepte resultados Decision Twin opacos.

## 9. Fuera de alcance

Esta unidad no:

- corrige la procedencia de QTG;
- crea persistencia de Alternative;
- crea `Alternative_ID`;
- modifica VF/O3/C0;
- selecciona, recomienda, aprueba o rechaza alternativas;
- modifica `run_mvp_execution`, que ya exige un invocador explícito desde PR #113.

## 10. Criterio de cierre

La unidad solo podrá declararse cerrada cuando:

1. implementación y tests respeten este contrato;
2. Auditoría 2 no encuentre rutas de re-etiquetado ni autoridad nueva;
3. CI de PR sea satisfactoria sobre el head exacto;
4. el merge se realice sobre ese head;
5. CI post-merge resulte satisfactoria.
