# EIOS — O2 Implementation Contract

**Estado:** CERRADO PARA MATERIALIZACIÓN
**Ámbito:** Coordinated Decision Support / Scenario Coordination

## Entrada

`PurchaseOperation` + `DecisionContext` + resultados de escenarios ya producidos.

## Salida

`O2SupportPackage` con contexto de ejecución, escenarios y comparación descriptiva cuando existen al menos dos escenarios.

## Invariantes físicas

1. La identidad de decisión procede de `DecisionContext`.
2. Los `scenario_id` son únicos dentro del paquete.
3. El orden de entrada no altera la identidad de ejecución ni el paquete final.
4. Reglas, parámetros y `data_snapshot_id` se conservan.
5. Estados técnicos no se convierten en resultados empresariales.
6. Valores ausentes y elementos no resueltos se conservan explícitamente.
7. Trazas permanecen asociadas al escenario.
8. `PurchaseOperation` no se muta.
9. La comparación es descriptiva.
10. No existe ranking, score, selección, recomendación, aprobación, rechazo ni optimización.
11. Los modelos físicos son inmutables y rechazan campos adicionales.

## Identidad de ejecución

Se deriva determinísticamente de `decision_id`, versiones, snapshot y conjunto normalizado de escenarios. No constituye una nueva identidad empresarial.

## No alcance

O2 no implementa nuevas capacidades económicas, reglas de negocio, persistencia, API ni decisión empresarial.

**O2 — CONTRATO DE IMPLEMENTACIÓN: CERRADO.**