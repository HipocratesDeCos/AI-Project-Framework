# EIOS — SUPPLIER EVIDENCE CORE · IMPLEMENTATION CONTRACT v0.2

**Estado:** DEPURADO — PENDIENTE DE AUDIT 2  
**Fecha:** 11/09/2026  
**Autoridad metodológica:** Supplier Evidence Core v0.3 🔒 CERRADO  
**Sustituye:** `Supplier_Evidence_Core_Implementation_Contract_v0.1.md`

---

## 1. Propósito

Materializar un núcleo factual de proveedor que:

- valide identidad, coherencia y trazabilidad;
- preserve gaps y contradicciones;
- resuelva candidatura factual mediante mapeo fijo;
- compare estructuralmente pares explícitos de observaciones;
- preserve métricas externas sin autoautorizar su uso;
- no calcule valoración, riesgo, ranking, reglas ni decisión.

---

## 2. Paquete físico autorizado

```text
eios/supplier/__init__.py
eios/supplier/models.py
eios/supplier/engine.py
tests/test_supplier_evidence_core.py
```

No se modifica ningún paquete cerrado existente.

---

## 3. Constante de metodología

```text
SUPPLIER_EVIDENCE_METHODOLOGY_VERSION = "0.3"
```

El contrato v0.2 solo representa esta metodología cerrada.

---

## 4. Tipos de estado

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

Ninguno sustituye estados físicos de C0.

---

## 5. FrozenModel

Todos los modelos propios del dominio usarán:

```python
ConfigDict(extra="forbid", str_strip_whitespace=True, frozen=True)
```

---

## 6. SupplierDataIssueRef

```text
issue_id: str
issue_type: IssueType
issue_record_ref: str
evidence_refs: tuple[str, ...]
trace_refs: tuple[str, ...]
```

Invariantes:

1. IDs/referencias no vacíos.
2. `evidence_refs` sin duplicados.
3. `trace_refs` sin duplicados.
4. `CONTRADICTION` requiere al menos dos `evidence_refs` distintas.
5. El issue describe la incidencia; no decide qué fuente prevalece.

---

## 7. SupplierScope

```text
company_scope: str
```

Es identidad de alcance y no amplía C0.

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

Los campos de DecisionContext se derivan del objeto canónico recibido.

---

## 9. SupplierCandidateEvidence

Campos:

```text
candidate_id: str
supplier_id: str
object_id: str
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

Invariantes locales:

1. `valid_to < valid_from` inválido.
2. `trace_refs` únicos.
3. `CURRENT_OPERATION_DEMONSTRATED` requiere:
   - `evidence_id`;
   - `source_ref`;
   - `captured_at`;
   - `applicability_ref`.
4. `CURRENT_OPERATION_DEMONSTRATED` no puede contener un issue `CONTRADICTION` no resuelto.
5. `REFERENCE_ONLY` requiere:
   - `evidence_id`;
   - `source_ref`;
   - `captured_at`.
6. `REFERENCE_ONLY` no requiere `applicability_ref` actual.
7. `GAP` no puede publicar `applicability_ref` como demostración actual.
8. `CONFLICTING_DATA` requiere al menos un `SupplierDataIssueRef` de tipo `CONTRADICTION`.
9. `CONFLICTING_DATA` no publica `applicability_ref` determinado.

Invariantes de sobre se aplican en SupplierEvidenceInput.

---

## 10. Mapeo de candidatura

El engine aplica exclusivamente:

```text
CURRENT_OPERATION_DEMONSTRATED → EVIDENCED_CANDIDATE
REFERENCE_ONLY                 → NOT_EVIDENCED
GAP                            → NOT_EVIDENCED
CONFLICTING_DATA               → CONFLICTING_DATA
```

No existe score ni probabilidad.

---

## 11. CandidateResolution

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

## 12. SupplierDimension

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

Las etiquetas identifican semántica de observación; no asignan efecto empresarial.

---

## 13. ObservationValueKind

```text
DECIMAL
TEXT
DATE
INTEGER
BOOLEAN
```

---

## 14. SupplierObservation

Campos:

```text
observation_id: str
supplier_id: str
candidate_id: str | None
object_id: str
dimension: SupplierDimension
state: ObservationState
value_kind: ObservationValueKind
value_decimal: Decimal | None
value_text: str | None
value_date: date | None
value_integer: int | None
value_boolean: bool | None
unit: str | None
semantic_ref: str
source_ref: str | None
evidence_id: str | None
captured_at: date | None
valid_from: date | None
valid_to: date | None
issue_refs: tuple[SupplierDataIssueRef, ...]
trace_refs: tuple[str, ...]
```

Invariantes locales:

1. `valid_to < valid_from` inválido.
2. Decimal debe ser finito.
3. `KNOWN` requiere exactamente un campo de valor no nulo y debe corresponder a `value_kind`.
4. `KNOWN` requiere `source_ref`, `evidence_id` y `captured_at`.
5. Estado no `KNOWN` no publica ningún valor determinado.
6. `CONFLICTING_DATA` requiere issue `CONTRADICTION`.
7. `NOT_EVIDENCED` puede llevar issue `MISSING_DATA`, pero no es obligatorio si la propia ausencia está identificada por el registro.
8. `semantic_ref` es obligatorio y no equivale a regla de negocio.
9. `trace_refs` únicos.

Propiedad y temporalidad se validan en el sobre.

---

## 15. SupplierHistoricalFact

```text
fact_id
supplier_id
event_type
event_date
scope_ref
source_ref
evidence_id
trace_refs
```

Es un hecho demostrado ya materializado en la entrada.

No contiene severidad, score, probabilidad o efecto.

---

## 16. SupplierSignal

```text
signal_id
supplier_id
signal_type
observed_at
scope_ref
source_ref
evidence_id
trace_refs
```

No contiene criticidad, severidad, efecto ni recomendación.

---

## 17. ExternalSupplierMetric

Campos:

```text
metric_id
supplier_id
metric_name
data_state: ObservationState
value: Decimal | None
unit: str
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

1. `period_end < period_start` inválido cuando ambas existen.
2. Si existe `value`, debe ser Decimal finito.
3. `KNOWN` requiere:
   - `value`;
   - `period_start`;
   - `period_end`;
   - `methodology_ref`;
   - `source_ref`;
   - `captured_at`.
4. Estado no `KNOWN` no publica `value` determinado.
5. `CONFLICTING_DATA` requiere issue `CONTRADICTION`.
6. `AUTHORIZED_EXTERNAL_METRIC` requiere `data_state = KNOWN`.
7. `AUTHORIZED_EXTERNAL_METRIC` requiere `usage_authority_ref`.
8. `CONTEXT_ONLY_METRIC` no se eleva automáticamente aunque exista `usage_authority_ref`.
9. El engine no recalcula la métrica.
10. Autoridad de uso y estado del dato son dimensiones independientes.

---

## 18. StructuralComparisonRequest

```text
comparison_id
current_observation_id
candidate_observation_id
```

Los pares son explícitos.

El engine no genera cross-product ni descubre candidatos “mejores”.

---

## 19. StructuralComparisonResult

```text
comparison_id
current_observation_id
candidate_observation_id
dimension
state: StructuralComparabilityState
difference_decimal: Decimal | None
issue_refs
limitations
```

Nunca publica `RULE_COMPARABLE`.

---

## 20. SupplierEvidenceInput

```text
context: DecisionContext
purchase_operation: PurchaseOperation
company_scope: str
evaluation_date: date
methodology_version: Literal["0.3"]
candidates: tuple[SupplierCandidateEvidence, ...]
observations: tuple[SupplierObservation, ...]
historical_facts: tuple[SupplierHistoricalFact, ...]
external_metrics: tuple[ExternalSupplierMetric, ...]
signals: tuple[SupplierSignal, ...]
comparison_requests: tuple[StructuralComparisonRequest, ...]
```

