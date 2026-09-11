# EIOS — STK Executable Implementation Design v0.1

**Estado:** DISEÑADO — PENDIENTE DE AUDITORÍA  
**Baseline:** `main @ c2945b56f41ac7cac3df15c2ce0d16950387e0b3`  
**Contrato cerrado:** `08_Implementacion/STK_Implementation_Contract.md` v0.17  
**Cierre contractual:** `08_Implementacion/STK_Implementation_Contract_Closure_v0.17.md`  
**Fecha:** 11/09/2026

---

## 1. Propósito

Diseñar la implementación ejecutable mínima de Stock & Demand Intelligence sin ampliar el contrato v0.17.

Esta fase traduce tipos, invariantes y cálculos autorizados a una arquitectura Python/Pydantic verificable. No redefine metodología, reglas, parámetros, decisiones ni defaults.

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

No se modifica `eios/core`. `eios.stock` puede importar `DecisionContext`; la dependencia inversa queda prohibida.

---

## 3. Estrategia de modelos

`models.py` materializará modelos Pydantic v2 con:

```python
ConfigDict(extra="forbid", str_strip_whitespace=True, frozen=True)
```

cuando el objeto represente un hecho/resultado inmutable.

Tipos controlados mediante `Literal` para estados, métodos, tipos de movimiento, ramas M07 y estados M08.

Todos los `Decimal` cuantitativos se validan como finitos. La negatividad solo se admite en saldos proyectados, nunca en cantidades físicas, umbrales, demanda o asignaciones.

---

## 4. Modelos mínimos

Se implementarán, como mínimo:

- `DataIssueRef`
- `StockScope`
- `DemandMethodSelection`
- `StockComputationContext`
- `StockResultIdentity`
- `NormalizedQuantity`
- `ConfiguredParameterValue`
- `AuthorizedQuantityThreshold`
- `AuthorizedStockPolicyQuantity`
- `CollectionEnvelope`
- `ProjectionHorizon`
- `StockCommitmentComponent`
- `IncorporatedDemandQuantity`
- `StockAvailabilityInput/Result`
- `ConsumptionPeriod`
- `RequiredPeriodSpec`
- `HistoricalDemandPolicy`
- `AuthorizedForecastRate`
- `DemandRateResult`
- `ProjectionMovement`
- `DemandProjectionSchedule`
- `ProjectionPoint`
- `ProjectedDecimalMetric`
- `ProjectedDateMetric`
- `StockProjectionInput/Result`
- `StockReferenceValue`
- `StockMaximumBasis`
- `ExcessToleranceBasis`
- `ExcessResult`
- `ConfirmedDemandRecord`
- `AllocationLedgerEntry/Snapshot`
- `DemandAllocation`
- `AllocationScope`
- `ConfirmedDemandAbsorptionResult`

No se crean clases de decisión final, Rules o CRC.

---

## 5. Funciones puras de engine

`engine.py` expondrá funciones puras y deterministas:

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

Ninguna función accede a reloj, red, base de datos o estado global.

---

## 6. Propagación de estado

Regla base:

- entradas estructuralmente inválidas → `ValidationError`/`ValueError`;
- ausencia/no evidencia/contradicción empresarial válida → resultado tipado no determinado;
- nunca se convierte ausencia en cero;
- `CONFLICTING_DATA` exige `DataIssueRef(CONTRADICTION)`;
- colecciones no `KNOWN` no se agregan silenciosamente.

Los resultados conservarán las incidencias/trazas de las dependencias que impidan el cálculo.

---

## 7. M01 / demanda histórica

`calculate_historical_demand` verificará:

- selección `HISTORICAL_CONSUMPTION` autorizada;
- `forecast_version is None`;
- política `KNOWN` con parámetro físico `STK-006`;
- colección `KNOWN`;
- correspondencia exacta de periodos requeridos;
- mismo scope/artículo/unidad/metodología;
- días evidenciados completos.

Cálculo:

```text
sum(consumption.quantity) / sum(consumption.evidenced_days)
```

No se rellenan periodos ni se usa catálogo como fallback.

