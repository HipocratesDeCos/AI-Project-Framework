# EIOS — MATRIZ DE REPRESENTATIVIDAD PRICE INTELLIGENCE

**Fase:** 8.5 — Price Intelligence  
**Versión:** 1.0  
**Estado:** CERRADA — METODOLOGÍA ESPECIALIZADA  
**Autoridad:** subordinada a `Price_Intelligence_Methodological_Matrix.md`

## 1. Propósito

Determinar si una referencia comparable, normalizada y temporalmente elegible refleja la realidad económica ordinaria del mercado en el contexto evaluado.

## 2. Principio

`REPRESENTATIVE` no significa "precio frecuente", "último precio", "precio barato", "precio mediano" ni "precio cercano al objetivo".

La representatividad es una evaluación económica contextual y trazable.

## 3. Estados

```text
REPRESENTATIVE
NON_REPRESENTATIVE
INDETERMINATE
```

## 4. Prerrequisitos

Una referencia no puede ser declarada representativa si no es:

- `COMPARABLE`;
- `NORMALIZED`;
- `ELIGIBLE` temporalmente.

Si alguno de estos prerrequisitos no está satisfecho, el estado de representatividad es `INDETERMINATE`.

## 5. Criterios observables

### REP-01 — Contexto económico ordinario

La operación debe corresponder a una situación económica ordinaria para el contexto evaluado.

### REP-02 — Condiciones comerciales ordinarias

No deben existir condiciones comerciales extraordinarias que expliquen materialmente el precio, salvo que formen parte de la base económica ordinaria definida para el contexto.

### REP-03 — Ausencia de anomalía transaccional

No debe existir evidencia de una circunstancia transaccional excepcional que haga que el precio no represente el comportamiento ordinario del mercado.

Un precio extremo no es por sí mismo una anomalía.

### REP-04 — Cantidad y alcance interpretables

La cantidad y el alcance deben corresponder a una operación económicamente ordinaria o estar adecuadamente normalizados.

### REP-05 — Evidencia suficiente para la determinación

La evidencia disponible debe permitir sostener los hechos relevantes para la evaluación de representatividad.

La mera ausencia de evidencia positiva no autoriza a clasificar como `NON_REPRESENTATIVE`; cuando impide concluir, el resultado es `INDETERMINATE`.

### REP-06 — Contradicciones materiales

Una contradicción material no resuelta sobre hechos relevantes impide declarar representatividad.

Una diferencia de precio u outlier estadístico no constituye por sí mismo contradicción.

## 6. Regla de decisión

`REPRESENTATIVE` requiere evidencia positiva suficiente para todos los criterios materiales aplicables y ausencia de contradicción material no resuelta.

`NON_REPRESENTATIVE` requiere evidencia suficiente de una condición que contradiga la realidad económica ordinaria y que no pueda resolverse mediante normalización autorizada.

`INDETERMINATE` se utiliza cuando la evidencia o información disponible no permite concluir de forma defendible.

## 7. Outliers

`OUTLIER ≠ NON_REPRESENTATIVE`.

Un outlier puede ser representativo si refleja una operación económica ordinaria del contexto.

La decisión de excluir un outlier por representatividad requiere evidencia económica, no únicamente distancia estadística.

## 8. Prohibiciones

La representatividad no puede determinarse mediante:

- frecuencia;
- mínimo o máximo precio;
- último precio;
- proveedor habitual;
- score;
- proximidad al PR;
- mediana;
- conveniencia de aumentar N;
- conveniencia de producir un PR.

## 9. Fronteras

```text
COMPARABILIDAD
→ misma base económica o equivalencia autorizada

NORMALIZACIÓN
→ llevar a base económica común

TEMPORALIDAD
→ pertinencia temporal

REPRESENTATIVIDAD
→ realidad económica ordinaria

SELECCIÓN
→ inclusión final según reglas cerradas
```

## 10. Invariantes

1. No comparable → no representativo.
2. No normalizado → no representativo.
3. Temporalmente inelegible → no representativo para selección.
4. Outlier ≠ automáticamente no representativo.
5. Contradicción ≠ automáticamente outlier.
6. Representatividad no depende del valor del PR.
7. Representatividad no modifica el precio.
8. Representatividad no modifica C0.
