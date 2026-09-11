# EIOS — ENTREGA / R-ENT-001 · METHODOLOGICAL DESIGN v0.2

**Estado:** DEPURADO — PENDIENTE DE AUDIT 2  
**Fecha:** 11/09/2026  
**Base:** `Delivery_Stockout_Methodological_Audit_1_v0.1.md`

---

## 1. Propósito de la depuración

Corregir los dos puntos de representabilidad detectados por Audit 1 sin modificar C0, STK, Supplier, Scenario Engine, RDM ni Rules:

1. un `scenario_id` no basta para demostrar que una proyección es el baseline sin compra;
2. una observación Supplier `DELIVERY_DATE` no basta para demostrar aplicabilidad a la propuesta concreta.

ENT se mantiene como analizador factual de una relación temporal ya sustentada por autoridades externas.

---

## 2. Frontera cerrada de autoridad

### STK posee

- proyección de stock;
- `depletion_date`;
- `horizon_end`;
- estados de determinabilidad;
- movimientos y reglas M05/M06.

### Arquitectura posee

La exigencia de comparar la compra contra un **escenario base sin compra**.

### Fuente/provenance externa posee

- relación del baseline con la decisión/operación precedente;
- prueba de exclusión de la compra propuesta;
- aplicabilidad de la fecha prevista de entrega a la propuesta concreta.

### ENT posee únicamente

- validación de que las evidencias recibidas son mutuamente compatibles;
- comparación estricta de las fechas cuando son determinables;
- preservación explícita de limitaciones, gaps y contradicciones.

### Rules/CRC/humano poseen

- evaluación de `R-ENT-001`;
- resultado `NEGOCIAR`;
- consolidación;
- recomendación/decisión.

---

## 3. BaselineStockoutQualification

Objeto conceptual de consumo ENT:

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
├── issue_refs
└── trace_refs
```

### 3.1 No crea identidad global nueva

`evaluated_purchase_trace_ref` es una referencia opaca a trazabilidad/evidencia existente que permite vincular la exclusión con la propuesta evaluada.

No constituye:

- `Purchase_ID` nuevo;
- `Alternative_ID`;
- `Scenario_Type`;
- `Parent_Scenario_ID`;
- nueva entidad persistente.

Si el flujo existente no puede producir una referencia trazable suficiente, la calificación no es determinable.

### 3.2 `baseline_relation_ref`

Debe demostrar documentalmente que la proyección consumida corresponde al estado/escenario de referencia previo a la hipótesis de la compra evaluada.

No basta:

```text
scenario_id == X
```

ni:

```text
scenario_id != candidate_scenario_id
```

La relación debe proceder de provenance/trazabilidad autorizada del flujo de escenarios o de la entrada que generó la proyección.

### 3.3 `proposed_purchase_exclusion_ref`

Debe demostrar que el movimiento `PROPOSED_PURCHASE` correspondiente a la compra evaluada no contribuyó al baseline.

No exige que ENT inspeccione o recalculе todos los movimientos; exige una prueba trazable de la exclusión.

### 3.4 Coherencia STK

`depletion_state`, `depletion_date` y `horizon_end` se conservan del resultado STK identificado por `baseline_projection_ref`.

ENT no los recalcula ni corrige.

---

## 4. PurchaseSpecificDeliveryTimingEvidence

Objeto conceptual:

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

### 4.1 `purchase_applicability_ref`

Debe demostrar que la fecha corresponde a la propuesta/compromiso evaluado y no únicamente:

- al proveedor;
- al artículo;
- a una fecha histórica;
- a una referencia genérica;
- a otro pedido/candidato.

### 4.2 Supplier como fuente adaptada

Una observación Supplier puede alimentar este objeto solo mediante adaptación trazable que demuestre:

```text
dimension == DELIVERY_DATE
value_kind == DATE
state == KNOWN
delivery_semantic_ref compatible
purchase_applicability_ref demostrado
article/supplier compatible
```

El adaptador no convierte `semantic_ref` genérico en aplicabilidad por inferencia.

### 4.3 Fecha derivada de lead time

Si otra autoridad produce una fecha trazable a partir de lead time, la fecha resultante puede ser consumida.

ENT no ejecuta la derivación.

---

## 5. Compatibilidad entre las dos evidencias

Para comparación concluyente deben coincidir o ser demostrablemente compatibles:

```text
decision_id
article_id
evaluation context
evaluated_purchase_trace_ref
```

Además, la evidencia de entrega debe referirse al proveedor/condición de la compra evaluada.

Una mera coincidencia de artículo o proveedor no basta.

---

## 6. Estados de relación temporal

```text
LATE_DELIVERY_DEMONSTRATED
NOT_LATE_DEMONSTRATED
NOT_LATE_WITHIN_EVIDENCED_HORIZON
NOT_EVIDENCED
CONFLICTING_DATA
NOT_DETERMINABLE
```

Estos estados son analíticos y no son `Assessment`.

---

## 7. Algoritmo metodológico determinista

### Paso 1 — cualificación del baseline

Si no se demuestra:

- relación de baseline;
- provenance STK;
- exclusión de la compra evaluada;

resultado:

```text
NOT_DETERMINABLE
```

ENT no intenta reconstruir el baseline.

### Paso 2 — evidencia de entrega

`NOT_EVIDENCED` → `NOT_EVIDENCED`.

`CONFLICTING_DATA` → `CONFLICTING_DATA`.

`NOT_DETERMINABLE` → `NOT_DETERMINABLE`.

Solo `KNOWN` permite continuar.

### Paso 3 — estado STK

`UNKNOWN` → `NOT_EVIDENCED` o `NOT_DETERMINABLE` conforme a la causa preservada por STK/provenance; ENT no inventa causalidad.

`CONFLICTING_DATA` → `CONFLICTING_DATA`.

`KNOWN` → Paso 4.

`NOT_APPLICABLE` → Paso 5.

### Paso 4 — depletion KNOWN

Con ambas fechas conocidas:

```text
expected_delivery_date > depletion_date
→ LATE_DELIVERY_DEMONSTRATED

