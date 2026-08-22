# REGISTRO DE EVIDENCIAS DE TRAZABILIDAD — F3

## EIOS — Enterprise Intelligent Operations System

**Versión:** 1.2  
**Estado:** CERRADO — F3 / C-07 / GAP-HIS-01 / GAP-HIS-02  
**Ámbito:** EIOS Vertical MVP  
**Fecha:** 22/08/2026  
**Especificación aplicable:** `00_Gobierno/Especificacion_Evidencia_Trazabilidad_F3.md` v1.2

---

# 1. PROPÓSITO

Registro operativo de las evidencias utilizadas para cerrar la trazabilidad entre datos, parámetros, reglas, resultados y CRC.

Este documento no crea ni modifica parámetros o reglas. Registra la evidencia encontrada y su estado.

---

# 2. ESTADOS DE CONTROL

- **DEMOSTRADA:** relación expresamente acreditada y reproducible.
- **NO DEMOSTRADA:** existe la entidad, pero la relación no está acreditada.
- **NO IDENTIFICADA:** no se ha localizado la entidad o fuente buscada.
- **GAP:** falta una definición o dependencia necesaria para completar una cadena crítica.
- **CONFLICTIVA:** existen fuentes incompatibles o autoridades concurrentes.
- **CERRADA:** evidencia y documentos de autoridad afectados se encuentran alineados.

---

# 3. EVIDENCIAS F3 — HISTÓRICO

## EVID-HIS-001

**Relación auditada:** `R-HIS-001` → antigüedad máxima de referencia  
**Parámetro consumidor:** `P-DAT-002`  
**Tipo de relación:** REGLA → PARAMETRO  
**Fuente primaria:** `04_Reglas/Matriz_Reglas_MVP.md` v2.1  
**Fuente secundaria:** `02_Parametros/Matriz_Parametros_Reglas_MVP.md` v0.8  
**Decisión aplicable:** `C-01` de `02_Parametros/Decision_Log_Parametros_MVP.md` v0.6  
**Expediente especializado:** `04_Reglas/Especificacion_Reglas_Historico_MVP.md` v1.2  
**Evidencia encontrada:** `C-01` establece que `P-PRE-003` se mantiene como criterio/metodología y no como parámetro directo. La Matriz de Parámetros establece `P-DAT-002 → R-HIS-001` como relación directa. El expediente histórico documenta además que no existe relación maestro → derivado demostrada.  
**Evidencia-tipo:** DIRECTA  
**Estado:** CERRADA  
**Conclusión:** `R-HIS-001` utiliza `P-DAT-002` como parámetro configurable de antigüedad de referencia. `P-PRE-003` no es consumidor directo.

---

## EVID-HIS-002

**Relación auditada:** `R-HIS-002` → mínimo histórico/comparable  
**Parámetro consumidor:** `P-PRE-006`  
**Tipo de relación:** REGLA → PARAMETRO  
**Fuente primaria:** `04_Reglas/Matriz_Reglas_MVP.md` v2.1  
**Fuente secundaria:** `02_Parametros/Matriz_Parametros_Reglas_MVP.md` v0.8  
**Decisión aplicable:** `GAP-HIS-02` de `02_Parametros/Decision_Log_Parametros_MVP.md` v0.6  
**Expediente especializado:** `04_Reglas/Especificacion_Reglas_Historico_MVP.md` v1.2  
**Evidencia encontrada:** `R-HIS-002` exige un número mínimo de operaciones comparables. La Matriz de Parámetros establece `P-PRE-006 → R-HIS-002` como relación directa y distingue `P-DAT-003` como parámetro sin consumidor directo demostrado. El expediente histórico documenta además que no existe relación maestro → derivado demostrada.  
**Evidencia-tipo:** DIRECTA  
**Estado:** CERRADA  
**Conclusión:** `P-PRE-006` es el parámetro configurable que establece el mínimo de operaciones comparables para `R-HIS-002`. `P-DAT-003` no sustituye este parámetro.

---

## EVID-HIS-003

**Relación auditada:** `R-HIS-003` → parámetro de comparabilidad  
**Origen:** `R-HIS-003`  
**Destino:** no se crea parámetro específico  
**Tipo de relación:** REGLA → LÓGICA DERIVADA  
**Fuente primaria:** `04_Reglas/Matriz_Reglas_MVP.md` v2.1  
**Evidencia encontrada:** la regla evalúa diferencias de cantidad, proveedor, condiciones, descuentos, rappels, plazo de pago y características del artículo. No se ha identificado un parámetro único que deba crearse para representar toda la comparabilidad.  
**Evidencia-tipo:** DIRECTA  
**Estado:** CERRADA  
**Conclusión:** no se crea un `HIS-*` artificial. La comparabilidad queda como lógica derivada del motor.

---

# 4. EVIDENCIAS DE RELACIÓN CON PRECIO

## EVID-HIS-004

**Relación auditada:** `R-HIS-*` → `R-PRE-001`  
**Tipo de relación:** REGLA → REGLA  
**Fuente:** `04_Reglas/Matriz_Reglas_MVP.md` v2.1  
**Estado:** NO DEMOSTRADA COMO DEPENDENCIA FORMAL  
**Conclusión:** existe relación funcional contextual, pero no se convierte en dependencia oficial sin evidencia adicional.

---

# 5. EVIDENCIAS F3 — PAGOS / C-07

## EVID-PAG-001

**Relación:** `P-PAG-001 → R-PAG-002`  
**Tipo:** DIRECTA  
**Evidencia primaria:** `04_Reglas/Especificacion_Reglas_Configuracion_Pagos_MVP.md` v1.0  
**Evidencia secundaria:** `04_Reglas/Matriz_Reglas_MVP.md` v2.1  
**Evidencia de enlace:** `02_Parametros/Matriz_Parametros_Reglas_MVP.md` v0.8  
**Estado:** DEMOSTRADA / CERRADA

