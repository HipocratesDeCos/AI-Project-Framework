# ESPECIFICACIÓN DE REGLAS HISTÓRICO — MVP

## EIOS — Enterprise Intelligent Operations System

**Versión:** 1.2  
**Estado:** CERRADO — GAP-HIS-01 / GAP-HIS-02  
**Baseline:** EIOS Vertical MVP  
**Fecha:** 22/08/2026  
**Ámbito:** Resolución documental de relaciones histórico → regla

---

# 1. PROPÓSITO

Este documento establece la evidencia especializada utilizada para resolver documentalmente `GAP-HIS-01` y `GAP-HIS-02` definidos en `00_Gobierno/Especificacion_Evidencia_Trazabilidad_F3.md`.

Su finalidad es determinar, sin inferencias por similitud de nombres o valores:

1. cuál es el parámetro efectivo de cada regla histórica;
2. si existen parámetros duplicados;
3. si existe una relación maestro → derivado;
4. cuál es la autoridad documental de la relación;
5. qué evidencia permite cerrar cada GAP.

---

# 2. CRITERIO DE EVIDENCIA

Una relación parámetro → regla solo podrá clasificarse como DEMOSTRADA cuando exista evidencia reproducible procedente de una fuente documental real, con ubicación identificable y autoridad conocida.

La coincidencia de nombre, prefijo, unidad, valor inicial o familia no constituye por sí misma evidencia suficiente.

---

# 3. FUENTES CONTRASTADAS Y VERSIONES DE CIERRE

Para la resolución se han contrastado y alineado las siguientes fuentes:

- `02_Parametros/Catalogo_Parametros_MVP_v0.3.md` v0.3;
- `02_Parametros/Matriz_Parametros_Reglas_MVP.md` v0.8;
- `02_Parametros/Decision_Log_Parametros_MVP.md` v0.6;
- `04_Reglas/Matriz_Reglas_MVP.md` v2.1;
- `00_Gobierno/Especificacion_Evidencia_Trazabilidad_F3.md` v1.2;
- `00_Gobierno/Registro_Evidencias_Trazabilidad_F3.md` v1.2;
- este documento `04_Reglas/Especificacion_Reglas_Historico_MVP.md` v1.2.

---

# 4. EVID-HIS-001 — GAP-HIS-01

## 4.1 Relación investigada

```text
P-PRE-003 / P-DAT-002
        ↓
R-HIS-001
```

### Regla

`R-HIS-001 — Referencia demasiado antigua`.

La regla evalúa si la compra utilizada como referencia supera la antigüedad máxima configurada.

### Determinación del parámetro efectivo

**PARÁMETRO EFECTIVO: `P-DAT-002`**

La decisión `C-01` registrada en `02_Parametros/Decision_Log_Parametros_MVP.md` v0.6 establece que `P-PRE-003` se mantiene como criterio/metodología histórica y no como parámetro directo. La `Matriz_Parametros_Reglas_MVP.md` v0.8 identifica `P-DAT-002 → R-HIS-001` como relación directa.

### Duplicidad / maestro → derivado

`P-PRE-003` y `P-DAT-002` **no se clasifican como duplicidad funcional del MVP** porque la documentación les asigna papeles distintos: criterio/metodología frente a parámetro configurable consumidor.

**No existe evidencia documental de una transformación `P-PRE-003 → P-DAT-002`; por tanto, no existe relación maestro → derivado demostrada.**

### Conclusión

`R-HIS-001` utiliza `P-DAT-002` como parámetro configurable de antigüedad de referencia. `P-PRE-003` no es consumidor directo.

**Estado: 🟢 CERRADO — EVIDENCIA DOCUMENTAL.**

---

# 5. EVID-HIS-002 — GAP-HIS-02

## 5.1 Relación investigada

```text
P-PRE-006 / P-DAT-003
        ↓
R-HIS-002
```

### Regla

`R-HIS-002 — Histórico insuficiente`.

La regla determina si no existe el número mínimo de operaciones comparables establecido.

### Determinación del parámetro efectivo

**PARÁMETRO EFECTIVO: `P-PRE-006`**

`04_Reglas/Matriz_Reglas_MVP.md` v2.1 establece que `R-HIS-002` trabaja con el número mínimo de operaciones comparables. `02_Parametros/Matriz_Parametros_Reglas_MVP.md` v0.8 identifica `P-PRE-006 → R-HIS-002` como relación directa y establece que `P-DAT-003` no tiene consumidor directo de regla MVP demostrado.

### Duplicidad / maestro → derivado

`P-PRE-006` y `P-DAT-003` **no se clasifican como duplicidad funcional del MVP** porque representan ámbitos funcionales distintos: mínimo de operaciones comparables frente a disponibilidad/registro histórico.

**No existe evidencia documental de una transformación `P-DAT-003 → P-PRE-006`; por tanto, no existe relación maestro → derivado demostrada.**

### Conclusión

`P-PRE-006` es el parámetro configurable efectivo de `R-HIS-002`. `P-DAT-003` no sustituye a `P-PRE-006` y no tiene consumidor directo demostrado en el MVP actual.

**Estado: 🟢 CERRADO — EVIDENCIA DOCUMENTAL.**

---

# 6. MATRIZ FINAL DE DETERMINACIÓN

| GAP | Parámetro efectivo | Regla consumidora | Duplicidad | Maestro → derivado | Estado |
|---|---|---|---|---|---|
| GAP-HIS-01 | `P-DAT-002` | `R-HIS-001` | NO | NO DEMOSTRADO | **CERRADO** |
| GAP-HIS-02 | `P-PRE-006` | `R-HIS-002` | NO | NO DEMOSTRADO | **CERRADO** |

---

# 7. AUTORIDAD DOCUMENTAL

La resolución se sustenta en la cadena documental alineada:

```text
Matriz de Reglas v2.1
        ↓
Matriz Parámetros → Reglas v0.8
        ↓
Decision Log v0.6
        ↓
Especificación Histórica v1.2
        ↓
Registro de Evidencias F3 v1.2
        ↓
Especificación F3 v1.2
```

Ninguna conclusión de cierre depende exclusivamente de similitud semántica o coincidencia de valores.

---

# 8. PROHIBICIONES

Este documento no autoriza:

1. crear parámetros `HIS-*` artificialmente;
2. elegir un parámetro por coincidencia de nombre;
3. elegir un parámetro por coincidencia de valor;
4. declarar duplicidad sin comparar ámbito y consumidor;
5. declarar maestro → derivado sin transformación documentada;
6. reabrir un GAP cerrado sin nueva evidencia o conflicto documental identificable.

---

# 9. RELACIÓN CON F3

La resolución completa queda incorporada en:

- `00_Gobierno/Especificacion_Evidencia_Trazabilidad_F3.md` v1.2;
- `00_Gobierno/Registro_Evidencias_Trazabilidad_F3.md` v1.2.

La creación de parámetros `HIS-*` queda expresamente descartada.

---

# 10. CONTROL DE CAMBIOS

**v1.2 — 22/08/2026**

Se cierra el Punto 3 de resolución histórica y se alinea la referencia de versiones con los documentos oficiales utilizados en el cierre de `GAP-HIS-01` y `GAP-HIS-02`.

---

# 11. ESTADO DEL DOCUMENTO

**Versión:** 1.2  
**Estado:** 🟢 CERRADO — GAP-HIS-01 / GAP-HIS-02  
**Baseline:** EIOS Vertical MVP
