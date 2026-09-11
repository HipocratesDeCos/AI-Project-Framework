# EIOS — ENTREGA / R-ENT-001 · METHODOLOGICAL AUDIT 2 v0.2

**Estado:** AUDIT 2 — 1 HALLAZGO CORRECTIVO  
**Fecha:** 11/09/2026  
**Objeto:** `Delivery_Stockout_Methodological_Design_v0.2.md`

---

## 1. Dictamen general

La depuración v0.2 resuelve correctamente los hallazgos de Audit 1 sobre:

- baseline sin compra;
- semántica insuficiente de `Scenario_ID`;
- aplicabilidad propuesta-específica de delivery date;
- no creación de identidades globales;
- no derivación implícita de lead time;
- horizonte STK;
- igualdad a granularidad DATE.

Se identifica un único hallazgo de determinismo antes del cierre.

---

## 2. ENT-A2-01 — Mapeo ambiguo de `depletion_state = UNKNOWN`

El diseño v0.2 establece:

```text
UNKNOWN → NOT_EVIDENCED o NOT_DETERMINABLE conforme a la causa preservada por STK/provenance
```

Esta formulación deja a ENT una responsabilidad interpretativa no cerrada.

STK ya conserva sus causas mediante estados, unresolved/conflicting items y limitaciones. ENT no debe reclasificar causalmente un `UNKNOWN` como ausencia de evidencia o indeterminación mediante heurística propia.

### Corrección obligatoria

El mapeo ENT debe ser determinista:

```text
STK depletion_state = UNKNOWN
→ ENT temporal relation = NOT_DETERMINABLE
```

preservando:

- unresolved items;
- limitations;
- issue/trace refs;
- provenance relevante.

La causa original puede explicarse, pero no cambia el estado ENT por inferencia.

Si una entrada `DeliveryTimingEvidence` está explícitamente `NOT_EVIDENCED`, ese estado sí puede conservarse como `NOT_EVIDENCED` porque procede de su propio contrato de entrada, no de una interpretación de STK.

---

## 3. Verificaciones superadas

### Baseline

SUPERADA.

`baseline_relation_ref` + `projection_provenance_ref` + `proposed_purchase_exclusion_ref` sustituyen correctamente la semántica insuficiente de un simple `scenario_id`.

### Scenario Engine / Decision Twin

SUPERADA.

No se crean `scenario_type`, `parent_scenario_id`, `Alternative_ID` ni otra identidad canónica.

### Delivery applicability

SUPERADA.

La fecha requiere `purchase_applicability_ref`; Supplier `DELIVERY_DATE` no se eleva automáticamente a fecha de la propuesta.

### Lead time

SUPERADA.

No existe derivación interna.

### Comparación temporal

SUPERADA.

La condición normativa se conserva como comparación estricta `delivery > depletion`.

### Igualdad

SUPERADA.

No satisface “posterior”, pero conserva limitación intradía.

### Horizonte

SUPERADA.

`NOT_APPLICABLE` no se extrapola más allá de `horizon_end`.

### Parámetros

SUPERADA.

No se crea `P-ENT-*` ni se reutiliza PYE-004 como consumidor directo.

### Decisión

SUPERADA.

ENT no produce `NEGOCIAR`, Assessment, CRC ni decisión.

---

## 4. Dictamen

**AUDIT 2 v0.2: NO SUPERADA — 1 HALLAZGO CORRECTIVO.**

Único hallazgo:

`ENT-A2-01 — hacer determinista el mapeo de depletion UNKNOWN → ENT NOT_DETERMINABLE.`

Debe emitirse v0.3 y repetir Audit 2 final.
