# EIOS — Vertical MVP Negotiation Ladder Context Integrity Contract v0.1

**Estado:** CERRADO PARA MATERIALIZACIÓN  
**Baseline:** `main @ 105b983b75f436b6ade710e2c209685a25471d05`  
**Ámbito:** composición de `NegotiationLadderResult` preproducido dentro de `run_mvp_execution`.

## 1. Propósito

Cerrar el hueco por el que una ejecución Vertical podía incorporar una Negotiation Ladder perteneciente a otra decisión, otro escenario o —cuando NI también se incorpora— a otro resultado de Negotiation Intelligence.

La validación es exclusivamente de identidad/procedencia. No modifica estructura, secuencia ni contenido negociador.

## 2. Autoridad existente

Este contrato deriva exclusivamente de autoridades ya cerradas:

- `Negotiation_Ladder_Implementation_Contract.md`: `LadderContextReferences` conserva `negotiation_result_id` y `decision_id` como referencias upstream obligatorias, `scenario_id` como referencia opcional y no incorpora `decision_version`.
- `Negotiation_Intelligence_Implementation_Contract.md`: `negotiation_result_id` identifica el artefacto NI.
- `E2E_Execution_Boundary_Implementation_Contract.md`: una ejecución Vertical debe rechazar identidad inconsistente.
- `DecisionContext`: autoridad física para `decision_id` y `scenario_id` de la ejecución.

## 3. Regla cerrada

Sea `refs = negotiation_ladder_result.context_references`:

1. `refs.decision_id` debe coincidir exactamente con `context.decision_id`.
2. Si `refs.scenario_id` está presente, debe coincidir exactamente con `context.scenario_id`.
3. Si `negotiation_intelligence_result` también se incorpora en la misma llamada a `run_mvp_execution`, entonces:

```text
refs.negotiation_result_id == negotiation_intelligence_result.negotiation_result_id
```

4. Si NI no forma parte de esa ejecución, la composición Vertical no inventa ni recupera un resultado NI externo para validar `negotiation_result_id`; la referencia Ladder se preserva sin reinterpretación.

Cualquier incompatibilidad verificable produce `ValueError` antes de `execute_plan`.

## 4. Límites

La validación:

- no recalcula NI ni Ladder;
- no modifica steps, transitions, routes ni posiciones;
- no determina contenido negociador ni estrategia;
- no crea ni modifica límites;
- no convierte `scenario_id` opcional en obligatorio;
- no exige NI cuando Ladder se ejecuta de forma aislada;
- no introduce `decision_version`;
- no infiere igualdad desde `source_references` o `source_content_reference`;
- no aprueba, recomienda, decide ni ejecuta negociación real.

## 5. Orden fail-closed

La integridad Ladder se valida durante la construcción del catálogo de ejecución, antes del snapshot/invocador de Ladder y antes de `execute_plan`. Si existe incompatibilidad, ninguna capacidad llega a ejecutarse.

Cuando NI está presente, su propia integridad contextual se valida primero; después se valida la vinculación Ladder ↔ NI.

## 6. Auditoría 1

Hallazgo confirmado: `run_mvp_execution` snapshoteaba/adaptaba Ladder sin comprobar `LadderContextReferences` contra `DecisionContext` ni, cuando ambas capacidades estaban presentes, contra el `negotiation_result_id` NI suministrado.

La corrección materializa referencias upstream ya declaradas; no amplía la autoridad Ladder.

## 7. Depuración

Se descartan endurecimientos no autorizados:

- `decision_id`: obligatorio y siempre comparable.
- `scenario_id`: solo comparable cuando Ladder lo proporciona.
- `negotiation_result_id`: comparable solo contra el NI que realmente forma parte de la misma composición.
- ausencia de NI: no es por sí misma un error Ladder.
- campos estructurales/source references: no se reinterpretan como identidad contextual.

## 8. Criterios de aceptación

1. Ladder con decisión/escenario coincidentes se integra sin regresión.
2. Ladder con `scenario_id=None` sigue siendo válida.
3. `decision_id` distinto se rechaza.
4. `scenario_id` presente y distinto se rechaza.
5. Ladder + NI con `negotiation_result_id` coincidente se integran.
6. Ladder + NI con `negotiation_result_id` distinto se rechazan antes de ejecutar.
7. Ladder aislada no requiere materializar un objeto NI solo para validar la referencia.
8. Si hay varias incompatibilidades, el error identifica todos los campos verificables discrepantes.
9. Los objetos de entrada permanecen inmutados.
10. No se añade autoridad decisional o estratégica.

## 9. Materialización prevista

```text
eios/core/mvp_execution.py
tests/test_mvp_ladder_context_integrity.py
```

## 10. Método

**DISEÑAR → AUDITAR → DEPURAR → AUDITAR 2 → CERRAR → MATERIALIZAR → CI**
