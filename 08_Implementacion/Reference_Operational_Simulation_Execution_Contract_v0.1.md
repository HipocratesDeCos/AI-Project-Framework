# EIOS — Reference Operational Simulation Execution Contract v0.1

**Baseline:** `main @ bf6cf496c3f57a3b462946cd63d3eb84be363990`  
**Fecha:** 23/09/2026  
**Estado:** DISEÑADO → AUDITADO → MATERIALIZADO EN RAMA / CI PENDIENTE

## 1. Propósito

Crear una fachada causal para ejecutar un caso
`REFERENCE_OPERATIONAL_SIMULATION` a través de:

```text
CaseProvenance
+ ProjectionOnlySyntheticMaterialBundle
+ ProjectionQualityReceipt(SYNTHETIC_TEST)
+ ProjectionQualityConsumption(TEST_ONLY)
+ PurchaseOperation / DecisionContext exactos
        ↓
validación causal y de provenance
        ↓
run_mvp_execution(...) exactamente una vez
        ↓
ReferenceSimulationExecution
```

La fachada existe para validación del producto EIOS. No es una ruta
operacional empresarial.

## 2. Frontera de autoridad

La ejecución exige simultáneamente:

- `case_kind = REFERENCE_OPERATIONAL_SIMULATION`;
- `material_nature = SYNTHETIC`;
- `qtg_mode_policy = SYNTHETIC_TEST_ONLY`;
- `operational_path = FORBIDDEN`;
- `effect_scope = NO_OPERATIONAL_EFFECT`;
- `validation_scope = PRODUCT_REFERENCE_E2E`;
- `requires_operational_preflight = false`;
- `decision_authority = false`.

La provenance debe ser recomputable desde el bundle exacto.

## 3. QTG

QTG se ejecuta fuera del catálogo genérico de invokers de O1, conservando el
contrato cerrado:

```text
produce_projection_quality(
    execution_mode = SYNTHETIC_TEST
)
        ↓
consume_projection_quality(
    execution_mode = SYNTHETIC_TEST,
    consumption_scope = TEST_ONLY
)
```

La fachada:

- valida receipt contra el envelope exacto;
- valida consumption contra receipt + envelope exactos;
- exige `operational_effect=false`;
- exige `decision_authority=false`;
- conserva los fingerprints;
- no acepta `quality_invoker` ni `qtg_invoker`.

QTG aparece primero en la secuencia arquitectónica del artefacto terminal, pero
no se introduce en la firma cerrada de `run_mvp_execution`.

## 4. Runtime canónico

La fachada extrae del bundle el
`FinanceDecisionInputPackage` ya ligado al envelope y reconstruye:

- `PurchaseOperation`;
- `DecisionContext`.

Los objetos runtime aportados deben ser completamente iguales a esos objetos.
Una diferencia en proveedor, importe, escenario, snapshot, versiones u otro
campo hace fallar la ejecución antes del MVP.

## 5. Ejecución MVP

Tras validar toda la provenance, la fachada delega exactamente una vez en
`run_mvp_execution(...)`.

Solo se aceptan los invokers ya autorizados por ese servicio:

- PRICE;
- TCO;
- SUPPLIER_RISK_VALUE;
- C0;
- DECISION_TWIN;
- SCENARIO_COORDINATION;
- NEGOTIATION_INTELLIGENCE;
- NEGOTIATION_LADDER.

La fachada no introduce nuevas capacidades ni adapta resultados crudos.

## 6. Artefacto terminal

`ReferenceSimulationExecution` es factory-built, inmutable y contiene:

- identidad del caso de referencia;
- CaseProvenance completa + fingerprint;
- fingerprint del dataset;
- fingerprint del bundle;
- fingerprint del envelope;
- fingerprints QTG receipt/consumption;
- resultado funcional QTG;
- PurchaseOperation + fingerprint;
- DecisionContext + fingerprint;
- policy_version;
- secuencia de capacidades, empezando por QTG;
- ExecutionOutcome + fingerprint;
- `runtime_scope = PRODUCT_REFERENCE_VALIDATION_ONLY`;
- `operational_effect = false`;
- `decision_authority = false`;
- `operational_path = FORBIDDEN`;
- fingerprint terminal.

No existe API pública de cierre post-hoc.

## 7. Resultado funcional ≠ efecto operacional

Una simulación puede producir:

- QTG `APTO`;
- `APTO_CON_ADVERTENCIAS`;
- `NO_APTO`;

sin alterar en ningún caso:

```text
material_nature = SYNTHETIC
operational_effect = false
decision_authority = false
operational_path = FORBIDDEN
```

La calidad del caso simulado no promociona su procedencia.

## 8. AUDITAR

### A1 — reutilizar binding operacional

Rechazado. El binding QTG↔O1 operacional exige
`OPERATIONAL/OPERATIONAL` y no se modifica.

### A2 — tercer execution mode

Rechazado. QTG conserva `SYNTHETIC_TEST | OPERATIONAL`.

### A3 — QTG como generic invoker

Rechazado. La firma de referencia no incorpora `qtg_invoker` ni
`quality_invoker`.

### A4 — detached receipt/consumption

Rechazado. Ambos se recomputan contra el envelope exacto.

### A5 — detached PurchaseOperation / DecisionContext

Rechazado. Ambos se reconstruyen desde el DIP anidado del bundle y se exige
igualdad completa.

### A6 — promoción por resultado favorable

Rechazado. Un QTG sintético `APTO/ALTA` continúa sin efecto operacional.

### A7 — cierre post-hoc

Rechazado. No existe builder que acepte un `ExecutionOutcome` ya producido.
La misma fachada posee validación → ejecución → cierre.

### A8 — doble ejecución MVP

Rechazado. La fachada delega exactamente una vez.

## 9. Fuera de alcance

Esta unidad no:

- crea todavía una nueva empresa ficticia de referencia;
- crea plantillas empresariales;
- garantiza que todas las capacidades MVP estén disponibles en un caso;
- modifica ningún motor analítico;
- modifica Operational Admission;
- modifica QTG;
- modifica el binding operacional;
- declara validación en empresa real.

## 10. Materialización

- `eios/core/reference_simulation_execution.py`;
- `tests/test_reference_simulation_execution.py`;
- este contrato.

## 11. Criterio de cierre

CI deberá demostrar:

- suite focal satisfactoria;
- suite completa sin regresión;
- provenance exacta;
- QTG sintético reproducible;
- runtime exacto;
- una única llamada MVP;
- QTG primero en la secuencia terminal;
- ausencia de `qtg_invoker`;
- ausencia de promoción operacional;
- tanto caso QTG negativo como positivo permanecen sin efecto.

## 12. Continuidad

Tras cerrar esta frontera, la siguiente unidad será la construcción del primer:

**EIOS Reference Business Case 001**

Ese caso aportará una empresa ficticia, operación coherente y material
documental sintético de referencia para ampliar progresivamente la cobertura
E2E del producto sin depender de una empresa real.
