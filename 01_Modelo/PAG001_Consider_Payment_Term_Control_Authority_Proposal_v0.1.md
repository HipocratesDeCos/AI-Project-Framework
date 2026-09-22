# EIOS — PAG001 Consider Payment-Term Control Authority Proposal v0.1

**Baseline:** `main @ 36ff1a44348b21293285270db887b293a44de1d3`  
**Fecha:** 22/09/2026  
**Estado:** PROPUESTA — NO AUTORIZADA  
**Ámbito:** semántica de `P-PAG-004` como control funcional de `R-PAG-001`.

## 1. Evidencia documental existente

La especificación PAG vigente establece:

- `P-PAG-004` = “Considerar plazo”;
- relación `P-PAG-004 → R-PAG-001` = CONTROL FUNCIONAL;
- cuando `P-PAG-004` esté desactivado, el plazo no se utilizará como criterio de la evaluación ordinaria;
- `P-PAG-004` no sustituye al umbral objetivo.

La relación está demostrada, pero falta cerrar el estado técnico resultante.

## 2. Semántica propuesta

### Control activado

Si `P-PAG-004 = Sí` y su configuración/evidencia es válida:

```text
payment_term_control = ENABLED
```

La evaluación de `R-PAG-001` puede continuar hacia:

```text
OfferedPaymentTermObservation
+
PaymentTermToleranceResolution
+
comparador de R-PAG-001
```

El control activado no determina TRUE ni FALSE por sí mismo.

### Control desactivado

Si `P-PAG-004 = No` y su configuración/evidencia es válida:

```text
payment_term_control = DISABLED
R-PAG-001 → NOT_EVALUABLE
reason = PAYMENT_TERM_CRITERION_DISABLED
```

No se autoriza convertir “desactivado” en:

- `FALSE`;
- `TRUE`;
- resultado `NEGOCIAR`;
- resultado `COMPRAR`;
- ausencia de evidencia.

La regla queda no evaluable porque el criterio de plazo ha sido excluido expresamente de esta evaluación ordinaria.

## 3. Razón de la elección NOT_EVALUABLE

`FALSE` significaría que la condición “plazo inferior al umbral” fue evaluada y no se cumplió.

Con `P-PAG-004 = No`, la condición no debe evaluarse.

Por tanto:

```text
DISABLED ≠ FALSE
DISABLED → NOT_EVALUABLE
```

Esto preserva la semántica de Assessment y evita introducir una falsa evidencia negativa.

## 4. Configuración válida

La futura implementación deberá consumir:

```text
ResolvedConfiguration(P-PAG-004)
+
ParameterConfigurationEvidence(P-PAG-004)
```

vinculadas a:

- `DecisionContext.parameters_version`;
- `company_scope`;
- `evaluation_date`;
- configuración vigente en el `effective_at` seleccionado.

## 5. Valores admitidos

`P-PAG-004` es un parámetro booleano funcional.

La autoridad propone admitir únicamente una representación canónica cerrada:

```text
Sí → ENABLED
No → DISABLED
```

No se interpretan automáticamente:

- true/false;
- 1/0;
- on/off;
- yes/no;
- texto libre;
- valores vacíos.

Cualquier representación distinta:

```text
NOT_EVALUABLE
reason = INVALID_CONTROL_CONFIGURATION
```

La futura implementación podrá introducir una representación técnica booleana interna solo después de validar exactamente el valor configurado autorizado.

## 6. Parámetro ausente o evidencia ausente

Si `P-PAG-004` no está resuelto o no existe su Evidence:

```text
NOT_EVALUABLE
reason = MISSING_CONTROL_CONFIGURATION
```

No se asume “Sí” por defecto.

## 7. Evidencia inválida

Si la evidencia:

- no es `ParameterConfigurationEvidence`;
- está en GAP;
- no referencia exactamente `resolved.configuration_ref`;
- no corresponde a evaluation_date;

entonces:

```text
NOT_EVALUABLE
reason = INVALID_CONTROL_EVIDENCE
```

## 8. Coherencia con P-PAG-002 / P-PAG-003

Cuando el control está ENABLED y la futura regla combine:

- `P-PAG-004`;
- `PaymentTermToleranceResolution`;

deberá existir coherencia del mismo contexto efectivo de configuración.

Esta propuesta no materializa aún ese bundle conjunto, pero prohíbe mezclar un control de una configuración con target/tolerance de otra.

## 9. Prioridad de evaluación propuesta

Para `R-PAG-001` futura:

```text
1. validar identidad/regla/contexto;
2. resolver P-PAG-004;
3. si DISABLED → NOT_EVALUABLE / CRITERION_DISABLED;
4. si control inválido/ausente → NOT_EVALUABLE;
5. solo si ENABLED, validar carrier y threshold;
6. comparar offered < effective_threshold.
```

Esto evita exigir datos de plazo cuando la propia política ha desactivado ese criterio.

## 10. P-PAG-005

Fuera de alcance.

`P-PAG-005` no puede:

- reactivar P-PAG-004;
- sustituir P-PAG-004;
- convertir DISABLED en ENABLED;
- cambiar el estado técnico definido aquí.

## 11. R-PAG-002

Aunque la documentación también relaciona `P-PAG-004` con `R-PAG-002`, esta autoridad v0.1 cierra únicamente su semántica para `R-PAG-001`.

No se extrapola automáticamente a R-PAG-002.

## 12. No alcance

No autoriza todavía:

- implementación completa de `R-PAG-001`;
- semántica completa de `P-PAG-005`;
- `R-PAG-002`;
- normalización multicuota;
- decisiones CRC;
- valores empresariales alternativos.

## 13. Gates propuestos

```text
PAG001-CTRL-G01 → P-PAG-004 Sí = ENABLED
PAG001-CTRL-G02 → P-PAG-004 No = DISABLED
PAG001-CTRL-G03 → DISABLED → NOT_EVALUABLE, nunca FALSE
PAG001-CTRL-G04 → sin default implícito
PAG001-CTRL-G05 → configuración/evidencia provenance-safe
PAG001-CTRL-G06 → mismo contexto efectivo al combinar con PAG001
PAG001-CTRL-G07 → R-PAG-002 fuera de alcance
```

## 14. Estado

**PAG001 Consider Payment-Term Control Authority v0.1 — PROPUESTA / NO AUTORIZADA.**
