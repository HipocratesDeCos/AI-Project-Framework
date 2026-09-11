# EIOS — Stock & Demand Implementation Contract

## 1. Identidad

**Documento:** STK Implementation Contract  
**Versión:** 0.7  
**Estado:** DEPURADO FINAL — PENDIENTE DE AUDIT 2 FINAL  
**Baseline de origen:** `main @ c2bd5b9b73974426d29cc234ffda42d494e720fb`  
**Dominio:** Capa 3 — Stock / Demanda  
**Autoridad metodológica:** `01_Modelo/Stock_Demand_Methodological_Matrix.md` v1.1  
**Autoridad de entrada:** `01_Modelo/STK_Contract_Entry_Authority.md` v1.0  
**Autoridad de reglas:** `04_Reglas/Matriz_Reglas_MVP.md` v2.1  
**Dependencias:** `04_Reglas/Rule_Dependency_Matrix.md` v1.4  
**Autoridad de parametrización:** `08_Implementacion/Centro_Parametrizacion_Implementation_Contract.md` v1.2  
**Auditorías:** `STK_Implementation_Contract_Audit_v0.1.md`, `STK_Implementation_Contract_Audit_2_v0.1.md`, `STK_Implementation_Contract_Audit_2_Final_v0.2.md`, `v0.3.md`, `v0.4.md`, `v0.5.md`

---

## 2. Propósito y frontera

Este contrato define la frontera física mínima implementable de **Stock & Demand Intelligence (STK) v0.1**. Materializa exclusivamente semántica, relaciones y cálculos previamente autorizados.

STK no crea reglas empresariales, parámetros, defaults normativos, forecasting implícito, una autoridad paralela de evidencia ni decisiones automáticas. El Motor de Reglas conserva R-STK-001…004; CRC conserva resolución de conflictos; MED conserva integración; la autoridad decisional final permanece en la persona autorizada.

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

No se introducen dependencias circulares con `eios.core`.

---

## 4. Identidad y temporalidad

La fecha canónica STK es `evaluation_date`. La proyección v0.1 tiene granularidad **diaria**; no existe autoridad para inferir secuencia intradía.

Todo resultado intermedio reutilizable conserva:

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

La identidad se deriva de `DecisionContext` y del contexto STK; no crea identidad empresarial nueva. Los consumidores posteriores exigen compatibilidad exacta salvo relación temporal expresamente definida en este contrato.

---

## 5. Estados STK

```text
KNOWN
UNKNOWN
NOT_EVIDENCED
NOT_APPLICABLE
CONFLICTING_DATA
```

- `KNOWN`: valor utilizable y suficientemente evidenciado.
- `UNKNOWN`: valor no determinable.
- `NOT_EVIDENCED`: valor declarado sin evidencia suficiente.
- `NOT_APPLICABLE`: evidencia de que la magnitud no aplica.
- `CONFLICTING_DATA`: fuentes materialmente incompatibles no resueltas.

Invariantes:

1. `state != KNOWN` no presenta un valor numérico como determinado.
2. `UNKNOWN / NOT_EVIDENCED / CONFLICTING_DATA ≠ 0`.
3. Todo dato `KNOWN` exige `source_ref` o al menos un `trace_ref`.
4. Estos estados no redefinen los estados de C0.

---

## 6. Colecciones empresariales

```text
CollectionEnvelope[T]
├── state: KNOWN | UNKNOWN | NOT_EVIDENCED | CONFLICTING_DATA
├── items: tuple[T, ...]
├── source_ref: str | null
└── trace_refs: tuple[str, ...]
```

Solo `KNOWN + items=()` con trazabilidad significa conjunto vacío evidenciado. Una colección vacía desconocida/no evidenciada no significa inexistencia. `CONFLICTING_DATA` impide tratarla como completa.

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

Representa **magnitud física**, no saldo analítico ni umbral empresarial.

