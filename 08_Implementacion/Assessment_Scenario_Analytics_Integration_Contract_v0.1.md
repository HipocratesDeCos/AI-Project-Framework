# EIOS — Assessment + Trace → Scenario Analytics Integration Contract v0.1

**Estado:** AUDITORÍA 2 SUPERADA — PENDIENTE CI  
**Baseline:** `main @ 696823c0c8a53a3a2ca5faf1b84774fe0eed3995`  
**Ámbito:** cerrar la procedencia de los Assessment C0 que alimentan `AuthorizedScenarioAnalytics` sin reejecutar reglas, Viability Frontier ni O3.

## 1. Problema objetivo

La frontera VF→Scenario Analytics ya valida un `ViabilityResult` tipado contra un escenario O2 `VALID`, pero recibe `assessments: tuple[Any, ...]`. Por tanto, la procedencia del VF queda demostrada mientras la de los Assessment C0 puede seguir siendo opaca.

PR #105 cerró la procedencia reusable de `Assessment + Trace`. Esta unidad conecta esa evidencia ya validable con la frontera analítica de escenarios.

## 2. Fronteras de autoridad

- C0 `Assessment`: resultado individual de regla.
- C0 `Trace`: procedencia y reproducibilidad del Assessment.
- O2 `ScenarioVersion`: identidad del escenario.
- Viability Frontier: resultado de viabilidad ya producido.
- O3: construcción del resultado de evaluación a partir de analítica ya producida.

Esta integración no evalúa reglas, no ejecuta VF, no ejecuta O3 y no crea decisión empresarial.

## 3. Contexto del escenario hijo

`O4O2O3Preparation.context.scenario_id` identifica el contexto base usado por O4/O2. Un `ScenarioVersion` materializado por O2 posee su propio `scenario_id`.

Para validar Assessment+Trace de un escenario O2 se deriva un `DecisionContext` analítico con:

- `decision_id` = preparación;
- `scenario_id` = `ScenarioVersion.scenario_id` objetivo;
- `rules_version` = preparación;
- `parameters_version` = preparación;
- `data_snapshot_id` = preparación.

No se valida un Assessment del escenario hijo contra el `scenario_id` base.

## 4. PurchaseOperation analítica explícita

La integración recibe un `PurchaseOperation` explícito perteneciente al escenario hijo para validar el `input_fingerprint` de los Trace.

Debe cumplir:
- mismo `decision_id` que la preparación;
- `scenario_id` igual al escenario O2 objetivo.

Esta unidad **no afirma** que dicho PurchaseOperation materialice semánticamente todos los `ScenarioVersion.changes`. No existe un mapping genérico autorizado O2-change→PurchaseOperation y no se inventará.

## 5. AssessmentTraceBinding

Cada Assessment se recibe como `AssessmentTraceBinding` de PR #105.

La integración reutiliza la validación provenance-safe y exige:
- Trace del mismo decision/scenario/version/snapshot;
- input fingerprint del PurchaseOperation suministrado;
- Assessment fingerprint completo;
- `trace_id` determinista reproducible;
- Rule catalogada en la versión del contexto.

Trazas legacy sin `assessment_fingerprint` fallan cerrado.

## 6. Assessment transport payload

Tras validar el binding tipado, el Assessment se transporta en forma canónica JSON-compatible con **solo** sus campos contractuales:

- `rule_id`;
- `status`;
- `outcome`;
- `evidence_ids`;
- `reason`.

No se fusionan campos de Trace dentro del Assessment. Los `trace_id` validados se transportan separadamente mediante `AuthorizedScenarioAnalytics.trace_references`.

## 7. Relación con Viability Frontier

El `ViabilityResult` se delega a la frontera ya cerrada `build_authorized_analytics_from_viability(...)`, que valida decisión, escenario y versiones/snapshot y produce su payload canónico.

**Separación obligatoria:**

`ViabilityResult.assessment_ids` identifica `FrontierAssessment.assessment_id`.

C0 `Assessment` no tiene `assessment_id`.

Por tanto:
- no se igualan IDs;
- no se exige que `ViabilityResult.rule_ids` coincida con los C0 Assessment;
- no se exige que los trace refs de VF coincidan con los C0 Trace;
- no se afirma causalidad entre ambos conjuntos.

Son dos analíticas preproducidas, autorizadas independientemente y vinculadas al mismo escenario.

## 8. Trazas del paquete

`AuthorizedScenarioAnalytics.trace_references` se deriva exclusivamente y en orden de los `Trace.trace_id` de bindings C0 validados.

La función segura no acepta trace references arbitrarios del caller.

## 9. Estados

