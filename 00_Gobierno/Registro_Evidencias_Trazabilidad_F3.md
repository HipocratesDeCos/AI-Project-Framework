# REGISTRO MAESTRO DE EVIDENCIAS DE TRAZABILIDAD — F3

## EIOS — Enterprise Intelligent Operations System

**Versión:** 1.7  
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

**Regla canónica:** un `EVID-ID` identifica una única relación origen → destino. Si una fuente demuestra varias relaciones, cada relación deberá disponer de su propio `EVID-ID`.

### 3.2 `DUP-*` — Registro de análisis de duplicidad

`DUP-*` representa **un análisis documental de posible duplicidad o de posible relación maestro → derivado entre dos entidades**.

No es una `EVID-*` y no deberá forzarse dentro de la misma plantilla.

---

# 4. MODELO CANÓNICO DE `EVID-*`

Cada `EVID-*` deberá disponer, como mínimo, de los campos definidos en la estructura canónica F3:

| Campo | Obligatorio | Descripción |
|---|---:|---|
| `EVID-ID` | Sí | Identificador único y estable. |
| `Origen-ID` | Sí | Entidad de origen. |
| `Origen-tipo` | Sí | Tipo de entidad de origen. |
| `Destino-ID` | Sí | Entidad de destino. |
| `Destino-tipo` | Sí | Tipo de entidad de destino. |
| `Relación` | Sí | Tipo exacto de dependencia. |
| `Fuente` | Sí | Fuente documental real. |
| `Ubicación` | Sí | Ubicación reproducible dentro de la fuente. |
| `Extracto` | Sí | Fragmento probatorio. |
| `Evidencia-tipo` | Sí | DIRECTA / INDIRECTA / CONTEXTUAL. |
| `Estado` | Sí | Estado oficial de la evidencia. |
| `Autoridad` | Sí | Documento con autoridad sobre la relación. |
| `Versión` | Sí | Versión de la fuente. |
| `Commit` | Recomendado | Commit reproducible. |
| `Observaciones` | No | Matices y limitaciones. |

**Regla de integridad:** no se admite un `EVID-ID` que represente simultáneamente dos relaciones distintas.

---

# 5. CONTROL DE IDENTIFICADORES

Los identificadores existentes se auditan antes de normalizar su contenido.

### 5.1 Identificadores históricos `EVID-HIS-*`

- `EVID-HIS-001` → único.
- `EVID-HIS-002` → único.
- `EVID-HIS-003` → único.
- `EVID-HIS-004` → único.

No se renumeran.

### 5.2 Identificadores `EVID-PAG-*`

- `EVID-PAG-001` → único.
- `EVID-PAG-002` → único.
- `EVID-PAG-003` → único.
- `EVID-PAG-004` → identificador único, pero su contenido original agrupa dos relaciones.
- `EVID-PAG-005` → identificador único, pero su contenido original agrupa dos relaciones.

Por tanto, `EVID-PAG-004` y `EVID-PAG-005` requieren **desdoblamiento funcional**.

---

# 6. NORMALIZACIÓN DE RELACIONES MÚLTIPLES

## 6.1 `EVID-PAG-004`

El registro histórico agrupaba:

`P-PAG-004 → R-PAG-001 / R-PAG-002`

Esto contradice la regla canónica de **una evidencia = una relación**.

Se conserva `EVID-PAG-004` como identificador histórico y se desdobla en:

- `EVID-PAG-004-A` → `P-PAG-004 → R-PAG-001`
- `EVID-PAG-004-B` → `P-PAG-004 → R-PAG-002`

`EVID-PAG-004` queda como **identificador padre histórico / agrupador**, no como evidencia canónica independiente.

## 6.2 `EVID-PAG-005`

El registro histórico agrupaba:

`P-PAG-005 → R-PAG-001 / R-PAG-002`

Se desdobla en:

- `EVID-PAG-005-A` → `P-PAG-005 → R-PAG-001`
- `EVID-PAG-005-B` → `P-PAG-005 → R-PAG-002`

`EVID-PAG-005` queda como **identificador padre histórico / agrupador**, no como evidencia canónica independiente.

### Regla de compatibilidad

Los identificadores padre no se eliminan para conservar trazabilidad histórica. Las nuevas referencias auditables deberán utilizar exclusivamente los identificadores hoja `*-A` / `*-B`.

---

# 7. INVENTARIO CANÓNICO DE EVIDENCIAS

