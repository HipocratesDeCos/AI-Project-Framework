# EIOS — Assessment + Trace Provenance Integration Contract v0.1

**Estado:** AUDITORÍA 2 SUPERADA — PENDIENTE CI  
**Baseline:** `main @ f021e3725b6c9bc22f494b93077252dad00d7dd6`  
**Ámbito:** cerrar la brecha de procedencia de Assessments ya producidos antes de reutilizarlos en Rules/CRC/O1 o en integraciones posteriores.

## 1. Problema objetivo

`Assessment` es deliberadamente context-free y debe permanecer así. Contiene `rule_id`, `status`, `outcome`, `evidence_ids` y `reason`, mientras que el contexto reproducible vive en `Trace`.

Las rutas actuales que reciben un `Assessment` separado y generan un `Trace` posteriormente con un contexto nuevo pueden atribuir ese Assessment al contexto de ejecución sin prueba de que se produjo allí.

## 2. Hallazgo de Auditoría 1

El diseño inicial `Assessment + Trace` seguía siendo insuficiente: el `Trace` físico vigente vinculaba `rule_id`, status, outcome, evidencias, contexto e input, pero no `Assessment.reason`.

CRC sí consume `Assessment.reason` como explicación/dominant reason. Por tanto, un `Assessment` podía cambiar su `reason` después de producirse y conservar un Trace aparentemente válido.

Esto constituye una contradicción objetiva de reproducibilidad y justifica reabrir únicamente la superficie técnica de `Trace`/fingerprint C0.

## 3. Refuerzo mínimo de Trace

Se añade a `Trace`:

`assessment_fingerprint: str | None`

Compatibilidad:
- el campo es opcional para poder leer/construir trazas legacy existentes;
- todo nuevo `build_trace(...)` C0 debe producirlo;
- cualquier ruta provenance-safe debe rechazar un Trace con `assessment_fingerprint=None`.

No se añade contexto a `Assessment` y no se modifica su contrato semántico.

## 4. Fingerprint canónico de Assessment

Se incorpora `assessment_fingerprint(assessment)` usando el mismo patrón técnico SHA-256/canonical JSON de `input_fingerprint`.

El payload canónico incluye exhaustivamente el `Assessment` físico:
- `rule_id`;
- `status`;
- `outcome`;
- `evidence_ids` en su orden contractual;
- `reason`.

La canonicalización ordena claves JSON, no reordena `evidence_ids` ni introduce semántica empresarial.

El fingerprint del Assessment se incorpora al material determinista de `trace_id`. Cambiar cualquier campo material del Assessment, incluido `reason`, cambia el fingerprint y el `trace_id`.

`created_at` permanece fuera de la identidad reproducible.

## 5. Unidad de procedencia

Se introduce `AssessmentTraceBinding`:
- `assessment: Assessment`;
- `trace: Trace`.

El binding no fusiona ambos conceptos ni crea autoridad analítica. Solo conserva juntos un resultado individual y su evidencia contextual.

## 6. Validación contextual completa

Para reutilizar un binding se valida contra `PurchaseOperation`, `DecisionContext` y la `Rule` autorizada:

- compra y contexto comparten `decision_id` y `scenario_id`;
- Trace coincide con contexto en `decision_id`, `scenario_id`, `rules_version`, `parameters_version`, `data_snapshot_id`;
- `Trace.rule_id == Assessment.rule_id == Rule.rule_id`;
- `Rule.version == DecisionContext.rules_version`;
- status, outcome y evidencias de Trace coinciden con Assessment;
- `Trace.input_fingerprint` coincide con el fingerprint canónico de la compra;
- `Trace.assessment_fingerprint` existe y coincide con el fingerprint del Assessment completo;
- `Trace.trace_id` coincide con el identificador determinista que `build_trace` produciría para ese mismo material.

Un Trace legacy sin fingerprint del Assessment no constituye prueba suficiente para esta reutilización y falla cerrado.

## 7. Runtime provenance-safe

Se añade una ruta separada `run_provenanced_assessments_vertical(...)` que:
1. recibe bindings ya producidos;
2. resuelve Rule y RuleMetadata desde el catálogo autorizado;
3. valida cada par contra compra/contexto/regla;
4. preserva los Trace suministrados, incluido `created_at`;
5. no genera trazas nuevas para atribuir Assessments desconectados;
6. reutiliza `adapt_c0`, CRC y O1 sin cambiar sus semánticas;
7. rechaza `rule_id` duplicados.

## 8. Invoker E2E provenance-safe

Se añade `build_provenanced_rules_engine_c0_invoker(...)`.

El constructor congela los bindings. Cada invocación valida el material contra el `PurchaseOperation` y `DecisionContext` recibidos. Material producido para otra decisión, escenario, versión, snapshot o input falla cerrado.

## 9. Compatibilidad legacy

No se eliminan todavía las APIs basadas en Assessments sueltos para evitar una rotura transversal no auditada:
- `run_assessment_set_vertical`;
- `run_authorized_assessments_vertical`;
- `run_rules_engine` / `RulesEngineInput`;
- `build_rules_engine_c0_invoker`.

