# EIOS — DELIVERY / STOCKOUT ANALYZER · IMPLEMENTATION CONTRACT v0.3

**Estado:** DEPURADO TRAS AUDIT 2 — PENDIENTE DE AUDIT 2 FINAL  
**Fecha:** 11/09/2026  
**Diseño activo:** v0.3  
**Baseline:** `main @ ee4e149c42fe8f1c6619fb62387397dc63767ea8`

---

## 1. Autoridad

Este contrato materializa exclusivamente la capa factual cerrada por:

- metodología ENT v0.3;
- Audit 2 final metodológico v0.3;
- cierre metodológico v0.3;
- reconciliación metodológica v0.3.1;
- especificación `R-ENT-001` v1.0;
- RDM v1.5;
- contratos físicos STK/Supplier vigentes.

No redefine Rules, Assessment, CRC ni decisión empresarial.

---

## 2. Frontera física

Tras cierre:

```text
eios/delivery/
├── __init__.py
├── models.py
└── engine.py
```

No se autoriza en esta unidad:

- `adapters.py` Supplier automático;
- cambios en `eios/core`;
- cambios en `eios/stock`;
- cambios en `eios/supplier`;
- SQL/persistencia;
- parámetros ENT;
- bridge a Assessment.

---

## 3. Estados

```text
BaselineQualificationState =
    KNOWN
    CONFLICTING_DATA
    NOT_DETERMINABLE

DeliveryTimingEvidenceState =
    KNOWN
    NOT_EVIDENCED
    CONFLICTING_DATA
    NOT_DETERMINABLE

DeliveryAnalysisState =
    LATE_DELIVERY_DEMONSTRATED
    NOT_LATE_DEMONSTRATED
    NOT_LATE_WITHIN_EVIDENCED_HORIZON
    NOT_EVIDENCED
    CONFLICTING_DATA
    NOT_DETERMINABLE

DeliveryLimitationCode =
    SAME_DAY_ORDER_NOT_DEMONSTRATED
    DELIVERY_BEYOND_STK_HORIZON
    PAST_DELIVERY_DATE_APPLICABILITY_UNPROVEN
```

Son estados/códigos locales ENT, no estados de Assessment.

---

## 4. Referencia de propuesta

`evaluated_purchase_ref` es la representación física local de `evaluated_purchase_trace_ref`.

Debe ser no vacía y trazable, pero:

```text
evaluated_purchase_ref ≠ Purchase_ID global
evaluated_purchase_ref ≠ scenario_id
```

No modifica `PurchaseOperation`.

---

## 5. `BaselineStockoutQualification`

```text
BaselineStockoutQualification
├── decision_id: str
├── article_id: str
├── evaluation_date: date
├── evaluated_purchase_ref: str
├── baseline_projection_ref: str
├── projection: StockProjectionResult
├── state: BaselineQualificationState
├── baseline_relation_ref: str | None
├── projection_provenance_ref: str | None
├── purchase_exclusion_ref: str | None
├── evidence_refs: tuple[str, ...]
├── unresolved_refs: tuple[str, ...]
├── issue_refs: tuple[str, ...]
├── limitations: tuple[str, ...]
└── trace_refs: tuple[str, ...]
```

### 5.1 Invariantes internas

Siempre:

```text
decision_id == projection.identity.decision_id
article_id == projection.identity.article_id
evaluation_date == projection.identity.evaluation_date
```

Un objeto que viole estas igualdades está internamente malformado y debe ser rechazado por validación.

### 5.2 KNOWN

Requiere:

- `baseline_projection_ref`;
- `baseline_relation_ref`;
- `projection_provenance_ref`;
- `purchase_exclusion_ref`;
- al menos una referencia en `evidence_refs` o `trace_refs`;
- `unresolved_refs` vacío.

No se infiere baseline desde `scenario_id`, nombre de escenario ni contenido visible del resultado STK.

### 5.3 CONFLICTING_DATA

Requiere al menos un `issue_ref` o `unresolved_ref`.

### 5.4 NOT_DETERMINABLE

Representa falta/incompatibilidad de provenance suficiente para demostrar baseline.

No equivale a `FALSE` ni a baseline válido.

---

## 6. `PurchaseSpecificDeliveryTimingEvidence`