El estado O3 (`ScenarioEvaluationStatus`) permanece explícito y no se deriva del estado de Viability Frontier ni del status de un Assessment.

En particular:
- `NOT_EVALUABLE` de un Assessment no se transforma en FALSE;
- `NOT_VIABLE` de VF no se transforma en FAILED/rejection de O3;
- ningún estado produce recomendación o decisión.

## 10. Fail-closed

Se rechaza antes de O3:
- escenario inexistente, duplicado o no VALID;
- bindings vacíos;
- rule_id C0 duplicados;
- PurchaseOperation de otra decisión/escenario;
- Trace de contexto distinto;
- fingerprint de input distinto;
- fingerprint de Assessment ausente/distinto;
- trace_id manipulado;
- Assessment/Trace incoherentes;
- regla no catalogada;
- ViabilityResult de otro contexto/versión/snapshot.

## 11. Inmutabilidad

Preparation, PurchaseOperation, bindings, Assessment, Trace y ViabilityResult se copian antes de validación/transporte. No se mutan entradas.

## 12. Fuera de alcance

- materializar automáticamente cambios O2 en PurchaseOperation;
- ejecutar reglas/C0, VF u O3;
- vincular C0 Assessment con FrontierAssessment por IDs;
- retirar APIs legacy de Rules;
- modificar O2/O3/VF;
- score, ranking, recomendación, selección, aprobación, rechazo o decisión;
- UI, persistencia o SQL.

## 13. Criterios de aceptación

1. binding C0 canónico del escenario hijo + VF tipado producen `AuthorizedScenarioAnalytics`;
2. Assessment se transporta con campos contractuales exactos;
3. trace references se derivan solo de Trace validados;
4. Trace del escenario base/ajeno falla;
5. decisión/versiones/snapshot ajenos fallan;
6. PurchaseOperation ajeno o con fingerprint distinto falla;
7. reason manipulado falla;
8. Trace legacy falla;
9. duplicados y bindings vacíos fallan;
10. escenario desconocido/DRAFT falla;
11. VF ajeno sigue fallando mediante su frontera cerrada;
12. `NOT_EVALUABLE` se preserva;
13. VF y C0 pueden usar identificadores distintos sin falsa vinculación;
14. status O3 explícito no se deriva de VF;
15. Stage 2 O3 consume correctamente el paquete;
16. inputs permanecen inmutables;
17. no aparece autoridad decisional.

## 14. Auditoría 1

Se comprobó la frontera contra O2, PR #99, PR #104 y PR #105.

Hallazgos/resoluciones:
- el `DecisionContext` de validación debe usar el `scenario_id` del hijo O2, no el `scenario_id` base de `preparation.context`;
- el `PurchaseOperation` del hijo se utiliza exclusivamente como material reproducible para comprobar `input_fingerprint`; no certifica una materialización genérica de `ScenarioVersion.changes`;
- `ViabilityResult.assessment_ids` pertenece al dominio `FrontierAssessment` y no puede equipararse a C0 `Assessment`;
- no existe circularidad de dependencias al situar el bridge en `eios/rules`;
- la validación reusable se expone de forma aditiva mediante `validate_assessment_trace_binding(...)`, sin reabrir la semántica del runtime Rules cerrado.

**DICTAMEN AUDITORÍA 1:** SUPERADA TRAS INCORPORAR LAS SALVAGUARDAS ANTERIORES.

## 15. Auditoría 2

Diff contra baseline:
- rama 5 commits por delante, 0 por detrás;
- 5 archivos afectados;
- 3 archivos añadidos: contrato, bridge y tests;
- 2 modificaciones aditivas: export público del validador provenance-safe y exports de `eios.rules`;
- O2, O3, VF, reglas específicas, CRC, O1, Vertical y presentación no se modifican.

Comprobaciones:
- no se invoca `evaluate_viability`, `evaluate_scenario`, `run_rules_engine` ni otra ejecución analítica;
- no se aceptan trace references libres del caller;
- no se deriva estado O3 desde VF;
- no se enlaza C0 Assessment con FrontierAssessment por identificadores;
- no se materializan cambios O2 en PurchaseOperation;
- Assessment y Trace permanecen separados;
- la salida usa el `AuthorizedScenarioAnalytics` ya autorizado por PR #99/104;
- la cobertura llega hasta Stage 2 O3 y presentación Vertical sin añadir autoridad decisional.

**DICTAMEN AUDITORÍA 2:** SUPERADA — SIN BLOQUEADORES DE DISEÑO.  
**Cierre definitivo:** condicionado a CI completa sobre el head exacto de la PR y CI post-merge sobre `main`.