expected_delivery_date < depletion_date
→ NOT_LATE_DEMONSTRATED

expected_delivery_date == depletion_date
→ NOT_LATE_DEMONSTRATED
   + SAME_DAY_ORDER_NOT_DEMONSTRATED
```

La igualdad no satisface la palabra normativa “posterior” a granularidad DATE, pero no prueba orden intradía.

### Paso 5 — depletion NOT_APPLICABLE

```text
expected_delivery_date <= horizon_end
→ NOT_LATE_WITHIN_EVIDENCED_HORIZON

expected_delivery_date > horizon_end
→ NOT_DETERMINABLE
   + DELIVERY_BEYOND_STK_HORIZON
```

No se extrapola stock.

---

## 8. Fecha de entrega anterior a evaluation_date

ENT no convierte automáticamente una `expected_delivery_date < evaluation_date` en error, porque una fecha comprometida puede haber quedado vencida y seguir siendo evidencia histórica/relevante de un incumplimiento.

Pero para una propuesta de compra actual, dicha situación exige semántica/aplicabilidad suficiente del origen.

Si la evidencia no demuestra por qué una fecha pasada sigue siendo la fecha aplicable a la propuesta evaluada:

```text
NOT_DETERMINABLE
+ PAST_DELIVERY_DATE_APPLICABILITY_UNPROVEN
```

No se corrige la fecha al presente ni se deriva una nueva fecha.

---

## 9. No contradicción con Scenario Engine / Decision Twin

ENT no crea un modelo físico global de escenarios.

`BaselineStockoutQualification` es una interfaz especializada de consumo para una regla concreta, sustentada por referencias externas.

No redefine:

- ciclo de escenario;
- parent/child global;
- identidad de alternativa;
- persistencia;
- Scenario Engine;
- Decision Twin.

---

## 10. RDM

Una vez cerrada esta metodología, podrán documentarse como dependencias especializadas candidatas:

```text
R-ENT-001 → BaselineStockoutQualification
R-ENT-001 → PurchaseSpecificDeliveryTimingEvidence
```

Solo se incorporarán a la RDM cuando la auditoría final demuestre que la relación está suficientemente documentada.

No se inferirán Criticality, fallback ni Evaluability_Impact no autorizados.

---

## 11. Parámetros

No se requiere ni se crea `P-ENT-*`.

La comparación normativa es estrictamente:

```text
expected_delivery_date > depletion_date
```

con las salvaguardas de evidencia, baseline y horizonte descritas.

---

## 12. Invariantes

1. baseline sin compra es obligatorio;
2. scenario_id por sí solo no demuestra baseline;
3. ENT no crea `scenario_type`;
4. ENT no crea Purchase_ID;
5. STK conserva autoridad sobre depletion;
6. ENT no recalcula STK;
7. delivery date debe ser propuesta-específica;
8. Supplier DELIVERY_DATE no adquiere aplicabilidad automática;
9. lead time no se convierte internamente en fecha;
10. igualdad de fecha no equivale a “posterior”;
11. igualdad no demuestra orden intradía;
12. NOT_APPLICABLE solo vale dentro del horizonte evidenciado;
13. no se extrapola más allá del horizonte;
14. ausencia != puntualidad;
15. contradicción no se resuelve por selección arbitraria;
16. ENT no produce NEGOCIAR ni Assessment.

---

## 13. Criterio de cierre

Audit 2 deberá confirmar:

- representabilidad sin inventar identidad global;
- baseline/exclusión demostrables por refs;
- propuesta-especificidad de delivery;
- algoritmo temporal sin circularidad;
- estados de incertidumbre conservadores;
- compatibilidad con STK/Supplier/Scenario Engine/Decision Twin;
- relación RDM suficientemente demostrada;
- 0 parámetros inventados;
- 0 autoridad decisional nueva.

---

## 14. Estado

**ENT v0.2 — DEPURADO.**  
**Pendiente:** AUDIT 2.  
**Implementación:** NO AUTORIZADA.  
**Nuevas identidades canónicas:** 0.  
**Nuevos parámetros:** 0.
