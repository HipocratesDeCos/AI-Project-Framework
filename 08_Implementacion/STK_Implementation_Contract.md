# EIOS — Stock & Demand Implementation Contract

## 1. Identidad

**Documento:** STK Implementation Contract  
**Versión:** 0.4  
**Estado:** DEPURADO FINAL — PENDIENTE DE AUDIT 2 FINAL  
**Baseline de origen:** `main @ c2bd5b9b73974426d29cc234ffda42d494e720fb`  
**Dominio:** Capa 3 — Stock / Demanda  
**Autoridad metodológica:** `01_Modelo/Stock_Demand_Methodological_Matrix.md` v1.1  
**Autoridad de entrada:** `01_Modelo/STK_Contract_Entry_Authority.md` v1.0  
**Autoridad de reglas:** `04_Reglas/Matriz_Reglas_MVP.md` v2.1  
**Dependencias:** `04_Reglas/Rule_Dependency_Matrix.md` v1.4  
**Auditorías:** `STK_Implementation_Contract_Audit_v0.1.md`, `STK_Implementation_Contract_Audit_2_v0.1.md`, `STK_Implementation_Contract_Audit_2_Final_v0.2.md`

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

## 7. Magnitud cuantitativa normalizada

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

Cada operación valida el `parameter_id`, tipo, dimensión/unidad y, cuando sea necesaria, la normalización autorizada. No existe fallback a los valores iniciales del catálogo.

---

## 10. Disponibilidad de stock

Entrada:

```text
StockAvailabilityInput
├── context: StockComputationContext
├── stock_on_hand: NormalizedQuantity
└── stock_committed: NormalizedQuantity
```

Con ambas magnitudes `KNOWN`, mismo artículo/unidad y vigencia compatible:

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

El déficit permanece visible aunque `stock_available` tenga suelo cero. Un consumidor debe exigir que `identity` coincida con su contexto STK.

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

Un periodo `KNOWN` exige consumo real, periodo trazable, `period_start <= period_end`, `evidenced_days > 0`, cantidad no negativa y ausencia de solapamiento con otro periodo de la misma ventana.

Ventas y forecast no son consumo real. Cero solo existe cuando está explícitamente evidenciado.

---

## 12. Política histórica de demanda

