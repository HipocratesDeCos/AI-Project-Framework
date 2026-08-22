# REGISTRO MAESTRO DE EVIDENCIAS DE TRAZABILIDAD — F3

## EIOS — Enterprise Intelligent Operations System

**Versión:** 1.5  
**Estado:** ACTIVO — REGISTRO MAESTRO DE EVIDENCIAS F3  
**Ámbito:** EIOS Vertical MVP  
**Fecha:** 22/08/2026  
**Especificación aplicable:** `00_Gobierno/Especificacion_Evidencia_Trazabilidad_F3.md` v1.2

---

# 1. PROPÓSITO

Este documento constituye el **Registro Maestro de Evidencias de Trazabilidad F3** de EIOS.

Es el registro oficial donde se identifican, clasifican, conservan y controlan las evidencias utilizadas para demostrar la trazabilidad entre:

- datos;
- parámetros;
- cálculos;
- reglas;
- resultados;
- excepciones;
- CRC;
- recomendaciones;
- y los documentos o componentes que intervienen en dichas relaciones.

Este documento no crea ni modifica parámetros o reglas. **Registra y gobierna el estado de la evidencia** que demuestra las relaciones documentales o funcionales del sistema.

---

# 2. AUTORIDAD DEL REGISTRO MAESTRO

A partir de la versión 1.3, este archivo queda fijado como **fuente maestra de registro de evidencias F3**.

Esto significa que:

1. toda evidencia F3 oficial deberá disponer de un `EVID-ID` único;
2. ninguna relación podrá considerarse evidenciada oficialmente sin estar registrada o referenciada en este registro;
3. el estado de una evidencia deberá ser el que figure en este registro después de la correspondiente decisión documental;
4. las fuentes originales conservan la autoridad sobre su propio contenido, pero este registro es la autoridad de **estado y trazabilidad de la evidencia**;
5. cualquier modificación del estado de una evidencia deberá quedar registrada mediante control de cambios y conservar su cadena de reproducibilidad;
6. una evidencia `NO DEMOSTRADA`, `GAP` o `CONFLICTIVA` no podrá convertirse en `CERRADA` por inferencia, similitud semántica o conveniencia del proyecto;
7. los documentos especializados aportan evidencia, pero no sustituyen este registro como índice maestro de evidencias F3.

**Principio:**

> La fuente original demuestra el hecho; el Registro Maestro F3 registra qué hecho está demostrado, con qué evidencia, bajo qué autoridad y en qué estado.

---

# 3. REGLA DE IDENTIFICACIÓN

Cada evidencia deberá identificarse mediante un `EVID-ID` único y estable.

No se reutilizará un `EVID-ID` para una relación diferente.

Cuando una evidencia cambie sustancialmente de objeto, deberá generarse un nuevo identificador y conservarse la referencia histórica correspondiente.

---

# 4. MODELO MÍNIMO DE UNA EVIDENCIA

Toda evidencia F3 deberá contener, como mínimo, los campos establecidos por `00_Gobierno/Especificacion_Evidencia_Trazabilidad_F3.md` v1.2:

| Campo | Obligatorio | Descripción |
|---|---:|---|
| `EVID-ID` | Sí | Identificador único de la evidencia. |
| `Origen-ID` | Sí | Parámetro, dato, regla, documento o componente de origen. |
| `Origen-tipo` | Sí | PARAMETRO / DATO / REGLA / DOCUMENTO / COMPONENTE. |
| `Destino-ID` | Sí | Entidad cuya dependencia se pretende demostrar. |
| `Destino-tipo` | Sí | PARAMETRO / DATO / REGLA / RESULTADO / COMPONENTE. |
| `Relación` | Sí | Tipo de dependencia observada. |
| `Fuente` | Sí | Documento o recurso donde aparece la evidencia. |
| `Ubicación` | Sí | Ruta, sección, encabezado, línea, commit u otra localización reproducible. |
| `Extracto` | Sí | Fragmento mínimo que demuestra la relación. |
| `Evidencia-tipo` | Sí | DIRECTA / INDIRECTA / CONTEXTUAL. |
| `Estado` | Sí | Estado oficial según la sección 6. |
| `Autoridad` | Sí | Documento que posee autoridad sobre la materia. |
| `Versión` | Sí | Versión de la fuente utilizada. |
| `Commit` | Recomendado | Commit de GitHub que permite reproducir la evidencia. |
| `Observaciones` | No | Matices, dependencias o limitaciones. |

