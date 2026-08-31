# EIOS — Price Intelligence — PR Design

## Estado

**Estado:** DISEÑO — NO AUTORIZA IMPLEMENTACIÓN  
**Referencia:** EIOS-BL-001  
**Orientación:** modelo híbrido aprobado para PR

## 1. Propósito

Definir la semántica mínima de diseño del Precio de Referencia (PR) sin introducir todavía fórmulas, pesos o umbrales no aprobados.

PR es un indicador de referencia de precio para análisis posterior. No constituye por sí mismo una recomendación, una regla ni una decisión empresarial.

## 2. Principio híbrido

El PR seguirá una secuencia conceptual de tres etapas:

```text
referencias candidatas
        ↓
comparabilidad
        ↓
selección / ponderación explícita
        ↓
PR
```

La selección o ponderación deberá ser explicable y trazable. Una única observación no adquiere automáticamente carácter de benchmark representativo por el mero hecho de existir.

## 3. Referencia candidata

Una referencia candidata debe conservar, cuando estén disponibles y sean aplicables:

- identificación del producto o concepto;
- unidad de medida;
- cantidad;
- fecha;
- moneda;
- condiciones comerciales relevantes;
- fuente;
- trazabilidad;
- vínculo con la evidencia que sustenta el precio.

La ausencia de un atributo necesario no se interpreta silenciosamente como equivalencia.

## 4. Comparabilidad

La comparabilidad debe evaluarse antes de utilizar una referencia para construir PR.

Como mínimo conceptual, debe considerar:

- equivalencia o relación suficiente del producto/concepto;
- unidad comparable o normalizable;
- cantidad comparable o normalizable;
- proximidad temporal adecuada al uso previsto;
- condiciones comerciales relevantes;
- moneda y componentes de precio comparables o normalizables.

Los criterios concretos, tolerancias y ventanas temporales permanecen pendientes de especificación funcional.

## 5. Selección y ponderación

Una referencia que no supere los criterios de comparabilidad aplicables no debe contribuir al PR como si fuera comparable.

Cuando existan varias referencias comparables, el diseño híbrido requiere una fase explícita de selección y/o ponderación.

La metodología concreta de selección y ponderación permanece pendiente. No se prescribe media, mediana, último precio, percentiles ni ningún otro método sin autorización posterior.

## 6. Normalización

Cuando dos referencias sean comparables pero presenten diferencias normalizables, dichas diferencias deberán quedar identificadas antes de su utilización.

La normalización podrá afectar, cuando corresponda, a unidad, cantidad, moneda y condiciones comerciales.

Las reglas concretas de normalización permanecen pendientes de especificación.

## 7. Evidencia y trazabilidad

Cada referencia utilizada para PR debe poder relacionarse con su evidencia y origen.

La ausencia de trazabilidad suficiente no se convierte en una referencia fiable por defecto.

QTG precede a Price Intelligence y conserva la autoridad sobre calidad y confianza. Price Intelligence no duplica sus controles.

## 8. Casos insuficientes

El diseño debe distinguir entre:

- conjunto suficiente de referencias comparables;
- conjunto limitado pero utilizable;
- ausencia de referencias comparables suficientes.

La semántica exacta de estos casos y su efecto sobre PR queda pendiente de especificación funcional.

No se inventará un PR cuando la evidencia disponible no permita construirlo de forma justificable.

## 9. Contradicciones

Las referencias contradictorias no se resuelven mediante prioridad arbitraria, último valor, promedio u otra heurística no autorizada.

Su tratamiento concreto queda pendiente de especificación.

## 10. Límites

Este diseño no define:

- fórmula de PR;
- pesos;
- umbrales;
- ventanas temporales concretas;
- tolerancias concretas;
- reglas de outliers;
- metodología de PO;
- metodología de PPV;
- metodología o fórmula de PMR.

No autoriza implementación.

## 11. Criterio de cierre

PR solo podrá pasar a contrato de implementación cuando exista autoridad suficiente para cerrar la metodología de comparabilidad, normalización, selección/ponderación y tratamiento de insuficiencia y contradicciones.

## 12. CP-69.1 — Matriz de comparabilidad (diseño)

Se adopta el modelo **graduado** de comparabilidad. Las dimensiones se clasifican según su función, sin convertirlas todavía en umbrales ni reglas ejecutables.

