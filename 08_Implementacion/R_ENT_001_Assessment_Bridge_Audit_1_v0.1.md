# EIOS — R-ENT-001 · Assessment Bridge Audit 1 v0.1

**Estado:** NO SUPERADA — DEPURACIÓN REQUERIDA  
**Fecha:** 11/09/2026  
**Objeto:** `R_ENT_001_Assessment_Bridge_Design_v0.1.md`

---

## 1. Dictamen

El mapeo de estados ENT → Assessment es coherente, pero el diseño v0.1 no demuestra todavía de forma suficiente la identidad operacional ni la vinculación role-specific de las evidencias C0.

**Bloqueadores:** 3.  
**Política empresarial nueva detectada:** 0.

---

## 2. ENT-A1-B01 — source_ref de baseline semánticamente incorrecto

**Severidad:** BLOQUEADOR.

El diseño exige:

```text
baseline_evidence.source_ref = analysis.baseline_projection_ref
```

pero el rol declarado es:

```text
source_type = BaselineStockoutQualification
```

`baseline_projection_ref` identifica una proyección STK, no identifica por sí sola la cualificación de baseline ni demuestra relación/provenance/exclusión de la compra.

### Corrección requerida

No fijar `Evidence.source_ref` a una referencia de otro concepto.

La vinculación debe realizarse mediante una referencia de demostración perteneciente específicamente a la dependencia original `BaselineStockoutQualification`, conservando `source_ref` bajo la semántica general del Evidence Contract.

---

## 3. ENT-A1-B02 — refs agregadas permiten cruce de roles

**Severidad:** BLOQUEADOR.

El diseño permite que ambas evidencias validen `demonstration_ref` contra:

```text
analysis.evidence_refs ∪ analysis.trace_refs
```

pero el resultado ENT agrega refs de baseline y delivery.

Por tanto una evidencia declarada como baseline podría enlazarse materialmente a una ref procedente de delivery, o viceversa.

### Corrección requerida

El bridge debe disponer de la provenance original separada:

```text
DeliveryStockoutAnalysisInput
├── baseline: BaselineStockoutQualification
└── delivery: PurchaseSpecificDeliveryTimingEvidence
```

Los conjuntos de refs válidas se construyen por rol, nunca desde el agregado del resultado.

---

## 4. ENT-A1-B03 — identidad artículo/proveedor no demostrada

**Severidad:** BLOQUEADOR.

`DecisionContext` no contiene `article_id` ni `supplier_id`.

Con la firma v0.1 sería posible presentar un `DeliveryStockoutAnalysisResult` del mismo `decision_id` pero de otro artículo/proveedor sin que el bridge pudiera demostrar incompatibilidad contra el input C0.

### Corrección requerida

Incorporar `PurchaseOperation` y exigir:

```text
purchase.decision_id == context.decision_id
purchase.scenario_id == context.scenario_id
analysis.article_id == purchase.article_id
analysis.supplier_id == purchase.supplier_id
analysis_input.article_id == purchase.article_id
analysis_input.delivery.supplier_id == purchase.supplier_id
```

También debe comprobarse que `analysis` y `analysis_input` comparten `decision_id`, `article_id`, `evaluation_date` y `evaluated_purchase_ref`.

---

## 5. ENT-A1-04 — mapeo factual

**SUPERADO.**

El mapeo propuesto preserva las autoridades:

```text
LATE_DELIVERY_DEMONSTRATED           → EVALUABLE / TRUE
NOT_LATE_DEMONSTRATED                → EVALUABLE / FALSE
NOT_LATE_WITHIN_EVIDENCED_HORIZON    → EVALUABLE / FALSE
NOT_EVIDENCED                        → NOT_EVALUABLE / None
CONFLICTING_DATA                     → NOT_EVALUABLE / None
NOT_DETERMINABLE                     → NOT_EVALUABLE / None
```

`NOT_LATE_WITHIN_EVIDENCED_HORIZON` es concluyente únicamente porque ENT ya exige delivery dentro del horizonte evidenciado. No autoriza extrapolación fuera de él.

---

## 6. ENT-A1-05 — GAP y FALSE

**SUPERADO.**

El diseño conserva:

```text
GAP ≠ FALSE
INVALID evidence ≠ FALSE
```

Un estado ENT concluyente sin las dos evidencias C0 válidas debe resultar `NOT_EVALUABLE`.

---

## 7. ENT-A1-06 — RDM

**SUPERADO con salvaguarda.**

El bridge puede consumir las dos dependencias `CONFIRMED` sin modificar los metadatos todavía `PENDING`.

No debe escribir ni inferir:

```text
Criticality
Evaluability_Impact
Affected_Component
```

La lógica del bridge se limita a determinar el `Assessment` concreto a partir de las dependencias efectivamente presentadas y del resultado factual ENT.

---

## 8. ENT-A1-07 — propiedad arquitectónica

**SUPERADO.**

La conversión a `Assessment` pertenece a `eios/rules`, no a ENT.

No se debe modificar `eios/delivery/*` para realizar esta conversión.

---

## 9. Diseño corregido requerido

Firma conceptual revisada:

```text
evaluate_r_ent_001(
    purchase: PurchaseOperation,
    context: DecisionContext,
    rule: Rule,
    analysis_input: DeliveryStockoutAnalysisInput,
    analysis: DeliveryStockoutAnalysisResult,
    baseline_evidence: Evidence,
    delivery_evidence: Evidence,
) -> Assessment
```

El bridge no recalcula ENT; `analysis_input` se consume exclusivamente para identity/provenance binding.

---

## 10. Regla de binding role-specific

### Baseline

`baseline_evidence.source_type` debe ser exactamente:

```text
BaselineStockoutQualification
```

Si `DEMONSTRATED`, `demonstration_ref` debe pertenecer al conjunto de refs explícitas del objeto baseline:

```text
baseline.evidence_refs
∪ baseline.trace_refs
∪ {baseline.baseline_relation_ref}
∪ {baseline.projection_provenance_ref}
∪ {baseline.purchase_exclusion_ref}
```

No se utiliza `baseline_projection_ref` como sustituto automático de la cualificación.

### Delivery

`delivery_evidence.source_type` debe ser exactamente:

```text
PurchaseSpecificDeliveryTimingEvidence
```

Si `DEMONSTRATED`, `demonstration_ref` debe pertenecer a:

```text
delivery.evidence_refs
∪ delivery.trace_refs
∪ {delivery.delivery_semantic_ref}
∪ {delivery.purchase_applicability_ref}
∪ {delivery.source_ref}
```

Refs nulas se excluyen del conjunto.

---

## 11. Resultado

**AUDIT 1: NO SUPERADA.**

Procede DEPURAR diseño a v0.2 cerrando B01–B03.  
Implementación continúa **NO AUTORIZADA**.
