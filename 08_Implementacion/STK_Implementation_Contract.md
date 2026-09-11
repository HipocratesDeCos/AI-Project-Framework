# EIOS — Stock & Demand Implementation Contract

## 1. Identidad

**Documento:** STK Implementation Contract  
**Versión:** 0.13  
**Estado:** DEPURADO L1…L5 — PENDIENTE DE AUDIT 2 FINAL  
**Baseline de origen:** `main @ c2bd5b9b73974426d29cc234ffda42d494e720fb`  
**Dominio:** Capa 3 — Stock / Demanda  
**Autoridad metodológica:** `01_Modelo/Stock_Demand_Methodological_Matrix.md` v1.1  
**Autoridad de entrada:** `01_Modelo/STK_Contract_Entry_Authority.md` v1.0  
**Autoridad de reglas:** `04_Reglas/Matriz_Reglas_MVP.md` v2.1  
**Dependencias:** `04_Reglas/Rule_Dependency_Matrix.md` v1.4  
**Autoridad de parametrización:** `08_Implementacion/Centro_Parametrizacion_Implementation_Contract.md` v1.2  
**Catálogo físico de parámetros:** `02_Parametros/Catalogo_Parametros_MVP_v0.3.md`

---

## 2. Propósito y frontera

Este contrato define la frontera física mínima implementable de **Stock & Demand Intelligence (STK) v0.1**.

STK materializa únicamente semántica, relaciones y cálculos previamente autorizados. No crea reglas empresariales, parámetros, defaults normativos, forecasting implícito, autoridad paralela de evidencia ni decisiones automáticas.

STK produce métricas, estados y evidencia operativa. Rules conserva `R-STK-001…004`; CRC conserva resolución de conflictos; MED conserva integración; la decisión final permanece en la persona autorizada.

La implementación ejecutable permanece bloqueada hasta superar `AUDIT 2 FINAL → CERRAR`.

---

## 3. Frontera C0 y paquete físico

STK reutiliza `DecisionContext` y no modifica `PurchaseOperation`, `Evidence`, `EvidenceValidation`, `Rule`, `Assessment` ni `Trace`.

`PurchaseOperation.quantity` no se convierte automáticamente en cantidad STK normalizada porque C0 no contiene unidad base ni ámbito operativo STK.

Paquete previsto:

```text
eios/stock/
├── __init__.py
├── models.py
└── engine.py
```

`eios.stock` puede importar contratos estables de `eios.core`; `eios.core` no depende de `eios.stock`.

---

## 4. Estados y principio `state ↔ payload`

```text
StockDataState = KNOWN | UNKNOWN | NOT_EVIDENCED | NOT_APPLICABLE | CONFLICTING_DATA
```

1. `KNOWN` exige payload material completo, valor finito cuando sea cuantitativo y trazabilidad suficiente.
2. Campos empresariales potencialmente ausentes son opcionales físicamente; nunca se fabrican valores para satisfacer el esquema.
3. Un valor singular no determinado no se presenta como cuantía verdadera. Conflictos conservan referencias de conflicto, no una selección heurística.
4. `UNKNOWN / NOT_EVIDENCED / CONFLICTING_DATA ≠ 0`.
5. `NOT_APPLICABLE` es exclusión demostrada, no ausencia.
6. Cero `KNOWN` requiere evidencia explícita.

---

## 5. Ámbito empresarial STK

```text
StockScope
├── company_id: str
└── operational_scope_id: str
```

`company_id` enlaza con el Centro de Parametrización. `operational_scope_id` identifica la organización/unidad operativa del stock y consumo. Son referencias canónicas suministradas aguas arriba.

STK no inventa jerarquías, equivalencias, redistribuciones entre centros ni mappings de ámbito.

---

## 6. Contexto e identidad

```text
StockComputationContext
├── decision_context: DecisionContext
├── scope: StockScope
├── article_id: str
├── evaluation_date: date
├── base_unit: str
├── methodology_version: str
└── forecast_version: str | null
```

```text
StockResultIdentity
├── decision_id
├── scenario_id
├── rules_version
├── parameters_version
├── data_snapshot_id
├── company_id
├── operational_scope_id
├── article_id
├── evaluation_date
├── base_unit
├── methodology_version
└── forecast_version: str | null
```