---

## 21. Invariantes globales del sobre

### Identidad

1. `context.decision_id == purchase_operation.decision_id`.
2. `context.scenario_id == purchase_operation.scenario_id`.
3. `methodology_version == "0.3"`.

### Unicidad

4. Cada colección mantiene IDs únicos en su namespace:
   - candidate_id;
   - observation_id;
   - fact_id;
   - metric_id;
   - signal_id;
   - comparison_id;
   - issue_id dentro del conjunto de issues materializados en cada registro.

### Candidatos

5. `candidate.supplier_id != purchase_operation.supplier_id`.
6. `candidate.object_id == purchase_operation.article_id`.
7. Múltiples candidatos pueden compartir `supplier_id` si sus `candidate_id` son distintos.
8. Para `CURRENT_OPERATION_DEMONSTRATED`:
   - `captured_at <= evaluation_date`;
   - si `valid_from` existe, `valid_from <= evaluation_date`;
   - si `valid_to` existe, `evaluation_date <= valid_to`.
9. Para `REFERENCE_ONLY`, `captured_at <= evaluation_date`.

### Observaciones

10. Si `candidate_id is None`, `supplier_id == purchase_operation.supplier_id`.
11. Si `candidate_id is not None`:
    - candidate_id debe existir;
    - observation.supplier_id debe coincidir con candidate.supplier_id.
12. `observation.object_id == purchase_operation.article_id`.
13. Si `captured_at` existe, `captured_at <= evaluation_date`.

### Hechos / señales

14. `historical_fact.event_date <= evaluation_date`.
15. `signal.observed_at <= evaluation_date`.

### Métricas

16. Si `captured_at` existe, `captured_at <= evaluation_date`.
17. `period_end <= evaluation_date` para una métrica utilizada en el snapshot actual.

### Requests de comparación

18. Todas las referencias de observación deben existir.
19. `current_observation_id` debe apuntar a:
    - `candidate_id = None`;
    - `supplier_id = purchase_operation.supplier_id`.
20. `candidate_observation_id` debe apuntar a una observación con `candidate_id` existente.
21. Un request no puede comparar una observación consigo misma.

### Semántica de colección vacía

22. Una colección vacía significa únicamente “no se proporcionaron registros a este contrato”; no demuestra inexistencia empresarial.

---

## 22. Vigencia de observaciones en comparación actual

Una observación puede conservarse aunque su vigencia explícita no cubra `evaluation_date`.

Sin embargo, para comparación estructural de la operación actual:

- si `valid_from > evaluation_date`, no es utilizable actualmente;
- si `valid_to < evaluation_date`, no es utilizable actualmente.

El resultado de comparación será `NOT_STRUCTURALLY_COMPARABLE` con limitación temporal explícita.

No se modifica ni elimina la observación histórica.

---

## 23. Algoritmo determinista de comparabilidad estructural

Para cada request explícito:

### Paso 1 — Candidatura actual

Si la observación candidata pertenece a un candidato cuya resolución no es `EVIDENCED_CANDIDATE`:

```text
state = UNKNOWN
limitation = CANDIDATE_NOT_EVIDENCED_CURRENTLY
```

Si el candidato está `CONFLICTING_DATA`, además se preservan sus issue refs.

### Paso 2 — Estado de observaciones

Si cualquiera está `NOT_EVIDENCED`:

```text
UNKNOWN
```

Si cualquiera está `CONFLICTING_DATA`:

```text
NOT_STRUCTURALLY_COMPARABLE
```

con issues/limitaciones de contradicción preservados.

### Paso 3 — Vigencia

Si una observación no cubre `evaluation_date` mediante su vigencia explícita:

```text
NOT_STRUCTURALLY_COMPARABLE
```

### Paso 4 — Compatibilidad estructural

Se exige igualdad/compatibilidad de:

- `dimension`;
- `value_kind`;
- `semantic_ref`;
- `object_id`;
- `unit` cuando aplique.

Cualquier incompatibilidad produce:

```text
NOT_STRUCTURALLY_COMPARABLE
```

### Paso 5 — Resultado compatible

Si ambas observaciones son `KNOWN`, vigentes y compatibles:

```text
STRUCTURALLY_COMPARABLE
```

### Paso 6 — Diferencia descriptiva

Solo si ambas son `DECIMAL` y estructuralmente comparables:

```text
difference_decimal = candidate.value_decimal - current.value_decimal
```

No se asigna signo favorable/desfavorable.

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

`unresolved_items` identifica elementos no evidenciados para el uso solicitado.

`conflicting_items` identifica elementos con contradicción preservada.

No son scores.

---

## 25. Engine público

```text
evaluate_supplier_evidence(payload: SupplierEvidenceInput) -> SupplierEvidenceResult
```

El engine:

1. construye identidad;
2. resuelve candidatos por mapeo fijo;
3. ejecuta comparaciones solicitadas;
4. calcula diferencia decimal puramente descriptiva cuando proceda;
5. conserva hechos, métricas y señales;
6. agrega referencias unresolved/conflicting sin resolverlas;
7. no muta inputs.

---

## 26. Prohibiciones

No puede:

- seleccionar, ordenar o puntuar proveedores;
- crear supplier/reliability/compliance/risk/concentration score;
- inferir disponibilidad desde catálogo/histórico;
- autoautorizar métricas externas;
- generar comparaciones no solicitadas;
- producir `RULE_COMPARABLE`;
- activar R-PROV-001/002;
- generar Assessment;
- ejecutar CRC;
- emitir recomendación o decisión;
- recalcular PRICE/TCO/STK/Finance;
- usar Q&T confidence como supplier reliability;
- transformar ausencia/GAP en FALSE o cero.

---

## 27. Tests contractuales mínimos

1. current candidate demostrado → EVIDENCED_CANDIDATE;
2. reference-only → NOT_EVIDENCED;
3. reference-only sin evidencia mínima rechazado;
4. GAP → NOT_EVIDENCED;
5. conflict sin issue rechazado;
6. contradiction con menos de dos evidence refs rechazada;
7. candidate current expirado/no vigente rechazado;
8. candidate captured_at futuro rechazado;
9. candidate igual a current supplier rechazado;
10. candidate object incompatible rechazado;
11. candidate_id duplicado rechazado;
12. mismo supplier con dos candidate_id permitido;
13. observation KNOWN tipada correctamente;
14. observation KNOWN con múltiples values rechazada;
15. observation no KNOWN con value rechazada;
16. observation candidate sin candidate_id rechazada por propiedad;
17. observation captured_at futuro rechazada;
18. disponibilidad TEXT no convertida a cantidad;
19. historical fact futuro rechazado;
20. signal futuro rechazado;
21. external metric KNOWN completa;
22. external metric authorized sin authority ref rechazada;
23. external metric non-KNOWN con value rechazada;
24. external metric conflict sin issue rechazada;
25. context-only no se eleva;
26. request explícito solamente;
27. no cross-product;
28. candidate no evidenciado → comparison UNKNOWN;
29. observation NOT_EVIDENCED → UNKNOWN;
30. observation conflict → NOT_STRUCTURALLY_COMPARABLE + issue;
31. observación fuera de vigencia → NOT_STRUCTURALLY_COMPARABLE;
32. semántica/unidad/dimensión incompatible → NOT_STRUCTURALLY_COMPARABLE;
33. decimal compatible → diferencia exacta;
34. diferencia sin mejor/peor;
35. context/purchase identity mismatch rechazado;
36. refs internas inválidas rechazadas;
37. no mutación;
38. resultado sin campos decisionales.

---

## 28. Criterio de cierre

Audit 2 deberá confirmar que este contrato es:

- determinista;
- representable en Pydantic/Python 3.11;
- compatible con C0;
- compatible con metodología v0.3;
- libre de scoring/ranking;
- libre de política empresarial nueva;
- suficientemente cerrado para implementación y tests.
