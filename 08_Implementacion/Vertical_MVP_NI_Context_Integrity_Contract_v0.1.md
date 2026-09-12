# EIOS — Vertical MVP Negotiation Intelligence Context Integrity Contract v0.1

**Estado:** CERRADO PARA MATERIALIZACIÓN  
**Baseline:** `main @ 2b1446e7dc41cc61d527bf75486ea576181e58d4`  
**Ámbito:** composición de resultados `NegotiationIntelligenceResult` preproducidos dentro de `run_mvp_execution`.

## 1. Propósito

Cerrar el hueco por el que una ejecución Vertical podía incorporar un resultado NI perteneciente a otro contexto decisional sin modificar la autoridad, el contenido ni la epistemología de Negotiation Intelligence.

## 2. Autoridad existente

Este contrato deriva exclusivamente de autoridades ya cerradas:

- `Negotiation_Intelligence_Implementation_Contract.md`: el resultado NI debe estar vinculado al contexto decisional correspondiente y reutilizar las identidades autorizadas existentes; `Scenario_ID`, `Rules_Version`, `Parameters_Version` y `Data_Snapshot_ID` se conservan cuando aplican.
- `E2E_Execution_Boundary_Implementation_Contract.md`: la ejecución recibe un contexto canónico y rechaza identidad inconsistente.
- `DecisionContext`: autoridad física para `decision_id`, `scenario_id`, `rules_version`, `parameters_version` y `data_snapshot_id`.

No se crea identidad NI nueva ni se modifica ninguna autoridad upstream.

## 3. Regla cerrada

Sea `refs = negotiation_intelligence_result.context_references`:

1. `refs.decision_id` es obligatorio en NI y debe coincidir exactamente con `context.decision_id`.
2. Para cada referencia opcional siguiente, si el valor NI está presente, debe coincidir exactamente con el valor canónico de `DecisionContext`:
   - `scenario_id`
   - `rules_version`
   - `parameters_version`
   - `data_snapshot_id`
3. La ausencia (`None`) de una referencia opcional no constituye por sí misma una inconsistencia, porque el contrato NI declara esas identidades «cuando aplique» y el modelo físico las hace opcionales.

Cualquier desigualdad aplicable produce `ValueError` antes de iniciar `execute_plan`.

## 4. Exclusiones y límites

La validación:

- no recalcula NI;
- no interpreta ni modifica contenido negociador;
- no valida la calidad de evidencia ni las afirmaciones epistemológicas;
- no convierte referencias opcionales en obligatorias;
- no compara `viability_reference` ni `decision_twin_reference` contra `DecisionContext`, porque éste no transporta campos canónicos equivalentes;
- no introduce `decision_version`, explícitamente excluido del contrato NI;
- no valida Negotiation Ladder en esta unidad;
- no aprueba, decide, ejecuta ni activa Strategy.

## 5. Orden fail-closed

La integridad contextual se comprueba durante la construcción del catálogo de ejecución, antes de crear el snapshot/invocador de NI y antes de `execute_plan`. Si falla, ninguna capacidad del plan llega a ejecutarse.

## 6. Auditoría 1

Hallazgo confirmado: `run_mvp_execution` snapshoteaba y adaptaba `NegotiationIntelligenceResult` sin comprobar `context_references` contra el `DecisionContext` actual. Por tanto, podía componer un resultado NI de otra decisión o de referencias de escenario/versiones/snapshot incompatibles.

La corrección materializa una obligación ya declarada; no amplía el contrato NI.

## 7. Depuración

Se elimina cualquier endurecimiento no autorizado:

- `decision_id`: siempre comparable y obligatorio.
- referencias opcionales: comparables únicamente cuando NI las proporciona.
- referencias sin homólogo en `DecisionContext`: fuera de esta validación.
- Negotiation Ladder: unidad posterior e independiente.

## 8. Criterios de aceptación

1. NI con todas las referencias contextuales presentes y coincidentes se integra sin regresión.
2. NI con solo `decision_id` y referencias opcionales ausentes se integra válidamente.
3. `decision_id` distinto se rechaza.
4. Cada referencia opcional presente y distinta se rechaza individualmente.
5. Si existen varias incompatibilidades, el error identifica todos los campos discrepantes.
6. La inconsistencia se rechaza antes de ejecutar cualquier capacidad.
7. Resultado NI y contexto permanecen inmutados.
8. No se introduce `decision_version` ni autoridad decisional nueva.

## 9. Materialización prevista

```text
eios/core/mvp_execution.py
tests/test_mvp_ni_context_integrity.py
```

## 10. Método

**DISEÑAR → AUDITAR → DEPURAR → AUDITAR 2 → CERRAR → MATERIALIZAR → CI**
