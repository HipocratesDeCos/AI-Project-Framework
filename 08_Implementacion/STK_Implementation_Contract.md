# EIOS — Stock & Demand Implementation Contract

## 1. Identidad

**Documento:** STK Implementation Contract  
**Versión:** 0.6  
**Estado:** DEPURADO TEMPORAL FINAL — PENDIENTE DE AUDIT 2 FINAL  
**Baseline de origen:** `main @ c2bd5b9b73974426d29cc234ffda42d494e720fb`  
**Dominio:** Capa 3 — Stock / Demanda  
**Autoridad metodológica:** `01_Modelo/Stock_Demand_Methodological_Matrix.md` v1.1  
**Autoridad de entrada:** `01_Modelo/STK_Contract_Entry_Authority.md` v1.0  
**Autoridad de reglas:** `04_Reglas/Matriz_Reglas_MVP.md` v2.1  
**Dependencias:** `04_Reglas/Rule_Dependency_Matrix.md` v1.4  
**Auditorías:** `STK_Implementation_Contract_Audit_v0.1.md`, `STK_Implementation_Contract_Audit_2_v0.1.md`, `STK_Implementation_Contract_Audit_2_Final_v0.2.md`, `STK_Implementation_Contract_Audit_2_Final_v0.3.md`, `STK_Implementation_Contract_Audit_2_Final_v0.4.md`

---

## 2. Propósito y frontera

Este contrato define la frontera física mínima implementable de **Stock & Demand Intelligence (STK) v0.1**.

STK materializa únicamente semántica, relaciones y cálculos previamente autorizados. No crea reglas empresariales, parámetros, defaults normativos, forecasting implícito, autoridad paralela de evidencia ni decisiones automáticas.

STK produce resultados analíticos y evidencia operativa. El Motor de Reglas conserva R-STK-001…004, CRC conserva la resolución de conflictos, MED conserva la integración y la autoridad decisional final permanece en la persona autorizada.

La implementación ejecutable permanece bloqueada hasta superar `AUDIT 2 FINAL → CERRAR`.

---

## 3. Frontera C0 y paquete físico

STK reutiliza `DecisionContext` y no modifica `PurchaseOperation`, `Evidence`, `EvidenceValidation`, `Rule`, `Assessment` ni `Trace`.

`PurchaseOperation.quantity` no se convierte automáticamente en cantidad STK normalizada porque C0 no contiene la unidad base objetivo.

Paquete físico previsto:

```text
eios/stock/
├── __init__.py
├── models.py
└── engine.py
```

STK no puede introducir dependencias circulares con `eios.core`.

---

## 4. Identidad temporal y de resultado

La fecha canónica STK es `evaluation_date`; las referencias metodológicas previas a `as_of_date` se materializan con esa misma identidad.

La proyección v0.1 opera a granularidad **diaria**. No existe autoridad para inferir una secuencia intradía.

Todo resultado intermedio reutilizable conserva una identidad equivalente a:

```text
StockResultIdentity
├── decision_id: str
├── scenario_id: str
├── data_snapshot_id: str
├── parameters_version: str
├── article_id: str
├── evaluation_date: date
├── base_unit: str
└── methodology_version: str
```

Esta identidad se deriva del `DecisionContext` y del contexto STK; no constituye una nueva identidad empresarial. Un consumidor posterior debe exigir igualdad exacta de identidad salvo que este contrato indique expresamente otra relación temporal.

---

## 5. Estados STK

```text
KNOWN
UNKNOWN
NOT_EVIDENCED
NOT_APPLICABLE
CONFLICTING_DATA
```

- `KNOWN`: valor utilizable y suficientemente evidenciado;
- `UNKNOWN`: valor no determinable;
- `NOT_EVIDENCED`: valor declarado sin soporte suficiente;
- `NOT_APPLICABLE`: evidencia de que la magnitud no aplica;
- `CONFLICTING_DATA`: fuentes materialmente incompatibles no resueltas.

Estos estados son especializados y no redefinen C0.

Invariantes:

1. `state != KNOWN` no presenta un valor numérico como determinado.
2. `UNKNOWN / NOT_EVIDENCED / CONFLICTING_DATA ≠ 0`.
3. Todo dato `KNOWN` exige `source_ref` o al menos un `trace_ref`.

---

## 6. Colecciones empresariales

```text
CollectionEnvelope[T]
├── state: KNOWN | UNKNOWN | NOT_EVIDENCED | CONFLICTING_DATA
├── items: tuple[T, ...]
├── source_ref: str | null
└── trace_refs: tuple[str, ...]
```

Reglas:

1. una colección `KNOWN` exige fuente o traza incluso cuando está vacía;
2. solo `KNOWN + items=()` significa conjunto vacío evidenciado;
3. una colección vacía `UNKNOWN/NOT_EVIDENCED` no significa inexistencia;
4. `CONFLICTING_DATA` impide tratar la colección como completa.

---

## 7. Magnitud física normalizada

```text
NormalizedQuantity
├── article_id: str
├── value: Decimal | null
├── unit: str
├── state: StockDataState
├── source_ref: str | null
├── effective_date: date | null
└── trace_refs: tuple[str, ...]
```

`NormalizedQuantity` representa una **magnitud física**, no un saldo analítico proyectado.

Reglas:

- valor Decimal finito;
- cantidad física `KNOWN` no negativa;
- operaciones entre cantidades exigen mismo artículo y unidad;
- `state != KNOWN` implica `value = null`;
- `KNOWN` exige trazabilidad;
- no existe conversión de unidad implícita.

---

## 8. Contexto STK

```text
StockComputationContext
├── decision_context: DecisionContext
├── article_id: str
├── evaluation_date: date
├── base_unit: str
├── methodology_version: str
└── forecast_version: str | null
```

`parameters_version` y `data_snapshot_id` se reutilizan desde `DecisionContext`. El contexto genera la `StockResultIdentity` utilizada por resultados y consumidores.

---

## 9. Parámetros configurados

```text
ConfiguredParameterValue
├── parameter_id: str
├── value: Decimal | int | bool | null
├── unit: str
├── state: StockDataState
├── parameters_version: str
├── source_ref: str
├── normalization_ref: str | null
└── trace_refs: tuple[str, ...]
```

Un parámetro `KNOWN` solo puede consumirse si:

```text
ConfiguredParameterValue.parameters_version
== DecisionContext.parameters_version
```

Cada operación valida `parameter_id`, tipo, dimensión/unidad y, cuando proceda, la normalización autorizada. No existe fallback a valores iniciales del catálogo.

---

## 10. Disponibilidad de stock

```text
StockAvailabilityInput
├── context: StockComputationContext
├── stock_on_hand: NormalizedQuantity
└── stock_committed: NormalizedQuantity
```

Para producir disponibilidad `KNOWN` se exige:

- ambas magnitudes `KNOWN`;
- mismo artículo que `context.article_id`;
- misma unidad que `context.base_unit`;
- `stock_on_hand.effective_date == context.evaluation_date`;
- `stock_committed.effective_date == context.evaluation_date`;
- trazabilidad suficiente de ambas magnitudes.

STK v0.1 no inventa una tolerancia de antigüedad para snapshots de stock. Un dato de otra fecha no se considera vigente por inferencia.

Cálculo:

```text
stock_available = max(0, stock_on_hand - stock_committed)
availability_deficit = max(0, stock_committed - stock_on_hand)
```

Salida:

```text
StockAvailabilityResult
├── identity: StockResultIdentity
├── stock_on_hand
├── stock_committed
├── stock_available: Decimal | null
├── availability_deficit: Decimal | null
├── state: StockDataState
└── trace_refs
```

El déficit permanece visible aunque `stock_available` tenga suelo cero. Un consumidor exige identidad compatible.

---

## 11. Consumo M01

```text
ConsumptionPeriod
├── article_id: str
├── period_id: str
├── period_start: date
├── period_end: date
├── evidenced_days: int
├── quantity: Decimal | null
├── unit: str
├── state: StockDataState
├── source_ref: str
└── trace_refs: tuple[str, ...]
```

Un periodo `KNOWN` exige consumo real, periodo trazable, `period_start <= period_end`, cantidad no negativa y `evidenced_days` coherente con el periodo completo exigido por la política. Ventas y forecast no son consumo real. Cero solo existe cuando está explícitamente evidenciado.

---

## 12. Política histórica de demanda

```text
RequiredPeriodSpec
├── period_id: str
├── period_start: date
└── period_end: date
```

```text
HistoricalDemandPolicy
├── parameter: ConfiguredParameterValue
├── required_periods: tuple[RequiredPeriodSpec, ...]
├── period_calendar_ref: str
├── extended_applicable_to: date | null
├── applicability_source_ref: str | null
├── source_ref: str
└── trace_refs: tuple[str, ...]
```

Reglas:

1. `parameter.parameter_id == P-STK-006`;
2. parámetro `KNOWN` y versión coincidente;
3. su valor normalizado es un entero positivo, no booleano;
4. la unidad está autorizada/normalizada como **meses o número de periodos mensuales**; si requiere conversión, `normalization_ref` es obligatorio;
5. STK no infiere la unidad por el ID;
6. `len(required_periods)` coincide con el valor normalizado;
7. `period_id` es único;
8. cada especificación cumple `period_start <= period_end`;
9. las especificaciones no se solapan;
10. `period_calendar_ref` identifica la fuente que determina los periodos concretos aplicables;
11. STK no presupone meses naturales ni genera IDs por sí mismo;
12. si `extended_applicable_to` está presente, debe ser `>= evaluation_date` y `applicability_source_ref` es obligatorio;
13. si no existe extensión de aplicabilidad autorizada, STK no presume que la tasa histórica sea válida para fechas futuras.

