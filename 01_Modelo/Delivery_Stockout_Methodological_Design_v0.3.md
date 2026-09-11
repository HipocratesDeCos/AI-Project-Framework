# EIOS — ENTREGA / R-ENT-001 · METHODOLOGICAL DESIGN v0.3

**Estado:** DEPURADO TRAS AUDIT 2 — PENDIENTE DE AUDIT 2 FINAL  
**Fecha:** 11/09/2026  
**Base:** `Delivery_Stockout_Methodological_Audit_2_v0.2.md`

---

## 1. Corrección ENT-A2-01

Se elimina el mapeo causal ambiguo de `depletion_state = UNKNOWN`.

Regla cerrada:

```text
STK depletion_state = UNKNOWN
→ ENT temporal relation = NOT_DETERMINABLE
```

ENT conserva las causas y referencias STK, pero no reclasifica el estado por heurística.

---

## 2. Entradas conceptuales cerradas

### 2.1 BaselineStockoutQualification

```text
BaselineStockoutQualification
├── decision_id
├── article_id
├── evaluation_date
├── baseline_projection_ref
├── baseline_relation_ref
├── projection_provenance_ref
├── evaluated_purchase_trace_ref
├── proposed_purchase_exclusion_ref
├── depletion_state
├── depletion_date: date | null
├── horizon_end
├── unresolved_refs
├── issue_refs
├── limitations
└── trace_refs
```

Semántica:

- demuestra que la proyección pertenece al contexto decisional correcto;
- demuestra que representa el baseline previo a la compra evaluada;
- demuestra exclusión de la entrada `PROPOSED_PURCHASE` correspondiente;
- conserva el estado/fecha/horizonte STK sin recalcularlos.

No crea identidad global de escenario o compra.

### 2.2 PurchaseSpecificDeliveryTimingEvidence

```text
PurchaseSpecificDeliveryTimingEvidence
├── decision_id
├── article_id
├── supplier_id
├── evaluation_date
├── evaluated_purchase_trace_ref
├── expected_delivery_date: date | null
├── state
├── delivery_semantic_ref
├── purchase_applicability_ref
├── source_ref
├── evidence_refs
├── captured_at
├── valid_from / valid_to
├── issue_refs
└── trace_refs
```

Estados:

```text
KNOWN
NOT_EVIDENCED
CONFLICTING_DATA
NOT_DETERMINABLE
```

---

## 3. Precondiciones de comparación

La comparación solo puede ser concluyente si:

1. baseline cualificado;
2. exclusión de compra demostrada;
3. `decision_id` compatible;
4. `article_id` compatible;
5. `evaluated_purchase_trace_ref` compatible;
6. delivery evidence aplicable al proveedor/propuesta evaluados;
7. delivery state `KNOWN`;
8. depletion state `KNOWN` o `NOT_APPLICABLE`;
9. sin contradicción material no resuelta en las dependencias.

Si falla una precondición de identidad/provenance:

```text
NOT_DETERMINABLE
```

---

## 4. Precedencia determinista

### Paso 1 — baseline/provenance

Falta o incompatibilidad material:

```text
NOT_DETERMINABLE
```

Contradicción explícita:

```text
CONFLICTING_DATA
```

### Paso 2 — delivery evidence

```text
NOT_EVIDENCED   → NOT_EVIDENCED
CONFLICTING_DATA → CONFLICTING_DATA
NOT_DETERMINABLE → NOT_DETERMINABLE
KNOWN            → continuar
```

### Paso 3 — depletion STK

```text
CONFLICTING_DATA → CONFLICTING_DATA
UNKNOWN          → NOT_DETERMINABLE
KNOWN            → comparar fecha
NOT_APPLICABLE   → evaluar contra horizon_end
```

No existe otro mapeo implícito.

### Paso 4 — depletion KNOWN

```text
expected_delivery_date > depletion_date
→ LATE_DELIVERY_DEMONSTRATED

expected_delivery_date < depletion_date
→ NOT_LATE_DEMONSTRATED

expected_delivery_date == depletion_date
→ NOT_LATE_DEMONSTRATED
+ SAME_DAY_ORDER_NOT_DEMONSTRATED
```

### Paso 5 — depletion NOT_APPLICABLE

```text
expected_delivery_date <= horizon_end
→ NOT_LATE_WITHIN_EVIDENCED_HORIZON

expected_delivery_date > horizon_end
→ NOT_DETERMINABLE
+ DELIVERY_BEYOND_STK_HORIZON
```

---

## 5. Delivery date pasada

Una fecha de entrega anterior a `evaluation_date` no se corrige ni se descarta automáticamente.

Si su semántica y aplicabilidad a la propuesta actual están demostradas, ENT conserva el dato y ejecuta la comparación normativa.

Si no se demuestra por qué sigue siendo aplicable:

```text
NOT_DETERMINABLE
+ PAST_DELIVERY_DATE_APPLICABILITY_UNPROVEN
```

---

## 6. Supplier adapter

Supplier `DELIVERY_DATE` puede alimentar delivery evidence solo mediante adaptación trazable.

Requisitos mínimos:

```text
dimension = DELIVERY_DATE
value_kind = DATE
state = KNOWN
semantic_ref compatible
purchase applicability demostrada externamente
supplier/article compatibles
```

No existe elevación automática por nombre de dimensión.

---

## 7. Lead time

ENT no calcula fecha desde lead time.

Una fecha derivada externamente puede consumirse solo si su derivación está autorizada/trazada.

---

## 8. Frontera de resultado

Estados analíticos ENT:

```text
LATE_DELIVERY_DEMONSTRATED
NOT_LATE_DEMONSTRATED
NOT_LATE_WITHIN_EVIDENCED_HORIZON
NOT_EVIDENCED
CONFLICTING_DATA
NOT_DETERMINABLE
```

No son:

- Assessment;
- recommendation;
- CRC result;
- decisión.

Rules conserva la autoridad para evaluar `R-ENT-001`.

---

## 9. RDM

Tras cierre metodológico, la evidencia documental especializada demostrará dos dependencias conceptuales:

```text
R-ENT-001 → BaselineStockoutQualification
R-ENT-001 → PurchaseSpecificDeliveryTimingEvidence
```

La incorporación canónica a RDM requerirá materialización documental explícita posterior y no incluirá atributos no demostrados.

---

## 10. Parámetros

No se crea parámetro ENT.

No existe umbral adicional: la condición vigente es estrictamente `delivery_date > depletion_date`.

---

## 11. Invariantes finales

1. scenario_id no demuestra baseline;
2. baseline sin compra es obligatorio;
3. exclusion ref obligatoria;
4. ENT no recalcula STK;
5. STK UNKNOWN → ENT NOT_DETERMINABLE;
6. delivery date propuesta-específica;
7. Supplier DELIVERY_DATE no implica aplicabilidad;
8. lead time no deriva fecha internamente;
9. igualdad no satisface “posterior”;
10. igualdad conserva limitación intradía;
11. NOT_APPLICABLE no se extrapola fuera del horizonte;
12. ausencia != puntualidad;
13. contradicción no se resuelve arbitrariamente;
14. no parameter ENT;
15. ENT no produce NEGOCIAR/Assessment/CRC/decisión.

---

## 12. Estado

**ENT v0.3 — DEPURADO.**  
**Pendiente:** AUDIT 2 FINAL.  
**Implementación:** NO AUTORIZADA.  
**Política empresarial nueva:** 0.
