# ESPECIFICACIÓN DE REGLAS Y CONFIGURACIÓN DE PAGOS — MVP

## EIOS — Enterprise Intelligent Operations System

**Versión:** 1.0  
**Estado:** PROPUESTA TÉCNICA — EVIDENCIA DIRECTA F3  
**Baseline:** EIOS Vertical MVP

---

# 1. Propósito

Este documento formaliza la relación funcional entre los parámetros de pago configurables del MVP y las reglas de pago que los consumen.

Su finalidad es eliminar la ambigüedad existente en `C-07` del Decision Log de Parámetros y proporcionar una fuente documental reproducible para la trazabilidad:

```text
PARÁMETRO DE PAGO
      ↓
CONFIGURACIÓN
      ↓
REGLA DE PAGO
      ↓
RESULTADO
```

Este documento no crea nuevos parámetros ni modifica por sí mismo la autoridad del Catálogo de Parámetros o de la Matriz de Reglas. Formaliza el vínculo funcional entre ambos.

---

# 2. Autoridad y límites

- El Catálogo de Parámetros mantiene la autoridad sobre la definición, identificación y naturaleza de `P-PAG-*`.
- La Matriz de Reglas mantiene la autoridad sobre la condición, resultado y efecto de `R-PAG-*`.
- Este documento tiene autoridad especializada únicamente sobre la **relación funcional parámetro → regla de pago** y su configuración operativa.
- La Capa de Resolución de Conflictos mantiene la autoridad sobre la resolución de resultados contradictorios.

No se considera suficiente la coincidencia de nombres, familias o valores para establecer una relación.

---

# 3. Parámetros de pago del MVP

| ID | Función | Papel funcional |
|---|---|---|
| `P-PAG-001` | Plazo mínimo deseado | Límite mínimo aceptable de plazo de pago |
| `P-PAG-002` | Plazo objetivo | Objetivo de plazo de pago para negociación |
| `P-PAG-003` | Tolerancia plazo | Margen permitido respecto al objetivo |
| `P-PAG-004` | Considerar plazo | Control de consideración del plazo en la evaluación |
| `P-PAG-005` | Descuento pronto pago | Factor económico para evaluar el efecto de pago anticipado |

---

# 4. Reglas de pago del MVP

## R-PAG-001 — Plazo de pago inferior al objetivo

La regla evalúa si el proveedor ofrece un plazo inferior al establecido como objetivo.

Resultado: **NEGOCIAR**.

Efecto: **R2 — NEGOCIACIÓN / ALTA**.

## R-PAG-002 — Plazo de pago insuficiente ante riesgo financiero

La regla evalúa si la operación puede ser viable únicamente si se amplía el plazo de pago.

Resultado: **COMPRAR CONDICIONADO**.

Condición de compra: conseguir el plazo de pago mínimo establecido.

Efecto: **R1 — CONDICIONANTE / ALTA**.

---

# 5. Mapa funcional de configuración

## 5.1 R-PAG-001

```text
P-PAG-002 — Plazo objetivo
          ↓
      objetivo de pago
          ↓
R-PAG-001 — plazo ofrecido < objetivo
          ↓
       NEGOCIAR
```

**Relación:** `P-PAG-002 → R-PAG-001`  
**Estado:** DEMOSTRADA — DIRECTA.

`P-PAG-004` actúa como control de consideración del plazo y no sustituye al umbral objetivo.

Cuando `P-PAG-004` esté desactivado, el plazo no se utilizará como criterio de esta evaluación ordinaria.

**Relación:** `P-PAG-004 → R-PAG-001`  
**Estado:** DEMOSTRADA — CONTROL FUNCIONAL.

---

## 5.2 R-PAG-002

```text
P-PAG-001 — Plazo mínimo deseado
          ↓
     mínimo aceptable
          ↓
R-PAG-002 — viabilidad condicionada al plazo mínimo
          ↓
  COMPRAR CONDICIONADO
```

**Relación:** `P-PAG-001 → R-PAG-002`  
**Estado:** DEMOSTRADA — DIRECTA.

`P-PAG-004` actúa como control de consideración del plazo también en esta evaluación.

**Relación:** `P-PAG-004 → R-PAG-002`  
**Estado:** DEMOSTRADA — CONTROL FUNCIONAL.

---

