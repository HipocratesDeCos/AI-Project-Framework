# EIOS — PAG001 Payment-Term Tolerance Authority v0.1

**Baseline de autorización:** `main @ 4fd2c51c32400c7e986c4b9947dbe3e191667d03`  
**Fecha:** 22/09/2026  
**Estado:** AUTORIZADO Y CORREGIDO  
**Ámbito:** transformación exacta de `P-PAG-003` dentro de `R-PAG-001`.

## 1. Autoridad humana explícita

Se autoriza la propuesta de transformación de tolerancia de plazo, con las correcciones de coherencia y fail-closed descritas en este documento.

## 2. Fórmula autorizada

```text
effective_payment_term_threshold_days =
target_payment_term_days - tolerance_days
```

Evaluación:

```text
offered_payment_term_days < effective_payment_term_threshold_days
    → TRUE

offered_payment_term_days >= effective_payment_term_threshold_days
    → FALSE
```

La igualdad con el umbral no activa `R-PAG-001`.

## 3. Dominio autorizado

La transformación solo es evaluable cuando:

```text
target_payment_term_days >= 0
tolerance_days >= 0
tolerance_days <= target_payment_term_days
```

No se clampa, corrige, absolutiza ni normaliza silenciosamente ninguna configuración fuera de dominio.

## 4. Corrección — ausencia vs configuración inválida

Se distinguen explícitamente dos clases de fallo:

### 4.1 Parámetro no disponible / no demostrado

Si falta `P-PAG-002` o `P-PAG-003`, su evidencia o su resolución efectiva:

```text
NOT_EVALUABLE
reason = missing/not-demonstrated configuration
```

### 4.2 Parámetro presente pero inválido

Si los parámetros están demostrados pero:

- target < 0;
- tolerance < 0;
- tolerance > target;
- unidad incompatible;

```text
NOT_EVALUABLE
reason = invalid configuration domain
```

No se debe degradar un parámetro inválido a “ausente”.

## 5. Corrección — coherencia de configuración

`P-PAG-002` y `P-PAG-003` solo pueden combinarse cuando pertenecen al mismo contexto efectivo de configuración aplicable a la evaluación.

Deben coincidir, como mínimo, en:

- `company_scope`;
- `effective_date` aplicable;
- contexto/selección de configuración;
- versión/configuration identity pertinente;
- provenance demostrada por su `ParameterConfigurationEvidence`.

Si no existe coherencia demostrable:

```text
NOT_EVALUABLE
```

No se permite mezclar un target de una configuración con una tolerance de otra.

## 6. Unidades

Ambos parámetros deben resolverse explícitamente en días.

No se autorizan conversiones automáticas desde semanas, meses, años o texto.

## 7. Carrier factual

La futura regla utilizará:

```text
OfferedPaymentTermObservation.AVAILABLE
+
ResolvedConfiguration(P-PAG-002) + Evidence
+
ResolvedConfiguration(P-PAG-003) + Evidence
```

Si `OfferedPaymentTermObservation.state != AVAILABLE`:

```text
R-PAG-001 → NOT_EVALUABLE
```

## 8. Casos límite cerrados

### Tolerancia = 0

```text
threshold = target
```

Se recupera exactamente la condición base.

### Tolerancia = target

```text
threshold = 0
```

Todo plazo ofrecido no negativo produce FALSE.

### Tolerancia > target

```text
NOT_EVALUABLE
```

### Igualdad

```text
offered == threshold → FALSE
```

## 9. P-PAG-004

Fuera de alcance.

Esta autoridad no define aún el resultado técnico cuando “Considerar plazo” esté desactivado.

## 10. P-PAG-005

Fuera de alcance.

No altera target, tolerance ni threshold.

## 11. Multicuota

Fuera de alcance.

La fórmula solo consume el escalar ya canonizado `offered_payment_term_days`.

## 12. No alcance

No autoriza aún la regla completa `R-PAG-001`, `P-PAG-004`, `P-PAG-005`, `R-PAG-002`, valores empresariales concretos ni normalización multicuota.

## 13. Gates

```text
PAG001-TOL-G01 → CLOSED
PAG001-TOL-G02 → CLOSED
PAG001-TOL-G03 → CLOSED
PAG001-TOL-G04 → CLOSED
PAG001-TOL-G05 → CLOSED
PAG001-TOL-G06 → CLOSED
PAG001-TOL-G07 → missing config ≠ invalid config
PAG001-TOL-G08 → same effective configuration context required
```

## 14. Estado

**PAG001 Payment-Term Tolerance Authority v0.1 — AUTORIZADO Y CORREGIDO.**
