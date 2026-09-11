# EIOS — ENTREGA / R-ENT-001 · METHODOLOGICAL DESIGN v0.1

**Estado:** DISEÑO INICIAL — PENDIENTE DE AUDIT 1  
**Fecha:** 11/09/2026  
**Baseline:** `main @ ab922bed82fb63af509c033d69fd62a178b8d058`  
**Rama:** `ent/delivery-stockout-methodology-v0.1`

---

## 1. Propósito

Definir la metodología factual mínima que permita sostener `R-ENT-001 — Entrega posterior al riesgo de rotura` sin recalcular STK, inventar una fecha de entrega, derivar lead time implícitamente ni producir una decisión empresarial.

La regla vigente establece:

> La fecha prevista de entrega es posterior a la fecha estimada de agotamiento del stock.

Resultado de regla: `NEGOCIAR`, efecto/severidad `R2 / ALTA`.

ENT no produce ese resultado; entrega únicamente la relación temporal factual necesaria para que Rules pueda evaluar la condición.

---

## 2. Separación de autoridad

### STK

STK conserva autoridad sobre:

- proyección de stock;
- horizonte;
- `depletion_date`;
- movimientos M05/M06;
- estados de insuficiencia/contradicción.

ENT no recalcula `depletion_date`.

### Evidencia de entrega

La fecha prevista de entrega debe proceder de evidencia temporal autorizada y aplicable a la propuesta evaluada.

ENT no decide qué fuente empresarial crea el compromiso de entrega.

### Rules

`R-ENT-001` conserva la condición y el resultado `NEGOCIAR`.

### CRC / humano

ENT no consolida reglas, no recomienda por sí mismo y no ejecuta acciones.

---

## 3. Salvaguarda de escenario base

La arquitectura Capa 3 establece:

> compra comparada contra escenario base sin compra.

STK físico permite movimientos `PROPOSED_PURCHASE`, que pueden elevar el stock proyectado y retrasar/eliminar el agotamiento.

Por tanto, para `R-ENT-001`:

```text
stockout timing source = BASE SCENARIO WITHOUT THE PROPOSED PURCHASE BEING EVALUATED
```

### Invariante ENT-BASE-01

No puede utilizarse como evidencia de agotamiento una proyección cuyo `depletion_date` haya sido calculado incluyendo la entrada de la misma compra propuesta cuya fecha de llegada se está evaluando.

Hacerlo produciría circularidad/automascaramiento:

```text
purchase inflow included
→ depletion delayed/removed
→ delivery appears not late
```

### Gap de representabilidad

`StockProjectionResult` no conserva por sí solo la colección de movimientos que originó la proyección.

Por ello el futuro contrato ENT deberá recibir o referenciar provenance suficiente que demuestre que el resultado procede del escenario base sin esa compra.

ENT no modifica `StockProjectionResult` para resolver este gap.

---

## 4. StockoutTimingEvidence conceptual

```text
StockoutTimingEvidence
├── decision_id
├── base_scenario_id
├── article_id
├── evaluation_date
├── depletion_state
├── depletion_date: date | null
├── horizon_end
├── projection_result_ref
├── projection_input_or_provenance_ref
├── evaluated_purchase_ref
├── proposed_purchase_exclusion_ref
├── issue_refs
└── trace_refs
```

### Requisitos

1. identidad/artículo compatibles con la evaluación;
2. `projection_result_ref` identifica el resultado STK consumido;
3. provenance demuestra que la compra evaluada no contribuyó como `PROPOSED_PURCHASE`;
4. el horizonte y `depletion_state` se copian/conservan de STK, no se reinterpretan;
5. incidencias/trazas STK relevantes se preservan.

Los nombres físicos quedan para contrato posterior.

---

## 5. DeliveryTimingEvidence conceptual

```text
DeliveryTimingEvidence
├── decision_id
├── scenario_id
├── article_id
├── supplier_id
├── evaluated_purchase_ref
├── expected_delivery_date: date | null
├── state
├── semantic_ref
├── applicability_ref
├── source_ref
├── evidence_refs
├── captured_at
├── valid_from / valid_to
├── issue_refs
└── trace_refs
```

### Estados conceptuales

```text
KNOWN
NOT_EVIDENCED
CONFLICTING_DATA
NOT_DETERMINABLE
```

### KNOWN exige

- fecha explícita;
- fuente/evidencia/traza;
- semántica de la fecha;
- aplicabilidad a la propuesta evaluada;
- captura no posterior a `evaluation_date`;
- identidad de artículo/proveedor compatible;
- ausencia de contradicción no resuelta.

---

## 6. Lead time no equivale a expected delivery date

ENT no ejecuta por sí mismo:

```text
operation_date + lead_time
expected_delivery_date = evaluation_date + lead_time
```

porque ello exigiría autoridad sobre:

- fecha de anclaje;
- días naturales/laborables;
- calendario/feriados/cut-off;
- unidad de lead time;
- vigencia y aplicabilidad del plazo;
- tratamiento de cambios/confirmaciones.