**Regla:** mientras una evidencia existente no contenga todos los campos obligatorios, se considerará **PENDIENTE DE NORMALIZACIÓN**, no evidencia completamente auditada.

---

# 5. ESTRUCTURA ÚNICA Y PLANTILLA CANÓNICA DE EVIDENCIA

A partir de la versión 1.4, toda nueva evidencia F3 deberá registrarse utilizando **una única estructura canónica**. No se admitirán formatos alternativos para nuevas evidencias.

## 5.1 Orden obligatorio de los campos

1. `EVID-ID`
2. `Origen-ID`
3. `Origen-tipo`
4. `Destino-ID`
5. `Destino-tipo`
6. `Relación`
7. `Fuente`
8. `Ubicación`
9. `Extracto`
10. `Evidencia-tipo`
11. `Estado`
12. `Autoridad`
13. `Versión`
14. `Commit`
15. `Observaciones`

## 5.2 Plantilla canónica

```markdown
## EVID-[DOMINIO]-[NNN]

**Origen-ID:** `[ID]`
**Origen-tipo:** `[PARAMETRO | DATO | REGLA | DOCUMENTO | COMPONENTE]`
**Destino-ID:** `[ID]`
**Destino-tipo:** `[PARAMETRO | DATO | REGLA | RESULTADO | COMPONENTE]`
**Relación:** `[TIPO DE RELACIÓN]`
**Fuente:** `[RUTA DEL DOCUMENTO O RECURSO]`
**Ubicación:** `[SECCIÓN / ENCABEZADO / LÍNEA / LOCALIZACIÓN REPRODUCIBLE]`
**Extracto:** `[FRAGMENTO MÍNIMO QUE DEMUESTRA LA RELACIÓN]`
**Evidencia-tipo:** `[DIRECTA | INDIRECTA | CONTEXTUAL]`
**Estado:** `[ESTADO OFICIAL F3]`
**Autoridad:** `[DOCUMENTO CON AUTORIDAD SOBRE LA MATERIA]`
**Versión:** `[VERSIÓN DE LA FUENTE]`
**Commit:** `[SHA DE GITHUB, SI EXISTE]`
**Observaciones:** `[MATICES, DEPENDENCIAS O LIMITACIONES]`
```

## 5.3 Regla de unicidad

Un `EVID-ID` representa **una relación auditada concreta**. Si una misma investigación demuestra varias relaciones independientes, cada relación deberá disponer de su propio `EVID-ID`.

## 5.4 Regla de evidencia mínima

Una evidencia no podrá pasar a `DEMOSTRADA` o `CERRADA` si falta cualquiera de estos elementos obligatorios:

- origen;
- destino;
- relación;
- fuente;
- ubicación reproducible;
- extracto probatorio;
- tipo de evidencia;
- estado;
- autoridad;
- versión.

El `Commit` será obligatorio cuando la evidencia proceda de GitHub y el commit sea necesario para reproducir el estado exacto de la fuente.

## 5.5 Separación entre evidencia y conclusión

El `Extracto` contiene la evidencia observable. La interpretación o decisión no sustituye al extracto y deberá constar en `Observaciones` o en el documento de decisión correspondiente.

## 5.6 Fuentes múltiples

Cuando una relación requiera varias fuentes, deberán identificarse todas y distinguirse la fuente primaria de las complementarias.

## 5.7 Normalización de evidencias existentes

Las evidencias anteriores a v1.4 podrán conservar temporalmente su formato histórico, pero quedarán clasificadas como **PENDIENTES DE NORMALIZACIÓN** hasta completar la plantilla canónica.

---

# 6. NOMENCLATURA OFICIAL DE ESTADOS F3

La siguiente nomenclatura es **oficial y única** para el Registro Maestro F3. No se utilizarán sinónimos como sustitutos de estos estados.

