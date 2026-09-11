# EIOS — DELIVERY / STOCKOUT ANALYZER · IMPLEMENTATION CONTRACT v0.1

**Estado:** DISEÑO TÉCNICO — PENDIENTE DE AUDIT 1  
**Fecha:** 11/09/2026  
**Regla soportada posteriormente:** `R-ENT-001 — Entrega posterior al riesgo de rotura`  
**Baseline de rama:** `main @ ee4e149c42fe8f1c6619fb62387397dc63767ea8`

---

## 1. Propósito

Definir el contrato técnico mínimo de un analizador factual especializado que compare una fecha prevista de entrega aplicable a una compra propuesta concreta contra el `depletion_date` producido por STK para el escenario base sin esa compra.

El analizador materializa exclusivamente la semántica cerrada por:

- `01_Modelo/Delivery_Stockout_Methodological_Closure_v0.3.md`;
- `04_Reglas/Especificacion_Reglas_Entrega_MVP.md`;
- `04_Reglas/Rule_Dependency_Matrix.md` v1.5;
- contrato físico STK vigente;
- Supplier Evidence Core vigente;
- `08_Implementacion/Assessment_Individual_Result_Contract.md` como frontera posterior.

Este contrato no redefine la regla `R-ENT-001` y no convierte el analizador en motor de reglas.

---

## 2. Frontera de autoridad

```text
STK baseline result
      +
provenance de baseline/exclusión
      ↓
BaselineStockoutQualification

Delivery evidence específica de propuesta
      ↓
PurchaseSpecificDeliveryTimingEvidence

ambas
      ↓
DeliveryStockoutAnalyzer
      ↓
DeliveryStockoutAnalysisResult
      ↓
[futura frontera Rules]
      ↓
Assessment R-ENT-001
```

El analizador:

- no calcula stock;
- no recalcula STK;
- no crea escenarios;
- no determina por sí solo qué escenario es baseline;
- no deriva fecha desde `lead_time`;
- no consulta Supplier;
- no valida una observación Supplier por coincidencia nominal;
- no produce `Assessment`;
- no produce `NEGOCIAR`;
- no ejecuta CRC;
- no decide una compra;
- no crea parámetros.

---

## 3. Ubicación física prevista

Después del cierre del contrato y no antes:

```text
eios/delivery/
├── __init__.py
├── models.py
└── engine.py
```

Opcionalmente podrá existir `adapters.py` únicamente si Audit 2 demuestra que un adaptador Supplier puede materializarse sin crear autoridad implícita.

No se autoriza persistencia SQL, tabla propia, API ni modificación de C0 para esta unidad.

---

## 4. Principio de identidad

ENT no crea una nueva identidad empresarial persistente.

El contexto se preserva mediante identidades ya existentes y referencias trazables:

- `decision_id`;
- `article_id`;
- `supplier_id`, cuando aplique a delivery evidence;
- `evaluated_purchase_ref`, como referencia externa trazable a la propuesta evaluada.

`evaluated_purchase_ref`:

- no es un nuevo `Purchase_ID` canónico;
- no redefine `PurchaseOperation`;
- no se reutiliza como `scenario_id`;
- solo permite demostrar que baseline y delivery evidence se refieren a la misma propuesta sometida a análisis.

---

## 5. Estados controlados del analizador

### 5.1 `DeliveryAnalysisState`

Valores autorizados:

```text
LATE_DELIVERY_DEMONSTRATED
NOT_LATE_DEMONSTRATED
NOT_LATE_WITHIN_EVIDENCED_HORIZON
NOT_EVIDENCED
CONFLICTING_DATA
NOT_DETERMINABLE
```

No son estados de `Assessment` ni recomendaciones empresariales.

### 5.2 Limitaciones autorizadas

`DeliveryLimitationCode` se limita inicialmente a:

```text
SAME_DAY_ORDER_NOT_DEMONSTRATED
DELIVERY_BEYOND_STK_HORIZON
```

No se crearán otros códigos sin autoridad documental adicional o una depuración contractual posterior que demuestre que son meras representaciones de una autoridad ya existente.

---

## 6. Estado de las entradas especializadas

Para evitar reutilizar indebidamente estados de STK o Supplier, las evidencias especializadas ENT utilizan un estado local de calificación:

```text
ENTEvidenceState =
    KNOWN
    NOT_EVIDENCED
    CONFLICTING_DATA
    NOT_DETERMINABLE
```

Este estado describe exclusivamente la suficiencia factual del objeto ENT y no redefine:

- `StockDataState`;
- `SupplierObservation.state`;
- `Evidence.state` de C0;
- `Assessment.status`.

---

## 7. `BaselineStockoutQualification`

### 7.1 Propósito

