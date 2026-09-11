# EIOS — Stock & Demand Implementation Contract

## 1. Identidad

**Documento:** STK Implementation Contract  
**Versión:** 0.2  
**Estado:** DEPURADO — PENDIENTE DE AUDIT 2  
**Baseline:** `main @ c2bd5b9b73974426d29cc234ffda42d494e720fb`  
**Dominio:** Capa 3 — Stock / Demanda  
**Autoridad metodológica:** `01_Modelo/Stock_Demand_Methodological_Matrix.md` v1.1  
**Autoridad de entrada:** `01_Modelo/STK_Contract_Entry_Authority.md` v1.0  
**Autoridad de reglas:** `04_Reglas/Matriz_Reglas_MVP.md` v2.1  
**Dependencias:** `04_Reglas/Rule_Dependency_Matrix.md` v1.4  
**Audit 1:** `07_Pruebas/STK_Implementation_Contract_Audit_v0.1.md`

---

## 2. Propósito y frontera

Este contrato define la frontera física mínima implementable de **Stock & Demand Intelligence (STK) v0.1**. Materializa únicamente semántica y cálculos previamente autorizados.

STK:

- calcula resultados analíticos de stock/demanda;
- conserva incertidumbre, contradicciones y trazabilidad;
- no crea reglas o parámetros empresariales;
- no hardcodea valores iniciales del catálogo;
- no crea forecasting implícito;
- no decide compras, reposiciones, cancelaciones, devoluciones o transferencias;
- no sustituye al Motor de Reglas, CRC, MED o decisor humano.

La implementación ejecutable sigue bloqueada hasta superar `AUDITAR 2 → CERRAR`.

---

## 3. Frontera con C0

STK reutiliza `DecisionContext` y no modifica:

- `InputContract` / `PurchaseOperation`;
- `DecisionContext`;
- `Evidence` / `EvidenceValidation`;
- `Rule` / `Assessment`;
- `Trace`.

`PurchaseOperation.quantity` no se considera automáticamente `proposed_quantity` normalizada porque C0 no contiene la unidad base objetivo. El impacto de una propuesta requiere una cantidad STK especializada, normalizada y trazable.

Paquete previsto:

```text
eios/stock/
├── __init__.py
├── models.py
└── engine.py
```

No se crearán dependencias circulares con `eios.core`.

---

## 4. Identidad temporal

La fecha canónica de STK es `evaluation_date`.

`as_of_date` de la metodología se materializa como `evaluation_date`; no existe una fecha paralela equivalente.

Toda entrada actual debe ser válida para esa fecha o declarar su propia vigencia. Las fechas futuras pertenecen a movimientos/proyecciones, pero el origen de la evaluación sigue siendo `evaluation_date`.

La granularidad temporal de proyección v0.1 es **fecha/día**. STK no infiere orden intradía.

---

## 5. Estados de dato STK

```text
KNOWN
UNKNOWN
NOT_EVIDENCED
NOT_APPLICABLE
CONFLICTING_DATA
```

- `KNOWN`: valor utilizable y suficientemente trazable para el cálculo;
- `UNKNOWN`: no puede determinarse;
- `NOT_EVIDENCED`: existe valor declarado, pero no posee soporte suficiente;
- `NOT_APPLICABLE`: existe evidencia de que no aplica;
- `CONFLICTING_DATA`: existen fuentes materialmente incompatibles no resueltas.

Son estados del dominio STK y no redefinen C0.

### Invariantes

- `state != KNOWN` → el valor no se presenta como determinado;
- `UNKNOWN / NOT_EVIDENCED / CONFLICTING_DATA ≠ 0`;
- un valor `KNOWN` debe conservar al menos `source_ref` o un `trace_ref`; un valor huérfano de trazabilidad no puede representarse como `KNOWN`.

---

## 6. Estado de colección

Las colecciones empresariales utilizan estado explícito:

