# EIOS — SUPPLIER EVIDENCE CORE · IMPLEMENTATION CONTRACT AUDIT 2 FINDINGS v0.2

**Estado:** COMPLETADA — DEPURACIÓN FINAL REQUERIDA  
**Fecha:** 11/09/2026  
**Objeto:** `Supplier_Evidence_Core_Implementation_Contract_v0.2.md`

---

## 1. Dictamen

v0.2 resuelve correctamente los siete hallazgos de Audit 1, pero Audit 2 identifica **cinco bloqueos técnicos finales** antes de implementación.

No requieren nueva política empresarial.

---

## 2. Verificación Audit 1

Quedan resueltos:

- A1-01 SupplierDataIssueRef común;
- A1-02 REFERENCE_ONLY con evidencia mínima;
- A1-03 propiedad estricta de observaciones;
- A1-04 coherencia temporal;
- A1-05 data_state separado de usage_state en métricas;
- A1-06 vigencia explícita;
- A1-07 metodología fija a v0.3.

---

## 3. Nuevos hallazgos

### PROV-TC-A2-01 — PRICE_REFERENCE podría reimplementar comparabilidad PRICE

La regla genérica de §23 declara `STRUCTURALLY_COMPARABLE` por coincidencia de dimensión, value_kind, semantic_ref, object y unit.

Para `PRICE_REFERENCE`, esto podría ignorar criterios de comparabilidad ya gobernados por PRICE, como condiciones, normalización o contexto económico.

**Riesgo:** Supplier Evidence Core se convierte en una segunda autoridad de comparabilidad de precio.

**Corrección obligatoria:** `StructuralComparisonRequest` debe incorporar:

```text
comparison_authority_ref: str | None
```

Para `dimension = PRICE_REFERENCE`, no se podrá producir `STRUCTURALLY_COMPARABLE` sin una referencia explícita a autoridad/comparabilidad PRICE ya resuelta.

Sin esa referencia:

```text
state = UNKNOWN
limitation = PRICE_COMPARABILITY_AUTHORITY_REQUIRED
```

Supplier no interpreta el contenido de esa autoridad; solo exige y conserva la referencia.

---

### PROV-TC-A2-02 — Hechos históricos y señales carecen de captured_at

`event_date`/`observed_at` indican cuándo ocurrió el hecho, pero no cuándo la evidencia estuvo disponible para EIOS.

Esto impide garantizar reproducibilidad temporal del snapshot.

**Corrección obligatoria:** añadir `captured_at` a:

- SupplierHistoricalFact;
- SupplierSignal.

Y exigir:

```text
captured_at <= evaluation_date
```

además de:

```text
event_date <= evaluation_date
observed_at <= evaluation_date
```

---

### PROV-TC-A2-03 — Hechos/métricas/señales de proveedores ajenos al conjunto pueden colarse

v0.2 valida propiedad de observaciones, pero no restringe `supplier_id` de:

- historical_facts;
- external_metrics;
- signals.

**Riesgo:** incorporar datos de proveedores no relacionados con el proveedor actual ni con candidatos de la operación.

**Corrección obligatoria:** todo `supplier_id` de hechos/métricas/señales debe pertenecer al conjunto:

```text
{current_supplier_id} ∪ {candidate.supplier_id}
```

---

### PROV-TC-A2-04 — value_kind necesita reglas estrictas contra coerción y unidades ambiguas

Pydantic puede aceptar/coaccionar tipos compatibles si no se protege explícitamente.

El contrato debe impedir, por ejemplo:

- booleano tratado como entero;
- entero ocupando campo booleano por coerción;
- unidad en DATE/TEXT/BOOLEAN;
- incompatibilidad por una unidad ausente frente a otra presente.

**Corrección obligatoria:**

1. validar exactamente un campo de valor según `value_kind`;
2. `INTEGER` no acepta booleanos;
3. `BOOLEAN` requiere bool real;
4. `DATE`, `TEXT`, `BOOLEAN` requieren `unit = None`;
5. para DECIMAL/INTEGER, comparabilidad estructural requiere igualdad exacta de `unit`, incluyendo `None == None`;
6. no se realizan conversiones de unidad en Supplier Evidence Core.

---

### PROV-TC-A2-05 — Orden de salida/agregación no está definido

El contrato agrega `unresolved_items`, `conflicting_items`, evidence refs y limitations, pero no define orden reproducible.

**Riesgo:** misma entrada lógica con ejecución equivalente puede producir distinto orden y dificultar fingerprints/tests.

**Corrección obligatoria:**

- conservar orden de entrada para candidatos, observaciones, hechos, métricas, señales y comparison requests;
- agregados de referencias/limitations usar orden de primera aparición con deduplicación estable;
- no ordenar por score, valor, proveedor o prioridad implícita.

---

## 4. Decisión

**CONTRATO v0.2: NO CERRABLE TODAVÍA.**

Depurar a v0.3 exclusivamente con A2-01…A2-05 y ejecutar Audit 2 final.