Reglas: Decimal finito; cantidad física `KNOWN` no negativa; mismo artículo/unidad para operar; `state != KNOWN → value = null`; `KNOWN` exige traza; no existe conversión implícita de unidad.

---

## 8. Umbral cuantitativo autorizado

Para no confundir política con inventario físico:

```text
AuthorizedQuantityThreshold
├── article_id: str
├── purpose: STOCK_MAXIMUM | EXCESS_TOLERANCE
├── value: Decimal | null
├── unit: str
├── state: StockDataState
├── applicable_reference_date: date
├── source_ref: str
└── trace_refs: tuple[str, ...]
```

Reglas:

1. `KNOWN` exige valor finito, no negativo y trazabilidad.
2. Artículo y unidad deben ser compatibles con el cálculo consumidor.
3. `purpose` debe coincidir con el uso declarado.
4. `applicable_reference_date` debe coincidir exactamente con `stock_reference.reference_date`.
5. Un umbral vigente para una fecha no adquiere vigencia futura por inferencia.
6. Este tipo no representa stock existente ni crea un parámetro nuevo.

---

## 9. Contexto STK

```text
StockComputationContext
├── decision_context: DecisionContext
├── article_id: str
├── evaluation_date: date
├── base_unit: str
├── methodology_version: str
└── forecast_version: str | null
```

`parameters_version` y `data_snapshot_id` se reutilizan de `DecisionContext`.

---

## 10. Parámetros configurados y vigencia

STK consume configuración ya resuelta por la autoridad de parametrización; no reimplementa `valid_from/valid_to`, zonas horarias ni selección de configuraciones.

```text
ConfiguredParameterValue
├── parameter_id: str
├── value: Decimal | int | bool | null
├── unit: str
├── state: StockDataState
├── parameters_version: str
├── applicable_reference_date: date
├── configuration_ref: str
├── source_ref: str
├── normalization_ref: str | null
└── trace_refs: tuple[str, ...]
```

Un parámetro `KNOWN` solo puede consumirse si:

- `parameters_version == DecisionContext.parameters_version`;
- `configuration_ref` identifica la configuración/autorización efectiva resuelta aguas arriba;
- `applicable_reference_date` coincide con la fecha para la que el cálculo exige el parámetro;
- tipo/unidad son compatibles y cualquier normalización necesaria es trazable.

STK no reutiliza silenciosamente una configuración actual para una fecha futura y no usa valores iniciales del catálogo como fallback.

---

## 11. Disponibilidad de stock

```text
StockAvailabilityInput
├── context: StockComputationContext
├── stock_on_hand: NormalizedQuantity
└── stock_committed: NormalizedQuantity
```

Para resultado `KNOWN`:

- ambas magnitudes `KNOWN`;
- artículo = `context.article_id`;
- unidad = `context.base_unit`;
- ambas `effective_date == context.evaluation_date`;
- trazabilidad suficiente.

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

El déficit no se oculta. STK v0.1 no inventa tolerancia de antigüedad para snapshots.

---

## 12. Consumo M01

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

`KNOWN` exige consumo real, cantidad no negativa, periodo trazable, `period_start <= period_end` y periodo completo. Ventas y forecast no son consumo. Cero solo existe cuando está explícitamente evidenciado.

---

## 13. Política histórica de demanda

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

1. `parameter.parameter_id == P-STK-006`.
2. Parámetro `KNOWN`, versión coincidente y `parameter.applicable_reference_date == context.evaluation_date`.
3. Valor normalizado entero positivo, no booleano.
4. Unidad autorizada/normalizada como meses o número de periodos mensuales; si hay conversión, `normalization_ref` es obligatorio.
5. `len(required_periods)` coincide con el valor normalizado.
6. IDs únicos, intervalos válidos y no solapados.
7. `period_calendar_ref` identifica la fuente de los periodos concretos.
8. STK no presupone meses naturales ni genera IDs.
9. Si `extended_applicable_to` está presente, debe ser `>= evaluation_date` y `applicability_source_ref` es obligatorio.
10. Sin autoridad explícita, una tasa histórica no adquiere vigencia futura.

