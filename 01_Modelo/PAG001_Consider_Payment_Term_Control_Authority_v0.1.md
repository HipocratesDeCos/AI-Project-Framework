# EIOS — PAG001 Consider Payment-Term Control Authority v0.1

**Baseline de autorización:** `main @ 36ff1a44348b21293285270db887b293a44de1d3`  
**Fecha:** 22/09/2026  
**Estado:** AUTORIZADO Y CORREGIDO  
**Ámbito:** semántica de `P-PAG-004` como control funcional de `R-PAG-001`.

## 1. Autoridad humana explícita

Se autoriza la propuesta de control funcional de `P-PAG-004`, con las correcciones de trazabilidad y diferenciación de causas descritas en este documento.

## 2. Semántica autorizada

```text
P-PAG-004 = Sí → ENABLED
P-PAG-004 = No → DISABLED
```

### ENABLED

```text
control_state = ENABLED
```

El control habilita que la evaluación de `R-PAG-001` continúe hacia el carrier de plazo y el umbral efectivo.

ENABLED no determina TRUE/FALSE por sí mismo.

### DISABLED

```text
control_state = DISABLED
R-PAG-001 → NOT_EVALUABLE
reason_code = PAYMENT_TERM_CRITERION_DISABLED
```

DISABLED representa una exclusión voluntaria del criterio de plazo por política/configuración válida.

No equivale a FALSE.

## 3. Corrección — exclusión voluntaria ≠ fallo de configuración

Se distinguen expresamente:

### 3.1 Criterio deshabilitado por política válida

```text
state = DISABLED
reason_code = PAYMENT_TERM_CRITERION_DISABLED
```

La configuración existe, está vigente, evidenciada y contiene `No`.

### 3.2 Configuración ausente

```text
state = NOT_EVALUABLE
reason_code = MISSING_CONTROL_CONFIGURATION
```

### 3.3 Configuración inválida

```text
state = NOT_EVALUABLE
reason_code = INVALID_CONTROL_CONFIGURATION
```

### 3.4 Evidencia inválida

```text
state = NOT_EVALUABLE
reason_code = INVALID_CONTROL_EVIDENCE
```

Estas causas no deben colapsarse en un único “disabled”.

## 4. Valores canónicos

Se admiten exclusivamente:

```text
Sí
No
```

No se autorizan aliases automáticos:

- true / false;
- 1 / 0;
- on / off;
- yes / no;
- texto libre;
- valor vacío.

## 5. Configuración y evidencia

La implementación debe consumir:

```text
ResolvedConfiguration(P-PAG-004)
+
ParameterConfigurationEvidence(P-PAG-004)
```

y verificar:

- `parameter_id == P-PAG-004`;
- `company_id == company_scope`;
- `parameters_version == DecisionContext.parameters_version`;
- `effective_at.date() == evaluation_date`;
- configuración vigente en `effective_at`;
- Evidence DEMONSTRATED;
- source_type exacto;
- captured_at == evaluation_date;
- demonstration_ref == resolved.configuration_ref.

## 6. Coherencia futura con el bundle PAG001

Cuando ENABLED se combine con `PaymentTermToleranceResolution`, deberá existir coherencia del mismo contexto efectivo de configuración.

Esta autoridad no materializa todavía ese bundle conjunto.

## 7. Prioridad futura de R-PAG-001

```text
1. validar identidad/contexto;
2. resolver P-PAG-004;
3. DISABLED → NOT_EVALUABLE / PAYMENT_TERM_CRITERION_DISABLED;
4. missing/invalid/evidence-invalid → NOT_EVALUABLE con razón propia;
5. ENABLED → continuar;
6. validar carrier y threshold;
7. comparar offered < effective_threshold.
```

No se exige carrier/threshold cuando el criterio está válidamente deshabilitado.

## 8. P-PAG-005

Fuera de alcance.

P-PAG-005 no puede reactivar un control DISABLED ni sustituir P-PAG-004.

## 9. R-PAG-002

Fuera de alcance de esta autoridad v0.1.

Aunque existe relación funcional documentada, no se extrapola automáticamente esta semántica a `R-PAG-002`.

## 10. No alcance

No autoriza todavía:

- implementación completa de `R-PAG-001`;
- semántica de `P-PAG-005`;
- `R-PAG-002`;
- normalización multicuota;
- decisiones CRC;
- valores alternativos de representación.

## 11. Gates

```text
PAG001-CTRL-G01 → CLOSED
PAG001-CTRL-G02 → CLOSED
PAG001-CTRL-G03 → CLOSED
PAG001-CTRL-G04 → CLOSED
PAG001-CTRL-G05 → CLOSED
PAG001-CTRL-G06 → CLOSED
PAG001-CTRL-G07 → CLOSED
PAG001-CTRL-G08 → policy-disabled ≠ config-failure
```

## 12. Estado

**PAG001 Consider Payment-Term Control Authority v0.1 — AUTORIZADO Y CORREGIDO.**