Quedan clasificadas como compatibilidad legacy no apta para transportar Assessments preproducidos entre contextos. Su migración/retirada será una unidad posterior específica.

## 10. Autoridades preservadas

- Assessment: resultado individual.
- Trace: reproducibilidad contextual.
- C0: fingerprint e identidad reproducible.
- Rules catalog: Rule y metadata autorizadas.
- CRC: consolidación.
- O1: soporte.

No se reevalúan reglas, no se modifican outcomes y no se crea decisión.

## 11. Fail-closed

Se rechaza:
- Trace de otra decisión/escenario;
- versiones o snapshot distintos;
- input fingerprint distinto;
- `assessment_fingerprint` ausente o distinto;
- `trace_id` no reproducible;
- rule_id/status/outcome/evidence incoherentes;
- Assessment con `reason` modificado respecto a la traza;
- regla no materializada o versión distinta;
- duplicados;
- binding de tipo incorrecto.

Un fallo de procedencia no se convierte en `NOT_EVALUABLE`, FALSE, no viable, rechazo ni decisión.

## 12. Inmutabilidad

Bindings, Assessments y Traces se copian profundamente antes de usarse. La ejecución no muta entradas ni reescribe los Trace recibidos.

## 13. Fuera de alcance

- añadir contexto a Assessment;
- cambiar semántica empresarial de C0/CRC/O1;
- ejecutar reglas específicas;
- retirar todas las APIs legacy en esta unidad;
- escenarios/O3/VF;
- score, ranking, recomendación, selección, aprobación o rechazo empresarial;
- UI, persistencia o SQL.

## 14. Criterios de aceptación

1. C0 nuevo produce `assessment_fingerprint` de 64 caracteres;
2. mismo Assessment produce fingerprint estable;
3. cambiar `reason` cambia fingerprint y `trace_id`;
4. Trace legacy sin fingerprint sigue siendo construible pero no reusable por la ruta segura;
5. binding canónico del mismo contexto se acepta;
6. Trace original y `created_at` se preservan;
7. decisión/escenario/versiones/snapshot ajenos fallan;
8. input fingerprint ajeno falla;
9. fingerprint o trace_id manipulados fallan;
10. status/outcome/evidence/reason incoherentes fallan;
11. regla no autorizada y duplicados fallan;
12. runtime seguro produce CRC/O1 coherentes con el material validado;
13. invoker seguro no puede reutilizar bindings en otro contexto;
14. inputs permanecen inmutables;
15. NOT_EVALUABLE conserva semántica;
16. no aparece autoridad decisional.

## 15. Auditoría 1

**Hallazgo:** el Trace previo no vinculaba `Assessment.reason`, pese a que CRC puede consumirlo.

**Depuración:** fingerprint exhaustivo del Assessment + inclusión del hash en `trace_id` + ruta segura que exige dicho fingerprint. Se conserva compatibilidad de lectura/construcción de Trace legacy mediante campo opcional, pero legacy no se considera prueba suficiente de procedencia.

**DICTAMEN TRAS DEPURACIÓN:** APTO PARA IMPLEMENTACIÓN.

## 16. Auditoría 2

Se ha verificado el diff completo frente al baseline:

- no se modifica ninguna regla específica ni sus condiciones empresariales;
- no se modifica CRC, O1, O2, O3, Viability Frontier ni presentación;
- `Assessment` permanece sin contexto adicional;
- `Trace` solo incorpora un campo técnico opcional de reproducibilidad;
- las trazas nuevas C0 quedan ligadas al Assessment completo;
- las trazas legacy siguen siendo construibles, pero no son aceptadas como prueba de procedencia por la nueva ruta;
- la API legacy permanece disponible y separada;
- la API provenance-safe se expone explícitamente;
- los tests cubren `reason`, fingerprint, `trace_id`, contexto extranjero, fingerprint de input, legacy, incoherencias status/outcome/evidence, regla no catalogada, duplicados, NOT_EVALUABLE, inmutabilidad e invoker E2E;
- no aparece score, ranking, recomendación, selección, aprobación, rechazo ni autoridad decisional.

**DICTAMEN AUDITORÍA 2:** SUPERADA — SIN BLOQUEADORES DE DISEÑO.

## 17. Hallazgo CI #678 y depuración

La primera CI sobre PR #105 ejecutó 804 tests: 803 pasaron y uno antiguo falló.

El fallo no era productivo. `build_support_package` ordena y deduplica por contrato las `trace_references` mediante `sorted(set(...))`; el test `test_batch_crc_resolves_multiple_active_rules_by_effect_priority` asumía accidentalmente que el orden de UUID de Trace coincidía con el orden de las reglas. El refuerzo del material de `trace_id` cambió los UUID y expuso esa dependencia no contractual.

**Depuración:** el test se corrige para afirmar la ordenación canónica de O1. No se modifica `build_support_package`, CRC, Rules runtime ni ninguna semántica empresarial.

**Cierre técnico definitivo:** condicionado a una nueva CI completa sobre el head corregido de la PR y posterior CI de `main`.
