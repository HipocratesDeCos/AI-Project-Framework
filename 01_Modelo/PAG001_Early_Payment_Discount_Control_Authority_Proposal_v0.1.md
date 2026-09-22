# EIOS — PAG001 Early-Payment Discount Control Authority Proposal v0.1

**Baseline:** `main @ 39c61b6f8185ba4441163e696c39631bb809abaf`  
**Fecha:** 22/09/2026  
**Estado:** PROPUESTA — NO AUTORIZADA  
**Ámbito:** reconciliación semántica de `P-PAG-005` respecto de `R-PAG-001`.

## 1. Conflicto documental

Existen dos descripciones que no pueden interpretarse literalmente como una sola cosa:

### Catálogo de parámetros

```text
P-PAG-005
Considerar descuento por pronto pago
Valor inicial: Sí
Unidad: Sí/No
```

Esto define un control funcional booleano.

### Especificación PAG

`P-PAG-005` se describe como factor económico asociado al descuento por pronto pago y como entrada indirecta/derivada a un cálculo coste/beneficio.

Eso describe una función económica derivada, no un valor booleano de descuento.

## 2. Reconciliación propuesta

Se separan responsabilidades:

### P-PAG-005

```text
P-PAG-005 = control de consideración del descuento por pronto pago
Sí → EARLY_PAYMENT_DISCOUNT_CONTEXT_ENABLED
No → EARLY_PAYMENT_DISCOUNT_CONTEXT_DISABLED
```

P-PAG-005 **no representa**:

- porcentaje de descuento;
- importe del descuento;
- días de pronto pago;
- coste financiero;
- TAE;
- coste efectivo;
- beneficio económico.

### Dato económico real

Cualquier descuento aplicable deberá provenir de una fuente factual separada y semánticamente autorizada.

Supplier Evidence Core puede conservar `COMMERCIAL_CONDITION`, pero esta dimensión genérica por sí sola no demuestra:

- que la condición sea un descuento por pronto pago;
- su porcentaje;
- su base de cálculo;
- su ventana temporal;
- su aplicabilidad a la compra exacta.

## 3. Efecto sobre R-PAG-001

La condición autorizada de `R-PAG-001` sigue siendo:

```text
offered_payment_term_days < effective_threshold_days
```

Por tanto:

`P-PAG-005` **no es prerequisito para determinar TRUE/FALSE de R-PAG-001**.

La ausencia, desactivación o falta de materialización del contexto económico de pronto pago no debe convertir por sí sola R-PAG-001 en NOT_EVALUABLE.

## 4. P-PAG-005 = No

Si `P-PAG-005 = No` y la configuración/evidencia es válida:

```text
early_payment_discount_context = DISABLED
```

La evaluación de plazo de `R-PAG-001` continúa sin enriquecimiento económico de pronto pago.

No se cambia:

- offered_payment_term_days;
- P-PAG-002;
- P-PAG-003;
- effective_threshold_days;
- comparador de plazo.

## 5. P-PAG-005 = Sí

Si `P-PAG-005 = Sí` y la configuración/evidencia es válida:

```text
early_payment_discount_context = ENABLED
```

Esto solo autoriza **considerar** un futuro contexto económico si existe una cadena adicional autorizada.

No autoriza por sí mismo calcular ni inferir ningún descuento.

Si no existe aún esa cadena económica:

```text
R-PAG-001 sigue siendo evaluable por plazo
economic_discount_context = NOT_AVAILABLE / NOT_MATERIALIZED
```

## 6. Sin fórmula económica implícita

No se autoriza:

```text
discount_pct
discount_amount
effective_cost
annualized_cost
cash_discount_yield
payment-term-equivalent
```

ni ninguna otra transformación económica.

La especificación “cálculo coste/beneficio” se conserva como capacidad futura condicionada a una autoridad específica.

## 7. Supplier Evidence Core

`COMMERCIAL_CONDITION` puede actuar como fuente factual potencial futura, pero requiere un adapter/semantic authority específico para “early payment discount”.

No se interpreta texto libre ni semantic_ref genérico como autoridad suficiente.

## 8. Valores canónicos de P-PAG-005

Se propone el mismo criterio estricto usado en P-PAG-004:

```text
Sí → ENABLED
No → DISABLED
```

No se admiten aliases automáticos:

- true/false;
- 1/0;
- yes/no;
- on/off.

Configuración ausente, inválida o evidencia inválida se mantienen trazables, pero **no bloquean el comparador puro de R-PAG-001** mientras el control P-PAG-004 esté ENABLED y carrier/threshold sean evaluables.

## 9. Separación de resultados

La futura ejecución completa podrá producir separadamente:

```text
payment_term_assessment
early_payment_discount_context
```

El segundo no reescribe el primero.

## 10. R-PAG-002

Fuera de alcance.

No se extrapola automáticamente esta semántica a la viabilidad financiera/condicionada de R-PAG-002.

## 11. Consecuencia arquitectónica propuesta

Con esta reconciliación, `P-PAG-005` deja de ser un bloqueo para materializar el **núcleo ejecutable de R-PAG-001**.

Permanecerá abierto únicamente el enriquecimiento económico de pronto pago.

## 12. Gates propuestos

```text
PAG001-DISC-G01 → P-PAG-005 es control Sí/No, no valor económico
PAG001-DISC-G02 → Sí habilita contexto; No lo excluye
PAG001-DISC-G03 → P-PAG-005 no altera threshold ni comparator
PAG001-DISC-G04 → P-PAG-005 no es requisito de evaluabilidad del core R-PAG-001
PAG001-DISC-G05 → sin fórmula de coste/beneficio implícita
PAG001-DISC-G06 → COMMERCIAL_CONDITION requiere autoridad semántica específica
PAG001-DISC-G07 → R-PAG-002 fuera de alcance
```

## 13. Estado

**PAG001 Early-Payment Discount Control Authority v0.1 — PROPUESTA / NO AUTORIZADA.**
