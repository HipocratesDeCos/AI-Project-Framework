# EIOS — R-ENT-001 · Assessment Bridge Design v0.2

**Estado:** DEPURADO TRAS AUDIT 1 — PENDIENTE DE AUDIT 2 FINAL  
**Fecha:** 11/09/2026  
**Base:** `R_ENT_001_Assessment_Bridge_Audit_1_v0.1.md`

---

## 1. Correcciones incorporadas

Se corrigen los tres bloqueadores de Audit 1:

- B01: `baseline_projection_ref` deja de utilizarse como `Evidence.source_ref` obligatorio;
- B02: la vinculación de evidencia se realiza contra refs role-specific de las dependencias ENT originales;
- B03: se incorpora `PurchaseOperation` para demostrar artículo/proveedor y coherencia C0.

No se introduce política empresarial nueva.

---

## 2. Propiedad arquitectónica

El bridge pertenece a:

```text
eios/rules/delivery.py
```

Consume objetos ENT ya materializados pero no llama a `analyze_delivery_stockout()` y no recalcula STK/ENT.

La ausencia de invocación al engine ENT evita convertir por conveniencia técnica la relación RDM EVIDENCE en una nueva dependencia COMPONENT.

---

## 3. Firma cerrada de diseño

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

`analysis_input` se utiliza solo para identity/provenance binding. No se reevalúa ENT dentro del bridge.

---

## 4. Identidad C0

Precondiciones obligatorias:

```text
purchase.decision_id == context.decision_id
purchase.scenario_id == context.scenario_id
rule.rule_id == "R-ENT-001"
rule.version == context.rules_version
rule.requires_evidence == True
```

Una violación es error de contrato/configuración (`ValueError`), no un resultado empresarial `FALSE`.

---

## 5. Identidad Purchase ↔ ENT

Se exige:

```text
analysis_input.decision_id == purchase.decision_id
analysis_input.article_id == purchase.article_id
analysis_input.delivery.supplier_id == purchase.supplier_id

analysis.decision_id == purchase.decision_id
analysis.article_id == purchase.article_id
analysis.supplier_id == purchase.supplier_id
```

Además:

```text
analysis.decision_id == analysis_input.decision_id
analysis.article_id == analysis_input.article_id
analysis.evaluation_date == analysis_input.evaluation_date
analysis.evaluated_purchase_ref == analysis_input.evaluated_purchase_ref
analysis.supplier_id == analysis_input.delivery.supplier_id
analysis.baseline_projection_ref == analysis_input.baseline.baseline_projection_ref
```

No se infiere `purchase.operation_date == analysis.evaluation_date`; son conceptos distintos.

---

## 6. Evidence role binding

### 6.1 Baseline role

```text
baseline_evidence.source_type == "BaselineStockoutQualification"
```

Si `baseline_evidence.state == DEMONSTRATED`, `demonstration_ref` debe pertenecer al conjunto:

```text
baseline_refs =
    analysis_input.baseline.evidence_refs
  ∪ analysis_input.baseline.trace_refs
  ∪ {baseline_relation_ref if not null}
  ∪ {projection_provenance_ref if not null}
  ∪ {purchase_exclusion_ref if not null}
```

No se exige que `source_ref` sea `baseline_projection_ref`.

### 6.2 Delivery role

```text
delivery_evidence.source_type == "PurchaseSpecificDeliveryTimingEvidence"
```

Si `delivery_evidence.state == DEMONSTRATED`, `demonstration_ref` debe pertenecer a:

```text
delivery_refs =
    analysis_input.delivery.evidence_refs
  ∪ analysis_input.delivery.trace_refs
  ∪ {delivery_semantic_ref if not null}
  ∪ {purchase_applicability_ref if not null}
  ∪ {source_ref if not null}
```

### 6.3 GAP

Una evidencia C0 `GAP` no necesita `demonstration_ref`; permanece `INVALID` conforme a `validate_evidence()`.

El rol se sigue verificando mediante `source_type`.

---

## 7. Validación C0

El bridge utiliza:

```text
validate_evidence(baseline_evidence)
validate_evidence(delivery_evidence)
```

No replica ni modifica sus reglas.

`both_valid` significa:

```text
baseline_validation.status == VALID
and
delivery_validation.status == VALID
```

---

## 8. Precedencia de evaluación

Orden determinista:

### Paso 1 — contrato e identidad

Cualquier incompatibilidad de secciones 4–6:

```text
raise ValueError
```

### Paso 2 — estado ENT no concluyente