Los cinco primeros proceden sin transformación de `DecisionContext`. Los demás proceden del contexto STK. Toda composición exige afinidad exacta de identidad.

- `AUTHORIZED_FORECAST` → `forecast_version != null`.
- `HISTORICAL_CONSUMPTION` → `forecast_version == null`.

---

## 7. Colecciones evidenciadas

```text
CollectionEnvelope[T]
├── state: KNOWN | UNKNOWN | NOT_EVIDENCED | CONFLICTING_DATA
├── items: tuple[T, ...]
├── source_ref: str | null
└── trace_refs: tuple[str, ...]
```

Solo `KNOWN + items=()` con fuente/traza suficiente significa vacío evidenciado. Una colección no `KNOWN` no se suma parcialmente para producir un resultado completo.

---

## 8. Magnitud física normalizada

```text
NormalizedQuantity
├── scope: StockScope
├── article_id
├── value: Decimal | null
├── unit: str
├── source_unit: str | null
├── normalization_ref: str | null
├── state: StockDataState
├── source_ref: str | null
├── effective_date: date | null
└── trace_refs
```

`KNOWN` exige valor finito no negativo, ámbito/artículo compatibles, unidad base objetivo, fecha cuando el consumidor la requiera, fuente/traza y unidad fuente conocida. Si `source_unit != unit`, `normalization_ref` es obligatorio. Conversión no demostrada impide `KNOWN`.

---

## 9. Umbral autorizado M07

```text
AuthorizedQuantityThreshold
├── scope: StockScope
├── article_id
├── purpose: STOCK_MAXIMUM | EXCESS_TOLERANCE
├── value: Decimal | null
├── unit
├── state
├── applicable_reference_date
├── authority_ref: str | null
├── authority_version: str | null
├── source_ref: str | null
└── trace_refs
```

`KNOWN` exige valor finito no negativo, ámbito/artículo/unidad compatibles, propósito correcto, autoridad/versionado, fuente/traza y fecha exactamente aplicable a la referencia consumidora.

---

## 10. Valores M02/M03 sin fórmula STK

```text
AuthorizedStockPolicyQuantity
├── concept: STOCK_MINIMUM | SAFETY_STOCK
├── scope: StockScope
├── article_id
├── quantity: Decimal | null
├── unit
├── state
├── policy_ref: str | null
├── policy_version: str | null
├── derivation_ref: str | null
├── valid_from: date | null
├── valid_to: date | null
├── source_ref: str | null
└── trace_refs
```

`KNOWN` exige cantidad finita no negativa, unidad/ámbito/artículo compatibles, política/versión, `derivation_ref`, vigencia y fuente/traza. `derivation_ref` permite reconstruir variables/evidencias exigidas por M02/M03 sin duplicar el artefacto fuente.

`STOCK_MINIMUM` y `SAFETY_STOCK` no son equivalentes ni se componen implícitamente. STK no calcula estos valores y no valida los iniciales `STK-001/002`.

---

## 11. Parámetros e IDs físicos

IDs físicos:

```text
STK-001 … STK-006
PYE-001 … PYE-006
```

`P-STK-* / P-PYE-*` es solo notación documental de relación parámetro↔regla, nunca `parameter_id` físico.

```text
ConfiguredParameterValue
├── parameter_id
├── company_id
├── value: Decimal | int | bool | null
├── unit: str | null
├── state
├── parameters_version
├── applicable_reference_date
├── configuration_ref: str | null
├── source_ref: str | null
├── normalization_ref: str | null
└── trace_refs
```

STK consume configuración ya resuelta por el Centro de Parametrización. `KNOWN` exige compañía y versión coincidentes, configuración efectiva identificada, fecha aplicable correcta, tipo/unidad válidos y fuente/traza. Sin fallback a catálogo.

---

## 12. Frontera PYE v0.1

- `PYE-001`: operativo solo como horizonte M05.
- `PYE-002/003`: no operativos como gates v0.1; M06 decide elegibilidad mediante evidencia/estado/temporalidad.
- `PYE-004`: no operativo; v0.1 no deriva fechas desde `lead_time`.
- `PYE-005`: no transforma ventas en demanda.
- `PYE-006`: no actúa como umbral de `R-STK-001`.

Una función futura adicional requiere autoridad contractual expresa.

---

## 13. Horizonte M05 — `PYE-001`