| EVID-ID canónico | Origen | Destino | Estado de normalización |
|---|---|---|---|
| `EVID-HIS-001` | `P-DAT-002` | `R-HIS-001` | IDENTIFICADOR VALIDADO |
| `EVID-HIS-002` | `P-PRE-006` | `R-HIS-002` | IDENTIFICADOR VALIDADO |
| `EVID-HIS-003` | `R-HIS-003` | LÓGICA DERIVADA | IDENTIFICADOR VALIDADO |
| `EVID-HIS-004` | `R-HIS-*` | `R-PRE-001` | IDENTIFICADOR VALIDADO — RELACIÓN NO DEMOSTRADA |
| `EVID-PAG-001` | `P-PAG-001` | `R-PAG-002` | IDENTIFICADOR VALIDADO |
| `EVID-PAG-002` | `P-PAG-002` | `R-PAG-001` | IDENTIFICADOR VALIDADO |
| `EVID-PAG-003` | `P-PAG-003` | `R-PAG-001` | IDENTIFICADOR VALIDADO |
| `EVID-PAG-004-A` | `P-PAG-004` | `R-PAG-001` | NUEVO ID HOJA — DESDOBLADO |
| `EVID-PAG-004-B` | `P-PAG-004` | `R-PAG-002` | NUEVO ID HOJA — DESDOBLADO |
| `EVID-PAG-005-A` | `P-PAG-005` | `R-PAG-001` | NUEVO ID HOJA — DESDOBLADO |
| `EVID-PAG-005-B` | `P-PAG-005` | `R-PAG-002` | NUEVO ID HOJA — DESDOBLADO |

Los `DUP-HIS-001/002` permanecen fuera de este inventario porque son objetos `DUP-*`, no evidencias `EVID-*`.

---

# 8. RELACIÓN CON `DUP-*`

`DUP-*` mantiene el modelo canónico definido en la versión anterior.

`DUP-HIS-001` se sustenta documentalmente en `EVID-HIS-001` y en la decisión `C-01`.

`DUP-HIS-002` se sustenta documentalmente en `EVID-HIS-002` y en la decisión `GAP-HIS-02`.

Los identificadores `DUP-*` no se transforman en `EVID-*`.

---

# 9. ESTADOS DE `DUP-*`

Los estados de `DUP-*` son independientes de los estados de evidencia.

| Estado DUP | Significado |
|---|---|
| **PENDIENTE DE ANÁLISIS** | Posible duplicidad identificada, análisis insuficiente. |
| **EN ANÁLISIS** | Contraste documental en curso. |
| **NO RESUELTO** | Analizado, pero sin conclusión suficiente. |
| **RESUELTO** | Clasificación documental suficiente y decisión registrada cuando corresponde. |
| **CONFLICTIVO** | Autoridades o documentos incompatibles. |

---

# 10. ESTADOS DE EVIDENCIA

Los estados de evidencia F3 permanecen definidos por la nomenclatura oficial del Registro:

- `PENDIENTE DE NORMALIZACIÓN`
- `NO IDENTIFICADA`
- `NO DEMOSTRADA`
- `GAP`
- `CONFLICTIVA`
- `DEMOSTRADA`
- `CERRADA`

La normalización de un `EVID-ID` **no implica automáticamente que pase a `DEMOSTRADA` o `CERRADA`**.

---

# 11. RESULTADO DEL PASO 2

El control de identificadores ha quedado completado.

### Resultado

- No existen `EVID-ID` duplicados.
- No se renumeran los `EVID-HIS-*` ni `EVID-PAG-001…003`.
- Se detectaron dos evidencias históricas que agrupaban relaciones múltiples.
- Se desdoblaron en cuatro identificadores hoja:
  - `EVID-PAG-004-A`
  - `EVID-PAG-004-B`
  - `EVID-PAG-005-A`
  - `EVID-PAG-005-B`
- Los identificadores padre se conservan únicamente como referencia histórica/agrupadora.
- `DUP-HIS-001/002` permanecen correctamente separados como objetos `DUP-*`.

**Estado del Paso 2: CERRADO.**

---

# 12. CONTROL DE CAMBIOS

**v1.7 — 22/08/2026**

Se valida la unicidad de los `EVID-ID` y se aplica la regla canónica de una relación por evidencia. Se desdoblan las relaciones múltiples históricas de `EVID-PAG-004` y `EVID-PAG-005` en identificadores hoja `-A` / `-B`, conservando los identificadores padre como referencia histórica.
