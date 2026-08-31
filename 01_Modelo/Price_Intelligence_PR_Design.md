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
