# REGISTRO MAESTRO DE EVIDENCIAS DE TRAZABILIDAD — F3

## EIOS — Enterprise Intelligent Operations System

**Versión:** 1.11  
**Estado:** ACTIVO — REGISTRO MAESTRO DE EVIDENCIAS F3  
**Ámbito:** EIOS Vertical MVP  
**Fecha:** 23/08/2026  
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

El Registro distingue cuatro objetos documentales:

### 3.1 `EVID-*` — Evidencia de relación

`EVID-*` representa **una relación concreta cuya existencia, ausencia o estado de demostración puede ser auditado**.

**Regla canónica:** un `EVID-ID` identifica una única relación origen → destino. Si una fuente demuestra varias relaciones, cada relación deberá disponer de su propio `EVID-ID`.

### 3.2 `DUP-*` — Registro de análisis de duplicidad

`DUP-*` representa **un análisis documental de posible duplicidad o de posible relación maestro → derivado entre dos entidades**.

No es una `EVID-*` y no deberá forzarse dentro de la misma plantilla.

### 3.3 `EVID-DESC-*` — Evidencia descriptiva de entidad/regla

`EVID-DESC-*` representa evidencia documental que **demuestra o documenta la definición, condición, resultado, efecto o comportamiento de una entidad**, pero no demuestra una relación formal `Origen → Destino` entre dos entidades.

No deberá utilizarse para crear dependencias relacionales no documentadas.

Los identificadores históricos `EVID-*` que resulten ser evidencias descriptivas conservarán su identificador original como referencia histórica, pero quedarán fuera del inventario canónico relacional.

### 3.4 `REL-FUNC-*` — Relación funcional no formalizada

`REL-FUNC-*` representa un **registro histórico de una relación funcional identificada durante el análisis, pero no formalizada documentalmente como dependencia del modelo EIOS**.

No constituye evidencia canónica, no demuestra una dependencia formal, no crea un vínculo de ejecución y no genera por sí mismo un GAP.

Cuando exista un identificador `EVID-*` histórico asociado a una relación funcional no formalizada, dicho identificador se conserva exclusivamente como **alias histórico** y se vincula al `REL-FUNC-*` correspondiente.

---

# 4. MODELO CANÓNICO DE `EVID-*`

Cada `EVID-*` relacional deberá disponer, como mínimo, de los campos definidos en la estructura canónica F3:

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

**Regla de integridad:** no se admite un `EVID-ID` relacional que represente simultáneamente dos relaciones distintas.

---

# 5. MODELO CANÓNICO DE `EVID-DESC-*`

Cada evidencia descriptiva deberá disponer, como mínimo, de:

| Campo | Obligatorio | Descripción |
|---|---:|---|
| `EVID-DESC-ID` | Sí | Identificador canónico de evidencia descriptiva. |
| `Entidad-ID` | Sí | Entidad documentada. |
| `Entidad-tipo` | Sí | Tipo de entidad. |
| `Aspecto-documentado` | Sí | Definición / condición / resultado / efecto / comportamiento. |
| `Fuente` | Sí | Fuente documental real. |
| `Ubicación` | Sí | Ubicación reproducible. |
| `Extracto` | Sí | Fragmento probatorio. |
| `Autoridad` | Sí | Documento con autoridad. |
| `Versión` | Sí | Versión de la fuente. |
| `Commit` | Recomendado | Commit reproducible. |
| `Estado` | Sí | Estado de la evidencia descriptiva. |
| `Observaciones` | No | Matices y limitaciones. |

---

# 6. RECLASIFICACIÓN DE `EVID-HIS-003`

## Identificador histórico

`EVID-HIS-003`

## Naturaleza determinada

**Evidencia descriptiva de la regla `R-HIS-003`**, no evidencia de una relación formal `Origen → Destino`.

## Evidencia documental

La `Matriz_Reglas_MVP.md` define `R-HIS-003` como **“Operación no comparable”**, establece sus condiciones y documenta como resultado **“Reducir el nivel de fiabilidad de la referencia”**. También establece que la operación no debe considerarse automáticamente equivalente a una operación comparable.

## Destino relacional

**NO APLICA.**

No se ha encontrado una entidad destino formal que permita demostrar una relación `R-HIS-003 → X`.

No se crea un destino artificial como `LÓGICA DERIVADA`, `RESULT-R-HIS-003` u otro identificador equivalente.

## Nuevo identificador descriptivo

Para el modelo canónico se conserva el identificador histórico `EVID-HIS-003` y se le asigna la clasificación canónica:

`EVID-DESC-HIS-003`

`EVID-HIS-003` queda como **alias histórico**, no como `EVID-*` relacional activo.

## Estado

**DEMOSTRADA** respecto de la definición/resultado de `R-HIS-003`.

