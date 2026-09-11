# EIOS — ROTACIÓN · METHODOLOGICAL DESIGN v0.2

**Estado:** DEPURADO — PENDIENTE DE AUDIT 2  
**Fecha:** 11/09/2026  
**Base:** `Rotation_Methodological_Audit_1_v0.1.md`

---

## 1. Decisión de depuración

Rotación se divide en dos tracks independientes:

```text
ROT-TRACK-A — SALES INACTIVITY
ROT-TRACK-B — ROTATION METRIC
```

Esta separación evita que la semántica demostrable de `R-ROT-002` quede bloqueada por la fórmula ausente de `R-ROT-001`.

---

# 2. ROT-TRACK-A — SALES INACTIVITY

## 2.1 Propósito

Determinar únicamente si existe evidencia suficiente para afirmar que un artículo registró **cero ventas** durante una ventana autorizada.

No calcula rotación.

## 2.2 Entrada conceptual

```text
article_id
evaluation_date
window_start
window_end
window_authority_ref
sales_source_ref
sales_evidence_refs
sales_scope_ref
sales_records / aggregated_sales_quantity
trace_refs
```

Los nombres físicos quedan para contrato posterior.

## 2.3 Invariantes

1. `window_start <= window_end <= evaluation_date`.
2. La ventana debe proceder de autoridad/configuración identificable.
3. La fuente de ventas debe ser aplicable al artículo/scope.
4. La ventana debe estar completa o suficientemente demostrada para afirmar cero.
5. Ausencia de registros no equivale a cero ventas.
6. Un periodo parcialmente disponible no se reduce silenciosamente.
7. Evidencia contradictoria no se resuelve por suma, recencia o prioridad arbitraria.
8. Ventas negativas, devoluciones o anulaciones no reciben tratamiento económico implícito; requieren semántica de fuente/autorización antes de agregación.

## 2.4 Estados conceptuales

```text
ZERO_SALES_DEMONSTRATED
SALES_PRESENT
NOT_EVIDENCED
CONFLICTING_DATA
NOT_DETERMINABLE
```

Estos estados pertenecen al análisis ROT y no reemplazan `Evidence.state` ni `Assessment`.

## 2.5 Relación con R-ROT-002

Solo:

```text
ZERO_SALES_DEMONSTRATED
+
period/configuration vigente
→ condición factual disponible para evaluar R-ROT-002
```

`SALES_PRESENT` permite determinar que la condición “no existen ventas” no se cumple, siempre que la misma ventana y evidencia sean legítimas.

`NOT_EVIDENCED`, `CONFLICTING_DATA` o `NOT_DETERMINABLE` no equivalen a FALSE y deben impedir una evaluación concluyente cuando la dependencia sea requerida.

---

# 3. Periodo de R-ROT-002

La regla exige “periodo configurado”.

El baseline no demuestra un parámetro vigente que lo represente.

Por tanto:

```text
window_authority_ref = REQUIRED
```

pero:

```text
P-ROT-* = NOT CREATED
P-STK-006 = NOT REUSED
P-DAT-* = NOT REUSED
```

El diseño puede aceptar una ventana autorizada abstracta, pero no puede inventar su fuente de configuración.

---

# 4. Excepciones de R-ROT-002

ROT-TRACK-A no aplica excepciones.

Su responsabilidad termina al producir evidencia sobre actividad/inactividad de ventas.

Las excepciones pertenecen a Rules/autoridad especializada:

```text
pedido confirmado
campaña prevista
operación estratégica
decisión empresarial explícita
```

No se ejecutan dentro del análisis ROT.

---

# 5. ROT-TRACK-B — ROTATION METRIC

## 5.1 Propósito

Reservar la frontera metodológica necesaria para `R-ROT-001` sin fijar una fórmula no autorizada.

## 5.2 Gaps obligatorios

Antes de cualquier cálculo deben cerrarse:

```text
rotation_metric_definition
rotation_formula
rotation_numerator
rotation_denominator
rotation_unit_or_basis
rotation_window
rotation_threshold
source/evidence dependencies
```

## 5.3 Prohibiciones

No se adoptan por defecto:

- stock turnover contable;
- inventory turns;
- sales velocity;
- units sold/day;
- units consumed/day;
- days inventory outstanding;
- cobertura inversa;
- frecuencia de ventas;
- frecuencia de pedidos;
- score de movimiento.

## 5.4 Estado

```text
ROT-TRACK-B = BLOCKED_BY_METHODOLOGICAL_AUTHORITY
```

---

# 6. Relación con STK

ROT puede consumir evidencia compatible procedente de fuentes también utilizadas por STK, pero no transfiere autoridad semántica.

```text
sales != consumption
sales != demand
rotation != coverage
rotation != excess
```

La reutilización de datos no convierte una metodología en otra.

---

# 7. Relación con parámetros

No se crean parámetros en v0.2.

Audit 2 deberá confirmar que existen dos gaps de parametrización explícitos:

```text
ROT-PARAM-G01 — periodo configurado de R-ROT-002
ROT-PARAM-G02 — umbral de R-ROT-001
```

La posible ventana de cálculo de una futura métrica puede constituir un tercer elemento, pero no se declara parámetro hasta disponer de autoridad de la metodología B.

---

# 8. Relación con RDM

Antes de implementación, deberán materializarse dependencias demostradas para cada regla.

Para `R-ROT-002`, como mínimo conceptual:

```text
Rule → sales window/configuration
Rule → evidenced sales activity
```

Para `R-ROT-001`, las dependencias permanecen bloqueadas hasta definir la métrica.

No se editan todavía relaciones canónicas en RDM durante este diseño.

---

# 9. Criterio de cierre parcial

ROT-TRACK-A puede considerarse **metodológicamente definido** si Audit 2 confirma:

- cero ventas ≠ ausencia;
- ventana obligatoria y autorizada;
- completitud demostrable;
- estados explícitos;
- separación de excepciones;
- separación STK;
- ausencia de fórmula ROT implícita.

Esto no autoriza implementación porque siguen pendientes el parámetro de periodo y las dependencias Rule↔Data/Evidence.

ROT-TRACK-B no puede cerrarse sin autoridad metodológica adicional.

---

# 10. Estado

**ROT v0.2 — DEPURADO.**  
**Track A:** candidato a cierre metodológico parcial.  
**Track B:** bloqueado por autoridad metodológica.  
**Implementación:** NO AUTORIZADA.  
**Nuevos parámetros:** 0.