| Estado oficial | Significado | ¿Puede considerarse evidencia demostrada? | Acción / condición |
|---|---|---:|---|
| **PENDIENTE DE NORMALIZACIÓN** | Existe un registro histórico de evidencia, pero todavía no cumple la estructura canónica F3. | No | Completar campos obligatorios antes de auditarla como evidencia completa. |
| **NO IDENTIFICADA** | No se ha localizado la entidad, fuente o evidencia que se estaba buscando. | No | Continuar búsqueda o registrar formalmente la ausencia. |
| **NO DEMOSTRADA** | La entidad existe o la relación es plausible, pero la evidencia disponible no acredita suficientemente la relación. | No | No cerrar; buscar evidencia adicional o mantener el estado. |
| **GAP** | Falta una definición, dependencia o evidencia necesaria para completar una cadena crítica de trazabilidad. | No | Registrar, priorizar y resolver documentalmente. |
| **CONFLICTIVA** | Existen fuentes, decisiones o autoridades incompatibles que impiden determinar una única relación válida. | No | Resolver primero la autoridad o el conflicto. |
| **DEMOSTRADA** | Existe evidencia suficiente, reproducible y atribuible a una fuente con autoridad para acreditar la relación. | Sí | Puede incorporarse a la trazabilidad oficial; todavía puede requerir propagación documental. |
| **CERRADA** | La evidencia está demostrada y, además, los documentos de autoridad afectados están alineados y la cadena de decisión/cambio ha sido auditada. | Sí | Estado final de cierre del bloque concreto. |

## 6.1 Distinción crítica: DEMOSTRADA ≠ CERRADA

Esta distinción queda fijada como regla de gobierno.

**DEMOSTRADA** significa:

> «La relación está probada por evidencia suficiente y reproducible.»

**CERRADA** significa:

> «La relación está probada, la decisión está registrada, los documentos de autoridad afectados están alineados y la cadena documental ha sido auditada.»

Por tanto:

```text
PENDIENTE DE NORMALIZACIÓN
        ↓
NO IDENTIFICADA / NO DEMOSTRADA / GAP / CONFLICTIVA
        ↓
DEMOSTRADA
        ↓
CERRADA
```

No todos los casos recorrerán todas las etapas. `CONFLICTIVA`, por ejemplo, puede volver a `NO DEMOSTRADA` una vez identificado y separado el conflicto, antes de alcanzar `DEMOSTRADA`.

## 6.2 Reglas de transición

### Hacia `PENDIENTE DE NORMALIZACIÓN`
Cuando existe un registro histórico pero faltan campos de la plantilla canónica.

### Hacia `NO IDENTIFICADA`
Cuando la búsqueda no localiza la entidad o fuente requerida.

### Hacia `NO DEMOSTRADA`
Cuando la entidad está localizada, pero la relación no puede acreditarse documentalmente.

### Hacia `GAP`
Cuando la ausencia afecta a una capacidad o dependencia necesaria para completar una cadena crítica.

### Hacia `CONFLICTIVA`
Cuando aparecen fuentes o autoridades incompatibles.

### Hacia `DEMOSTRADA`
Solo cuando se cumplen simultáneamente:

1. fuente real identificada;
2. ubicación reproducible;
3. extracto probatorio suficiente;
4. origen y destino identificados;
5. relación definida;
6. autoridad documental conocida;
7. versión identificada;
8. ausencia de conflicto de autoridad no resuelto;
9. ausencia de inferencia semántica como prueba principal.

### Hacia `CERRADA`
Solo después de `DEMOSTRADA` y cuando, además:

1. la decisión correspondiente está registrada;
2. los documentos de autoridad afectados han sido actualizados o confirmados;
3. las referencias/versiones son coherentes;
4. la cadena documental ha sido auditada;
5. no queda una discrepancia conocida que afecte al cierre de esa relación.

## 6.3 Prohibiciones

Queda prohibido:

- pasar de `NO DEMOSTRADA` a `CERRADA` directamente;
- pasar de `GAP` a `CERRADA` sin evidencia y decisión;
- utilizar `DEMOSTRADA` para ocultar una discrepancia documental posterior;
- utilizar `CERRADA` como sinónimo de «parece correcto»;
- crear una fuente, parámetro o regla únicamente para cambiar el estado;
- eliminar una evidencia negativa para mejorar el estado visual del mapa.

---

# 7. REGLAS DE GOBIERNO DEL REGISTRO MAESTRO

## RM-01 — Registro único

El Registro F3 es el registro maestro de estado de las evidencias de trazabilidad.

## RM-02 — No inferencia

No se registrará una relación como DEMOSTRADA por similitud de nombres, valores, prefijos, unidades o proximidad documental.

## RM-03 — Fuente reproducible

Toda evidencia que pretenda alcanzar estado DEMOSTRADA/CERRADA deberá poder localizarse en una fuente real y reproducible.

## RM-04 — Autoridad

La evidencia deberá identificar el documento que tiene autoridad sobre la materia demostrada.

## RM-05 — Versionado

