# EIOS — Supplier Risk / Value External Assessment Completion Package v0.1

**Baseline:** `main @ e4638f871efc2e2cb30506fba8000c6e499b44e1`  
**Fecha:** 23/09/2026  
**Estado:** 🔒 AUTORIZADO — VIGENTE

## 1. Objetivo

Cerrar una primera capacidad provenance-safe de Capa 5 para:

- representar riesgo de proveedor;
- representar valor contextual de proveedor;
- consumir determinaciones externas autorizadas por dimensión;
- entregar resultados trazables a capas posteriores;

sin crear:

- supplier score;
- ranking;
- preferred supplier;
- fiabilidad nativa;
- cumplimiento nativo;
- concentración nativa;
- trade-off automático;
- recomendación.

## 2. Principio

```text
Supplier Evidence ≠ Supplier Risk Score
Historical Fact ≠ Current Risk
External Metric ≠ Authorized Metric by default
Difference ≠ Superiority
Value Dimension ≠ Supplier Ranking
```

## 3. Dimensiones Risk v0.1

Se propone admitir únicamente:

```text
RELIABILITY
COMPLIANCE
AVAILABILITY
CONCENTRATION
CRITICAL_SIGNAL
```

Cada dimensión debe llegar ya evaluada por una metodología externa competente.

Estados:

```text
FAVORABLE
ADVERSE
NOT_DETERMINABLE
CONFLICTING
```

No existe estado NEUTRAL implícito.

## 4. Dimensiones Value v0.1

Se propone admitir únicamente:

```text
PRICE
PAYMENT_TERM
COMMERCIAL_CONDITIONS
RELIABILITY
AVAILABILITY
```

Estados:

```text
BETTER
EQUIVALENT
WORSE
NOT_DETERMINABLE
CONFLICTING
```

`BETTER` solo puede ser suministrado por autoridad externa que ya haya resuelto la comparabilidad y la semántica de mejora.

Supplier Risk/Value no infiere BETTER desde:

- difference_decimal;
- STRUCTURALLY_COMPARABLE;
- EVIDENCED_CANDIDATE;
- PRICE result sin autoridad de mejora;
- una observación aislada.

## 5. Carrier Risk propuesto

```text
SupplierRiskDimensionAssessment
├── supplier_id
├── dimension
├── state
├── authority_ref
├── methodology_ref
├── assessment_ref
├── evidence_refs
└── trace_refs
```

Requisitos:

- authority_ref explícita;
- methodology_ref explícita;
- assessment_ref explícita;
- evidence_refs DEMONSTRATED;
- trace_refs no vacías.

## 6. Carrier Value propuesto

```text
SupplierValueDimensionAssessment
├── supplier_id
├── comparison_supplier_id?
├── dimension
├── state
├── authority_ref
├── methodology_ref
├── assessment_ref
├── evidence_refs
└── trace_refs
```

Para estados BETTER/EQUIVALENT/WORSE se exige `comparison_supplier_id`.

No se permite comparar un proveedor consigo mismo.

## 7. Resultado agregado no-score

Se propone:

```text
SupplierRiskValueResult
├── decision_id
├── scenario_id
├── article_id
├── current_supplier_id
├── risk_dimensions[]
├── value_dimensions[]
├── unresolved_items[]
├── evidence_refs[]
└── trace_refs[]
```

No contiene:

- score;
- total;
- media;
- peso;
- rank;
- selected_supplier;
- recommendation.

## 8. Semántica unresolved

Se añade `unresolved_items` cuando:

- exista NOT_DETERMINABLE;
- exista CONFLICTING;
- falte autoridad demostrada;
- exista mismatch de identidad;
- una dimensión Value comparativa carezca de comparison_supplier_id.

No se convierten gaps en FAVORABLE/EQUIVALENT.

## 9. Productor

API propuesta:

```text
produce_supplier_risk_value(
    purchase,
    context,
    supplier_result,
    risk_assessments,
    value_assessments,
    evidences
) -> SupplierRiskValueResult
```

Debe revalidar:

- PurchaseOperation ↔ DecisionContext;
- SupplierEvidenceResult ↔ PurchaseOperation/DecisionContext;
- supplier_id;
- article_id;
- decision_id;
- scenario_id;
- rules_version;
- parameters_version;
- data_snapshot_id;
- Evidence DEMONSTRATED.

## 10. Relación con PROV

El productor puede consumir como contexto:

- SupplierEvidenceResult;
- determinaciones PROV ya autorizadas;

pero no promociona automáticamente:

```text
POTENTIALLY_BETTER → VALUE.BETTER
SIGNIFICANT_IMPROVEMENT → preferred supplier
COMPARABLE → EQUIVALENT
```

Si se desea reutilizar una determinación PROV como Value, debe existir una authority_ref que declare explícitamente esa equivalencia.

## 11. Relación con Viability

v0.1 no mapea Supplier Risk/Value directamente a H/K/U/S.

Cualquier incorporación a Viability Frontier requerirá un catálogo explícito posterior.

## 12. Relación con Rules / CRC

v0.1 no ejecuta reglas.

No modifica:

- R-PROV-001;
- R-PROV-002;
- CRC;
- Decision Twin;
- NI;
- Ladder.

## 13. Invocador O1

Se propone:

```text
build_provenanced_supplier_risk_value_invoker(...)
→ (PurchaseOperation, DecisionContext) -> CapabilityExecution
```

Capability:

```text
SUPPLIER_RISK_VALUE
```

Estados:

- COMPLETED si no existen unresolved_items;
- PARTIALLY_COMPLETED si existen unresolved_items;
- no produce recomendación.

## 14. No alcance

No autoriza:

- reliability ratio;
- compliance ratio;
- incident rate;
- concentration formula;
- concentration threshold;
- supplier risk score;
- supplier value score;
- weighted matrix;
- supplier ranking;
- preferred supplier;
- automatic switching;
- threshold defaults;
- inference from missing data;
- LLM valuation.

## 15. Tests mínimos

1. external Risk FAVORABLE preserved;
2. external Risk ADVERSE preserved;
3. NOT_DETERMINABLE creates unresolved;
4. CONFLICTING creates unresolved;
5. Value BETTER requires comparison_supplier_id;
6. self-comparison rejected;
7. authority_ref not demonstrated → fail closed;
8. GAP does not authorize;
9. identity mismatch → fail closed;
10. no score/rank fields;
11. deterministic ordering;
12. duplicate dimensions rejected per supplier+dimension+comparison;
13. invoker O1 COMPLETED;
14. invoker O1 PARTIALLY_COMPLETED with unresolved;
15. no VF/CRC side effect.

## 16. Efecto de autorización

```text
AUTORIZAR
→ AUDITAR
→ MATERIALIZAR
   - Risk carriers
   - Value carriers
   - SupplierRiskValueResult
   - provenance-safe producer
   - O1 invoker
   - tests
→ CI
→ merge
→ CI main
```

## 17. Autorización humana

Autorizado expresamente el 23/09/2026 como paquete único de cierre Supplier Risk / Value v0.1.

La autorización comprende las taxonomías Risk/Value, sus estados, carriers de determinaciones externas, regla de no agregación y exposición O1 informativa, sin fórmulas ni scores nativos.

**SUPPLIER RISK / VALUE EXTERNAL ASSESSMENT COMPLETION PACKAGE v0.1 — 🔒 AUTORIZADO / VIGENTE.**