```text
ProjectionHorizon
├── parameter: ConfiguredParameterValue  # parameter_id == "PYE-001"
├── horizon_days: int | null
├── horizon_end: date | null
├── state: StockDataState
└── trace_refs
```

`KNOWN`: parámetro efectivo en `evaluation_date`, entero positivo no booleano, unidad autorizada/normalizada a días y:

```text
horizon_end = evaluation_date + horizon_days
```

Los días son naturales y los movimientos contribuyentes cumplen `evaluation_date < effective_date <= horizon_end`. 90 días no es default.

---

## 14. Composición de compromiso de apertura

```text
StockCommitmentComponent
├── commitment_id
├── demand_segment_id: str | null
├── confirmed_demand_id: str | null
├── scope: StockScope
├── article_id
├── quantity: Decimal
├── unit
├── source_unit: str | null
├── normalization_ref: str | null
├── effective_date
├── source_ref
└── trace_refs
```

Cantidad finita no negativa, mismo ámbito/artículo/unidad/fecha que `stock_committed`, ID único y normalización demostrada. Demanda comercial confirmada requiere `confirmed_demand_id + demand_segment_id`. La suma de una composición `KNOWN` coincide exactamente con `stock_committed.value`.

---

## 15. Demanda confirmada ya incorporada

```text
IncorporatedDemandQuantity
├── confirmed_demand_id
├── quantity: Decimal
├── unit
├── demand_segment_ids: tuple[str, ...]
└── trace_refs
```

Cantidad finita no negativa, segmentos no vacíos y únicos. Se agrega por pedido conservando segmentos.

---

## 16. Disponibilidad

```text
StockAvailabilityInput
├── context
├── stock_on_hand: NormalizedQuantity
├── stock_committed: NormalizedQuantity
└── committed_components: CollectionEnvelope[StockCommitmentComponent]
```

Resultado `KNOWN` exige ambas cantidades `KNOWN`, misma identidad material, `effective_date == evaluation_date`, y composición `KNOWN`, compatible, única y de suma exacta.

```text
stock_available = max(0, stock_on_hand - stock_committed)
availability_deficit = max(0, stock_committed - stock_on_hand)
```

```text
StockAvailabilityResult
├── identity
├── stock_available: Decimal | null
├── availability_deficit: Decimal | null
├── unit
├── state
├── incorporated_confirmed_demand
└── trace_refs
```

---

## 17. Consumo M01

STK v0.1 consume periodos mensuales ya clasificados como consumo real; no transforma ventas/compras/salidas genéricas en consumo.

```text
ConsumptionPeriod
├── scope: StockScope
├── article_id
├── period_id
├── period_start
├── period_end
├── evidenced_days: int | null
├── quantity: Decimal | null
├── unit
├── state
├── methodology_version
├── aggregation_ref: str | null
├── source_ref: str | null
└── trace_refs
```

`KNOWN` exige ámbito/artículo/unidad compatibles, cantidad finita no negativa, periodo completo, días exactos, `methodology_version == context.methodology_version` y agregación/normalización/fuente reconstruibles. Cero solo con evidencia explícita.

---

## 18. Política histórica

```text
RequiredPeriodSpec(period_id, period_start, period_end)
```

```text
HistoricalDemandPolicy
├── parameter: ConfiguredParameterValue  # parameter_id == "STK-006"
├── required_periods
├── period_calendar_ref
├── extended_applicable_to: date | null
├── applicability_source_ref: str | null
├── source_ref
└── trace_refs
```

`STK-006` `KNOWN`, efectivo en `evaluation_date`, entero positivo no booleano y unidad meses/periodos mensuales autorizada. Número de periodos coincidente; IDs únicos; intervalos válidos/no solapados; calendario trazable. No se generan meses implícitamente.

---

## 19. Demanda histórica

Colección `KNOWN`, correspondencia exacta de periodos, ámbito/unidad/metodología compatibles y periodos completos:

```text
historical_daily_demand = sum(quantity) / sum(evidenced_days)
```

No se acorta, rellena ni duplica la ventana.

```text
applicable_from = evaluation_date
applicable_to = extended_applicable_to or evaluation_date
forecast_version = null
```

---

## 20. Forecast autorizado y demanda común