Representar la calificación trazable de un `StockProjectionResult` como escenario base apto para ENT, demostrando que la compra evaluada no está incorporada a esa proyección.

### 7.2 Campos mínimos previstos

```text
BaselineStockoutQualification
├── decision_id: str
├── article_id: str
├── evaluated_purchase_ref: str
├── projection: StockProjectionResult
├── state: ENTEvidenceState
├── baseline_relation_ref: str | None
├── projection_provenance_ref: str | None
├── purchase_exclusion_ref: str | None
├── evidence_refs: tuple[str, ...]
├── issue_refs: tuple[str, ...]
└── trace_refs: tuple[str, ...]
```

### 7.3 Invariantes

Cuando `state = KNOWN`:

1. `decision_id == projection.identity.decision_id`;
2. `article_id == projection.identity.article_id`;
3. `baseline_relation_ref` es obligatorio;
4. `projection_provenance_ref` es obligatorio;
5. `purchase_exclusion_ref` es obligatorio;
6. debe existir al menos una referencia trazable entre `evidence_refs` y `trace_refs`;
7. ninguna validación puede considerar `projection.identity.scenario_id` suficiente para demostrar baseline;
8. el objeto no inspecciona nombres de escenario para inferir baseline;
9. no recalcula `projection.depletion_date`;
10. no reconstruye la lista de movimientos STK.

Cuando `state != KNOWN`, el objeto no puede publicar una afirmación de baseline válido por mera presencia de referencias parciales.

### 7.4 `depletion_date`

ENT consume exactamente:

```text
projection.depletion_date.state
projection.depletion_date.value
projection.horizon.horizon_end
```

No crea una segunda fecha de agotamiento.

---

## 8. `PurchaseSpecificDeliveryTimingEvidence`

### 8.1 Propósito

Representar una fecha prevista de entrega cuya semántica y aplicabilidad estén demostradas para la propuesta concreta analizada.

### 8.2 Campos mínimos previstos

```text
PurchaseSpecificDeliveryTimingEvidence
├── decision_id: str
├── article_id: str
├── supplier_id: str
├── evaluated_purchase_ref: str
├── state: ENTEvidenceState
├── expected_delivery_date: date | None
├── date_semantic_ref: str | None
├── applicability_ref: str | None
├── source_ref: str | None
├── evidence_id: str | None
├── captured_at: date | None
├── issue_refs: tuple[str, ...]
└── trace_refs: tuple[str, ...]
```

### 8.3 Invariantes

Cuando `state = KNOWN`:

1. `expected_delivery_date` es obligatoria;
2. `date_semantic_ref` es obligatoria;
3. `applicability_ref` es obligatoria;
4. `source_ref` es obligatoria;
5. `evidence_id` es obligatoria;
6. `captured_at` es obligatoria;
7. `decision_id`, `article_id`, `supplier_id` y `evaluated_purchase_ref` son no vacíos;
8. no existe campo `lead_time` en este contrato;
9. no se deriva fecha desde `operation_date`;
10. no se deriva fecha desde la fecha de captura.

Cuando `state != KNOWN`, `expected_delivery_date` debe ser `None`.

---

## 9. Compatibilidad entre entradas

`DeliveryStockoutAnalysisInput` reúne:

```text
baseline: BaselineStockoutQualification
delivery: PurchaseSpecificDeliveryTimingEvidence
```

La entrada solo es estructuralmente compatible cuando:

```text
baseline.decision_id == delivery.decision_id
baseline.article_id == delivery.article_id
baseline.evaluated_purchase_ref == delivery.evaluated_purchase_ref
```

Una incompatibilidad de identidad/contexto es error de contrato de entrada y no una conclusión empresarial.

No se comparan dos propuestas distintas dentro del mismo resultado ENT.

---

## 10. `DeliveryStockoutAnalysisResult`

### 10.1 Campos previstos

```text
DeliveryStockoutAnalysisResult
├── decision_id: str
├── article_id: str
├── supplier_id: str
├── evaluated_purchase_ref: str
├── state: DeliveryAnalysisState
├── depletion_date: date | None
├── expected_delivery_date: date | None
├── horizon_end: date | None
├── limitation_codes: tuple[DeliveryLimitationCode, ...]
├── evidence_refs: tuple[str, ...]
├── issue_refs: tuple[str, ...]
└── trace_refs: tuple[str, ...]
```

### 10.2 Regla de publicación de fechas

El resultado puede copiar una fecha únicamente cuando esa fecha procede de una entrada que la publica legítimamente.

No sintetiza fechas.

### 10.3 No `Assessment`

El resultado no contiene:

- `rule_id` como mecanismo de evaluación;
- `Assessment.status`;
- `Assessment.outcome`;
- efecto;
- severidad;
- recomendación;
- `NEGOCIAR`;
- decisión.