---

## 13. Demanda histórica

```text
HistoricalDemandInput
├── context: StockComputationContext
├── policy: HistoricalDemandPolicy
└── periods: CollectionEnvelope[ConsumptionPeriod]
```

Resultado numérico `KNOWN` solo si:

- colección `KNOWN` y trazable;
- `ConsumptionPeriod.period_id` único;
- correspondencia uno-a-uno con `required_periods`;
- para cada ID coinciden `period_start` y `period_end`;
- todos los periodos son `KNOWN`;
- no hay solapamientos;
- artículo/unidad son homogéneos y compatibles;
- para cada periodo completo `evidenced_days == (period_end - period_start).days + 1`;
- no existen contradicciones no resueltas.

Cálculo:

```text
total_evidenced_consumption = sum(period.quantity)
evidenced_days_in_window = sum(period.evidenced_days)
historical_daily_demand = total_evidenced_consumption / evidenced_days_in_window
```

No se sustituye, duplica ni acorta la ventana.

La aplicabilidad temporal del resultado se materializa de forma conservadora:

```text
applicable_from = context.evaluation_date
applicable_to = policy.extended_applicable_to or context.evaluation_date
```

`applicable_to > evaluation_date` solo es válido cuando existe `applicability_source_ref` trazable. La igualdad `applicable_from == applicable_to == evaluation_date` no afirma forecasting ni vigencia futura; limita técnicamente el resultado histórico al instante de evaluación cuando no existe autoridad para extenderlo.

Salida común:

```text
DemandRateResult
├── identity: StockResultIdentity
├── method: HISTORICAL_CONSUMPTION | AUTHORIZED_FORECAST
├── daily_demand: Decimal | null
├── unit: str
├── state: StockDataState
├── reference_date: date
├── applicable_from: date
├── applicable_to: date
├── applicability_source_ref: str
├── window_or_horizon
├── source_ref
├── forecast_version: str | null
└── trace_refs
```

Para demanda histórica sin extensión futura, `applicability_source_ref` identifica la propia política/ventana y la fecha de evaluación. Para una extensión futura debe identificar además la autoridad que permite esa vigencia.

---

## 14. Forecast autorizado

```text
AuthorizedDemandForecast
├── article_id: str
├── daily_demand: Decimal | null
├── unit: str
├── horizon_start: date
├── horizon_end: date
├── state: StockDataState
├── forecast_version: str
├── source_ref: str
└── trace_refs: tuple[str, ...]
```

Para consumir un forecast `KNOWN`:

1. versión no vacía;
2. `context.forecast_version == forecast.forecast_version`;
3. `horizon_start <= evaluation_date <= horizon_end`;
4. artículo/unidad compatibles;
5. tasa no negativa y finita;
6. trazabilidad suficiente.

La salida `DemandRateResult` de forecast conserva:

```text
reference_date = context.evaluation_date
applicable_from = forecast.horizon_start
applicable_to = forecast.horizon_end
applicability_source_ref = forecast.source_ref
```

STK no calcula forecast y no realiza fallback automático forecast↔histórico. Ventas históricas no constituyen método de demanda STK v0.1.

---

## 15. Cobertura M04

Para cobertura en la fecha de evaluación se exige además:

```text
demand_rate.applicable_from
<= context.evaluation_date
<= demand_rate.applicable_to
```

Si stock disponible y demanda diaria son `KNOWN`, sus identidades son compatibles, la tasa es aplicable y `daily_demand > 0`:

```text
coverage_days = stock_available / daily_demand
status = DETERMINED
```

Si `daily_demand == 0` está confirmada, evidenciada y temporalmente aplicable:

```text
coverage_days = null
status = UNBOUNDED
reason = CONFIRMED_ZERO_DEMAND
```

No se representa infinito numérico. Estados: `DETERMINED | UNBOUNDED | UNKNOWN | NOT_EVIDENCED | CONFLICTING_DATA`. La salida conserva `StockResultIdentity`.

---

## 16. Movimientos proyectivos M05/M06

