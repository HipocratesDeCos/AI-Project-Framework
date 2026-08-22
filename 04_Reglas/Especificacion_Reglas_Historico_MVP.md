# ESPECIFICACIÓN DE REGLAS HISTÓRICO — MVP

## EIOS — Enterprise Intelligent Operations System

**Versión:** 1.1  
**Estado:** DOCUMENTO DE EVIDENCIA — PUNTO 2 RESUELTO / PUNTO 3 PENDIENTE  
**Baseline:** EIOS Vertical MVP  
**Fecha:** 22/08/2026  
**Ámbito:** Resolución documental de relaciones histórico → regla

---

# 1. PROPÓSITO

Este documento establece la estructura de evidencia necesaria para resolver documentalmente `GAP-HIS-01` y `GAP-HIS-02` definidos en `00_Gobierno/Especificacion_Evidencia_Trazabilidad_F3.md`.

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

# 3. FUENTES CONTRASTADAS

Para esta determinación se han contrastado:

- `02_Parametros/Catalogo_Parametros_MVP_v0.3.md` v0.3;
- `02_Parametros/Matriz_Parametros_Reglas_MVP.md` v0.7;
- `02_Parametros/Decision_Log_Parametros_MVP.md` v0.5;
- `04_Reglas/Matriz_Reglas_MVP.md` v2.1;
- `00_Gobierno/Especificacion_Evidencia_Trazabilidad_F3.md` v1.1;
- este documento `04_Reglas/Especificacion_Reglas_Historico_MVP.md`.

---

# 4. EVID-HIS-001 — GAP-HIS-01

## 4.1 Relación investigada

```text
PRE-003 / DAT-002
        ↓
R-HIS-001
```

### Regla

`R-HIS-001 — Referencia demasiado antigua`

La regla evalúa si la compra utilizada como referencia supera la antigüedad máxima configurada. `04_Reglas/Matriz_Reglas_MVP.md` v2.1 define esta condición, pero no incorpora dentro de la propia regla un identificador de parámetro histórico en su definición textual.

### Parámetros candidatos

- `PRE-003` — Antigüedad máxima de referencia.
- `DAT-002` — Antigüedad máxima de referencia de precio.

### Evidencia determinante

**Fuente:** `02_Parametros/Decision_Log_Parametros_MVP.md` v0.5, decisión `C-01`.

`C-01` establece expresamente que `PRE-003` se mantiene como **criterio/metodología pendiente**, sin crear parámetro directo.

**Fuente complementaria:** `02_Parametros/Matriz_Parametros_Reglas_MVP.md` v0.7.

La matriz establece explícitamente:

```text
P-DAT-002 → R-HIS-001
Tipo: Directa
Estado: CONFIRMADO
```

La misma matriz registra que `P-PRE-003` no es parámetro directo de `R-HIS-001` y lo mantiene como criterio/metodología conforme a `C-01`.

### Determinación del parámetro efectivo

**PARÁMETRO EFECTIVO: `P-DAT-002`**

La evidencia determinante no es la coincidencia de nombre o valor: es la decisión documental `C-01`, que excluye `P-PRE-003` como parámetro directo, combinada con la matriz oficial que identifica `P-DAT-002` como consumidor directo de `R-HIS-001`.

### Estado del punto 2

**RESUELTO:** consumidor efectivo determinado como `P-DAT-002`.

El análisis de si `P-PRE-003` y `P-DAT-002` son duplicados, conceptos distintos o presentan relación maestro → derivado se traslada al **Punto 3**.

---

# 5. EVID-HIS-002 — GAP-HIS-02

## 5.1 Relación investigada

```text
PRE-006 / DAT-003
        ↓
R-HIS-002
```

### Regla

`R-HIS-002 — Histórico insuficiente`

La regla determina si no existe el número mínimo de operaciones comparables establecido.

### Parámetros candidatos

- `PRE-006` — Nº mínimo de compras comparables.
- `DAT-003` — Nº mínimo de registros históricos.