---

## 11. Algoritmo determinista autorizado

La función prevista:

```text
analyze_delivery_stockout(input) -> DeliveryStockoutAnalysisResult
```

aplica esta precedencia exacta.

### 11.1 Calificación de baseline

```text
baseline.state = CONFLICTING_DATA
→ CONFLICTING_DATA

baseline.state != KNOWN
→ NOT_DETERMINABLE
```

`NOT_EVIDENCED` del baseline no se convierte aquí en `NOT_EVIDENCED` del resultado porque la metodología cerrada establece baseline/provenance inválido como `NOT_DETERMINABLE`.

### 11.2 Evidencia de delivery

Con baseline KNOWN:

```text
delivery.state = NOT_EVIDENCED
→ NOT_EVIDENCED

delivery.state = CONFLICTING_DATA
→ CONFLICTING_DATA

delivery.state = NOT_DETERMINABLE
→ NOT_DETERMINABLE
```

### 11.3 Estado STK de agotamiento

Con baseline y delivery KNOWN:

```text
projection.depletion_date.state = CONFLICTING_DATA
→ CONFLICTING_DATA

projection.depletion_date.state = UNKNOWN
→ NOT_DETERMINABLE

projection.depletion_date.state = NOT_EVIDENCED
→ NOT_DETERMINABLE
```

`NOT_EVIDENCED` de STK no se transforma en puntualidad ni en `FALSE`.

### 11.4 `depletion_date = KNOWN`

```text
expected_delivery_date > depletion_date
→ LATE_DELIVERY_DEMONSTRATED

expected_delivery_date < depletion_date
→ NOT_LATE_DEMONSTRATED

expected_delivery_date = depletion_date
→ NOT_LATE_DEMONSTRATED
   + SAME_DAY_ORDER_NOT_DEMONSTRATED
```

### 11.5 `depletion_date = NOT_APPLICABLE`

Se requiere `projection.horizon.state = KNOWN` y `horizon_end` determinada.

```text
expected_delivery_date <= horizon_end
→ NOT_LATE_WITHIN_EVIDENCED_HORIZON

expected_delivery_date > horizon_end
→ NOT_DETERMINABLE
   + DELIVERY_BEYOND_STK_HORIZON
```

Si el horizonte no está determinado, el resultado es `NOT_DETERMINABLE` sin extrapolación.

### 11.6 Otros estados

Cualquier estado STK no cubierto expresamente por la autoridad anterior produce `NOT_DETERMINABLE`; no se crea una interpretación nueva.

---

## 12. Orden de precedencia completo

El orden es parte del contrato:

```text
1. incompatibilidad estructural de identidad → error de validación
2. baseline CONFLICTING_DATA → CONFLICTING_DATA
3. baseline no KNOWN → NOT_DETERMINABLE
4. delivery NOT_EVIDENCED → NOT_EVIDENCED
5. delivery CONFLICTING_DATA → CONFLICTING_DATA
6. delivery NOT_DETERMINABLE → NOT_DETERMINABLE
7. depletion CONFLICTING_DATA → CONFLICTING_DATA
8. depletion UNKNOWN / NOT_EVIDENCED → NOT_DETERMINABLE
9. depletion KNOWN → comparación estricta de fechas
10. depletion NOT_APPLICABLE → razonamiento limitado al horizonte evidenciado
```

La precedencia evita que una contradicción posterior o una ausencia factual se conviertan silenciosamente en resultado booleano.

---

## 13. Provenance y trazabilidad

El analizador no crea un segundo sistema de Trace.

El resultado conserva referencias de entrada suficientes para reconstruir:

- qué proyección STK fue utilizada;
- por qué fue calificada como baseline sin la compra;
- qué evidencia aportó la fecha de entrega;
- qué aplicabilidad vinculó esa fecha con la propuesta;
- qué issues/contradicciones estaban presentes.

La implementación podrá combinar referencias para exposición, pero no las reinterpretará como autoridad nueva.

No se autoriza un hash propio ni persistencia de trace ENT en esta versión.

---

## 14. Supplier Evidence Adapter

La metodología permite que una `SupplierObservation` con:

```text
dimension = DELIVERY_DATE
value_kind = DATE
```

sea una fuente potencial.

Sin embargo, `SupplierObservation` no demuestra por sí sola aplicabilidad a la propuesta evaluada.

Por tanto, v0.1 del contrato **no autoriza todavía** un adaptador automático Supplier → `PurchaseSpecificDeliveryTimingEvidence`.

Audit 1 deberá determinar si existe en los contratos físicos actuales una combinación suficiente de:

- `SupplierObservation`;
- evidencia de candidato/propuesta;
- `applicability_ref` externo;
- identidad decisional;

