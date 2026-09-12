# EIOS — Vertical MVP Scenario Support Presentation Contract v0.1

**Estado:** CERRADO PARA IMPLEMENTACIÓN  
**Baseline:** `main @ 56b921d77a20d44b197b9210380fda82c38ca152`  
**Ámbito:** exposición estrictamente presentacional de `VerticalMVPSupportResult.scenario_support` a través del application boundary y del view-model Vertical MVP.

## 1. Propósito

Cerrar el hueco entre el `scenario_support` ya preservado por el Vertical MVP y su capa pública de presentación, sin ejecutar lógica analítica ni crear autoridad decisional.

## 2. Autoridad

- `O2SupportPackage` conserva toda la autoridad sobre estructura, estados, comparación y trazabilidad de soporte de escenarios.
- `present_vertical_mvp_result` solo serializa una copia del soporte ya existente.
- `build_vertical_mvp_view_model` solo valida y copia el payload contractual recibido.
- Esta unidad no ejecuta O4, O2, O3, Assessment, Viability Frontier, reglas, CRC ni capacidades MVP.

## 3. Contrato público

`present_vertical_mvp_result` debe incluir siempre la clave de nivel superior `scenario_support`.

- Si `VerticalMVPSupportResult.scenario_support is None`, el valor público será exactamente `None`.
- Si existe soporte, el valor será un payload JSON-compatible con tres secciones exactas procedentes del `O2SupportPackage`:
  - `execution_context`;
  - `scenarios`;
  - `comparison`.

No existe ausencia implícita: omitir la clave `scenario_support` es payload mal formado.

## 4. Execution context

Se exponen literalmente:

- `execution_id`;
- `decision_id`;
- `rules_version`;
- `parameters_version`;
- `data_snapshot_id`.

No se admite contexto alternativo ni override.

## 5. Escenarios

Cada escenario expone únicamente campos ya contenidos en `O2ScenarioResult`:

- `scenario_id`;
- `status`;
- `values`;
- `trace_references`;
- `unresolved_items`;
- `failure_reason`.

El orden recibido desde O2 se conserva. No se calcula score, prioridad ni preferencia.

## 6. Comparación

Si O2 no generó comparación, `comparison` será `None`.

Si existe, se copian literalmente los campos cerrados de `O2Comparison`:

- `scenario_ids`;
- `observations`;
- `differences`;
- `missing`;
- `statuses`;
- `unresolved_items`;
- `traceability`.

La presentación no interpreta diferencias ni selecciona un escenario.

## 7. View-model

`build_vertical_mvp_view_model` exige las tres claves superiores contractuales:

- `execution`;
- `rules`;
- `scenario_support`.

Para `scenario_support=None` debe producir:

- `scenario_support_available=False`;
- `scenario_execution_context=None`;
- `scenario_records=None`;
- `scenario_comparison=None`.

Para soporte presente debe validar fail-closed la forma mínima de `execution_context`, `scenarios` y `comparison`, y producir copias profundas de esos datos sin reinterpretarlos.

## 8. Fail-closed

El view-model debe rechazar:

- ausencia de la clave `scenario_support`;
- `scenario_support` distinto de `None` o Mapping;
- ausencia de claves contractuales de soporte;
- `execution_context` no Mapping o incompleto;
- `scenarios` no secuencia de registros Mapping;
- registro de escenario incompleto;
- `comparison` no `None`/Mapping o incompleta.

No se permiten defaults silenciosos para datos ausentes.

## 9. Inmutabilidad

Application boundary y view-model operan sobre serializaciones/copias. Mutar la salida no puede modificar `VerticalMVPSupportResult`, `O2SupportPackage` ni el payload de entrada.

## 10. Autoridad decisional prohibida

Esta integración no puede introducir ni derivar:

- `score`;
- `ranking`;
- `recommendation`;
- `approval`;
- `rejection`;
- `best_scenario`;
- `selected_scenario`;
- decisión empresarial.

`NOT_EVALUABLE` se conserva como estado y `FAILED` permanece técnico.

## 11. Fuera de alcance

- modificación de HTML/CSS/JS;
- reapertura de U1.1;
- ejecución del pipeline de escenarios;
- cambio de modelos O2;
- modificación de `SCENARIO_COORDINATION`;
- cálculo de comparación distinto del ya producido por O2.

## 12. Criterios de aceptación

Las pruebas deben demostrar:

1. `scenario_support=None` se expone explícitamente;
2. soporte presente conserva contexto, escenarios y comparación;
3. estados, values, trazas, unresolved y failure reason se conservan;
4. el view-model expone soporte sin cálculo adicional;
5. payload sin `scenario_support` falla cerrado;
6. payload de soporte mal formado falla cerrado;
7. `NOT_EVALUABLE` no se transforma en falso/no viable;
8. `FAILED` no se transforma en rechazo;
9. entradas no se mutan;
10. no aparecen campos de ranking/recomendación/decisión.

**DICTAMEN DE DISEÑO:** APTO PARA IMPLEMENTACIÓN. Extensión presentacional explícita, fail-closed y sin nueva semántica decisional.