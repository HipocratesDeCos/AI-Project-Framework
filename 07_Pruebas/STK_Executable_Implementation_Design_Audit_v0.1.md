# EIOS — STK Executable Implementation Design · Audit v0.1

**Estado:** NO SUPERADA — DEPURACIÓN REQUERIDA  
**Diseño auditado:** `08_Implementacion/STK_Executable_Implementation_Design_v0.1.md`  
**Contrato:** STK Implementation Contract v0.17 cerrado  
**Fecha:** 11/09/2026

---

## 1. Dictamen

El diseño conserva correctamente la frontera C0, la separación Rules/CRC y el enfoque Pydantic/puro. Sin embargo, todavía permite divergencias físicas relevantes entre implementaciones.

Se identifican **8 hallazgos**, todos resolubles sin nueva autoridad empresarial.

**DICTAMEN:** NO MATERIALIZAR CÓDIGO todavía. Resolver A1…A8 y repetir Audit 2.

---

## 2. A1 — Propagación de estados no es determinista

**BLOQUEANTE.**

El diseño indica “propagar estado” pero no fija cómo combinar varias dependencias no determinadas. Dos implementaciones podrían devolver `UNKNOWN` o `NOT_EVIDENCED` ante el mismo conjunto de entradas.

**Depuración requerida:** implementar una función técnica común que preserve el estado más específico sin inventar certeza:

- cualquier `CONFLICTING_DATA` dependiente → `CONFLICTING_DATA`;
- en ausencia de conflicto, presencia de `NOT_EVIDENCED` → `NOT_EVIDENCED`;
- en ausencia de ambos, presencia de `UNKNOWN` → `UNKNOWN`;
- `NOT_APPLICABLE` solo excluye el elemento cuya no aplicabilidad está demostrada y nunca oculta otra dependencia obligatoria incierta.

Las `issue_refs` se unen de forma estable, sin duplicados y preservando orden de primera aparición.

Esto materializa M09/M10; no crea prioridad empresarial.

---

## 3. A2 — Falta explicitar qué modelos producen estado vs error estructural

**BLOQUEANTE.**

El diseño lista modelos pero no separa suficientemente validación estructural de evaluabilidad empresarial.

Ejemplo: `NormalizedQuantity(state=UNKNOWN, value=None)` debe ser válido; `NormalizedQuantity(state=KNOWN, value=None)` debe ser rechazado. Lo mismo aplica a parámetro, forecast, política, ledger y otros tipos.

**Depuración requerida:** el diseño debe exigir validadores `state ↔ payload` por familia de modelos y prohibir que engine capture un `ValidationError` para transformarlo en `UNKNOWN`.

---

## 4. A3 — Schedule de demanda M05 queda condicionalmente ambiguo

**BLOQUEANTE.**

La frase “cuando exista demanda seleccionada que deba intervenir” no define el gate físico de completitud.

**Depuración requerida:**

- si la proyección contiene movimientos `AUTHORIZED_DEMAND`, `DemandProjectionSchedule KNOWN` es obligatorio;
- los `movement_id` de esos movimientos deben coincidir exactamente con `schedule.demand_movement_ids`;
- si una evaluación declara que la demanda seleccionada forma parte de la proyección pero no existe transformación/reconciliación autorizada, la proyección no puede ser `KNOWN`;
- la mera existencia de una tasa no genera movimientos;
- `CONFIRMED_DEMAND`, `RESERVATION` y otros movimientos no se clasifican como `AUTHORIZED_DEMAND` para satisfacer artificialmente el schedule.

---

## 5. A4 — M06 necesita validación global, no solo por movimiento

**BLOQUEANTE.**

Validar cada `ProjectionMovement` individualmente no impide que dos movimientos distintos representen la misma cantidad logística como `PENDING_ORDER` e `IN_TRANSIT`.

**Depuración requerida:** la proyección debe construir un índice por `supply_identity`/segmento logístico y rechazar:

- identidad logística duplicada contribuyente;
- coexistencia pending + transit para la misma cantidad;
- duplicación de una parcialidad identificada.

La simple diferencia de `movement_id` no convierte dos cantidades en suministros independientes.

---

## 6. A5 — Composición de demanda confirmada necesita algoritmo explícito

**BLOQUEANTE.**

El diseño exige preservarla, pero no especifica el algoritmo físico que garantiza igualdad exacta.

**Depuración requerida:**

- opening: derivar por agrupación de `StockCommitmentComponent` comerciales;
- cada `CONFIRMED_DEMAND` M05 añade exactamente `quantity` al `confirmed_demand_id` y el `demand_segment_id` correspondiente;
- mismo segmento no puede aparecer dos veces;
- ordenar la colección resultante de forma determinista por primera aparición o clave estable documentada;
- `StockReferenceValue` y `ExcessResult` copian la composición; no la recalculan.

---

## 7. A6 — M07 rate necesita normalización numérica cerrada

**BLOQUEANTE.**

El diseño dice “normalized_rate” pero no declara qué acepta físicamente. Inferir si `10` significa 10 % o proporción 10 violaría M07.

**Depuración requerida:** `ConfiguredParameterValue(STK-005)` solo puede consumirse como RATE cuando `normalization_ref`/unidad ya demuestran una proporción adimensional normalizada. El engine recibe el valor normalizado y no divide entre 100 por heurística.

Análogamente `STK-004` debe llegar normalizado a días; el engine no interpreta nombres/unidades libres.

---

## 8. A7 — M08 requiere reconciliación por pedido antes de calcular totales

**BLOQUEANTE.**

El diseño describe la fórmula global, pero debe exigir primero una tabla determinista por `confirmed_demand_id`:

```text
pending
incorporated_before_M08
already_allocated
remaining_allocatable
```

**Depuración requerida:**

- IDs de pedidos aplicables únicos;
- ledger solo del mismo scope/article/date;
- `incorporated + allocated <= pending` por pedido;
- el plan solo contiene pedidos presentes y no supera el remaining individual;
- suma del plan por pedido y global verificadas;
- `resulting_ledger` conserva entradas previas byte/semánticamente equivalentes y añade exactamente el plan.

---

## 9. A8 — Criterio de mínimo/depletion con incertidumbre debe implementarse literalmente

**BLOQUEANTE.**

Un engine podría calcular un mínimo parcial aunque una fecha posterior sea incierta, o declarar depletion con incertidumbre previa.

**Depuración requerida:**

- `minimum_projected_stock` solo `KNOWN` si todo el horizonte relevante está determinado;
- `depletion_date` solo `KNOWN` si ninguna incertidumbre anterior puede adelantar la primera fecha `<=0`;
- opening cero `KNOWN` → evaluación;
- horizonte completo `KNOWN` sin agotamiento → `NOT_APPLICABLE`;
- no se usa el último punto conocido como sustituto de horizonte completo.

---

## 10. Verificaciones sin bloqueo

- C0 permanece sin cambios.
- `eios.core` no depende de `eios.stock`.
- M02/M03 no reciben fórmula.
- No se implementa forecasting, ventas→demanda, SQL, API ni decisión.
- `PYE-001` es único parámetro PYE operativo en esta frontera.
- No se introducen valores iniciales como defaults.

---

## 11. Resultado

**A1…A8: ABIERTOS.**

Siguiente paso: **DEPURAR diseño v0.2 → AUDITAR 2**.
