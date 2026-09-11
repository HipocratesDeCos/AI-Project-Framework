# EIOS — STK Executable Implementation Design v0.2

**Estado:** DEPURADO A1…A8 — PENDIENTE DE AUDIT 2  
**Baseline:** `main @ c2945b56f41ac7cac3df15c2ce0d16950387e0b3`  
**Contrato cerrado:** `08_Implementacion/STK_Implementation_Contract.md` v0.17  
**Cierre contractual:** `08_Implementacion/STK_Implementation_Contract_Closure_v0.17.md`  
**Fecha:** 11/09/2026

---

## 1. Propósito

Diseñar la implementación ejecutable mínima de Stock & Demand Intelligence sin ampliar el contrato v0.17.

Esta fase traduce tipos, invariantes y cálculos autorizados a Python/Pydantic. No redefine metodología, reglas, parámetros, decisiones ni defaults.

---

## 2. Paquete físico

```text
eios/stock/
├── __init__.py
├── models.py
└── engine.py

tests/
└── test_stock_engine.py
```

No se modifica `eios/core`. `eios.stock` puede importar `DecisionContext`; la dependencia inversa está prohibida.

---

## 3. Estrategia Pydantic y frontera error/incertidumbre

Los hechos/resultados se implementan con Pydantic v2, `extra="forbid"`, `str_strip_whitespace=True` y `frozen=True` cuando proceda.

Tipos controlados mediante `Literal`. Todos los `Decimal` cuantitativos se validan como finitos.

**Separación obligatoria:**

- forma/identidad/tipo dimensional/invariante imposible → `ValidationError` o `ValueError`;
- ausencia, no evidencia o contradicción empresarial representable → objeto válido con estado no determinado;
- el engine **no captura** un error estructural para convertirlo en `UNKNOWN`.

Cada familia con `state` implementa `state ↔ payload`:

- `KNOWN` exige payload material completo;
- estado no determinado permite nulos donde precisamente falta evidencia;
- un valor cuantitativo determinado no se publica bajo un estado no determinado;
- `CONFLICTING_DATA` exige incidencia de contradicción.

La negatividad solo se admite en `projected_stock`, nunca en cantidades físicas, demanda, umbrales o asignaciones.

---

## 4. Modelos mínimos

Se materializan los modelos del contrato v0.17, incluyendo:

`DataIssueRef`, `StockScope`, `DemandMethodSelection`, `StockComputationContext`, `StockResultIdentity`, `NormalizedQuantity`, `ConfiguredParameterValue`, `AuthorizedQuantityThreshold`, `AuthorizedStockPolicyQuantity`, `CollectionEnvelope`, `ProjectionHorizon`, `StockCommitmentComponent`, `IncorporatedDemandQuantity`, `StockAvailabilityInput/Result`, `ConsumptionPeriod`, `RequiredPeriodSpec`, `HistoricalDemandPolicy`, `AuthorizedForecastRate`, `DemandRateResult`, `ProjectionMovement`, `DemandProjectionSchedule`, `ProjectionPoint`, `ProjectedDecimalMetric`, `ProjectedDateMetric`, `StockProjectionInput/Result`, `StockReferenceValue`, `StockMaximumBasis`, `ExcessToleranceBasis`, `ExcessResult`, `ConfirmedDemandRecord`, `AllocationLedgerEntry/Snapshot`, `DemandAllocation`, `AllocationScope`, `ConfirmedDemandAbsorptionResult`.

No se crean clases de decisión final, Rules o CRC.

---

## 5. Funciones puras

`engine.py` expondrá funciones puras:

```text
build_identity(context)
calculate_stock_availability(payload)
build_projection_horizon(context, parameter)
calculate_historical_demand(context, policy, periods)
use_authorized_forecast(context, forecast)
calculate_coverage(availability, demand)
calculate_stock_projection(payload, demand_schedule=None)
build_current_stock_reference(availability)
build_projected_stock_reference(projection, reference_date)
calculate_excess(stock_reference, maximum_basis, tolerance_basis)
calculate_confirmed_demand_absorption(excess, orders, ledger, allocation_scope, allocation_plan)
```