```text
AuthorizedForecastRate
├── scope: StockScope
├── article_id
├── daily_demand: Decimal | null
├── unit
├── state: StockDataState
├── forecast_version: str | null
├── reference_date: date
├── applicable_from: date | null
├── applicable_to: date | null
├── horizon_ref: str | null
├── source_ref: str | null
└── trace_refs
```

`KNOWN` exige mismo ámbito/artículo/unidad, tasa finita no negativa, versión no nula coincidente con contexto, intervalo válido que contenga la fecha consumidora, horizonte/fuente/traza y referencia temporal.

```text
DemandRateResult
├── identity
├── method: HISTORICAL_CONSUMPTION | AUTHORIZED_FORECAST
├── daily_demand: Decimal | null
├── unit
├── state
├── reference_date
├── applicable_from: date | null
├── applicable_to: date | null
├── applicability_source_ref: str | null
├── window_or_horizon: str | null
├── source_ref: str | null
├── forecast_version: str | null
└── trace_refs
```

Forecast `KNOWN` exige coincidencia exacta entre `context.forecast_version`, `AuthorizedForecastRate.forecast_version`, identidad y resultado. Histórico exige todas las referencias de forecast nulas.

No forecasting interno, ventas→demanda ni fallback.

**Frontera M05:** una tasa no crea automáticamente movimientos diarios. M05 solo descuenta movimientos futuros explícitamente autorizados; calendarización tasa→movimientos queda fuera de v0.1.

---

## 21. Cobertura M04

```text
CoverageState = FINITE | UNBOUNDED | UNKNOWN | NOT_EVIDENCED | CONFLICTING_DATA
```

Con stock disponible `KNOWN` y demanda `KNOWN` aplicable a `evaluation_date`:

```text
coverage_days = stock_available / daily_demand  # daily_demand > 0
```

Demanda cero confirmada → `UNBOUNDED`, valor nulo; sin infinito numérico.

```text
CoverageResult(identity, coverage_days: Decimal | null, state, demand, trace_refs)
```

M04 v0.1 calcula cobertura sobre stock disponible actual. Cualquier uso futuro sobre una referencia proyectada requerirá una extensión explícita; no se deriva desde este contrato por conveniencia.

---

## 22. Movimientos M05/M06

```text
ProjectionMovement
├── movement_id
├── supply_identity: str | null
├── supplier_id: str | null
├── supply_document_ref: str | null
├── confirmed_demand_id: str | null
├── demand_segment_id: str | null
├── scenario_id: str | null
├── scope: StockScope
├── article_id
├── direction: INFLOW | OUTFLOW
├── quantity: Decimal | null
├── unit: str | null
├── source_unit: str | null
├── normalization_ref: str | null
├── effective_date: date | null
├── state
├── source_kind: PENDING_ORDER | IN_TRANSIT | AUTHORIZED_DEMAND | RESERVATION | OTHER_AUTHORIZED_NEED | PROPOSED_PURCHASE
├── source_ref: str | null
└── trace_refs
```

Dirección:

```text
PENDING_ORDER | IN_TRANSIT | PROPOSED_PURCHASE → INFLOW
AUTHORIZED_DEMAND | RESERVATION | OTHER_AUTHORIZED_NEED → OUTFLOW
```

Movimiento `KNOWN` contribuyente: ID único, cantidad finita no negativa, ámbito/artículo/unidad compatibles, normalización/fuente/traza y `evaluation_date < effective_date <= horizon_end`.

`NOT_APPLICABLE` no contribuye ni contamina. Estados no determinados contaminan desde su fecha conocida; sin fecha demostrable, desde `evaluation_date`.

`AUTHORIZED_DEMAND` comercial confirmada exige IDs de pedido lógico y segmento. Un segmento no se duplica opening↔M05.

`PENDING_ORDER | IN_TRANSIT` `KNOWN` exige `supply_identity`, `supplier_id`, `supply_document_ref`, fecha, cantidad, unidad y evidencia. Misma cantidad no puede estar simultáneamente en ambos estados. Recepción confirmada sale M06.

`PROPOSED_PURCHASE` exige escenario coincidente, cantidad normalizada, fecha futura y traza; no presume aprobación.

---

## 23. Proyección M05

```text
StockProjectionInput
├── context
├── opening: StockAvailabilityResult
├── movements: CollectionEnvelope[ProjectionMovement]
├── horizon: ProjectionHorizon
└── scenario_id
```

