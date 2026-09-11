# EIOS — DELIVERY / STOCKOUT ANALYZER · IMPLEMENTATION CONTRACT v0.2

**Estado:** DEPURADO TRAS AUDIT 1 — PENDIENTE DE AUDIT 2  
**Fecha:** 11/09/2026  
**Sustituye como diseño activo:** v0.1  
**Baseline:** `main @ ee4e149c42fe8f1c6619fb62387397dc63767ea8`

---

## 1. Propósito

Definir el contrato técnico mínimo del analizador factual ENT que relaciona una fecha prevista de entrega propuesta-específica con el `depletion_date` producido por STK para un baseline demostrado sin la compra evaluada.

Fuentes de autoridad:

- `01_Modelo/Delivery_Stockout_Methodological_Design_v0.3.md`;
- `01_Modelo/Delivery_Stockout_Methodological_Audit_2_Final_v0.3.md`;
- `01_Modelo/Delivery_Stockout_Methodological_Closure_v0.3.md`;
- `01_Modelo/Delivery_Stockout_Methodological_Reconciliation_v0.3.1.md`;
- `04_Reglas/Especificacion_Reglas_Entrega_MVP.md`;
- `04_Reglas/Rule_Dependency_Matrix.md` v1.5;
- STK físico vigente;
- Supplier Evidence Core vigente;
- Assessment contract como frontera posterior.

---

## 2. Correcciones incorporadas de Audit 1

```text
ENT-TC-A1-01  CORREGIDO
ENT-TC-A1-02  CORREGIDO mediante reconciliación v0.3.1
ENT-TC-A1-03  CORREGIDO
ENT-TC-A1-04  CORREGIDO
ENT-TC-A1-05  CORREGIDO
```

No se añade política empresarial.

---

## 3. Posición y frontera

```text
StockProjectionResult
        +
provenance de baseline/exclusión
        ↓
BaselineStockoutQualification

fecha delivery + semántica + aplicabilidad
        ↓
PurchaseSpecificDeliveryTimingEvidence

ambas entradas
        ↓
DeliveryStockoutAnalyzer
        ↓
DeliveryStockoutAnalysisResult
        ↓
[futura unidad Rules]
        ↓
Assessment R-ENT-001
```

ENT no:

- calcula ni recalcula stock;
- crea escenarios;
- determina baseline por `scenario_id`;
- deriva delivery desde lead time;
- consulta sistemas externos;
- eleva Supplier observations automáticamente;
- produce Assessment;
- produce `NEGOCIAR`;
- ejecuta CRC;
- decide una compra.

---

## 4. Materialización física autorizable tras cierre

```text
eios/delivery/
├── __init__.py
├── models.py
└── engine.py
```

No se autoriza `adapters.py` en esta versión.

No se autoriza SQL, persistencia, API ni modificación de C0/STK/Supplier.

---

## 5. Identidad y referencia de propuesta

ENT reutiliza:

- `decision_id`;
- `article_id`;
- `evaluation_date`;
- `supplier_id` en delivery evidence;
- `evaluated_purchase_ref` como referencia trazable local a la propuesta analizada.

`evaluated_purchase_ref` representa físicamente el concepto metodológico `evaluated_purchase_trace_ref`.

No constituye:

- `Purchase_ID` global;
- identidad de escenario;
- modificación de `PurchaseOperation`;
- identidad persistente nueva.

---

## 6. Estados técnicos locales

### 6.1 Baseline

```text
BaselineQualificationState =
    KNOWN
    CONFLICTING_DATA
    NOT_DETERMINABLE
```

Semántica local:

- `KNOWN`: la relación baseline + exclusión de compra está suficientemente demostrada;
- `CONFLICTING_DATA`: la calificación contiene contradicción material no resuelta;
- `NOT_DETERMINABLE`: falta o incompatibilidad de provenance/identidad impide demostrar baseline.

No existe `NOT_EVIDENCED` como estado especializado de baseline; la ausencia de la prueba requerida desemboca en `NOT_DETERMINABLE` conforme a la metodología.

### 6.2 Delivery evidence

Se conserva exactamente:

```text
DeliveryTimingEvidenceState =
    KNOWN
    NOT_EVIDENCED
    CONFLICTING_DATA
    NOT_DETERMINABLE
```

### 6.3 Resultado ENT