que permita una adaptación determinista sin inventar relación.

Si no existe, la implementación MVP recibirá directamente `PurchaseSpecificDeliveryTimingEvidence` ya calificada por la capa autorizada que la construya.

---

## 15. Frontera posterior hacia Rules

Este contrato no implementa el bridge ENT → `Assessment`.

La futura unidad de integración de `R-ENT-001` deberá auditar separadamente una correspondencia potencial como:

```text
LATE_DELIVERY_DEMONSTRATED
→ Assessment EVALUABLE / TRUE

NOT_LATE_DEMONSTRATED
NOT_LATE_WITHIN_EVIDENCED_HORIZON
→ Assessment EVALUABLE / FALSE

NOT_EVIDENCED
CONFLICTING_DATA
NOT_DETERMINABLE
→ Assessment NOT_EVALUABLE / None
```

Esta tabla se registra aquí solo como **frontera candidata a auditar**, no como comportamiento autorizado del analizador.

No será materializada en `eios/delivery` dentro de esta unidad.

---

## 16. Inmutabilidad y validación física

Los modelos previstos deberán seguir las convenciones defensivas ya utilizadas por STK/Supplier:

```text
extra = forbid
str_strip_whitespace = true
frozen = true
```

cuando sean compatibles con el patrón físico vigente.

Se prohibirán:

- referencias vacías;
- duplicados en tuplas de referencias cuando corresponda;
- `expected_delivery_date` en evidencia no KNOWN;
- baseline KNOWN sin prueba de exclusión;
- baseline KNOWN sin provenance;
- resultados que publiquen fechas sintetizadas;
- estados contradictorios con su payload.

---

## 17. Persistencia

Para el Vertical MVP:

- no se demuestra necesidad de tabla ENT;
- no se demuestra necesidad de `DeliveryAnalysis_ID` persistente;
- no se demuestra necesidad de índices propios;
- no se modifica SQL Server.

El resultado puede ser transitorio y trazable mediante referencias existentes.

Persistencia futura requiere autoridad separada.

---

## 18. Tests contractuales previstos

Después del cierre del contrato, la implementación deberá cubrir al menos:

1. delivery posterior a depletion KNOWN;
2. delivery anterior;
3. misma fecha + limitación autorizada;
4. depletion NOT_APPLICABLE + delivery dentro de horizonte;
5. depletion NOT_APPLICABLE + delivery posterior al horizonte;
6. depletion UNKNOWN;
7. depletion NOT_EVIDENCED;
8. depletion CONFLICTING_DATA;
9. delivery NOT_EVIDENCED;
10. delivery CONFLICTING_DATA;
11. delivery NOT_DETERMINABLE;
12. baseline NOT_EVIDENCED/NOT_DETERMINABLE;
13. baseline CONFLICTING_DATA;
14. identidad decision/article/purchase incompatible;
15. baseline KNOWN sin exclusión → validación rechazada;
16. baseline KNOWN sin provenance → validación rechazada;
17. delivery KNOWN sin applicability → validación rechazada;
18. delivery no KNOWN con fecha → validación rechazada;
19. no derivación de fecha desde lead time;
20. no extrapolación fuera de horizonte;
21. ausencia de campos Assessment/decision/recommendation;
22. modelos inmutables y `extra=forbid`.

---

## 19. No regresión

La futura implementación no podrá modificar silenciosamente:

- `eios/core/models.py`;
- `eios/core/c0.py`;
- `eios/stock/*`;
- `eios/supplier/*`;
- parámetros;
- Rules/RDM ya cerradas;
- CRC;
- Decision Twin;
- autoridad humana.

Cualquier necesidad real de modificar uno de esos componentes deberá detener la materialización y volver a auditoría de contrato.

---

## 20. Gate de cierre

Este diseño solo podrá pasar a implementación cuando Audit 1, depuración y Audit 2 confirmen:

- semántica exacta de estados;
- compatibilidad con `StockProjectionResult` físico;
- tratamiento completo de `ProjectionHorizon`;
- ausencia de identidad inventada;
- suficiencia de provenance del baseline;
- suficiencia de aplicabilidad del delivery;
- separación ENT / Assessment;
- separación ENT / Supplier;
- separación ENT / STK;
- ausencia de fecha derivada;
- ausencia de persistencia inventada;
- determinismo de precedencia;
- testabilidad completa.

---

## 21. Estado

```text
DISEÑO TÉCNICO ENT ANALYZER v0.1   MATERIALIZADO
AUDIT 1                            PENDIENTE
DEPURACIÓN                         PENDIENTE
AUDIT 2                            PENDIENTE
CIERRE                             PENDIENTE
CÓDIGO                             NO AUTORIZADO TODAVÍA
```