# 6. P-PAG-003 — Tolerancia de plazo

`P-PAG-003` define el margen permitido respecto al objetivo de pago.

Se utiliza como parámetro derivado de negociación cuando la política de pago permita aceptar una desviación respecto de `P-PAG-002` sin activar automáticamente la condición crítica.

**Relación:** `P-PAG-003 → R-PAG-001`  
**Estado:** DEMOSTRADA — DERIVADA.

La tolerancia no sustituye a `P-PAG-001` como mínimo aceptable. Su función es modular la evaluación alrededor del objetivo.

---

# 7. P-PAG-005 — Descuento pronto pago

`P-PAG-005` representa el factor económico asociado al descuento por pronto pago.

No se utiliza como umbral directo de `R-PAG-001` ni `R-PAG-002`.

Su función es alimentar el análisis económico de la condición de pago y, cuando exista evidencia del descuento aplicable, el cálculo de coste efectivo utilizado por la lógica de negociación.

**Relación funcional:**

```text
P-PAG-005
     ↓
cálculo coste/beneficio de pronto pago
     ↓
contexto económico de negociación
     ↓
R-PAG-001 / R-PAG-002 cuando corresponda
```

**Estado:** DEMOSTRADA — INDIRECTA / DERIVADA.

No se interpreta como un umbral adicional de plazo.

---

# 8. Matriz de relaciones

| Parámetro | Regla | Tipo de relación | Estado |
|---|---|---|---|
| `P-PAG-001` | `R-PAG-002` | Directa | **DEMOSTRADA** |
| `P-PAG-002` | `R-PAG-001` | Directa | **DEMOSTRADA** |
| `P-PAG-003` | `R-PAG-001` | Derivada | **DEMOSTRADA** |
| `P-PAG-004` | `R-PAG-001` | Control funcional | **DEMOSTRADA** |
| `P-PAG-004` | `R-PAG-002` | Control funcional | **DEMOSTRADA** |
| `P-PAG-005` | `R-PAG-001 / R-PAG-002` | Indirecta / derivada | **DEMOSTRADA** |

---

# 9. Restricciones de interpretación

1. `P-PAG-001` y `P-PAG-002` no son equivalentes.
2. `P-PAG-001` representa el mínimo aceptable; `P-PAG-002` representa el objetivo de negociación.
3. `P-PAG-003` modula el objetivo y no sustituye el mínimo aceptable.
4. `P-PAG-004` controla si el plazo debe entrar en la evaluación; no define por sí mismo un umbral.
5. `P-PAG-005` es económico/derivado y no debe tratarse como umbral de plazo.
6. Ninguno de estos parámetros puede alterar por sí mismo la autoridad de la CRC.

---

# 10. Evidencia F3

Esta especificación constituye la evidencia documental directa de la relación funcional entre los parámetros de pago y las reglas `R-PAG-*`.

Para cada relación, la evidencia reproducible es:

- identificador del parámetro;
- definición funcional;
- identificador de la regla;
- condición de la regla;
- función del parámetro dentro de la evaluación;
- tipo de relación;
- estado de demostración.

La evidencia debe ser versionada conjuntamente mediante GitHub y referenciada por el Registro de Evidencias de Trazabilidad F3.

---

# 11. Cierre de C-07

La decisión `C-07` del Decision Log establecía que las relaciones entre `P-PAG-*` y `R-PAG-*` no debían asignarse sin evidencia documental suficiente.

Esta especificación aporta dicha evidencia y establece las siguientes relaciones funcionales:

- `P-PAG-001 → R-PAG-002`;
- `P-PAG-002 → R-PAG-001`;
- `P-PAG-003 → R-PAG-001`;
- `P-PAG-004 → R-PAG-001`;
- `P-PAG-004 → R-PAG-002`;
- `P-PAG-005 → R-PAG-001 / R-PAG-002` mediante cálculo económico derivado.

La actualización de los documentos de autoridad correspondientes deberá incorporar estas relaciones sin redefinir las condiciones de las reglas.

---

# 12. Estado

**Versión:** 1.0  
**Estado:** PROPUESTA TÉCNICA — EVIDENCIA DIRECTA F3  
**Baseline:** EIOS Vertical MVP

Este documento es la fuente especializada para la relación funcional entre parámetros y reglas de pago dentro del MVP.
