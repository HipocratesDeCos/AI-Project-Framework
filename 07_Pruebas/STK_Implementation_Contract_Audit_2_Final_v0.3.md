# EIOS — STK Implementation Contract · Audit 2 Final v0.3

**Estado:** NO SUPERADA — SEGUNDA DEPURACIÓN FINAL REQUERIDA  
**Contrato auditado:** `08_Implementacion/STK_Implementation_Contract.md` v0.4  
**Fecha:** 11/09/2026

---

## 1. Dictamen

La v0.4 incorpora correctamente C1…C7 y mantiene resueltos A1…A9 y B1…B13. La revisión de consistencia entre M05, M07 y M08 detecta cuatro ambigüedades físicas adicionales. Ninguna cambia política empresarial; cierran tipos, horizonte, estado y trazabilidad.

**DICTAMEN:** NO CERRAR v0.4.

---

## 2. D1 — Stock proyectado negativo incompatible con `NormalizedQuantity`

**Tipo:** BLOQUEANTE.

M05 autoriza conservar un saldo proyectado negativo como evidencia de déficit. `NormalizedQuantity`, en cambio, representa cantidades físicas y prohíbe valores conocidos negativos. M07 v0.4 utiliza `stock_reference: NormalizedQuantity`, aunque metodológicamente puede consumir un punto futuro M05.

**Corrección requerida:** separar la referencia analítica de stock de la cantidad física mediante un tipo equivalente a `StockReferenceValue`, que conserve `reference_kind = CURRENT_AVAILABLE | PROJECTED`, `reference_date`, identidad STK, unidad, estado, fuente/traza y valor. `CURRENT_AVAILABLE` no puede ser negativo; `PROJECTED` sí puede serlo. M07 consume este tipo sin transformar un déficit proyectado en cantidad física.

---

## 3. D2 — M08: un conjunto de IDs no modela asignación parcial

**Tipo:** BLOQUEANTE.

`already_allocated_ids` marca un pedido completo como utilizado aunque solo una parte de su cantidad pendiente haya absorbido exceso. Sustituirlo por otro ID tampoco resuelve el caso de varias demandas aplicables cuando `absorbed_excess` es menor que la suma disponible: elegir qué pedido consume primero introduciría una prioridad no autorizada.

**Corrección requerida:**

- conservar un ledger cuantitativo por `confirmed_demand_id` (`already_allocated_quantity`);
- calcular para cada pedido `remaining_allocatable = pending_quantity - already_allocated_quantity`;
- preservar la fórmula agregada autorizada `absorbed_excess = min(excess_quantity, total_remaining_applicable)`;
- cuando la absorción positiva deba distribuirse entre más de un pedido y existan múltiples repartos válidos, STK **no elige orden/prioridad**;
- la materialización por pedido requiere un `allocation_plan` explícito y trazable que indique ID y cantidad aplicada; STK solo lo valida contra el total agregado, el exceso y los saldos disponibles;
- el ledger de salida suma únicamente las cantidades efectivamente asignadas.

Esto preserva la autoridad M08 sin inventar FIFO, prioridad por fecha, cliente, ID u otro criterio comercial.

---

## 4. D3 — Tratamiento de movimientos `NOT_APPLICABLE`

**Tipo:** BLOQUEANTE.

`ProjectionMovement.state` admite `NOT_APPLICABLE`, pero v0.4 no establece si contamina la proyección o se omite. La semántica general M09 diferencia no aplicable de desconocido.

**Corrección requerida:** un movimiento `NOT_APPLICABLE` suficientemente evidenciado no aporta cantidad y no contamina la determinabilidad; permanece en trazabilidad como excluido. `UNKNOWN`, `NOT_EVIDENCED` y `CONFLICTING_DATA` sí propagan incertidumbre según su fecha.

---

## 5. D4 — Horizonte y fecha de referencia insuficientemente materializados

**Tipo:** BLOQUEANTE.

M05 exige horizonte explícito y trazable, pero `horizon_end` carece de referencia de autoridad/fuente. M07 puede evaluar un punto futuro pero la identidad v0.4 solo conserva `evaluation_date`. M08 exige demostrar que la entrega confirmada es aplicable al horizonte evaluado, pero ese horizonte no está físicamente ligado a la absorción.

**Corrección requerida:**

- `StockProjectionInput` incorpora `horizon_source_ref`/traza o una política equivalente; no se inventa P-PYE-001;
- `StockReferenceValue` conserva `reference_date` distinta de la fecha base cuando procede de M05;
- `ExcessResult` conserva `reference_date`;
- `AllocationScope`/entrada M08 conserva `horizon_end` y referencia trazable del horizonte, además de `evaluation_date` y `excess_reference_date`;
- la aplicabilidad temporal se valida con esos datos sin introducir un horizonte por defecto.

---

## 6. Resultado

- A1…A9: resueltos.
- B1…B13: resueltos.
- C1…C7: resueltos en v0.4.
- D1…D4: abiertos en v0.4.

**Siguiente paso:** DEPURACIÓN FINAL 2 → Audit 2 Final independiente.
