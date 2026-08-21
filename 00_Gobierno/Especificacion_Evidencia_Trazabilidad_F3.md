# ESPECIFICACIÓN DE EVIDENCIA DE TRAZABILIDAD — F3

## EIOS — Enterprise Intelligent Operations System

**Versión:** 1.0  
**Estado:** PROPUESTA TÉCNICA — F3  
**Ámbito:** EIOS Vertical MVP  
**Fecha:** 21/08/2026

---

# 1. PROPÓSITO

Esta especificación define qué debe contener una evidencia de trazabilidad para demostrar, de forma auditable y reproducible, la relación entre:

- parámetros;
- reglas;
- datos;
- evidencias de entrada;
- resultados;
- excepciones;
- y componentes que consumen o producen dicha información.

Su objetivo es impedir que una relación **Parámetro → Regla**, **Dato → Regla** o **Regla → Resultado** se considere oficial únicamente por similitud semántica, proximidad documental o coincidencia de valores.

La ausencia de evidencia suficiente deberá permanecer explícitamente como **NO DEMOSTRADA** o **GAP**, sin completar la cadena por inferencia.

---

# 2. PRINCIPIOS DE CONTROL

## 2.1 Evidencia antes que inferencia

Una relación solo podrá declararse **DEMOSTRADA** cuando exista una fuente documental o técnica identificable que la sustente.

La coincidencia de:

- nombres;
- códigos;
- valores;
- unidades;
- descripciones similares;
- o comportamiento aparentemente equivalente

no constituye por sí sola evidencia de dependencia.

## 2.2 Una ausencia no implica una creación

Si no se encuentra el parámetro, regla, documento o dependencia buscada, el resultado será:

- **NO IDENTIFICADO**, cuando no se ha localizado la entidad;
- **NO DEMOSTRADO**, cuando la entidad existe pero su relación no está acreditada;
- **GAP**, cuando la ausencia afecta a una capacidad necesaria de gobierno, trazabilidad o ejecución.

No se crearán parámetros, reglas o documentos únicamente para cerrar artificialmente un hueco de trazabilidad.

## 2.3 Autoridad documental

La evidencia deberá identificar siempre qué documento tiene autoridad sobre el aspecto que se pretende demostrar.

Como mínimo se distinguirá entre:

- **Catálogo de Parámetros:** existencia, definición y configuración de parámetros.
- **Matriz de Reglas MVP:** condiciones, lógica y resultados individuales de las reglas.
- **Capa de Resolución de Conflictos (CRC):** consolidación de resultados de reglas, salvaguardas, prioridades, excepciones y recomendación final.

Cuando una dependencia entre estas capas no esté documentada, no se considerará demostrada.

---

# 3. OBJETO DE EVIDENCIA

Cada relación auditada deberá poder representarse mediante una ficha con la siguiente estructura mínima:

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
| `Estado` | Sí | DEMOSTRADA / NO DEMOSTRADA / GAP / CONFLICTIVA. |
| `Autoridad` | Sí | Documento que posee autoridad sobre la materia. |
| `Versión` | Sí | Versión de la fuente utilizada. |
| `Commit` | Recomendado | Commit de GitHub que permite reproducir la evidencia. |
| `Observaciones` | No | Matices, dependencias o limitaciones. |

---

# 4. TIPOS DE RELACIÓN

La especificación reconoce, como mínimo, las siguientes relaciones:

### `PARAMETRO → REGLA`

El parámetro interviene en la condición, umbral o configuración de una regla.

### `DATO → REGLA`

Un dato de entrada interviene directamente en la evaluación de una regla.

### `REGLA → RESULTADO`

La regla produce un resultado definido documentalmente.

### `REGLA → REGLA`

Una regla depende funcionalmente de otra regla o utiliza su resultado.

Esta relación requiere evidencia explícita y no deberá deducirse únicamente por orden de ejecución.

### `REGLA → CRC`