```text
KNOWN
UNKNOWN
NOT_EVIDENCED
CONFLICTING_DATA
```

Interfaz equivalente:

```text
CollectionEnvelope[T]
├── state: CollectionState
├── items: tuple[T, ...]
├── source_ref: str | null
└── trace_refs: tuple[str, ...]
```

Reglas:

1. solo `KNOWN + items=()` significa **conjunto vacío evidenciado**;
2. una colección vacía `UNKNOWN` o `NOT_EVIDENCED` no significa inexistencia;
3. `CONFLICTING_DATA` impide utilizar la colección como completa;
4. `NO_EXISTE` de M08 solo puede producirse cuando la colección de demanda confirmada es `KNOWN` y vacía.

---

## 7. Magnitud normalizada

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

- `Decimal` finito;
- cantidades físicas conocidas no negativas;
- operaciones cuantitativas exigen mismo artículo y unidad base;
- `state != KNOWN` implica `value = null` para la magnitud no determinada;
- `KNOWN` exige trazabilidad;
- STK v0.1 no inventa conversiones de unidad.

---

## 8. Contexto técnico

```text
StockComputationContext
├── decision_context: DecisionContext
├── article_id: str
├── evaluation_date: date
├── base_unit: str
├── methodology_version: str
└── forecast_version: str | null
```

`forecast_version` es obligatorio cuando se consume forecast externo. `parameters_version` y `data_snapshot_id` proceden de `DecisionContext`.

---

## 9. Parámetros configurados

Todo valor configurable consumido por STK utiliza una interfaz equivalente a:

```text
ConfiguredParameterValue
├── parameter_id: str
├── value: Decimal | int | bool | null
├── unit: str
├── state: StockDataState
├── source_ref: str
└── trace_refs: tuple[str, ...]
```

Debe ser coherente con `DecisionContext.parameters_version`.

No existe fallback al valor inicial del catálogo cuando el valor vigente está ausente/no evidenciado.

---

## 10. Disponibilidad de stock

Entrada:

```text
StockAvailabilityInput
├── context
├── stock_on_hand: NormalizedQuantity
└── stock_committed: NormalizedQuantity
```

Precondiciones: mismo artículo/unidad y vigencia compatible con `evaluation_date`.

Con ambas magnitudes `KNOWN`:

```text
stock_available = max(0, stock_on_hand - stock_committed)
availability_deficit = max(0, stock_committed - stock_on_hand)
```

Salida:

```text
StockAvailabilityResult
├── stock_on_hand
├── stock_committed
├── stock_available: Decimal | null
├── availability_deficit: Decimal | null
├── state
└── trace_refs
```

Una entrada no determinada impide presentar `stock_available` completo. El suelo cero no oculta `availability_deficit`.

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

Reglas:

- consumo real, no ventas ni forecast;
- `evidenced_days > 0` para periodo `KNOWN`;
- periodos no solapados;
- cero solo cuando es `KNOWN` y evidenciado;
- STK no decide qué transacción fuente equivale a consumo real.

---

## 12. Demanda histórica

Métodos v0.1:

```text
AUTHORIZED_FORECAST
HISTORICAL_CONSUMPTION
```

No existen otros métodos ni fallback automático.

### 12.1 Política de ventana histórica

```text
HistoricalDemandPolicy
├── required_period_count: int
├── parameter_ref: str
├── state: StockDataState
├── source_ref: str
└── trace_refs
```

Cuando la política deriva de `P-STK-006`, `parameter_ref` debe identificarlo y el valor debe proceder de configuración vigente. El contrato no asume meses naturales ni deriva por sí mismo el número de días de un periodo empresarial.

### 12.2 Entrada

```text
HistoricalDemandInput
├── context
├── policy: HistoricalDemandPolicy
└── periods: CollectionEnvelope[ConsumptionPeriod]
```

Para un resultado `KNOWN`:

