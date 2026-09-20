# EIOS — MGE Rules Authority v0.1

**Fecha:** 20/09/2026  
**Baseline:** `main @ 6ad89d0bc70900a14cb7a11c4b8fa7660d0bae6e`  
**Estado:** AUTORIZADA — MGE-RULES-AUTH v0.1

## 1. Autoridad humana explícita

Se autoriza expresamente que EIOS evalúe:

- `R-MGE-001`;
- `R-MGE-002`;
- `R-MGE-003`;

a partir exclusivamente de un `ProvenancedProfitabilityExecution` válido y de configuraciones `P-MGE-001/002/003` resueltas, vigentes y evidenciadas.

## 2. Semántica autorizada

Sean:

```text
m = profitability.margin_percentage
minimum = resolved(P-MGE-001)
target = resolved(P-MGE-002)
tolerance = resolved(P-MGE-003)
```

con unidades:

```text
P-MGE-001 → %
P-MGE-002 → %
P-MGE-003 → puntos porcentuales
```

y un conjunto de parámetros coherente.

### R-MGE-001

```text
m < minimum
```

### R-MGE-002

```text
m >= minimum
AND
m >= target - tolerance
AND
m < target
```

La tolerancia representa puntos porcentuales por debajo del objetivo.

### R-MGE-003

```text
m >= target
```

## 3. Coherencia del conjunto de parámetros

Para evitar reglas contradictorias o solapadas:

- `minimum <= target`;
- `tolerance >= 0`;
- los tres valores deben ser decimales finitos;
- los tres parámetros deben pertenecer al mismo `parameters_version`, empresa y fecha efectiva aplicables a la ejecución;
- los tres deben estar vigentes y evidenciados.

Si el conjunto no cumple estas condiciones, las reglas MGE no deben pronunciarse.

La ausencia o invalidez de cualquiera de `P-MGE-001/002/003` no autoriza defaults ni valores iniciales del catálogo.

## 4. Estados no determinables

Si:

```text
ProfitabilityResult.calculation_state != DETERMINED
```

o `margin_percentage = null`, las reglas MGE dependientes del porcentaje producen:

```text
Assessment.status = NOT_EVALUABLE
Assessment.outcome = null
```

Ausencia, contradicción, incompatibilidad o `SALE_BASIS_ZERO` nunca se convierten en margen 0 % ni en `FALSE`.

## 5. Metadata autorizada

Para esta primera materialización:

```text
R-MGE-001 → R1 / ALTA
R-MGE-002 → R2 / MEDIA
R-MGE-003 → R3 / INFORMATIVA
```

No se autoriza escalada automática de `R-MGE-001` a R0.

## 6. No autorizado

Esta autoridad no autoriza:

- hardcodear 20 %, 30 % o 3 pp;
- consumir `P-MGE-004/005/006`;
- seleccionar o construir bases económicas upstream;
- adaptar PRICE/TCO;
- convertir resultados no determinados en valores;
- escalada R0;
- excepciones;
- overrides;
- cambiar la semántica CRC;
- producir una decisión empresarial fuera del runtime EIOS ya autorizado.

## 7. Consecuencia

Quedan satisfechos:

```text
MGE-RULES-G01 → autoridad de ejecución
MGE-RULES-G02 → banda matemática de tolerancia
MGE-RULES-G03 → interacción mínimo/objetivo/tolerancia
MGE-RULES-G05 → metadata conservadora sin R0
```

`MGE-RULES-G04` debe cerrarse físicamente mediante binding provenance-safe de `ResolvedConfiguration + Evidence`.
