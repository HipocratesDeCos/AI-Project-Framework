# EIOS — Scenario Stage 2 Provenance Boundary Contract v0.1

**Estado:** AUDITORÍA 2 SUPERADA — PENDIENTE CI  
**Baseline:** `main @ 5e5243d4e5245991c5e6db515aaff14e3840a059`  
**Ámbito:** separar la mecánica interna O4→O2→O3 Stage 2 de la frontera externa autorizada, de modo que la finalización pública no pueda recibir `Assessment`/trazas/VF opacos.

## 1. Hallazgo objetivo

PR #106 cerró la procedencia de C0 `Assessment + Trace` hacia Scenario Analytics, pero `complete_o4_o2_o3_orchestration(...)` seguía siendo una función pública capaz de aceptar `AuthorizedScenarioAnalytics` construidos manualmente con `tuple[Any, ...]`, `Any` y trace references libres.

La suite `test_vertical_mvp_scenario_e2e_conformance.py` todavía utilizaba exactamente ese bypass y lo presentaba como E2E. Por tanto, la frontera provenance-safe existía, pero no gobernaba el camino E2E real.

## 2. Distinción de fronteras

### 2.1 Stage 2 interno

La mecánica cerrada de Stage 2 conserva un transporte interno `AuthorizedScenarioAnalytics` para probar:
- correspondencia exacta 1:1 con escenarios O2 VALID;
- orden determinista O2;
- estados O3 explícitos;
- ausencia de reejecución O4/O2;
- preservación de limitaciones y datos analíticos.

Ese transporte **no constituye prueba de procedencia** por sí mismo.

### 2.2 Finalización externa

La frontera externa autorizada recibe material verificable por escenario:
- `scenario_id` O2 real;
- `PurchaseOperation` explícito del escenario hijo;
- `AssessmentTraceBinding` ya producido;
- `ViabilityResult` tipado;
- estado O3 explícito;
- limitaciones/failure reason explícitos cuando proceda.

La frontera construye internamente el transporte Stage 2 mediante el bridge provenance-safe de PR #106 y solo después delega a O3.

## 3. ProvenancedScenarioAnalyticsInput

Se introduce un contenedor inmutable de solicitud:

`ProvenancedScenarioAnalyticsInput`

Campos:
- `scenario_id: str`
- `purchase: PurchaseOperation`
- `assessment_bindings: tuple[AssessmentTraceBinding, ...]`
- `viability_result: ViabilityResult`
- `status: ScenarioEvaluationStatus`
- `limitations: tuple[str, ...]`
- `failure_reason: str | None`

El objeto no es una autorización. Toda autoridad procede de las validaciones ejecutadas al completar.

## 4. Nueva finalización pública

`complete_provenanced_o4_o2_o3_orchestration(...)`:
1. congela preparation e inputs;
2. para cada input llama exclusivamente a `build_authorized_scenario_analytics_from_provenanced_assessments(...)`;
3. esa frontera verifica escenario hijo, compra, regla, Trace, input fingerprint, assessment fingerprint, trace_id y `ViabilityResult`;
4. únicamente después delega los transportes resultantes al Stage 2 interno;
5. O3 mantiene su función de representación y no reejecuta reglas ni VF.

## 5. Cuarentena del Stage 2 previo

`complete_o4_o2_o3_orchestration(...)` deja de ser API pública.

La implementación pasa a helper interno `_complete_o4_o2_o3_orchestration(...)` y se elimina de `__all__`.

`AuthorizedScenarioAnalytics` se conserva físicamente como transporte interno porque permite probar la mecánica de Stage 2 sin confundir esas pruebas con conformance E2E.

## 6. E2E obligatorio

Toda prueba o integración que afirme conformance E2E de escenarios debe usar la frontera provenance-safe.

Los tests estrictamente unitarios de la mecánica Stage 2 pueden usar el helper interno y transportes sintéticos, identificándolos como internos.

## 7. Fail-closed

Antes de O3 debe rechazarse:
- escenario desconocido, duplicado o no VALID;
- input faltante/sobrante respecto de escenarios VALID;
- bindings vacíos o rule_id duplicados;
- compra de otra decisión/escenario;
- Trace de otro contexto/version/snapshot/input;
- Trace legacy sin `assessment_fingerprint`;
- Assessment manipulado;
- `trace_id` no reproducible;
- regla no catalogada;
- `ViabilityResult` de otro escenario/contexto/version/snapshot.

