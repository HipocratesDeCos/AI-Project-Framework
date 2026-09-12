# EIOS — Assessment + Trace Provenance Integration Contract v0.1

**Estado:** DISEÑO PARA AUDITORÍA  
**Baseline:** `main @ f021e3725b6c9bc22f494b93077252dad00d7dd6`  
**Ámbito:** cerrar la brecha de procedencia de Assessments ya producidos antes de reutilizarlos en Rules/CRC/O1 o en integraciones posteriores.

## 1. Problema objetivo

`Assessment` es deliberadamente context-free: contiene `rule_id`, `status`, `outcome`, `evidence_ids` y `reason`, pero no `decision_id`, `scenario_id`, versiones ni snapshot.

El contexto reproducible vive en `Trace`.

Las rutas actuales que reciben un `Assessment` separado y generan un `Trace` posteriormente con un `PurchaseOperation`/`DecisionContext` nuevo pueden atribuir materialmente ese Assessment al contexto de ejecución sin prueba de que se produjo allí.

La corrección no añadirá contexto dentro de `Assessment`; preservará su contrato cerrado.

## 2. Unidad de procedencia

Se introduce `AssessmentTraceBinding`:

- `assessment: Assessment`;
- `trace: Trace`.

El binding no fusiona ambos conceptos ni crea una nueva autoridad analítica. Solo conserva juntos el resultado individual y su evidencia de contexto reproducible.

## 3. Validación contextual

Para reutilizar un binding en un contexto, debe validarse contra:

- `PurchaseOperation`;
- `DecisionContext`;
- `Rule` autorizado para `assessment.rule_id` y `context.rules_version`.

La validación exige:

- `PurchaseOperation.decision_id == DecisionContext.decision_id`;
- `PurchaseOperation.scenario_id == DecisionContext.scenario_id`;
- `Trace.decision_id == DecisionContext.decision_id`;
- `Trace.scenario_id == DecisionContext.scenario_id`;
- `Trace.rules_version == DecisionContext.rules_version`;
- `Trace.parameters_version == DecisionContext.parameters_version`;
- `Trace.data_snapshot_id == DecisionContext.data_snapshot_id`;
- `Trace.rule_id == Assessment.rule_id == Rule.rule_id`;
- `Rule.version == DecisionContext.rules_version`;
- `Trace.assessment_status == Assessment.status`;
- `Trace.assessment_outcome == Assessment.outcome`;
- `Trace.evidence_ids == tuple(Assessment.evidence_ids)`;
- `Trace.input_fingerprint` coincide con el fingerprint canónico de la compra;
- `Trace.trace_id` coincide con el `trace_id` determinista que produciría el contrato C0 para ese mismo material.

`created_at` no forma parte de la igualdad reproducible: es metadato temporal de creación y no participa en `trace_id`.

## 4. Runtime provenance-safe

Se añade una ruta separada:

`run_provenanced_assessments_vertical(...)`

Esta operación:

1. recibe bindings `Assessment + Trace` ya producidos;
2. valida cada par contra compra/contexto/regla autorizada;
3. preserva los Trace suministrados; no genera trazas nuevas para atribuir Assessments desconectados;
4. reutiliza las autoridades cerradas `adapt_c0`, CRC y O1;
5. conserva orden y rechazo de `rule_id` duplicados.

## 5. Invoker E2E provenance-safe

Se añade:

`build_provenanced_rules_engine_c0_invoker(...)`

El constructor recibe bindings ya trazados y los congela. En cada invocación valida esos bindings contra el `PurchaseOperation` y `DecisionContext` recibidos.

Un invoker construido con material de una decisión/escenario no puede ejecutarse silenciosamente en otro contexto: debe fallar cerrado.

## 6. Compatibilidad legacy

Las APIs existentes basadas en Assessments sueltos no se eliminan en esta unidad para evitar una rotura transversal no auditada.

Quedan explícitamente clasificadas como **compatibilidad legacy no apta para reutilización de Assessments desconectados entre contextos**:

- `run_assessment_set_vertical`;
- `run_authorized_assessments_vertical`;
- `run_rules_engine` / `RulesEngineInput` mientras solo acepten Assessments;
- `build_rules_engine_c0_invoker`.

La nueva ruta provenance-safe será la única autorizada para material analítico preproducido cuya procedencia deba sobrevivir entre fronteras.

La migración o retirada de las APIs legacy requerirá una unidad posterior específica tras inventariar todos sus consumidores.

## 7. Autoridades preservadas

- `Assessment` mantiene su semántica de resultado individual.
- `Trace` mantiene autoridad de reproducibilidad contextual.
- C0 mantiene la canonicalización/fingerprint/trace_id.
- Rules catalog mantiene autoridad sobre Rule y metadata implementadas.
- CRC mantiene consolidación.
- O1 mantiene empaquetado de soporte.

Esta unidad no reevalúa reglas ni cambia outcomes.

## 8. Fail-closed

Se rechaza:

- Trace de otra decisión o escenario;
- cualquier versión/snapshot distinto;
- fingerprint distinto;
- `trace_id` no reproducible;
- rule_id distinto;
- status/outcome/evidence distintos entre Assessment y Trace;
- regla no materializada;
- rule version distinta;
- rule_id duplicado en una ejecución;
- binding de tipo incorrecto.

Ningún fallo de procedencia se convierte en `NOT_EVALUABLE`, FALSE, no viable, rechazo empresarial ni decisión.

## 9. Inmutabilidad

Bindings, Assessments y Traces se copian antes de usarse. La ejecución no muta entradas ni reescribe los Trace recibidos.

## 10. Fuera de alcance

- añadir contexto a `Assessment`;
- cambiar semántica de C0/CRC/O1;
- ejecutar reglas específicas;
- reparar/migrar todas las APIs legacy en esta misma unidad;
- escenarios/O3/VF;
- score, ranking, recomendación, selección, aprobación o rechazo empresarial;
- UI, persistencia o SQL.

## 11. Criterios de aceptación

1. un par Assessment+Trace canónico del mismo contexto se acepta;
2. el Trace original se preserva, incluido `created_at`;
3. decisión ajena falla cerrada;
4. escenario ajeno falla cerrada;
5. versiones/snapshot ajenos fallan;
6. fingerprint ajeno falla;
7. trace_id manipulado falla;
8. status/outcome/evidence incoherentes fallan;
9. regla no autorizada falla;
10. duplicados fallan;
11. runtime seguro produce el mismo CRC/O1 que el material canónico equivalente;
12. invoker seguro no puede reutilizar bindings en otro contexto;
13. inputs permanecen inmutables;
14. NOT_EVALUABLE conserva su semántica;
15. no aparece autoridad decisional.

**DICTAMEN DE DISEÑO:** pendiente de Auditoría 1.
