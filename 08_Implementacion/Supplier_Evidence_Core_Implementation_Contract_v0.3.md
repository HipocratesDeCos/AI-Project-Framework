# EIOS — SUPPLIER EVIDENCE CORE · IMPLEMENTATION CONTRACT v0.3

**Estado:** DEPURADO — PENDIENTE DE AUDIT 2 FINAL  
**Fecha:** 11/09/2026  
**Autoridad metodológica:** Supplier Evidence Core v0.3 🔒 CERRADO  
**Sustituye:** `Supplier_Evidence_Core_Implementation_Contract_v0.2.md`

---

## 1. Propósito

Definir el contrato físico final candidato para `Supplier Evidence Core` como núcleo factual, trazable, determinista y no decisional.

No calcula riesgo, fiabilidad, cumplimiento, concentración, ranking ni preferencia.

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

## 4. Estados

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
```

Son estados de dominio y no sustituyen C0.

---

## 5. Convención de modelos

Modelos propios:

```python
ConfigDict(extra="forbid", str_strip_whitespace=True, frozen=True)
```

Decimales determinados deben ser finitos.

IDs/referencias obligatorias no aceptan cadena vacía.

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

- evidence_refs únicas;
- trace_refs únicas;
- `CONTRADICTION` requiere al menos dos evidence_refs distintas;
- no resuelve cuál prevalece.

---

## 7. SupplierResultIdentity

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

## 8. SupplierCandidateEvidence

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

1. `valid_to < valid_from` inválido.
2. trace_refs únicos.
3. `CURRENT_OPERATION_DEMONSTRATED` requiere evidence_id, source_ref, captured_at y applicability_ref.
4. `CURRENT_OPERATION_DEMONSTRATED` no admite contradicción no resuelta.
5. `REFERENCE_ONLY` requiere evidence_id, source_ref y captured_at.
6. `GAP` no publica applicability_ref actual.
7. `CONFLICTING_DATA` requiere issue CONTRADICTION.
8. `CONFLICTING_DATA` no publica applicability_ref determinado.

---

## 9. Mapeo de candidatura

```text
CURRENT_OPERATION_DEMONSTRATED → EVIDENCED_CANDIDATE
REFERENCE_ONLY                 → NOT_EVIDENCED
GAP                            → NOT_EVIDENCED
CONFLICTING_DATA               → CONFLICTING_DATA
```

No existe scoring/probabilidad.

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

1. `valid_to < valid_from` inválido.
2. `KNOWN` requiere exactamente un campo de valor y debe corresponder a value_kind.
3. `KNOWN` requiere source_ref, evidence_id, captured_at.
4. estado no KNOWN no publica valor.
5. CONFLICTING_DATA requiere issue CONTRADICTION.
6. semantic_ref obligatorio.
7. trace_refs únicos.
8. INTEGER no acepta bool.
9. BOOLEAN requiere bool real.
10. DATE/TEXT/BOOLEAN requieren `unit = None`.
11. Supplier no convierte unidades.

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
6. AUTHORIZED_EXTERNAL_METRIC requiere data_state = KNOWN.
7. AUTHORIZED_EXTERNAL_METRIC requiere usage_authority_ref.
8. CONTEXT_ONLY_METRIC nunca se eleva automáticamente.
9. engine no recalcula la métrica.

---

## 17. StructuralComparisonRequest

```text
comparison_id
current_observation_id
candidate_observation_id
comparison_authority_ref: str | None
```

Los pares se solicitan explícitamente.

`comparison_authority_ref` no crea autoridad; referencia una autoridad externa ya resuelta cuando una dimensión la exige.

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

Nunca publica `RULE_COMPARABLE`.

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

5. candidate.supplier_id != current supplier_id.
6. candidate.object_id == purchase_operation.article_id.
7. mismo supplier_id puede tener varios candidate_id distintos.
8. cualquier captured_at de candidate debe ser <= evaluation_date.
9. CURRENT_OPERATION_DEMONSTRATED debe cubrir evaluation_date cuando exista valid_from/valid_to.

### Observaciones

10. candidate_id None → supplier_id == current supplier_id.
11. candidate_id presente → debe existir y supplier_id coincidir.
12. object_id == current article_id.
13. cualquier captured_at debe ser <= evaluation_date.

### Proveedores admitidos en hechos/métricas/señales

14. supplier_id debe pertenecer a:

```text
{current_supplier_id} ∪ {candidate.supplier_id}
```

### Hechos y señales

15. event_date <= evaluation_date.
16. historical_fact.captured_at <= evaluation_date.
17. signal.observed_at <= evaluation_date.
18. signal.captured_at <= evaluation_date.

### Métricas

19. metric.captured_at <= evaluation_date cuando exista.
20. metric.period_end <= evaluation_date cuando exista.

### Requests

21. IDs de observación deben existir.
22. current_observation debe pertenecer al proveedor actual y candidate_id=None.
23. candidate_observation debe pertenecer a candidate_id existente.
24. no se compara una observación consigo misma.

### Colecciones vacías

25. colección vacía = no registros proporcionados; no demuestra inexistencia empresarial.

---

## 21. Vigencia de observaciones

Observaciones históricas pueden conservarse.

Para comparación actual:

- valid_from > evaluation_date → no vigente;
- valid_to < evaluation_date → no vigente.

Una observación no vigente produce `NOT_STRUCTURALLY_COMPARABLE` con limitación temporal; no se elimina.

---

## 22. Regla estructural de comparación

El engine procesa requests en el orden recibido.

### Paso 1 — candidatura actual

Si candidate_resolution != EVIDENCED_CANDIDATE:

```text
UNKNOWN
CANDIDATE_NOT_EVIDENCED_CURRENTLY
```

Issues se preservan.

### Paso 2 — observaciones

Si alguna está NOT_EVIDENCED:

```text
UNKNOWN
```

Si alguna está CONFLICTING_DATA:

```text
NOT_STRUCTURALLY_COMPARABLE
```

con issues preservados.

### Paso 3 — vigencia

Si alguna no cubre evaluation_date:

```text
NOT_STRUCTURALLY_COMPARABLE
```

### Paso 4 — autoridad especializada PRICE

Si la dimensión de cualquiera de las observaciones es `PRICE_REFERENCE` y no existe `comparison_authority_ref`:

```text
UNKNOWN
PRICE_COMPARABILITY_AUTHORITY_REQUIRED
```

Supplier Evidence Core no determina si la referencia PRICE es correcta; solo conserva la referencia suministrada.

### Paso 5 — compatibilidad estructural

Se exige igualdad exacta de:

- dimension;
- value_kind;
- semantic_ref;
- object_id.

Para DECIMAL/INTEGER se exige además igualdad exacta de `unit`, incluyendo `None == None`.

DATE/TEXT/BOOLEAN ya deben tener unit=None.

No se realizan conversiones.

Incompatibilidad → `NOT_STRUCTURALLY_COMPARABLE`.

### Paso 6 — compatible

Ambas KNOWN, vigentes y estructuralmente compatibles → `STRUCTURALLY_COMPARABLE`.

### Paso 7 — diferencia descriptiva

Solo DECIMAL + STRUCTURALLY_COMPARABLE:

```text
difference_decimal = candidate - current
```

No asigna mejor/peor.

---

## 23. Reglas estrictas de tipos

La implementación deberá validar después del parseo que:

- value_integer sea `int` real y no `bool`;
- value_boolean sea `bool` real;
- exactamente un value_* esté presente en KNOWN;
- value_decimal sea Decimal finito;
- campos de valor no correspondientes a value_kind sean None.

No se autoriza coerción semántica entre tipos.

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
unresolved_items
conflicting_items
limitations
```