Más helpers privados deterministas para propagación de estado, deduplicación de incidencias/trazas, composición confirmada, validación logística y reconciliación M08.

Sin reloj, red, DB, UUID aleatorio ni estado global.

---

## 6. Propagación determinista A1

Helper privado conceptual:

```text
propagate_state(required_dependencies)
```

Para dependencias materiales obligatorias:

1. si alguna es `CONFLICTING_DATA` → resultado `CONFLICTING_DATA`;
2. en otro caso, si alguna es `NOT_EVIDENCED` → `NOT_EVIDENCED`;
3. en otro caso, si alguna es `UNKNOWN` → `UNKNOWN`;
4. `NOT_APPLICABLE` solo excluye el elemento cuya no aplicabilidad está demostrada; no cancela incertidumbre de otra dependencia obligatoria.

Esta precedencia es técnica para preservar información de M09/M10, no prioridad empresarial.

`issue_refs` y `trace_refs` se fusionan sin duplicados, preservando orden de primera aparición.

---

## 7. M01 / demanda histórica

`calculate_historical_demand` exige selección `KNOWN/HISTORICAL_CONSUMPTION`, `forecast_version is None`, política `KNOWN`, parámetro físico `STK-006`, colección `KNOWN`, correspondencia uno-a-uno de periodos, scope/artículo/unidad/metodología comunes y días completos.

```text
historical_daily_demand = sum(quantity) / sum(evidenced_days)
```

No rellena periodos ni usa defaults.

---

## 8. Forecast y M04

`use_authorized_forecast` exige selección `KNOWN/AUTHORIZED_FORECAST`, versión exacta, intervalo cerrado aplicable y trazabilidad.

`calculate_coverage` solo usa disponibilidad actual y demanda aplicable en `evaluation_date`:

- demanda >0 → `FINITE`;
- demanda 0 `KNOWN` → `UNBOUNDED`;
- dependencia no determinada → estado correspondiente.

No cobertura proyectada.

---

## 9. M05 — horizon y schedule A3

`build_projection_horizon` consume configuración efectiva `PYE-001`, entero positivo no booleano, normalizado a días:

```text
horizon_end = evaluation_date + horizon_days
```

Para `calculate_stock_projection`:

- si existen movimientos `AUTHORIZED_DEMAND`, `DemandProjectionSchedule` `KNOWN` es obligatorio;
- `schedule.demand_movement_ids` coincide **exactamente** con IDs de movimientos `AUTHORIZED_DEMAND` que participan;
- schedule y demanda comparten selección/contexto/horizonte;
- `transformation_ref` y `reconciliation_ref` deben estar presentes;
- una tasa nunca genera movimientos automáticamente;
- `CONFIRMED_DEMAND`, `RESERVATION` y `OTHER_AUTHORIZED_NEED` no pueden utilizarse para satisfacer el conjunto de IDs del schedule;
- si la política de evaluación declara demanda seleccionada como parte de la proyección pero no existe schedule autorizado, el resultado completo no es `KNOWN`.

---

## 10. M05/M06 — movimientos y exclusividad logística A4

Movimiento contribuyente: estrictamente futuro, dentro del horizonte, cantidad/identidad/normalización/traza válidas.

El engine crea índices de unicidad:

- `movement_id` global único;
- `demand_segment_id` confirmado único;
- `commitment_id` de opening no se reutiliza como salida nueva;
- para M06, `supply_identity`/parcialidad logística identifica la cantidad real, no el `movement_id`.

Se rechaza como error estructural:

- misma identidad logística contribuyente dos veces;
- misma parcialidad como `PENDING_ORDER` e `IN_TRANSIT`;
- duplicación de una parcialidad bajo dos movement IDs.

Si no existe identidad suficiente para demostrar independencia, no se suma silenciosamente.

---

## 11. Proyección diaria y composición A5/A8

