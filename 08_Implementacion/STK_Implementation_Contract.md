# EIOS — Stock & Demand Implementation Contract

## 1. Identidad

**Documento:** STK Implementation Contract  
**Versión:** 0.3  
**Estado:** DEPURADO 2 — PENDIENTE DE AUDIT 2 FINAL  
**Baseline:** `main @ c2bd5b9b73974426d29cc234ffda42d494e720fb`  
**Dominio:** Capa 3 — Stock / Demanda  
**Autoridad metodológica:** `01_Modelo/Stock_Demand_Methodological_Matrix.md` v1.1  
**Autoridad de entrada:** `01_Modelo/STK_Contract_Entry_Authority.md` v1.0  
**Autoridad de reglas:** `04_Reglas/Matriz_Reglas_MVP.md` v2.1  
**Dependencias:** `04_Reglas/Rule_Dependency_Matrix.md` v1.4  
**Auditorías:** `STK_Implementation_Contract_Audit_v0.1.md` y `STK_Implementation_Contract_Audit_2_v0.1.md`

---

## 2. Propósito y frontera

Este contrato define la frontera física mínima implementable de **Stock & Demand Intelligence (STK) v0.1**.

STK materializa únicamente semántica y cálculos ya autorizados. No crea reglas, parámetros, defaults normativos, forecasting implícito, autoridad paralela de evidencia ni decisión automática.

STK produce resultados analíticos para capas posteriores; Motor de Reglas, CRC, MED y decisor humano conservan sus respectivas autoridades.

La implementación ejecutable permanece bloqueada hasta superar `AUDIT 2 FINAL → CERRAR`.

---

## 3. Frontera C0 y paquete físico

STK reutiliza `DecisionContext` y no modifica `PurchaseOperation`, `Evidence`, `EvidenceValidation`, `Rule`, `Assessment` ni `Trace`.

`PurchaseOperation.quantity` no se convierte automáticamente en cantidad STK normalizada porque C0 no contiene la unidad base objetivo.

Paquete previsto:

```text
eios/stock/
├── __init__.py
├── models.py
└── engine.py
```

No se permiten dependencias circulares con `eios.core`.

---

## 4. Identidad temporal

La fecha canónica es `evaluation_date`; `as_of_date` se materializa con esa misma identidad.

La proyección v0.1 opera a granularidad **diaria**. No existe autoridad para inferir secuencia intradía.

Toda entrada actual debe ser válida para `evaluation_date`; toda entrada futura declara su fecha/horizonte explícito.

---

## 5. Estados STK

```text
KNOWN
UNKNOWN
NOT_EVIDENCED
NOT_APPLICABLE
CONFLICTING_DATA
```

- `KNOWN`: valor utilizable y trazable;
- `UNKNOWN`: no determinable;
- `NOT_EVIDENCED`: valor declarado sin soporte suficiente;
- `NOT_APPLICABLE`: evidencia de que no aplica;
- `CONFLICTING_DATA`: fuentes materialmente incompatibles no resueltas.

No redefinen los estados C0.

### Invariantes

1. `state != KNOWN` no presenta un valor como determinado.
2. `UNKNOWN / NOT_EVIDENCED / CONFLICTING_DATA ≠ 0`.
3. Todo valor `KNOWN` exige al menos `source_ref` o `trace_ref`.

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

1. una colección `KNOWN` exige `source_ref` o al menos un `trace_ref`, incluso si está vacía;
2. solo `KNOWN + items=()` significa conjunto vacío evidenciado;
3. una colección vacía `UNKNOWN`/`NOT_EVIDENCED` no significa inexistencia;
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

- Decimal finito;
- cantidad física `KNOWN` no negativa;
- mismo artículo/unidad para operaciones entre cantidades;
- `state != KNOWN` → `value = null`;
- `KNOWN` exige trazabilidad;
- no hay conversión de unidad implícita.

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

