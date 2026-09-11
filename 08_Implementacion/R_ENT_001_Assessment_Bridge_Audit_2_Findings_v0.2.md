# EIOS — R-ENT-001 · Assessment Bridge Audit 2 Findings v0.2

**Estado:** HALLAZGO BLOQUEANTE — CORRECCIÓN QUIRÚRGICA REQUERIDA  
**Fecha:** 11/09/2026  
**Objeto:** `R_ENT_001_Assessment_Bridge_Design_v0.2.md`

---

## 1. Dictamen

Los tres blockers de Audit 1 están resueltos.

Se identifica un único blocker residual de integridad entre `analysis_input` y `analysis`.

**Blockers Audit 2:** 1.  
**Política empresarial nueva:** 0.

---

## 2. ENT-A2-B01 — factual copy integrity incompleta

El diseño v0.2 comprueba IDs y `baseline_projection_ref`, pero no exige que las fechas factuales publicadas por el resultado ENT coincidan exactamente con las fuentes contenidas en `DeliveryStockoutAnalysisInput`.

Un caller podría presentar, por error o manipulación:

```text
analysis.expected_delivery_date != analysis_input.delivery.expected_delivery_date
```

o:

```text
analysis.depletion_date != analysis_input.baseline.projection.depletion_date.value
```

manteniendo compatibles los demás identificadores.

Eso permitiría evaluar `R-ENT-001` sobre un resultado cuya provenance role-specific no corresponde a los valores temporales publicados.

---

## 3. Corrección requerida

Añadir precondiciones estructurales, sin recalcular ENT:

```text
analysis.expected_delivery_date
== analysis_input.delivery.expected_delivery_date

analysis.depletion_date
== analysis_input.baseline.projection.depletion_date.value

analysis.horizon_end
== analysis_input.baseline.projection.horizon.horizon_end
```

Estas igualdades no reproducen la lógica del analyzer; verifican únicamente que el resultado consume/copió las mismas salidas factuales que el input de provenance presentado al bridge.

---

## 4. Resto de Audit 2

### Mapeo ENT → Assessment

SUPERADO.

### GAP / INVALID → no FALSE

SUPERADO.

### NOT_LATE_WITHIN_EVIDENCED_HORIZON → FALSE

SUPERADO, con reason explícitamente limitado al horizonte evidenciado.

### Evidence role binding

SUPERADO tras Audit 1: los roles son separados y `demonstration_ref` se valida contra refs de su dependencia original, no contra el agregado ENT.

### Purchase / Context / Rule identity

SUPERADO.

### Frontera Rules vs ENT

SUPERADO: no se invoca el engine ENT desde Rules.

### RDM

SUPERADO: no se modifican atributos `PENDING` ni se infiere COMPONENT.

---

## 5. Estado

**AUDIT 2: NO CERRABLE todavía por ENT-A2-B01.**

Procede corrección v0.2.1 y Audit 2 Final.
