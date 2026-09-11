# EIOS — SUPPLIER EVIDENCE CORE · IMPLEMENTATION CONTRACT v0.1

**Estado:** DISEÑO TÉCNICO — PENDIENTE DE AUDIT 1  
**Fecha:** 11/09/2026  
**Autoridad metodológica:** Supplier Evidence Core v0.3 🔒 CERRADO

---

## 1. Propósito

Definir el contrato físico mínimo para materializar `Supplier Evidence Core` como dominio factual, trazable y no decisional.

La implementación tendrá tres responsabilidades:

1. validar coherencia estructural de hechos de proveedor;
2. resolver estados factuales mediante mapeos deterministas ya autorizados;
3. producir comparabilidad **estructural** únicamente para pares explícitamente solicitados.

No calcula riesgo, fiabilidad, cumplimiento, concentración ni preferencia de proveedor.

---

## 2. Paquete físico

```text
eios/supplier/__init__.py
eios/supplier/models.py
eios/supplier/engine.py
tests/test_supplier_evidence_core.py
```

No se modifica:

- `eios/core`;
- `eios/quality`;
- `eios/pricing`;
- `eios/tco`;
- `eios/stock`;
- `eios/finance`;
- `eios/rules`;
- SQL;
- frontend.

---

## 3. Tipos de estado

### 3.1 CandidateEvidenceState

```text
CURRENT_OPERATION_DEMONSTRATED
REFERENCE_ONLY
GAP
CONFLICTING_DATA
```

Describe la aplicabilidad factual declarada de la evidencia de candidatura.

No sustituye `Evidence.state` de C0.

### 3.2 CandidateResolutionState

```text
EVIDENCED_CANDIDATE
NOT_EVIDENCED
CONFLICTING_DATA
```

Mapeo fijo:

```text
CURRENT_OPERATION_DEMONSTRATED → EVIDENCED_CANDIDATE
REFERENCE_ONLY                 → NOT_EVIDENCED
GAP                            → NOT_EVIDENCED
CONFLICTING_DATA               → CONFLICTING_DATA
```

### 3.3 ObservationState

```text
KNOWN
NOT_EVIDENCED
CONFLICTING_DATA
```

### 3.4 StructuralComparabilityState

```text
STRUCTURALLY_COMPARABLE
NOT_STRUCTURALLY_COMPARABLE
UNKNOWN
```

Nunca se expone `RULE_COMPARABLE`.

### 3.5 ExternalMetricUsageState

```text
AUTHORIZED_EXTERNAL_METRIC
CONTEXT_ONLY_METRIC
```

El engine no eleva una métrica de un estado a otro.

---

## 4. FrozenModel

Los modelos propios del dominio utilizarán conceptualmente:

```python
ConfigDict(extra="forbid", str_strip_whitespace=True, frozen=True)
```

No se admiten campos extra silenciosos.

---

## 5. SupplierScope

```text
company_scope: str
```

`company_scope` es obligatorio y no modifica C0.

---

## 6. SupplierResultIdentity

El resultado conservará:

```text
decision_id
scenario_id
rules_version
parameters_version
data_snapshot_id
company_scope
article_id
evaluation_date
methodology_version
```

Los cinco primeros se derivan de `DecisionContext`; no se reciben como duplicado independiente.

`article_id` se deriva de `PurchaseOperation`.

---

## 7. SupplierCandidateEvidence

Campos físicos mínimos:

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
trace_refs: tuple[str, ...]
```

### Invariantes

1. `candidate_id` identifica una propuesta/candidatura concreta y debe ser único dentro del input.
2. `supplier_id` puede repetirse en candidatos distintos solo si `candidate_id` es distinto.
3. `supplier_id` no puede ser el proveedor actual de `PurchaseOperation`.
4. `object_id` debe coincidir con `PurchaseOperation.article_id` para poder participar como candidatura de esa operación.
5. `valid_to < valid_from` es inválido.
6. `CURRENT_OPERATION_DEMONSTRATED` requiere:
   - `evidence_id`;
   - `source_ref`;
   - `captured_at`;
   - `applicability_ref`.
7. Si `valid_from` existe y es posterior a `evaluation_date`, `CURRENT_OPERATION_DEMONSTRATED` es inválido.
8. Si `valid_to` existe y es anterior a `evaluation_date`, `CURRENT_OPERATION_DEMONSTRATED` es inválidoido.
9. `CONFLICTING_DATA` requiere al menos dos referencias distintas entre `evidence_id`/`trace_refs` o una referencia de contradicción explícita que el contrato deberá representar.
10. `REFERENCE_ONLY` puede conservar evidencia histórica sin resolver candidatura actual.
11. `GAP` no puede publicar `applicability_ref` como si la candidatura estuviera demostrada.

---

## 8. CandidateResolution

```text
candidate_id
supplier_id
state: CandidateResolutionState
evidence_refs
trace_refs
limitations
```

El engine aplica exclusivamente el mapeo fijo de §3.2.

No calcula probabilidad ni score.

---

## 9. SupplierObservation

Representa una condición/hecho dimensional de proveedor.

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
trace_refs: tuple[str, ...]
```