Resultado completo `KNOWN`: escenario compatible, horizonte `KNOWN`, opening `KNOWN`, colección/movimientos válidos y sin duplicación de segmentos.

Para cada día futuro desde `evaluation_date + 1` hasta `horizon_end` inclusive:

```text
closing_stock_date = previous_closing_stock
                   + sum(inflows de la fecha)
                   - sum(outflows de la fecha)
```

Sin orden intradía. Saldo negativo se conserva.

```text
ProjectionPoint
├── reference_date
├── projected_stock: Decimal | null
├── state: StockDataState
├── incorporated_confirmed_demand: tuple[IncorporatedDemandQuantity, ...]
└── trace_refs
```

La composición de cada punto incluye exclusivamente demanda confirmada incorporada desde opening y movimientos M05 hasta esa fecha; no incluye segmentos futuros posteriores al punto.

```text
ProjectedDecimalMetric
├── value: Decimal | null
├── state: StockDataState
└── trace_refs
```

```text
ProjectedDateMetric
├── value: date | null
├── state: StockDataState
└── trace_refs
```

```text
StockProjectionResult
├── identity
├── horizon
├── points
├── minimum_projected_stock: ProjectedDecimalMetric
├── depletion_date: ProjectedDateMetric
├── incorporated_confirmed_demand_at_horizon: tuple[IncorporatedDemandQuantity, ...]
├── state: StockDataState
└── trace_refs
```

Incertidumbre contamina desde su fecha; datos posteriores no restauran `KNOWN` sin resolución autorizada.

`minimum_projected_stock` es `KNOWN` únicamente cuando todo el horizonte necesario para demostrar el mínimo está determinado; entonces:

```text
min(opening_stock, all daily closings)
```

No se publica un mínimo parcial como mínimo del horizonte.

`depletion_date`:

- opening cero `KNOWN` → `KNOWN`, `evaluation_date`;
- primera fecha futura determinada con cierre `<= 0` → `KNOWN` solo si no existe incertidumbre previa capaz de adelantarla;
- horizonte totalmente `KNOWN` sin agotamiento → `NOT_APPLICABLE`, valor nulo;
- incertidumbre previa a poder determinar el primer agotamiento → estado de incertidumbre, valor nulo.

---

## 24. Frontera R-STK-001 / M02 / M03

STK entrega proyección y movimientos evidenciados, no evalúa `R-STK-001`. La RDM todavía mantiene dependencias DATA/COMPONENT no individualizadas para esa regla; este contrato no inventa una semántica nueva de “próxima compra”.

M02/M03 se representan como valores autorizados sin fórmula ni consumidor directo inventado.

---

## 25. Referencia de stock M07

```text
StockReferenceValue
├── identity
├── reference_kind: CURRENT_AVAILABLE | PROJECTED
├── reference_date
├── value: Decimal | null
├── unit
├── state
├── incorporated_confirmed_demand
├── source_ref: str | null
└── trace_refs
```

`CURRENT_AVAILABLE` deriva de disponibilidad `KNOWN`, fecha evaluación y composición opening.

`PROJECTED` deriva de **un `ProjectionPoint` concreto**. Su valor/estado/composición son los de ese punto; puede ser negativo. Nunca usa la composición de fin de horizonte para una fecha intermedia.

---

## 26. Máximo y tolerancia M07

```text
StockMaximumBasis
├── mode: DIRECT_QUANTITY | COVERAGE_MAXIMUM
├── direct_threshold: AuthorizedQuantityThreshold | null
├── coverage_parameter: ConfiguredParameterValue | null
├── demand: DemandRateResult | null
└── trace_refs
```

Ramas exclusivas:

- `DIRECT_QUANTITY`: solo `direct_threshold`, purpose `STOCK_MAXIMUM`;
- `COVERAGE_MAXIMUM`: solo `coverage_parameter(parameter_id="STK-004") + demand`.

Todo `KNOWN`, mismo ámbito/artículo/unidad y aplicable a `stock_reference.reference_date`.

```text
stock_maximum = coverage_maximum_days * authorized_daily_demand
```

para rama cobertura, con demanda > 0.

```text
ExcessToleranceBasis
├── mode: QUANTITY | RATE
├── quantity_threshold: AuthorizedQuantityThreshold | null
├── rate_parameter: ConfiguredParameterValue | null
└── trace_refs
```