| Categoría | Dimensiones | Tratamiento |
|---|---|---|
| **Obligatorias** | Producto/concepto; evidencia; fuente/trazabilidad | Deben permitir identificar qué se está comparando y de dónde procede el precio. Su ausencia impide tratar la referencia como comparable por defecto. |
| **Normalizables** | Unidad; cantidad; moneda; condiciones comerciales | Una diferencia no invalida automáticamente la referencia, pero solo puede corregirse mediante una regla de normalización aprobada. |
| **Temporales** | Fecha | La proximidad temporal es necesaria para valorar la pertinencia, pero la ventana concreta queda pendiente de especificación. |

### 12.1 Clasificación conceptual

Una referencia puede clasificarse, a efectos de diseño, como:

- **COMPARABLE:** supera las condiciones aplicables y puede contribuir a la fase de selección/ponderación.
- **NO_COMPARABLE:** no satisface una condición necesaria y no existe normalización autorizada que permita utilizarla.
- **PENDIENTE_DE_EVALUACIÓN:** falta información necesaria para determinar comparabilidad.

Estas etiquetas son de diseño y **no constituyen todavía estados físicos ni contrato técnico**.

### 12.2 Regla de información faltante

La ausencia de un atributo necesario no se interpreta como equivalencia. Una referencia con información insuficiente debe permanecer pendiente de evaluación o quedar excluida, según la metodología que posteriormente sea aprobada.

### 12.3 Regla de normalización

La normalización solo puede aplicarse cuando exista una regla aprobada que defina cómo transformar la diferencia sin alterar indebidamente el significado económico del precio.

No se autoriza una normalización implícita.

### 12.4 Regla de contradicción

Cuando las fuentes o atributos relevantes sean contradictorios, la referencia no adquiere comparabilidad por selección arbitraria del valor más conveniente. El tratamiento debe conservar la contradicción y esperar la metodología aprobada.

### 12.5 Regla de dependencia entre dimensiones

La clasificación graduada no significa que una dimensión pueda compensar libremente otra.

En particular:

- una referencia no puede ser considerada comparable únicamente porque producto y precio coincidan si carece de evidencia/trazabilidad suficiente;
- una diferencia normalizable no puede darse por normalizada sin regla aprobada;
- una dimensión obligatoria no puede ser compensada mediante ponderación estadística;
- la selección/ponderación solo opera sobre referencias que hayan superado previamente las condiciones de comparabilidad aplicables.

### 12.6 Límites de esta matriz

Esta matriz no fija:

- tolerancias numéricas;
- ventanas temporales;
- tipos de cambio;
- reglas de ajuste de cantidad;
- reglas de ajuste comercial;
- criterios de outlier;
- pesos;
- algoritmo de selección;
- fórmula de PR.

Su función es establecer la estructura de evaluación, no completar las decisiones metodológicas pendientes.

## 13. CP-70 — Decisión de comparabilidad graduada

La comparabilidad se interpreta mediante tres categorías funcionales: **obligatoria**, **normalizable** y **temporal**.

La categoría normalizable no permite compensar una deficiencia en una dimensión obligatoria. La selección o ponderación de referencias solo puede actuar después de la evaluación de comparabilidad.

La dimensión temporal permanece separada de la normalización económica: la antigüedad o pertinencia temporal no se corrige implícitamente mediante un ajuste de precio.

Esta decisión mantiene el modelo híbrido de PR sin introducir todavía umbrales, tolerancias, pesos o fórmulas.

## 14. CP-87 — Separación selección → ponderación

Se aprueba la separación explícita entre **selección** y **ponderación** como etapas independientes del modelo híbrido.

La secuencia normativa de diseño queda:

```text
referencias candidatas
        ↓
comparabilidad
        ↓
selección
        ↓
ponderación
        ↓
PR
```

### 14.1 Selección

La selección determina qué referencias comparables participan en la construcción de PR.

Una referencia debe haber superado previamente las condiciones de comparabilidad aplicables. La selección no puede utilizarse para convertir una referencia no comparable o pendiente de evaluación en comparable.

La metodología concreta de selección permanece pendiente de especificación funcional.

### 14.2 Ponderación

La ponderación determina, cuando proceda, la influencia relativa de las referencias seleccionadas sobre la construcción de PR.

La ponderación es conceptualmente posterior a la selección y no puede utilizarse para compensar deficiencias de comparabilidad.

La metodología concreta de ponderación permanece pendiente de especificación funcional.

### 14.3 Límites

Esta separación no autoriza todavía:

- criterios concretos de selección;
- criterios de exclusión por representatividad;
- pesos;
- ponderación por recencia, volumen, proveedor u otra variable;
- media, mediana, percentiles u otra agregación;
- fórmula de PR.

Cualquier metodología de selección o ponderación deberá ser aprobada antes de convertirse en regla ejecutable.