### SupplierDimension

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

### ObservationValueKind

```text
DECIMAL
TEXT
DATE
INTEGER
BOOLEAN
```

### Invariantes

1. `KNOWN` requiere exactamente un campo de valor correspondiente a `value_kind`.
2. Un estado no `KNOWN` no publica valor determinado.
3. `KNOWN` requiere `source_ref`, `evidence_id` y `captured_at`.
4. Decimal debe ser finito.
5. `valid_to < valid_from` es inválido.
6. `candidate_id = None` solo puede utilizarse para hechos del proveedor actual o hechos no vinculados a una candidatura concreta según contrato.
7. Cuando `candidate_id` existe debe referir a un candidato presente en el mismo input y su `supplier_id` debe coincidir.
8. `object_id` debe coincidir con el artículo de la operación para participar en comparaciones de la operación actual.
9. `semantic_ref` es obligatorio y define la semántica/unidad conceptual del valor sin crear regla de negocio.
10. `RELIABILITY_REFERENCE` no implica que el valor sea una métrica autorizada; las métricas agregadas se representan mediante `ExternalSupplierMetric`.

---

## 10. SupplierHistoricalFact

Campos:

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

No contiene:

- severity;
- probability;
- risk_score;
- reliability_score;
- effect.

El engine conserva estos hechos; no los agrega.

---

## 11. SupplierSignal

Campos:

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

`signal_type` describe el hecho fuente.

No contiene criticidad, severidad, efecto o recomendación.

---

## 12. ExternalSupplierMetric

Campos:

```text
metric_id
supplier_id
metric_name
value: Decimal
unit
scope_ref
period_start
period_end
methodology_ref
source_ref
captured_at
usage_state: ExternalMetricUsageState
usage_authority_ref: str | None
trace_refs
```

### Invariantes

1. `value` debe ser finito.
2. `period_end < period_start` es inválido.
3. `AUTHORIZED_EXTERNAL_METRIC` requiere `usage_authority_ref` no vacío.
4. `CONTEXT_ONLY_METRIC` puede conservar `usage_authority_ref`, pero el engine no lo eleva automáticamente a autorizado.
5. El engine no recalcula la métrica.
6. El engine no compara métricas con distinto `metric_name`, `unit`, `scope_ref`, periodo o metodología como si fueran equivalentes.

---

## 13. StructuralComparisonRequest

La comparación estructural solo se ejecuta cuando el consumidor solicita expresamente un par:

```text
comparison_id
current_observation_id
candidate_observation_id
```

No se generan pares por cross-product.

No se buscan “mejores” candidatos.

---

## 14. StructuralComparisonResult

Campos:

```text
comparison_id
current_observation_id
candidate_observation_id
dimension
state: StructuralComparabilityState
difference_decimal: Decimal | None
limitations
```

`difference_decimal` solo puede publicarse cuando:

- ambos estados son `KNOWN`;
- ambos `value_kind = DECIMAL`;
- dimensión coincide;
- `semantic_ref` coincide;
- unidad coincide;
- objeto coincide;
- no existe contradicción;
- estado resultante = `STRUCTURALLY_COMPARABLE`.

La diferencia se define únicamente como:

```text
candidate.value_decimal - current.value_decimal
```

No implica mejor/peor.

Para valores no decimales, el resultado puede indicar comparabilidad estructural pero no publica diferencia numérica.

---

## 15. Regla determinista de comparabilidad estructural

Para un par solicitado:

### UNKNOWN

Si cualquiera de las observaciones está `NOT_EVIDENCED`, el resultado es:

```text
UNKNOWN
```

### NOT_STRUCTURALLY_COMPARABLE

Si cualquiera está `CONFLICTING_DATA`, o si existe incompatibilidad en:

- dimensión;
- `value_kind`;
- `semantic_ref`;
- unidad cuando aplique;
- `object_id`;
- supplier/candidate relation necesaria;

el resultado es:

```text
NOT_STRUCTURALLY_COMPARABLE
```

### STRUCTURALLY_COMPARABLE

Si ambas observaciones están `KNOWN` y los atributos estructurales anteriores son compatibles:

```text
STRUCTURALLY_COMPARABLE
```

Esta regla es técnica y no satisface por sí sola `R-PROV-002`.

---

## 16. SupplierEvidenceInput