### Evidencia determinante

**Fuente primaria funcional:** `04_Reglas/Matriz_Reglas_MVP.md` v2.1.

`R-HIS-002` establece que la condición es la ausencia del número mínimo de **operaciones comparables**.

**Fuente de enlace:** `02_Parametros/Matriz_Parametros_Reglas_MVP.md` v0.7.

La matriz establece explícitamente:

```text
P-PRE-006 → R-HIS-002
Tipo: Directa
Estado: CONFIRMADO
```

La misma matriz distingue `P-DAT-003` como:

```text
Sin consumidor directo de regla MVP demostrado
```

y especifica que `P-DAT-003` no sustituye a `P-PRE-006`.

### Determinación del parámetro efectivo

**PARÁMETRO EFECTIVO: `P-PRE-006`**

La determinación se basa en el objeto funcional de `R-HIS-002` —operaciones comparables— y en la asignación documental directa de `P-PRE-006` a dicha regla en la matriz oficial. `P-DAT-003` queda sin consumidor directo demostrado en el MVP actual.

### Estado del punto 2

**RESUELTO:** consumidor efectivo determinado como `P-PRE-006`.

El análisis de si `P-PRE-006` y `P-DAT-003` son duplicados, conceptos distintos o presentan relación maestro → derivado se traslada al **Punto 3**.

---

# 6. MATRIZ DE DETERMINACIÓN — PUNTO 2

| GAP | Parámetro efectivo | Regla consumidora | Evidencia determinante | Estado |
|---|---|---|---|---|
| GAP-HIS-01 | `P-DAT-002` | `R-HIS-001` | `C-01` + Matriz Parámetros → Reglas | **DETERMINADO** |
| GAP-HIS-02 | `P-PRE-006` | `R-HIS-002` | Matriz Reglas + Matriz Parámetros → Reglas | **DETERMINADO** |

---

# 7. PUNTO 3 — DUPLICIDAD / MAESTRO → DERIVADO

Este punto **todavía no está resuelto**.

Debe determinarse para cada pareja:

- `P-PRE-003` ↔ `P-DAT-002`;
- `P-PRE-006` ↔ `P-DAT-003`;

si existe:

- duplicidad real;
- conceptos distintos;
- relación maestro → derivado;
- o ausencia de relación funcional.

La existencia de valores iniciales iguales no será suficiente para declarar duplicidad.

---

# 8. EVIDENCIA DE AUTORIDAD

Las conclusiones del Punto 2 se apoyan en documentos del sistema documental EIOS con identificación de versión y ubicación.

Para el Punto 3 deberá identificarse además qué documento tiene autoridad para decidir la naturaleza de la relación entre los parámetros candidatos.

---

# 9. PROHIBICIONES

Este documento no autoriza:

1. crear parámetros `HIS-*` artificialmente;
2. elegir un parámetro por coincidencia de nombre;
3. elegir un parámetro por coincidencia de valor;
4. declarar duplicidad sin comparar ámbito y consumidor;
5. declarar maestro → derivado sin transformación documentada;
6. cerrar un GAP sin completar los puntos 3 a 7 del procedimiento acordado.

---

# 10. RELACIÓN CON F3

La cadena de resolución queda estructurada así:

```text
1. Evidencia documental real          → COMPLETADO
2. Parámetro efectivo                 → COMPLETADO
3. Duplicidad / maestro-derivado      → PENDIENTE
4. Actualizar matriz                  → PENDIENTE
5. Registrar decisión                 → PENDIENTE
6. Actualizar evidencia F3            → PENDIENTE
7. Auditar cadena completa            → PENDIENTE
```

La determinación del Punto 2 **no cierra todavía** `GAP-HIS-01` ni `GAP-HIS-02`.

---

# 11. ESTADO DEL DOCUMENTO

**Versión:** 1.1  
**Estado:** PUNTO 2 RESUELTO / PUNTO 3 PENDIENTE  
**Baseline:** EIOS Vertical MVP
