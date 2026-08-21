# REGISTRO DE EVIDENCIAS DE TRAZABILIDAD — F3

## EIOS — Enterprise Intelligent Operations System

**Versión:** 1.0  
**Estado:** EN CONSTRUCCIÓN — F3  
**Ámbito:** EIOS Vertical MVP  
**Fecha:** 21/08/2026  
**Especificación aplicable:** `00_Gobierno/Especificacion_Evidencia_Trazabilidad_F3.md`

---

# 1. PROPÓSITO

Registro operativo de las evidencias utilizadas para cerrar la trazabilidad entre datos, parámetros, reglas, resultados y CRC.

Este documento **no crea ni modifica** parámetros o reglas. Registra únicamente la evidencia encontrada y su estado.

---

# 2. ESTADOS DE CONTROL

- **DEMOSTRADA:** relación expresamente acreditada y reproducible.
- **NO DEMOSTRADA:** existe la entidad, pero la relación no está acreditada.
- **NO IDENTIFICADA:** no se ha localizado la entidad o fuente buscada.
- **GAP:** falta una definición o dependencia necesaria para completar una cadena crítica.
- **CONFLICTIVA:** existen fuentes incompatibles o autoridades concurrentes.

---

# 3. EVIDENCIAS F3 — HISTÓRICO

## EVID-HIS-001

**Relación auditada:** `R-HIS-001` → antigüedad máxima de referencia  
**Origen:** `R-HIS-001`  
**Destino candidato:** `PRE-003` / `DAT-002`  
**Tipo de relación:** REGLA → PARAMETRO  
**Fuente primaria:** `04_Reglas/Matriz_Reglas_MVP.md`  
**Fuente secundaria:** `02_Parametros/Catalogo_Parametros_MVP_v0.3.md`  
**Evidencia encontrada:** `R-HIS-001` establece que la referencia no puede superar la antigüedad máxima configurada. El catálogo contiene `PRE-003` y `DAT-002`, ambos relacionados semánticamente con antigüedad de referencia.  
**Evidencia-tipo:** CONTEXTUAL  
**Estado:** GAP  
**Conclusión:** no está demostrado qué parámetro es el consumidor efectivo de `R-HIS-001`. La coincidencia de valor no permite resolver la dependencia.  
**Acción:** mantener ambos parámetros sin modificación y buscar evidencia documental/técnica adicional.

---

## EVID-HIS-002

**Relación auditada:** `R-HIS-002` → mínimo histórico/comparable  
**Origen:** `R-HIS-002`  
**Destino candidato:** `PRE-006` / `DAT-003`  
**Tipo de relación:** REGLA → PARAMETRO  
**Fuente primaria:** `04_Reglas/Matriz_Reglas_MVP.md`  
**Fuente secundaria:** `02_Parametros/Catalogo_Parametros_MVP_v0.3.md`  
**Evidencia encontrada:** `R-HIS-002` exige un número mínimo de operaciones comparables. El catálogo contiene `PRE-006` (compras comparables) y `DAT-003` (registros históricos).  
**Evidencia-tipo:** CONTEXTUAL  
**Estado:** GAP  
**Conclusión:** no está demostrado si `PRE-006`, `DAT-003`, ambos o una relación derivada alimentan la regla. No se consideran duplicados por compartir valor.  
**Acción:** mantener ambos parámetros sin modificación y buscar evidencia adicional.

---

## EVID-HIS-003

**Relación auditada:** `R-HIS-003` → parámetro de comparabilidad  
**Origen:** `R-HIS-003`  
**Destino candidato:** no identificado  
**Tipo de relación:** REGLA → PARAMETRO  
**Fuente primaria:** `04_Reglas/Matriz_Reglas_MVP.md`  
**Evidencia encontrada:** la regla evalúa diferencias de cantidad, proveedor, condiciones, descuentos, rappels, plazo de pago y características del artículo. No se ha localizado un parámetro específico que establezca un umbral único de comparabilidad.  
**Evidencia-tipo:** DIRECTA para la existencia y contenido de la regla; NO IDENTIFICADA para un parámetro específico.  
**Estado:** NO DEMOSTRADA  
**Conclusión:** no existe base para crear un `HIS-*` únicamente por la ausencia de un parámetro identificado. La regla puede ser lógica/derivada del motor.  
**Acción:** no crear parámetros; mantener abierta la determinación arquitectónica.

---

# 4. EVIDENCIAS DE RELACIÓN CON PRECIO

## EVID-HIS-004

**Relación auditada:** `R-HIS-*` → `R-PRE-001`  
**Origen:** reglas `R-HIS-001/002/003`  
**Destino:** `R-PRE-001`  
**Tipo de relación:** REGLA → REGLA  
**Fuente:** `04_Reglas/Matriz_Reglas_MVP.md`  
**Evidencia encontrada:** `R-PRE-001` requiere una operación comparable y suficientemente reciente conforme a parámetros configurados. Las reglas `R-HIS-*` definen criterios de antigüedad, suficiencia histórica y comparabilidad.  
**Evidencia-tipo:** CONTEXTUAL  
**Estado:** NO DEMOSTRADA  
**Conclusión:** existe relación funcional plausible, pero la documentación no establece una dependencia formal `R-HIS-* → R-PRE-001`. No se debe convertir esta relación en dependencia oficial sin evidencia adicional.

---

# 5. CONTROL DE DUPLICIDADES

## DUP-HIS-001

**Pares:** `PRE-003` ↔ `DAT-002`  
**Clasificación:** PENDIENTE  
**Estado:** NO RESUELTO  
**Regla de control:** conservar ambos hasta demostrar equivalencia funcional, relación maestro/derivado o diferencia de ámbito.

## DUP-HIS-002

**Pares:** `PRE-006` ↔ `DAT-003`  
**Clasificación:** PENDIENTE  
**Estado:** NO RESUELTO  
**Regla de control:** conservar ambos hasta demostrar equivalencia funcional, relación maestro/derivado o diferencia de ámbito.

---

# 6. DECISIONES NEGATIVAS REGISTRADAS

Las siguientes acciones quedan expresamente descartadas mientras no aparezca evidencia nueva:

- crear parámetros `HIS-*` para cubrir la ausencia de trazabilidad;
- fusionar `PRE-003` con `DAT-002`;
- fusionar `PRE-006` con `DAT-003`;
- modificar `04_Reglas/Matriz_Reglas_MVP.md` por inferencia;
- modificar `02_Parametros/Catalogo_Parametros_MVP_v0.3.md` por inferencia;
- crear `Rule_Dependency_Matrix.md` como solución artificial al GAP.

---

# 7. CRITERIO DE CIERRE

Una evidencia solo podrá pasar a **DEMOSTRADA** cuando la relación pueda reproducirse desde una fuente real, con ubicación identificable, autoridad documental conocida y sin depender de similitud semántica como prueba principal.

Todo cambio posterior deberá conservar la cadena:

`EVID-ID → fuente → evidencia → decisión → modificación → commit`

---

# 8. ESTADO DEL REGISTRO

| Bloque | Estado |
|---|---|
| HIS-001 | 🔴 GAP |
| HIS-002 | 🔴 GAP |
| HIS-003 | 🟡 No demostrada |
| HIS-004 | 🟡 No demostrada |
| Duplicidad PRE-003 / DAT-002 | 🔴 Pendiente |
| Duplicidad PRE-006 / DAT-003 | 🔴 Pendiente |
| Modificación de catálogo | ⛔ Bloqueada |
| Modificación de reglas | ⛔ Bloqueada |