No contiene scoring, ranking, preferred supplier, rule result, Assessment, effect, severity, CRC o decisión.

---

## 25. Orden reproducible

El resultado conserva orden de entrada para:

- candidates → candidate_resolutions;
- observations;
- historical_facts;
- external_metrics;
- signals;
- comparison_requests → structural_comparisons.

Agregados:

```text
evidence_refs
trace_refs
issue_refs
unresolved_items
conflicting_items
limitations
```

se deduplican conservando **orden de primera aparición**.

No se ordena por score, valor, proveedor, severidad ni prioridad implícita.

---

## 26. Engine público

```text
evaluate_supplier_evidence(payload: SupplierEvidenceInput) -> SupplierEvidenceResult
```

Responsabilidades:

1. construir identidad;
2. mapear candidatos;
3. validar referencias internas;
4. procesar requests explícitos;
5. preservar hechos/métricas/señales;
6. producir diferencias decimales descriptivas cuando proceda;
7. agregar unresolved/conflicting de forma estable;
8. no mutar inputs.

---

## 27. Prohibiciones

El engine no puede:

- seleccionar/ordenar/puntuar proveedores;
- calcular fiabilidad/cumplimiento/riesgo/concentración;
- inferir disponibilidad desde catálogo/histórico;
- autoautorizar métricas;
- generar cross-product;
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

