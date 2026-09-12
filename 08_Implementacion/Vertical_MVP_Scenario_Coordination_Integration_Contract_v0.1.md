# EIOS — Vertical MVP Scenario Coordination Integration Contract v0.1

**Estado:** CERRADO PARA IMPLEMENTACIÓN
**Autoridad:** ampliación expresamente autorizada por el propietario del proyecto
**Ámbito:** O3 → O2 → Vertical MVP

## 1. Propósito

Incorporar al flujo Vertical MVP resultados de evaluación de escenarios ya producidos por O3 y coordinados por O2, sin convertir la simulación en decisión empresarial ni duplicar O2 y O3 como capacidades verticales independientes.

La cadena se representa en el ejecutor Vertical MVP mediante una sola capacidad técnica:

`SCENARIO_COORDINATION`

## 2. Entrada autorizada

`run_vertical_mvp_support` puede recibir opcionalmente una secuencia de `ScenarioEvaluationResult` ya producidos por O3.

La fachada:

1. no ejecuta O3;
2. construye `O2SupportPackage` exclusivamente mediante `build_o2_support_from_o3`;
3. conserva dicho paquete completo en `VerticalMVPSupportResult.scenario_support`;
4. adapta el paquete O2 a un único `CapabilityExecution` denominado `SCENARIO_COORDINATION` para la frontera E2E.

`run_mvp_execution`, al aceptar directamente un `O2SupportPackage`, debe validar antes de registrarlo que `decision_id`, `rules_version`, `parameters_version` y `data_snapshot_id` coinciden con el `DecisionContext` de la ejecución. Un paquete O2 ajeno falla cerrado.

Si no se suministran resultados O3, el comportamiento Vertical MVP existente permanece inalterado.

## 3. Posición canónica

`SCENARIO_COORDINATION` se sitúa después de `DECISION_TWIN` y antes de `NEGOTIATION_INTELLIGENCE`.

La posición expresa secuencia técnica de presentación/coordinación; no implica preferencia, ranking ni autoridad decisional.

## 4. Política de estados

El adaptador O2 → O1/Vertical no crea estados nuevos.

- todos los escenarios `COMPLETED` → `COMPLETED`, `result_available=True`;
- cualquier escenario `FAILED` → `FAILED`, `result_available=False`;
- si todos comparten el mismo estado no `FAILED`, dicho estado se conserva literalmente y `result_available=False` salvo `COMPLETED`;
- mezcla de estados no fallidos → `PARTIALLY_COMPLETED`, `result_available=False`.

`NOT_EVALUABLE ≠ FALSE`, `FAILED ≠ rechazo empresarial` y `PARTIALLY_COMPLETED ≠ recomendación`.

## 5. Trazabilidad y no resueltos

- Las referencias de traza se agregan de forma determinista y sin duplicados desde los escenarios O2.
- Los elementos no resueltos del `CapabilityExecution` se etiquetan con `scenario_id` para no perder su asociación.
- Los estados incompletos sin texto de limitación se conservan mediante un marcador técnico `scenario_id:STATUS`.
- Los motivos detallados de fallo permanecen en `O2SupportPackage`; el `CapabilityExecution` solo identifica determinísticamente los escenarios fallidos.

## 6. Invariantes

1. O3 no se ejecuta ni recalcula desde esta integración.
2. O2 se construye usando exclusivamente el bridge O2↔O3 ya validado cuando la entrada procede de la fachada Vertical.
3. Una entrada O2 directa al ejecutor se valida contra el `DecisionContext`; no puede cruzar decisiones, versiones ni snapshots.
4. No se mutan `PurchaseOperation`, `DecisionContext`, resultados O3 ni paquetes O2 suministrados.
5. No se crean score, ranking, selección, recomendación, aprobación, rechazo u optimización.
6. No se interpreta el contenido de Assessments ni de Viability Frontier.
7. La identidad/versiones/snapshot siguen validadas por O2↔O3 y por el gate directo del ejecutor.
8. `NOT_STARTED` continúa fallando cerrado en el bridge O2↔O3; no se convierte a `READY`.
9. `scenario_support` es soporte descriptivo y nunca decisión del CEO.
10. La ausencia de escenarios significa capacidad no suministrada; no genera un resultado sintético.
11. Los componentes cerrados O2 y O3 no se modifican.

## 7. Fuera de alcance

- ejecutar o generar escenarios;
- modificar O2/O3;
- modificar CRC o reglas de negocio;
- conectar todavía la nueva sección a HTML/UI;
- alterar Negotiation Intelligence/Ladder;
- automatizar una decisión humana.

## 8. Auditoría previa

**APTO PARA IMPLEMENTACIÓN.** La autoridad explícita permite ampliar el catálogo Vertical MVP, y la solución preserva las fronteras de O1, O2, O3, Decision Twin y negociación sin crear doble contabilización ni autoridad decisional nueva.