Este estado **no significa** que exista una dependencia de `R-HIS-003` con otra regla o componente.

---

# 7. RECLASIFICACIÓN DE `EVID-HIS-004`

## Identificador histórico

`EVID-HIS-004`

## Naturaleza determinada

**Registro histórico de una relación funcional no formalizada**, no evidencia de una relación formal `Origen → Destino`.

## Relación funcional identificada

`R-HIS-003 ↔ R-PRE-001`

Las reglas presentan una relación funcional conceptual: `R-HIS-003` define criterios para determinar si una operación es comparable y `R-PRE-001` requiere una operación comparable reciente. Sin embargo, no existe documentación que establezca una dependencia formal `R-HIS-003 → R-PRE-001`.

## Identificador canónico de registro funcional

`REL-FUNC-HIS-004`

`EVID-HIS-004` queda como **alias histórico** de `REL-FUNC-HIS-004` y deja de formar parte del inventario canónico de evidencias relacionales.

## Estado

**NO FORMALIZADA**.

Este estado significa que la relación funcional ha sido identificada durante el análisis, pero no constituye una dependencia formal demostrada por la documentación del modelo.

## Consecuencias

- No se crea una dependencia oficial `R-HIS-003 → R-PRE-001`.
- No se crea un nuevo `EVID-*` relacional.
- No se crea un `EVID-DESC-*`, porque el objeto registrado no es una evidencia descriptiva de la definición o comportamiento de una única entidad.
- No se crea un `GAP` por esta relación.
- No se modifica `Matriz_Reglas_MVP.md` por inferencia.

---

# 8. CONTROL DE IDENTIFICADORES RELACIONALES

Los identificadores relacionales existentes se auditan antes de normalizar su contenido.

### 8.1 Identificadores históricos `EVID-HIS-*`

- `EVID-HIS-001` → único.
- `EVID-HIS-002` → único.
- `EVID-HIS-003` → **reclasificado como `EVID-DESC-HIS-003`; alias histórico**.
- `EVID-HIS-004` → **reclasificado como alias histórico de `REL-FUNC-HIS-004`; fuera del inventario relacional**.

No se renumeran los identificadores históricos.

### 8.2 Identificadores `EVID-PAG-*`

- `EVID-PAG-001` → único.
- `EVID-PAG-002` → único.
- `EVID-PAG-003` → único.
- `EVID-PAG-004` → identificador histórico agrupador.
- `EVID-PAG-005` → identificador histórico agrupador.

---

# 9. INVENTARIO CANÓNICO DE EVIDENCIAS RELACIONALES

| EVID-ID canónico | Origen | Destino | Relación | Evidencia-tipo | Estado | Clasificación / observación | Fuente / versión | Ubicación | Commit |
|---|---|---|---|---|---|---|---|---|---|
| `EVID-HIS-001` | `P-DAT-002` | `R-HIS-001` | PARÁMETRO → REGLA | DIRECTA | **DEMOSTRADA / CERRADA** | — | `04_Reglas/Especificacion_Reglas_Historico_MVP.md` v1.2; `02_Parametros/Matriz_Parametros_Reglas_MVP.md` v0.8 | §4.1 Determinación del parámetro efectivo; §8 Relaciones confirmadas | No determinado para la v0.8; cierre documental fijado en `dbede0c...` |
| `EVID-HIS-002` | `P-PRE-006` | `R-HIS-002` | PARÁMETRO → REGLA | DIRECTA | **DEMOSTRADA / CERRADA** | — | `04_Reglas/Especificacion_Reglas_Historico_MVP.md` v1.2; `02_Parametros/Matriz_Parametros_Reglas_MVP.md` v0.8 | §5.1 Determinación del parámetro efectivo; §8 Relaciones confirmadas | No determinado para la v0.8; cierre documental fijado en `dbede0c...` |
| `EVID-PAG-001` | `P-PAG-001` | `R-PAG-002` | PARÁMETRO → REGLA | DIRECTA | **NO DEMOSTRADA** | `IDENTIFICADOR VALIDADO` | Fuentes de configuración de pagos | Según fuente | — |
| `EVID-PAG-002` | `P-PAG-002` | `R-PAG-001` | PARÁMETRO → REGLA | DIRECTA | **NO DEMOSTRADA** | `IDENTIFICADOR VALIDADO` | Fuentes de configuración de pagos | Según fuente | — |
| `EVID-PAG-003` | `P-PAG-003` | `R-PAG-001` | PARÁMETRO → REGLA | DIRECTA | **NO DEMOSTRADA** | `IDENTIFICADOR VALIDADO` | Fuentes de configuración de pagos | Según fuente | — |
| `EVID-PAG-004-A` | `P-PAG-004` | `R-PAG-001` | PARÁMETRO → REGLA | DIRECTA | **NO DEMOSTRADA** | `NUEVO ID HOJA — DESDOBLADO` | Fuentes de configuración de pagos | Según fuente | — |
| `EVID-PAG-004-B` | `P-PAG-004` | `R-PAG-002` | PARÁMETRO → REGLA | DIRECTA | **NO DEMOSTRADA** | `NUEVO ID HOJA — DESDOBLADO` | Fuentes de configuración de pagos | Según fuente | — |
| `EVID-PAG-005-A` | `P-PAG-005` | `R-PAG-001` | PARÁMETRO → REGLA | DIRECTA | **NO DEMOSTRADA** | `NUEVO ID HOJA — DESDOBLADO` | Fuentes de configuración de pagos | Según fuente | — |
| `EVID-PAG-005-B` | `P-PAG-005` | `R-PAG-002` | PARÁMETRO → REGLA | DIRECTA | **NO DEMOSTRADA** | `NUEVO ID HOJA — DESDOBLADO` | Fuentes de configuración de pagos | Según fuente | — |

