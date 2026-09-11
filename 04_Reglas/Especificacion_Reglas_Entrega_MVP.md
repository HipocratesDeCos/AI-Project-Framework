# EIOS — ESPECIFICACIÓN DE REGLA Y DEPENDENCIAS DE ENTREGA MVP

## R-ENT-001 — Entrega posterior al riesgo de rotura

**Versión:** 1.0  
**Estado:** CERRADA — EVIDENCIA ESPECIALIZADA PARA RDM  
**Fecha:** 11/09/2026  
**Autoridad de regla:** `04_Reglas/Matriz_Reglas_MVP.md` v2.1  
**Autoridad metodológica:** `01_Modelo/Delivery_Stockout_Methodological_Closure_v0.3.md`

---

## 1. Propósito

Formalizar exclusivamente las dependencias demostradas de `R-ENT-001` para permitir su incorporación trazable a `Rule_Dependency_Matrix.md`.

Este documento no redefine:

- condición de la regla;
- resultado `NEGOCIAR`;
- efecto/severidad;
- STK;
- Supplier Evidence;
- Scenario Engine;
- parámetros;
- Assessment;
- CRC;
- decisión humana.

---

## 2. Condición normativa preservada

La condición oficial permanece:

> La fecha prevista de entrega es posterior a la fecha estimada de agotamiento del stock.

La metodología especializada cierra la relación factual como:

```text
expected_delivery_date > depletion_date
→ LATE_DELIVERY_DEMONSTRATED
```

Rules conserva la autoridad para convertir el soporte factual legítimo en evaluación de `R-ENT-001`.

---

## 3. Dependencia ENT-D01 — BaselineStockoutQualification

### Relación

```text
R-ENT-001 → BaselineStockoutQualification
```

### Tipo primario propuesto para RDM

`EVIDENCE`

### Source_ID

`BaselineStockoutQualification`

### Source_Domain

`STK / ENT METHODOLOGY`

### Función

Demostrar el timing de agotamiento autorizado para la regla, procedente de una proyección STK cualificada como escenario base sin la compra propuesta evaluada.

### Contenido mínimo demostrado

- `decision_id`;
- artículo/contexto compatible;
- referencia al resultado STK;
- relación trazable de baseline;
- provenance de la proyección;
- prueba de exclusión de la compra propuesta;
- `depletion_state`;
- `depletion_date` cuando KNOWN;
- `horizon_end`;
- issues/limitations/traces relevantes.

### Evidencia documental

- `03_Arquitectura/Architecture_Blueprint.md` — compra comparada contra escenario base sin compra;
- `01_Modelo/Delivery_Stockout_Methodological_Closure_v0.3.md`;
- contrato/implementación STK vigente para `depletion_date`.

### Criticality

`PENDING`

No se infiere de la severidad R2/ALTA de la regla.

### Evaluability_Impact

`PENDING`

Aunque la metodología define estados de indeterminación, esta especificación no redefine globalmente el impacto RDM sin autoridad expresa adicional.

### Fallback

`NONE`

No existe sustitución autorizada de depletion timing.

### Affected_Component

`NONE`

No se infiere una dependencia `COMPONENT` adicional solo porque STK produzca el dato/evidencia.

---

## 4. Dependencia ENT-D02 — PurchaseSpecificDeliveryTimingEvidence

### Relación

```text
R-ENT-001 → PurchaseSpecificDeliveryTimingEvidence
```

### Tipo primario propuesto para RDM

`EVIDENCE`

### Source_ID

`PurchaseSpecificDeliveryTimingEvidence`

### Source_Domain

`DELIVERY / SUPPLIER EVIDENCE ADAPTER`

### Función

Demostrar una fecha prevista de entrega aplicable específicamente a la propuesta evaluada, con semántica, fuente, evidencia y trazabilidad suficientes.

### Contenido mínimo demostrado

- `decision_id`;
- artículo/proveedor compatibles;
- referencia trazable a la propuesta evaluada;
- `expected_delivery_date` cuando KNOWN;
- semántica de la fecha;
- aplicabilidad a la propuesta concreta;
- fuente/evidencia/captura;
- issues/traces relevantes.

### Fuente Supplier opcional

Una `SupplierObservation` con:

```text
dimension = DELIVERY_DATE
value_kind = DATE
```

puede alimentar esta evidencia mediante adaptación trazable, pero no constituye la dependencia completa por nombre o dimensión.

La aplicabilidad a la propuesta debe quedar demostrada externamente.

### Criticality

`PENDING`

### Evaluability_Impact

`PENDING`

### Fallback

`NONE`

No se autoriza derivar una fecha desde lead time como contingencia.

### Affected_Component

`NONE`

No se declara `Supplier` como dependencia COMPONENT porque la evidencia puede proceder de otra fuente autorizada.

---

## 5. Relaciones expresamente NO demostradas

No quedan demostradas como dependencias canónicas:

```text
R-ENT-001 → P-PYE-004
R-ENT-001 → lead_time bruto
R-ENT-001 → operation_date
R-ENT-001 → Supplier component
R-ENT-001 → STK component
R-ENT-001 → scenario_id como baseline
```

Razones:

- PYE-004 no autoriza derivación de fecha;
- lead time bruto requiere transformación no cerrada;
- `operation_date` no es fecha prevista de entrega;
- una fuente de evidencia no implica dependencia COMPONENT;
- `scenario_id` no contiene semántica suficiente de baseline.

---

## 6. Parámetros

`R-ENT-001` no demuestra necesidad de un umbral configurable adicional.

No se crea `P-ENT-*`.

La comparación temporal continúa siendo estrictamente:

```text
expected_delivery_date > depletion_date
```

---

## 7. Estados de evidencia y evaluación

La metodología ENT puede producir estados analíticos de soporte como:

- `LATE_DELIVERY_DEMONSTRATED`;
- `NOT_LATE_DEMONSTRATED`;
- `NOT_LATE_WITHIN_EVIDENCED_HORIZON`;
- `NOT_EVIDENCED`;
- `CONFLICTING_DATA`;
- `NOT_DETERMINABLE`.

Estos estados no sustituyen `Assessment`.

La RDM registra relaciones de dependencia, no resultados de regla.

---

## 8. Incorporación autorizable a RDM

Esta especificación demuestra exclusivamente la existencia de dos relaciones `EVIDENCE`:

```text
DEP-ENT-BSQ-RENT-001
DEP-ENT-DTE-RENT-001
```

con:

```text
Evidence_Status = CONFIRMED
Criticality = PENDING
Evaluability_Impact = PENDING
Fallback = NONE
Affected_Component = NONE
```

No se incorporará ningún tercer registro por inferencia.

---

## 9. Estado

**ESPECIFICACIÓN R-ENT-001 v1.0: CERRADA PARA MATERIALIZACIÓN DE DEPENDENCIAS RDM.**

Dependencias demostradas: 2.  
Parámetros nuevos: 0.  
Dependencias COMPONENT inferidas: 0.  
Fallbacks inventados: 0.