1. colección `KNOWN`;
2. `len(periods) == required_period_count`;
3. todos los periodos `KNOWN`;
4. no existen solapamientos;
5. artículo/unidad homogéneos;
6. cada periodo tiene `evidenced_days > 0`;
7. no hay contradicciones.

Cálculo:

```text
total_evidenced_consumption = sum(period.quantity)
evidenced_days_in_window = sum(period.evidenced_days)
historical_daily_demand = total_evidenced_consumption / evidenced_days_in_window
```

No se reduce silenciosamente la ventana si falta un periodo.

---

## 13. Forecast autorizado

```text
AuthorizedDemandForecast
├── article_id
├── daily_demand: Decimal | null
├── unit
├── horizon_start: date
├── horizon_end: date
├── state
├── forecast_version
├── source_ref
└── trace_refs
```

STK no calcula el forecast. Para cobertura en `evaluation_date`:

```text
horizon_start <= evaluation_date <= horizon_end
```

Si la fecha consumida queda fuera del horizonte, el forecast no es utilizable como `KNOWN` para ese cálculo.

Una proyección futura solo puede utilizar demanda explícitamente fechada/cubierta para la fecha correspondiente; la tasa media no se transforma automáticamente en movimientos.

Salida común de demanda:

```text
DemandRateResult
├── method
├── daily_demand: Decimal | null
├── unit
├── state
├── window_or_horizon
├── source_ref
├── forecast_version: str | null
└── trace_refs
```

Ventas históricas no son método autorizado v0.1.

---

## 14. Cobertura M04

Con stock disponible y demanda diaria `KNOWN`, `daily_demand > 0`:

```text
coverage_days = stock_available / daily_demand
status = DETERMINED
```

Con demanda cero `KNOWN` y evidenciada:

```text
coverage_days = null
status = UNBOUNDED
reason = CONFIRMED_ZERO_DEMAND
```

No se representa infinito y no se mantiene un segundo estado simultáneo `NOT_APPLICABLE`.

Estados de resultado:

```text
DETERMINED
UNBOUNDED
UNKNOWN
NOT_EVIDENCED
CONFLICTING_DATA
```

`CoverageResult` conserva `status`, `coverage_days`, `reason`, fuentes y trazas.

---

## 15. Movimientos de proyección M05/M06

```text
ProjectionMovement
├── movement_id: str
├── supply_identity: str | null
├── article_id: str
├── direction: INFLOW | OUTFLOW
├── quantity: Decimal | null
├── unit: str
├── effective_date: date | null
├── state
├── source_kind: PENDING_ORDER | IN_TRANSIT | AUTHORIZED_DEMAND | RESERVATION | OTHER_AUTHORIZED_NEED | PROPOSED_PURCHASE
├── source_ref: str
└── trace_refs
```

### 15.1 M06

Para `PENDING_ORDER` e `IN_TRANSIT`, `supply_identity` es obligatorio.

Una misma `supply_identity` no puede aportar simultáneamente cantidad como pendiente y tránsito. `movement_id` identifica el evento; `supply_identity` identifica la cantidad logística.

Una entrada M06 solo se proyecta cuando su fecha futura está evidenciada y:

```text
evaluation_date <= effective_date <= horizon_end
```

Si la fecha prevista está vencida (`effective_date < evaluation_date`), STK no la desplaza automáticamente al futuro: requiere una fecha vigente/evidenciada o queda no determinada para la proyección futura.

Recepción confirmada deja de pertenecer a M06. El historial no suma cantidades adicionales.

### 15.2 Cantidad propuesta

`PROPOSED_PURCHASE` exige cantidad normalizada, fecha explícita del escenario, `scenario_id` canónico y traza. STK no presume aprobación ni recepción.

### 15.3 Demanda y calendario

`DemandRateResult` no genera automáticamente `OUTFLOW`. Una salida proyectada requiere movimiento/calendario autorizado y fechado o futura extensión normativa tasa → calendario.

---

