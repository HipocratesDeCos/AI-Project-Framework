# EIOS — Vertical MVP TCO Context Integrity Contract v0.1

**Estado:** CERRADO PARA MATERIALIZACIÓN  
**Baseline:** `main @ 70f3dda1a0b90ab6fd42212474de6ee6c7b025d8`  
**Ámbito:** composición de resultados `TCOResult` preproducidos dentro de `run_mvp_execution`.

## 1. Propósito

Cerrar el hueco por el que una ejecución Vertical podía incorporar un resultado TCO perteneciente a otra propuesta decisional o a otro escenario.

La validación es exclusivamente de identidad contextual. No recalcula TCO ni amplía el TCO Core.

## 2. Autoridad existente

Este contrato deriva exclusivamente de autoridades ya cerradas:

- `TCO_Core_Implementation_Contract.md`: TCO evalúa una propuesta de compra, exige relación trazable entre costes y propuesta y no crea autoridad decisional.
- `eios/tco/engine.py`: `calculate_tco` construye `TCOResult.decision_id` y `scenario_id` directamente desde `PurchaseOperation`.
- `E2E_Execution_Boundary_Implementation_Contract.md`: una ejecución Vertical debe rechazar identidad inconsistente.
- `DecisionContext`: autoridad física para `decision_id` y `scenario_id` de la ejecución.

## 3. Regla cerrada

Cuando `run_mvp_execution` recibe `tco_result`, antes de crear el snapshot/invocador TCO debe verificar igualdad exacta de:

```text
tco_result.decision_id == context.decision_id
tco_result.scenario_id == context.scenario_id
```

Una desigualdad en cualquiera de estos campos es una inconsistencia estructural y produce `ValueError` antes de `execute_plan`.

## 4. Límites

La validación:

- no recalcula TCO;
- no modifica componentes, valor, limitaciones ni completitud;
- no transforma ausencia en cero;
- no interpreta un TCO incompleto como rechazo;
- no valida `data_snapshot_id`, `rules_version` o `parameters_version`, porque `TCOResult` no transporta esos campos;
- no crea identidad paralela, fingerprint o `decision_version`;
- no modifica `PurchaseOperation`, `DecisionContext` ni `TCOResult`;
- no resuelve GAP-TCO-01 ni GAP-TCO-02.

## 5. Orden fail-closed

La identidad TCO se valida durante la construcción del catálogo de ejecución, antes del snapshot y antes de `execute_plan`. Si falla, ninguna capacidad del plan llega a ejecutarse.

## 6. Auditoría 1

Hallazgo confirmado: `run_mvp_execution` incorporaba `TCOResult` mediante snapshot/adaptación sin comprobar que `decision_id` y `scenario_id` correspondieran al contexto Vertical actual.

El engine TCO demuestra que ambos campos proceden de la propuesta canónica evaluada, por lo que su comparación no introduce semántica nueva.

## 7. Depuración

Se descartan endurecimientos no autorizados:

- solo se comparan `decision_id` y `scenario_id`;
- moneda sigue siendo semántica propia de TCO, no identidad de `DecisionContext`;
- no se añade snapshot/versionado ausente del resultado físico;
- no se reabre el Core TCO ni sus GAPs.

## 8. Criterios de aceptación

1. TCO con decisión y escenario coincidentes se integra sin regresión.
2. `decision_id` distinto se rechaza antes de ejecutar.
3. `scenario_id` distinto se rechaza antes de ejecutar.
4. Si ambos difieren, el error identifica ambos campos.
5. TCO completo e incompleto conservan su semántica existente cuando la identidad coincide.
6. La inconsistencia evita ejecutar cualquier otra capacidad.
7. Resultado y contexto permanecen inmutados.
8. No se añade autoridad decisional ni se resuelven GAPs TCO.

## 9. Materialización prevista

```text
eios/core/mvp_execution.py
tests/test_mvp_tco_context_integrity.py
```

## 10. Método

**DISEÑAR → AUDITAR → DEPURAR → AUDITAR 2 → CERRAR → MATERIALIZAR → CI**