Si una autoridad externa ya ha producido una fecha de entrega trazable a partir de lead time, ENT puede consumir **la fecha resultante evidenciada**, no recrear la transformación.

---

## 7. Supplier Evidence como posible fuente, no como autoridad automática

Supplier Evidence Core dispone de dimensión `DELIVERY_DATE` y puede conservar observaciones DATE trazables.

No toda observación `DELIVERY_DATE` es automáticamente la fecha prevista de la compra concreta.

Para ser consumible por ENT debe demostrarse, como mínimo:

```text
semantic_ref → expected delivery/receipt date
applicability → evaluated purchase
supplier/article identity → compatible
state → KNOWN
```

ENT puede usar un adaptador autorizado; no acopla metodológicamente `R-ENT-001` a Supplier Evidence por nombre de dimensión.

---

## 8. Relación temporal factual

Estados conceptuales del análisis ENT:

```text
LATE_DELIVERY_DEMONSTRATED
NOT_LATE_DEMONSTRATED
NOT_LATE_WITHIN_EVIDENCED_HORIZON
NOT_EVIDENCED
CONFLICTING_DATA
NOT_DETERMINABLE
```

### Caso A — depletion_date KNOWN

Con `expected_delivery_date` KNOWN:

```text
expected_delivery_date > depletion_date
→ LATE_DELIVERY_DEMONSTRATED

expected_delivery_date <= depletion_date
→ NOT_LATE_DEMONSTRATED
```

La comparación es estricta porque la regla utiliza “posterior”.

### Igualdad de fecha

```text
expected_delivery_date == depletion_date
```

no satisface la condición estricta “posterior” a granularidad de fecha.

ENT deberá conservar una limitación de granularidad cuando no exista orden intradía autorizado. No afirmará que la recepción evita físicamente la rotura dentro de ese día; solo que la fecha no es posterior.

---

## 9. Depletion NOT_APPLICABLE y horizonte

En STK, `depletion_date = NOT_APPLICABLE` significa:

> no se produjo agotamiento dentro del horizonte completamente determinado.

No significa “el artículo nunca se agotará”.

Por tanto:

### Entrega dentro del horizonte evidenciado

```text
STK depletion = NOT_APPLICABLE
AND expected_delivery_date <= horizon_end
→ NOT_LATE_WITHIN_EVIDENCED_HORIZON
```

La proyección demuestra que no hubo agotamiento anterior a la fecha de entrega dentro del periodo cubierto.

### Entrega posterior al horizonte

```text
STK depletion = NOT_APPLICABLE
AND expected_delivery_date > horizon_end
→ NOT_DETERMINABLE
```

No se extrapola el stock más allá del horizonte.

---

## 10. Propagación de incertidumbre

Si cualquiera de las dependencias materiales está:

- no evidenciada;
- en contradicción;
- no determinable;
- sin provenance del escenario base;

ENT no produce TRUE/FALSE concluyente para la condición temporal.

Ausencia ≠ entrega a tiempo.

Conflicto ≠ selección por fecha más reciente/más conservadora.

---

## 11. RDM

`R-ENT-001` no aparece actualmente en la RDM v1.4.

Antes de implementación deberán demostrarse y registrar, como mínimo, las relaciones:

```text
R-ENT-001 → StockoutTimingEvidence
R-ENT-001 → DeliveryTimingEvidence
```

La metodología especializada puede servir como evidencia documental para el futuro cruce, pero este diseño no modifica aún RDM.

---

## 12. Parámetros

La condición vigente es una comparación directa de fechas y no demuestra un umbral configurable adicional.

No se crea `P-ENT-*`.

PYE-004 no se convierte en parámetro consumidor de `R-ENT-001`: su autoridad actual no deriva fechas desde lead time.

---

## 13. Prohibiciones

ENT no puede:

- recalcular stock;
- calcular demanda;
- crear `depletion_date`;
- incluir la compra evaluada en el escenario base;
- inferir fecha desde lead time;
- elegir entre fechas contradictorias;
- extrapolar más allá del horizonte STK;
- convertir ausencia en puntualidad;
- producir `NEGOCIAR`;
- recomendar proveedor alternativo por sí mismo;
- ejecutar CRC;
- modificar C0, STK o Supplier.

---

## 14. Criterio de entrada a contrato técnico

Audit 1/2 deberán confirmar:

1. autoridad de escenario base sin compra;
2. provenance suficiente del resultado STK;
3. semántica de delivery date propuesta-específica;
4. comparación estricta de fechas;
5. tratamiento correcto de igualdad;
6. tratamiento de `NOT_APPLICABLE` limitado al horizonte;
7. propagación de estados;
8. no derivación implícita de lead time;
9. dependencias RDM demostrables;
10. ausencia de necesidad de un parámetro ENT inventado.

---

## 15. Estado

**ENT v0.1 — DISEÑO INICIAL.**  
**Implementación:** NO AUTORIZADA.  
**Nuevos parámetros:** 0.  
**Fórmulas empresariales nuevas:** 0.
