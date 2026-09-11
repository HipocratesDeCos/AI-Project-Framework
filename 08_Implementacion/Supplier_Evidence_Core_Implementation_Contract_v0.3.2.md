# EIOS — SUPPLIER EVIDENCE CORE · IMPLEMENTATION CONTRACT v0.3.2

**Estado:** DEPURADO — PENDIENTE DE AUDIT 2 FINAL  
**Fecha:** 11/09/2026  
**Autoridad metodológica:** Supplier Evidence Core v0.3 🔒 CERRADO  
**Sustituye:** `Supplier_Evidence_Core_Implementation_Contract_v0.3.1.md`

---

## 1. Propósito y frontera

Materializar `Supplier Evidence Core` como núcleo factual, trazable, determinista y no decisional.

Puede validar identidad/coherencia, preservar gaps/contradicciones, resolver candidatura factual por mapeo fijo y comparar estructuralmente pares solicitados.

No calcula riesgo, fiabilidad, cumplimiento, concentración, ranking, preferencia, Rules, CRC ni decisión.

---

## 2. Paquete físico

```text
eios/supplier/__init__.py
eios/supplier/models.py
eios/supplier/engine.py
tests/test_supplier_evidence_core.py
```

No modifica paquetes cerrados existentes.

---

## 3. Versión metodológica

```text
SUPPLIER_EVIDENCE_METHODOLOGY_VERSION = "0.3"
```

---

## 4. Estados de dominio

```text
CandidateEvidenceState =
    CURRENT_OPERATION_DEMONSTRATED
    REFERENCE_ONLY
    GAP
    CONFLICTING_DATA

CandidateResolutionState =
    EVIDENCED_CANDIDATE
    NOT_EVIDENCED
    CONFLICTING_DATA

ObservationState =
    KNOWN
    NOT_EVIDENCED
    CONFLICTING_DATA

StructuralComparabilityState =
    STRUCTURALLY_COMPARABLE
    NOT_STRUCTURALLY_COMPARABLE
    UNKNOWN

ExternalMetricUsageState =
    AUTHORIZED_EXTERNAL_METRIC
    CONTEXT_ONLY_METRIC

IssueType =
    MISSING_DATA
    CONTRADICTION

SupplierItemType =
    CANDIDATE
    OBSERVATION
    METRIC
    COMPARISON
```

No sustituyen estados físicos de C0.

---

## 5. Convención de modelos

Modelos propios:

```python
ConfigDict(extra="forbid", str_strip_whitespace=True, frozen=True)
```

Decimales determinados deben ser finitos. IDs y referencias obligatorias no aceptan vacío.

Las validaciones contra coerción semántica de booleanos se ejecutarán **antes del parseo** mediante `field_validator(..., mode="before")` o mecanismo strict equivalente.

---

## 6. SupplierDataIssueRef

```text
issue_id
issue_type
issue_record_ref
evidence_refs: tuple[str, ...]
trace_refs: tuple[str, ...]
```

Invariantes:

- evidence_refs y trace_refs sin duplicados;
- CONTRADICTION requiere al menos dos evidence_refs distintas;
- nunca selecciona fuente prevalente.

---

## 7. SupplierItemRef

Referencia estructurada para agregados de estado:

```text
item_type: SupplierItemType
item_id: str
```

Evita colisiones entre namespaces de IDs.

Deduplicación se realiza sobre `(item_type, item_id)` en orden de primera aparición.

---

## 8. SupplierResultIdentity

```text
decision_id
scenario_id
rules_version
parameters_version
data_snapshot_id
company_scope
article_id
evaluation_date
methodology_version = "0.3"
```

Los campos de DecisionContext se derivan del objeto canónico.

---

## 9. SupplierCandidateEvidence

```text
candidate_id
supplier_id
object_id
state: CandidateEvidenceState
evidence_id: str | None
source_ref: str | None
captured_at: date | None
applicability_ref: str | None
valid_from: date | None
valid_to: date | None
issue_refs: tuple[SupplierDataIssueRef, ...]
trace_refs: tuple[str, ...]
```

