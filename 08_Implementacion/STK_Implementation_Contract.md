# EIOS — Stock & Demand Implementation Contract

## 1. Identidad

**Documento:** STK Implementation Contract  
**Versión:** 0.8  
**Estado:** DEPURADO FINAL DE IDENTIDAD — PENDIENTE DE AUDIT 2 FINAL  
**Baseline de origen:** `main @ c2bd5b9b73974426d29cc234ffda42d494e720fb`  
**Dominio:** Capa 3 — Stock / Demanda  
**Autoridad metodológica:** `01_Modelo/Stock_Demand_Methodological_Matrix.md` v1.1  
**Autoridad de entrada:** `01_Modelo/STK_Contract_Entry_Authority.md` v1.0  
**Autoridad de reglas:** `04_Reglas/Matriz_Reglas_MVP.md` v2.1  
**Dependencias:** `04_Reglas/Rule_Dependency_Matrix.md` v1.4  
**Autoridad de parametrización:** `08_Implementacion/Centro_Parametrizacion_Implementation_Contract.md` v1.2

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
├── rules_version: str
├── parameters_version: str
├── data_snapshot_id: str
├── article_id: str
├── evaluation_date: date
├── base_unit: str
├── methodology_version: str
└── forecast_version: str | null
```

`decision_id`, `scenario_id`, `rules_version`, `parameters_version` y `data_snapshot_id` se derivan sin transformación de `DecisionContext`. `forecast_version` se deriva del `StockComputationContext` y puede ser nula cuando la evaluación no consume forecast.

La identidad no crea una identidad empresarial nueva. Los consumidores posteriores exigen compatibilidad exacta, incluida `rules_version`, y preservan `forecast_version` cuando el resultado depende directa o indirectamente de una previsión autorizada.

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

`StockResultIdentity` se deriva de este contexto y conserva íntegramente la identidad canónica de `DecisionContext`.

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

Para resultado `KNOWN`: ambas magnitudes `KNOWN`; artículo = contexto; unidad = base; ambas `effective_date == evaluation_date`; trazabilidad suficiente.

```text
stock_available = max(0, stock_on_hand - stock_committed)
availability_deficit = max(0, stock_committed - stock_on_hand)
```

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

Reglas: `parameter_id == P-STK-006`; parámetro `KNOWN`, versión coincidente y aplicable a `evaluation_date`; valor entero positivo no booleano; unidad autorizada/normalizada como meses o periodos mensuales; número de periodos coincide; IDs únicos; intervalos válidos/no solapados; calendario trazable; sin generación implícita de meses; extensión futura únicamente con autoridad trazable.

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

```text
total_evidenced_consumption = sum(period.quantity)
evidenced_days_in_window = sum(period.evidenced_days)
historical_daily_demand = total_evidenced_consumption / evidenced_days_in_window
```

No se sustituye, duplica ni acorta la ventana.

```text
applicable_from = evaluation_date
applicable_to = extended_applicable_to or evaluation_date
```

Sin autoridad explícita, una tasa histórica no adquiere vigencia futura.

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

Para forecast `KNOWN`: versión no vacía; `context.forecast_version == forecast.forecast_version`; `identity.forecast_version == forecast.forecast_version`; horizonte contiene `evaluation_date`; artículo/unidad compatibles; tasa finita no negativa; traza.

Para método histórico, `DemandRateResult.forecast_version` e `identity.forecast_version` son nulos salvo que exista otra dependencia autorizada explícita; STK no inventa una versión.

Resultados posteriores que consuman un `DemandRateResult` de forecast preservan la misma `forecast_version` mediante `StockResultIdentity` y trazabilidad.

STK no calcula forecasting, no convierte ventas en demanda y no realiza fallback forecast↔histórico.

---

## 16. Cobertura M04

La tasa debe ser temporalmente aplicable:

```text
demand_rate.applicable_from <= evaluation_date <= demand_rate.applicable_to
```

Con stock y demanda `KNOWN`, identidades compatibles —incluidas versiones canónicas y `forecast_version` cuando aplica— y `daily_demand > 0`:

```text
coverage_days = stock_available / daily_demand
status = DETERMINED
```

Con demanda cero confirmada, evidenciada y aplicable: `coverage_days = null`, `status = UNBOUNDED`, razón `CONFIRMED_ZERO_DEMAND`. No se representa infinito numérico.

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

Invariantes: `movement_id` único; movimiento `KNOWN` contribuyente con cantidad finita no negativa, artículo/unidad compatibles, traza y fecha; por ser futuro sobre opening diario:

```text
evaluation_date < effective_date <= horizon_end
```

No existe cutoff intradía; un movimiento en `evaluation_date` no se incorpora por inferencia. Fuera del horizonte no se desplaza. `NOT_APPLICABLE` evidenciado no contribuye/contamina. Estados no determinados propagan incertidumbre. Tasa de demanda no genera movimientos implícitos.

M06 exige `supply_identity` estable y único; parcialidades diferenciadas; no pendiente+tránsito simultáneo; sin roll-forward de fecha vencida; recepción confirmada sale de M06; historial no suma.

`PROPOSED_PURCHASE` exige escenario coincidente, cantidad normalizada, fecha futura dentro del horizonte y traza; no presume aprobación.

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

Escenario coincidente; horizonte >= evaluación y trazable; opening `KNOWN` e identidad compatible; movimientos contribuyentes estrictamente futuros y dentro del horizonte.

Para cada fecha futura:

```text
total_inflows_date = sum(known applicable inflows)
total_outflows_date = sum(known applicable outflows)
closing_stock_date = opening_stock_date + total_inflows_date - total_outflows_date
```

Sin orden intradía; movimientos del mismo día se agregan. Saldo negativo se conserva como déficit analítico.

Incertidumbre fechada contamina desde su fecha; sin fecha, desde evaluación; `NOT_APPLICABLE` evidenciado no contamina; un dato conocido posterior no restaura `KNOWN`.

```text
minimum_projected_stock = min(opening_stock, determined daily closings)
```

Opening cero conocido → `depletion_date = evaluation_date`; si no, primera fecha futura determinada con cierre `<= 0`.

---

## 19. Frontera R-STK-001 / M02 / M03

STK entrega métricas y evidencia; no emite decisiones de compra/negociación.

STK v0.1 no calcula `stock_minimum` ni `safety_stock` mediante fórmula propia: M02/M03 exigen política cuantitativa explícita y no existe fórmula autorizada. La ausencia de valor no equivale a cero. Un valor explícitamente autorizado puede ser consumido por la capa competente conservando su autoridad/trazabilidad, sin convertirlo en fórmula STK.

`P-PYE-006 = 15 días`, `STK-002 = 15 %` y otros valores iniciales no son defaults.

---

## 20. Referencia de stock M07

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

CURRENT procede de disponibilidad, no negativo, fecha = evaluación. PROJECTED procede de punto compatible y puede ser negativo. Un negativo proyectado es déficit analítico, no inventario físico negativo.

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

Ramas exclusivas. DIRECT exige solo umbral `purpose == STOCK_MAXIMUM`, compatible y aplicable a `stock_reference.reference_date`.

COVERAGE exige `P-STK-004`, parámetro `KNOWN`, versión canónica coincidente y aplicable a la fecha de referencia, unidad días normalizada, demanda `KNOWN` con identidad compatible, demanda > 0 y fecha de referencia dentro de su intervalo de aplicabilidad.

```text
stock_maximum = coverage_maximum_days * authorized_daily_demand
```

Demanda cero no deriva máximo cero. Configuración/tasa no aplicable temporalmente no se reutiliza.

---

## 22. Tolerancia M07

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

QUANTITY: solo umbral `purpose == EXCESS_TOLERANCE`, aplicable a la referencia. RATE: solo `P-STK-005`, versión coincidente, fecha aplicable coincidente, configuration_ref/normalización trazables y tasa no negativa. No se infiere escala porcentual.

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

Con entradas determinadas, identidades/versiones compatibles y aplicables a la misma fecha:

```text
excess_threshold = stock_maximum + excess_tolerance_quantity
excess_quantity = max(0, stock_reference.value - excess_threshold)
```

Estados: `NO_EXCESS | WITHIN_TOLERANCE | EXCESS | UNKNOWN | NOT_EVIDENCED | CONFLICTING_DATA`.

PROJECTED negativo puede dar NO_EXCESS sin borrar el déficit. M07 no reañade M06/propuesta.

Únicas relaciones parámetro↔regla confirmadas: `P-STK-004 → R-STK-002`, `P-STK-004 → R-STK-003` derivada, `P-STK-005 → R-STK-003` derivada.

`ExcessResult` conserva `StockResultIdentity`, referencia/fecha, máximo, tolerancia, umbral, exceso, estado y trazas. Rules evalúa R-STK-002/003.

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

Colección mediante `CollectionEnvelope`; solo vacío KNOWN trazable significa NO_EXISTE. Solo cantidad pendiente KNOWN absorbe. APLICABLE_Y_VALIDADA exige entrega prevista evidenciada y compatible con horizonte. Cambios/cancelaciones/parcialidades requieren evidencia vigente.

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

`remaining_allocatable = pending_quantity - already_allocated_quantity`, con `0 <= allocated <= pending`. No existe prioridad implícita de reparto.

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

Compatible con identidad STK y `ExcessResult.reference_date`; horizonte explícito/trazable.

IDs únicos; ledger/plan solo IDs presentes; solo APLICABLE_Y_VALIDADA, artículo/unidad compatibles, cantidad KNOWN y entrega dentro del horizonte participan; asignación positiva no superior al saldo; colección no KNOWN hace M08 no evaluable; STK no elige reparto.

```text
total_remaining_applicable = sum(remaining_allocatable aplicable)
absorbed_excess = min(excess_quantity, total_remaining_applicable)
residual_excess = max(0, excess_quantity - absorbed_excess)
```

Plan por pedido debe sumar exactamente absorbed. Si absorbed=0, plan vacío. Si >0, plan ausente/inválido bloquea materialización por pedido. Ledger actualizado suma solo asignaciones explícitas. M08 no reescribe M07.

---

## 27. M09 — ausencia

No existe imputación STK v0.1. Ausencia no se sustituye por cero, media, último valor, estimación ni default. El resultado dependiente conserva incertidumbre y traza.

---

## 28. M10 — contradicciones

`CONFLICTING_DATA` bloquea cálculo dependiente sin selección automática por recencia, máximo, mínimo, promedio, score o prioridad. Una resolución externa autorizada conserva evidencia original y autoridad aplicada.

---

## 29. Error estructural vs incertidumbre

Se rechaza estructuralmente, entre otros: Decimal no finito; cantidad física negativa; artículo/unidad incompatibles; identidad distinta en cualquiera de sus componentes canónicos o `forecast_version` cuando aplica; escenario inconsistente; stock actual de otra fecha; horizonte inválido/sin traza; movimiento conocido no estrictamente futuro o fuera del horizonte; KNOWN sin traza; IDs duplicados; source kind/dirección incompatible; versiones/configuración efectiva incompatibles; P-STK-006 inválido; periodos incompletos; demanda fuera de vigencia; umbral con purpose/fecha incorrectos; ramas discriminadas dobles; ledger/plan M08 inválidos.

Se representa como incertidumbre empresarial: dato ausente/no evidenciado, contradicción, colección no evidenciada, forecast no verificable, configuración/umbral no disponible para fecha requerida, demanda no aplicable temporalmente, aplicabilidad M08 no verificable.

---

## 30. Determinismo

`Decimal`; rechazo NaN/infinitos; fechas explícitas; sin reloj del sistema; sin redondeo empresarial implícito; sin prioridad M08; misma entrada + misma identidad canónica + mismas versiones/configuración efectiva → mismo resultado.

---

## 31. Defaults prohibidos

No se hardcodean: 15 % safety stock; 30/90 días; 10 % tolerancia; 12 meses; 90 días de horizonte; `PYE-002…005 = Sí`; 15 días de riesgo. Ausencia de configuración no activa valores iniciales.

---

## 32. Interfaces de autoridad

- Evidence/QTG: STK consume, no redefine admisibilidad.
- Centro de Parametrización: resuelve configuración efectiva; STK consume referencia trazable para la fecha requerida.
- Motor de Reglas: consume hechos STK; STK no emite decisión R-STK.
- CRC: fuera de STK.
- TCO: no se inyectan costes derivados.
- Decision Twin: escenarios/versiones distintos no se mezclan.
- MED: integra sin transferir autoridad.
- R-STK-004: M08 sobre exceso M07; no se amplía a cobertura elevada por interpretación.

---

## 33. Invariantes ejecutables

1. No decisión automática.
2. C0 inmutable.
3. Ausencia ≠ cero.
4. KNOWN exige traza; vacío evidenciado ≠ ausencia.
5. Magnitud física ≠ umbral empresarial.
6. Identidad STK conserva `decision_id`, `scenario_id`, `rules_version`, `parameters_version`, `data_snapshot_id`.
7. `forecast_version` se preserva cuando aplica y no se inventa cuando no aplica.
8. Artículo/unidad compatibles.
9. Stock actual KNOWN corresponde a evaluation_date.
10. Stock disponible no negativo y déficit visible.
11. Demanda solo forecast autorizado o histórico de consumo.
12. Demanda conserva fecha/intervalo de aplicabilidad.
13. Histórico sin autoridad futura solo aplica a evaluation_date.
14. P-STK-006: versión + fecha efectiva + unidad autorizada.
15. Ventana histórica exacta/completa/sin duplicados.
16. Ventas ≠ demanda; sin fallback.
17. Forecast: versión/horizonte/aplicabilidad e identidad concordantes.
18. Coverage consume demanda aplicable e identidad concordante.
19. movement_id único; supply_identity evita doble conteo M06.
20. Source kind/dirección compatibles.
21. Movimientos contribuyentes estrictamente futuros respecto al opening diario.
22. No cutoff intradía inventado.
23. NOT_APPLICABLE evidenciado no contamina.
24. Tasa de demanda no crea movimientos.
25. Propuesta exige escenario coincidente.
26. Horizonte explícito/trazable.
27. Opening reutiliza disponibilidad compatible.
28. Sin orden intradía; cierre diario agregado.
29. Incertidumbre se propaga temporalmente.
30. Saldo proyectado puede ser negativo.
31. Opening cero → depletion_date=evaluation_date; mínimo incluye opening.
32. M07 distingue stock actual de saldo proyectado.
33. Umbrales directos usan AuthorizedQuantityThreshold.
34. P-STK-004/P-STK-005 solo para la fecha de referencia resuelta.
35. Coverage maximum exige demanda >0 y aplicable.
36. Ramas máximo/tolerancia exclusivas; M07 no duplica M05/M06.
37. Tolerancia RATE normalizada/trazada.
38. M08 cantidad pendiente conserva estado propio y fecha aplicable evidenciada.
39. Horizonte M08 explícito/trazable; ledger cuantitativo.
40. STK no inventa prioridad; plan suma absorción agregada.
41. M08 no reescribe M07; R-STK-004 no se amplía.
42. Contradicción no se resuelve heurísticamente.
43. M02/M03 no adquieren fórmula ni default implícito.
44. Sin defaults normativos.
45. Determinismo.

---

## 34. Pruebas mínimas futuras

Como mínimo: disponibilidad/deficit/identidad y snapshot de otra fecha; rules_version distinto; forecast_version distinto; vacío evidenciado; parámetro con versión/fecha efectiva erróneas; P-STK-006 unidad; ventana histórica duplicada/faltante/incompleta; histórico actual/extensión trazada; forecast versión/horizonte; cobertura; movimiento duplicado/mismo día/fuera de horizonte/NOT_APPLICABLE; M06 identidad/dirección/fecha; propuesta de escenario incorrecto; mezcla entre escenarios/snapshots/versiones; proyección diaria/opening cero/saldo negativo/incertidumbre; horizonte sin traza; referencia M07 actual/proyectada; umbral con propósito/fecha incorrectos; M07 por cobertura no aplicable; máximo/tolerancia; exceso; M08 cantidad/fecha/ledger/plan/absorción; M09/M10; no decisión/no defaults/reproducibilidad.

---

## 35. Exclusiones v0.1

Fuera de alcance: forecasting interno; ventas→demanda automática; tasa→calendario automático; vigencia histórica futura implícita; cutoff intradía; tolerancia temporal implícita de stock; optimización/EOQ; fórmula normativa de stock_minimum/safety_stock; imputación; resolución heurística; prioridad M08; costes TCO derivados; acciones automáticas; persistencia SQL STK; API externa; cambios C0; CRC; decisión final.

---

## 36. Estado

**Contrato v0.8:** DEPURADO FINAL DE IDENTIDAD.  
**Hallazgos A1…A9:** resueltos.  
**Hallazgos B1…B13:** resueltos.  
**Hallazgos C1…C7:** resueltos.  
**Hallazgos D1…D4:** resueltos.  
**Hallazgos E1…E3:** resueltos.  
**Hallazgos F1…F3:** resueltos.  
**Hallazgos G1…G2:** resueltos.  
**Frontera R-STK-004:** verificada sin ampliación.  
**M02/M03:** sin fórmula cuantitativa ni default implícito.  
**Siguiente paso:** AUDIT 2 FINAL independiente.  
**Implementación ejecutable:** NO AUTORIZADA TODAVÍA.
