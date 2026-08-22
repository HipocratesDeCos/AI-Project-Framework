# DECISION LOG — PARÁMETROS MVP

## EIOS — Enterprise Intelligent Operations System

**Versión:** 0.6  
**Estado:** APROBADO — C-07 / GAP-HIS-01 / GAP-HIS-02 CERRADOS  
**Baseline:** EIOS Vertical MVP  
**Fecha:** 22/08/2026

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
| C-01 | `PRE-003` | Se mantiene como criterio/metodología, no como parámetro directo. Para `R-HIS-001`, el parámetro configurable efectivo es `P-DAT-002`. | CERRADO |
| C-02 | `TES-003` | Se mantiene como metodología de umbral financiero pendiente, sin crear parámetro en esta fase. | CERRADO |
| C-03 | `PRO-002` | Se trata como evaluación de indicadores del proveedor; no se crea parámetro directo. | CERRADO |
| C-04 | `CON-002` | Se trata como cálculo/escenario de razonabilidad económica, no como parámetro directo. | CERRADO |
| C-05 | `CON-003` | Se trata como resultado de evaluación/viabilidad, no como parámetro directo. | CERRADO |
| C-06 | `FIN-003` | Se trata como evaluación financiera mediante variables y cálculos; no se crea parámetro directo. | CERRADO |
| C-07 | Plazos de pago | Se distinguen `P-PAG-001` como parámetro de plazo mínimo deseado y `P-PAG-002` como parámetro de plazo objetivo. Las relaciones funcionales con `R-PAG-*` quedan establecidas mediante `04_Reglas/Especificacion_Reglas_Configuracion_Pagos_MVP.md` v1.0, incorporadas a `04_Reglas/Matriz_Reglas_MVP.md` v2.1 y reflejadas en `02_Parametros/Matriz_Parametros_Reglas_MVP.md` v0.7. | CERRADO — EVIDENCIA DOCUMENTAL |
| **GAP-HIS-01** | `PRE-003 / DAT-002 → R-HIS-001` | `P-DAT-002` es el parámetro configurable efectivo de `R-HIS-001`. `P-PRE-003` queda como criterio/metodología histórica, no como parámetro directo. No existe relación maestro → derivado documentada entre ambos. | **CERRADO — EVIDENCIA DOCUMENTAL** |
| **GAP-HIS-02** | `PRE-006 / DAT-003 → R-HIS-002` | `P-PRE-006` es el parámetro configurable efectivo de `R-HIS-002`. `P-DAT-003` representa un criterio distinto de disponibilidad/registro histórico y no sustituye a `P-PRE-006`. No existe relación maestro → derivado documentada entre ambos. | **CERRADO — EVIDENCIA DOCUMENTAL** |
| GAP-ID-01 | Convención de IDs | Se mantiene la convención ya establecida: `P-*` para parámetros y `R-*` para reglas. Los documentos que aún utilicen IDs sin prefijo requieren migración controlada. | ABIERTO — MIGRACIÓN |

---

# 4. DECISIÓN SOBRE GAP-HIS-01

### Relación analizada

`P-PRE-003 / P-DAT-002 → R-HIS-001`

### Decisión aprobada

`P-DAT-002` es el **parámetro configurable efectivo** consumido por `R-HIS-001` para la antigüedad máxima de referencia de precio.

`P-PRE-003` se mantiene como **criterio/metodología histórica** y no como parámetro directo.

No se clasifica la relación entre ambos como maestro → derivado porque no existe evidencia documental de una transformación entre los dos parámetros.

No se clasifica como duplicidad funcional del MVP porque la documentación les asigna papeles distintos: criterio/metodología frente a parámetro configurable consumidor.

**Estado: CERRADO — EVIDENCIA DOCUMENTAL.**

---

# 5. DECISIÓN SOBRE GAP-HIS-02

### Relación analizada

`P-PRE-006 / P-DAT-003 → R-HIS-002`

### Decisión aprobada

`P-PRE-006` es el **parámetro configurable efectivo** consumido por `R-HIS-002` para el número mínimo de operaciones comparables.

`P-DAT-003` representa un criterio distinto de disponibilidad/registro histórico y no sustituye a `P-PRE-006`.

No se clasifica la relación entre ambos como maestro → derivado porque no existe evidencia documental de una transformación entre los dos parámetros.

No se clasifica como duplicidad funcional del MVP porque la documentación les asigna ámbitos distintos.

**Estado: CERRADO — EVIDENCIA DOCUMENTAL.**

---

# 6. DECISIÓN SOBRE C-07

No se utilizará `CON-001` como identificador de una regla de plazo de pago.