Toda evidencia deberá conservar la versión de la fuente utilizada. Cuando sea posible deberá conservar también el commit de GitHub.

## RM-06 — Trazabilidad de cambios

Toda modificación del registro deberá conservar la cadena:

`EVID-ID → fuente → evidencia → decisión → modificación → commit`

## RM-07 — No cierre artificial

No se cerrará una evidencia únicamente para eliminar un GAP del mapa o cambiar el color de un documento.

## RM-08 — Evidencia negativa

Las relaciones no demostradas también forman parte del registro y deberán permanecer registradas mientras sean relevantes para la auditoría.

## RM-09 — Documentos especializados

Un documento especializado puede aportar la evidencia, pero su existencia no implica automáticamente que la evidencia esté cerrada. El Registro Maestro debe registrar su estado.

## RM-10 — Auditoría

El Registro Maestro deberá poder auditarse contra las fuentes documentales y contra la Especificación F3.

## RM-11 — Estructura única

Toda evidencia nueva deberá utilizar exclusivamente la plantilla canónica definida en la sección 5.

## RM-12 — Estados únicos

Toda evidencia deberá utilizar exclusivamente uno de los estados oficiales definidos en la sección 6.

---

# 8. CADENA MAESTRA DE TRAZABILIDAD

Cuando resulte aplicable, el Registro deberá poder reconstruir:

```text
DATO / FUENTE
      ↓
PARÁMETRO
      ↓
CÁLCULO / INDICADOR
      ↓
REGLA
      ↓
RESULTADO
      ↓
CRC
      ↓
RECOMENDACIÓN
```

No todos los casos requerirán todos los niveles. Cada evidencia deberá indicar qué tramo demuestra y cuáles permanecen sin demostrar.

---

# 9. EVIDENCIAS F3 — HISTÓRICO

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

## EVID-HIS-004

**Relación auditada:** `R-HIS-*` → `R-PRE-001`  
**Tipo de relación:** REGLA → REGLA  
**Fuente:** `04_Reglas/Matriz_Reglas_MVP.md` v2.1  
**Estado:** NO DEMOSTRADA  
**Conclusión:** existe relación funcional contextual, pero no se convierte en dependencia oficial sin evidencia adicional.

---

# 10. EVIDENCIAS F3 — PAGOS / C-07

## EVID-PAG-001

**Relación:** `P-PAG-001 → R-PAG-002`  
**Tipo:** DIRECTA  
**Evidencia primaria:** `04_Reglas/Especificacion_Reglas_Configuracion_Pagos_MVP.md` v1.0  
**Evidencia secundaria:** `04_Reglas/Matriz_Reglas_MVP.md` v2.1  
**Evidencia de enlace:** `02_Parametros/Matriz_Parametros_Reglas_MVP.md` v0.8  
**Estado:** CERRADA

## EVID-PAG-002

**Relación:** `P-PAG-002 → R-PAG-001`  
**Tipo:** DIRECTA  
**Evidencia primaria:** `04_Reglas/Especificacion_Reglas_Configuracion_Pagos_MVP.md` v1.0  
**Evidencia secundaria:** `04_Reglas/Matriz_Reglas_MVP.md` v2.1  
**Evidencia de enlace:** `02_Parametros/Matriz_Parametros_Reglas_MVP.md` v0.8  
**Estado:** CERRADA

## EVID-PAG-003

**Relación:** `P-PAG-003 → R-PAG-001`  
**Tipo:** DERIVADA  
**Evidencia primaria:** `04_Reglas/Especificacion_Reglas_Configuracion_Pagos_MVP.md` v1.0  
**Evidencia secundaria:** `04_Reglas/Matriz_Reglas_MVP.md` v2.1  
**Evidencia de enlace:** `02_Parametros/Matriz_Parametros_Reglas_MVP.md` v0.8  
**Estado:** CERRADA

## EVID-PAG-004

**Relaciones:** `P-PAG-004 → R-PAG-001 / R-PAG-002`  
**Tipo:** CONTROL FUNCIONAL  
**Evidencia primaria:** `04_Reglas/Especificacion_Reglas_Configuracion_Pagos_MVP.md` v1.0  
**Evidencia secundaria:** `04_Reglas/Matriz_Reglas_MVP.md` v2.1  
**Evidencia de enlace:** `02_Parametros/Matriz_Parametros_Reglas_MVP.md` v0.8  
**Estado:** CERRADA

## EVID-PAG-005

