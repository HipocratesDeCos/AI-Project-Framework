# EIOS — Viability Frontier → Scenario Analytics Integration Contract v0.1

**Estado:** DISEÑO PARA AUDITORÍA  
**Baseline:** `main @ 592144e96014cff2137667d1648a9601c00b768c`  
**Ámbito:** vinculación tipada y fail-closed de un `ViabilityResult` ya producido con un `ScenarioVersion VALID` materializado en `O4O2O3Preparation`, antes de construir `AuthorizedScenarioAnalytics`.

## 1. Propósito

Cerrar una brecha de procedencia existente entre Viability Frontier y la orquestación O4→O2→O3 sin ejecutar lógica analítica nueva.

`AuthorizedScenarioAnalytics` conserva deliberadamente `viability_result: Any`; por ello, la orquestación cerrada puede comprobar la identidad del paquete analítico, pero no puede demostrar que un objeto real de Viability Frontier contenido en ese paquete pertenezca a la misma decisión, escenario, versiones y snapshot.

Esta integración añade una frontera opcional y tipada para construir el paquete a partir de un `ViabilityResult` real cuya procedencia haya sido validada.

## 2. Entradas

La operación recibe exclusivamente:

- `O4O2O3Preparation` ya materializada;
- `scenario_id` de un escenario O2 `VALID` de esa preparación;
- `assessments` ya producidos/autorizados y no vacíos;
- un `ViabilityResult` ya producido por Viability Frontier;
- estado técnico O3 explícito o `COMPLETED` por defecto;
- limitaciones, trazas y causa de fallo cuando correspondan.

No recibe un `DecisionContext` separado.

## 3. Vinculación obligatoria

Antes de crear `AuthorizedScenarioAnalytics`, el `ViabilityResult` debe coincidir exactamente con la preparación en:

- `decision_id`;
- `scenario_id`;
- `rules_version`;
- `parameters_version`;
- `data_snapshot_id`.

El `scenario_id` solicitado debe corresponder exactamente a un `ScenarioVersion` con estado `VALID` dentro de la preparación.

Para esta frontera tipada, `rules_version`, `parameters_version` y `data_snapshot_id` del `ViabilityResult` son obligatorios. Un resultado VF legado o incompleto con cualquiera de esos campos en `None` no aporta evidencia suficiente de procedencia para esta integración y se rechaza fail-closed.

## 4. Autoridades preservadas

- Viability Frontier conserva toda autoridad sobre `ViabilityStatus` y su cálculo.
- O2 conserva identidad, estado estructural, canonicalización y versionado del escenario.
- O3 conserva el estado técnico de evaluación y sus invariantes.
- `AuthorizedScenarioAnalytics` conserva la forma cerrada del paquete analítico.
- esta integración no ejecuta VF ni O3.

## 5. Semántica de estados

No se introduce mapping entre `ViabilityStatus` y `ScenarioEvaluationStatus`.

En particular:

- `ViabilityStatus.VIABLE` no fuerza `COMPLETED`;
- `VIABLE_CON_CONDICIONES` no fuerza estado parcial;
- `NOT_VIABLE` no equivale a fallo técnico ni rechazo empresarial;
- `NOT_EVALUABLE` de VF no se transforma automáticamente en `ScenarioEvaluationStatus.NOT_EVALUABLE`.

El estado técnico O3 continúa siendo una entrada explícita y es validado posteriormente por los contratos cerrados existentes.

## 6. Assessment

Esta unidad no intenta reinterpretar ni volver a calcular Assessment.

Solo exige que `assessments` sea explícito y no vacío, igual que el contrato cerrado de `AuthorizedScenarioAnalytics`. La procedencia interna de cada tipo de Assessment sigue perteneciendo a su autoridad productora y queda fuera de esta integración específica VF→Scenario Analytics.

## 7. Trazabilidad

El `ViabilityResult` se conserva íntegro y sin reinterpretación dentro del paquete analítico.

Las `trace_references` del paquete siguen siendo una entrada explícita. Esta integración no fusiona, inventa ni deduplica trazas de VF con trazas O3, porque hacerlo introduciría una política adicional no autorizada.

## 8. Inmutabilidad

Preparación, Assessment, ViabilityResult, limitaciones y trazas se copian antes de construir la salida.

La operación no modifica ninguna entrada.

## 9. Fail-closed

Se rechaza explícitamente:

- `scenario_id` inexistente;
- escenario presente pero no `VALID`;
- `ViabilityResult` de otra decisión;
- `ViabilityResult` de otro escenario;
- `rules_version` distinta o ausente;
- `parameters_version` distinta o ausente;
- `data_snapshot_id` distinto o ausente;
- Assessment vacío;
- cualquier estado/campo que `AuthorizedScenarioAnalytics` rechace por su contrato cerrado.

Ningún error se convierte en `NOT_VIABLE`, `NOT_EVALUABLE`, recomendación o decisión.

## 10. Salida

Salida exacta: `AuthorizedScenarioAnalytics`.

La salida conserva:

- `scenario_id` validado;
- Assessment suministrados;
- el objeto `ViabilityResult` tipado y validado;
- estado técnico, limitaciones, trazas y causa de fallo suministrados.

## 11. Fuera de alcance

- ejecutar `evaluate_viability`;
- derivar consecuencias H/K/U/S;
- ejecutar reglas o CRC;
- ejecutar O3;
- modificar O4, O2, O3, VF o la orquestación existente;
- mapear estados VF↔O3;
- score, ranking, optimización, selección, recomendación, aprobación o rechazo empresarial;
- persistencia, SQL, API o UI.

## 12. Criterios de aceptación

Las pruebas deben demostrar:

1. VF del contexto exacto produce `AuthorizedScenarioAnalytics` válido;
2. objeto VF se conserva semánticamente íntegro;
3. rechazo de decisión ajena;
4. rechazo de escenario ajeno;
5. rechazo de `rules_version` ajena o ausente;
6. rechazo de `parameters_version` ajena o ausente;
7. rechazo de `data_snapshot_id` ajeno o ausente;
8. rechazo de escenario DRAFT/no VALID;
9. rechazo de Assessment vacío;
10. no mapping automático entre `ViabilityStatus` y estado O3;
11. inmutabilidad;
12. integración posterior mediante `complete_o4_o2_o3_orchestration` sin reejecutar VF;
13. ausencia de autoridad decisional.

**DICTAMEN DE DISEÑO:** pendiente de Auditoría 1.