```text
ProjectionMovement
├── movement_id: str
├── supply_identity: str | null
├── scenario_id: str | null
├── article_id: str
├── direction: INFLOW | OUTFLOW
├── quantity: Decimal | null
├── unit: str
├── effective_date: date | null
├── state: StockDataState
├── source_kind: PENDING_ORDER | IN_TRANSIT | AUTHORIZED_DEMAND | RESERVATION | OTHER_AUTHORIZED_NEED | PROPOSED_PURCHASE
├── source_ref: str
└── trace_refs: tuple[str, ...]
```

Dirección obligatoria:

```text
PENDING_ORDER | IN_TRANSIT | PROPOSED_PURCHASE → INFLOW
AUTHORIZED_DEMAND | RESERVATION | OTHER_AUTHORIZED_NEED → OUTFLOW
```

Invariantes:

- `movement_id` único dentro de una proyección;
- todo movimiento `KNOWN` que contribuya exige cantidad no negativa y finita, artículo/unidad compatibles, traza y `effective_date` no nula;
- todo movimiento `KNOWN` contribuyente debe cumplir `evaluation_date <= effective_date <= horizon_end`;
- un movimiento conocido fuera del horizonte no se desplaza ni se suma silenciosamente;
- un movimiento `NOT_APPLICABLE` suficientemente evidenciado aporta **cero contribución por no aplicabilidad**, permanece en trazabilidad y **no contamina** la determinabilidad;
- `UNKNOWN`, `NOT_EVIDENCED` y `CONFLICTING_DATA` no se sustituyen por cero y propagan incertidumbre según su fecha;
- una tasa de demanda no genera movimientos implícitos.

### M06

Para `PENDING_ORDER`/`IN_TRANSIT`:

- `supply_identity` obligatorio;
- cada identidad activa aparece una sola vez;
- una parcialidad distinta exige identidad de segmento distinta y trazable;
- una identidad no coexiste como pendiente y tránsito;
- una entrada futura `KNOWN` queda sometida al mismo intervalo temporal global de la proyección;
- fecha vencida no se desplaza automáticamente;
- recepción confirmada deja M06;
- historial aporta trazabilidad, no cantidades adicionales.

### Cantidad propuesta

Para `PROPOSED_PURCHASE`:

- `scenario_id` obligatorio y coincidente con `DecisionContext.scenario_id`;
- cantidad normalizada;
- fecha explícita dentro del horizonte;
- traza.

STK no presume aprobación ni recepción.

---

## 17. Colección de movimientos

`StockProjectionInput.movements` es `CollectionEnvelope[ProjectionMovement]`.

Solo una colección `KNOWN`, trazable y sin IDs duplicados puede afirmar que el conjunto recibido del horizonte está completo. Colección no determinada hace no determinada la proyección global según M09/M10.

---

## 18. Proyección M05

```text
StockProjectionInput
├── context: StockComputationContext
├── opening_availability: StockAvailabilityResult
├── movements: CollectionEnvelope[ProjectionMovement]
├── horizon_end: date
├── horizon_source_ref: str
├── horizon_trace_refs: tuple[str, ...]
└── scenario_id: str
```

Precondiciones:

- `scenario_id == DecisionContext.scenario_id`;
- `horizon_end >= evaluation_date`;
- el horizonte tiene referencia trazable; no se usa `P-PYE-001` como default;
- `opening_availability.identity` coincide con el contexto;
- opening `KNOWN` para proyección determinada;
- todos los movimientos `KNOWN` contribuyentes están fechados dentro de `[evaluation_date, horizon_end]`.

### 18.1 Cálculo diario

No existe orden intradía por ID. Para cada fecha:

```text
total_inflows_date = sum(known applicable inflows)
total_outflows_date = sum(known applicable outflows)
closing_stock_date = opening_stock_date + total_inflows_date - total_outflows_date
```

Movimientos del mismo día se agregan antes del cierre. El stock negativo se conserva como saldo analítico de déficit.

### 18.2 Incertidumbre

Cada `ProjectionPoint` conserva identidad, fecha, stock proyectado, estado, entradas/salidas y trazas.

- movimiento requerido `UNKNOWN/NOT_EVIDENCED/CONFLICTING_DATA` con fecha conocida → incertidumbre desde esa fecha;
- el mismo tipo de movimiento sin fecha → incertidumbre desde `evaluation_date`;
- `NOT_APPLICABLE` evidenciado no contamina;
- un movimiento conocido posterior no restaura por sí solo `KNOWN`.

### 18.3 Mínimo y agotamiento

```text
minimum_projected_stock = min(opening_stock, determined daily closings)
```

Si `opening_stock_available == 0` y es `KNOWN`, `depletion_date = evaluation_date`. En otro caso, es la primera fecha de cierre diario determinado con stock `<= 0`. No se afirma instante intradía.

La salida conserva `StockResultIdentity`, `scenario_id`, horizonte y trazas.

---

## 19. Frontera R-STK-001

