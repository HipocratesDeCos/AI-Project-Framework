# REGISTRO MAESTRO DE EVIDENCIAS DE TRAZABILIDAD — F3

## EIOS — Enterprise Intelligent Operations System

**Versión:** 1.9  
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

El Registro distingue tres objetos documentales:

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

# 7. CONTROL DE IDENTIFICADORES RELACIONALES

Los identificadores relacionales existentes se auditan antes de normalizar su contenido.

### 7.1 Identificadores históricos `EVID-HIS-*`

- `EVID-HIS-001` → único.
- `EVID-HIS-002` → único.
- `EVID-HIS-003` → **reclasificado como `EVID-DESC-HIS-003`; alias histórico**.
- `EVID-HIS-004` → único; relación no demostrada.

No se renumeran los identificadores históricos.

### 7.2 Identificadores `EVID-PAG-*`

- `EVID-PAG-001` → único.
- `EVID-PAG-002` → único.
- `EVID-PAG-003` → único.
- `EVID-PAG-004` → identificador histórico agrupador.
- `EVID-PAG-005` → identificador histórico agrupador.

---

# 8. INVENTARIO CANÓNICO DE EVIDENCIAS RELACIONALES

| EVID-ID canónico | Origen | Destino | Relación | Evidencia-tipo | Estado | Fuente / versión | Ubicación | Commit |
|---|---|---|---|---|---|---|---|---|
| `EVID-HIS-001` | `P-DAT-002` | `R-HIS-001` | PARÁMETRO → REGLA | DIRECTA | **DEMOSTRADA / CERRADA** | `04_Reglas/Especificacion_Reglas_Historico_MVP.md` v1.2; `02_Parametros/Matriz_Parametros_Reglas_MVP.md` v0.8 | §4.1 Determinación del parámetro efectivo; §8 Relaciones confirmadas | No determinado para la v0.8; cierre documental fijado en `dbede0c...` |
| `EVID-HIS-002` | `P-PRE-006` | `R-HIS-002` | PARÁMETRO → REGLA | DIRECTA | **DEMOSTRADA / CERRADA** | `04_Reglas/Especificacion_Reglas_Historico_MVP.md` v1.2; `02_Parametros/Matriz_Parametros_Reglas_MVP.md` v0.8 | §5.1 Determinación del parámetro efectivo; §8 Relaciones confirmadas | No determinado para la v0.8; cierre documental fijado en `dbede0c...` |
| `EVID-HIS-004` | `R-HIS-*` | `R-PRE-001` | RELACIÓN ENTRE REGLAS | DIRECTA | **NO DEMOSTRADA** | Registro F3 / fuentes históricas pendientes | Registro histórico | — |
| `EVID-PAG-001` | `P-PAG-001` | `R-PAG-002` | PARÁMETRO → REGLA | DIRECTA | IDENTIFICADOR VALIDADO | Fuentes de configuración de pagos | Según fuente | — |
| `EVID-PAG-002` | `P-PAG-002` | `R-PAG-001` | PARÁMETRO → REGLA | DIRECTA | IDENTIFICADOR VALIDADO | Fuentes de configuración de pagos | Según fuente | — |
| `EVID-PAG-003` | `P-PAG-003` | `R-PAG-001` | PARÁMETRO → REGLA | DIRECTA | IDENTIFICADOR VALIDADO | Fuentes de configuración de pagos | Según fuente | — |
| `EVID-PAG-004-A` | `P-PAG-004` | `R-PAG-001` | PARÁMETRO → REGLA | DIRECTA | NUEVO ID HOJA — DESDOBLADO | Fuentes de configuración de pagos | Según fuente | — |
| `EVID-PAG-004-B` | `P-PAG-004` | `R-PAG-002` | PARÁMETRO → REGLA | DIRECTA | NUEVO ID HOJA — DESDOBLADO | Fuentes de configuración de pagos | Según fuente | — |
| `EVID-PAG-005-A` | `P-PAG-005` | `R-PAG-001` | PARÁMETRO → REGLA | DIRECTA | NUEVO ID HOJA — DESDOBLADO | Fuentes de configuración de pagos | Según fuente | — |
| `EVID-PAG-005-B` | `P-PAG-005` | `R-PAG-002` | PARÁMETRO → REGLA | DIRECTA | NUEVO ID HOJA — DESDOBLADO | Fuentes de configuración de pagos | Según fuente | — |