## 16. Estado de colección de movimientos

`StockProjectionInput` recibe:

```text
movements: CollectionEnvelope[ProjectionMovement]
```

Solo una colección `KNOWN` permite afirmar que el conjunto de movimientos requerido para el horizonte está completo.

Colección `UNKNOWN`, `NOT_EVIDENCED` o `CONFLICTING_DATA` impide presentar la proyección global como determinada, aunque se conserven eventos conocidos para trazabilidad.

---

## 17. Proyección M05

```text
StockProjectionInput
├── context
├── opening_stock_available: Decimal | null
├── opening_state
├── movements: CollectionEnvelope[ProjectionMovement]
├── horizon_end: date
└── scenario_id: str
```

Precondiciones:

- `scenario_id == DecisionContext.scenario_id`;
- `horizon_end >= evaluation_date`;
- artículo/unidad homogéneos.

### 17.1 Cálculo por fecha

STK no establece orden intradía por `movement_id`.

Para cada fecha, agrega antes de calcular:

```text
total_inflows_date = sum(known inflows on date)
total_outflows_date = sum(known outflows on date)
closing_stock_date = opening_stock_date + total_inflows_date - total_outflows_date
```

El cierre de una fecha alimenta la fecha siguiente.

Con granularidad diaria, STK no afirma agotamiento intradía.

El stock proyectado puede ser negativo y no se trunca.

### 17.2 Incertidumbre temporal

```text
ProjectionPoint
├── date
├── projected_stock: Decimal | null
├── state
├── inflow_total: Decimal | null
├── outflow_total: Decimal | null
└── trace_refs
```

Si una fecha contiene un movimiento requerido `UNKNOWN`, `NOT_EVIDENCED` o `CONFLICTING_DATA`, el cierre de esa fecha no es `KNOWN`. Todos los puntos posteriores dependientes permanecen no determinados; un movimiento conocido posterior no restaura certeza por sí solo.

Se conservan movimientos conocidos y no resueltos, pero no se presenta una cifra parcial como proyección completa.

### 17.3 Resultado

```text
StockProjectionResult
├── state
├── opening_stock_available
├── points
├── unresolved_movement_ids
├── minimum_projected_stock: Decimal | null
├── depletion_date: date | null
├── horizon_end
└── trace_refs
```

`minimum_projected_stock` y `depletion_date` solo se producen cuando la secuencia necesaria es determinada.

`depletion_date` es la primera **fecha de cierre diaria** con stock `<= 0`; no afirma el instante intradía.

---

## 18. Frontera R-STK-001

STK puede entregar `minimum_projected_stock`, `depletion_date`, recepción evidenciada relevante y determinabilidad. No emite `COMPRAR` ni `COMPRAR CONDICIONADO`.

La activación de `R-STK-001` pertenece al Motor de Reglas. `P-PYE-006 = 15 días` no se usa como condición oculta.

---

## 19. Máximo y tolerancia para exceso M07

Base máxima explícita:

```text
DIRECT_QUANTITY
COVERAGE_MAXIMUM
```

Una cantidad directa debe venir normalizada, autorizada y trazable; el contrato no crea un nuevo parámetro.

Con cobertura máxima:

```text
stock_maximum = coverage_maximum_days * authorized_daily_demand
```

`coverage_maximum_days` debe llegar como `ConfiguredParameterValue` vigente; no existe default.

Tolerancia explícita:

```text
QUANTITY
RATE
```

Para tasa:

```text
excess_tolerance_quantity = stock_maximum * authorized_tolerance_rate
```

La tasa se recibe ya normalizada como proporción no negativa. STK no interpreta el significado de `10` o `0.10` por magnitud numérica.

---

## 20. Exceso M07

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

- `stock_reference <= stock_maximum` → `NO_EXCESS`;
- `stock_maximum < stock_reference <= excess_threshold` → `WITHIN_TOLERANCE`;
- `stock_reference > excess_threshold` → `EXCESS`.