```text
PurchaseSpecificDeliveryTimingEvidence
├── decision_id: str
├── article_id: str
├── supplier_id: str
├── evaluation_date: date
├── evaluated_purchase_ref: str
├── state: DeliveryTimingEvidenceState
├── expected_delivery_date: date | None
├── delivery_semantic_ref: str | None
├── purchase_applicability_ref: str | None
├── source_ref: str | None
├── evidence_refs: tuple[str, ...]
├── captured_at: date | None
├── valid_from: date | None
├── valid_to: date | None
├── issue_refs: tuple[str, ...]
└── trace_refs: tuple[str, ...]
```

### 6.1 Vigencia estructural

Si ambas existen:

```text
valid_to >= valid_from
```

ENT no crea una política universal de expiración a partir de ese intervalo.

### 6.2 KNOWN

Requiere:

- `expected_delivery_date`;
- `delivery_semantic_ref`;
- `purchase_applicability_ref`;
- `source_ref`;
- `captured_at`;
- al menos un `evidence_ref`.

Solo `KNOWN` habilita la comparación temporal.

### 6.3 NOT_EVIDENCED

Puede conservar `expected_delivery_date` si existe un valor declarado, conforme a M09.

Ese valor:

- no es utilizable para comparar;
- no se promueve a KNOWN;
- permanece acompañado por `state = NOT_EVIDENCED`;
- conserva cualquier fuente/evidencia disponible.

También es válido `expected_delivery_date = None` si ni siquiera existe un valor declarado utilizable.

### 6.4 CONFLICTING_DATA

No publica una fecha única resuelta:

```text
expected_delivery_date = None
```

Requiere al menos un `issue_ref`.

### 6.5 NOT_DETERMINABLE

Puede conservar una fecha factual cuando la fecha está identificada pero no se demuestra su aplicabilidad a la propuesta actual.

Si publica fecha, requiere al menos:

- `delivery_semantic_ref`;
- `source_ref`;
- `captured_at`;
- un `evidence_ref`.

La presencia de fecha no permite comparación mientras el estado no sea KNOWN.

---

## 7. Contexto objetivo del análisis

Para evitar elegir arbitrariamente entre dependencias incompatibles, el envelope declara el contexto que se pretende analizar:

```text
DeliveryStockoutAnalysisInput
├── decision_id: str
├── article_id: str
├── evaluation_date: date
├── evaluated_purchase_ref: str
├── baseline: BaselineStockoutQualification
└── delivery: PurchaseSpecificDeliveryTimingEvidence
```

Estos cuatro campos no crean identidad nueva; repiten explícitamente el contexto objetivo que ambas dependencias deben soportar.

El modelo **no valida por excepción** que baseline/delivery coincidan con el contexto objetivo. Esa comprobación pertenece al engine porque la metodología exige producir `NOT_DETERMINABLE` ante incompatibilidad entre dependencias válidas.

---

## 8. Malformed vs incompatible

### 8.1 Malformed

Se rechaza al construir el modelo cuando un objeto contradice su propia carga interna, por ejemplo:

```text
baseline.decision_id != baseline.projection.identity.decision_id
baseline.evaluation_date != baseline.projection.identity.evaluation_date
CONFLICTING_DATA sin issue/unresolved ref
KNOWN sin refs obligatorias
valid_to < valid_from
```

### 8.2 Incompatible

El engine devuelve `NOT_DETERMINABLE` cuando objetos válidos por separado no soportan el mismo contexto objetivo:

```text
input.decision_id != baseline.decision_id
input.decision_id != delivery.decision_id
input.article_id != baseline.article_id
input.article_id != delivery.article_id
input.evaluation_date != baseline.evaluation_date
input.evaluation_date != delivery.evaluation_date
input.evaluated_purchase_ref != baseline.evaluated_purchase_ref
input.evaluated_purchase_ref != delivery.evaluated_purchase_ref
```

No se selecciona una de las identidades como correcta por heurística.

---

## 9. `DeliveryStockoutAnalysisResult`