STK entrega evidencia como `minimum_projected_stock`, `depletion_date`, recepciones relevantes y estados. No emite `COMPRAR`, `COMPRAR CONDICIONADO`, `NEGOCIAR` o `NO COMPRAR`.

`P-PYE-006 = 15 días` no se usa como condición oculta ni default.

---

## 20. Referencia de stock para M07

Para no confundir stock físico con saldo proyectado:

```text
StockReferenceValue
├── identity: StockResultIdentity
├── reference_kind: CURRENT_AVAILABLE | PROJECTED
├── reference_date: date
├── value: Decimal | null
├── unit: str
├── state: StockDataState
├── source_ref: str
└── trace_refs: tuple[str, ...]
```

Reglas:

- `CURRENT_AVAILABLE` procede de disponibilidad actual y, si es `KNOWN`, `value >= 0` y `reference_date == evaluation_date`;
- `PROJECTED` procede de un `ProjectionPoint` compatible y puede ser negativo;
- el valor proyectado negativo representa déficit analítico, no cantidad física negativa;
- identidad, unidad, fecha y procedencia deben conservarse;
- `state != KNOWN` implica `value = null`.

---

## 21. Base de stock máximo M07

```text
StockMaximumBasis
├── kind: DIRECT_QUANTITY | COVERAGE_MAXIMUM
├── direct_quantity: NormalizedQuantity | null
├── coverage_maximum: ConfiguredParameterValue | null
├── demand_rate: DemandRateResult | null
├── state: StockDataState
├── source_ref: str
└── trace_refs: tuple[str, ...]
```

Ramas mutuamente excluyentes:

- `DIRECT_QUANTITY` → `direct_quantity` presente; resto de rama alternativa nulo;
- `COVERAGE_MAXIMUM` → `direct_quantity = null`; `coverage_maximum` y `demand_rate` presentes.

`state` debe ser compatible con la rama activa.

Para `COVERAGE_MAXIMUM`:

- `coverage_maximum.parameter_id == P-STK-004`;
- valor `KNOWN`, versión coincidente y unidad temporal normalizada en días;
- demanda `KNOWN`, identidad compatible y `daily_demand > 0`;
- la fecha de referencia del stock debe pertenecer al intervalo de aplicabilidad de la demanda:

```text
demand_rate.applicable_from
<= stock_reference.reference_date
<= demand_rate.applicable_to
```

Solo entonces:

```text
stock_maximum = coverage_maximum_days * authorized_daily_demand
```

Con demanda cero confirmada no se deriva máximo cero. Una tasa histórica cuya vigencia futura no esté demostrada no puede usarse para construir un máximo sobre una referencia futura.

---

## 22. Tolerancia de exceso M07

```text
NormalizedRate
├── parameter_id: str
├── normalized_rate: Decimal | null
├── original_unit: str
├── state: StockDataState
├── parameters_version: str
├── normalization_ref: str
├── source_ref: str
└── trace_refs: tuple[str, ...]
```

```text
ExcessToleranceBasis
├── kind: QUANTITY | RATE
├── quantity: NormalizedQuantity | null
├── rate: NormalizedRate | null
├── state: StockDataState
└── trace_refs: tuple[str, ...]
```

Ramas mutuamente excluyentes:

- `QUANTITY` → `quantity` presente, `rate = null`;
- `RATE` → `quantity = null`, `rate` presente.

Para `RATE`: `parameter_id == P-STK-005`, versión coincidente, tasa normalizada no negativa y `normalization_ref` obligatorio. No se infiere el significado de `10` o `0.10`.

```text
excess_tolerance_quantity = stock_maximum * normalized_rate
```

---

## 23. Exceso M07

```text
ExcessInput
├── context: StockComputationContext
├── stock_reference: StockReferenceValue
├── maximum_basis: StockMaximumBasis
└── tolerance_basis: ExcessToleranceBasis
```

Con entradas determinadas y compatibles:

```text
excess_threshold = stock_maximum + excess_tolerance_quantity
excess_quantity = max(0, stock_reference.value - excess_threshold)
```

Estados: `NO_EXCESS | WITHIN_TOLERANCE | EXCESS | UNKNOWN | NOT_EVIDENCED | CONFLICTING_DATA`.

Un `PROJECTED` negativo puede producir legítimamente `NO_EXCESS` porque el cero de exceso es resultado del cálculo con una referencia conocida; no convierte el déficit proyectado en cero.

Si la referencia procede de M05, M07 no vuelve a sumar M06 ni propuesta.

Relaciones parámetro↔regla confirmadas únicamente:

- `P-STK-004 → R-STK-002`;
- `P-STK-004 → R-STK-003` derivada;
- `P-STK-005 → R-STK-003` derivada.

