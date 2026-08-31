# EIOS — Price Intelligence — PR Design

## Estado

**Estado:** DISEÑO — NO AUTORIZA IMPLEMENTACIÓN  
**Referencia:** EIOS-BL-001  
**Orientación:** modelo híbrido aprobado para PR

## 1. Propósito

Definir la semántica mínima de diseño del Precio de Referencia (PR) sin introducir todavía fórmulas, pesos o umbrales no aprobados.

PR es un indicador de referencia de precio para análisis posterior. No constituye por sí mismo una recomendación, una regla ni una decisión empresarial.

## 2. Principio híbrido

El PR seguirá la secuencia:

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

La selección y la ponderación deberán ser explicables y trazables. Una única observación no adquiere automáticamente carácter de benchmark representativo.

## 3. Entrada canónica

Price Intelligence consume el contexto y los datos autorizados contenidos en el **DECISION INPUT PACKAGE (DIP)**. No crea ni duplica un contexto de evaluación paralelo.

El DIP precede a QTG y a Price Intelligence en la arquitectura funcional. Pricing consume los atributos necesarios para su función respetando la autoridad de cada capa.

## 4. Referencia candidata

Una referencia candidata conserva, cuando estén disponibles y sean aplicables:

- identificación del producto o concepto;
- unidad de medida;
- cantidad;
- fecha;
- precio;
- moneda;
- condiciones comerciales relevantes;
- proveedor, cuando resulte pertinente;
- fuente;
- trazabilidad;
- vínculo con la evidencia que sustenta el precio.

La ausencia de un atributo necesario no se interpreta silenciosamente como equivalencia.

## 5. Comparabilidad graduada

Se adopta el modelo **graduado**.

| Categoría | Dimensiones | Tratamiento |
|---|---|---|
| **Obligatorias** | Producto/concepto; evidencia; fuente/trazabilidad | Su ausencia impide tratar la referencia como comparable por defecto. |
| **Normalizables** | Unidad; cantidad; moneda; condiciones comerciales | Una diferencia no invalida automáticamente la referencia, pero solo puede corregirse mediante una regla aprobada. |
| **Temporal** | Fecha | Determina pertinencia temporal; no implica ajuste automático del precio. |

Estados conceptuales:

- **COMPARABLE:** supera las condiciones aplicables.
- **NO_COMPARABLE:** no satisface una condición necesaria y no existe normalización autorizada.
- **PENDIENTE_DE_EVALUACIÓN:** falta información necesaria para determinar comparabilidad.

La clasificación graduada no permite compensar una deficiencia obligatoria mediante otra dimensión.

## 6. Normalización

La normalización solo puede aplicarse cuando exista una regla aprobada que defina la transformación sin alterar indebidamente el significado económico del precio.

No se autoriza normalización implícita de unidad, cantidad, moneda, transporte, descuentos, rappels, impuestos o condiciones comerciales.

La moneda puede conservarse como atributo de la referencia, pero su conversión para construir PR requiere metodología autorizada.

## 7. Evidencia y QTG

Cada referencia utilizada para PR debe poder relacionarse con su evidencia y origen.

QTG mantiene la autoridad sobre calidad y confianza. Price Intelligence no duplica ni sustituye esos controles.

La evidencia/trazabilidad es condición de confianza y auditabilidad; no constituye por sí misma una variable de representatividad económica.

## 8. Temporalidad histórica

El Framework dispone de parámetros y reglas temporales diferenciados:

- `P-PRE-001`: periodo principal de comparación — valor inicial 3 meses.
- `P-PRE-002`: periodo ampliado de comparación — valor inicial 12 meses.
- `P-DAT-002`: antigüedad máxima de referencia de precio — valor inicial 12 meses.

`R-HIS-001` utiliza `P-DAT-002` como parámetro configurable efectivo para la antigüedad máxima. `P-PRE-003` permanece como criterio/metodología histórica y no como parámetro directo.

Para `R-PRE-001`, la expresión **"referencia comparable reciente"** se interpreta en el diseño MVP como referencia comparable situada dentro del **periodo principal de comparación `P-PRE-001`**, salvo que una autoridad posterior apruebe una definición distinta.

`P-PRE-002` representa el periodo ampliado de análisis histórico y no sustituye a `P-PRE-001` como criterio de referencia reciente.

`P-DAT-002` opera como límite superior de antigüedad histórica y no como peso de recencia.

Esta resolución cierra el **GAP-PI-TEMP-01** sin introducir un parámetro nuevo ni una fórmula de decaimiento temporal.

## 9. Selección → ponderación

Se aprueba la separación explícita entre ambas etapas:

