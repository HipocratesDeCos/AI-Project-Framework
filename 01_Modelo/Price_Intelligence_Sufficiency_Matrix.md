# EIOS — MATRIZ DE SUFICIENCIA PRICE INTELLIGENCE

**Fase:** 8.5 — Price Intelligence  
**Versión:** 1.1  
**Estado:** CERRADA — METODOLOGÍA ESPECIALIZADA  
**Autoridad:** subordinada a `Price_Intelligence_Methodological_Matrix.md`

## 1. Propósito

Determinar si el conjunto final de referencias seleccionadas proporciona una base suficiente para emitir un Precio de Referencia (PR) con el nivel de defendibilidad autorizado.

## 2. Principio

Suficiencia es una propiedad del **conjunto seleccionado**, no de una referencia individual.

No debe confundirse con comparabilidad, representatividad, ausencia de outliers, proximidad entre precios o tamaño bruto del histórico.

## 3. Estados

```text
SUFFICIENT
LIMITED
NOT_JUSTIFIABLE
```

## 4. Regla de multiplicidad mínima

La metodología canónica establece:

```text
N_SELECTED = 0 → NOT_JUSTIFIABLE
N_SELECTED = 1 → como máximo LIMITED
N_SELECTED >= 2 → puede ser SUFFICIENT
```

Por tanto, `N_SELECTED >= 2` es condición necesaria para `SUFFICIENT`, pero nunca condición suficiente por sí sola.

No existe un umbral superior universal.

## 5. Condiciones de SUFFICIENT

Además de `N_SELECTED >= 2`, deben satisfacerse todas las condiciones aplicables:

- referencias comparables;
- representatividad determinada;
- normalización válida cuando corresponda;
- evidencia y trazabilidad suficientes;
- ausencia de contradicciones materiales no resueltas que afecten al conjunto;
- contexto temporal aplicable;
- base de observaciones económicamente defendible.

## 6. N = 0

`NOT_JUSTIFIABLE`.

No existe base empírica seleccionada para calcular un PR defendible.

El resultado debe mantener `PR_VALUE = null`.

## 7. N = 1

`LIMITED` como máximo.

La existencia de una mediana matemática no convierte una única observación histórica en benchmark suficiente de mercado.

## 8. N >= 2

Puede alcanzarse `SUFFICIENT`, pero solo después de evaluar las condiciones cualitativas y las limitaciones del conjunto.

No se autoriza elevar automáticamente a `SUFFICIENT` por superar el umbral.

## 9. Dispersión y outliers

Una elevada dispersión no demuestra por sí misma que el conjunto sea insuficiente.

Un outlier no se elimina automáticamente para mejorar N.

La exclusión debe proceder de representatividad/selección y mantenerse trazable.

## 10. Contradicciones

Una contradicción material no resuelta que afecte al conjunto impide declararlo plenamente suficiente mientras permanezca sin resolver.

La diferencia de precio, por sí sola, no constituye contradicción.

## 11. Estados y PR

```text
SUFFICIENT
    → PR_AVAILABLE

LIMITED
    → PR_LIMITED

NOT_JUSTIFIABLE
    → PR_NOT_JUSTIFIABLE
```

La relación es determinista.

## 12. Trazabilidad

La determinación debe conservar:

- N seleccionado;
- reglas aplicadas;
- umbral aplicado (`N>=2`, cuando corresponda);
- limitaciones;
- referencias de trazabilidad.

## 13. Prohibiciones

La suficiencia no puede determinarse mediante necesidad de producir un PR, conveniencia del decisor, frecuencia histórica, proveedor habitual, último precio, precio mínimo/máximo, score, proximidad al PR o ajuste posterior para alcanzar un umbral.

## 14. Frontera con agregación

Suficiencia determina si el conjunto permite emitir el resultado.

Agregación determina cómo se obtiene el valor del PR a partir del conjunto ya declarado apto.

La agregación no puede corregir una insuficiencia.

## 15. Autoridad

`P-PRE-006` conserva exclusivamente la autoridad que ya posee sobre `R-HIS-002`; no constituye el umbral de suficiencia de PR.

La regla `N_SELECTED >= 2` procede de la matriz metodológica canónica de Price Intelligence.
