# DECISION LOG — PARÁMETROS MVP

## EIOS — Enterprise Intelligent Operations System

**Versión:** 0.4  
**Estado:** APROBADO  
**Baseline:** EIOS Vertical MVP  
**Fecha:** 20/08/2026

---

# 1. PROPÓSITO

Registrar las decisiones necesarias para cerrar la definición funcional de `02_Parametros` y mantener trazabilidad sobre los GAPs detectados.

Este documento no sustituye al Catálogo de Parámetros ni a la Matriz de Reglas.

---

# 2. DECISIONES APROBADAS

Se mantienen las decisiones D-01 a D-08 de la versión anterior, salvo las precisiones expresamente indicadas en este documento.

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
| C-07 | Plazos de pago | Se distinguen `P-PAG-001` como parámetro de plazo mínimo deseado y `P-PAG-002` como parámetro de plazo objetivo. Las reglas de la familia correspondiente deberán utilizar la nomenclatura `R-PAG-*`. No se asigna todavía una relación concreta parámetro-regla sin evidencia documental. | CERRADO |
| GAP-ID-01 | Convención de IDs | Se mantiene la convención ya establecida: `P-*` para parámetros y `R-*` para reglas. Los documentos que aún utilicen IDs sin prefijo requieren migración controlada. | ABIERTO — MIGRACIÓN |

---

# 4. CONVENCIÓN DE IDENTIFICADORES

La identificación de entidades entre capas se expresa mediante prefijo de tipo:

- `P-XXX-NNN` → parámetro.
- `R-XXX-NNN` → regla.

Ejemplo:

- `P-FIN-001` → parámetro financiero.
- `R-FIN-001` → regla financiera.

La migración no cambia la numeración funcional existente; añade el prefijo de tipo para eliminar ambigüedad entre capas.

---

# 5. DECISIÓN SOBRE C-07

No se utilizará `CON-001` como identificador de una regla de plazo de pago.

La matriz oficial de reglas utiliza identificadores de regla de la familia correspondiente. Por tanto, cualquier referencia anterior a `CON-001` para esta cuestión queda sin efecto hasta disponer de evidencia documental que la respalde.

No se crean parámetros nuevos.

---

# 6. DOCUMENTOS AFECTADOS

- `02_Parametros/Catalogo_Parametros_MVP_v0.3.md`: migración de IDs a `P-*` cuando corresponda.
- `02_Parametros/Matriz_Parametros_Reglas_MVP.md`: migración de IDs de parámetros y referencias a reglas a `P-*` / `R-*`; no inventar relaciones pendientes.
- `04_Reglas/Matriz_Reglas_MVP.md`: migración de IDs de reglas a `R-*` cuando corresponda.
- `04_Reglas/Reglas_MVP.md`: mantener bajo revisión por coexistencia documental hasta resolver su papel respecto a la matriz oficial.
- `05_Motor`: no modificar todavía.
- `06_SQL`: no modificar todavía.
- `07_Pruebas`: no modificar todavía.

---

# 7. PRINCIPIO DE NO INFERENCIA

La coincidencia del número o familia de un ID no demuestra una relación funcional.

Una relación parámetro → regla solo se considerará confirmada cuando exista evidencia documental suficiente.

---

# 8. CRITERIO DE CIERRE

Los GAPs funcionales quedan cerrados cuando la decisión está registrada y los documentos de autoridad afectados están identificados.

Los GAPs de migración documental permanecen abiertos hasta completar la actualización controlada y su posterior auditoría.

---

# 9. ESTADO

**Versión:** 0.4  
**Estado:** APROBADO  
**Baseline:** EIOS Vertical MVP