1. current candidate demostrado → EVIDENCED_CANDIDATE;
2. reference-only → NOT_EVIDENCED;
3. reference-only sin evidencia mínima rechazado;
4. GAP → NOT_EVIDENCED;
5. conflict sin issue rechazado;
6. contradiction con <2 evidence refs rechazada;
7. current candidate expirado/no vigente rechazado;
8. candidate captured_at futuro rechazado;
9. current supplier como candidate rechazado;
10. object incompatible rechazado;
11. candidate_id duplicado rechazado;
12. mismo supplier con dos candidate_id permitido;
13. observation KNOWN tipada;
14. KNOWN múltiples values rechazado;
15. non-KNOWN con value rechazado;
16. candidate observation sin candidate_id rechazado;
17. observation captured_at futuro rechazado;
18. boolean/int estrictos;
19. DATE/TEXT/BOOLEAN con unit rechazado;
20. disponibilidad TEXT no se convierte;
21. historical fact captured después de evaluation rechazado;
22. signal captured después de evaluation rechazado;
23. unrelated supplier historical/metric/signal rechazado;
24. external metric KNOWN completa;
25. authorized metric sin authority ref rechazado;
26. non-KNOWN metric con value rechazado;
27. metric conflict sin issue rechazado;
28. context-only no se eleva;
29. comparison request explícito solamente;
30. no cross-product;
31. candidate no evidenciado → UNKNOWN;
32. observation NOT_EVIDENCED → UNKNOWN;
33. observation conflict → NOT_STRUCTURALLY_COMPARABLE + issue;
34. fuera de vigencia → NOT_STRUCTURALLY_COMPARABLE;
35. price sin comparison_authority_ref → UNKNOWN;
36. price con authority ref no recalcula PRICE;
37. semantic/unit/dimension incompatible → NOT_STRUCTURALLY_COMPARABLE;
38. decimal comparable → diferencia exacta;
39. diferencia no genera mejor/peor;
40. context/purchase mismatch rechazado;
41. internal refs inválidas rechazadas;
42. orden estable de salidas/agregados;
43. no mutación;
44. resultado sin campos decisionales.

---

## 29. Criterio de cierre

Audit 2 final deberá confirmar:

- 0 contradicciones metodológicas;
- 0 duplicación de autoridad PRICE/Q&T/C0/Rules;
- representabilidad Pydantic/Python 3.11;
- estados/gaps/contradicciones explícitos;
- no scoring/ranking;
- no política empresarial nueva;
- contrato suficientemente cerrado para implementación física.