---

## 8. M04 cobertura

Solo usa `StockAvailabilityResult` actual y `DemandRateResult` aplicable a `evaluation_date`.

- demanda > 0 → cobertura finita;
- demanda = 0 `KNOWN` → `UNBOUNDED`;
- dependencia no determinada → estado propagado.

No se implementa cobertura proyectada.

---

## 9. M05/M06 proyección

`build_projection_horizon` exige configuración efectiva `PYE-001` y construye:

```text
horizon_end = evaluation_date + horizon_days
```

La proyección:

- empieza en `stock_available`;
- acepta solo movimientos estrictamente posteriores a evaluación y dentro del horizonte;
- agrupa por día sin orden intradía;
- preserva saldo negativo;
- identifica incertidumbre desde la primera fecha aplicable;
- preserva composición de demanda confirmada por punto;
- evita doble uso de commitment/segment/supply identity.

Cuando exista demanda seleccionada que deba intervenir en M05, un resultado completo exige `DemandProjectionSchedule` `KNOWN`, externo/autorizado, que identifique exactamente los movimientos `AUTHORIZED_DEMAND` y su reconciliación. El engine no genera dichos movimientos desde una tasa.

---

## 10. M07 exceso

Ramas explícitas:

```text
StockMaximumBasis:
  DIRECT_QUANTITY | COVERAGE_MAXIMUM

ExcessToleranceBasis:
  QUANTITY | RATE
```

La implementación validará exclusividad de ramas y vigencia para `stock_reference.reference_date`.

Cálculos autorizados:

```text
stock_maximum = coverage_days * daily_demand  # rama cobertura
excess_tolerance_quantity = stock_maximum * normalized_rate
excess_threshold = stock_maximum + excess_tolerance_quantity
excess_quantity = max(0, stock_reference - excess_threshold)
```

No se aceptan 90 días/10 % como defaults.

---

## 11. M08 absorción

La implementación:

- requiere exceso determinado;
- diferencia `NO_EXISTE / NO_APLICABLE / APLICABLE_Y_VALIDADA / NO_VERIFICABLE`;
- descuenta cantidad ya incorporada en opening/M05;
- descuenta ledger activo previo;
- rechaza sobreconsumo de pending;
- no elige prioridad entre pedidos;
- exige plan cuando absorción > 0;
- verifica `sum(plan) == absorbed_excess`;
- preserva todas las entries activas previas y añade exactamente las del plan;
- no genera IDs aleatorios.

---

## 12. Pruebas mínimas de implementación

La primera batería cubrirá como mínimo:

1. identidad C0 + scope;
2. ausencia ≠ cero y conflicto con evidencia;
3. disponibilidad y déficit;
4. committed composition y duplicados;
5. histórico completo/incompleto y cero evidenciado;
6. forecast compatible/incompatible;
7. cobertura finita/unbounded/unknown;
8. `PYE-001` y rechazo de bool/default;
9. movimientos fuera de horizonte/mismo día;
10. supply identity pending↔transit;
11. reconciliación opening↔M05;
12. schedule demanda obligatorio cuando aplica;
13. proyección diaria, saldo negativo, depletion/minimum;
14. M07 ramas, vigencia, exceso y tolerancia;
15. M08 ledger ausente vs vacío, plan, colisiones, sobreconsumo y determinismo;
16. no modificación C0;
17. no decisión automática/no defaults.

---

## 13. Límites explícitos

No implementar en v0.1:

- SQL STK;
- API STK;
- persistencia ledger;
- forecasting interno;
- ventas→demanda;
- calendarización interna de tasa;
- cobertura proyectada;
- EOQ;
- fórmula M02/M03;
- reglas `R-STK-*`;
- CRC;
- acciones de compra;
- cambios C0.

---

## 14. Criterio para pasar a materialización

Solo podrá escribirse `eios/stock` cuando este diseño complete:

`AUDITAR → DEPURAR → AUDITAR 2 → CERRAR`.

**Estado actual:** DISEÑADO — NO MATERIALIZAR CÓDIGO TODAVÍA.