Para `EVID-HIS-001` y `EVID-HIS-002`, la evidencia especializada determina además que no existe duplicidad funcional ni relación maestro → derivado demostrada entre los parámetros históricos contrastados.

`EVID-HIS-003` y `EVID-HIS-004` **no aparecen en este inventario relacional**, porque han sido reclasificados respectivamente como evidencia descriptiva y relación funcional no formalizada.

Los registros `EVID-PAG-*` conservan sus clasificaciones históricas como observaciones, pero su **Estado** se expresa exclusivamente mediante la nomenclatura oficial F3. La ausencia de evidencia localizada no se eleva a `GAP` sin demostrar que exista una obligación documental pendiente.

---

# 10. INVENTARIO DE EVIDENCIA DESCRIPTIVA

| ID canónico | Alias histórico | Entidad | Aspecto | Estado |
|---|---|---|---|---|
| `EVID-DESC-HIS-003` | `EVID-HIS-003` | `R-HIS-003` | Definición / condición / resultado / efecto | DEMOSTRADA |

---

# 11. INVENTARIO DE RELACIONES FUNCIONALES NO FORMALIZADAS

| ID canónico | Alias histórico | Origen | Relación funcional identificada | Formalización | Estado |
|---|---|---|---|---|---|
| `REL-FUNC-HIS-004` | `EVID-HIS-004` | `R-HIS-003` | `R-HIS-003 ↔ R-PRE-001` | No existe dependencia formal documentada | **NO FORMALIZADA** |

Este inventario conserva relaciones funcionales identificadas durante el análisis sin convertirlas en evidencias relacionales ni dependencias oficiales.

---

# 12. RELACIÓN CON `DUP-*`

`DUP-*` mantiene el modelo canónico definido en versiones anteriores.

`DUP-HIS-001` se sustenta documentalmente en `EVID-HIS-001` y en la decisión `C-01`.

`DUP-HIS-002` se sustenta documentalmente en `EVID-HIS-002` y en la decisión `GAP-HIS-02`.

Los identificadores `DUP-*` no se transforman en `EVID-*`.

---

# 13. ESTADOS DE `DUP-*`

Los estados de `DUP-*` son independientes de los estados de evidencia.

| Estado DUP | Significado |
|---|---|
| **PENDIENTE DE ANÁLISIS** | Posible duplicidad identificada, análisis insuficiente. |
| **EN ANÁLISIS** | Contraste documental en curso. |
| **NO RESUELTO** | Analizado, pero sin conclusión suficiente. |
| **RESUELTO** | Clasificación documental suficiente y decisión registrada cuando corresponde. |
| **CONFLICTIVO** | Autoridades o documentos incompatibles. |

---

# 14. ESTADOS DE EVIDENCIA

Los estados de evidencia F3 permanecen definidos por la nomenclatura oficial del Registro:

- `PENDIENTE DE NORMALIZACIÓN`
- `NO IDENTIFICADA`
- `NO DEMOSTRADA`
- `GAP`
- `CONFLICTIVA`
- `DEMOSTRADA`
- `CERRADA`

La normalización de un identificador **no implica automáticamente que su relación pase a `DEMOSTRADA` o `CERRADA`**.

En el caso de `EVID-DESC-HIS-003`, `DEMOSTRADA` se refiere exclusivamente a la definición documental de `R-HIS-003`.

`REL-FUNC-HIS-004` utiliza el estado específico `NO FORMALIZADA`; este estado no equivale a `NO DEMOSTRADA` de una evidencia relacional, porque `REL-FUNC-*` no es una evidencia.

En `EVID-PAG-*`, `IDENTIFICADOR VALIDADO` y `NUEVO ID HOJA — DESDOBLADO` son **clasificaciones/observaciones históricas**, no estados oficiales F3.