`parameters_version` y `data_snapshot_id` proceden de `DecisionContext`.

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
└── trace_refs: tuple[str, ...]
```

Para utilizar un parámetro como `KNOWN`:

```text
ConfiguredParameterValue.parameters_version
== DecisionContext.parameters_version
```

No existe fallback a valores iniciales del catálogo.

Cada operación debe validar además el `parameter_id` esperado, no solo unidad o tipo.

---

## 10. Disponibilidad de stock

```text
StockAvailabilityInput
├── context
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
├── article_id
├── unit
├── evaluation_date
├── stock_on_hand
├── stock_committed
├── stock_available: Decimal | null
├── availability_deficit: Decimal | null
├── state
└── trace_refs
```

El déficit permanece visible aunque `stock_available` tenga suelo cero.

---

## 11. Consumo M01

```text
ConsumptionPeriod
├── article_id
├── period_id: str
├── period_start: date
├── period_end: date
├── evidenced_days: int
├── quantity: Decimal | null
├── unit
├── state
├── source_ref
└── trace_refs
```

`KNOWN` exige:

- consumo real;
- periodo identificable y trazable;
- `evidenced_days > 0`;
- cantidad no negativa;
- no solapamiento con otro periodo de la misma ventana.

Ventas y forecast no son consumo real. Cero solo existe cuando está evidenciado.

---

## 12. Política histórica de demanda

```text
HistoricalDemandPolicy
├── parameter: ConfiguredParameterValue
├── required_period_ids: tuple[str, ...]
├── period_calendar_ref: str
├── source_ref: str
└── trace_refs: tuple[str, ...]
```

Reglas:

1. `parameter.parameter_id == P-STK-006`;
2. parámetro `KNOWN` y versión coincidente;
3. su valor entero positivo debe corresponder al número de periodos mensuales requeridos;
4. `len(required_period_ids)` debe coincidir con ese valor;
5. `required_period_ids` son únicos;
6. `period_calendar_ref` identifica la fuente que resuelve qué periodos mensuales concretos forman la ventana para `evaluation_date`;
7. STK no presupone meses naturales ni genera por sí mismo IDs de periodo.

---

## 13. Demanda histórica

```text
HistoricalDemandInput
├── context
├── policy: HistoricalDemandPolicy
└── periods: CollectionEnvelope[ConsumptionPeriod]
```

Resultado `KNOWN` solo si:

- colección `KNOWN` y trazable;
- el conjunto de `period_id` recibido coincide exactamente con `required_period_ids`;
- todos los periodos son `KNOWN`;
- no se solapan;
- artículo/unidad homogéneos;
- cada `evidenced_days > 0`;
- no existen contradicciones.

Cálculo:

```text
total_evidenced_consumption = sum(period.quantity)
evidenced_days_in_window = sum(period.evidenced_days)
historical_daily_demand = total_evidenced_consumption / evidenced_days_in_window
```

No se sustituye ni acorta la ventana.

---

## 14. Forecast autorizado

Métodos de demanda v0.1:

```text
AUTHORIZED_FORECAST
HISTORICAL_CONSUMPTION
```

Forecast físico:

```text
AuthorizedDemandForecast
├── article_id
├── daily_demand: Decimal | null
├── unit
├── horizon_start: date
├── horizon_end: date
├── state
├── forecast_version: str
├── source_ref
└── trace_refs
```

Para consumirlo como `KNOWN`:

1. `forecast_version` no vacío;
2. `StockComputationContext.forecast_version == AuthorizedDemandForecast.forecast_version`;
3. `horizon_start <= evaluation_date <= horizon_end` para cobertura en fecha de evaluación;
4. artículo/unidad compatibles;
5. trazabilidad suficiente.

STK no calcula forecast ni hace fallback forecast↔histórico.

`DemandRateResult` conserva método, tasa diaria, unidad, estado, ventana/horizonte, versión y trazas.

Ventas históricas no son un método de demanda v0.1.

---

## 15. Cobertura M04

Si stock disponible y demanda diaria son `KNOWN` y `daily_demand > 0`:

```text
coverage_days = stock_available / daily_demand
status = DETERMINED
```

Si demanda cero está confirmada y evidenciada:

```text
coverage_days = null
status = UNBOUNDED
reason = CONFIRMED_ZERO_DEMAND
```

No se representa infinito numérico.

Estados de cobertura:

```text
DETERMINED
UNBOUNDED
UNKNOWN
NOT_EVIDENCED
CONFLICTING_DATA
```

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
├── state
├── source_kind: PENDING_ORDER | IN_TRANSIT | AUTHORIZED_DEMAND | RESERVATION | OTHER_AUTHORIZED_NEED | PROPOSED_PURCHASE
├── source_ref
└── trace_refs
```

### Dirección obligatoria

```text
PENDING_ORDER | IN_TRANSIT | PROPOSED_PURCHASE
→ INFLOW

AUTHORIZED_DEMAND | RESERVATION | OTHER_AUTHORIZED_NEED
→ OUTFLOW
```

Una combinación incompatible es error estructural.

### M06

Para `PENDING_ORDER`/`IN_TRANSIT`:

- `supply_identity` obligatorio;
- cada `supply_identity` activo aparece una sola vez en la colección de proyección;
- una parcialidad distinta exige identidad de segmento distinta y trazable;
- la misma identidad no puede existir como pendiente y tránsito a la vez;
- una entrada futura `KNOWN` exige `evaluation_date <= effective_date <= horizon_end`;
- fecha vencida no se desplaza automáticamente;
- recepción confirmada deja M06.

### Cantidad propuesta

Para `PROPOSED_PURCHASE`:

- `scenario_id` obligatorio;
- `scenario_id == DecisionContext.scenario_id`;
- cantidad normalizada;
- fecha explícita;
- traza.

STK no presume aprobación o recepción.

### Demanda y calendario

Una tasa de demanda no genera automáticamente movimientos `OUTFLOW`. Se requiere calendario/movimiento autorizado y fechado.

---

## 17. Colección de movimientos

`StockProjectionInput.movements` es `CollectionEnvelope[ProjectionMovement]`.

Solo una colección `KNOWN` y trazable puede afirmar que el conjunto requerido del horizonte está completo.

Colección no determinada → proyección global no determinada.

---

## 18. Proyección M05

```text
StockProjectionInput
├── context
├── opening_availability: StockAvailabilityResult
├── movements: CollectionEnvelope[ProjectionMovement]
├── horizon_end: date
└── scenario_id: str
```

Precondiciones:

- `scenario_id == DecisionContext.scenario_id`;
- `horizon_end >= evaluation_date`;
- `opening_availability` corresponde a mismo artículo, unidad y `evaluation_date`;
- opening `KNOWN` para proyección determinada.

### 18.1 Cálculo diario

No hay orden intradía por ID.

Para cada fecha:

```text
total_inflows_date = sum(known inflows)
total_outflows_date = sum(known outflows)
closing_stock_date = opening_stock_date + total_inflows_date - total_outflows_date
```

Movimientos del mismo día se agregan antes del cierre. El cierre alimenta la fecha siguiente. Stock negativo se conserva.

### 18.2 Incertidumbre

Cada `ProjectionPoint` conserva `date`, `projected_stock`, `state`, totales de entrada/salida y trazas.

- movimiento requerido no determinado con fecha conocida → incertidumbre desde esa fecha;
- movimiento requerido no determinado con `effective_date = null` → incertidumbre desde `evaluation_date` para toda la proyección futura;
- un movimiento conocido posterior no restaura `KNOWN` por sí solo.

### 18.3 Mínimo y agotamiento

El valor inicial forma parte de la secuencia analizada.

```text
minimum_projected_stock = min(opening_stock, determined daily closings)
```

Si `opening_stock_available == 0` y es `KNOWN`:

```text
depletion_date = evaluation_date
```

En otro caso, `depletion_date` es la primera fecha de cierre diario determinada con stock `<= 0`.

No se afirma instante intradía.

---

## 19. Frontera R-STK-001

STK entrega evidencia analítica (`minimum_projected_stock`, `depletion_date`, recepción relevante y estado). No emite `COMPRAR` ni `COMPRAR CONDICIONADO`.

`P-PYE-006 = 15 días` no se usa como condición oculta.

---

## 20. Base de stock máximo M07

```text
StockMaximumBasis
├── kind: DIRECT_QUANTITY | COVERAGE_MAXIMUM
├── direct_quantity: NormalizedQuantity | null
├── coverage_maximum: ConfiguredParameterValue | null
├── demand_rate: DemandRateResult | null
├── state
├── source_ref
└── trace_refs
```

### DIRECT_QUANTITY

- `direct_quantity` obligatorio y `KNOWN`;
- no crea un parámetro nuevo;
- `coverage_maximum` y `demand_rate` no se usan para derivar el máximo.

### COVERAGE_MAXIMUM

- `coverage_maximum.parameter_id == P-STK-004`;
- valor `KNOWN`, versión coincidente y unidad temporal compatible en días;
- `demand_rate` `KNOWN`;
- **`daily_demand > 0`**;
- mismo artículo/unidad.

Solo entonces:

```text
stock_maximum = coverage_maximum_days * authorized_daily_demand
```

Con demanda cero confirmada no se deriva `stock_maximum = 0`; esta base queda no aplicable/no determinable para el cálculo de máximo por cobertura.

---

## 21. Tolerancia de exceso M07

```text
NormalizedRate
├── parameter_id: str
├── normalized_rate: Decimal | null
├── original_unit: str
├── state
├── parameters_version: str
├── normalization_ref: str
├── source_ref
└── trace_refs
```

```text
ExcessToleranceBasis
├── kind: QUANTITY | RATE
├── quantity: NormalizedQuantity | null
├── rate: NormalizedRate | null
├── state
└── trace_refs
```

