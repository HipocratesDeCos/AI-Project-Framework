# EIOS — PAG001 Payment-Term Tolerance Authority Proposal v0.1

**Baseline:** `main @ 4fd2c51c32400c7e986c4b9947dbe3e191667d03`  
**Fecha:** 22/09/2026  
**Estado:** PROPUESTA — NO AUTORIZADA  
**Ámbito:** transformación exacta de `P-PAG-003` dentro de `R-PAG-001`.

## 1. Problema

La autoridad vigente establece:

- `P-PAG-002` = plazo objetivo;
- `P-PAG-003` = tolerancia de plazo;
- `P-PAG-003 → R-PAG-001` = relación derivada;
- la tolerancia modula la evaluación alrededor del objetivo.

No existe todavía fórmula autorizada.

## 2. Política propuesta

Definir el umbral efectivo de activación como:

```text
effective_payment_term_threshold_days =
target_payment_term_days - tolerance_days
```

y evaluar:

```text
offered_payment_term_days < effective_payment_term_threshold_days
    → R-PAG-001 TRUE
offered_payment_term_days >= effective_payment_term_threshold_days
    → R-PAG-001 FALSE
```

## 3. Semántica

La tolerancia representa una desviación desfavorable permitida respecto al objetivo.

Ejemplo puramente ilustrativo, no validación de valores empresariales:

```text
objetivo    = 90 días
tolerancia  = 15 días
umbral      = 75 días

oferta 74   → TRUE
oferta 75   → FALSE
oferta 90   → FALSE
```

La igualdad con el umbral queda dentro de la tolerancia y no activa negociación por esta regla.

## 4. Restricciones de dominio

Para que la transformación sea evaluable:

```text
target_payment_term_days >= 0
tolerance_days >= 0
tolerance_days <= target_payment_term_days
```

Si no se cumplen:

```text
NOT_EVALUABLE
```

No se clampa el umbral a cero.

No se usa valor absoluto.

No se invierte el signo.

## 5. Unidades

`P-PAG-002` y `P-PAG-003` deben resolverse en días.

No se autorizan conversiones automáticas desde:

- semanas;
- meses;
- años;
- textos.

Una unidad incompatible produce `NOT_EVALUABLE`.

## 6. Configuración

La futura implementación deberá consumir:

```text
ResolvedConfiguration(P-PAG-002)
+ ParameterConfigurationEvidence(P-PAG-002)
+ ResolvedConfiguration(P-PAG-003)
+ ParameterConfigurationEvidence(P-PAG-003)
```

sobre el mismo:

- company_scope;
- effective_date;
- selected configuration context aplicable.

No se hardcodean los valores iniciales del catálogo.

## 7. Relación con el carrier factual

La condición futura combinará:

```text
OfferedPaymentTermObservation.AVAILABLE
+
P-PAG-002
+
P-PAG-003
```

Esta autoridad no modifica `OfferedPaymentTermObservation`.

Si el carrier no está AVAILABLE:

```text
R-PAG-001 → NOT_EVALUABLE
```

cuando llegue a materializarse la regla completa.

## 8. P-PAG-004

Fuera de esta autoridad.

No se decide aquí si `P-PAG-004 = No` produce:

- NOT_EVALUABLE;
- SKIPPED;
- otro estado de control.

Eso requiere cierre específico de control funcional.

## 9. P-PAG-005

Fuera de esta autoridad.

No se autoriza usar descuento por pronto pago para:

- alterar el objetivo;
- alterar la tolerancia;
- recalcular días;
- neutralizar R-PAG-001.

Su cálculo económico permanece separado.

## 10. Multicuota

Fuera de alcance.

La fórmula solo consume un `offered_payment_term_days` ya canonizado.

No reduce vencimientos múltiples a un escalar.

## 11. Casos límite

### Tolerancia cero

```text
threshold = target
```

Se recupera la condición base:

```text
offered < target
```

### Tolerancia igual al objetivo

```text
threshold = 0
```

Todo plazo no negativo resulta FALSE.

Se permite como configuración formal, aunque su valor empresarial siga sujeto a validación.

### Tolerancia mayor que objetivo

```text
NOT_EVALUABLE
```

### Valores negativos

```text
NOT_EVALUABLE
```

## 12. No alcance

No autoriza todavía:

- implementación completa de `R-PAG-001`;
- `P-PAG-004`;
- `P-PAG-005`;
- `R-PAG-002`;
- normalización multicuota;
- valores 90/15 como política empresarial definitiva;
- automatización de decisión.

## 13. Gates propuestos

```text
PAG001-TOL-G01 → fórmula target - tolerance autorizada
PAG001-TOL-G02 → igualdad con umbral no activa
PAG001-TOL-G03 → tolerance > target → NOT_EVALUABLE
PAG001-TOL-G04 → unidades homogéneas en días
PAG001-TOL-G05 → configuración provenance-safe
PAG001-TOL-G06 → P-PAG-004/005 fuera de alcance
```

## 14. Estado

**PAG001 Payment-Term Tolerance Authority v0.1 — PROPUESTA / NO AUTORIZADA.**