---

# 15. DECISIONES F3 — RECLASIFICACIONES

## 15.1 `EVID-HIS-003`

**Decisión:** `EVID-HIS-003` no constituye una evidencia relacional canónica.

**Motivo:** su supuesto destino `LÓGICA DERIVADA` no es una entidad formal identificable y no existe evidencia documental explícita de una relación `R-HIS-003 → X`.

**Acción:** conservar `EVID-HIS-003` como alias histórico y clasificarlo canónicamente como `EVID-DESC-HIS-003`.

**Prohibición:** no crear una relación `R-HIS-003 → R-PRE-001`, `R-HIS-003 → CRC` ni otra dependencia por inferencia.

## 15.2 `EVID-HIS-004`

**Decisión:** `EVID-HIS-004` no constituye una evidencia relacional canónica.

**Motivo:** se identificó una relación funcional conceptual entre `R-HIS-003` y `R-PRE-001`, pero no existe documentación que establezca una dependencia formal `R-HIS-003 → R-PRE-001`.

**Acción:** conservar `EVID-HIS-004` como alias histórico y clasificarlo canónicamente como `REL-FUNC-HIS-004`.

**Prohibición:** no crear una dependencia oficial ni un `EVID-*` relacional a partir de esta relación funcional.

**Consecuencia:** la relación queda registrada para trazabilidad histórica sin contaminar el inventario de evidencias relacionales.

## 15.3 `EVID-PAG-*`

**Decisión:** los registros `EVID-PAG-001` a `EVID-PAG-005-B` mantienen sus identificadores y clasificaciones históricas, pero adoptan la nomenclatura oficial F3 para el campo `Estado`.

**Estado:** `NO DEMOSTRADA`.

**Motivo:** la búsqueda documental realizada en el repositorio no localizó evidencia probatoria independiente suficiente para demostrar las relaciones registradas.

**Importante:** esta clasificación no implica que las relaciones sean falsas ni que exista un GAP. Significa exclusivamente que **no están demostradas por la evidencia actualmente localizada**.

**Clasificaciones conservadas como observación:**
- `IDENTIFICADOR VALIDADO` para `EVID-PAG-001/002/003`.
- `NUEVO ID HOJA — DESDOBLADO` para `EVID-PAG-004-A/B` y `EVID-PAG-005-A/B`.

**Prohibición:** no convertir estos registros en `DEMOSTRADA`, `CERRADA` o `GAP` sin nueva evidencia o una decisión formal que establezca el requisito correspondiente.

---

# 16. CONTROL DE CAMBIOS

**v1.11 — 23/08/2026**

Se normaliza el campo `Estado` de `EVID-PAG-001` a `EVID-PAG-005-B` conforme a la nomenclatura oficial F3. `IDENTIFICADOR VALIDADO` y `NUEVO ID HOJA — DESDOBLADO` pasan a conservarse como clasificaciones/observaciones históricas. Los siete registros adoptan `NO DEMOSTRADA` porque no se localizó evidencia probatoria independiente suficiente en el repositorio durante la auditoría 10A.1. Se establece expresamente que esta clasificación no implica falsedad ni genera automáticamente un GAP.

**v1.10 — 22/08/2026**

Se formaliza el tratamiento canónico de las relaciones funcionales no formalizadas mediante la categoría `REL-FUNC-*`. Se reclasifica `EVID-HIS-004` como alias histórico de `REL-FUNC-HIS-004`, se elimina del inventario canónico de evidencias relacionales y se incorpora al inventario específico de relaciones funcionales no formalizadas. Se establece expresamente que este registro no constituye evidencia relacional, no crea dependencias oficiales y no genera un GAP por sí mismo.

**v1.9 — 22/08/2026**

Se normalizan `EVID-HIS-001` y `EVID-HIS-002` conforme a la estructura canónica F3. Se incorporan origen, destino, relación, tipo de evidencia, estado, fuente, versión y ubicación reproducible. Se conserva expresamente la limitación de que el commit creador de la v0.8 de la matriz no está determinado; el commit `dbede0c0cf531229ac700dc16aa6d765f72b5c45` se registra únicamente como commit documental de cierre, no como creador de la matriz v0.8.

**v1.8 — 22/08/2026**

Se resuelve la anomalía estructural de `EVID-HIS-003`: se determina que es evidencia descriptiva de `R-HIS-003`, no evidencia relacional. Se crea el tipo canónico `EVID-DESC-*`, se asigna `EVID-DESC-HIS-003` como identificador canónico y se conserva `EVID-HIS-003` como alias histórico. Se elimina `EVID-HIS-003` del inventario relacional sin crear ninguna relación artificial.