Para `RATE`:

- `parameter_id == P-STK-005`;
- versión coincidente;
- `normalized_rate >= 0`;
- `normalization_ref` obligatorio;
- STK no infiere que `10` signifique 10 % ni que `0.10` sea la escala correcta sin normalización trazada.

Cálculo:

```text
excess_tolerance_quantity = stock_maximum * normalized_rate
```

Para `QUANTITY`, la cantidad debe ser `KNOWN`, misma unidad/artículo y trazable.

---

## 22. Exceso M07

```text
ExcessInput
├── context
├── stock_reference: NormalizedQuantity
├── maximum_basis: StockMaximumBasis
└── tolerance_basis: ExcessToleranceBasis
```

Con entradas determinadas:

```text
excess_threshold = stock_maximum + excess_tolerance_quantity
excess_quantity = max(0, stock_reference - excess_threshold)
```

Estados:

```text
NO_EXCESS
WITHIN_TOLERANCE
EXCESS
UNKNOWN
NOT_EVIDENCED
CONFLICTING_DATA
```

Si `stock_reference` procede de M05, esa procedencia queda trazada y M07 no vuelve a sumar M06 ni propuesta.

STK calcula; Motor de Reglas evalúa `R-STK-002/003`.

Relaciones confirmadas únicamente:

- `P-STK-004 → R-STK-002`;
- `P-STK-004 → R-STK-003` derivada;
- `P-STK-005 → R-STK-003` derivada.

---

## 23. M08 — demanda confirmada

```text
confirmed_demand: CollectionEnvelope[ConfirmedDemandRecord]
```

Solo `KNOWN + items=()` y colección trazable permite `NO_EXISTE`.

```text
ConfirmedDemandRecord
├── confirmed_demand_id
├── order_id
├── customer_id
├── article_id
├── pending_quantity: Decimal | null
├── unit
├── order_date
├── confirmation_date
├── expected_delivery_date: date | null
├── business_status
├── applicability_state: NO_APLICABLE | APLICABLE_Y_VALIDADA | NO_VERIFICABLE
├── applicability_source_ref: str
├── source_ref
└── trace_refs
```

La aplicabilidad consumida por v0.1 debe estar trazada; un booleano aislado no basta. STK v0.1 materializa la cuantificación de la absorción y no inventa una regla adicional de reclasificación logística.

---

## 24. Alcance de asignación M08

```text
AllocationScope
├── decision_id
├── scenario_id
├── article_id
└── evaluation_date
```

Debe coincidir con `StockComputationContext`.

Entrada de absorción:

```text
ConfirmedDemandAbsorptionInput
├── context
├── allocation_scope: AllocationScope
├── excess_result
├── confirmed_demand: CollectionEnvelope[ConfirmedDemandRecord]
└── already_allocated_ids: frozenset[str]
```

Reglas:

1. `confirmed_demand_id` único en la colección;
2. IDs presentes en `already_allocated_ids` no pueden reutilizarse;
3. solo `APLICABLE_Y_VALIDADA`, mismo artículo/unidad y cantidad pendiente `KNOWN` absorben;
4. `NO_APLICABLE` y `NO_VERIFICABLE` no reducen exceso;
5. colección no `KNOWN` hace M08 no evaluable; no se infiere que no existan pedidos.

Cálculo, cuando M08 es evaluable:

```text
confirmed_order_quantity_applicable = sum(unique not-yet-allocated applicable quantities)
absorbed_excess = min(excess_quantity, confirmed_order_quantity_applicable)
residual_excess = max(0, excess_quantity - absorbed_excess)
```

Salida conserva:

- exceso original;
- absorbido;
- residual;
- IDs usados;
- `allocated_ids = already_allocated_ids ∪ ids_used`;
- estado M08 y trazas.

La operación es pura; no requiere estado interno/persistencia para hacer cumplir el alcance recibido.

M08 no reescribe M07.

---

## 25. M09 — ausencia

Se conserva una estructura equivalente a:

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

No existe imputación v0.1.

---

## 26. M10 — contradicciones

`CONFLICTING_DATA` bloquea el cálculo dependiente sin seleccionar automáticamente por recencia, máximo, mínimo, promedio, score o prioridad arbitraria.

Una resolución externa autorizada puede aportar posteriormente un valor `KNOWN` conservando referencia a la autoridad aplicada.

---

## 27. Error estructural vs incertidumbre empresarial

### Error estructural

Se rechaza técnicamente:

