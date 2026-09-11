# EIOS — STK Executable Implementation Design v0.3

**Estado:** DEPURADO A1…A8 + B1…B4 — PENDIENTE DE AUDIT 2 FINAL  
**Baseline:** `main @ c2945b56f41ac7cac3df15c2ce0d16950387e0b3`  
**Contrato cerrado:** `08_Implementacion/STK_Implementation_Contract.md` v0.17  
**Fecha:** 11/09/2026

---

## 1. Propósito y paquete

Implementación ejecutable mínima y estricta del contrato STK v0.17.

```text
eios/stock/
├── __init__.py
├── models.py
└── engine.py

tests/
└── test_stock_engine.py
```

C0 no se modifica. `eios.stock → eios.core` es la única dirección permitida.

---

## 2. Estrategia Pydantic

Modelos Pydantic v2, `extra="forbid"`, `str_strip_whitespace=True`, `frozen=True` para hechos/resultados.

- error estructural → `ValidationError/ValueError`;
- incertidumbre empresarial válida → estado tipado;
- el engine no convierte excepciones estructurales en `UNKNOWN`;
- `KNOWN` exige payload material;
- estados no determinados permiten nulos evidenciales;
- `CONFLICTING_DATA` exige incidencia de contradicción;
- Decimal finito; negativos solo para saldos proyectados.

---

## 3. Modelos

Se materializan literalmente los modelos públicos del contrato v0.17: estados/incidencias, scope/context/identity, cantidades/políticas/parámetros, disponibilidad, consumo/demanda, horizon, movimientos/schedule, proyección, M07 y M08.

No se crean modelos de Rules, CRC o decisión final.

---

## 4. API pura

```text
build_identity(context)
calculate_stock_availability(payload)
build_projection_horizon(context, parameter)
calculate_historical_demand(context, policy, periods)
use_authorized_forecast(context, forecast)
calculate_coverage(availability, demand)
calculate_stock_projection(payload: StockProjectionInput)
build_current_stock_reference(availability)
build_projected_stock_reference(projection, reference_date)
calculate_excess(stock_reference, maximum_basis, tolerance_basis)
calculate_confirmed_demand_absorption(excess, orders, ledger, allocation_scope, allocation_plan)
```

Helpers privados deterministas para estado, incidencias/trazas, composición, M06 y M08. Sin reloj, red, DB, UUID o estado global.

---

## 5. Propagación A1/A2

Para dependencias obligatorias materiales:

1. `CONFLICTING_DATA`;
2. `NOT_EVIDENCED`;
3. `UNKNOWN`;

`NOT_APPLICABLE` solo excluye la dependencia cuya no aplicabilidad esté demostrada y nunca oculta otra dependencia obligatoria incierta.

`issue_refs/trace_refs`: unión estable sin duplicados, orden de primera aparición.

Cada modelo aplica `state ↔ payload`; un KNOWN incompleto se rechaza y un UNKNOWN no exige datos ficticios.

---

## 6. M01 / demanda / cobertura

Histórico exige selección `KNOWN/HISTORICAL_CONSUMPTION`, política `KNOWN`, `STK-006`, periodos exactos y completos, mismo scope/artículo/unidad/metodología:

```text
historical_daily_demand = sum(quantity) / sum(evidenced_days)
```

Forecast exige selección `KNOWN/AUTHORIZED_FORECAST`, versión exacta e intervalo cerrado aplicable.

Cobertura usa stock disponible actual:

- demanda >0 → FINITE;
- demanda =0 KNOWN → UNBOUNDED;
- dependencia incierta → propagación.

---

## 7. Horizon M05

`PYE-001` efectivo, entero positivo no booleano, normalizado a días:

```text
horizon_end = evaluation_date + horizon_days
```

90 días nunca es fallback.

---

## 8. DemandProjectionSchedule B1/B2/B4

`demand_schedule` es **miembro obligatorio de `StockProjectionInput`**, no argumento externo opcional. Puede tener estado no determinado; si una proyección depende de demanda y el schedule no es KNOWN, la proyección completa no puede ser KNOWN.

Antes del cálculo diario, para `payload.movements.state == KNOWN`:

```text
expected_schedule_ids = movement_id de TODOS los items con
source_kind in {AUTHORIZED_DEMAND, CONFIRMED_DEMAND}
```

Se exige:

```text
set/tupla única del schedule == expected_schedule_ids exactos
```

sin filtrar previamente por conveniencia temporal. Duplicados son error estructural.

Además:

- selection/demand/context/horizon compatibles;
- `schedule_from = evaluation_date + 1`;
- `schedule_to = horizon_end`;
- `transformation_ref`, `reconciliation_ref`, fuente/trazas obligatorios para KNOWN;
- AUTHORIZED_DEMAND = demanda genérica transformada, sin IDs comerciales;
- CONFIRMED_DEMAND = demanda comercial, con `confirmed_demand_id + demand_segment_id`;
- ambos pertenecen al schedule;
- reservas/otras necesidades no se usan para completar artificialmente el set del schedule;
- una tasa nunca genera movimientos internamente.

