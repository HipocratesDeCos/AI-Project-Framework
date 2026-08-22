# ESPECIFICACIÓN DE REGLAS HISTÓRICO — MVP

## EIOS — Enterprise Intelligent Operations System

**Versión:** 1.0  
**Estado:** DOCUMENTO DE EVIDENCIA — GAP-HIS-01 / GAP-HIS-02  
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

Este documento **no presupone la respuesta**. La conclusión de cada GAP solo podrá establecerse cuando la evidencia documental identificable la sostenga.

---

# 2. CRITERIO DE EVIDENCIA

Una relación parámetro → regla solo podrá clasificarse como DEMOSTRADA cuando exista evidencia reproducible procedente de una fuente documental real, con ubicación identificable y autoridad conocida.

La coincidencia de:

- nombre;
- prefijo;
- unidad;
- valor inicial;
- familia;

no constituye por sí misma evidencia suficiente.

Cuando la documentación no permita determinar el consumidor efectivo, el GAP permanecerá abierto.

---

# 3. FUENTES A CONSIDERAR

Para cada GAP deberán contrastarse, como mínimo:

- `02_Parametros/Catalogo_Parametros_MVP_v0.3.md`;
- `02_Parametros/Matriz_Parametros_Reglas_MVP.md`;
- `02_Parametros/Decision_Log_Parametros_MVP.md`;
- `04_Reglas/Matriz_Reglas_MVP.md`;
- `04_Reglas/Reglas_MVP.md`;
- `00_Gobierno/Especificacion_Evidencia_Trazabilidad_F3.md`;
- cualquier especificación funcional adicional que establezca explícitamente el consumidor de la regla.

La fuente de autoridad deberá identificarse para cada conclusión.

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

La regla evalúa si la compra utilizada como referencia supera la antigüedad máxima configurada.

### Parámetros candidatos

- `PRE-003` — Antigüedad máxima de referencia.
- `DAT-002` — Antigüedad máxima de referencia de precio.

### Evidencia requerida

Debe determinarse documentalmente:

- definición exacta de cada parámetro;
- ámbito funcional de cada parámetro;
- regla o cálculo consumidor;
- unidad;
- valor inicial;
- autoridad documental;
- si existe duplicidad;
- si existe maestro → derivado;
- cuál es el consumidor efectivo de `R-HIS-001`.

### Estado de evidencia actual

La documentación existente acredita la existencia y definición de los candidatos y la necesidad de una antigüedad máxima en `R-HIS-001`.

**No se considera todavía demostrada la elección del consumidor efectivo únicamente por coincidencia semántica o de valor.**

### Conclusión

**PENDIENTE DE DETERMINACIÓN DEL PARÁMETRO EFECTIVO.**

No se crea un parámetro `HIS-*` para resolver el GAP.

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

### Evidencia requerida

Debe determinarse documentalmente:

- definición exacta de cada parámetro;
- ámbito funcional de cada parámetro;
- regla o cálculo consumidor;
- unidad;
- valor inicial;
- autoridad documental;
- si existe duplicidad;
- si existe maestro → derivado;
- cuál es el consumidor efectivo de `R-HIS-002`.

### Estado de evidencia actual

La documentación existente acredita la existencia y definición de los candidatos y la necesidad de un número mínimo de operaciones comparables en `R-HIS-002`.

**No se considera todavía demostrada la elección del consumidor efectivo únicamente por coincidencia semántica o de valor.**

### Conclusión

**PENDIENTE DE DETERMINACIÓN DEL PARÁMETRO EFECTIVO.**

No se crea un parámetro `HIS-*` para resolver el GAP.

---

# 6. MATRIZ DE DETERMINACIÓN

| GAP | Candidato A | Candidato B | Consumidor efectivo | Duplicidad | Maestro/derivado | Estado |
|---|---|---|---|---|---|---|
| GAP-HIS-01 | `PRE-003` | `DAT-002` | Por determinar | Por determinar | Por determinar | ABIERTO |
| GAP-HIS-02 | `PRE-006` | `DAT-003` | Por determinar | Por determinar | Por determinar | ABIERTO |

