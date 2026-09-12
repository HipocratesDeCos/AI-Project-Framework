# EIOS — Vertical MVP Scenario E2E Conformance Contract v0.1

**Estado:** CERRADO PARA VERIFICACIÓN  
**Baseline:** `main @ c6636a92fb5fa2cffb3661008d2a9fdbb8e8249e`  
**Ámbito:** conformidad extremo a extremo del hilo de escenarios autorizado, desde O4→O2→O3 hasta application boundary y view-model, sin HTML.

## 1. Propósito

Demostrar mediante pruebas ejecutables que las unidades cerradas del hilo de escenarios componen una cadena coherente sin pérdida de identidad, trazabilidad, estados ni frontera de autoridad.

Esta unidad no introduce funcionalidad productiva nueva.

## 2. Cadena bajo verificación

1. `prepare_o4_o2_o3_orchestration`;
2. producción externa explícita de `AuthorizedScenarioAnalytics` para los `scenario_id` O2 VALID reales;
3. `complete_o4_o2_o3_orchestration`;
4. `run_vertical_mvp_from_orchestration`;
5. `present_vertical_mvp_result`;
6. `build_vertical_mvp_view_model`.

## 3. Procedencia e identidad

La prueba E2E debe demostrar que se conservan desde `DecisionContext` hasta el view-model:

- `decision_id`;
- `rules_version`;
- `parameters_version`;
- `data_snapshot_id`.

Los `scenario_id` materializados por O2 son la única identidad autorizada para vincular los paquetes analíticos y deben llegar sin sustitución al soporte/presentación final.

## 4. Condición analítica

La verificación mantiene la invariante cerrada de PR #99:

- O3 solo recibe Assessment ya producido/autorizado;
- O3 solo recibe Viability Frontier ya producido/autorizado;
- no se fabrican artefactos ausentes;
- no se deriva `NOT_EVALUABLE` o `FAILED` para suplir análisis faltante.

## 5. Estados y agregación

La conformidad debe demostrar continuidad semántica para:

- `COMPLETED`;
- `NOT_EVALUABLE` local;
- `FAILED` técnico.

La continuidad de estado no exige igualdad literal entre el estado de una capacidad y el estado agregado del límite Vertical. Se preserva la autoridad cerrada de `ExecutionOutcome`:

- una evaluación/registro `NOT_EVALUABLE` permanece `NOT_EVALUABLE` en O3, O2 Support y `SCENARIO_COORDINATION`;
- como `ExecutionOutcome` síncrono no admite `NOT_EVALUABLE` como terminal, una capacidad `NOT_EVALUABLE` produce `BoundaryStatus.PARTIALLY_COMPLETED` en el agregado Vertical;
- esa agregación no convierte el resultado local en `FALSE`, no viable, rechazo ni decisión;
- `FAILED` técnico sí produce `BoundaryStatus.FAILED` conforme al límite cerrado.

Las limitaciones/unresolved y `failure_reason` correspondientes deben conservarse hasta presentación.

## 6. Trazabilidad y contenido

Los datos de Assessment, Viability Frontier y `trace_references` deben sobrevivir sin reinterpretación a través de:

O3 → O2 Support → `SCENARIO_COORDINATION` → Vertical MVP → application boundary → view-model.

## 7. Determinismo

Con las mismas entradas:

- O4 genera la misma secuencia;
- O2 produce los mismos `scenario_id`/fingerprints conforme a su contrato;
- el soporte O2 conserva orden determinista;
- la representación final conserva el mismo orden de escenarios.

La prueba puede repetir la cadena completa para demostrar igualdad semántica de la salida de presentación.

## 8. Frontera de autoridad

En ningún punto de la salida E2E pueden aparecer campos o conclusiones de:

- `score`;
- `ranking`;
- `recommendation`;
- `approval`;
- `rejection`;
- `best_scenario`;
- `selected_scenario`;
- decisión del CEO.

La comparación O2 sigue siendo descriptiva y no decisional.

## 9. Reglas y otros motores

La fachada de escenarios se mantiene deliberadamente estrecha:

- `rules_available=False` en el view-model;
- no se ejecutan Rules/CRC;
- no se ejecutan QTG, PRICE, TCO, C0, Decision Twin, Negotiation Intelligence ni Negotiation Ladder.

`SCENARIO_COORDINATION` debe ser la única capacidad Vertical producida por esta fachada.

## 10. Inmutabilidad

La prueba debe demostrar que las entradas canónicas no cambian después de atravesar la cadena completa.

La mutación de payload/view-model final tampoco puede retropropagarse a la salida Vertical ni a la orquestación fuente.

## 11. Frontera visual

Esta conformidad termina en `build_vertical_mvp_view_model`.

Queda explícitamente fuera de alcance:

- modificar `index.html`;
- cablear HTML a ejecución real;
- reabrir U1.1.

## 12. Criterios de aceptación

La suite E2E debe cubrir, como mínimo:

1. ruta COMPLETED completa hasta view-model;
2. preservación de decisión/versiones/snapshot;
3. preservación de `scenario_id`, Assessment, Viability y trazas;
4. varios escenarios con orden determinista;
5. `NOT_EVALUABLE` íntegro en registro y `SCENARIO_COORDINATION`, con agregado Vertical `PARTIALLY_COMPLETED` y unresolved preservados;
6. `FAILED` técnico íntegro hasta view-model;
7. `rules_available=False` y `scenario_support_available=True`;
8. única capacidad `SCENARIO_COORDINATION`;
9. ausencia de autoridad decisional;
10. inmutabilidad y salida desacoplada;
11. repetibilidad determinista de la cadena.

**DICTAMEN DE DEPURACIÓN:** APTO. Se distingue explícitamente estado local de capacidad/escenario y estado agregado del límite Vertical, sin modificar ninguna semántica productiva cerrada.