Un fallo de procedencia es error técnico y no se traduce a FALSE, NOT_VIABLE, rechazo o decisión.

## 8. Estados y autoridad

- estado VF no deriva estado O3;
- `NOT_EVALUABLE` permanece distinto de FALSE;
- `FAILED` sigue siendo fallo técnico;
- la agregación Vertical sigue obedeciendo al execution boundary cerrado;
- no aparece score, ranking, recomendación, selección, aprobación, rechazo ni decisión empresarial.

## 9. Inmutabilidad

Preparation, compras hijo, bindings, Assessments, Traces y ViabilityResult se copian antes de su uso. La finalización pública no muta entradas.

## 10. Fuera de alcance

- materializar automáticamente `ScenarioVersion.changes` en PurchaseOperation;
- modificar O4/O2/O3/VF;
- cambiar semántica de reglas, CRC/O1 o Scenario Coordination;
- retirar el transporte interno usado por tests unitarios;
- UI/HTML, SQL o persistencia;
- inventar relación entre C0 Assessment y FrontierAssessment.

## 11. Criterios de aceptación

1. la finalización pública solo recibe material provenance-safe;
2. no acepta `AuthorizedScenarioAnalytics` opaco como argumento público;
3. el Stage 2 previo queda interno y fuera de `__all__`;
4. un binding válido + VF tipado completan O3;
5. múltiples escenarios conservan orden O2 determinista;
6. missing/extra/duplicate falla antes de O3;
7. Trace manipulado/legacy/contexto ajeno falla antes de O3;
8. VF ajeno falla antes de O3;
9. `NOT_EVALUABLE` y `FAILED` conservan semántica;
10. el E2E Scenario→Vertical→Presentation usa la nueva frontera;
11. tests unitarios internos pueden seguir cubriendo Stage 2 con transporte sintético;
12. inputs permanecen inmutables;
13. no aparece autoridad decisional.

## 12. Auditoría 1

**Hallazgo:** intentar convertir `AuthorizedScenarioAnalytics` en un supuesto token seguro sería una falsa garantía: cualquier caller Python podría construirlo. La seguridad contractual debe residir en una función que reciba material verificable y ejecute las validaciones de procedencia, no en el nombre del objeto transportado.

**Depuración:** se mantiene el modelo como transporte interno; se privatiza la finalización Stage 2 y se introduce una finalización pública que reconstruye ese transporte exclusivamente a partir de bindings+Trace y VF tipado.

**DICTAMEN AUDITORÍA 1:** SUPERADA — APTO PARA IMPLEMENTACIÓN.

## 13. Auditoría 2

Se ha auditado el diff completo frente a `main @ 5e5243d4e5245991c5e6db515aaff14e3840a059`:

- 7 archivos modificados/añadidos en el primer cierre de alcance;
- 0 commits por detrás del baseline;
- la producción se limita a la frontera de orquestación Stage 2 y al facade provenance-safe de Rules;
- no se modifica lógica de O4, O2, O3 ni Viability Frontier;
- no se modifica ninguna regla empresarial, C0 core, CRC, O1, Scenario Coordination ni presentación;
- `AuthorizedScenarioAnalytics` queda identificado expresamente como transporte interno, no como prueba de procedencia;
- `_complete_o4_o2_o3_orchestration` queda fuera de `__all__`;
- la API pública nueva exige `ProvenancedScenarioAnalyticsInput` y reconstruye cada transporte mediante validación C0+Trace y VF tipada;
- el E2E principal de escenarios ya no fabrica Assessment/VF/trazas opacos;
- los tests de mecánica Stage 2 se identifican y consumen como internos;
- los nuevos tests cubren rechazo de transporte opaco, Trace manipulado, cobertura missing/extra/duplicate y visibilidad pública;
- no aparece score, ranking, recomendación, selección, aprobación, rechazo ni autoridad decisional.

**DICTAMEN AUDITORÍA 2:** SUPERADA — SIN BLOQUEADORES DE DISEÑO. Cierre técnico condicionado a CI completa y reconciliación post-merge.
