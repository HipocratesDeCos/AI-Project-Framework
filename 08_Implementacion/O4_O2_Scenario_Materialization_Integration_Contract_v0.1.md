# EIOS — O4 → O2 Scenario Materialization Integration Contract v0.1

**Estado:** CERRADO PARA IMPLEMENTACIÓN
**Baseline:** `main @ 06dbb9f3f28b19d3848af3a06510e8d7f5123049`
**Ámbito:** materialización estructural de candidatos O4 mediante la autoridad de identidad/versionado O2.

## 1. Propósito

Conectar la generación controlada O4 con el Scenario Engine O2 sin modificar ninguno de ambos componentes y sin ejecutar O3.

O4 conserva la autoridad exclusiva sobre generación finita y determinista de candidatos. O2 conserva la autoridad exclusiva sobre identidad, fingerprint, canonicalización, versionado y estado estructural de `ScenarioVersion`.

## 2. Entrada autorizada

La integración recibe exclusivamente:

- un `GenerationResult` ya producido por O4;
- el `DecisionContext` canónico asociado.

La integración no ejecuta `generate_scenarios` y no deriva variables, reglas, parámetros, Assessments ni resultados de Viability Frontier.

## 3. Salida

La integración devuelve un `O4O2MaterializationResult` inmutable con:

- copia profunda del `GenerationResult` original;
- cero o más `ScenarioVersion` creados mediante `create_scenario` de O2.

El `GenerationResult` se conserva completo para mantener literalmente la representación O4 de `status`, `policy_version`, `reason`, `parent_scenario_id`, `depth` y cambios candidatos. La representación interna de los `ScenarioVersion` materializados pertenece a O2 y puede aplicar su canonicalización contractual.

## 4. Política de materialización

### 4.1 `GENERATED`

Cada `CandidateScenario` se materializa llamando exclusivamente a:

`create_scenario(context, changes=candidate.changes, parent_scenario_id=candidate.parent_scenario_id, validate=True)`

No se fabrica ni modifica ningún `scenario_id`, fingerprint, versión, snapshot o representación canónica fuera de O2.

La integración no exige igualdad estructural entre `candidate.changes` y `ScenarioVersion.changes`, porque la canonicalización materializada es responsabilidad cerrada de O2. La fuente O4 original permanece disponible en `generation`.

### 4.2 Estados O4 no generativos

`EMPTY`, `BLOCKED`, `NOT_EVALUABLE` y `FAILED` producen un resultado de integración con `scenarios=()` y conservan literalmente el `GenerationResult` original.

No se convierten en fallos O2, escenarios sintéticos ni estados empresariales.

## 5. Candidato base sin cambios

O4 puede emitir un candidato de cero variables con `changes=()`.

Ese candidato se entrega sin alteración a `create_scenario`. Como O2 define un escenario sin cambios como `DRAFT`, la integración debe conservar el `DRAFT` resultante.

Queda prohibido forzarlo a `VALID`, añadir cambios ficticios o declararlo listo para O3.

## 6. Preparación para O3

La salida puede contener escenarios `VALID` y/o `DRAFT` según las reglas cerradas de O2.

La integración:

- no invoca `evaluate_scenario`;
- no marca escenarios como `EVALUATED`;
- no filtra silenciosamente escenarios para O3;
- no fabrica Assessments, Viability Frontier, limitaciones o trazas analíticas.

Cualquier ejecución coordinada O4 → O2 → O3 que produzca evaluación requerirá resultados analíticos autorizados y un alcance posterior específico.

## 7. Determinismo e identidad

- El orden de escenarios materializados conserva el orden determinista de candidatos O4.
- Para la misma entrada O4 y el mismo `DecisionContext`, O2 debe producir los mismos `scenario_id` y fingerprints.
- La identidad, canonicalización y versiones proceden exclusivamente del `DecisionContext` y de `create_scenario`.
- La integración no introduce identidad paralela.

## 8. Inmutabilidad

La integración no muta:

- `GenerationResult`;
- `CandidateScenario`;
- `AuthorizedScenarioChange`;
- `DecisionContext`.

La salida conserva una copia profunda del resultado O4 para aislar estructuras mutables anidadas.

## 9. Fronteras de autoridad

Quedan prohibidos:

- ranking, score, selección o recomendación;
- optimización o poda adicional;
- interpretación económica de cambios;
- ejecución de reglas o Viability Frontier;
- negociación;
- decisión, aprobación o rechazo empresarial;
- persistencia, SQL o API;
- modificación de O2, O3 u O4.

## 10. Criterios de aceptación

Las pruebas deben demostrar al menos:

1. `GENERATED` con cambios produce `ScenarioVersion VALID`;
2. identidad, fingerprint y canonicalización dependen exclusivamente de O2 y son deterministas;
3. `parent_scenario_id` se conserva y la fuente O4 original permanece íntegra;
4. múltiples candidatos conservan orden y unicidad determinista;
5. cero variables produce escenario `DRAFT`, nunca `VALID` sintético;
6. `EMPTY`, `BLOCKED`, `NOT_EVALUABLE` y `FAILED` no crean escenarios;
7. contexto y versiones se conservan;
8. entradas no se mutan;
9. estructuras mutables anidadas quedan aisladas mediante copia profunda;
10. no aparecen campos o comportamientos de ranking, selección, recomendación o decisión;
11. O2, O3 y O4 permanecen físicamente sin modificaciones.

## 11. Auditoría previa

**DICTAMEN: APTO PARA IMPLEMENTACIÓN TRAS DEPURACIÓN.**

Audit 1 detectó y corrigió una formulación incorrecta que exigía preservación literal de los cambios dentro de `ScenarioVersion`. El contrato depurado reconoce que O2 posee la autoridad de canonicalización y conserva separadamente la fuente O4 original. La integración llena una brecha expresamente diferida por O4 sin ampliar O3 ni transformar estados técnicos en conclusiones empresariales.
