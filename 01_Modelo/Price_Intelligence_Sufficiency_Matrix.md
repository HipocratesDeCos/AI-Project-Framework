# EIOS — MATRIZ DE SUFICIENCIA PRICE INTELLIGENCE

**Fase:** 8.5 — Price Intelligence  
**Versión:** 1.2  
**Estado:** CERRADA — METODOLOGÍA ESPECIALIZADA  
**Autoridad:** subordinada a `Price_Intelligence_Methodological_Matrix.md`

## 1. Propósito

Determinar si el conjunto final de referencias seleccionadas proporciona una base suficiente para emitir un Precio de Referencia (PR) con el nivel de defendibilidad autorizado.

## 2. Principio

Suficiencia es una propiedad del **conjunto seleccionado**, no de una referencia individual.

No debe confundirse con comparabilidad, representatividad, temporalidad, dispersión ni tamaño bruto del histórico.

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

`N_SELECTED >= 2` es condición necesaria, pero nunca suficiente por sí sola.

## 5. Condiciones de SUFFICIENT

Además de `N_SELECTED >= 2`, deben satisfacerse las condiciones cualitativas aplicables:

- evidencia suficiente para sostener la evaluación del conjunto;
- ausencia de contradicciones materiales pendientes que afecten a su defendibilidad;
- ausencia de limitaciones metodológicas pendientes que impidan la defendibilidad requerida;
- decisión trazada a evidencia, regla y traza.

Las referencias que llegan a este gate ya han superado los gates anteriores que correspondan. Sufficiency no los reevalúa.

## 6. Semántica de evidence_sufficient

`evidence_sufficient = true` significa que existe evidencia suficiente para sostener la evaluación del conjunto seleccionado en los aspectos que la metodología de suficiencia exige y que no hayan quedado resueltos por gates anteriores.

No significa simplemente:

- que todas las evidencias sean válidas;
- que cada referencia tenga una evidencia;
- que exista un PR plausible;
- que las referencias sean numerosas.

## 7. Semántica de contradictions_resolved

`contradictions_resolved = true` significa que no permanece una contradicción material no resuelta que afecte a la defendibilidad del conjunto seleccionado.

Una diferencia de precio no constituye por sí misma contradicción.

## 8. N = 0

`NOT_JUSTIFIABLE` y `PR_VALUE = null`.

## 9. N = 1

`LIMITED` como máximo. Una única observación no constituye por sí sola benchmark suficiente de mercado.

## 10. N >= 2

Puede alcanzarse `SUFFICIENT` únicamente cuando las condiciones cualitativas aplicables estén satisfechas.

## 11. Dispersión y outliers

Una elevada dispersión no demuestra por sí misma insuficiencia. Un outlier no se elimina para aumentar N. Su tratamiento pertenece a representatividad/selección y debe conservar trazabilidad.

## 12. Contradicciones

Una contradicción material no resuelta que afecte al conjunto impide declararlo plenamente suficiente mientras permanezca sin resolver.

## 13. Relación con temporalidad

Temporalidad es un gate independiente. Sufficiency no contiene una segunda decisión temporal.

## 14. Frontera con agregación

Suficiencia determina si el conjunto permite emitir el resultado. Agregación determina cómo se obtiene el valor del PR a partir del conjunto ya declarado apto. La agregación no puede corregir una insuficiencia.

## 15. Trazabilidad

Una decisión `SUFFICIENT` debe conservar:

- N seleccionado;
- evidencia utilizada;
- regla aplicada;
- traza;
- limitaciones evaluadas.

## 16. Prohibiciones

La suficiencia no puede determinarse mediante necesidad de producir un PR, conveniencia del decisor, frecuencia histórica, proveedor habitual, último precio, precio mínimo/máximo, score, proximidad al PR o ajuste posterior para alcanzar un umbral.

## 17. Mapeo a resultado

```text
SUFFICIENT       → PR_AVAILABLE
LIMITED          → PR_LIMITED
NOT_JUSTIFIABLE  → PR_NOT_JUSTIFIABLE
```

La relación es determinista.