Si `stock_reference` procede de M05, M07 no vuelve a sumar M06 ni cantidad propuesta.

STK calcula la magnitud; Motor de Reglas evalúa `R-STK-002/003`.

Relaciones confirmadas: `P-STK-004 → R-STK-002`, `P-STK-004 → R-STK-003` derivada y `P-STK-005 → R-STK-003` derivada. No se añaden otras.

---

## 21. Demanda confirmada y M08

Colección:

```text
confirmed_demand: CollectionEnvelope[ConfirmedDemandRecord]
```

Solo `KNOWN + items=()` permite producir `NO_EXISTE`.

Registro:

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
├── source_ref
└── trace_refs
```

La clasificación de aplicabilidad debe estar evidenciada; una marca booleana aislada no basta. M08 v0.1 consume el estado trazable de aplicabilidad y materializa su **cuantificación**, sin inventar una regla logística adicional para reclasificar pedidos.

Solo `APLICABLE_Y_VALIDADA`, mismo artículo/unidad y cantidad pendiente determinada pueden absorber exceso.

IDs aplicables deben ser únicos dentro de una evaluación.

```text
confirmed_order_quantity_applicable = sum(unique applicable pending quantities)
absorbed_excess = min(excess_quantity, confirmed_order_quantity_applicable)
residual_excess = max(0, excess_quantity - absorbed_excess)
```

La salida conserva exceso original, absorción, residual e IDs utilizados. M08 no reescribe M07.

---

## 22. M09 — ausencia

La implementación conserva entradas no resueltas:

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

No existe imputación v0.1. Una futura imputación requiere política y extensión contractual.

---

## 23. M10 — contradicciones

`CONFLICTING_DATA` impide seleccionar automáticamente una fuente.

STK no usa:

- recencia;
- máximo/mínimo;
- promedio;
- score;
- prioridad arbitraria.

Una resolución externa autorizada puede entregar después un valor `KNOWN` con referencia a la autoridad aplicada. STK no crea autoridad documental paralela.

---

## 24. Error estructural vs incertidumbre empresarial

### Error estructural

Se rechaza técnicamente, por ejemplo:

- Decimal no finito;
- cantidad física negativa;
- artículo/unidad incompatible;
- `scenario_id` inconsistente;
- horizonte anterior a `evaluation_date`;
- ID técnico duplicado ambiguo;
- `supply_identity` ausente en M06.

### Incertidumbre empresarial

Se representa mediante estado, no excepción que borre significado:

- valor desconocido;
- valor no evidenciado;
- contradicción;
- colección no evidenciada;
- fecha futura no evidenciada;
- forecast no verificable.

---

## 25. Determinismo

STK usa `Decimal`, rechaza `NaN`/infinito, recibe fechas explícitas y no depende de hora de sistema.

Misma entrada + mismos datos/versiones/contexto → mismo resultado.

No existe redondeo empresarial implícito.

---

## 26. Defaults prohibidos

No se hardcodean como política:

- 15 % safety stock;
- 30/90 días cobertura;
- 10 % tolerancia;
- 12 meses consumo;
- 90 días horizonte;
- `PYE-002…005 = Sí`;
- 15 días de riesgo.

Valores requeridos se reciben desde configuración vigente y trazada a `parameters_version`. Su ausencia no activa el valor inicial como fallback.

---

## 27. Interfaces y autoridad

- **Quality & Trust / Evidence:** STK consume evidencia/estado; no redefine admisibilidad global.
- **Motor de Reglas:** consume resultados STK; STK no emite resultados decisionales.
- **CRC:** STK no resuelve conflictos entre reglas.
- **TCO:** no se inyectan costes derivados de stock en v0.1.
- **Decision Twin:** puede utilizar distintos `scenario_id`; no se sobrescriben escenarios.
- **MED:** coordina integración, sin transferir autoridad.

---

## 28. Invariantes ejecutables

1. **I-STK-01 — No decisión automática.**
2. **I-STK-02 — C0 inmutable.**
3. **I-STK-03 — Ausencia ≠ cero.**
4. **I-STK-04 — `KNOWN` exige trazabilidad.**
5. **I-STK-05 — Artículo/unidad compatibles.**
6. **I-STK-06 — Stock disponible no negativo y déficit visible.**
7. **I-STK-07 — Colección vacía solo significa ninguna entrada cuando la colección es `KNOWN`.**
8. **I-STK-08 — Demanda solo `AUTHORIZED_FORECAST` o `HISTORICAL_CONSUMPTION`.**
9. **I-STK-09 — Ventana histórica completa; no se acorta.**
10. **I-STK-10 — Ventas ≠ demanda.**
11. **I-STK-11 — Sin fallback automático de método.**
12. **I-STK-12 — Forecast válido solo dentro de su horizonte.**
13. **I-STK-13 — `supply_identity` impide doble conteo M06.**
14. **I-STK-14 — Fecha M06 vencida no se desplaza automáticamente.**
15. **I-STK-15 — Tasa de demanda no genera movimientos implícitos.**
16. **I-STK-16 — Cantidad propuesta explícita y trazable.**
17. **I-STK-17 — No orden intradía inventado; cálculo por cierre diario agregado.**
18. **I-STK-18 — Incertidumbre en una fecha contamina puntos dependientes posteriores.**
19. **I-STK-19 — Stock proyectado puede ser negativo.**
20. **I-STK-20 — M07 no duplica M05/M06.**
21. **I-STK-21 — Tolerancia tipada; no inferida por valor.**
22. **I-STK-22 — Demanda confirmada no reutilizable.**
23. **I-STK-23 — M08 no reescribe M07.**
24. **I-STK-24 — Contradicción no resuelta por heurística.**
25. **I-STK-25 — Sin defaults normativos.**
26. **I-STK-26 — Determinismo.**

---

## 29. Pruebas mínimas futuras

La implementación deberá verificar al menos:

- disponibilidad normal, compromiso igual/superior al físico y déficit visible;
- `KNOWN` sin trazabilidad rechazado;
- colección vacía evidenciada vs colección ausente;
- consumo histórico completo, incompleto y cero evidenciado;
- periodos solapados y `evidenced_days` inválidos;
- forecast dentro/fuera de horizonte;
- cobertura determinada y `UNBOUNDED`;
- artículo/unidad incompatibles;
- M06 pendiente/tránsito con misma `supply_identity`;
- fecha M06 vencida sin roll-forward;
- proyección agregada por fecha, negativa y sin orden intradía;
- incertidumbre que se propaga a puntos posteriores;
- cantidad propuesta solo si escenario la incluye;
- máximo directo/por cobertura y tolerancia cantidad/tasa;
- `NO_EXCESS`, `WITHIN_TOLERANCE`, `EXCESS`;
- M08: `NO_EXISTE` solo con colección vacía `KNOWN`, absorción nula/parcial/total y no reutilización;
- propagación M09 y bloqueo M10;
- no decisión, no defaults, reproducibilidad.

---

## 30. Exclusiones v0.1

Fuera de alcance:

- forecasting interno;
- ventas → demanda automática;
- transformación automática tasa diaria → calendario futuro;
- optimización de stock / EOQ;
- fórmulas normativas de `stock_minimum` o `safety_stock`;
- imputación;
- resolución heurística de contradicciones;
- costes TCO de exceso;
- acciones automáticas;
- persistencia SQL STK;
- API externa;
- cambios C0;
- lógica CRC;
- decisión final.

---

## 31. Estado

**Contrato v0.2:** DEPURADO tras Audit 1.  
**Hallazgos A1…A9:** incorporados.  
**Siguiente paso:** AUDITAR 2.  
**Implementación ejecutable:** NO AUTORIZADA TODAVÍA.