La matriz oficial de reglas utiliza identificadores de regla de la familia correspondiente. Por tanto, cualquier referencia anterior a `CON-001` para esta cuestión queda sin efecto.

No se crean parámetros nuevos.

### Resolución funcional aprobada

| Parámetro | Regla | Tipo de relación | Estado |
|---|---|---|---|
| `P-PAG-001` | `R-PAG-002` | Directa | CERRADA |
| `P-PAG-002` | `R-PAG-001` | Directa | CERRADA |
| `P-PAG-003` | `R-PAG-001` | Derivada | CERRADA |
| `P-PAG-004` | `R-PAG-001 / R-PAG-002` | Control funcional | CERRADA |
| `P-PAG-005` | `R-PAG-001 / R-PAG-002` | Indirecta / derivada | CERRADA |

### Evidencia documental

La relación se encuentra formalizada en:

1. `04_Reglas/Especificacion_Reglas_Configuracion_Pagos_MVP.md` v1.0 — evidencia especializada.
2. `04_Reglas/Matriz_Reglas_MVP.md` v2.1 — incorporación de los parámetros en las reglas consumidoras.
3. `02_Parametros/Matriz_Parametros_Reglas_MVP.md` v0.8 — matriz oficial de enlace.
4. `00_Gobierno/Registro_Evidencias_Trazabilidad_F3.md` v1.1 — registro de evidencias EVID-PAG-001…005.

La cadena documental queda:

`P-PAG-* → Especificación → R-PAG-* → Matriz P→R → Evidencia F3 → C-07`

---

# 7. EVIDENCIA DE LOS GAP HISTÓRICOS

La evidencia especializada queda documentada en:

`04_Reglas/Especificacion_Reglas_Historico_MVP.md` v1.1

La matriz oficial queda actualizada en:

`02_Parametros/Matriz_Parametros_Reglas_MVP.md` v0.8

Para `GAP-HIS-01`:

`P-PRE-003 → criterio/metodología`  
`P-DAT-002 → R-HIS-001`

Para `GAP-HIS-02`:

`P-DAT-003 → criterio distinto / sin consumidor directo demostrado`  
`P-PRE-006 → R-HIS-002`

La creación de parámetros `HIS-*` queda expresamente descartada.

---

# 8. DOCUMENTOS AFECTADOS

- `02_Parametros/Catalogo_Parametros_MVP_v0.3.md`: migración de IDs a `P-*` cuando corresponda.
- `02_Parametros/Matriz_Parametros_Reglas_MVP.md`: migración de IDs de parámetros y referencias a reglas a `P-*` / `R-*`; C-07 y GAP-HIS-01/02 incorporados.
- `04_Reglas/Matriz_Reglas_MVP.md`: migración de IDs de reglas a `R-*` cuando corresponda; C-07 ya incorporado.
- `04_Reglas/Especificacion_Reglas_Configuracion_Pagos_MVP.md`: evidencia especializada de C-07.
- `04_Reglas/Especificacion_Reglas_Historico_MVP.md`: evidencia especializada de GAP-HIS-01/02.
- `04_Reglas/Reglas_MVP.md`: mantener bajo revisión por coexistencia documental hasta resolver su papel respecto a la matriz oficial.
- `00_Gobierno/Registro_Evidencias_Trazabilidad_F3.md`: requiere actualización en el paso específico de F3.
- `00_Gobierno/Especificacion_Evidencia_Trazabilidad_F3.md`: requiere actualización en el paso específico de F3.
- `05_Motor`: no modificar todavía.
- `06_SQL`: no modificar todavía.
- `07_Pruebas`: no modificar todavía.

---

# 9. PRINCIPIO DE NO INFERENCIA

La coincidencia del número o familia de un ID no demuestra una relación funcional.

Una relación parámetro → regla solo se considerará confirmada cuando exista evidencia documental suficiente.

Para `GAP-HIS-01` y `GAP-HIS-02`, dicha evidencia queda formalizada en `04_Reglas/Especificacion_Reglas_Historico_MVP.md` y reflejada en `02_Parametros/Matriz_Parametros_Reglas_MVP.md`.

---

# 10. CRITERIO DE CIERRE

Los GAPs funcionales quedan cerrados cuando la decisión está registrada y los documentos de autoridad afectados están identificados.

Los GAPs de migración documental permanecen abiertos hasta completar la actualización controlada y su posterior auditoría.

`C-07`, `GAP-HIS-01` y `GAP-HIS-02` quedan cerrados funcional y documentalmente para sus respectivas relaciones.

---

# 11. ESTADO

**Versión:** 0.6  
**Estado:** APROBADO — C-07 / GAP-HIS-01 / GAP-HIS-02 CERRADOS  
**Baseline:** EIOS Vertical MVP