```text
DeliveryStockoutAnalysisResult
├── decision_id: str
├── article_id: str
├── evaluation_date: date
├── evaluated_purchase_ref: str
├── supplier_id: str
├── baseline_projection_ref: str
├── state: DeliveryAnalysisState
├── depletion_date: date | None
├── expected_delivery_date: date | None
├── horizon_end: date | None
├── limitation_codes: tuple[DeliveryLimitationCode, ...]
├── evidence_refs: tuple[str, ...]
├── unresolved_refs: tuple[str, ...]
├── issue_refs: tuple[str, ...]
└── trace_refs: tuple[str, ...]
```

Los cuatro primeros campos proceden del contexto objetivo del input; no se eligen desde una dependencia incompatible.

`supplier_id` se conserva desde delivery evidence como dato fuente, sin convertirlo en autoridad de identidad del análisis.

Las fechas se copian únicamente desde las entradas; no se sintetizan.

---

## 10. Adaptación referencial de incidencias STK

STK publica:

```text
StockProjectionResult.issue_refs: tuple[DataIssueRef, ...]
```

ENT publica solo referencias string.

La transformación autorizada es exclusivamente:

```text
for issue in projection.issue_refs:
    ENT issue_refs += issue.issue_record_ref
```

ENT no:

- serializa el objeto completo;
- cambia `issue_type`;
- resuelve la incidencia;
- inventa texto explicativo;
- usa `issue_id` como sustituto si `issue_record_ref` ya existe.

`projection.trace_refs` se preserva por separado en `trace_refs`.

---

## 11. Engine determinista

```text
analyze_delivery_stockout(payload)
→ DeliveryStockoutAnalysisResult
```

### Paso 1 — compatibilidad de contexto

Si cualquiera de las ocho comparaciones del §8.2 falla:

```text
→ NOT_DETERMINABLE
```

Se preservan refs/issues/traces disponibles.

No se ejecuta comparación temporal.

### Paso 2 — baseline

```text
CONFLICTING_DATA → CONFLICTING_DATA
NOT_DETERMINABLE → NOT_DETERMINABLE
KNOWN            → continuar
```

### Paso 3 — delivery

```text
NOT_EVIDENCED    → NOT_EVIDENCED
CONFLICTING_DATA → CONFLICTING_DATA
```

Si:

```text
state = NOT_DETERMINABLE
AND expected_delivery_date is not None
AND expected_delivery_date < evaluation_date
AND purchase_applicability_ref is None
```

→

```text
NOT_DETERMINABLE
+ PAST_DELIVERY_DATE_APPLICABILITY_UNPROVEN
```

Cualquier otro `NOT_DETERMINABLE` → `NOT_DETERMINABLE` sin comparación.

`KNOWN` → continuar.

### Paso 4 — depletion STK

Con baseline/delivery KNOWN:

```text
CONFLICTING_DATA → CONFLICTING_DATA
UNKNOWN          → NOT_DETERMINABLE
NOT_EVIDENCED    → NOT_DETERMINABLE
KNOWN            → comparar
NOT_APPLICABLE   → horizonte
```

`NOT_EVIDENCED → NOT_DETERMINABLE` procede de reconciliación metodológica v0.3.1.

### Paso 5 — depletion KNOWN

```text
delivery > depletion
→ LATE_DELIVERY_DEMONSTRATED

delivery < depletion
→ NOT_LATE_DEMONSTRATED

delivery == depletion
→ NOT_LATE_DEMONSTRATED
+ SAME_DAY_ORDER_NOT_DEMONSTRATED
```

### Paso 6 — depletion NOT_APPLICABLE

Si horizonte no KNOWN o `horizon_end` ausente:

```text
→ NOT_DETERMINABLE
```

Con horizonte KNOWN:

```text
delivery <= horizon_end
→ NOT_LATE_WITHIN_EVIDENCED_HORIZON

delivery > horizon_end
→ NOT_DETERMINABLE
+ DELIVERY_BEYOND_STK_HORIZON
```

No se extrapola stock.

---

## 12. Regla de fecha publicada

El resultado puede conservar `expected_delivery_date` aunque el estado final sea `NOT_EVIDENCED` o `NOT_DETERMINABLE` si la entrada delivery la aportó.

Esa publicación es trazabilidad, no autorización de comparación.

La comparación temporal se ejecuta **exclusivamente** cuando:

```text
baseline.state = KNOWN
delivery.state = KNOWN
```

y el estado STK correspondiente permite comparar.

`depletion_date` se publica solo si STK la publica como valor.

---