**Relaciones:** `P-PAG-005 → R-PAG-001 / R-PAG-002`  
**Tipo:** INDIRECTA / DERIVADA  
**Evidencia primaria:** `04_Reglas/Especificacion_Reglas_Configuracion_Pagos_MVP.md` v1.0  
**Evidencia secundaria:** `04_Reglas/Matriz_Reglas_MVP.md` v2.1  
**Evidencia de enlace:** `02_Parametros/Matriz_Parametros_Reglas_MVP.md` v0.8  
**Estado:** CERRADA

### C-07 — estado de evidencia

La condición establecida por `C-07` era no asignar relaciones concretas entre parámetros de pago y reglas sin evidencia documental suficiente.

La especificación especializada de configuración de pagos aporta la evidencia funcional directa y la Matriz de Reglas y Matriz de Parámetros incorporan las relaciones. Por tanto, **C-07 queda cerrado documentalmente para `P-PAG-001…005 → R-PAG-*`.**

---

# 11. CONTROL DE DUPLICIDADES

## DUP-HIS-001

**Pares:** `P-PRE-003` ↔ `P-DAT-002`  
**Estado:** CERRADA  
**Resolución:** `C-01` mantiene `P-PRE-003` como criterio/metodología; `P-DAT-002` es el parámetro configurable consumidor de `R-HIS-001`. No existe relación maestro → derivado demostrada.

## DUP-HIS-002

**Pares:** `P-PRE-006` ↔ `P-DAT-003`  
**Estado:** CERRADA  
**Resolución:** `P-PRE-006` establece el mínimo de operaciones comparables de `R-HIS-002`; `P-DAT-003` no sustituye este parámetro y queda sin consumidor directo demostrado en el MVP actual. No existe relación maestro → derivado demostrada.

---

# 12. DECISIONES NEGATIVAS REGISTRADAS

Las siguientes acciones siguen expresamente descartadas:

- crear parámetros `HIS-*` para cubrir la ausencia de trazabilidad;
- fusionar `P-PRE-003` con `P-DAT-002`;
- fusionar `P-PRE-006` con `P-DAT-003`;
- crear una dependencia `R-HIS-* → R-PRE-001` sin evidencia adicional.

---

# 13. CRITERIO DE CIERRE

Una evidencia pasa a **DEMOSTRADA** cuando la relación puede reproducirse desde una fuente real, con ubicación identificable, autoridad documental conocida y sin depender de similitud semántica como prueba principal.

Una evidencia pasa a **CERRADA** cuando, además, la decisión está registrada, los documentos de autoridad afectados están alineados y la cadena documental ha sido auditada.

Todo cambio posterior deberá conservar la cadena:

`EVID-ID → fuente → evidencia → decisión → modificación → commit`

---

# 14. ESTADO DEL REGISTRO

El **Registro Maestro F3 está ACTIVO** como registro de gobierno de evidencias.

Que el registro esté activo no significa que todas sus evidencias estén cerradas. Los estados se controlan individualmente.

| Bloque | Estado |
|---|---|
| HIS-001 | 🟢 CERRADA |
| HIS-002 | 🟢 CERRADA |
| HIS-003 | 🟢 CERRADA |
| HIS-004 | 🟡 NO DEMOSTRADA |
| Duplicidad P-PRE-003 / P-DAT-002 | 🟢 CERRADA |
| Duplicidad P-PRE-006 / P-DAT-003 | 🟢 CERRADA |
| PAG-001 | 🟢 CERRADA |
| PAG-002 | 🟢 CERRADA |
| PAG-003 | 🟢 CERRADA |
| PAG-004 | 🟢 CERRADA |
| PAG-005 | 🟢 CERRADA |
| C-07 | 🟢 CERRADA |

---

# 15. CONTROL DE CAMBIOS

**v1.5 — 22/08/2026**

Se establece formalmente la **nomenclatura única de estados F3** y sus criterios de transición.

Se incorporan como estados oficiales:

- `PENDIENTE DE NORMALIZACIÓN`;
- `NO IDENTIFICADA`;
- `NO DEMOSTRADA`;
- `GAP`;
- `CONFLICTIVA`;
- `DEMOSTRADA`;
- `CERRADA`.

Se establece expresamente la diferencia entre `DEMOSTRADA` y `CERRADA`: la primera acredita la relación; la segunda exige además alineación documental, decisión registrada y auditoría de la cadena.

Esta modificación no cierra `EVID-HIS-004` ni altera las evidencias existentes por inferencia.
