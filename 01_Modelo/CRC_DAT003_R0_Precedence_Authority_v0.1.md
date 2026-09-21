# EIOS — CRC DAT003 vs R0 Precedence Authority v0.1

**Baseline de autorización:** `main @ 7a2114e52dd4c388c0c8bdeaae338ccf4d45290c`  
**Fecha:** 21/09/2026  
**Estado:** AUTORIZADO Y CORREGIDO  
**Ámbito:** coexistencia de `R-DAT-003 TRUE → INFORMACIÓN INSUFICIENTE` con otro `R0 TRUE → NO COMPRAR`

## 1. Autoridad humana explícita

Se autoriza la política propuesta de precedencia de fiabilidad, con las correcciones de seguridad descritas en este documento.

## 2. Regla de precedencia autorizada

La precedencia especial se activa únicamente cuando:

```text
R-DAT-003.status == EVALUABLE
AND
R-DAT-003.outcome == TRUE
```

y existe al menos otro Assessment:

```text
effect == R0
AND
status == EVALUABLE
AND
outcome == TRUE
AND
resultado autorizado == NO COMPRAR
```

En ese caso:

```text
resultado consolidado = INFORMACIÓN INSUFICIENTE
motivo dominante      = motivo de R-DAT-003
```

## 3. Corrección de seguridad — DAT003 NOT_EVALUABLE no domina

Un Assessment de DAT003:

```text
NOT_EVALUABLE
```

no activa esta precedencia y no puede absorber un R0 evaluable/TRUE.

Por tanto:

```text
DAT003 NOT_EVALUABLE + R0 TRUE
≠
precedencia DAT003 TRUE
```

La CRC debe preservar la semántica normal aplicable al resto de assessments y su política ya autorizada para no evaluables.

## 4. Preservación del otro R0

La precedencia de fiabilidad no invalida, rebaja ni elimina el otro R0 activo.

Todo R0 concurrente deberá conservarse en:

- `relevant_factors`;
- `conflicts`;
- traceability;
- explicación.

El resultado global `INFORMACIÓN INSUFICIENTE` significa únicamente que EIOS no dispone de base suficiente para emitir una recomendación global fiable.

No significa que el riesgo R0 concurrente sea falso, resuelto o irrelevante.

## 5. Motivo dominante

Cuando la precedencia DAT003 sea aplicable:

```text
dominant_reason = R-DAT-003.reason
```

Los motivos de los R0 concurrentes deberán permanecer como factores críticos relevantes.

No se autoriza escoger otro motivo dominante por orden de ejecución.

## 6. Casos cerrados

### A — DAT003 EVALUABLE/TRUE + R0 EVALUABLE/TRUE

```text
→ INFORMACIÓN INSUFICIENTE
```

### B — DAT003 EVALUABLE/FALSE + R0 EVALUABLE/TRUE

```text
→ resultado normal autorizado del R0
```

### C — DAT003 EVALUABLE/TRUE sin otro R0

```text
→ INFORMACIÓN INSUFICIENTE
```

### D — DAT003 NOT_EVALUABLE + R0 EVALUABLE/TRUE

La precedencia especial DAT003 NO se activa.

### E — ningún DAT003 TRUE

La CRC conserva el comportamiento previo.

## 7. No ranking general R0

Esta autoridad no crea una tabla general de precedencia entre R0.

Solo autoriza la excepción semántica:

```text
R-DAT-003 EVALUABLE/TRUE
→ prioridad de fiabilidad para resultado consolidado
```

No se autoriza extrapolar esta regla a otras parejas de resultados.

## 8. No mutación

La CRC no modifica:

- status;
- outcome;
- evidence_ids;
- reason;
- metadata;

de ningún Assessment original.

La precedencia pertenece únicamente a la fase de consolidación.

## 9. No automatización

`INFORMACIÓN INSUFICIENTE` no es una orden de compra, aprobación, rechazo ni ejecución empresarial.

La decisión final sigue correspondiendo al decisor autorizado.

## 10. Gates cerrados

```text
CRC-DAT003-R0-G01 → CLOSED
CRC-DAT003-R0-G02 → CLOSED
CRC-DAT003-R0-G03 → CLOSED
CRC-DAT003-R0-G04 → CLOSED
CRC-DAT003-R0-G05 → CLOSED
CRC-DAT003-R0-G06 → DAT003 NOT_EVALUABLE no activa precedencia
```

## 11. Estado

**CRC DAT003 vs R0 Precedence Authority v0.1 — AUTORIZADO Y CORREGIDO.**