Ramas exclusivas:

- `QUANTITY`: threshold purpose `EXCESS_TOLERANCE`;
- `RATE`: `rate_parameter(parameter_id="STK-005")` normalizado/trazado.

```text
excess_tolerance_quantity = stock_maximum * normalized_rate
```

Sin inferencia porcentual.

---

## 27. Exceso M07

```text
ExcessState = NO_EXCESS | WITHIN_TOLERANCE | EXCESS | UNKNOWN | NOT_EVIDENCED | CONFLICTING_DATA
```

```text
excess_threshold = stock_maximum + excess_tolerance_quantity
excess_quantity = max(0, stock_reference.value - excess_threshold)
```

- `stock_reference <= stock_maximum` → `NO_EXCESS`, exceso 0.
- `stock_maximum < stock_reference <= excess_threshold` → `WITHIN_TOLERANCE`, exceso 0.
- `stock_reference > excess_threshold` → `EXCESS`.

```text
ExcessResult
├── identity
├── stock_reference: StockReferenceValue
├── stock_maximum: Decimal | null
├── excess_tolerance_quantity: Decimal | null
├── excess_threshold: Decimal | null
├── excess_quantity: Decimal | null
├── state: ExcessState
├── incorporated_confirmed_demand
└── trace_refs
```

Estados determinados (`NO_EXCESS/WITHIN_TOLERANCE/EXCESS`) exigen todas las cantidades calculadas. Estados de incertidumbre no presentan un exceso determinado.

Relaciones regla↔parámetro confirmadas: `STK-004→R-STK-002`, `STK-004→R-STK-003`, `STK-005→R-STK-003`.

---

## 28. M08 — demanda confirmada

```text
ConfirmedDemandRecord
├── confirmed_demand_id
├── order_id: str | null
├── customer_id: str | null
├── scope: StockScope
├── article_id
├── pending_quantity: NormalizedQuantity
├── order_date: date | null
├── confirmation_date: date | null
├── expected_delivery_date: date | null
├── business_status: str | null
├── applicability_state: NO_APLICABLE | APLICABLE_Y_VALIDADA | NO_VERIFICABLE
├── applicability_source_ref: str | null
├── source_ref: str | null
└── trace_refs
```

Solo colección `KNOWN` vacía/trazada significa `NO_EXISTE`.

`APLICABLE_Y_VALIDADA` exige todos los atributos mínimos M08, pending `KNOWN` del mismo ámbito y fecha, fechas comerciales coherentes y:

```text
expected_delivery_date > excess_reference_date
expected_delivery_date <= allocation_scope.horizon.horizon_end
```

`NO_VERIFICABLE` permite campos realmente ausentes nulos; no se fabrican.

---

## 29. Ledger M08 activo, evidenciado y aislado

```text
AllocationLedgerEntry
├── allocation_entry_id
├── confirmed_demand_id
├── scope: StockScope
├── article_id
├── allocated_quantity: Decimal
├── unit
├── decision_id
├── scenario_id
├── excess_reference_date
├── allocation_result_ref
└── trace_refs
```

Cantidad finita y estrictamente positiva.

```text
AllocationLedgerSnapshot
├── reference_date
├── scope: StockScope
├── article_id
├── state: KNOWN | UNKNOWN | NOT_EVIDENCED | CONFLICTING_DATA
├── entries
├── source_ref: str | null
└── trace_refs
```

Solo `KNOWN + entries=()` con fuente/traza significa cero asignaciones activas. `KNOWN` exige fecha/ámbito/artículo coincidentes con `AllocationScope`, IDs únicos y entries compatibles. Otro ámbito/artículo es error estructural.

Snapshot contiene solo asignaciones activas; histórico liberado/consumido queda aguas arriba. STK no persiste ni decide liberaciones.

---

## 30. Plan M08

```text
DemandAllocation
├── confirmed_demand_id
├── quantity_to_apply: Decimal
├── unit
├── allocation_source_ref
└── trace_refs
```

Cantidad finita y estrictamente positiva. STK no decide prioridad entre pedidos.

---

## 31. Reconciliación opening/M05/M08

Por pedido:

```text
incorporated_before_M08 = cantidad ya incorporada en stock_reference
already_allocated       = suma activa en ledger KNOWN
remaining_allocatable   = pending_quantity - incorporated_before_M08 - already_allocated
```