---

## 14. Demanda histórica

```text
HistoricalDemandInput
├── context: StockComputationContext
├── policy: HistoricalDemandPolicy
└── periods: CollectionEnvelope[ConsumptionPeriod]
```

Resultado numérico `KNOWN` solo con colección `KNOWN`, IDs únicos, correspondencia uno-a-uno contra `required_periods`, límites exactos, todos los periodos `KNOWN`, sin solapamientos, artículo/unidad homogéneos y:

```text
evidenced_days == (period_end - period_start).days + 1
```

Cálculo:

```text
total_evidenced_consumption = sum(period.quantity)
evidenced_days_in_window = sum(period.evidenced_days)
historical_daily_demand = total_evidenced_consumption / evidenced_days_in_window
```

No se sustituye, duplica ni acorta la ventana.

Aplicabilidad conservadora:

```text
applicable_from = context.evaluation_date
applicable_to = policy.extended_applicable_to or context.evaluation_date
```

La extensión futura solo existe con referencia de autoridad trazable.

---

## 15. Demanda común y forecast autorizado

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

Forecast de entrada:

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
└── trace_refs
```

Para forecast `KNOWN`: versión no vacía y coincidente con contexto; `horizon_start <= evaluation_date <= horizon_end`; artículo/unidad compatibles; tasa finita no negativa; traza.

El `DemandRateResult` de forecast conserva el horizonte como intervalo de aplicabilidad. STK no calcula forecasting, no convierte ventas en demanda y no realiza fallback forecast↔histórico.

---

## 16. Cobertura M04

La tasa debe ser temporalmente aplicable:

```text
demand_rate.applicable_from <= evaluation_date <= demand_rate.applicable_to
```

Con stock y demanda `KNOWN` y `daily_demand > 0`:

```text
coverage_days = stock_available / daily_demand
status = DETERMINED
```

Con demanda cero confirmada, evidenciada y aplicable:

```text
coverage_days = null
status = UNBOUNDED
reason = CONFIRMED_ZERO_DEMAND
```

No se representa infinito numérico. Estados: `DETERMINED | UNBOUNDED | UNKNOWN | NOT_EVIDENCED | CONFLICTING_DATA`.

---

## 17. Movimientos M05/M06

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
- movimiento `KNOWN` contribuyente: cantidad finita no negativa, artículo/unidad compatibles, traza y fecha no nula;
- por tratarse de movimientos futuros sobre stock de apertura diario:

```text
evaluation_date < effective_date <= horizon_end
```

- un movimiento fechado en `evaluation_date` no se incorpora por inferencia; v0.1 no posee cutoff intradía;
- movimiento conocido fuera del horizonte no se desplaza ni suma silenciosamente;
- `NOT_APPLICABLE` evidenciado no contribuye y no contamina;
- `UNKNOWN`, `NOT_EVIDENCED`, `CONFLICTING_DATA` propagan incertidumbre;
- una tasa de demanda no genera movimientos implícitos.

Para `PENDING_ORDER`/`IN_TRANSIT`: `supply_identity` obligatorio y único; una parcialidad distinta exige identidad de segmento distinta; una identidad no coexiste en ambos estados; fecha vencida no se desplaza; recepción confirmada sale de M06; historial no suma cantidad.

Para `PROPOSED_PURCHASE`: `scenario_id` obligatorio y coincidente; cantidad normalizada, fecha futura dentro del horizonte y traza. No se presume aprobación ni recepción.

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

Precondiciones: escenario coincidente; `horizon_end >= evaluation_date`; horizonte trazable; opening con identidad compatible y `KNOWN`; todos los movimientos `KNOWN` contribuyentes son estrictamente posteriores a `evaluation_date` y no posteriores a `horizon_end`.

No existe orden intradía. Para cada fecha futura:

```text
total_inflows_date = sum(known applicable inflows)
total_outflows_date = sum(known applicable outflows)
closing_stock_date = opening_stock_date + total_inflows_date - total_outflows_date
```

Movimientos del mismo día se agregan antes del cierre. Saldo proyectado negativo se conserva como déficit analítico.

Incertidumbre: movimiento requerido desconocido con fecha conocida contamina desde esa fecha; sin fecha, desde `evaluation_date`; `NOT_APPLICABLE` evidenciado no contamina; un movimiento conocido posterior no restaura `KNOWN`.

Mínimo:

```text
minimum_projected_stock = min(opening_stock, determined daily closings)
```

Si opening `KNOWN == 0`, `depletion_date = evaluation_date`; si no, primera fecha futura determinada con cierre `<= 0`.

---

## 19. Frontera R-STK-001

STK entrega `minimum_projected_stock`, `depletion_date`, recepciones relevantes y estados. No emite decisiones de compra/negociación.

STK v0.1 **no calcula `stock_minimum` ni `safety_stock` mediante una fórmula propia** porque no existe autoridad cuantitativa cerrada para hacerlo. Si una regla consume un mínimo explícitamente autorizado, su autoridad y trazabilidad se conservan fuera de cualquier fórmula implícita STK. `P-PYE-006 = 15 días` no se usa como condición oculta ni default.

---

## 20. Referencia de stock para M07

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

`CURRENT_AVAILABLE` procede de disponibilidad actual, `value >= 0` y fecha = evaluación. `PROJECTED` procede de `ProjectionPoint` compatible y puede ser negativo. El negativo proyectado representa déficit analítico, no cantidad física negativa.

---

## 21. Base de stock máximo M07

```text
StockMaximumBasis
├── kind: DIRECT_QUANTITY | COVERAGE_MAXIMUM
├── direct_threshold: AuthorizedQuantityThreshold | null
├── coverage_maximum: ConfiguredParameterValue | null
├── demand_rate: DemandRateResult | null
├── state: StockDataState
├── source_ref: str
└── trace_refs: tuple[str, ...]
```

Ramas exclusivas:

- `DIRECT_QUANTITY` → solo `direct_threshold` presente y `purpose == STOCK_MAXIMUM`.
- `COVERAGE_MAXIMUM` → solo `coverage_maximum + demand_rate` presentes.

En ambas ramas la autoridad debe ser aplicable a `stock_reference.reference_date`.

Para `COVERAGE_MAXIMUM`:

- `coverage_maximum.parameter_id == P-STK-004`;
- parámetro `KNOWN`, versión coincidente y `coverage_maximum.applicable_reference_date == stock_reference.reference_date`;
- unidad temporal normalizada en días;
- demanda `KNOWN`, identidad compatible, `daily_demand > 0`;
- `demand_rate.applicable_from <= stock_reference.reference_date <= demand_rate.applicable_to`.

Solo entonces:

```text
stock_maximum = coverage_maximum_days * authorized_daily_demand
```

Con demanda cero confirmada no se deriva máximo cero. Una tasa/configuración no demostrablemente aplicable a la fecha de referencia no se reutiliza.

---

## 22. Tolerancia de exceso M07

```text
NormalizedRate
├── parameter_id: str
├── normalized_rate: Decimal | null
├── original_unit: str
├── state: StockDataState
├── parameters_version: str
├── applicable_reference_date: date
├── configuration_ref: str
├── normalization_ref: str
├── source_ref: str
└── trace_refs: tuple[str, ...]
```

```text
ExcessToleranceBasis
├── kind: QUANTITY | RATE
├── quantity_threshold: AuthorizedQuantityThreshold | null
├── rate: NormalizedRate | null
├── state: StockDataState
└── trace_refs: tuple[str, ...]
```

Ramas exclusivas:

- `QUANTITY` → solo `quantity_threshold`, con `purpose == EXCESS_TOLERANCE` y fecha aplicable = `stock_reference.reference_date`.
- `RATE` → solo `rate`.

Para `RATE`: `parameter_id == P-STK-005`; versión coincidente; `applicable_reference_date == stock_reference.reference_date`; `configuration_ref` trazable; tasa normalizada no negativa; `normalization_ref` obligatorio. No se infiere si `10` significa 10 % ni si `0.10` es la escala correcta.

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

Con entradas determinadas y aplicables a la misma fecha:

```text
excess_threshold = stock_maximum + excess_tolerance_quantity
excess_quantity = max(0, stock_reference.value - excess_threshold)
```

Estados: `NO_EXCESS | WITHIN_TOLERANCE | EXCESS | UNKNOWN | NOT_EVIDENCED | CONFLICTING_DATA`.

Un `PROJECTED` negativo puede producir `NO_EXCESS` sin convertir el déficit en cero. Si la referencia procede de M05, M07 no vuelve a sumar M06/propuesta.

Relaciones parámetro↔regla confirmadas únicamente:

- `P-STK-004 → R-STK-002`;
- `P-STK-004 → R-STK-003` derivada;
- `P-STK-005 → R-STK-003` derivada.

`ExcessResult` conserva identidad, `reference_date`, referencia, máximo, tolerancia, umbral, exceso, estado y trazas. STK calcula; Rules evalúa R-STK-002/003.

---

## 24. M08 — demanda confirmada

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

La colección utiliza `CollectionEnvelope`. Solo `KNOWN + items=()` trazable permite `NO_EXISTE`.

Solo cantidad pendiente `KNOWN` absorbe. `APLICABLE_Y_VALIDADA` exige fecha prevista no nula, evidenciada y compatible con el horizonte. Booleanos aislados no constituyen evidencia; cambios/cancelaciones/parcialidades requieren evidencia vigente.

---

## 25. Ledger y plan M08

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

```text
remaining_allocatable = pending_quantity.value - already_allocated_quantity
```

Debe cumplirse `0 <= already_allocated_quantity <= pending_quantity.value`. No existe prioridad implícita por fecha, cliente, ID, tamaño o recencia.

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

Debe ser compatible con la identidad STK y `ExcessResult.reference_date`; horizonte explícito y trazable.

Input: contexto, scope, exceso, colección de demanda confirmada, ledger y plan.

Reglas: IDs únicos; ledger/plan solo referencian demanda presente; solo `APLICABLE_Y_VALIDADA`, mismo artículo/unidad, cantidad `KNOWN` y entrega dentro del horizonte participan; cada asignación positiva y no mayor que el saldo disponible; colección no `KNOWN` hace M08 no evaluable; STK no elige reparto.

Cálculo agregado:

```text
total_remaining_applicable = sum(remaining_allocatable aplicable)
absorbed_excess = min(excess_quantity, total_remaining_applicable)
residual_excess = max(0, excess_quantity - absorbed_excess)
```

Para materializar reparto por pedido:

```text
sum(allocation_plan.quantity_to_apply) == absorbed_excess
```

Si absorbed = 0, plan vacío. Si absorbed > 0, un plan ausente/incompleto/sobreasignado impide materializar reparto; STK no lo inventa.

M08 conserva exceso original, total aplicable, absorbido, residual, asignaciones, ledger actualizado, identidad y trazas; no reescribe M07.

---

## 27. M09 — ausencia

No existe imputación STK v0.1. Un dato ausente no se sustituye por cero, media, último valor, estimación o default. La salida dependiente conserva incertidumbre y trazabilidad del dato/fuente esperada.

---

## 28. M10 — contradicciones

`CONFLICTING_DATA` bloquea el cálculo dependiente sin seleccionar por recencia, máximo, mínimo, promedio, score o prioridad arbitraria. Una resolución externa autorizada conserva evidencia original y autoridad aplicada.

---

## 29. Error estructural vs incertidumbre empresarial

### Error estructural

Se rechaza técnicamente, entre otros:

- Decimal no finito;
- cantidad física negativa;
- artículo/unidad incompatibles;
- identidad de resultado incompatible;
- `scenario_id` inconsistente;
- stock actual `KNOWN` de otra fecha;
- horizonte inválido/sin traza;
- movimiento `KNOWN` contribuyente con fecha `<= evaluation_date` o `> horizon_end`;
- `KNOWN` sin traza;
- `movement_id` o `supply_identity` duplicado donde está prohibido;
- source kind/dirección incompatible;
- versión de parámetro/forecast inconsistente;
- parámetro resuelto para una fecha distinta de la requerida;
- P-STK-006 con unidad no autorizada/normalizada;
- periodos históricos duplicados/incompletos/incompatibles;
- demanda fuera de vigencia requerida;
- umbral autorizado con purpose/fecha incompatibles;
- ramas discriminadas simultáneamente pobladas;
- ID de demanda confirmada duplicado;
- ledger/plan M08 inválidos.

### Incertidumbre empresarial

Se representa mediante estado: dato desconocido/no evidenciado; contradicción; colección no evidenciada; forecast no verificable; configuración/umbral no disponible para la fecha requerida; demanda no aplicable temporalmente; aplicabilidad M08 no verificable.

---

## 30. Determinismo

`Decimal`; rechazo NaN/infinitos; fechas explícitas; sin reloj del sistema; sin redondeo empresarial implícito; sin prioridad M08; misma entrada + misma identidad/versiones/configuración efectiva → mismo resultado.

---

## 31. Defaults prohibidos

No se hardcodean: 15 % safety stock; 30/90 días; 10 % tolerancia; 12 meses; 90 días de horizonte; `PYE-002…005 = Sí`; 15 días de riesgo. La ausencia de configuración requerida no activa esos valores.

---

## 32. Interfaces de autoridad

- Evidence/QTG: STK consume, no redefine admisibilidad.
- Centro de Parametrización: resuelve la configuración efectiva; STK consume una referencia trazable para la fecha requerida y no reimplementa su vigencia.
- Motor de Reglas: consume hechos STK; STK no emite decisiones de R-STK.
- CRC: fuera de STK.
- TCO: STK v0.1 no inyecta costes derivados.
- Decision Twin: escenarios distintos no se mezclan.
- MED: integra sin transferir autoridad.
- R-STK-004: STK consume M08 sobre exceso M07; no amplía la excepción a cobertura elevada por interpretación.

---

## 33. Invariantes ejecutables

1. No decisión automática.
2. C0 inmutable.
3. Ausencia ≠ cero.
4. `KNOWN` y colección `KNOWN` exigen traza.
5. Vacío evidenciado ≠ ausencia.
6. Magnitud física ≠ umbral empresarial.
7. Artículo/unidad compatibles.
8. Identidad STK preservada y validada.
9. Stock actual `KNOWN` corresponde a `evaluation_date`.
10. Stock disponible no negativo y déficit visible.
11. Demanda solo forecast autorizado o histórico de consumo.
12. Demanda conserva fecha de referencia e intervalo de aplicabilidad.
13. Histórico sin autoridad futura solo aplica a `evaluation_date`.
14. P-STK-006: versión + fecha efectiva + unidad autorizada.
15. Ventana histórica exacta, completa y sin duplicados.
16. Ventas ≠ demanda; sin fallback.
17. Forecast: versión/horizonte/aplicabilidad.
18. Coverage consume demanda aplicable.
19. `movement_id` único.
20. `supply_identity` evita doble conteo M06.
21. Source kind/dirección compatibles.
22. Movimientos proyectivos contribuyentes son estrictamente futuros respecto al opening diario.
23. No cutoff intradía inventado.
24. `NOT_APPLICABLE` evidenciado no contamina.
25. Tasa de demanda no crea movimientos.
26. Propuesta exige escenario coincidente.
27. Horizonte explícito y trazable.
28. Opening reutiliza disponibilidad compatible.
29. Sin orden intradía; cierre diario agregado.
30. Incertidumbre se propaga desde su fecha o desde evaluación si fecha desconocida.
31. Saldo proyectado puede ser negativo.
32. Opening cero → depletion_date = evaluation_date.
33. Mínimo incluye opening.
34. M07 distingue stock actual de saldo proyectado.
35. Umbrales directos usan `AuthorizedQuantityThreshold`, no `NormalizedQuantity`.
36. P-STK-004/P-STK-005 se consumen solo si están resueltos para `stock_reference.reference_date`.
37. Coverage maximum exige demanda > 0 y aplicable a la fecha de referencia.
38. Ramas máximo/tolerancia exclusivas.
39. M07 no duplica M05/M06.
40. Tolerancia RATE normalizada y trazada.
41. M08 cantidad pendiente conserva estado propio.
42. Pedido M08 aplicable exige fecha evidenciada.
43. Horizonte M08 explícito/trazable.
44. Ledger M08 cuantitativo.
45. STK no inventa prioridad de asignación.
46. Plan suma exactamente absorción agregada.
47. M08 no reescribe M07.
48. R-STK-004 no se amplía fuera de M08/M07.
49. Contradicción no se resuelve heurísticamente.
50. Sin defaults normativos.
51. Determinismo.

---

## 34. Pruebas mínimas futuras

La implementación cubrirá como mínimo:

- disponibilidad/deficit/identidad y snapshot de otra fecha rechazado;
- vacío evidenciado vs ausencia;
- parámetro con versión o `applicable_reference_date` incorrectos;
- P-STK-006 con unidad no normalizada;
- ventana histórica con duplicado, sustitución, falta, intervalo o días incompletos;
- histórico limitado a evaluation_date y extensión trazada;
- forecast versión/horizonte/aplicabilidad;
- cobertura determinada/UNBOUNDED;
- movimiento duplicado, mismo día que opening, fuera de horizonte, NOT_APPLICABLE, M06 doble identidad/dirección inválida/fecha vencida;
- propuesta en escenario incorrecto;
- mezcla entre escenarios/snapshots rechazada;
- proyección diaria, opening cero, saldo negativo e incertidumbre;
- horizonte sin traza;
- referencia M07 actual/proyectada;
- `AuthorizedQuantityThreshold` con propósito/fecha incorrectos;
- M07 por cobertura con parámetro/demanda no aplicable a fecha de referencia;
- máximo directo/por cobertura y demanda cero;
- tolerancia por cantidad/tasa;
- estados de exceso;
- M08 cantidad desconocida, fecha no verificable, ledger parcial, plan inválido, absorción parcial/total y ausencia de prioridad implícita;
- M09/M10;
- no decisión, no defaults y reproducibilidad.

---

## 35. Exclusiones v0.1

Fuera de alcance: forecasting interno; ventas→demanda automática; tasa→calendario automático; vigencia futura implícita del histórico; cutoff intradía; tolerancia temporal implícita de stock; optimización/EOQ; fórmula normativa de `stock_minimum` o `safety_stock`; imputación; resolución heurística; prioridad M08; costes TCO derivados; acciones automáticas; persistencia SQL STK; API externa; cambios C0; CRC; decisión final.

---

## 36. Estado

**Contrato v0.7:** DEPURADO FINAL tras Audit 2 Final v0.5.  
**Hallazgos A1…A9:** resueltos.  
**Hallazgos B1…B13:** resueltos.  
**Hallazgos C1…C7:** resueltos.  
**Hallazgos D1…D4:** resueltos.  
**Hallazgos E1…E3:** resueltos.  
**Hallazgos F1…F3:** resueltos.  
**Frontera R-STK-004:** verificada sin ampliación de alcance.  
**Siguiente paso:** AUDIT 2 FINAL independiente sobre v0.7.  
**Implementación ejecutable:** NO AUTORIZADA TODAVÍA.