- Decimal no finito;
- cantidad física negativa;
- artículo/unidad incompatibles;
- `scenario_id` inconsistente;
- horizonte anterior a `evaluation_date`;
- `KNOWN` sin traza;
- colección `KNOWN` sin traza;
- `supply_identity` ausente o duplicado en M06;
- source_kind/direction incompatible;
- versión de parámetro/forecast inconsistente;
- IDs de periodos que no coinciden con la política;
- ID de demanda confirmada duplicado.

### Incertidumbre empresarial

Se representa mediante estado:

- dato desconocido/no evidenciado;
- contradicción;
- colección no evidenciada;
- fecha futura no evidenciada;
- forecast no verificable;
- aplicabilidad M08 no verificable.

---

## 28. Determinismo

- `Decimal` para cantidades/tasas;
- rechazo de `NaN`/infinitos;
- fechas explícitas;
- no dependencia de hora del sistema;
- sin redondeo empresarial implícito;
- misma entrada + mismas versiones/contexto → mismo resultado.

---

## 29. Defaults prohibidos

No se hardcodean como política:

- 15 % safety stock;
- 30/90 días cobertura;
- 10 % tolerancia;
- 12 meses consumo;
- 90 días horizonte;
- `PYE-002…005 = Sí`;
- 15 días riesgo.

La ausencia de configuración requerida no activa esos valores como fallback.

---

## 30. Interfaces de autoridad

- Quality & Trust / Evidence: STK consume, no redefine admisibilidad.
- Motor de Reglas: consume STK; STK no emite decisión de regla.
- CRC: fuera de STK.
- TCO: STK v0.1 no inyecta costes derivados.
- Decision Twin: escenarios distintos no se sobrescriben.
- MED: integra resultados sin transferir autoridad.

---

## 31. Invariantes ejecutables

1. No decisión automática.
2. C0 inmutable.
3. Ausencia ≠ cero.
4. `KNOWN` exige traza.
5. Colección `KNOWN` exige traza.
6. Artículo/unidad compatibles.
7. Stock disponible no negativo; déficit visible.
8. Vacío evidenciado ≠ ausencia.
9. Demanda solo forecast autorizado o histórico de consumo.
10. Ventana histórica coincide exactamente con periodos requeridos.
11. Ventas ≠ demanda.
12. Sin fallback de método.
13. Forecast y contexto comparten versión.
14. Forecast solo dentro de horizonte válido.
15. `supply_identity` único evita doble conteo M06.
16. Source kind y dirección son compatibles.
17. Fecha M06 vencida no se mueve al futuro.
18. Tasa de demanda no crea movimientos implícitos.
19. Propuesta exige `scenario_id` coincidente.
20. Opening projection reutiliza `StockAvailabilityResult`.
21. Sin orden intradía inventado; cierre diario agregado.
22. Incertidumbre sin fecha contamina desde `evaluation_date`.
23. Incertidumbre fechada contamina desde esa fecha.
24. Stock proyectado puede ser negativo.
25. Opening cero produce `depletion_date = evaluation_date`.
26. Mínimo incluye opening stock.
27. Coverage maximum requiere demanda diaria > 0 para derivar máximo.
28. M07 no duplica M05/M06.
29. Tolerancia tipada y normalizada con traza.
30. M08 no reutiliza IDs dentro del `AllocationScope` recibido.
31. M08 no reescribe M07.
32. Contradicción no se resuelve por heurística.
33. Sin defaults normativos.
34. Determinismo.

---

## 32. Pruebas mínimas futuras

La implementación debe cubrir al menos:

- disponibilidad, déficit y trazabilidad;
- vacío evidenciado vs ausencia de colección;
- versión de parámetro incorrecta;
- ventana histórica con ID sustituido/faltante;
- forecast versión/horizonte;
- cobertura determinada y `UNBOUNDED`;
- M06 identidad duplicada y dirección inválida;
- fecha vencida sin roll-forward;
- propuesta en escenario incorrecto;
- proyección diaria agregada, opening cero, stock negativo e incertidumbre con/sin fecha;
- máximo directo y por cobertura, incluida demanda cero;
- tolerancia por cantidad/tasa normalizada;
- estados de exceso;
- M08 colección ausente, vacío evidenciado, absorción parcial/total y reutilización bloqueada por allocation scope;
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

**Contrato v0.3:** DEPURADO tras Audit 2 v0.1.  
**Hallazgos A1…A9:** resueltos.  
**Hallazgos B1…B13:** resueltos.  
**Siguiente paso:** AUDIT 2 FINAL independiente.  
**Implementación ejecutable:** NO AUTORIZADA TODAVÍA.