Para `EVID-HIS-001` y `EVID-HIS-002`, la evidencia especializada determina además que no existe duplicidad funcional ni relación maestro → derivado demostrada entre los parámetros históricos contrastados.

`EVID-HIS-003` **ya no aparece en este inventario relacional**, porque ha sido reclasificado como evidencia descriptiva.

---

# 9. INVENTARIO DE EVIDENCIA DESCRIPTIVA

| ID canónico | Alias histórico | Entidad | Aspecto | Estado |
|---|---|---|---|---|
| `EVID-DESC-HIS-003` | `EVID-HIS-003` | `R-HIS-003` | Definición / condición / resultado / efecto | DEMOSTRADA |

---

# 10. RELACIÓN CON `DUP-*`

`DUP-*` mantiene el modelo canónico definido en versiones anteriores.

`DUP-HIS-001` se sustenta documentalmente en `EVID-HIS-001` y en la decisión `C-01`.

`DUP-HIS-002` se sustenta documentalmente en `EVID-HIS-002` y en la decisión `GAP-HIS-02`.

Los identificadores `DUP-*` no se transforman en `EVID-*`.

---

# 11. ESTADOS DE `DUP-*`

Los estados de `DUP-*` son independientes de los estados de evidencia.

| Estado DUP | Significado |
|---|---|
| **PENDIENTE DE ANÁLISIS** | Posible duplicidad identificada, análisis insuficiente. |
| **EN ANÁLISIS** | Contraste documental en curso. |
| **NO RESUELTO** | Analizado, pero sin conclusión suficiente. |
| **RESUELTO** | Clasificación documental suficiente y decisión registrada cuando corresponde. |
| **CONFLICTIVO** | Autoridades o documentos incompatibles. |

---

# 12. ESTADOS DE EVIDENCIA

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

---

# 13. DECISIÓN F3 — RECLASIFICACIÓN DE EVID-HIS-003

**Decisión:** `EVID-HIS-003` no constituye una evidencia relacional canónica.

**Motivo:** su supuesto destino `LÓGICA DERIVADA` no es una entidad formal identificable y no existe evidencia documental explícita de una relación `R-HIS-003 → X`.

**Acción:** conservar `EVID-HIS-003` como alias histórico y clasificarlo canónicamente como `EVID-DESC-HIS-003`.

**Prohibición:** no crear una relación `R-HIS-003 → R-PRE-001`, `R-HIS-003 → CRC` ni otra dependencia por inferencia.

**Consecuencia:** la ausencia de una dependencia formal no se considera un error del Registro; queda correctamente representada como ausencia de relación demostrada.

---

# 14. CONTROL DE CAMBIOS

**v1.9 — 22/08/2026**

Se normalizan `EVID-HIS-001` y `EVID-HIS-002` conforme a la estructura canónica F3. Se incorporan origen, destino, relación, tipo de evidencia, estado, fuente, versión y ubicación reproducible. Se conserva expresamente la limitación de que el commit creador de la v0.8 de la matriz no está determinado; el commit `dbede0c0cf531229ac700dc16aa6d765f72b5c45` se registra únicamente como commit documental de cierre, no como creador de la matriz v0.8.

**v1.8 — 22/08/2026**

Se resuelve la anomalía estructural de `EVID-HIS-003`: se determina que es evidencia descriptiva de `R-HIS-003`, no evidencia relacional. Se crea el tipo canónico `EVID-DESC-*`, se asigna `EVID-DESC-HIS-003` como identificador canónico y se conserva `EVID-HIS-003` como alias histórico. Se elimina `EVID-HIS-003` del inventario relacional sin crear ninguna relación artificial.