Misma unidad, cantidades >=0 y:

```text
incorporated_before_M08 + already_allocated <= pending_quantity
```

Si no se cumple, contradicción/inconsistencia; no suelo cero.

---

## 32. Alcance M08 y horizonte autorizado

```text
AllocationScope
├── identity: StockResultIdentity
├── scope: StockScope
├── article_id
├── evaluation_date
├── excess_reference_date
├── horizon: ProjectionHorizon
└── trace_refs
```

`horizon` debe ser `KNOWN`, compatible con contexto y derivado de `PYE-001`. No existe `horizon_end` paralelo suministrable por el llamador.

Para exceso `PROJECTED`, el horizonte es el mismo objeto/identidad temporal de la proyección origen. Para exceso actual, se usa el horizonte STK `PYE-001` del contexto.

---

## 33. Absorción M08

Solo pedidos `APLICABLE_Y_VALIDADA`, mismo ámbito/artículo/unidad, pending vigente y entrega posterior al exceso y dentro de `horizon.horizon_end` participan. Ledger/plan solo IDs presentes. Colección/ledger no `KNOWN` impide resultado validado. STK no elige reparto.

```text
total_remaining_applicable = sum(remaining_allocatable)
absorbed_excess = min(excess_quantity, total_remaining_applicable)
residual_excess = max(0, excess_quantity - absorbed_excess)
```

Si `absorbed_excess > 0`:

```text
sum(allocation_plan.quantity_to_apply) == absorbed_excess
```

```text
ConfirmedDemandAbsorptionResult
├── identity
├── excess_result: ExcessResult
├── business_state: NO_EXISTE | NO_APLICABLE | APLICABLE_Y_VALIDADA | NO_VERIFICABLE
├── total_remaining_applicable: Decimal | null
├── absorbed_excess: Decimal | null
├── residual_excess: Decimal | null
├── allocation_plan: tuple[DemandAllocation, ...]
├── resulting_ledger: AllocationLedgerSnapshot | null
└── trace_refs
```

- `NO_EXISTE`: colección de pedidos `KNOWN` vacía; exceso conocido; absorción 0 y residual = exceso.
- `NO_APLICABLE`: no existe exceso o ningún pedido conocido es aplicable; cuando el exceso está determinado, absorción 0 y residual = exceso.
- `APLICABLE_Y_VALIDADA`: fórmulas y plan/ledger válidos.
- `NO_VERIFICABLE`: no se presenta absorción/residual determinados cuando faltan evidencias necesarias.

M08 no reescribe M07.

---

## 34. M09 — ausencia

Sin imputación. Ausencia no se sustituye por cero, media, último valor, estimación o default. Cada resultado no determinado conserva estado y trazas suficientes para identificar la dependencia faltante.

---

## 35. M10 — contradicciones

`CONFLICTING_DATA` bloquea cálculo dependiente sin resolución por recencia, máximo, mínimo, promedio, score o prioridad arbitraria. Resolución externa autorizada conserva evidencia original y autoridad aplicada.

---

## 36. Error estructural vs incertidumbre

Error estructural, entre otros:

- Decimal no finito;
- `KNOWN` sin payload requerido;
- cantidad física `KNOWN` negativa;
- identidades/versiones/ámbitos incompatibles;
- IDs físicos `P-STK-* / P-PYE-*`;
- conversión no demostrada;
- M01 `KNOWN` sin reconstruibilidad;
- M02/M03 `KNOWN` sin política/derivación/vigencia;
- `PYE-001` inválido/no aplicable;
- stock actual de otra fecha;
- committed inconsistente/duplicado;
- movimiento `KNOWN` no estrictamente futuro/fuera de horizonte;
- M06 `KNOWN` sin proveedor/origen/supply identity;
- demand_segment duplicado;
- ramas discriminadas simultáneas;
- M07 umbral fuera de vigencia/autoridad;
- M08 fechas incompatibles;
- ledger `KNOWN` de otro ámbito/artículo/fecha, sin evidencia o duplicado;
- `incorporated + allocated > pending`;
- plan inválido.

Incertidumbre empresarial: ausencia/no evidencia, contradicción, colección no evidenciada, forecast/configuración/política no verificables, movimiento incompleto, demanda no aplicable o M08 no verificable.

---

## 37. Determinismo