Un item de demanda explícitamente `NOT_APPLICABLE` sigue perteneciendo a la colección/evidencia y debe estar reconciliado por el schedule; no se borra para conseguir igualdad artificial.

---

## 9. M05/M06 — movimientos

Contribuyentes KNOWN: estrictamente futuros, dentro de horizon, cantidad/normalización/traza válidas y dirección compatible.

Índices globales:

- `movement_id` único;
- `demand_segment_id` comercial único;
- `commitment_id` opening no reutilizado como necesidad nueva;
- `supply_identity`/identidad de parcialidad logística única.

Se rechaza una misma cantidad M06 duplicada o representada simultáneamente como pending/transit aunque use movement IDs distintos.

Opening reconciliation obligatoria para RESERVATION/OTHER_AUTHORIZED_NEED según contrato.

---

## 10. Proyección y composición

```text
closing = previous_closing + inflows(date) - outflows(date)
```

Sin orden intradía; saldo negativo preservado.

Composición confirmada:

1. opening deriva de committed components comerciales;
2. cada CONFIRMED_DEMAND contabilizado añade exactamente su cantidad/segmento;
3. no hay segmentos duplicados;
4. orden determinista: opening por orden de componentes, después movimientos por `(effective_date, movement_id)`;
5. cada point conserva solo composición hasta su fecha;
6. StockReference y ExcessResult copian exactamente.

Mínimo/depletion:

- mínimo KNOWN solo con horizonte completo determinado;
- depletion KNOWN solo sin incertidumbre anterior que pueda adelantarla;
- opening cero KNOWN → evaluation_date;
- horizonte KNOWN sin agotamiento → NOT_APPLICABLE;
- nunca usar mínimo parcial como final.

---

## 11. M07

Ramas exclusivas:

```text
maximum: DIRECT_QUANTITY | COVERAGE_MAXIMUM
tolerance: QUANTITY | RATE
```

`STK-004` debe llegar normalizado a días; `STK-005` RATE debe llegar como proporción adimensional ya demostrada mediante unidad/normalization_ref. El engine no divide por 100 ni interpreta nombres.

```text
stock_maximum = coverage_maximum_days * daily_demand
excess_tolerance_quantity = stock_maximum * normalized_rate
excess_threshold = stock_maximum + tolerance
excess_quantity = max(0, reference - threshold)
```

---

## 12. M08 por ramas B3

Evaluación estrictamente por necesidad material:

1. `ExcessResult` no determinado → resultado M08 no verificable/dependiente; no se fabrica absorción.
2. exceso determinado `NO_EXCESS` o `WITHIN_TOLERANCE` → `NO_APLICABLE`, absorción 0 y residual conforme al contrato; **no se exige ledger** para demostrar una asignación que no procede.
3. `EXCESS` + colección de pedidos `KNOWN` vacía → `NO_EXISTE`; plan vacío.
4. con `EXCESS` y pedidos potenciales, se evalúa aplicabilidad y solo entonces ledger/saldos son materiales para impedir reutilización.
5. falta de evidencia que impida demostrar inclusión/exclusión → `NO_VERIFICABLE`.

Para cada pedido materialmente aplicable:

```text
remaining = pending - incorporated_before_M08 - already_allocated
```

- IDs de pedidos únicos;
- scope/article/unit/fecha compatibles;
- `incorporated + allocated <= pending` por pedido;
- plan solo IDs presentes/aplicables;
- plan por pedido <= remaining;
- si absorbed>0, suma global plan = absorbed;
- IDs de ledger aportados por plan, sin colisión;
- resulting ledger preserva previas una vez e inalteradas y añade exactamente plan.

Sin prioridad automática.

---

## 13. Pruebas obligatorias

Cubrir, además del contrato:

- precedencia de estados;
- UNKNOWN construible / KNOWN incompleto rechazado;
- schedule exacto con AUTHORIZED + CONFIRMED, extra/faltante/duplicado/NOT_APPLICABLE;
- `StockProjectionInput` siempre contiene schedule;
- supply identity duplicada y pending↔transit;
- composición exacta por point;
- STK-005 sin normalización no se interpreta como porcentaje;
- mínimo/depletion con incertidumbre;
- M08 NO_APLICABLE sin exigir ledger irrelevante;
- M08 EXCESS con ledger ausente → no verificable;
- reconciliación y preservación ledger;
- no defaults/no decisión/C0 inmutable.

---

## 14. Límites

Fuera: SQL/API/persistencia ledger, forecasting, ventas→demanda, tasa→calendario interna, cobertura proyectada, EOQ, fórmula M02/M03, Rules, CRC, acciones automáticas y cambios C0.

---

## 15. Estado

**Diseño v0.3 DEPURADO A1…A8 + B1…B4.**

Pendiente: **AUDIT 2 FINAL**. Código todavía bloqueado.
