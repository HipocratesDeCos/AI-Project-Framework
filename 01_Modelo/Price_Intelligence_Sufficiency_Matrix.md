# EIOS — MATRIZ DE SUFICIENCIA PRICE INTELLIGENCE

**Fase:** 8.5 — Price Intelligence  
**Versión:** 1.0  
**Estado:** CERRADA — METODOLOGÍA ESPECIALIZADA  
**Autoridad:** subordinada a `Price_Intelligence_Methodological_Matrix.md`

## 1. Propósito

Determinar si el conjunto final de referencias seleccionadas proporciona una base suficiente para emitir un Precio de Referencia (PR) con el nivel de defendibilidad autorizado.

## 2. Principio

Suficiencia es una propiedad del **conjunto seleccionado**, no de una referencia individual.

No debe confundirse con:

- comparabilidad;
- representatividad;
- ausencia de outliers;
- proximidad entre precios;
- tamaño bruto del histórico.

## 3. Estados

```text
SUFFICIENT
LIMITED
NOT_JUSTIFIABLE
```

## 4. Reglas invariantes

### N = 0

`NOT_JUSTIFIABLE`.

No existe base empírica seleccionada para calcular un PR defendible.

### N = 1

Nunca implica automáticamente `SUFFICIENT`.

El único dato disponible no proporciona por sí mismo evidencia de variabilidad ni contraste suficiente para elevar el resultado a suficiente.

### N > 1

No garantiza automáticamente `SUFFICIENT`.

El tamaño del conjunto es una condición necesaria potencial, no una prueba completa de suficiencia.

## 5. Umbrales

Los umbrales cuantitativos solo pueden utilizarse cuando estén definidos por una regla metodológica autorizada.

C1 no inventa un N mínimo.

Si existe un parámetro autorizado, debe conservarse su referencia y aplicarse literalmente.

Si no existe, el resultado no se fuerza a `SUFFICIENT` por conveniencia operativa.

## 6. Criterios cualitativos

La evaluación de suficiencia debe considerar, cuando estén metodológicamente definidos:

- número de referencias seleccionadas;
- cobertura efectiva del contexto evaluado;
- calidad de la evidencia;
- estabilidad o dispersión relevante del conjunto;
- limitaciones conocidas que afecten a la interpretación.

Estos criterios no pueden utilizarse para re-clasificar una referencia individual como representativa.

## 7. Dispersión y outliers

Una elevada dispersión no demuestra por sí misma que el conjunto sea insuficiente.

Un outlier no se elimina automáticamente para mejorar la suficiencia.

La exclusión debe proceder de la evaluación de representatividad y mantenerse trazable.

## 8. Estados y PR

```text
SUFFICIENT
    → PR_AVAILABLE

LIMITED
    → PR_LIMITED

NOT_JUSTIFIABLE
    → PR_NOT_JUSTIFIABLE
```

La relación es determinista y no puede ser alterada por el valor calculado del PR.

## 9. Trazabilidad

La determinación de suficiencia debe conservar:

- N seleccionado;
- reglas aplicadas;
- parámetros/umbrales autorizados, si existen;
- limitaciones;
- referencias de trazabilidad.

## 10. Prohibiciones

La suficiencia no puede determinarse mediante:

- necesidad de producir un PR;
- conveniencia del decisor;
- frecuencia histórica;
- proveedor habitual;
- último precio;
- precio mínimo/máximo;
- score;
- proximidad al PR;
- ajuste posterior para alcanzar un umbral.

## 11. Frontera con agregación

Suficiencia determina si el conjunto permite emitir el resultado.

Agregación determina cómo se obtiene el valor del PR a partir del conjunto que ya ha sido declarado apto.

La agregación no puede corregir una insuficiencia.
