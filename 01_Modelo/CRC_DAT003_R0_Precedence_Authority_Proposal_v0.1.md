# EIOS — CRC DAT003 vs R0 Precedence Authority Proposal v0.1

**Baseline:** `main @ 7a2114e52dd4c388c0c8bdeaae338ccf4d45290c`  
**Fecha:** 21/09/2026  
**Estado:** PROPUESTA — NO AUTORIZADA  
**Ámbito:** conflicto entre `R-DAT-003 TRUE → INFORMACIÓN INSUFICIENTE` y otro `R0 TRUE → NO COMPRAR`

## 1. Problema

DAT003 ya está materializada y autorizada para producir:

```text
R-DAT-003 TRUE → INFORMACIÓN INSUFICIENTE
```

Otros R0 materializados pueden producir:

```text
R0 TRUE → NO COMPRAR
```

La CRC actual falla cerrada cuando ambos resultados aparecen simultáneamente con el mismo efecto dominante R0 porque no existe autoridad de precedencia.

## 2. Autoridad documental disponible

La CRC oficial reconoce cinco resultados:

- COMPRAR;
- NEGOCIAR;
- COMPRAR CONDICIONADO;
- NO COMPRAR;
- INFORMACIÓN INSUFICIENTE.

La Matriz de Reglas establece que la categoría `INFORMACIÓN INSUFICIENTE` existe para evitar que EIOS emita una recomendación cuando la calidad de los datos no permita una conclusión suficientemente fiable.

`R-DAT-003` está definida como:

```text
R0 — BLOQUEO / CRÍTICA respecto a la fiabilidad
Resultado: INFORMACIÓN INSUFICIENTE
```

La CRC también declara como posibles salvaguardas críticas:

- imposibilidad de atender obligaciones financieras;
- ausencia de información crítica;
- datos incompatibles o inválidos;
- errores graves en datos de entrada.

No existe actualmente una regla explícita de desempate entre salvaguardas R0 que conduzcan a resultados distintos.

## 3. Política propuesta

Cuando `R-DAT-003` sea:

```text
EVALUABLE / TRUE
```

y exista simultáneamente cualquier otra regla `R0 / TRUE` cuyo resultado sea `NO COMPRAR`, la CRC consolidará:

```text
INFORMACIÓN INSUFICIENTE
```

## 4. Justificación semántica

La condición DAT003 significa que falta al menos un requisito previamente declarado como necesario para una evaluación fiable.

Por tanto, mientras DAT003 permanezca TRUE:

- EIOS no puede afirmar que el conjunto global de evaluación sea suficientemente fiable;
- no debe convertir una señal crítica parcial en una recomendación empresarial global definitiva;
- la existencia de otro R0 activo debe conservarse como evidencia crítica relevante, no eliminarse.

La precedencia propuesta es una **precedencia de fiabilidad**, no una afirmación de que el riesgo empresarial desaparezca.

## 5. Tratamiento del otro R0 activo

El otro R0 activo debe permanecer visible en:

- `relevant_factors`;
- `conflicts`;
- trazabilidad;
- explicación.

Ejemplo:

```text
Resultado consolidado:
INFORMACIÓN INSUFICIENTE

Motivo dominante:
Falta información crítica requerida para una evaluación fiable.

Factor crítico adicional:
La evaluación financiera disponible activa R-FIN-001.
```

No se rebaja ni invalida el R0 concurrente.

## 6. Casos autorizables propuestos

### Caso A — DAT003 TRUE + otro R0 TRUE

```text
→ INFORMACIÓN INSUFICIENTE
```

### Caso B — DAT003 FALSE + otro R0 TRUE

```text
→ resultado normal del otro R0
```

Ejemplo ordinario:

```text
→ NO COMPRAR
```

### Caso C — DAT003 TRUE sin otro R0

```text
→ INFORMACIÓN INSUFICIENTE
```

### Caso D — DAT003 NOT_EVALUABLE

Se conserva la política CRC ya existente para assessments no evaluables.

No se usa DAT003 NOT_EVALUABLE como sustituto de DAT003 TRUE.

## 7. Restricciones

Esta política NO autoriza:

- ignorar otros R0;
- convertir `NO COMPRAR` en `COMPRAR`;
- marcar como resuelto el riesgo financiero;
- modificar outcomes individuales;
- alterar el Assessment original;
- modificar metadata de severidad/efecto;
- usar score;
- ordenar R0 por nombre, ID, posición o ejecución;
- aplicar la misma precedencia a otros resultados sin autoridad específica.

## 8. Mecanismo técnico propuesto

La CRC debe reconocer explícitamente la combinación:

```text
R-DAT-003 TRUE + conflictivo R0 TRUE
```

y seleccionar `INFORMACIÓN INSUFICIENTE` por autoridad semántica, no por orden de lista.

El motivo dominante será DAT003.

Los demás R0 activos se conservarán como factores críticos y conflictos trazables.

## 9. No regresión

Para cualquier combinación que no incluya `R-DAT-003 TRUE`:

- la CRC debe conservar su comportamiento actual;
- los mapeos R0/R1/R2/R3 permanecen sin cambios;
- el soporte `active_result` sigue vigente;
- no se introduce ranking general entre reglas R0.

## 10. Gate

Si se autoriza:

```text
CRC-DAT003-R0-G01 → precedencia de fiabilidad autorizada
CRC-DAT003-R0-G02 → otros R0 preservados como factores/conflictos
CRC-DAT003-R0-G03 → no mutación de Assessment cerrada
CRC-DAT003-R0-G04 → no ranking general R0
CRC-DAT003-R0-G05 → no regresión fuera de DAT003
```

## 11. Estado

**CRC DAT003 vs R0 Precedence Authority v0.1 — PROPUESTA / NO AUTORIZADA.**
