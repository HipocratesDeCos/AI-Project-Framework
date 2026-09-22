# EIOS — PAG001 Early-Payment Discount Control Authority v0.1

**Baseline de autorización:** `main @ 39c61b6f8185ba4441163e696c39631bb809abaf`  
**Fecha:** 22/09/2026  
**Estado:** AUTORIZADO Y CORREGIDO  
**Ámbito:** reconciliación semántica de `P-PAG-005` respecto de `R-PAG-001`.

## 1. Autoridad humana

Se autoriza la reconciliación de `P-PAG-005` como control funcional de consideración del descuento por pronto pago.

## 2. Semántica autorizada

```text
P-PAG-005 = Sí → EARLY_PAYMENT_DISCOUNT_CONTEXT_ENABLED
P-PAG-005 = No → EARLY_PAYMENT_DISCOUNT_CONTEXT_DISABLED
```

`P-PAG-005` no representa el valor económico del descuento.

No representa:

- porcentaje;
- importe;
- días;
- coste financiero;
- TAE;
- yield;
- coste efectivo.

## 3. Corrección — separación de planos

Se separan tres planos independientes:

### A. Control de consideración

```text
P-PAG-005
→ ENABLED / DISABLED
```

### B. Disponibilidad del contexto económico

```text
AVAILABLE
NOT_AVAILABLE
NOT_MATERIALIZED
INVALID
```

Este plano depende de una futura cadena factual/metodológica específica.

### C. Evaluabilidad de R-PAG-001

```text
offered_payment_term_days < effective_threshold_days
```

La evaluabilidad del comparador base de `R-PAG-001` no depende de A ni de B.

## 4. Consecuencia autorizada para R-PAG-001

`P-PAG-005` **no es prerequisito de evaluabilidad** del core de `R-PAG-001`.

Por tanto:

- P-PAG-005 ausente;
- P-PAG-005 inválido;
- P-PAG-005 sin Evidence;
- P-PAG-005 = No;
- P-PAG-005 = Sí pero sin cadena económica;

no deben convertir por sí solos el comparador de plazo en `NOT_EVALUABLE`.

## 5. P-PAG-005 = No

```text
discount_context_control = DISABLED
```

La evaluación de plazo continúa sin enriquecimiento económico.

No altera:

- offered_payment_term_days;
- target_days;
- tolerance_days;
- effective_threshold_days;
- comparator.

## 6. P-PAG-005 = Sí

```text
discount_context_control = ENABLED
```

Solo habilita considerar una futura cadena económica autorizada.

No implica que exista descuento ni permite inferirlo.

## 7. Corrección — control inválido no contamina el core

Si P-PAG-005 está ausente, inválido o con Evidence inválida:

```text
discount_context_control = NOT_EVALUABLE
```

con causa trazable propia.

Pero:

```text
R-PAG-001 core comparator
→ puede seguir evaluándose
```

si P-PAG-004 está ENABLED y carrier + threshold son evaluables.

## 8. Valores canónicos

Solo:

```text
Sí
No
```

No aliases automáticos.

## 9. Supplier Evidence Core

`COMMERCIAL_CONDITION` puede ser futura fuente factual, pero no demuestra por sí sola un descuento por pronto pago.

Será necesaria autoridad semántica específica para cualquier carrier de descuento.

## 10. Sin fórmula implícita

No se autoriza ningún cálculo económico.

## 11. R-PAG-002

Fuera de alcance.

## 12. Consecuencia arquitectónica

Con esta autoridad:

```text
P-PAG-005
≠ blocker del core R-PAG-001
```

Permanece abierto únicamente como enriquecimiento económico opcional y separado.

## 13. Gates

```text
PAG001-DISC-G01 → CLOSED
PAG001-DISC-G02 → CLOSED
PAG001-DISC-G03 → CLOSED
PAG001-DISC-G04 → CLOSED
PAG001-DISC-G05 → CLOSED
PAG001-DISC-G06 → CLOSED
PAG001-DISC-G07 → CLOSED
PAG001-DISC-G08 → invalid discount control ≠ non-evaluable R-PAG-001 core
```

## 14. Estado

**PAG001 Early-Payment Discount Control Authority v0.1 — AUTORIZADO Y CORREGIDO.**