Opening = `stock_available`.

Por día:

```text
closing = previous_closing + sum(inflows) - sum(outflows)
```

Sin orden intradía; saldo negativo preservado.

**Composición confirmada exacta:**

1. opening se deriva de componentes committed comerciales;
2. cada movimiento `CONFIRMED_DEMAND` contabilizado añade exactamente su `quantity` al pedido y su `demand_segment_id`;
3. mismo segmento no puede repetirse;
4. orden de colección determinista por primera aparición en opening y después por orden estable de fecha + movement_id;
5. cada `ProjectionPoint` conserva solo composición hasta su fecha;
6. `StockReferenceValue` y `ExcessResult` copian la composición exacta; no recalculan.

**Métricas bajo incertidumbre:**

- `minimum_projected_stock` es `KNOWN` solo si todo el horizonte requerido está determinado;
- no se publica mínimo parcial como mínimo final;
- `depletion_date` solo `KNOWN` si ninguna incertidumbre anterior puede adelantarla;
- opening cero `KNOWN` → `evaluation_date`;
- horizonte entero `KNOWN` sin agotamiento → `NOT_APPLICABLE`;
- incertidumbre previa → métrica no determinada.

---

## 12. M07 — normalización cerrada A6

Ramas exclusivas:

```text
StockMaximumBasis: DIRECT_QUANTITY | COVERAGE_MAXIMUM
ExcessToleranceBasis: QUANTITY | RATE
```

`STK-004` solo se consume cuando llega ya normalizado a días mediante configuración efectiva/trazable. El engine no interpreta unidades libres por nombre.

`STK-005` como RATE solo se consume cuando la entrada ya demuestra una **proporción adimensional normalizada** mediante unidad/`normalization_ref`. El engine **no divide entre 100** por heurística.

Cálculos:

```text
stock_maximum = coverage_maximum_days * daily_demand
excess_tolerance_quantity = stock_maximum * normalized_rate
excess_threshold = stock_maximum + excess_tolerance_quantity
excess_quantity = max(0, stock_reference - excess_threshold)
```

Sin defaults 90/10.

---

## 13. M08 — reconciliación por pedido A7

Antes de agregar, se construye por `confirmed_demand_id`:

```text
pending
incorporated_before_M08
already_allocated
remaining_allocatable = pending - incorporated - allocated
```

Invariantes:

- IDs de pedidos de entrada únicos;
- mismo scope/article/unit/date aplicable;
- ledger `KNOWN` compatible;
- `incorporated + allocated <= pending` por pedido;
- ledger no conocido impide absorción determinada;
- plan solo contiene IDs aplicables presentes;
- suma del plan por pedido <= remaining individual;
- si absorción >0, suma global plan = absorción;
- IDs de nuevas entries aportados por el plan y sin colisión;
- `resulting_ledger` preserva cada entry activa previa una vez e inalterada y añade exactamente una por allocation.

No existe prioridad implícita.

---

## 14. Pruebas obligatorias

Además de la matriz contractual, incluir explícitamente:

- precedencia `CONFLICTING > NOT_EVIDENCED > UNKNOWN`;
- modelos UNKNOWN construibles sin datos ficticios y KNOWN incompleto rechazado;
- schedule exacto: faltante, extra, duplicado e incompatible;
- supply identity duplicada y pending↔transit;
- composición exacta por punto y orden determinista;
- `STK-005=10` sin normalización rechazada/no consumida como 10 %;
- M08 reconciliación por pedido y preservación exacta de ledger;
- mínimo/depletion frente a incertidumbre anterior/posterior.

---

## 15. Límites

Fuera: SQL/API/persistencia ledger, forecasting, ventas→demanda, tasa→calendario interna, cobertura proyectada, EOQ, fórmula M02/M03, Rules, CRC, acciones automáticas, cambios C0.

---

## 16. Estado

**Diseño v0.2 DEPURADO A1…A8.**

No materializar código hasta superar **AUDITAR 2 → CERRAR**.
