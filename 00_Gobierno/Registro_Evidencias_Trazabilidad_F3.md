# REGISTRO MAESTRO DE EVIDENCIAS DE TRAZABILIDAD — F3

## EIOS — Enterprise Intelligent Operations System

**Versión:** 1.6  
**Estado:** ACTIVO — REGISTRO MAESTRO DE EVIDENCIAS F3  
**Ámbito:** EIOS Vertical MVP  
**Fecha:** 22/08/2026  
**Especificación aplicable:** `00_Gobierno/Especificacion_Evidencia_Trazabilidad_F3.md` v1.2

---

# 1. PROPÓSITO

Este documento constituye el **Registro Maestro de Evidencias de Trazabilidad F3** de EIOS.

Es el registro oficial donde se identifican, clasifican, conservan y controlan las evidencias utilizadas para demostrar la trazabilidad entre datos, parámetros, cálculos, reglas, resultados, excepciones, CRC, recomendaciones y los documentos o componentes que intervienen en dichas relaciones.

Este documento no crea ni modifica parámetros o reglas. Registra y gobierna el estado de la evidencia que demuestra las relaciones documentales o funcionales del sistema.

---

# 2. AUTORIDAD DEL REGISTRO MAESTRO

Este archivo es la fuente maestra de registro de evidencias F3.

Las fuentes originales conservan la autoridad sobre su propio contenido; este registro es la autoridad sobre el **estado, identidad y trazabilidad de las evidencias F3**.

Toda evidencia F3 oficial deberá disponer de un identificador único y estable. Las evidencias no demostradas, GAP o conflictivas no podrán convertirse en cerradas por inferencia, similitud semántica o conveniencia del proyecto.

---

# 3. MODELO DE OBJETOS F3

El Registro distingue dos objetos documentales relacionados pero diferentes:

### 3.1 `EVID-*` — Evidencia de relación

`EVID-*` representa **una relación concreta cuya existencia, ausencia o estado de demostración puede ser auditado**.

Ejemplos:

- `P-DAT-002 → R-HIS-001`
- `P-PRE-006 → R-HIS-002`
- `P-PAG-001 → R-PAG-002`

Una `EVID-*` utiliza la estructura canónica de evidencia definida en este Registro.

### 3.2 `DUP-*` — Registro de análisis de duplicidad

`DUP-*` representa **un análisis documental de posible duplicidad o de posible relación maestro → derivado entre dos entidades**.

No es una `EVID-*` y **no deberá forzarse dentro de la misma plantilla**.

Un `DUP-*` responde a la pregunta:

> «¿Las dos entidades comparadas representan el mismo concepto funcional, o existe entre ellas una relación maestro → derivado?»

El `DUP-*` registra el análisis y la decisión; las evidencias que sustentan ese análisis se registran mediante uno o varios `EVID-*`.

---

# 4. MODELO CANÓNICO DE `DUP-*`

Cada registro de duplicidad deberá contener como mínimo:

| Campo | Obligatorio | Descripción |
|---|---:|---|
| `DUP-ID` | Sí | Identificador único y estable del análisis. |
| `Entidad-A-ID` | Sí | Primera entidad comparada. |
| `Entidad-A-tipo` | Sí | Tipo de entidad A. |
| `Entidad-B-ID` | Sí | Segunda entidad comparada. |
| `Entidad-B-tipo` | Sí | Tipo de entidad B. |
| `Hipótesis` | Sí | Motivo por el que se sospecha duplicidad o relación maestro → derivado. |
| `Criterios` | Sí | Criterios utilizados para comparar las entidades. |
| `EVID-IDs soporte` | Sí | Evidencias F3 que sustentan el análisis. |
| `Resultado` | Sí | Clasificación final del análisis. |
| `Decisión-ID` | Condicional | Decisión formal que resuelve el análisis, cuando exista. |
| `Autoridad` | Sí | Documento con autoridad para resolver la clasificación. |
| `Fuente` | Sí | Fuentes documentales utilizadas. |
| `Versión` | Sí | Versión de las fuentes relevantes. |
| `Commit` | Recomendado | Commit reproducible de la evidencia documental. |
| `Estado` | Sí | Estado del análisis DUP. |
| `Observaciones` | No | Matices o limitaciones. |

---

# 5. RESULTADOS CANÓNICOS DE `DUP-*`

El campo `Resultado` solo podrá adoptar uno de estos valores:

- **DUPLICIDAD REAL** — las entidades representan funcionalmente el mismo concepto en el mismo ámbito y debe resolverse su coexistencia.
- **CONCEPTOS DISTINTOS** — la similitud inicial no implica duplicidad funcional.
- **MAESTRO → DERIVADO** — existe una transformación o dependencia explícitamente demostrada.
- **GAP DE DEFINICIÓN** — la documentación disponible no permite determinar la clasificación.
- **CONFLICTO DE AUTORIDAD** — existen fuentes con autoridad incompatible.

No se utilizarán sinónimos como sustitutos de estos resultados.

---

# 6. RELACIÓN ENTRE `EVID-*` Y `DUP-*`

La arquitectura documental queda establecida así:

```text
EVID-*  = evidencia observable de una relación
                 ↓
DUP-*   = análisis de posible duplicidad / maestro-derivado
                 ↓
Decisión = resolución formal, cuando corresponda
```

Una `DUP-*` puede requerir varias `EVID-*`.

Una `EVID-*` no implica por sí sola que exista una duplicidad.

Un `DUP-*` no podrá declararse resuelto si no identifica las evidencias que sustentan su resultado, salvo que la fuente de autoridad documente directamente la decisión y quede identificada como tal.

---

# 7. ESTADOS DE `DUP-*`

Los estados de `DUP-*` se separan de los estados de evidencia `EVID-*`.