```text
ExcessResult
├── identity: StockResultIdentity
├── reference_date: date
├── stock_reference
├── stock_maximum
├── tolerance_quantity
├── excess_threshold
├── excess_quantity
├── state
└── trace_refs
```

STK calcula; el Motor de Reglas evalúa R-STK-002/003.

---

## 24. M08 — demanda confirmada

```text
confirmed_demand: CollectionEnvelope[ConfirmedDemandRecord]
```

Solo `KNOWN + items=()` y colección trazable permite `NO_EXISTE`.

```text
ConfirmedDemandRecord
├── confirmed_demand_id: str
├── order_id: str
├── customer_id: str
├── article_id: str
├── pending_quantity: NormalizedQuantity
├── order_date: date
├── confirmation_date: date
├── expected_delivery_date: date | null
├── business_status: str
├── applicability_state: NO_APLICABLE | APLICABLE_Y_VALIDADA | NO_VERIFICABLE
├── applicability_source_ref: str
├── source_ref: str
└── trace_refs: tuple[str, ...]
```

Reglas:

1. cantidad pendiente conserva estado, artículo, unidad y evidencia;
2. solo `pending_quantity.state == KNOWN` puede absorber;
3. `APLICABLE_Y_VALIDADA` exige fecha prevista no nula, evidenciada y temporalmente compatible con el horizonte M08;
4. si la fecha falta/no puede verificarse, el registro no puede ser aplicable y validado;
5. un booleano aislado no demuestra pedido confirmado;
6. cancelaciones, parcialidades y cambios requieren evidencia vigente.

---

## 25. Ledger y plan de asignación M08

La prevención de doble uso se modela cuantitativamente, no por un simple conjunto de IDs.

```text
AllocationLedgerEntry
├── confirmed_demand_id: str
├── allocated_quantity: Decimal
├── unit: str
└── trace_refs: tuple[str, ...]
```

```text
DemandAllocation
├── confirmed_demand_id: str
├── quantity_to_apply: Decimal
├── unit: str
├── allocation_source_ref: str
└── trace_refs: tuple[str, ...]
```

Para cada pedido:

```text
remaining_allocatable
= pending_quantity.value - already_allocated_quantity
```

Debe cumplirse `0 <= already_allocated_quantity <= pending_quantity.value`.

No existe prioridad implícita por fecha, cliente, ID, tamaño, recencia o cualquier otro criterio.

---

## 26. Alcance y absorción M08

```text
AllocationScope
├── decision_id: str
├── scenario_id: str
├── article_id: str
├── evaluation_date: date
├── excess_reference_date: date
├── horizon_end: date
├── horizon_source_ref: str
└── trace_refs: tuple[str, ...]
```

Debe ser compatible con `StockResultIdentity` y con `ExcessResult.reference_date`. `horizon_end >= excess_reference_date` y el horizonte es trazable; no se introduce un valor por defecto.

```text
ConfirmedDemandAbsorptionInput
├── context: StockComputationContext
├── allocation_scope: AllocationScope
├── excess_result: ExcessResult
├── confirmed_demand: CollectionEnvelope[ConfirmedDemandRecord]
├── allocation_ledger: tuple[AllocationLedgerEntry, ...]
└── allocation_plan: tuple[DemandAllocation, ...]
```

Reglas:

1. `confirmed_demand_id` único en la colección, ledger y plan;
2. ledger y plan solo pueden referenciar IDs presentes en la colección;
3. solo registros `APLICABLE_Y_VALIDADA`, mismo artículo/unidad, cantidad pendiente `KNOWN` y `expected_delivery_date <= horizon_end` pueden participar;
4. cada cantidad de plan es positiva y no supera `remaining_allocatable`;
5. `NO_APLICABLE`/`NO_VERIFICABLE` no reducen exceso;
6. colección no `KNOWN` hace M08 no evaluable;
7. STK no elige cómo repartir una absorción entre varios pedidos.

Cálculo agregado autorizado:

```text
total_remaining_applicable = sum(remaining_allocatable de pedidos aplicables)
absorbed_excess = min(excess_quantity, total_remaining_applicable)
residual_excess = max(0, excess_quantity - absorbed_excess)
```

Para materializar la absorción como asignaciones por pedido, el plan debe cumplir:

```text
sum(allocation_plan.quantity_to_apply) == absorbed_excess
```

Si `absorbed_excess == 0`, el plan debe ser vacío.

Si `absorbed_excess > 0`, un plan ausente, incompleto, sobreasignado o incompatible impide materializar una asignación trazable; STK no inventa el reparto.

Ledger de salida:

```text
allocated_quantity_out[id]
= allocated_quantity_in[id] + quantity_to_apply[id]
```

