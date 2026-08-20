# Decision Log — Parámetros MVP

> Registro de decisiones y resolución de gaps de la integración vertical MVP.

## Estado

**Baseline:** EIOS Vertical MVP  
**Estado:** APROBADO  

## 1. Propósito

Registrar decisiones que afecten a la definición, consumo o interpretación de parámetros y dejar trazabilidad de su resolución antes de modificar documentos de autoridad.

## 2. Decisiones vigentes

Se mantienen las decisiones D-01 a D-08 y el criterio de que una regla que requiera un valor configurable sin parámetro correspondiente debe registrarse como gap.

## 3. Registro de resolución de GAPs

| ID | Elemento | Resolución | Estado |
|---|---|---|---|
| GAP-01 | PRO-001 | La autorización/requisitos del proveedor se trata como dato de proveedor, no como parámetro empresarial de 02_Parametros. | CERRADO |
| GAP-02 / C-07 | CON-001 | Se distinguen PAG-001 como mínimo aceptable y PAG-002 como objetivo de negociación. La expresión ambigua «mínimo objetivo» debe sustituirse en 04_Reglas. | CERRADO |
| C-01 | PRE-003 | Se mantiene como criterio/metodología pendiente, sin crear parámetro directo. | CERRADO |
| C-02 | TES-003 | Se mantiene como metodología de umbral financiero pendiente, sin crear parámetro en esta fase. | CERRADO |
| C-03 | PRO-002 | Se trata como evaluación de indicadores del proveedor; no se crea parámetro directo. | CERRADO |
| C-04 | CON-002 | Se trata como cálculo/escenario de razonabilidad económica, no como parámetro directo. | CERRADO |
| C-05 | CON-003 | Se trata como resultado de evaluación/viabilidad, no como parámetro directo. | CERRADO |
| C-06 | FIN-003 | Se trata como evaluación financiera mediante variables y cálculos; no se crea parámetro directo. | CERRADO |

## 4. Documentos afectados

- `04_Reglas`: actualizar CON-001 para eliminar la terminología ambigua y formalizar el uso de PAG-001/PAG-002.
- `Rule_Dependency_Matrix`: actualizar relaciones parámetro-regla y distinguir parámetros de datos/cálculos derivados.
- `02_Parametros`: no requiere nuevos parámetros por esta ronda.
- `05_Motor`: sin modificación derivada de estos gaps.
- `07_Pruebas`: sin modificación derivada de estos gaps.
- `06_SQL`: no modificar hasta completar el cierre documental previo a implementación.

## 5. Criterio de cierre

Los gaps quedan cerrados a nivel funcional cuando la decisión queda registrada y los documentos de autoridad afectados quedan identificados para una única ventana de actualización.