La ventana requerida se materializa sin inferir el calendario:

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
├── source_ref: str
└── trace_refs: tuple[str, ...]
```

Reglas:

1. `parameter.parameter_id == P-STK-006`;
2. parámetro `KNOWN` y versión coincidente;
3. el valor debe ser entero positivo;
4. su unidad debe estar normalizada/autorizada como **meses o número de periodos mensuales**; si requiere conversión, `normalization_ref` es obligatorio;
5. la implementación no infiere la unidad por el ID `P-STK-006`;
6. `len(required_periods)` coincide con el valor normalizado del parámetro;
7. `RequiredPeriodSpec.period_id` es único;
8. cada especificación cumple `period_start <= period_end`;
9. las especificaciones no se solapan;
10. `period_calendar_ref` identifica la fuente que determina los periodos concretos aplicables a `evaluation_date`;
11. STK no presupone meses naturales ni genera IDs por sí mismo.

---

## 13. Demanda histórica

```text
HistoricalDemandInput
├── context: StockComputationContext
├── policy: HistoricalDemandPolicy
└── periods: CollectionEnvelope[ConsumptionPeriod]
```

Resultado `KNOWN` solo si:

- colección `KNOWN` y trazable;
- `ConsumptionPeriod.period_id` es único en la colección;
- existe correspondencia uno-a-uno entre los periodos recibidos y `required_periods`;
- para cada ID coinciden exactamente `period_start` y `period_end` con su `RequiredPeriodSpec`;
- todos los periodos son `KNOWN`;
- no hay solapamientos;
- artículo/unidad son homogéneos y compatibles con el contexto;
- cada `evidenced_days > 0`;
- no existen contradicciones no resueltas.

Cálculo:

```text
total_evidenced_consumption = sum(period.quantity)
evidenced_days_in_window = sum(period.evidenced_days)
historical_daily_demand = total_evidenced_consumption / evidenced_days_in_window
```

No se sustituye, duplica ni acorta la ventana.

Salida:

```text
DemandRateResult
├── identity: StockResultIdentity
├── method: HISTORICAL_CONSUMPTION | AUTHORIZED_FORECAST
├── daily_demand: Decimal | null
├── unit: str
├── state: StockDataState
├── window_or_horizon
├── source_ref
├── forecast_version: str | null
└── trace_refs
```

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

Para consumir un forecast como `KNOWN`:

1. versión no vacía;
2. `context.forecast_version == forecast.forecast_version` y ninguno es nulo;
3. `horizon_start <= evaluation_date <= horizon_end`;
4. artículo/unidad compatibles;
5. tasa no negativa y finita;
6. trazabilidad suficiente.

STK no calcula forecast y no realiza fallback automático forecast↔histórico. Ventas históricas no constituyen método de demanda STK v0.1.

---

## 15. Cobertura M04

Si stock disponible y demanda diaria son `KNOWN`, pertenecen a la misma `StockResultIdentity` y `daily_demand > 0`:

```text
coverage_days = stock_available / daily_demand
status = DETERMINED
```

Si `daily_demand == 0` está confirmada y evidenciada:

```text
coverage_days = null
status = UNBOUNDED
reason = CONFIRMED_ZERO_DEMAND
```

No se representa infinito numérico. Estados de cobertura:

`DETERMINED | UNBOUNDED | UNKNOWN | NOT_EVIDENCED | CONFLICTING_DATA`.

La salida conserva `StockResultIdentity`.

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

- `movement_id` es único dentro de la colección de una proyección; un duplicado es error estructural y nunca se suma dos veces;
- movimiento `KNOWN` exige cantidad no negativa, finita, unidad/artículo compatibles y traza;
- no se convierte una tasa de demanda en movimientos implícitos.

### M06

Para `PENDING_ORDER`/`IN_TRANSIT`:

- `supply_identity` obligatorio;
- cada `supply_identity` activo aparece una sola vez en la colección;
- una parcialidad distinta exige identidad de segmento distinta y trazable;
- una identidad no puede coexistir como pendiente y tránsito;
- una entrada futura `KNOWN` exige `evaluation_date <= effective_date <= horizon_end`;
- fecha vencida no se desplaza automáticamente;
- recepción confirmada deja M06;
- historial logístico aporta trazabilidad, no cantidades adicionales.

### Cantidad propuesta

Para `PROPOSED_PURCHASE`:

- `scenario_id` obligatorio;
- `scenario_id == DecisionContext.scenario_id`;
- cantidad normalizada;
- fecha explícita;
- traza.

STK no presume aprobación ni recepción.

---

## 17. Colección de movimientos

`StockProjectionInput.movements` es `CollectionEnvelope[ProjectionMovement]`.

Solo una colección `KNOWN`, trazable y sin IDs duplicados puede afirmar que el conjunto recibido del horizonte está determinado. Una colección no determinada hace no determinada la proyección global según M09/M10.

---

## 18. Proyección M05

```text
StockProjectionInput
├── context: StockComputationContext
├── opening_availability: StockAvailabilityResult
├── movements: CollectionEnvelope[ProjectionMovement]
├── horizon_end: date
└── scenario_id: str
```

Precondiciones:

- `scenario_id == DecisionContext.scenario_id`;
- `horizon_end >= evaluation_date`;
- `opening_availability.identity == context.result_identity`;
- opening `KNOWN` para una proyección determinada.

### 18.1 Cálculo diario

No existe orden intradía por ID. Para cada fecha:

```text
total_inflows_date = sum(known inflows)
total_outflows_date = sum(known outflows)
closing_stock_date = opening_stock_date + total_inflows_date - total_outflows_date
```

Movimientos del mismo día se agregan antes del cierre. El cierre alimenta la fecha siguiente. El stock negativo se conserva como evidencia.

### 18.2 Incertidumbre

Cada `ProjectionPoint` conserva identidad STK, fecha, stock proyectado, estado, totales de entrada/salida y trazas.

- movimiento requerido no determinado con fecha conocida → incertidumbre desde esa fecha;
- movimiento requerido no determinado con `effective_date = null` → incertidumbre desde `evaluation_date`;
- un movimiento conocido posterior no restaura por sí solo un estado `KNOWN`.

### 18.3 Mínimo y agotamiento

El valor inicial forma parte de la secuencia:

```text
minimum_projected_stock = min(opening_stock, determined daily closings)
```

Si `opening_stock_available == 0` y es `KNOWN`, `depletion_date = evaluation_date`.

En otro caso, `depletion_date` es la primera fecha de cierre diario determinado con stock `<= 0`. No se afirma un instante intradía.

La salida de proyección conserva `StockResultIdentity` y el `scenario_id` canónico.

---

## 19. Frontera R-STK-001

STK entrega evidencia como `minimum_projected_stock`, `depletion_date`, recepciones relevantes y estados de determinabilidad. No emite `COMPRAR`, `COMPRAR CONDICIONADO`, `NEGOCIAR` o `NO COMPRAR`.

`P-PYE-006 = 15 días` no se usa como condición oculta ni default.

---

## 20. Base de stock máximo M07

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

Las ramas son mutuamente excluyentes:

- `DIRECT_QUANTITY` → `direct_quantity` presente; `coverage_maximum = null`; `demand_rate = null`;
- `COVERAGE_MAXIMUM` → `direct_quantity = null`; `coverage_maximum` y `demand_rate` presentes.

`state` debe ser compatible con la rama activa. Campos de una rama inactiva no pueden influir en el cálculo.

### DIRECT_QUANTITY

Cantidad `KNOWN`, trazable y compatible con contexto. No crea un parámetro nuevo.

### COVERAGE_MAXIMUM

- `coverage_maximum.parameter_id == P-STK-004`;
- valor `KNOWN`, versión coincidente y unidad temporal normalizada en días;
- `demand_rate` `KNOWN` con identidad compatible;
- `daily_demand > 0`.

Solo entonces:

```text
stock_maximum = coverage_maximum_days * authorized_daily_demand
```

Con demanda cero confirmada no se deriva `stock_maximum = 0`; la base por cobertura queda no aplicable/no determinable.

---

## 21. Tolerancia de exceso M07

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

- `QUANTITY` → `quantity` presente y `rate = null`;
- `RATE` → `quantity = null` y `rate` presente.

Para `RATE`:

- `parameter_id == P-STK-005`;
- versión coincidente;
- `normalized_rate >= 0`;
- `normalization_ref` obligatorio;
- no se infiere si `10` significa 10 % ni si `0.10` es la escala correcta sin normalización trazada.

```text
excess_tolerance_quantity = stock_maximum * normalized_rate
```

Para `QUANTITY`, la cantidad debe ser `KNOWN`, misma unidad/artículo y trazable.

---

## 22. Exceso M07

```text
ExcessInput
├── context: StockComputationContext
├── stock_reference: NormalizedQuantity
├── maximum_basis: StockMaximumBasis
└── tolerance_basis: ExcessToleranceBasis
```

Con entradas determinadas y compatibles:

```text
excess_threshold = stock_maximum + excess_tolerance_quantity
excess_quantity = max(0, stock_reference - excess_threshold)
```

Estados:

`NO_EXCESS | WITHIN_TOLERANCE | EXCESS | UNKNOWN | NOT_EVIDENCED | CONFLICTING_DATA`.

Si `stock_reference` procede de M05, conserva la `StockResultIdentity`/traza correspondiente y M07 no vuelve a sumar M06 ni propuesta.

STK calcula; el Motor de Reglas evalúa R-STK-002/003. Relaciones parámetro↔regla confirmadas únicamente:

- `P-STK-004 → R-STK-002`;
- `P-STK-004 → R-STK-003` derivada;
- `P-STK-005 → R-STK-003` derivada.

La salida `ExcessResult` conserva `StockResultIdentity`, máximo, tolerancia, umbral, exceso, estado y trazas.

---

## 23. M08 — demanda confirmada

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

1. la cantidad pendiente conserva su propio estado, artículo, unidad y evidencia;
2. solo `pending_quantity.state == KNOWN` puede absorber exceso;
3. `APLICABLE_Y_VALIDADA` exige `expected_delivery_date` no nula, evidenciada y compatible con la fecha/horizonte de la evaluación;
4. si la fecha de entrega falta o no puede verificarse, el registro no puede ser `APLICABLE_Y_VALIDADA`;
5. un booleano aislado no constituye evidencia de pedido confirmado;
6. cancelaciones, parcialidades y cambios requieren nueva evidencia vigente.

---

## 24. Alcance de asignación M08

```text
AllocationScope
├── decision_id: str
├── scenario_id: str
├── article_id: str
└── evaluation_date: date
```

Debe coincidir con la `StockResultIdentity` aplicable.

```text
ConfirmedDemandAbsorptionInput
├── context: StockComputationContext
├── allocation_scope: AllocationScope
├── excess_result: ExcessResult
├── confirmed_demand: CollectionEnvelope[ConfirmedDemandRecord]
└── already_allocated_ids: frozenset[str]
```

Reglas:

1. `confirmed_demand_id` único en la colección;
2. IDs ya presentes en `already_allocated_ids` no pueden reutilizarse;
3. solo `APLICABLE_Y_VALIDADA`, mismo artículo/unidad, identidad/contexto compatible, fecha aplicable y cantidad pendiente `KNOWN` absorben;
4. `NO_APLICABLE` y `NO_VERIFICABLE` no reducen exceso;
5. colección no `KNOWN` hace M08 no evaluable; no se infiere inexistencia.

Cálculo:

```text
confirmed_order_quantity_applicable = sum(unique not-yet-allocated applicable pending quantities)
absorbed_excess = min(excess_quantity, confirmed_order_quantity_applicable)
residual_excess = max(0, excess_quantity - absorbed_excess)
```

La salida conserva exceso original, absorbido, residual, IDs usados, `allocated_ids = already_allocated_ids ∪ ids_used`, identidad, estado y trazas.

La operación es pura; no requiere persistencia interna. M08 no reescribe M07.

---

## 25. M09 — ausencia

Estructura equivalente:

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

No existe política de imputación STK v0.1. Un dato ausente no se sustituye por cero, media, último valor, estimación o default.

---

## 26. M10 — contradicciones

`CONFLICTING_DATA` bloquea el cálculo dependiente sin seleccionar automáticamente por recencia, máximo, mínimo, promedio, score o prioridad arbitraria.

Una resolución externa autorizada puede aportar posteriormente un valor `KNOWN` conservando referencia a la evidencia original y a la autoridad de resolución aplicada.

---

## 27. Error estructural vs incertidumbre empresarial

### Error estructural

Se rechaza técnicamente:

- Decimal no finito;
- cantidad física negativa;
- artículo/unidad incompatibles;
- `StockResultIdentity` incompatible entre productor y consumidor;
- `scenario_id` inconsistente;
- horizonte anterior a `evaluation_date`;
- `KNOWN` o colección `KNOWN` sin traza;
- `movement_id` duplicado;
- `supply_identity` ausente o duplicado en M06;
- `source_kind/direction` incompatible;
- versión de parámetro o forecast inconsistente;
- P-STK-006 con unidad/dimensión no autorizada ni normalizada;
- periodo histórico duplicado o límites temporales incompatibles con `RequiredPeriodSpec`;
- ramas discriminadas simultáneamente pobladas;
- ID de demanda confirmada duplicado.

### Incertidumbre empresarial

Se representa mediante estado:

- dato desconocido/no evidenciado;
- contradicción;
- colección no evidenciada;
- fecha futura no evidenciada;
- forecast no verificable;
- pedido M08 sin fecha/evidencia suficiente;
- aplicabilidad M08 no verificable.

---

## 28. Determinismo

- `Decimal` para cantidades y tasas;
- rechazo de `NaN`/infinitos;
- fechas explícitas;
- no dependencia de hora del sistema;
- sin redondeo empresarial implícito;
- misma entrada + misma identidad/versiones → mismo resultado.

---

## 29. Defaults prohibidos

No se hardcodean como política:

- 15 % safety stock;
- 30/90 días de cobertura;
- 10 % tolerancia;
- 12 meses de consumo;
- 90 días de horizonte;
- `PYE-002…005 = Sí`;
- 15 días de riesgo.

La ausencia de configuración requerida no activa esos valores como fallback.

---

## 30. Interfaces de autoridad

- Quality & Trust / Evidence: STK consume evidencia; no redefine admisibilidad.
- Motor de Reglas: consume hechos STK; STK no emite el resultado empresarial de R-STK.
- CRC: fuera de STK.
- TCO: STK v0.1 no inyecta costes derivados.
- Decision Twin: escenarios distintos no se sobrescriben ni mezclan gracias a identidad de contexto.
- MED: integra resultados sin transferir autoridad.

---

## 31. Invariantes ejecutables

1. No decisión automática.
2. C0 inmutable.
3. Ausencia ≠ cero.
4. `KNOWN` exige traza.
5. Colección `KNOWN` exige traza.
6. Vacío evidenciado ≠ ausencia.
7. Artículo/unidad compatibles.
8. Resultados intermedios conservan y validan `StockResultIdentity`.
9. Stock disponible no negativo y déficit visible.
10. Demanda solo forecast autorizado o histórico de consumo.
11. P-STK-006 exige unidad mensual normalizada/autorizada.
12. Ventana histórica coincide uno-a-uno en ID y límites con `RequiredPeriodSpec`.
13. IDs de consumo históricos son únicos.
14. Ventas ≠ demanda.
15. Sin fallback de método.
16. Forecast y contexto comparten versión.
17. Forecast solo dentro de horizonte válido.
18. `movement_id` único.
19. `supply_identity` único evita doble conteo M06.
20. Source kind y dirección son compatibles.
21. Fecha M06 vencida no se mueve al futuro.
22. Tasa de demanda no crea movimientos implícitos.
23. Propuesta exige `scenario_id` coincidente.
24. Opening projection reutiliza `StockAvailabilityResult` con identidad compatible.
25. Sin orden intradía inventado; cierre diario agregado.
26. Incertidumbre sin fecha contamina desde `evaluation_date`.
27. Incertidumbre fechada contamina desde esa fecha.
28. Stock proyectado puede ser negativo.
29. Opening cero produce `depletion_date = evaluation_date`.
30. Mínimo incluye opening stock.
31. Coverage maximum requiere demanda diaria > 0.
32. Ramas de máximo y tolerancia son mutuamente excluyentes.
33. M07 no duplica M05/M06.
34. Tolerancia tipada y normalizada con traza.
35. Cantidad pendiente M08 conserva estado cuantitativo propio.
36. Pedido M08 aplicable/validado exige fecha prevista evidenciada y aplicable.
37. M08 no reutiliza IDs dentro del `AllocationScope` recibido.
38. M08 no reescribe M07.
39. Contradicción no se resuelve por heurística.
40. Sin defaults normativos.
41. Determinismo.

---

## 32. Pruebas mínimas futuras

La implementación deberá cubrir al menos:

- disponibilidad, déficit, identidad y trazabilidad;
- vacío evidenciado vs ausencia;
- parámetro con versión incorrecta;
- P-STK-006 con unidad incorrecta/no normalizada;
- ventana histórica con ID duplicado, sustituido, faltante o límites temporales incompatibles;
- forecast con versión/horizonte inválidos;
- cobertura determinada y `UNBOUNDED`;
- `movement_id` duplicado;
- M06 con identidad duplicada, dirección inválida y fecha vencida sin roll-forward;
- propuesta en escenario incorrecto;
- mezcla rechazada de resultados intermedios entre escenarios/snapshots;
- proyección diaria agregada, opening cero, stock negativo e incertidumbre con/sin fecha;
- bases discriminadas con ramas simultáneas rechazadas;
- máximo directo y por cobertura, incluida demanda cero;
- tolerancia por cantidad y tasa normalizada;
- estados de exceso;
- M08 con cantidad pendiente no conocida, fecha no verificable, colección ausente, vacío evidenciado, absorción parcial/total y reutilización bloqueada;
- M09/M10;
- no decisión, no defaults y reproducibilidad.

---

## 33. Exclusiones v0.1

Fuera de alcance:

- forecasting interno;
- ventas → demanda automática;
- tasa diaria → calendario automático;
- optimización / EOQ;
- fórmula normativa de `stock_minimum` o `safety_stock`;
- imputación;
- resolución heurística de contradicciones;
- costes TCO derivados;
- acciones automáticas;
- persistencia SQL STK;
- API externa;
- cambios C0;
- CRC;
- decisión final.

---

## 34. Estado

**Contrato v0.4:** DEPURADO FINAL tras Audit 2 Final v0.2.  
**Hallazgos A1…A9:** resueltos.  
**Hallazgos B1…B13:** resueltos.  
**Hallazgos C1…C7:** resueltos.  
**Siguiente paso:** AUDIT 2 FINAL independiente sobre v0.4.  
**Implementación ejecutable:** NO AUTORIZADA TODAVÍA.