Decimal; fechas explícitas; sin reloj; sin redondeo implícito; sin prioridad M08; sin selección automática de método; sin calendarización de tasa; misma entrada + identidad + ámbito + versiones + configuración + política + opening/M05 + ledger → mismo resultado.

---

## 38. Defaults prohibidos

No se hardcodean: 15 %, 30/90 días, 10 %, 12 meses, 90 días, booleanos `PYE-002…005`, 15 días. Ausencia de configuración no activa catálogo.

---

## 39. Interfaces de autoridad

Evidence/QTG valida evidencia; Centro de Parametrización resuelve configuración; adaptadores suministran ámbito/normalización; M02/M03 suministran valores autorizados; Rules evalúa reglas; CRC resuelve conflictos; MED integra. STK no emite decisión final.

`R-STK-001`: STK conserva proyección y movimientos; no inventa una dependencia DATA/COMPONENT adicional mientras la RDM la mantenga no demostrada individualmente.

`R-STK-004`: limitado a M08 sobre exceso M07.

---

## 40. Invariantes ejecutables

1. C0 inmutable; no decisión automática.
2. Ausencia ≠ cero; vacío evidenciado ≠ ausencia.
3. Company/scope forman parte de identidad y compatibilidad.
4. IDs físicos parámetros = `STK-* / PYE-*`.
5. Histórico forecast nulo; forecast versión exacta.
6. M02/M03 sin fórmula, con derivación/vigencia.
7. Stock actual misma fecha/ámbito; déficit visible.
8. Committed composición completa.
9. M01 ámbito/metodología/agregación reconstruible.
10. `STK-006` ventana exacta; sin fallback.
11. Coverage cero demanda → UNBOUNDED.
12. `PYE-001` gobierna horizonte; 90 no default.
13. `PYE-002…006` no adquieren función no autorizada.
14. M06 conserva supply identity/proveedor/origen y evita doble conteo.
15. Movimiento futuro estricto; sin cutoff intradía.
16. Segmentos evitan doble uso opening↔M05.
17. Tasa no crea calendario.
18. Proyección diaria; saldo negativo preservado.
19. Cada punto proyectado conserva demanda confirmada acumulada hasta su fecha.
20. Mínimo/depletion tienen estado propio; no mínimos parciales disfrazados.
21. StockReference PROJECTED usa el punto concreto y su composición.
22. M07 ramas exclusivas, vigencia y autoridad.
23. M08 horizonte = ProjectionHorizon PYE-001, no fecha paralela.
24. Ledger ausente ≠ vacío y queda aislado por ámbito/artículo.
25. M08 descuenta opening/M05/ledger y no sobreconsume pending.
26. Sin prioridad M08; plan suma absorción.
27. Contradicciones no heurísticas.
28. Sin defaults; determinismo.

---

## 41. Pruebas mínimas futuras

Cubrir: identidad C0/company/scope; IDs físicos; estados no determinados; M01 reconstruibilidad; M02/M03; disponibilidad/déficit/committed; histórico/forecast; `STK-006`; cobertura; `PYE-001`; frontera PYE; movimientos/M06/propuesta; proyección diaria y métricas con estado; composición por punto; M07 ramas/umbrales/ExcessResult; M08 horizonte común, pedido ya incorporado, ledger ausente-vacío, aislamiento scope/article, sobreconsumo, plan y resultado; M09/M10; no decisión/no defaults/reproducibilidad.

---

## 42. Exclusiones v0.1

Forecasting interno; ventas→demanda; tasa→calendario; cobertura proyectada no autorizada expresamente; vigencia futura implícita; cutoff intradía; jerarquías/redistribución entre ámbitos; optimización/EOQ; fórmula normativa M02/M03; imputación; resolución heurística; prioridad M08; persistencia ledger; SQL STK; API; cambios C0; CRC; decisión final.

---

## 43. Criterio de cierre

El contrato solo puede marcarse `CERRADO` si Audit 2 Final independiente confirma: M01…M10 implementables dentro de frontera, ausencia representable, identidad/ámbito/versionado reproducibles, no doble conteo opening/M05/M06/M08, compatibilidad C0/Parametrización/Rules/CRC/MED, cero defaults no autorizados y **cero hallazgos bloqueantes**.

Hasta entonces no está autorizada la creación de `eios/stock` ejecutable.