La salida conserva exceso original, total aplicable, absorbido, residual, asignaciones por pedido, ledger actualizado, identidad, estado y trazas. M08 no reescribe M07.

---

## 27. M09 — ausencia

```text
UnresolvedInput
├── field_or_entity
├── state
├── expected_source
├── source_ref
├── evaluation_date
├── affected_operation
└── trace_refs
```

No existe imputación STK v0.1. Un dato ausente no se sustituye por cero, media, último valor, estimación o default.

---

## 28. M10 — contradicciones

`CONFLICTING_DATA` bloquea el cálculo dependiente sin seleccionar automáticamente por recencia, máximo, mínimo, promedio, score o prioridad arbitraria.

Una resolución externa autorizada puede aportar posteriormente un valor `KNOWN` conservando evidencia original y autoridad aplicada.

---

## 29. Error estructural vs incertidumbre empresarial

### Error estructural

Se rechaza técnicamente:

- Decimal no finito;
- cantidad física negativa;
- artículo/unidad incompatibles;
- identidad de resultado incompatible;
- `scenario_id` inconsistente;
- stock actual `KNOWN` cuya `effective_date` no coincide con `evaluation_date`;
- horizonte anterior a `evaluation_date` o sin referencia trazable cuando es requerido;
- movimiento `KNOWN` contribuyente sin fecha o fuera del horizonte;
- `KNOWN` o colección `KNOWN` sin traza;
- `movement_id` duplicado;
- `supply_identity` ausente/duplicado en M06;
- `source_kind/direction` incompatible;
- versión de parámetro/forecast inconsistente;
- P-STK-006 con unidad no autorizada ni normalizada;
- periodo histórico duplicado, incompleto o con límites incompatibles;
- intervalo de aplicabilidad de demanda inválido o ampliado sin referencia trazable;
- ramas discriminadas simultáneamente pobladas;
- ID de demanda confirmada duplicado;
- ledger M08 que excede cantidad pendiente;
- plan M08 que excede saldo disponible o cuyo total no coincide con la absorción agregada.

### Incertidumbre empresarial

Se representa mediante estado:

- dato desconocido/no evidenciado;
- contradicción;
- colección no evidenciada;
- fecha futura no evidenciada;
- forecast no verificable;
- demanda no demostrablemente aplicable a la fecha de referencia requerida;
- aplicabilidad M08 no verificable.

---

## 30. Determinismo

- `Decimal` para cantidades y tasas;
- rechazo de `NaN`/infinitos;
- fechas explícitas;
- no dependencia de hora del sistema;
- sin redondeo empresarial implícito;
- sin prioridad implícita M08;
- misma entrada + misma identidad/versiones → mismo resultado.

---

## 31. Defaults prohibidos

No se hardcodean como política:

- 15 % safety stock;
- 30/90 días de cobertura;
- 10 % tolerancia;
- 12 meses de consumo;
- 90 días de horizonte;
- `PYE-002…005 = Sí`;
- 15 días de riesgo.

La ausencia de configuración no activa esos valores como fallback.

---

## 32. Interfaces de autoridad

- Quality & Trust / Evidence: STK consume, no redefine admisibilidad.
- Motor de Reglas: consume hechos STK; STK no emite resultados empresariales R-STK.
- CRC: fuera de STK.
- TCO: STK v0.1 no inyecta costes derivados.
- Decision Twin: escenarios distintos no se mezclan.
- MED: integra resultados sin transferir autoridad.
- R-STK-004: el contrato consume exclusivamente M08 sobre exceso M07 conforme a la matriz STK especializada; no amplía la excepción a cobertura elevada por interpretación.

---

## 33. Invariantes ejecutables