| Estado DUP | Significado |
|---|---|
| **PENDIENTE DE ANÁLISIS** | Se ha identificado una posible duplicidad, pero todavía no se ha realizado el análisis suficiente. |
| **EN ANÁLISIS** | El contraste documental está en curso. |
| **NO RESUELTO** | Se ha analizado, pero la documentación no permite una conclusión suficiente. |
| **RESUELTO** | Existe una clasificación documental suficiente y una decisión registrada cuando corresponde. |
| **CONFLICTIVO** | Existen autoridades o documentos incompatibles que impiden resolverlo. |

`DUP-*` **no utiliza** `DEMOSTRADA` o `CERRADA` como estados propios. Esos estados pertenecen a `EVID-*`.

---

# 8. MODELO CANÓNICO APLICADO A LOS DUP-HIS EXISTENTES

## DUP-HIS-001

**Entidad-A:** `P-PRE-003`  
**Entidad-B:** `P-DAT-002`  
**Hipótesis:** posible duplicidad / posible relación maestro → derivado por similitud funcional relativa a la antigüedad histórica de referencia.  
**Resultado:** **CONCEPTOS DISTINTOS**  
**Resolución:** `P-PRE-003` queda como criterio/metodología histórica; `P-DAT-002` es el parámetro configurable consumidor de `R-HIS-001`. No existe transformación documental demostrada entre ambos.  
**Evidencias soporte:** `EVID-HIS-001` y la evidencia/decisión documental asociada al análisis `C-01`.  
**Autoridad:** `02_Parametros/Decision_Log_Parametros_MVP.md` v0.6, complementado por `02_Parametros/Matriz_Parametros_Reglas_MVP.md` v0.8 y `04_Reglas/Especificacion_Reglas_Historico_MVP.md` v1.2.  
**Estado:** **RESUELTO**

## DUP-HIS-002

**Entidad-A:** `P-PRE-006`  
**Entidad-B:** `P-DAT-003`  
**Hipótesis:** posible duplicidad / posible relación maestro → derivado relativa al número mínimo de registros u operaciones históricas.  
**Resultado:** **CONCEPTOS DISTINTOS**  
**Resolución:** `P-PRE-006` representa el mínimo de operaciones comparables consumido por `R-HIS-002`; `P-DAT-003` representa un criterio distinto de disponibilidad/registro histórico y no sustituye a `P-PRE-006`. No existe transformación documental demostrada entre ambos.  
**Evidencias soporte:** `EVID-HIS-002` y la evidencia/decisión documental asociada al análisis `GAP-HIS-02`.  
**Autoridad:** `02_Parametros/Decision_Log_Parametros_MVP.md` v0.6, complementado por `02_Parametros/Matriz_Parametros_Reglas_MVP.md` v0.8 y `04_Reglas/Especificacion_Reglas_Historico_MVP.md` v1.2.  
**Estado:** **RESUELTO**

---

# 9. REGLAS DE GOBIERNO PARA DUPLICIDADES

**DUP-01 — No inferencia:** similitud de nombre, código, unidad o valor no demuestra duplicidad.

**DUP-02 — Comparación obligatoria:** toda posible duplicidad deberá contrastar definición, ámbito, consumidor, autoridad y ciclo de vida; cuando aplique también unidad y valor por defecto.

**DUP-03 — Maestro → derivado:** solo podrá utilizarse este resultado cuando exista una transformación o dependencia explícitamente documentada.

**DUP-04 — Evidencia soporte:** todo `DUP-*` deberá identificar las `EVID-*` que sustentan su resultado.

**DUP-05 — Decisión:** cuando el resultado implique modificar, fusionar, reclasificar o retirar una entidad, deberá existir una decisión formal registrada.

**DUP-06 — No cierre artificial:** no se resolverá una posible duplicidad únicamente para eliminar un GAP del mapa.

**DUP-07 — Separación de estados:** los estados de `DUP-*` no se mezclarán con los estados de `EVID-*`.

---

# 10. PLANTILLA CANÓNICA `DUP-*`

```markdown
## DUP-[DOMINIO]-[NNN]

**Entidad-A-ID:** `[ID]`
**Entidad-A-tipo:** `[TIPO]`
**Entidad-B-ID:** `[ID]`
**Entidad-B-tipo:** `[TIPO]`
**Hipótesis:** `[MOTIVO DEL ANÁLISIS]`
**Criterios:** `[DEFINICIÓN / ÁMBITO / CONSUMIDOR / AUTORIDAD / CICLO DE VIDA / OTROS]`
**EVID-IDs soporte:** `[EVID-ID, EVID-ID...]`
**Resultado:** `[RESULTADO CANÓNICO]`
**Decisión-ID:** `[ID, SI CORRESPONDE]`
**Autoridad:** `[DOCUMENTO CON AUTORIDAD]`
**Fuente:** `[RUTAS / FUENTES]`
**Versión:** `[VERSIONES]`
**Commit:** `[SHA, SI PROCEDE]`
**Estado:** `[ESTADO DUP]`
**Observaciones:** `[MATICES / LIMITACIONES]`
```

---

# 11. ESTADO DEL REGISTRO

La normalización de `DUP-HIS-001/002` se considera **MODELO CANÓNICO DEFINIDO** y sus resultados actuales quedan clasificados como **RESUELTO / CONCEPTOS DISTINTOS**.

La normalización física de todas las evidencias `EVID-*` existentes continúa en el proceso general de normalización.

---

# 12. CONTROL DE CAMBIOS

**v1.6 — 22/08/2026**

Se establece el modelo canónico de `DUP-*` como objeto documental distinto de `EVID-*`, se definen sus campos, resultados, estados, relación con evidencias y se normaliza conceptualmente `DUP-HIS-001/002` como análisis de duplicidad resuelto.
