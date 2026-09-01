# EIOS — MATRIZ TEMPORAL PRICE INTELLIGENCE

**Fase:** 8.5 — Price Intelligence  
**Versión:** 1.0  
**Estado:** CERRADA — METODOLOGÍA ESPECIALIZADA  
**Autoridad:** subordinada a `Price_Intelligence_Methodological_Matrix.md`

## 1. Propósito

Determinar la elegibilidad temporal de una referencia sin convertir la antigüedad en peso de precio ni utilizar la temporalidad para decidir representatividad.

## 2. Principio

La temporalidad responde exclusivamente a si la referencia es pertinente dentro del horizonte temporal autorizado para la evaluación.

No responde a si el precio es representativo.

## 3. Estados

```text
ELIGIBLE
INELIGIBLE
INDETERMINATE
```

## 4. Regla de autoridad

Los parámetros temporales existentes conservan su autoridad propia. C1 no inventa ventanas, periodos, decaimientos ni umbrales cuando la regla autorizada no está disponible.

## 5. Evaluación

`ELIGIBLE`: existe una regla temporal autorizada y la fecha de la referencia satisface sus condiciones.

`INELIGIBLE`: existe una regla temporal autorizada y la fecha de la referencia incumple sus condiciones.

`INDETERMINATE`: falta la regla autorizada o la información necesaria para determinar elegibilidad.

## 6. Prohibiciones

La temporalidad no puede utilizar:

- ponderación por recencia;
- frecuencia;
- último precio;
- proveedor habitual;
- score;
- conveniencia para obtener PR.

La antigüedad no genera por sí misma una penalización ni un peso.

## 7. Fronteras

```text
TEMPORALIDAD
→ pertinencia temporal

REPRESENTATIVIDAD
→ realidad económica ordinaria

SELECCIÓN
→ inclusión conforme a criterios cerrados
```

Una referencia temporalmente elegible puede seguir siendo `NON_REPRESENTATIVE` o `INDETERMINATE`.

Una referencia temporalmente inelegible no puede entrar en el conjunto seleccionado.

## 8. Trazabilidad

Toda clasificación `ELIGIBLE` o `INELIGIBLE` debe poder vincularse a la regla temporal aplicada y a la fecha utilizada.

`INDETERMINATE` debe conservar la causa de indeterminación.

## 9. Invariante

No existe una transformación de precio asociada a temporalidad en el MVP.
