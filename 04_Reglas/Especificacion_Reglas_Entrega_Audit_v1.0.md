# EIOS — R-ENT-001 · AUDITORÍA DE CRUCE RULES ↔ RDM v1.0

**Estado:** SUPERADA — APTO PARA MATERIALIZAR EN RDM  
**Fecha:** 11/09/2026

---

## 1. Fuentes contrastadas

- `04_Reglas/Matriz_Reglas_MVP.md` v2.1;
- `04_Reglas/Rule_Dependency_Matrix.md` v1.4;
- `04_Reglas/Evidence_Contract.md`;
- `04_Reglas/Especificacion_Reglas_Entrega_MVP.md` v1.0;
- `01_Modelo/Delivery_Stockout_Methodological_Closure_v0.3.md`;
- Architecture Blueprint;
- STK implementation contract/runtime;
- Supplier Evidence Core;
- Scenario Engine / Decision Twin boundaries.

---

## 2. Regla

`R-ENT-001` existe en la Matriz de Reglas con condición explícita:

> fecha prevista de entrega posterior a fecha estimada de agotamiento.

La especificación especializada no cambia condición, resultado, efecto ni severidad.

**Resultado:** LIMPIO.

---

## 3. Dependencia BSQ

Relación propuesta:

```text
R-ENT-001 → BaselineStockoutQualification
```

La relación está demostrada porque la regla necesita la fecha de agotamiento y la autoridad arquitectónica exige comparar la compra contra escenario base sin compra.

Clasificación `EVIDENCE` es adecuada: el objeto no es un parámetro y la dependencia no exige declarar STK como COMPONENT.

**Resultado:** CONFIRMABLE.

---

## 4. Dependencia DTE

Relación propuesta:

```text
R-ENT-001 → PurchaseSpecificDeliveryTimingEvidence
```

La regla necesita una fecha prevista de entrega aplicable a la propuesta concreta. La metodología cerrada demuestra sus requisitos de semántica/aplicabilidad.

Clasificación `EVIDENCE` es adecuada.

**Resultado:** CONFIRMABLE.

---

## 5. Criticality

No existe autoridad suficiente para asignar `CRITICAL/HIGH/MEDIUM/LOW` a ninguna de las dos dependencias sin extrapolar la severidad R2/ALTA de la regla.

La RDM prohíbe esa extrapolación.

**Valor correcto:** `PENDING`.

---

## 6. Evaluability_Impact

La metodología ENT define estados analíticos conservadores, pero no constituye por sí sola una política general de impacto RDM equivalente a `BLOCKED`, `INSUFFICIENT_DATA` o `WARNING`.

**Valor correcto:** `PENDING`.

---

## 7. Fallback

No existe sustitución autorizada:

- no derivación lead time → date;
- no fecha por defecto;
- no uso de operation_date;
- no selección arbitraria entre fechas.

**Valor correcto:** `NONE`.

---

## 8. COMPONENT

No se demuestra dependencia COMPONENT directa a STK o Supplier:

- STK puede ser productor de una evidencia;
- Supplier puede ser una fuente adaptada de delivery date;
- ninguna fuente concreta es obligatoria como servicio exclusivo de la regla.

Crear `COMPONENT` sería inferencia prohibida.

**Valor correcto:** `Affected_Component = NONE`; no crear registros COMPONENT.

---

## 9. PARAMETER

No existe umbral configurable propio de `R-ENT-001`.

No crear `P-ENT-*` ni relación directa con `P-PYE-004`.

**Resultado:** LIMPIO.

---

## 10. Identificadores propuestos

```text
DEP-ENT-BSQ-RENT-001
DEP-ENT-DTE-RENT-001
```

Son únicos respecto de la cobertura actual y expresan dominio/fuente/regla sin introducir identidad empresarial.

---

## 11. Dictamen

**AUDITORÍA SUPERADA.**

Autorizado documentalmente para materialización en RDM:

- 2 registros `EVIDENCE / CONFIRMED`;
- `Criticality=PENDING`;
- `Evaluability_Impact=PENDING`;
- `Fallback=NONE`;
- `Affected_Component=NONE`.

No se autoriza ningún otro cruce ENT.