Invariantes:

1. valid_to < valid_from inválido.
2. trace_refs únicos.
3. CURRENT_OPERATION_DEMONSTRATED requiere evidence_id, source_ref, captured_at y applicability_ref.
4. CURRENT_OPERATION_DEMONSTRATED no admite contradicción no resuelta.
5. REFERENCE_ONLY requiere evidence_id, source_ref y captured_at.
6. GAP no publica applicability_ref actual.
7. CONFLICTING_DATA requiere issue CONTRADICTION.
8. CONFLICTING_DATA no publica applicability_ref determinado.

Mapeo fijo:

```text
CURRENT_OPERATION_DEMONSTRATED → EVIDENCED_CANDIDATE
REFERENCE_ONLY                 → NOT_EVIDENCED
GAP                            → NOT_EVIDENCED
CONFLICTING_DATA               → CONFLICTING_DATA
```

---

## 10. CandidateResolution

```text
candidate_id
supplier_id
state: CandidateResolutionState
evidence_refs
issue_refs
trace_refs
limitations
```

---

## 11. SupplierDimension

```text
PRICE_REFERENCE
PAYMENT_TERM
COMMERCIAL_CONDITION
DELIVERY_DATE
LEAD_TIME
AVAILABILITY
QUALITY_REFERENCE
RELIABILITY_REFERENCE
OTHER_EVIDENCED_CONDITION
```

---

## 12. ObservationValueKind

```text
DECIMAL
TEXT
DATE
INTEGER
BOOLEAN
```

---

## 13. SupplierObservation

```text
observation_id
supplier_id
candidate_id: str | None
object_id
dimension: SupplierDimension
state: ObservationState
value_kind: ObservationValueKind
value_decimal: Decimal | None
value_text: str | None
value_date: date | None
value_integer: int | None
value_boolean: bool | None
unit: str | None
semantic_ref
source_ref: str | None
evidence_id: str | None
captured_at: date | None
valid_from: date | None
valid_to: date | None
issue_refs: tuple[SupplierDataIssueRef, ...]
trace_refs: tuple[str, ...]
```

Invariantes:

1. valid_to < valid_from inválido.
2. KNOWN requiere exactamente un campo value_* y debe corresponder a value_kind.
3. KNOWN requiere source_ref, evidence_id y captured_at.
4. estado no KNOWN no publica value_*.
5. CONFLICTING_DATA requiere issue CONTRADICTION.
6. semantic_ref obligatorio.
7. trace_refs únicos.
8. INTEGER no acepta bool.
9. BOOLEAN requiere bool real.
10. DATE/TEXT/BOOLEAN requieren unit=None.
11. Supplier no convierte unidades.

### Tipado estricto previo

Antes de que Pydantic pueda coaccionar valores:

- `value_integer=True/False` se rechaza;
- `value_decimal=True/False` se rechaza;
- `value_boolean` solo acepta bool real.

Se permite el parsing ordinario no booleano que Pydantic soporte para Decimal/fecha cuando no altera la semántica contractual.

---

## 14. SupplierHistoricalFact

```text
fact_id
supplier_id
event_type
event_date
captured_at
scope_ref
source_ref
evidence_id
trace_refs
```

No contiene severidad, probabilidad, score ni efecto.

---

## 15. SupplierSignal

```text
signal_id
supplier_id
signal_type
observed_at
captured_at
scope_ref
source_ref
evidence_id
trace_refs
```

No contiene criticidad, severidad, efecto ni recomendación.

---

## 16. ExternalSupplierMetric

```text
metric_id
supplier_id
metric_name
data_state: ObservationState
value: Decimal | None
unit
scope_ref
period_start: date | None
period_end: date | None
methodology_ref: str | None
source_ref: str | None
captured_at: date | None
usage_state: ExternalMetricUsageState
usage_authority_ref: str | None
issue_refs: tuple[SupplierDataIssueRef, ...]
trace_refs: tuple[str, ...]
```

Invariantes:

1. period_end < period_start inválido.
2. value finito cuando existe.
3. KNOWN requiere value, periodo completo, methodology_ref, source_ref y captured_at.
4. estado no KNOWN no publica value.
5. CONFLICTING_DATA requiere issue CONTRADICTION.
6. AUTHORIZED_EXTERNAL_METRIC requiere data_state=KNOWN y usage_authority_ref.
7. CONTEXT_ONLY_METRIC nunca se eleva automáticamente.
8. engine no recalcula la métrica.
9. `value=True/False` se rechaza en validación `mode="before"` antes de conversión a Decimal.

---

## 17. StructuralComparisonRequest

```text
comparison_id
current_observation_id
candidate_observation_id
comparison_authority_ref: str | None
```

Los pares se solicitan expresamente. El engine no genera cross-product.

`comparison_authority_ref` referencia una autoridad externa ya resuelta; Supplier no la crea ni la interpreta como regla.

---

## 18. StructuralComparisonResult

```text
comparison_id
current_observation_id
candidate_observation_id
dimension
state: StructuralComparabilityState
difference_decimal: Decimal | None
comparison_authority_ref: str | None
issue_refs
limitations
```

Nunca publica RULE_COMPARABLE.

---

## 19. SupplierEvidenceInput

```text
context: DecisionContext
purchase_operation: PurchaseOperation
company_scope
evaluation_date
methodology_version: Literal["0.3"]
candidates: tuple[SupplierCandidateEvidence, ...]
observations: tuple[SupplierObservation, ...]
historical_facts: tuple[SupplierHistoricalFact, ...]
external_metrics: tuple[ExternalSupplierMetric, ...]
signals: tuple[SupplierSignal, ...]
comparison_requests: tuple[StructuralComparisonRequest, ...]
```

---

## 20. Invariantes globales

### Identidad

1. context.decision_id == purchase_operation.decision_id.
2. context.scenario_id == purchase_operation.scenario_id.
3. methodology_version == "0.3".

### Unicidad

4. IDs únicos por colección: candidate, observation, fact, metric, signal, comparison.

### Candidatos

5. candidate.supplier_id != purchase_operation.supplier_id.
6. candidate.object_id == purchase_operation.article_id.
7. mismo supplier_id puede tener varios candidate_id distintos.
8. cualquier candidate.captured_at existente debe ser <= evaluation_date.
9. CURRENT_OPERATION_DEMONSTRATED debe cubrir evaluation_date cuando haya valid_from/valid_to.

### Observaciones

10. candidate_id=None → supplier_id == current supplier_id.
11. candidate_id presente → candidate debe existir y supplier_id coincidir.
12. object_id == current article_id.
13. cualquier captured_at existente debe ser <= evaluation_date.

### Proveedores admitidos

14. supplier_id de historical_facts, external_metrics y signals debe pertenecer a:

```text
{current_supplier_id} ∪ {candidate.supplier_id}
```

### Hechos / señales

15. event_date <= evaluation_date.
16. historical_fact.captured_at <= evaluation_date.
17. signal.observed_at <= evaluation_date.
18. signal.captured_at <= evaluation_date.

### Métricas

19. metric.captured_at <= evaluation_date cuando exista.
20. metric.period_end <= evaluation_date cuando exista.

### Requests

21. observation IDs deben existir.
22. current_observation pertenece al proveedor actual y candidate_id=None.
23. candidate_observation pertenece a candidate_id existente.
24. no se compara una observación consigo misma.

### Colecciones vacías

25. colección vacía significa solo “sin registros proporcionados”; no demuestra inexistencia empresarial.

---

## 21. Vigencia de observaciones

Puede conservarse una observación histórica.

Para comparación actual:

- valid_from > evaluation_date → no vigente;
- valid_to < evaluation_date → no vigente.

Resultado: NOT_STRUCTURALLY_COMPARABLE con limitación temporal. La observación no se elimina.

---

## 22. Reglas estrictas de tipos/unidades

La implementación debe impedir coerciones semánticas antes de parseo:

- bool no entra como INTEGER;
- bool no entra como DECIMAL;
- value_boolean exige bool real.

Después del parseo valida:

- exactamente un value_* en KNOWN;
- value_decimal Decimal finito;
- campos no correspondientes al value_kind son None;
- DATE/TEXT/BOOLEAN usan unit=None;
- DECIMAL/INTEGER se comparan solo con igualdad exacta de unit, incluyendo None==None;
- no se realizan conversiones.

---

## 23. Algoritmo determinista de comparación estructural

El engine procesa requests en orden de entrada.

### Paso 1 — candidatura actual

Si candidate_resolution != EVIDENCED_CANDIDATE:

```text
state = UNKNOWN
limitation = CANDIDATE_NOT_EVIDENCED_CURRENTLY
```

Si existe conflicto, issue_refs se preservan.

### Paso 2 — estado de observaciones

Alguna NOT_EVIDENCED:

```text
UNKNOWN
```

Alguna CONFLICTING_DATA:

```text
NOT_STRUCTURALLY_COMPARABLE
```

con issues preservados.

### Paso 3 — vigencia

Alguna observación no cubre evaluation_date:

```text
NOT_STRUCTURALLY_COMPARABLE
```

### Paso 4 — compatibilidad estructural básica

Se exige igualdad exacta de:

- dimension;
- value_kind;
- semantic_ref;
- object_id.

Para DECIMAL/INTEGER se exige igualdad exacta de unit. DATE/TEXT/BOOLEAN ya tienen unit=None.

Cualquier incompatibilidad:

```text
NOT_STRUCTURALLY_COMPARABLE
```

### Paso 5 — autoridad PRICE

Solo cuando ambas observaciones comparten `dimension = PRICE_REFERENCE` y han superado pasos anteriores:

sin comparison_authority_ref:

```text
UNKNOWN
PRICE_COMPARABILITY_AUTHORITY_REQUIRED
```

Con authority ref, Supplier conserva la referencia y continúa. No recalcula ni valida comparabilidad económica PRICE.

### Paso 6 — comparable estructural

Ambas KNOWN, vigentes y compatibles:

```text
STRUCTURALLY_COMPARABLE
```

### Paso 7 — diferencia descriptiva

Solo DECIMAL + STRUCTURALLY_COMPARABLE:

```text
difference_decimal = candidate.value_decimal - current.value_decimal
```

No asigna mejor/peor.

---

## 24. SupplierEvidenceResult

```text
identity: SupplierResultIdentity
current_supplier_id
candidate_resolutions
observations
historical_facts
external_metrics
signals
structural_comparisons
unresolved_items: tuple[SupplierItemRef, ...]
conflicting_items: tuple[SupplierItemRef, ...]
limitations
```

No contiene supplier_score, rank, preferred_supplier, risk_level, reliability_score, compliance_score, rule result, Assessment, effect, severity, CRC ni decisión.

### Agregación de item refs

Como mínimo:

- candidate NOT_EVIDENCED → unresolved `CANDIDATE/candidate_id`;
- candidate CONFLICTING_DATA → conflicting `CANDIDATE/candidate_id`;
- observation NOT_EVIDENCED → unresolved `OBSERVATION/observation_id`;
- observation CONFLICTING_DATA → conflicting `OBSERVATION/observation_id`;
- metric NOT_EVIDENCED → unresolved `METRIC/metric_id`;
- metric CONFLICTING_DATA → conflicting `METRIC/metric_id`;
- comparison UNKNOWN por evidencia insuficiente → unresolved `COMPARISON/comparison_id`;
- comparison afectada por contradicción explícita → conflicting `COMPARISON/comparison_id`.

Una incompatibilidad estructural ordinaria no se registra como contradicción de datos.

---

## 25. Orden reproducible

Conservar orden de entrada para:

- candidates → candidate_resolutions;
- observations;
- historical_facts;
- external_metrics;
- signals;
- comparison_requests → structural_comparisons.

Agregados de refs/issues/item refs/limitations se deduplican en orden de primera aparición.

No se ordena por score, valor, proveedor, severidad o prioridad implícita.

---

## 26. Engine público

```text
evaluate_supplier_evidence(payload: SupplierEvidenceInput) -> SupplierEvidenceResult
```