## 13. Merge de referencias

El resultado deduplica preservando primer orden de aparición:

```text
evidence_refs:
    baseline.evidence_refs
    + delivery.evidence_refs

unresolved_refs:
    baseline.unresolved_refs

issue_refs:
    baseline.issue_refs
    + delivery.issue_refs
    + tuple(issue.issue_record_ref for issue in projection.issue_refs)

trace_refs:
    baseline.trace_refs
    + delivery.trace_refs
    + projection.trace_refs
```

No se deduplica mediante orden alfabético ni prioridad inventada.

---

## 14. Supplier

No existe adapter automático Supplier en v0.3.

Una capa anterior podrá construir `PurchaseSpecificDeliveryTimingEvidence` a partir de Supplier únicamente si demuestra semántica y aplicabilidad propuesta-específica.

```text
candidate_id ≠ evaluated_purchase_ref
DELIVERY_DATE ≠ aplicabilidad automática
```

---

## 15. Assessment / Rules

`eios/delivery` no importará `Assessment` para producir el resultado.

La futura traducción de estados ENT a `Assessment` constituye otra unidad contractual.

No se materializa aquí la tabla de correspondencia Rule outcome.

---

## 16. Convenciones físicas

Modelos Pydantic:

```text
extra="forbid"
str_strip_whitespace=True
frozen=True
```

Las tuplas de refs/códigos deben ser únicas.

No se permiten refs vacías.

---

## 17. Persistencia

No procede:

- SQL;
- tabla ENT;
- `DeliveryAnalysis_ID`;
- índices;
- repositorio persistente.

---

## 18. Tests obligatorios

### Contexto

1. mismatch decision → NOT_DETERMINABLE;
2. mismatch article → NOT_DETERMINABLE;
3. mismatch evaluation_date → NOT_DETERMINABLE;
4. mismatch evaluated_purchase_ref → NOT_DETERMINABLE;
5. baseline internamente incompatible con projection → validation error.

### Baseline

6. KNOWN sin relation ref → validation error;
7. KNOWN sin provenance → validation error;
8. KNOWN sin exclusion → validation error;
9. conflict sin issue/unresolved → validation error;
10. baseline CONFLICTING → result CONFLICTING;
11. baseline NOT_DETERMINABLE → result NOT_DETERMINABLE.

### Delivery

12. KNOWN completo;
13. KNOWN sin applicability → validation error;
14. NOT_EVIDENCED sin fecha;
15. NOT_EVIDENCED con fecha declarada → conserva fecha, no compara;
16. CONFLICTING con fecha única → validation error;
17. NOT_DETERMINABLE con fecha + refs;
18. fecha pasada sin aplicabilidad → limitation autorizada;
19. fecha pasada KNOWN con aplicabilidad → comparación normal;
20. valid_to < valid_from → validation error.

### STK

21. depletion UNKNOWN → NOT_DETERMINABLE;
22. depletion NOT_EVIDENCED → NOT_DETERMINABLE;
23. depletion CONFLICTING → CONFLICTING;
24. depletion NOT_APPLICABLE + horizon unknown → NOT_DETERMINABLE;
25. NOT_APPLICABLE + delivery dentro horizonte;
26. NOT_APPLICABLE + delivery fuera horizonte.

### Comparación

27. delivery > depletion;
28. delivery < depletion;
29. igualdad + SAME_DAY.

### Fronteras

30. no `scenario_id` usado como prueba de baseline;
31. no `lead_time` en modelos/engine;
32. no Assessment en result;
33. no Supplier adapter automático;
34. conversión STK issue → `issue_record_ref` exacta;
35. deduplicación estable de refs;
36. modelos frozen/extra forbid.

---

## 19. No regresión

La materialización no modificará:

```text
eios/core/*
eios/stock/*
eios/supplier/*
04_Reglas/*
02_Parametros/*
SQL
```

---

## 20. Estado

```text
DISEÑAR       ✅
AUDITAR       ✅
DEPURAR       ✅ v0.2
AUDITAR 2     ✅ findings
DEPURAR 2     ✅ v0.3
AUDIT 2 FINAL PENDIENTE
CERRAR        PENDIENTE
MATERIALIZAR  NO AUTORIZADO
```

**v0.3: APTO PARA AUDIT 2 FINAL.**