```text
DeliveryAnalysisState =
    LATE_DELIVERY_DEMONSTRATED
    NOT_LATE_DEMONSTRATED
    NOT_LATE_WITHIN_EVIDENCED_HORIZON
    NOT_EVIDENCED
    CONFLICTING_DATA
    NOT_DETERMINABLE
```

### 6.4 Limitaciones autorizadas

```text
DeliveryLimitationCode =
    SAME_DAY_ORDER_NOT_DEMONSTRATED
    DELIVERY_BEYOND_STK_HORIZON
    PAST_DELIVERY_DATE_APPLICABILITY_UNPROVEN
```

No se crean otros códigos.

---

## 7. `BaselineStockoutQualification`

### 7.1 Modelo previsto

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

### 7.2 Coherencia de identidad

Siempre, independientemente del estado:

```text
decision_id == projection.identity.decision_id
article_id == projection.identity.article_id
evaluation_date == projection.identity.evaluation_date
```

Una incompatibilidad es error estructural de entrada.

### 7.3 Requisitos `KNOWN`

`KNOWN` exige:

- `baseline_projection_ref` no vacío;
- `baseline_relation_ref` no vacío;
- `projection_provenance_ref` no vacío;
- `purchase_exclusion_ref` no vacío;
- `evaluated_purchase_ref` no vacío;
- al menos una referencia entre `evidence_refs` y `trace_refs`;
- `unresolved_refs` vacío.

`KNOWN` no se deduce de:

- `projection.identity.scenario_id`;
- nombre del escenario;
- ausencia aparente de un movimiento en el resultado STK.

ENT no reconstruye los movimientos originales.

### 7.4 `CONFLICTING_DATA`

Exige al menos un `issue_ref` o `unresolved_ref` que preserve la contradicción documentada.

No selecciona una versión preferente.

### 7.5 `NOT_DETERMINABLE`

Puede representar ausencia o incompatibilidad de provenance de baseline.

No publica una afirmación positiva de exclusión de compra.

---

## 8. Consumo de STK

ENT consume sin recalcular:

```text
projection.identity
projection.depletion_date.state
projection.depletion_date.value
projection.horizon.state
projection.horizon.horizon_end
projection.issue_refs
projection.trace_refs
```

`baseline_projection_ref` conserva una referencia estable al objeto/resultado STK consumido.

No se crea una segunda `depletion_date` como cálculo independiente.

---

## 9. `PurchaseSpecificDeliveryTimingEvidence`

### 9.1 Modelo previsto

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

### 9.2 Validez temporal estructural

Si existen `valid_from` y `valid_to`:

```text
valid_to >= valid_from
```

El intervalo se conserva como metadata de evidencia. ENT no inventa una política universal de expiración basada únicamente en esas fechas.

### 9.3 Estado `KNOWN`

Exige:

- `expected_delivery_date`;
- `delivery_semantic_ref`;
- `purchase_applicability_ref`;
- `source_ref`;
- `captured_at`;
- al menos un `evidence_ref`;
- sin contradicción material no resuelta representada por el estado.

La aplicabilidad a la propuesta actual debe quedar demostrada por `purchase_applicability_ref`; artículo/proveedor/candidate no bastan.

### 9.4 Estado `NOT_EVIDENCED`

No puede sostener una fecha utilizable por la comparación.

`expected_delivery_date = None` en el modelo operativo ENT.

Las referencias disponibles se conservan para trazabilidad.

### 9.5 Estado `CONFLICTING_DATA`

No publica una fecha única utilizable:

```text
expected_delivery_date = None
```

Debe conservar al menos un `issue_ref`.

### 9.6 Estado `NOT_DETERMINABLE`

Puede ocurrir de dos formas:

1. sin fecha suficientemente determinada → `expected_delivery_date = None`;
2. existe una fecha factual suficientemente identificada, pero no se demuestra su aplicabilidad actual a la propuesta → se permite conservar `expected_delivery_date` junto con `source_ref`, `evidence_refs`, `captured_at` y `delivery_semantic_ref`, sin `purchase_applicability_ref` concluyente.

Esta segunda forma existe para representar el caso metodológico de fecha pasada cuya aplicabilidad actual no se demuestra.

Conservar la fecha no la convierte en KNOWN para comparación.

---

## 10. Compatibilidad entre entradas

`DeliveryStockoutAnalysisInput` contiene:

```text
baseline: BaselineStockoutQualification
delivery: PurchaseSpecificDeliveryTimingEvidence
```

Debe cumplir:

```text
baseline.decision_id == delivery.decision_id
baseline.article_id == delivery.article_id
baseline.evaluation_date == delivery.evaluation_date
baseline.evaluated_purchase_ref == delivery.evaluated_purchase_ref
```

Una incompatibilidad produce error de validación.

No se convierte en `FALSE`, `NOT_LATE` ni recomendación.

---

## 11. `DeliveryStockoutAnalysisResult`

### 11.1 Modelo previsto

```text
DeliveryStockoutAnalysisResult
├── decision_id: str
├── article_id: str
├── supplier_id: str
├── evaluation_date: date
├── evaluated_purchase_ref: str
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

### 11.2 Copia, no cálculo

Las fechas solo pueden proceder de:

- `baseline.projection.depletion_date.value`;
- `delivery.expected_delivery_date`;
- `baseline.projection.horizon.horizon_end`.

No se sintetizan fechas.

### 11.3 No Assessment

El resultado no contiene semántica de:

- `Assessment.status`;
- `Assessment.outcome`;
- efecto;
- severidad;
- `NEGOCIAR`;
- recommendation;
- decisión.

---

## 12. Precedencia del engine

Función prevista:

```text
analyze_delivery_stockout(
    payload: DeliveryStockoutAnalysisInput
) -> DeliveryStockoutAnalysisResult
```

### Paso 0 — validación estructural

Las incompatibilidades de `decision/article/evaluation_date/evaluated_purchase_ref` son errores de contrato de entrada.

### Paso 1 — baseline

```text
baseline.state = CONFLICTING_DATA
→ CONFLICTING_DATA

baseline.state = NOT_DETERMINABLE
→ NOT_DETERMINABLE

baseline.state = KNOWN
→ continuar
```

### Paso 2 — delivery evidence

Antes del mapeo genérico de `NOT_DETERMINABLE`, si:

```text
delivery.state = NOT_DETERMINABLE
AND delivery.expected_delivery_date existe
AND delivery.expected_delivery_date < delivery.evaluation_date
AND purchase_applicability_ref no demuestra aplicabilidad actual
```

entonces:

```text
→ NOT_DETERMINABLE
+ PAST_DELIVERY_DATE_APPLICABILITY_UNPROVEN
```

En el resto:

```text
delivery NOT_EVIDENCED    → NOT_EVIDENCED
delivery CONFLICTING_DATA → CONFLICTING_DATA
delivery NOT_DETERMINABLE → NOT_DETERMINABLE
delivery KNOWN            → continuar
```

### Paso 3 — depletion STK

Con baseline y delivery KNOWN:

```text
depletion CONFLICTING_DATA → CONFLICTING_DATA
depletion UNKNOWN          → NOT_DETERMINABLE
depletion NOT_EVIDENCED     → NOT_DETERMINABLE
depletion KNOWN             → comparar
depletion NOT_APPLICABLE    → horizonte
```

El tercer mapeo está autorizado específicamente por `Delivery_Stockout_Methodological_Reconciliation_v0.3.1.md`.

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

Si:

```text
projection.horizon.state != KNOWN
OR horizon_end is None
```

→ `NOT_DETERMINABLE`.

Con horizonte KNOWN:

```text
expected_delivery_date <= horizon_end
→ NOT_LATE_WITHIN_EVIDENCED_HORIZON