```text
context: DecisionContext
purchase_operation: PurchaseOperation
company_scope: str
evaluation_date: date
methodology_version: str
candidates: tuple[SupplierCandidateEvidence, ...]
observations: tuple[SupplierObservation, ...]
historical_facts: tuple[SupplierHistoricalFact, ...]
external_metrics: tuple[ExternalSupplierMetric, ...]
signals: tuple[SupplierSignal, ...]
comparison_requests: tuple[StructuralComparisonRequest, ...]
```

### Invariantes globales

1. `context.decision_id == purchase_operation.decision_id`.
2. `context.scenario_id == purchase_operation.scenario_id`.
3. `methodology_version` debe identificar la metodología cerrada aplicable.
4. `candidate_id`, `observation_id`, `fact_id`, `metric_id`, `signal_id` y `comparison_id` deben ser únicos dentro de su colección.
5. Cada referencia interna debe existir.
6. Observaciones de candidato deben concordar con `supplier_id` del candidato.
7. Requests de comparación deben referenciar una observación del proveedor actual y otra de un candidato.
8. Ninguna colección vacía se interpreta como demostración de ausencia empresarial.

---

## 17. SupplierEvidenceResult

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

El resultado puede preservar objetos de entrada inmutables o representaciones equivalentes normalizadas sin mutarlos.

No contiene:

```text
supplier_score
supplier_rank
preferred_supplier
supplier_risk_level
reliability_score
compliance_score
rule_comparable
assessment
outcome
effect
severity
recommendation
crc_result
purchase_decision
```

---

## 18. Engine

Función pública única propuesta:

```text
evaluate_supplier_evidence(payload: SupplierEvidenceInput) -> SupplierEvidenceResult
```

Responsabilidades:

1. construir identidad;
2. resolver candidatos mediante mapeo fijo;
3. validar referencias internas;
4. ejecutar comparaciones estructurales solicitadas;
5. calcular diferencias decimales puramente descriptivas cuando proceda;
6. preservar hechos, métricas y señales;
7. producir listas explícitas de unresolved/conflicting;
8. no mutar inputs.

---

## 19. No responsabilidades del engine

Queda prohibido:

- seleccionar proveedor;
- ordenar proveedores;
- puntuar proveedor;
- calcular fiabilidad;
- calcular cumplimiento;
- calcular riesgo;
- calcular concentración;
- activar `R-PROV-001/002`;
- generar `Assessment`;
- ejecutar CRC;
- emitir recomendación;
- convertir GAP/ausencia en FALSE;
- reinterpretar Q&T confidence como supplier reliability;
- recalcular PRICE/TCO/STK/Finance.

---

## 20. Estados unresolved/conflicting

`unresolved_items` deberá incluir referencias a elementos cuya información factual no esté suficientemente evidenciada para el uso solicitado.

`conflicting_items` deberá incluir referencias a elementos en `CONFLICTING_DATA`.

Estas colecciones son trazabilidad/explicabilidad y no constituyen score de calidad.

---

## 21. Tests contractuales mínimos

La implementación deberá cubrir, como mínimo:

1. candidato actual demostrado;
2. reference-only → NOT_EVIDENCED;
3. GAP → NOT_EVIDENCED;
4. conflicto → CONFLICTING_DATA;
5. candidato igual a proveedor actual rechazado;
6. candidato con otro objeto rechazado;
7. candidato actual expirado rechazado;
8. candidate_id duplicado rechazado;
9. dos propuestas distintas del mismo supplier permitidas;
10. observation KNOWN con valor tipado;
11. observation no KNOWN no publica valor;
12. disponibilidad texto no se transforma en cantidad;
13. hecho histórico preservado sin score;
14. señal preservada sin criticidad;
15. métrica autorizada exige `usage_authority_ref`;
16. métrica context-only no se eleva;
17. request explícito produce comparabilidad estructural;
18. no se genera cross-product de comparaciones;
19. NOT_EVIDENCED → comparison UNKNOWN;
20. CONFLICTING_DATA → no comparación factual determinada;
21. incompatibilidad de unidad/semántica → NOT_STRUCTURALLY_COMPARABLE;
22. decimal comparable produce diferencia descriptiva exacta;
23. diferencia no genera mejor/peor;
24. DecisionContext/PurchaseOperation coherentes;
25. referencias internas inválidas rechazadas;
26. no mutación;
27. salida sin campos decisionales.

---

## 22. Criterio de cierre técnico

El contrato podrá cerrarse si Audit 1 y Audit 2 confirman:

- representabilidad completa de la metodología v0.3;
- ausencia de política empresarial nueva;
- separación de C0 Evidence;
- no autoautorización de métricas;
- comparabilidad estructural inequívocamente separada de Rules;
- no scoring/ranking;
- no duplicación de otras capas;
- no mutación;
- tests suficientes para proteger las invariantes.