```text
referencias candidatas
        ↓
comparabilidad
        ↓
conjunto admisible
        ↓
representatividad
        ↓
selección
        ↓
ponderación
        ↓
PR
```

### 9.1 Selección

La selección determina qué referencias comparables participan en la construcción de PR.

No puede convertir una referencia no comparable o pendiente de evaluación en comparable.

### 9.2 Ponderación

La ponderación determina, cuando proceda, la influencia relativa de las referencias seleccionadas.

No puede utilizarse para compensar deficiencias de comparabilidad.

## 10. Representatividad contextual

La representatividad se evalúa respecto al **contexto de la evaluación de compra para la que se construye PR**.

No es una propiedad absoluta del precio histórico, del mercado, del proveedor o de la categoría.

La representatividad es conceptualmente distinta de:

- calidad/confianza de QTG;
- comparabilidad;
- selección;
- ponderación.

Una referencia no comparable o pendiente de evaluación no puede adquirir comparabilidad por presentar alta representatividad.

La selección no puede basarse retrospectivamente en que una referencia produzca un PR más conveniente para la decisión empresarial.

## 11. Selección híbrida por comparabilidad + representatividad

Primero se determina el conjunto admisible mediante comparabilidad. Solo después se evalúa la representatividad contextual para determinar el conjunto seleccionado.

La representatividad deberá ser explicable y trazable.

No se autoriza todavía ningún score, peso, umbral ni variable concreta para medirla.

## 12. Dimensiones disponibles

Los datos del DIP que pueden alimentar la evaluación incluyen, según pertinencia:

- producto/concepto;
- cantidad;
- unidad;
- fecha;
- precio;
- moneda;
- proveedor;
- condiciones comerciales;
- descuentos/rappels;
- transporte u otros componentes;
- datos empresariales pertinentes.

**Dato disponible ≠ criterio metodológico autorizado.** La inclusión de una variable en el DIP no implica que deba intervenir en representatividad o ponderación.

## 13. Insuficiencia

El diseño distingue entre:

- conjunto suficiente de referencias comparables;
- conjunto limitado pero potencialmente utilizable;
- ausencia de referencias comparables suficientes.

No se inventará un PR cuando la evidencia disponible no permita construirlo de forma justificable.

La semántica exacta y los umbrales de suficiencia permanecen pendientes.

## 14. Contradicciones

Las referencias contradictorias no se resuelven mediante prioridad arbitraria, último valor, promedio u otra heurística no autorizada.

Su tratamiento concreto permanece pendiente.

## 15. Límites

Este diseño no define todavía:

- fórmula de PR;
- pesos;
- scores;
- umbrales de representatividad;
- tolerancias de normalización;
- reglas de ajuste de cantidad;
- reglas de conversión monetaria;
- reglas de ajuste comercial;
- reglas de outliers;
- criterios finales de suficiencia;
- algoritmo concreto de selección;
- algoritmo concreto de ponderación.

No autoriza implementación.

## 16. Invariantes de diseño

1. QTG precede a Price Intelligence en materia de calidad/confianza.
2. La comparabilidad precede a representatividad, selección y ponderación.
3. La representatividad no modifica la comparabilidad.
4. La selección precede a la ponderación.
5. La ponderación no compensa deficiencias de comparabilidad.
6. La normalización requiere una regla aprobada.
7. La antigüedad histórica no se convierte automáticamente en peso de recencia.
8. Pricing consume el DIP y no crea una segunda autoridad contextual.
9. La selección no puede depender de la conveniencia del PR resultante.
10. Ningún dato disponible se convierte en criterio metodológico sin decisión explícita.

## 17. Estado de cierre parcial

Quedan cerrados en diseño:

- modelo híbrido de PR;
- comparabilidad graduada;
- separación selección → ponderación;
- selección híbrida por comparabilidad + representatividad;
- representatividad contextual respecto a la evaluación de compra;
- DIP como entrada contextual canónica;
- resolución temporal de `R-PRE-001`: "reciente" = dentro de `P-PRE-001` para el diseño MVP;
- distinción entre `P-PRE-001`, `P-PRE-002` y `P-DAT-002`.

Quedan abiertos para posteriores decisiones metodológicas:

- dimensiones concretas de representatividad;
- normalización;
- criterios de suficiencia;
- selección concreta;
- ponderación;
- agregación/fórmula PR;
- outliers;
- contradicciones.

## 18. Criterio de cierre

PR solo podrá pasar a contrato de implementación cuando exista autoridad suficiente para cerrar comparabilidad, normalización, temporalidad aplicable, representatividad, selección, ponderación, suficiencia y contradicciones.