expected_delivery_date > horizon_end
→ NOT_DETERMINABLE
+ DELIVERY_BEYOND_STK_HORIZON
```

No se extrapola fuera del horizonte.

---

## 13. Precedencia completa

```text
1. error estructural de identidad/contexto → excepción de validación
2. baseline CONFLICTING_DATA → CONFLICTING_DATA
3. baseline NOT_DETERMINABLE → NOT_DETERMINABLE
4. delivery past-date sin aplicabilidad actual → NOT_DETERMINABLE + limitation
5. delivery NOT_EVIDENCED → NOT_EVIDENCED
6. delivery CONFLICTING_DATA → CONFLICTING_DATA
7. delivery NOT_DETERMINABLE → NOT_DETERMINABLE
8. depletion CONFLICTING_DATA → CONFLICTING_DATA
9. depletion UNKNOWN → NOT_DETERMINABLE
10. depletion NOT_EVIDENCED → NOT_DETERMINABLE
11. depletion KNOWN → comparación estricta
12. depletion NOT_APPLICABLE → límite de horizonte
```

---

## 14. Propagación de refs

El resultado conserva, sin reinterpretar:

- `evidence_refs` de baseline y delivery;
- `unresolved_refs` de baseline;
- `issue_refs` de ambas entradas y del resultado STK cuando materialmente aplicables;
- `trace_refs` de ambas entradas y STK.

La implementación debe deduplicar preservando el primer orden de aparición.

No se crea un sistema Trace paralelo.

---

## 15. Supplier

No se autoriza adaptador automático Supplier en esta versión.

Una `SupplierObservation` puede actuar como fuente previa solo si otra capa construye `PurchaseSpecificDeliveryTimingEvidence` y aporta explícitamente:

- semántica correcta;
- `purchase_applicability_ref`;
- identidad compatible;
- evidencia/captura;
- trazabilidad.

`candidate_id` no se interpreta como `evaluated_purchase_ref`.

---

## 16. Frontera posterior Rules

El bridge a `Assessment` queda fuera de alcance.

La correspondencia potencial se auditará en una unidad posterior y no se implementará en `eios/delivery` durante esta unidad.

ENT no importa `Assessment` para producir su salida.

---

## 17. Convenciones físicas

Los modelos ENT serán Pydantic y seguirán, donde aplique:

```text
extra="forbid"
str_strip_whitespace=True
frozen=True
```

Se validará:

- refs obligatorias no vacías;
- tuplas sin duplicados;
- `valid_to >= valid_from`;
- identidad STK/ENT compatible;
- baseline KNOWN con refs completas;
- conflicto con issues preservados;
- delivery KNOWN con fecha, semántica, aplicabilidad, fuente, evidencia y captura;
- `NOT_EVIDENCED`/`CONFLICTING_DATA` sin fecha operativa;
- `NOT_DETERMINABLE` con fecha solo cuando la fecha factual está soportada pero la aplicabilidad no está demostrada;
- estados de resultado compatibles con sus fechas/limitaciones.

---

## 18. Persistencia

No procede persistencia propia en MVP.

No se crean:

- tabla ENT;
- `DeliveryAnalysis_ID`;
- índice SQL;
- DDL;
- repositorio de resultados.

---

## 19. Tests mínimos obligatorios

1. `delivery > depletion`;
2. `delivery < depletion`;
3. igualdad + SAME_DAY;
4. NOT_APPLICABLE dentro de horizonte;
5. NOT_APPLICABLE fuera de horizonte;
6. horizon no KNOWN con depletion NOT_APPLICABLE;
7. depletion UNKNOWN;
8. depletion NOT_EVIDENCED;
9. depletion CONFLICTING_DATA;
10. delivery NOT_EVIDENCED;
11. delivery CONFLICTING_DATA;
12. delivery NOT_DETERMINABLE sin fecha;
13. fecha pasada + aplicabilidad no demostrada;
14. fecha pasada + aplicabilidad demostrada → comparación normal;
15. baseline NOT_DETERMINABLE;
16. baseline CONFLICTING_DATA;
17. baseline KNOWN sin relation/provenance/exclusion → validación rechazada;
18. mismatch decision;
19. mismatch article;
20. mismatch evaluation_date;
21. mismatch evaluated_purchase_ref;
22. delivery KNOWN sin applicability → rechazado;
23. delivery KNOWN sin evidence_refs → rechazado;
24. delivery NOT_EVIDENCED con fecha → rechazado;
25. delivery CONFLICTING_DATA con fecha única → rechazado;
26. valid_to anterior a valid_from → rechazado;
27. `scenario_id` no usado para calificar baseline;
28. no lead time en input/engine;
29. no Assessment en output;
30. inmutabilidad/extra forbid;
31. deduplicación estable de refs.

---

## 20. No regresión

La futura implementación no modificará:

```text
eios/core/*
eios/stock/*
eios/supplier/*
04_Reglas/*
02_Parametros/*
SQL
```

Si durante materialización se demuestra imprescindible modificar una de esas autoridades, se detiene implementación y se vuelve a contrato/auditoría.

---

## 21. Gate

```text
DISEÑAR       ✅ v0.1
AUDITAR       ✅ Audit 1
RECONCILIAR   ✅ metodología v0.3.1
DEPURAR       ✅ v0.2
AUDITAR 2     PENDIENTE
CERRAR        PENDIENTE
MATERIALIZAR  NO AUTORIZADO TODAVÍA
CI            NO APLICA TODAVÍA
```

**Estado actual: APTO PARA AUDIT 2; NO APTO TODAVÍA PARA CÓDIGO.**
