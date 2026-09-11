# EIOS — O2 ↔ O3 Integration Contract v0.1

**Estado:** CERRADO PARA IMPLEMENTACIÓN
**Ámbito:** adaptación de `ScenarioEvaluationResult` (O3) a `O2ScenarioResult` (O2)

## Propósito

Conectar dos componentes ya cerrados sin modificar su semántica ni reabrir sus contratos internos.

## Entrada

`PurchaseOperation` + `DecisionContext` + uno o más `ScenarioEvaluationResult` ya producidos por O3.

## Salida

`O2SupportPackage` construido mediante las funciones públicas existentes de O2.

## Mapeo autorizado

- `scenario_id` → copia literal.
- estados O3 con valor idéntico en O2 → copia literal.
- `assessments` no vacíos → `values["assessments"]`.
- `viability_result` no nulo → `values["viability_result"]`.
- `limitations` → `unresolved_items`, sin reinterpretar su contenido.
- `trace_references` → copia literal.
- `failure_reason` → copia literal.

La ausencia de `assessments` o `viability_result` se conserva omitiendo esa clave de `values`; no se fabrica `None`, `False` ni resultado sustitutorio.

## Validaciones obligatorias

1. `PurchaseOperation.decision_id == DecisionContext.decision_id`.
2. `PurchaseOperation.scenario_id == DecisionContext.scenario_id`.
3. Cada resultado O3 debe coincidir con el contexto en `decision_id`, `rules_version`, `parameters_version` y `data_snapshot_id`.
4. Los `scenario_id` deben seguir siendo únicos mediante las validaciones O2 existentes.
5. Solo se permiten estados con equivalencia literal O3 ↔ O2.
6. `NOT_STARTED` falla cerrado: no se convierte a `READY`, `BLOCKED` ni otro estado.

## Invariantes

- No ejecutar O3, Rules Engine, Viability Frontier ni otra capacidad.
- No recalcular Assessments ni viabilidad.
- No mutar `PurchaseOperation`, `DecisionContext` ni resultados O3.
- No crear score, ranking, selección, recomendación, aprobación, rechazo u optimización.
- No modificar `eios/core/o2.py` ni `eios/core/scenario_evaluation.py` salvo contradicción objetiva posterior.

## Auditoría previa

**APTO PARA IMPLEMENTACIÓN.** El adaptador cierra una frontera física entre dos componentes existentes y conserva estados, ausencias, contexto y trazabilidad sin introducir semántica decisional nueva.