La regla entrega un resultado a la Capa de Resolución de Conflictos para su consolidación.

### `PARAMETRO → CALCULO`

El parámetro alimenta un cálculo intermedio cuyo resultado puede ser utilizado posteriormente por una regla.

### `DATO → CALCULO → REGLA`

Cadena indirecta en la que el dato no alimenta directamente la regla, sino un cálculo o indicador intermedio.

---

# 5. NIVELES DE EVIDENCIA

## 🟢 DIRECTA

La fuente identifica explícitamente ambos extremos de la relación.

Ejemplo conceptual:

`PRE-003 → R-HIS-001`

cuando un documento oficial indique expresamente que `PRE-003` alimenta `R-HIS-001`.

## 🟡 INDIRECTA

La cadena completa puede reproducirse mediante varias fuentes oficiales que documentan cada tramo, sin que una única fuente escriba la relación completa.

Debe registrarse cada tramo por separado.

## 🟡 CONTEXTUAL

La documentación demuestra que los conceptos están relacionados funcionalmente, pero no permite acreditar una dependencia técnica o paramétrica concreta.

No puede utilizarse para convertir una relación en oficial.

## 🔴 CONFLICTIVA

Dos o más fuentes oficiales atribuyen la misma relación o concepto a autoridades diferentes, o presentan definiciones incompatibles.

Debe resolverse antes de modificar el catálogo o las reglas.

---

# 6. ESTADOS DE TRAZABILIDAD

| Estado | Significado | Acción |
|---|---|---|
| **DEMOSTRADA** | Existe evidencia suficiente y reproducible. | Puede incorporarse a la trazabilidad oficial. |
| **NO DEMOSTRADA** | La relación es plausible, pero no existe evidencia suficiente. | No modificar documentación basándose en ella. |
| **NO IDENTIFICADA** | No se ha localizado la entidad o fuente buscada. | Auditar fuentes adicionales antes de crearla. |
| **GAP** | Falta una definición o dependencia necesaria para completar una cadena crítica. | Registrar, priorizar y resolver documentalmente. |
| **CONFLICTIVA** | Existen fuentes incompatibles o autoridades concurrentes. | Resolver autoridad antes de modificar. |

---

# 7. CADENA DE TRAZABILIDAD MÍNIMA

Cuando una regla dependa de parámetros y datos, la evidencia deberá poder reconstruir la cadena completa:

```text
DATO / FUENTE
      ↓
PARÁMETRO (si existe)
      ↓
CÁLCULO / INDICADOR (si aplica)
      ↓
REGLA
      ↓
RESULTADO
      ↓
CRC
      ↓
RECOMENDACIÓN
```

No todos los casos requerirán todos los niveles. La ficha deberá indicar expresamente qué tramos existen y cuáles no están demostrados.

---

# 8. REQUISITOS ESPECÍFICOS PARA F3

Para cada regla MVP que pueda depender de configuración, deberá comprobarse como mínimo:

1. existencia de la regla;
2. definición de la condición;
3. existencia de parámetros candidatos;
4. relación documentada entre parámetro y regla;
5. existencia de datos de entrada;
6. existencia de cálculo intermedio, si procede;
7. resultado definido;
8. relación con CRC cuando corresponda;
9. fuente de autoridad;
10. versión/commit reproducible.

Una coincidencia de nombre o valor no será suficiente para cerrar el punto 4.

---

# 9. TRATAMIENTO DE DUPLICIDADES APARENTES

Cuando dos parámetros parezcan representar el mismo concepto, como consecuencia de compartir nombre, unidad o valor, se deberán conservar ambos hasta demostrar su equivalencia funcional.

La auditoría deberá comprobar:

- definición;
- ámbito;
- consumidor;
- autoridad;
- ciclo de vida;
- unidad;
- valor por defecto;
- y regla o cálculo consumidor.

Solo después podrá clasificarse el caso como:

- **DUPLICIDAD REAL**;
- **CONCEPTOS DISTINTOS**;
- **PARÁMETRO MAESTRO + DERIVADO**;
- **GAP DE DEFINICIÓN**;
- **CONFLICTO DE AUTORIDAD**.

---

# 10. CASO DE REFERENCIA F3 — HISTÓRICO

La auditoría actual ha identificado, sin resolver todavía, los siguientes pares:

### GAP-HIS-01

```text
PRE-003 — Antigüedad máxima de referencia
        ↕
DAT-002 — Antigüedad máxima de referencia de precio
        ↓
R-HIS-001 — Referencia demasiado antigua
```

La especificación exige demostrar documentalmente cuál de los parámetros, o qué combinación de ellos, alimenta la regla.

No se permite concluir que son duplicados por compartir el valor de 12 meses.

### GAP-HIS-02

```text
PRE-006 — Nº mínimo de compras comparables
        ↕
DAT-003 — Nº mínimo de registros históricos
        ↓
R-HIS-002 — Histórico insuficiente
```

La especificación exige determinar si ambos conceptos son distintos, si uno deriva del otro o si uno de ellos es el parámetro efectivo de la regla.

No se permite fusionarlos por compartir el valor de 2 operaciones.

### R-HIS-003

La regla evalúa comparabilidad de operaciones históricas. Si no existe un umbral configurable explícito, no deberá crearse un parámetro `HIS-*` por defecto.

La ausencia de parámetro deberá clasificarse como **NO DEMOSTRADA** o **NO NECESARIAMENTE PARAMÉTRICA**, según la evidencia disponible.

---

# 11. CRITERIOS DE ACEPTACIÓN DE UNA EVIDENCIA

Una evidencia F3 solo podrá marcarse como **DEMOSTRADA** si:

- la fuente existe realmente;
- la ruta/ubicación puede reproducirse;
- la versión está identificada;
- la relación está expresamente soportada o puede reconstruirse mediante una cadena de evidencias documentadas;
- la autoridad documental es conocida;
- no existe una fuente oficial concurrente sin resolver;
- y no se ha utilizado una inferencia semántica como sustituto de evidencia.

Si falla cualquiera de estos puntos críticos, la evidencia no podrá cerrarse como DEMOSTRADA.

---

# 12. CONTROL DE CAMBIOS

Esta especificación no modifica por sí misma:

- el Catálogo de Parámetros;
- la Matriz de Reglas;
- la CRC;
- ni las reglas del MVP.

Su función es establecer el **criterio de evidencia** que deberá cumplirse antes de realizar dichas modificaciones.

Cualquier cambio posterior deberá mantener:

```text
EVID-ID
→ fuente
→ versión
→ decisión
→ modificación
→ commit
```

permitiendo reconstruir por qué se tomó la decisión.

---

# 13. ESTADO ACTUAL F3

| Área | Estado |
|---|---|
| Reglas `HIS` | 🟢 Identificadas |
| Reglas `ROT` | 🟢 Identificadas |
| Reglas `PROV` | 🟢 Identificadas |
| Trazabilidad Parámetro → Regla | 🟡 En construcción |
| `PRE-003` ↔ `DAT-002` | 🔴 GAP-HIS-01 |
| `PRE-006` ↔ `DAT-003` | 🔴 GAP-HIS-02 |
| Parámetros nuevos `HIS-*` | ⛔ No autorizados por esta especificación |
| Modificación del catálogo | ⛔ No autorizada por esta especificación |
| Modificación de reglas | ⛔ No autorizada por esta especificación |

---

# 14. PRINCIPIO DE CIERRE

> **EIOS no considerará trazada una dependencia porque parezca lógica. La dependencia deberá poder demostrarse, reproducirse y atribuirse a una fuente con autoridad.**

Esta especificación constituye el criterio de control para la construcción de la evidencia F3 y evita que la fase de trazabilidad genere modificaciones prematuras en parámetros, reglas o arquitectura.