1. No decisión automática.
2. C0 inmutable.
3. Ausencia ≠ cero.
4. `KNOWN` exige traza.
5. Colección `KNOWN` exige traza.
6. Vacío evidenciado ≠ ausencia.
7. Artículo/unidad compatibles.
8. Resultados intermedios conservan/validan `StockResultIdentity`.
9. Stock actual `KNOWN` corresponde exactamente a `evaluation_date`.
10. Stock disponible no negativo y déficit visible.
11. Demanda solo forecast autorizado o histórico de consumo.
12. Toda demanda conserva fecha de referencia e intervalo de aplicabilidad.
13. La media histórica sin autoridad futura queda aplicable solo a `evaluation_date`.
14. P-STK-006 exige unidad mensual autorizada/normalizada.
15. Ventana histórica coincide uno-a-uno en ID y límites.
16. Periodos completos: `evidenced_days` coincide con días del periodo requerido.
17. IDs históricos únicos.
18. Ventas ≠ demanda.
19. Sin fallback de método.
20. Forecast y contexto comparten versión.
21. Forecast dentro de horizonte válido.
22. Coverage consume demanda aplicable a `evaluation_date`.
23. `movement_id` único.
24. `supply_identity` único evita doble conteo M06.
25. Source kind/dirección compatibles.
26. Todo movimiento `KNOWN` contribuyente está dentro del horizonte.
27. Fecha M06 vencida no se desplaza.
28. Movimiento `NOT_APPLICABLE` evidenciado no contamina.
29. Tasa de demanda no crea movimientos.
30. Propuesta exige escenario coincidente.
31. Horizonte proyectivo explícito y trazable.
32. Opening reutiliza disponibilidad con identidad compatible.
33. Sin orden intradía; cierre diario agregado.
34. Incertidumbre sin fecha contamina desde evaluación.
35. Incertidumbre fechada contamina desde su fecha.
36. Stock proyectado puede ser negativo como saldo analítico.
37. Opening cero produce `depletion_date = evaluation_date`.
38. Mínimo incluye opening.
39. M07 distingue referencia física actual de saldo proyectado.
40. Coverage maximum exige demanda diaria > 0 y aplicable a `stock_reference.reference_date`.
41. Ramas de máximo/tolerancia son exclusivas.
42. M07 no duplica M05/M06.
43. Tolerancia tipada/normalizada.
44. Cantidad pendiente M08 conserva estado propio.
45. Pedido M08 aplicable exige fecha prevista evidenciada.
46. Horizonte M08 es explícito y trazable.
47. Ledger M08 es cuantitativo.
48. STK no inventa prioridad de asignación M08.
49. Plan por pedido suma exactamente la absorción agregada.
50. M08 no reescribe M07.
51. R-STK-004 no se amplía fuera de M08/M07.
52. Contradicción no se resuelve por heurística.
53. Sin defaults normativos.
54. Determinismo.

---

## 34. Pruebas mínimas futuras

La implementación debe cubrir al menos:

- disponibilidad, déficit, identidad, trazabilidad y rechazo de snapshot de otra fecha;
- vacío evidenciado vs ausencia;
- versión de parámetro incorrecta;
- P-STK-006 con unidad incorrecta/no normalizada;
- ventana histórica con ID duplicado/sustituido/faltante, límites incompatibles o días incompletos;
- tasa histórica limitada a `evaluation_date` sin autoridad de vigencia futura;
- tasa histórica con extensión futura trazada;
- forecast versión/horizonte y aplicabilidad;
- cobertura determinada y `UNBOUNDED` solo con tasa temporalmente aplicable;
- movimiento duplicado, sin fecha, fuera del horizonte, `NOT_APPLICABLE`, M06 doble identidad/dirección inválida/fecha vencida;
- propuesta en escenario incorrecto;
- mezcla rechazada entre escenarios/snapshots;
- proyección diaria agregada, opening cero, saldo negativo e incertidumbre con/sin fecha;
- horizonte sin traza rechazado;
- referencia M07 actual/proyectada, incluido saldo proyectado negativo;
- M07 por cobertura rechazado cuando la demanda no es aplicable a la fecha de referencia;
- bases discriminadas incompatibles;
- máximo directo/por cobertura, incluida demanda cero;
- tolerancia por cantidad/tasa;
- estados de exceso;
- M08 cantidad no conocida, fecha no verificable, ledger parcial, plan inválido, absorción parcial/total y ausencia de prioridad implícita;
- M09/M10;
- no decisión, no defaults y reproducibilidad.

---

## 35. Exclusiones v0.1

Fuera de alcance:

- forecasting interno;
- ventas → demanda automática;
- tasa diaria → calendario automático;
- vigencia futura implícita de demanda histórica;
- tolerancia temporal implícita para snapshots de stock;
- optimización / EOQ;
- fórmula normativa de `stock_minimum` o `safety_stock`;
- imputación;
- resolución heurística de contradicciones;
- política de prioridad de asignación M08;
- costes TCO derivados;
- acciones automáticas;
- persistencia SQL STK;
- API externa;
- cambios C0;
- CRC;
- decisión final.

---

## 36. Estado

**Contrato v0.6:** DEPURADO TEMPORAL FINAL.  
**Hallazgos A1…A9:** resueltos.  
**Hallazgos B1…B13:** resueltos.  
**Hallazgos C1…C7:** resueltos.  
**Hallazgos D1…D4:** resueltos.  
**Hallazgos E1…E3:** resueltos.  
**Frontera R-STK-004:** verificada sin ampliación de alcance.  
**Siguiente paso:** AUDIT 2 FINAL independiente sobre v0.6.  
**Implementación ejecutable:** NO AUTORIZADA TODAVÍA.
