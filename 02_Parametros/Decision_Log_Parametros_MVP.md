# DECISION LOG — PARÁMETROS MVP

## EIOS — Enterprise Intelligent Operations System

**Versión:** 0.3  
**Estado:** APROBADO  
**Baseline:** EIOS Vertical MVP  
**Fecha:** 20/08/2026

---

# 1. PROPÓSITO

Este documento registra las decisiones necesarias para cerrar la definición funcional de `02_Parametros` sin modificar silenciosamente la autoridad de `01_Modelo`, `04_Reglas` o la CRC.

Actúa como documento de decisión y no sustituye al Centro de Parametrización, al Catálogo de Parámetros ni a la Matriz de Reglas.

---

# 2. DECISIONES APROBADAS

Se mantienen las decisiones D-01 a D-08 de la versión 0.2.

---

# 3. REGISTRO DE RESOLUCIÓN DE GAPs

| ID | Elemento | Resolución | Estado |
|---|---|---|---|
| GAP-01 | `PRO-001` | La autorización/requisitos del proveedor se trata como dato del proveedor, no como parámetro empresarial de `02_Parametros`. No se crea parámetro nuevo. | CERRADO |
| C-01 | `PRE-003` | Se mantiene como criterio/metodología pendiente, sin crear parámetro directo. | CERRADO |
| C-02 | `TES-003` | Se mantiene como metodología de umbral financiero pendiente, sin crear parámetro en esta fase. | CERRADO |
| C-03 | `PRO-002` | Se trata como evaluación de indicadores del proveedor; no se crea parámetro directo. | CERRADO |
| C-04 | `CON-002` | Se trata como cálculo/escenario de razonabilidad económica, no como parámetro directo. | CERRADO |
| C-05 | `CON-003` | Se trata como resultado de evaluación/viabilidad, no como parámetro directo. | CERRADO |
| C-06 | `FIN-003` | Se trata como evaluación financiera mediante variables y cálculos; no se crea parámetro directo. | CERRADO |
| C-07 | `CON-001` | Se distinguen `PAG-001` como plazo mínimo aceptable y `PAG-002` como plazo objetivo de negociación. La expresión «mínimo objetivo» se sustituye para evitar ambigüedad. | CERRADO |

---

# 4. DECISIÓN SOBRE CON-001

`CON-001` deberá consumir los dos conceptos existentes en el catálogo:

- `PAG-001` — plazo mínimo aceptable.
- `PAG-002` — plazo objetivo de negociación.

No se crea un parámetro adicional.

La materialización de esta decisión corresponde al documento de autoridad de `04_Reglas`.

---

# 5. DOCUMENTOS AFECTADOS

- `04_Reglas`: incorporar/normalizar `CON-001` y eliminar la terminología ambigua «mínimo objetivo».
- `02_Parametros/Matriz_Parametros_Reglas_MVP.md`: actualizar únicamente las relaciones parámetro-regla demostradas documentalmente.
- `02_Parametros/Catalogo_Parametros_MVP_v0.3.md`: no requiere nuevos parámetros por esta ronda.
- `05_Motor`: sin modificación derivada de estos GAPs.
- `06_SQL`: no modificar hasta completar el cierre documental previo a implementación.
- `07_Pruebas`: sin modificación derivada de estos GAPs.

---

# 6. CRITERIO DE CIERRE

Los GAPs quedan cerrados a nivel funcional cuando la decisión queda registrada y los documentos de autoridad afectados quedan identificados para una única ventana de actualización.

La modificación del documento de autoridad se realizará de forma controlada y posteriormente será auditada.

---

# 7. PRINCIPIO DE NO ALTERACIÓN DE AUTORIDAD

Este Decision Log no modifica por sí mismo documentos aprobados.

Una decisión aprobada que afecte a `04_Reglas`, la CRC, `01_Modelo` o la Arquitectura deberá materializarse mediante la actualización controlada del documento que tenga autoridad sobre la materia.

---

# 8. ESTADO

**Versión:** 0.3  
**Estado:** APROBADO  
**Baseline:** EIOS Vertical MVP