## EVID-PAG-002

**Relación:** `P-PAG-002 → R-PAG-001`  
**Tipo:** DIRECTA  
**Evidencia primaria:** `04_Reglas/Especificacion_Reglas_Configuracion_Pagos_MVP.md` v1.0  
**Evidencia secundaria:** `04_Reglas/Matriz_Reglas_MVP.md` v2.1  
**Evidencia de enlace:** `02_Parametros/Matriz_Parametros_Reglas_MVP.md` v0.8  
**Estado:** DEMOSTRADA / CERRADA

## EVID-PAG-003

**Relación:** `P-PAG-003 → R-PAG-001`  
**Tipo:** DERIVADA  
**Evidencia primaria:** `04_Reglas/Especificacion_Reglas_Configuracion_Pagos_MVP.md` v1.0  
**Evidencia secundaria:** `04_Reglas/Matriz_Reglas_MVP.md` v2.1  
**Evidencia de enlace:** `02_Parametros/Matriz_Parametros_Reglas_MVP.md` v0.8  
**Estado:** DEMOSTRADA / CERRADA

## EVID-PAG-004

**Relaciones:** `P-PAG-004 → R-PAG-001 / R-PAG-002`  
**Tipo:** CONTROL FUNCIONAL  
**Evidencia primaria:** `04_Reglas/Especificacion_Reglas_Configuracion_Pagos_MVP.md` v1.0  
**Evidencia secundaria:** `04_Reglas/Matriz_Reglas_MVP.md` v2.1  
**Evidencia de enlace:** `02_Parametros/Matriz_Parametros_Reglas_MVP.md` v0.8  
**Estado:** DEMOSTRADA / CERRADA

## EVID-PAG-005

**Relaciones:** `P-PAG-005 → R-PAG-001 / R-PAG-002`  
**Tipo:** INDIRECTA / DERIVADA  
**Evidencia primaria:** `04_Reglas/Especificacion_Reglas_Configuracion_Pagos_MVP.md` v1.0  
**Evidencia secundaria:** `04_Reglas/Matriz_Reglas_MVP.md` v2.1  
**Evidencia de enlace:** `02_Parametros/Matriz_Parametros_Reglas_MVP.md` v0.8  
**Estado:** DEMOSTRADA / CERRADA

### C-07 — estado de evidencia

La condición establecida por `C-07` era no asignar relaciones concretas entre parámetros de pago y reglas sin evidencia documental suficiente.

La especificación especializada de configuración de pagos aporta la evidencia funcional directa y la Matriz de Reglas y Matriz de Parámetros incorporan las relaciones. Por tanto, **C-07 queda cerrado documentalmente para `P-PAG-001…005 → R-PAG-*`.**

---

# 6. CONTROL DE DUPLICIDADES

## DUP-HIS-001

**Pares:** `P-PRE-003` ↔ `P-DAT-002`  
**Estado:** CERRADO  
**Resolución:** `C-01` mantiene `P-PRE-003` como criterio/metodología; `P-DAT-002` es el parámetro configurable consumidor de `R-HIS-001`. No existe relación maestro → derivado demostrada.

## DUP-HIS-002

**Pares:** `P-PRE-006` ↔ `P-DAT-003`  
**Estado:** CERRADO  
**Resolución:** `P-PRE-006` establece el mínimo de operaciones comparables de `R-HIS-002`; `P-DAT-003` no sustituye este parámetro y queda sin consumidor directo demostrado en el MVP actual. No existe relación maestro → derivado demostrada.

---

# 7. DECISIONES NEGATIVAS REGISTRADAS

Las siguientes acciones siguen expresamente descartadas:

- crear parámetros `HIS-*` para cubrir la ausencia de trazabilidad;
- fusionar `P-PRE-003` con `P-DAT-002`;
- fusionar `P-PRE-006` con `P-DAT-003`;
- crear una dependencia `R-HIS-* → R-PRE-001` sin evidencia adicional.

---

# 8. CRITERIO DE CIERRE

Una evidencia pasa a **DEMOSTRADA/CERRADA** cuando la relación puede reproducirse desde una fuente real, con ubicación identificable, autoridad documental conocida y sin depender de similitud semántica como prueba principal.

Todo cambio posterior deberá conservar la cadena:

`EVID-ID → fuente → evidencia → decisión → modificación → commit`

---

# 9. ESTADO DEL REGISTRO

| Bloque | Estado |
|---|---|
| HIS-001 | 🟢 CERRADO |
| HIS-002 | 🟢 CERRADO |
| HIS-003 | 🟢 CERRADO |
| HIS-004 | 🟡 No demostrada como dependencia formal |
| Duplicidad P-PRE-003 / P-DAT-002 | 🟢 CERRADA |
| Duplicidad P-PRE-006 / P-DAT-003 | 🟢 CERRADA |
| PAG-001 | 🟢 DEMOSTRADA |
| PAG-002 | 🟢 DEMOSTRADA |
| PAG-003 | 🟢 DEMOSTRADA |
| PAG-004 | 🟢 DEMOSTRADA |
| PAG-005 | 🟢 DEMOSTRADA |
| C-07 | 🟢 CERRADO |

---

# 10. CONTROL DE CAMBIOS

**v1.2 — 22/08/2026**

Se alinean las referencias de versión de `Matriz_Parametros_Reglas_MVP` a v0.8 y `Decision_Log_Parametros_MVP` a v0.6, y se incorpora `Especificacion_Reglas_Historico_MVP` v1.2 como expediente especializado de cierre de `GAP-HIS-01` y `GAP-HIS-02`.