Esta tabla no deberá convertirse en una conclusión cerrada hasta que exista evidencia documental suficiente.

---

# 7. CLASIFICACIÓN DE RELACIONES

Cuando se complete la investigación, cada relación deberá clasificarse exclusivamente como una de las siguientes:

- **DIRECTA:** el documento de autoridad identifica el parámetro como consumidor de la regla.
- **INDIRECTA:** el parámetro participa a través de otra variable o cálculo documentado.
- **DERIVADA:** existe una transformación explícita desde un parámetro maestro.
- **DUPLICIDAD:** dos parámetros representan funcionalmente la misma variable en el mismo ámbito y uno debe eliminarse/reclasificarse según autoridad.
- **CONCEPTOS DISTINTOS:** los parámetros parecen similares pero representan variables diferentes.
- **NO DEMOSTRADA:** la documentación no permite concluir la relación.

---

# 8. EVIDENCIA DE AUTORIDAD

Para cerrar cualquiera de los GAP deberá existir una fuente que permita responder:

> ¿Qué documento tiene autoridad para determinar la relación parámetro → regla?

La conclusión deberá identificar:

```text
Fuente
Ruta
Versión
Sección
Contenido probatorio
Autoridad
```

Una referencia a otro documento sin contenido probatorio identificable no se considerará suficiente por sí sola.

---

# 9. EVIDENCIA NEGATIVA

La ausencia de una relación explícita también deberá registrarse cuando sea relevante.

Ejemplo:

```text
No se ha localizado evidencia documental que establezca:
DAT-002 → R-HIS-001
```

Esto no demuestra que la relación sea falsa; demuestra únicamente que **no está documentalmente acreditada**.

---

# 10. FICHA DE CIERRE OBLIGATORIA

Cuando exista evidencia suficiente, cada GAP deberá completar:

```text
GAP-ID:

PARÁMETRO EFECTIVO:

REGLA CONSUMIDORA:

TIPO DE RELACIÓN:

DUPLICIDAD:

MAESTRO / DERIVADO:

FUENTE PRIMARIA:

FUENTE SECUNDARIA:

AUTORIDAD:

EVIDENCIA:

DECISIÓN:

ESTADO:
```

El estado solo podrá pasar a `CERRADO` cuando todos los campos críticos estén sustentados.

---

# 11. PROHIBICIONES

Este documento no autoriza:

1. crear parámetros `HIS-*` artificialmente;
2. elegir un parámetro por coincidencia de nombre;
3. elegir un parámetro por coincidencia de valor;
4. declarar duplicidad sin comparar ámbito y consumidor;
5. declarar maestro → derivado sin transformación documentada;
6. cerrar un GAP sin fuente primaria identificable;
7. modificar el motor o código para ocultar una ausencia de evidencia documental.

---

# 12. RELACIÓN CON F3

Este documento actúa como evidencia especializada para los dos GAP históricos definidos por F3.

La cadena de cierre prevista es:

```text
Fuente documental
      ↓
Evidencia histórica
      ↓
Parámetro efectivo
      ↓
Regla consumidora
      ↓
Matriz Parámetros → Reglas
      ↓
Decision Log
      ↓
Registro de Evidencias F3
      ↓
Auditoría
```

La creación de este documento **no cierra por sí misma** `GAP-HIS-01` ni `GAP-HIS-02`.

---

# 13. ESTADO DEL DOCUMENTO

**Versión:** 1.0  
**Estado:** DOCUMENTO DE EVIDENCIA — PENDIENTE DE RESOLUCIÓN  
**Baseline:** EIOS Vertical MVP

Este documento queda preparado para incorporar las conclusiones documentales que permitan resolver `GAP-HIS-01` y `GAP-HIS-02` sin inferencia no demostrada.