```text
NOT_EVIDENCED     → NOT_EVALUABLE / None
CONFLICTING_DATA  → NOT_EVALUABLE / None
NOT_DETERMINABLE  → NOT_EVALUABLE / None
```

No se transforma en FALSE aunque ambas evidencias C0 estén DEMONSTRATED.

### Paso 3 — suficiencia C0 para estado ENT concluyente

Para cualquiera de:

```text
LATE_DELIVERY_DEMONSTRATED
NOT_LATE_DEMONSTRATED
NOT_LATE_WITHIN_EVIDENCED_HORIZON
```

si `both_valid == False`:

```text
NOT_EVALUABLE / None
```

### Paso 4 — booleano de regla

Con ambas evidencias VALID:

```text
LATE_DELIVERY_DEMONSTRATED
→ EVALUABLE / TRUE

NOT_LATE_DEMONSTRATED
→ EVALUABLE / FALSE

NOT_LATE_WITHIN_EVIDENCED_HORIZON
→ EVALUABLE / FALSE
```

---

## 9. SAME_DAY

`NOT_LATE_DEMONSTRATED` con:

```text
SAME_DAY_ORDER_NOT_DEMONSTRATED
```

permanece `EVALUABLE / FALSE`, porque igualdad de fecha no satisface la condición estricta `delivery > depletion`.

Reason específico:

```text
"R-ENT-001 no demostrada: entrega y agotamiento en la misma fecha; orden intradía no demostrado."
```

No afirma qué evento ocurrió primero dentro del día.

---

## 10. NOT_LATE_WITHIN_EVIDENCED_HORIZON

Permanece `EVALUABLE / FALSE` solo porque ENT ya ha demostrado:

```text
depletion_state = NOT_APPLICABLE
expected_delivery_date <= horizon_end
```

Reason:

```text
"R-ENT-001 no demostrada dentro del horizonte STK evidenciado."
```

No se extrapola más allá del horizonte.

---

## 11. Reasons deterministas

```text
LATE + VALID
→ "R-ENT-001 demostrada: entrega posterior al agotamiento estimado."

NOT_LATE + VALID
→ "R-ENT-001 no demostrada: entrega no posterior al agotamiento estimado."

SAME_DAY + VALID
→ "R-ENT-001 no demostrada: entrega y agotamiento en la misma fecha; orden intradía no demostrado."

HORIZON + VALID
→ "R-ENT-001 no demostrada dentro del horizonte STK evidenciado."

NOT_EVIDENCED
→ "R-ENT-001 no evaluable: evidencia factual ENT insuficientemente demostrada."

CONFLICTING_DATA
→ "R-ENT-001 no evaluable: evidencia factual ENT contradictoria."

NOT_DETERMINABLE
→ "R-ENT-001 no evaluable: relación temporal ENT no determinable."

ENT concluyente + alguna evidencia C0 INVALID
→ "R-ENT-001 no evaluable: una o más dependencias C0 no están demostradas."
```

Ningún reason contiene recomendación, efecto, severidad o resolución CRC.

---

## 12. evidence_ids

El Assessment conserva exactamente los IDs C0 presentados, en orden de dependencia:

```text
[
  baseline_evidence.evidence_id,
  delivery_evidence.evidence_id,
]
```

No se deduplican por inferencia; el comportamiento reproduce el principio C0 de conservar los IDs de evidencia presentados.

No se convierten refs ENT en `evidence_ids`.

---

## 13. RDM

Se consumen únicamente:

```text
DEP-ENT-BSQ-RENT-001
DEP-ENT-DTE-RENT-001
```

No se modifican ni infieren:

```text
Criticality = PENDING
Evaluability_Impact = PENDING
Fallback = NONE
Affected_Component = NONE
```

El bridge no escribe RDM.

---

## 14. Fronteras negativas

La unidad no puede:

- producir `NEGOCIAR`;
- copiar efecto/severidad a Assessment;
- ejecutar CRC;
- modificar C0;
- modificar ENT/STK/Supplier;
- convertir GAP/ausencia/contradicción en FALSE;
- derivar delivery desde lead time;
- inferir nuevos parámetros;
- crear un tercer requisito de evidencia RDM;
- persistir resultados.

---

## 15. Alcance físico si Audit 2 supera

```text
eios/rules/delivery.py
tests/test_r_ent_001_assessment_bridge.py
```

`eios/rules/__init__.py` solo podrá modificarse para exportación explícita, sin lógica adicional.

---

## 16. Estado

**DISEÑO v0.2 DEPURADO.**  
**Pendiente:** AUDIT 2 FINAL.  
**Implementación:** NO AUTORIZADA.  
**Política empresarial nueva:** 0.