Responsabilidades:

1. construir identidad;
2. mapear candidatos;
3. validar referencias internas;
4. procesar únicamente requests explícitos;
5. preservar hechos/métricas/señales;
6. calcular diferencia decimal descriptiva cuando proceda;
7. agregar unresolved/conflicting con SupplierItemRef estable;
8. no mutar inputs.

---

## 27. Prohibiciones

No puede:

- seleccionar, ordenar o puntuar proveedores;
- calcular fiabilidad, cumplimiento, riesgo o concentración;
- inferir disponibilidad desde catálogo/histórico;
- autoautorizar métricas;
- generar comparaciones no solicitadas;
- decidir comparabilidad PRICE sin authority ref;
- producir RULE_COMPARABLE;
- activar R-PROV-001/002;
- generar Assessment;
- ejecutar CRC;
- recomendar/decidir;
- recalcular PRICE/TCO/STK/Finance;
- usar Q&T confidence como supplier reliability;
- convertir ausencia/GAP en FALSE/0.

---

## 28. Tests mínimos

1. demonstrated current candidate → EVIDENCED_CANDIDATE;
2. reference-only → NOT_EVIDENCED;
3. reference-only sin evidencia mínima rechazado;
4. GAP → NOT_EVIDENCED;
5. conflict sin issue rechazado;
6. contradiction con <2 evidence refs rechazada;
7. candidate expirado/no vigente rechazado;
8. candidate captured_at futuro rechazado;
9. current supplier como candidate rechazado;
10. object incompatible rechazado;
11. candidate_id duplicado rechazado;
12. mismo supplier con candidate_id distintos permitido;
13. observation KNOWN tipada;
14. KNOWN con múltiples values rechazado;
15. non-KNOWN con value rechazado;
16. candidate observation sin candidate_id rechazado;
17. observation captured_at futuro rechazado;
18. bool→integer rechazado antes de coerción;
19. bool→decimal rechazado antes de coerción;
20. value_boolean no bool rechazado;
21. DATE/TEXT/BOOLEAN con unit rechazado;
22. disponibilidad TEXT no se convierte;
23. historical fact futuro/captured futuro rechazado;
24. signal futuro/captured futuro rechazado;
25. proveedor ajeno en fact/metric/signal rechazado;
26. external metric KNOWN completa;
27. external metric bool→decimal rechazado;
28. authorized metric sin authority ref rechazado;
29. non-KNOWN metric con value rechazado;
30. metric conflict sin issue rechazado;
31. context-only no se eleva;
32. request explícito únicamente;
33. no cross-product;
34. candidate no evidenciado → UNKNOWN;
35. observation NOT_EVIDENCED → UNKNOWN;
36. observation conflict → NOT_STRUCTURALLY_COMPARABLE + issue;
37. fuera de vigencia → NOT_STRUCTURALLY_COMPARABLE;
38. dimensiones incompatibles → NOT_STRUCTURALLY_COMPARABLE sin exigir PRICE authority;
39. ambas PRICE sin authority ref → UNKNOWN;
40. ambas PRICE con authority ref no recalculan PRICE;
41. semantic/unit/value_kind incompatibles → NOT_STRUCTURALLY_COMPARABLE;
42. decimal compatible → diferencia exacta;
43. diferencia no genera mejor/peor;
44. context/purchase mismatch rechazado;
45. internal refs inválidas rechazadas;
46. item refs con namespace evitan colisiones;
47. unresolved/conflicting agregados estables;
48. no mutación;
49. resultado sin campos decisionales.

---

## 29. Criterio de cierre

Audit 2 final deberá confirmar:

- determinismo completo;
- representabilidad Pydantic/Python 3.11;
- compatibilidad C0;
- compatibilidad metodología v0.3;
- 0 duplicación de PRICE/Q&T/Rules/CRC;
- gaps/contradicciones explícitos;
- tipado semántico protegido contra coerción bool;
- referencias agregadas no ambiguas;
- 0 scoring/ranking;
- 0 política empresarial nueva;
- cierre suficiente para implementación física.
