# EIOS — Reference Business Case 001 · Provenance-Safe C0 E2E Audit v0.1

**Baseline:** `main @ d416a22cb9d69ceb543e07665c4baab18e64ece9`  
**Fecha:** 23/09/2026  
**Estado:** MATERIALIZADO EN RAMA / CI PENDIENTE

## 1. Propósito

Convertir la fixture física sintética ya existente en el primer caso de
referencia explícito de producto:

`REF-BUSINESS-001`.

No se modifica la fixture ni se cambian etiquetas para obtener un resultado
favorable. Se reutilizan sus bytes físicos, su naturaleza `SYNTHETIC` y sus
limitaciones conocidas.

## 2. Substrato físico

Dataset:

`tests/fixtures/projection_only_semantic_dataset_01`

Identidad técnica:

- dataset: `EIOS-PROJECTION-SEMANTIC-MOCK-001`;
- company: `COMPANY-MOCK-001`;
- decision: `DECISION-MOCK-001`;
- scenario: `SCENARIO-MOCK-001`;
- supplier: `SUPPLIER-MOCK-001`;
- article: `ARTICLE-MOCK-001`;
- quantity: 10;
- unit price: 20,50 EUR;
- total purchase/payment: 205 EUR;
- available treasury: 1.000 EUR;
- treasury minimum: 100 EUR;
- projection horizon: 30 days.

Todos esos datos son sintéticos.

## 3. QTG

El caso se procesa mediante las fronteras cerradas:

```text
ProjectionMockDataset
→ ProjectionOnlySyntheticMaterialBundle
→ ProjectionMaterialEnvelope
→ ProjectionQualityReceipt(SYNTHETIC_TEST)
→ ProjectionQualityConsumption(TEST_ONLY)
```

La fixture física conserva una limitación declarada en su inventario de flujos.

Resultado esperado y preservado:

```text
QTG.status      = NO_APTO
QTG.confidence  = BAJA
operational_effect = false
```

Este resultado no se corrige para facilitar la prueba.

## 4. C0 provenance-safe real

Se elimina el stub utilizado en las pruebas mecánicas de la fachada de
simulación.

La cadena de C0 del caso es:

```text
DecisionEvidenceRequirementSet
        ↓
RequirementEvidenceBinding(DEMONSTRATED)
        ↓
DecisionEvidenceSufficiencyProducer
        ↓
DecisionEvidenceSufficiencyObservation
        ↓
Evidence demostrada y ligada por demonstration_ref
        ↓
evaluate_r_dat_003(...)
        ↓
Assessment
        ↓
build_trace(...)
        ↓
AssessmentTraceBinding
        ↓
build_provenanced_rules_engine_c0_invoker(...)
        ↓
C0 CapabilityExecution
```

La condición de referencia declara cubierto el requisito de calidad documental
seleccionado para R-DAT-003.

Por ello:

```text
R-DAT-003.status  = EVALUABLE
R-DAT-003.outcome = FALSE
```

Esto significa que R-DAT-003 no detecta insuficiencia en **ese requirement set
concreto**. No contradice el `NO_APTO` de QTG, que evalúa una cadena y un
catálogo diferentes.

## 5. Ejecución de referencia

La ejecución terminal utiliza:

`run_reference_operational_simulation(...)`

con:

- `REFERENCE_OPERATIONAL_SIMULATION`;
- QTG sintético exacto;
- PurchaseOperation exacta del bundle;
- DecisionContext exacto del bundle;
- C0 provenance-safe.

Secuencia esperada:

```text
QTG → C0
```

Outcome MVP esperado:

`COMPLETED`

El resultado terminal continúa declarando:

- `operational_effect=false`;
- `decision_authority=false`;
- `operational_path=FORBIDDEN`.

## 6. Lectura correcta del caso

`COMPLETED` describe que la ejecución técnica de las capacidades solicitadas
terminó correctamente.

No significa:

- que QTG sea favorable;
- que la compra esté aprobada;
- que exista una recomendación empresarial;
- que el caso sea real;
- que pueda cruzar a OPERATIONAL.

El caso demuestra precisamente que EIOS puede completar su ejecución técnica
preservando simultáneamente un hallazgo de calidad desfavorable.

## 7. Auditoría

### A1 — fixture convertida en operacional

No. La fixture permanece `SYNTHETIC`.

### A2 — QTG falseado a APTO

No. Se conserva `NO_APTO/BAJA`.

### A3 — C0 stub

Eliminado para esta prueba. C0 procede de un productor factual, regla
R-DAT-003, Assessment y Trace reproducible.

### A4 — Assessment desprendido

No. El invoker valida `AssessmentTraceBinding` contra PurchaseOperation,
DecisionContext, regla y fingerprints exactos.

### A5 — contradicción QTG/C0

No existe. QTG y R-DAT-003 evalúan afirmaciones diferentes. R-DAT-003 solo
declara que el requirement set definido para esta prueba está satisfecho.

### A6 — decisión automática

No. Ninguno de los artefactos concede autoridad decisional.

## 8. Materialización

Se añade exclusivamente:

- `tests/test_reference_business_case_001.py`;
- este documento de auditoría.

No se modifica código de producción.

## 9. Criterio de cierre

CI debe demostrar:

- carga física del dataset;
- construcción completa del bundle;
- receipt/consumption QTG reproducibles;
- conservación de `NO_APTO/BAJA`;
- producción real de R-DAT-003;
- Trace C0 reproducible;
- invoker C0 provenance-safe;
- secuencia terminal `QTG → C0`;
- outcome técnico `COMPLETED`;
- efecto operacional y autoridad decisional falsos.

## 10. Continuidad

Tras este caso se podrá ampliar `REF-BUSINESS-001` capacidad por capacidad,
sin fabricar resultados raw:

1. PRICE;
2. TCO;
3. SUPPLIER_RISK_VALUE;
4. Scenario / Viability;
5. Decision Twin;
6. Negotiation Intelligence;
7. Negotiation Ladder.

Cada incorporación deberá usar su productor/builder provenance-safe específico
o permanecer fuera del caso hasta que esa garantía exista.
