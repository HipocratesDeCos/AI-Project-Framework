# EIOS — Stock & Demand Implementation Contract

## 1. Identidad

**Documento:** STK Implementation Contract  
**Versión:** 0.14  
**Estado:** DEPURADO M1…M4 — PENDIENTE DE AUDIT 2 FINAL  
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

## 4. Estados, incidencias y principio `state ↔ payload`

```text
StockDataState = KNOWN | UNKNOWN | NOT_EVIDENCED | NOT_APPLICABLE | CONFLICTING_DATA
```

```text
DataIssueRef
├── issue_id: str
├── issue_type: MISSING_DATA | CONTRADICTION
├── issue_record_ref: str
├── evidence_refs: tuple[str, ...]
└── trace_refs: tuple[str, ...]
```

`issue_record_ref` referencia un artefacto aguas arriba que conserva el detalle exigido por M09/M10. STK no crea persistencia paralela ni resuelve la incidencia desde esta referencia.

**Contrato común de estado:** toda estructura de este contrato que exponga `state: StockDataState` incorpora además, aunque se omita gráficamente en diagramas posteriores para evitar repetición:

```text
issue_refs: tuple[DataIssueRef, ...]
trace_refs: tuple[str, ...]
```

Reglas transversales:

1. `KNOWN` exige payload material completo, valor finito cuando sea cuantitativo y trazabilidad suficiente.
2. Campos empresariales potencialmente ausentes son opcionales físicamente; nunca se fabrican valores para satisfacer el esquema.
3. Un valor singular no determinado no se presenta como cuantía verdadera.
4. `UNKNOWN / NOT_EVIDENCED / CONFLICTING_DATA ≠ 0`.
5. `NOT_APPLICABLE` es exclusión demostrada, no ausencia.
6. Cero `KNOWN` requiere evidencia explícita.
7. Todo `CONFLICTING_DATA` exige al menos un `DataIssueRef(issue_type=CONTRADICTION)`; si la contradicción está sin resolver, ese registro conserva al menos dos `evidence_refs` distintos.
8. `UNKNOWN / NOT_EVIDENCED` puede incorporar `MISSING_DATA`; cuando existe un registro de ausencia, su referencia se conserva.
9. Una resolución autorizada posterior no elimina la incidencia histórica ni convierte la contradicción anterior en inexistente.
10. `DataIssueRef` gobierna incidencias de datos/evidencia STK; no sustituye CRC ni la Matriz de Autoridad Documental.

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
├── issue_refs: tuple[DataIssueRef, ...]
└── trace_refs: tuple[str, ...]
```

Solo `KNOWN + items=()` con fuente/traza suficiente significa vacío evidenciado. Una colección no `KNOWN` no se suma parcialmente para producir un resultado completo. `CONFLICTING_DATA` cumple el contrato M10 de §4.

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
├── issue_refs: tuple[DataIssueRef, ...]
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
├── issue_refs
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
├── issue_refs
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
├── issue_refs
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
├── parameter: ConfiguredParameterValue
├── horizon_days: int | null
├── horizon_end: date | null
├── state: StockDataState
├── issue_refs
└── trace_refs
```

`KNOWN`: `parameter_id == "PYE-001"`, parámetro efectivo en `evaluation_date`, entero positivo no booleano, unidad autorizada/normalizada a días y:

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
├── issue_refs
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
├── issue_refs
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
├── parameter: ConfiguredParameterValue
├── required_periods
├── period_calendar_ref
├── extended_applicable_to: date | null
├── applicability_source_ref: str | null
├── source_ref
└── trace_refs
```

`parameter_id == "STK-006"`. Parámetro `KNOWN`, efectivo en `evaluation_date`, entero positivo no booleano y unidad meses/periodos mensuales autorizada. Número de periodos coincidente; IDs únicos; intervalos válidos/no solapados; calendario trazable. No se generan meses implícitamente.

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
├── reference_date: date | null
├── applicable_from: date | null
├── applicable_to: date | null
├── horizon_ref: str | null
├── source_ref: str | null
├── issue_refs
└── trace_refs
```

`KNOWN` exige mismo ámbito/artículo/unidad, tasa finita no negativa, versión no nula coincidente con contexto, `reference_date` no nula, intervalo válido que contenga la fecha consumidora, horizonte/fuente/traza y referencia temporal. Estado no determinado puede conservar `reference_date = null`; no se inventa.

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
├── issue_refs
└── trace_refs
```

`DemandRateResult.reference_date` es la fecha de referencia del **cálculo STK**, normalmente `evaluation_date`, y no se utiliza para fabricar una fecha fuente ausente.

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

`CoverageResult` conserva identidad, cobertura, estado, demanda, `issue_refs` y trazas.

M04 v0.1 calcula cobertura sobre stock disponible actual. Cualquier uso futuro sobre una referencia proyectada requiere extensión explícita; no se deriva por conveniencia.

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
├── issue_refs
└── trace_refs
```

Dirección:

```text
PENDING_ORDER | IN_TRANSIT | PROPOSED_PURCHASE → INFLOW
AUTHORIZED_DEMAND | RESERVATION | OTHER_AUTHORIZED_NEED → OUTFLOW
```

Movimiento `KNOWN` contribuyente: ID único, cantidad finita no negativa, ámbito/artículo/unidad compatibles, normalización/fuente/traza y `evaluation_date < effective_date <= horizon_end`.

**Gate temporal previo a propagación de incertidumbre:**

1. si `effective_date` está evidenciada y `effective_date > horizon_end`, el movimiento queda fuera del horizonte y no contribuye ni contamina esa proyección;
2. si `effective_date` está evidenciada y `effective_date <= evaluation_date`, no es movimiento futuro de M05 v0.1 y no contribuye al horizonte; permanece trazable, sin roll-forward ni desplazamiento de fecha;
3. si `evaluation_date < effective_date <= horizon_end`, un movimiento `UNKNOWN / NOT_EVIDENCED / CONFLICTING_DATA` propaga incertidumbre desde `effective_date`;
4. si `effective_date` no puede demostrarse, la incertidumbre puede afectar desde `evaluation_date` y se propaga conservadoramente;
5. esta exclusión temporal pertenece al resultado de la proyección; STK no reescribe el estado fuente para fingir `NOT_APPLICABLE`.

`NOT_APPLICABLE` evidenciado tampoco contribuye/contamina.

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

Resultado completo `KNOWN`: escenario compatible, horizonte `KNOWN`, opening `KNOWN`, colección/movimientos aplicables válidos y sin duplicación de segmentos.

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
├── issue_refs
└── trace_refs
```

La composición de cada punto incluye exclusivamente demanda confirmada incorporada desde opening y movimientos M05 hasta esa fecha; no incluye segmentos futuros posteriores al punto.

```text
ProjectedDecimalMetric(value: Decimal | null, state: StockDataState, issue_refs, trace_refs)
ProjectedDateMetric(value: date | null, state: StockDataState, issue_refs, trace_refs)
```

```text
StockProjectionResult
├── identity
├── horizon
├── points
├── minimum_projected_stock: ProjectedDecimalMetric
├── depletion_date: ProjectedDateMetric
├── incorporated_confirmed_demand_at_horizon
├── state
├── issue_refs
└── trace_refs
```

Incertidumbre aplicable contamina desde su fecha; datos posteriores no restauran `KNOWN` sin resolución autorizada.

`minimum_projected_stock` es `KNOWN` únicamente cuando todo el horizonte necesario para demostrar el mínimo está determinado; entonces `min(opening_stock, all daily closings)`. No se publica un mínimo parcial.

`depletion_date`:

- opening cero `KNOWN` → `KNOWN`, `evaluation_date`;
- primera fecha futura determinada con cierre `<= 0` → `KNOWN` solo si no existe incertidumbre previa capaz de adelantarla;
- horizonte totalmente `KNOWN` sin agotamiento → `NOT_APPLICABLE`, valor nulo;
- incertidumbre previa → estado de incertidumbre, valor nulo.

---

## 24. Frontera R-STK-001 / M02 / M03

STK entrega proyección y movimientos evidenciados, no evalúa `R-STK-001`. La RDM mantiene dependencias DATA/COMPONENT no individualizadas; este contrato no inventa una semántica nueva de “próxima compra”.

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
├── issue_refs
└── trace_refs
```

`CURRENT_AVAILABLE` deriva de disponibilidad `KNOWN`, fecha evaluación y composición opening.

`PROJECTED` deriva de un `ProjectionPoint` concreto. Su valor/estado/composición son los de ese punto; puede ser negativo. Nunca usa la composición de fin de horizonte para una fecha intermedia.

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

Para cobertura, demanda > 0:

```text
stock_maximum = coverage_maximum_days * authorized_daily_demand
```

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
├── stock_reference
├── stock_maximum: Decimal | null
├── excess_tolerance_quantity: Decimal | null
├── excess_threshold: Decimal | null
├── excess_quantity: Decimal | null
├── state: ExcessState
├── incorporated_confirmed_demand
├── issue_refs
└── trace_refs
```

Estados determinados exigen todas las cantidades calculadas. Estados de incertidumbre cumplen §4 y no presentan exceso determinado.

Relaciones confirmadas: `STK-004→R-STK-002`, `STK-004→R-STK-003`, `STK-005→R-STK-003`.

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

### `APLICABLE_Y_VALIDADA`

Exige:

- `ExcessResult.state == EXCESS`;
- todos los atributos mínimos M08 evidenciados;
- pending `KNOWN`, mismo ámbito/artículo/unidad y `effective_date == evaluation_date`;
- `order_date <= confirmation_date <= evaluation_date`;
- `expected_delivery_date > excess_reference_date`;
- `expected_delivery_date <= allocation_scope.horizon.horizon_end`;
- `applicability_source_ref` y trazas.

### `NO_APLICABLE`

Solo se utiliza cuando la exclusión está **demostrada** con evidencia suficiente: artículo/ámbito incompatible, cantidad pendiente conocida no aplicable, entrega fuera del horizonte, ausencia de exceso u otra causa autorizada por M08. Conserva `applicability_source_ref` y trazas de esa causa.

Si faltan datos y esa falta impide demostrar la exclusión, el estado es `NO_VERIFICABLE`, no `NO_APLICABLE`.

### `NO_VERIFICABLE`

Permite campos realmente ausentes nulos y conserva la incidencia/evidencia disponible; no se fabrican IDs empresariales, fechas o cantidades.

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
├── issue_refs
└── trace_refs
```

Solo `KNOWN + entries=()` con fuente/traza significa cero asignaciones activas. `KNOWN` exige fecha/ámbito/artículo coincidentes con `AllocationScope`, IDs únicos y entries compatibles. Otro ámbito/artículo es error estructural. `CONFLICTING_DATA` cumple M10 de §4.

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

Misma unidad, cantidades >=0 y `incorporated_before_M08 + already_allocated <= pending_quantity`.

Si no se cumple, contradicción/inconsistencia; no suelo cero.

---

## 32. Alcance M08 y horizonte autorizado

```text
AllocationScope
├── identity
├── scope
├── article_id
├── evaluation_date
├── excess_reference_date
├── horizon: ProjectionHorizon
└── trace_refs
```

`horizon` debe ser `KNOWN`, compatible con contexto y derivado de `PYE-001`. No existe `horizon_end` paralelo suministrable.

Para exceso `PROJECTED`, es el mismo horizonte de la proyección origen. Para exceso actual, se usa el horizonte STK `PYE-001` del contexto.

---

## 33. Absorción M08

La absorción validada solo existe cuando `ExcessResult.state == EXCESS`.

Solo pedidos `APLICABLE_Y_VALIDADA`, mismo ámbito/artículo/unidad, pending vigente y entrega posterior al exceso y dentro de `horizon.horizon_end` participan. Ledger/plan solo IDs presentes. Colección/ledger no `KNOWN` impide resultado validado. STK no elige reparto.

```text
total_remaining_applicable = sum(remaining_allocatable)
absorbed_excess = min(excess_quantity, total_remaining_applicable)
residual_excess = max(0, excess_quantity - absorbed_excess)
```

Si `absorbed_excess > 0`, `sum(allocation_plan.quantity_to_apply) == absorbed_excess`.

```text
ConfirmedDemandAbsorptionResult
├── identity
├── excess_result
├── business_state: NO_EXISTE | NO_APLICABLE | APLICABLE_Y_VALIDADA | NO_VERIFICABLE
├── total_remaining_applicable: Decimal | null
├── absorbed_excess: Decimal | null
├── residual_excess: Decimal | null
├── allocation_plan
├── resulting_ledger: AllocationLedgerSnapshot | null
├── issue_refs
└── trace_refs
```

- `NO_EXISTE`: colección de pedidos `KNOWN` vacía; exceso determinado; absorción 0 y residual = exceso.
- `NO_APLICABLE`: ausencia de exceso o exclusión de pedidos demostrada; con exceso determinado, absorción 0 y residual = exceso.
- `APLICABLE_Y_VALIDADA`: `ExcessResult.state == EXCESS`, fórmulas y plan/ledger válidos.
- `NO_VERIFICABLE`: no se presenta absorción/residual determinados cuando faltan evidencias necesarias.

M08 no reescribe M07.

---

## 34. M09 — ausencia

Sin imputación. Ausencia no se sustituye por cero, media, último valor, estimación o default. Cuando existe registro de ausencia, se conserva mediante `DataIssueRef(MISSING_DATA)` y trazas. Una salida conocida e independiente puede mantenerse sin volver completa una conclusión dependiente de información ausente.

---

## 35. M10 — contradicciones

`CONFLICTING_DATA` exige `DataIssueRef(CONTRADICTION)` conforme a §4 y bloquea cálculo dependiente sin resolución por recencia, máximo, mínimo, promedio, score o prioridad arbitraria.

El artefacto referenciado conserva artículo, variable, ámbito/momento comparable, fuentes, valores/estados, fechas, versiones, evaluaciones/módulos afectados y evidencia. Una resolución externa autorizada conserva la contradicción original y la autoridad aplicada.

---

## 36. Error estructural vs incertidumbre

Error estructural, entre otros:

- Decimal no finito;
- `KNOWN` sin payload requerido;
- cantidad física `KNOWN` negativa;
- identidades/versiones/ámbitos incompatibles;
- IDs físicos `P-STK-* / P-PYE-*`;
- conversión no demostrada;
- `CONFLICTING_DATA` sin incidencia M10 válida;
- M01 `KNOWN` sin reconstruibilidad;
- M02/M03 `KNOWN` sin política/derivación/vigencia;
- `PYE-001` inválido/no aplicable;
- stock actual de otra fecha;
- committed inconsistente/duplicado;
- movimiento `KNOWN` aplicable no estrictamente futuro o fuera de horizonte;
- M06 `KNOWN` sin proveedor/origen/supply identity;
- demand_segment duplicado;
- ramas discriminadas simultáneas;
- M07 umbral fuera de vigencia/autoridad;
- `APLICABLE_Y_VALIDADA` sin exceso real o evidencia completa;
- `NO_APLICABLE` M08 sin exclusión demostrada;
- ledger `KNOWN` de otro ámbito/artículo/fecha, sin evidencia o duplicado;
- `incorporated + allocated > pending`;
- plan inválido.

Incertidumbre empresarial: ausencia/no evidencia, contradicción, colección no evidenciada, forecast/configuración/política no verificables, movimiento incompleto potencialmente aplicable, demanda no aplicable o M08 no verificable.

---

## 37. Determinismo

Decimal; fechas explícitas; sin reloj; sin redondeo implícito; sin prioridad M08; sin selección automática de método; sin calendarización de tasa; misma entrada + identidad + ámbito + versiones + configuración + política + opening/M05 + ledger → mismo resultado.

---

## 38. Defaults prohibidos

No se hardcodean: 15 %, 30/90 días, 10 %, 12 meses, 90 días, booleanos `PYE-002…005`, 15 días. Ausencia de configuración no activa catálogo.

---

## 39. Interfaces de autoridad

Evidence/QTG valida evidencia; Centro de Parametrización resuelve configuración; adaptadores suministran ámbito/normalización; M02/M03 suministran valores autorizados; Rules evalúa reglas; CRC resuelve resultados incompatibles; MED integra. STK no emite decisión final.

`R-STK-001`: STK conserva proyección y movimientos; no inventa una dependencia DATA/COMPONENT mientras RDM la mantenga no demostrada individualmente.

`R-STK-004`: limitado a M08 sobre exceso M07.

---

## 40. Invariantes ejecutables

1. C0 inmutable; no decisión automática.
2. Ausencia ≠ cero; vacío evidenciado ≠ ausencia.
3. `CONFLICTING_DATA` conserva incidencia M10 y al menos dos evidencias cuando esté sin resolver.
4. Company/scope forman parte de identidad y compatibilidad.
5. IDs físicos parámetros = `STK-* / PYE-*`.
6. Histórico forecast nulo; forecast versión exacta y fecha fuente solo si evidenciada.
7. M02/M03 sin fórmula, con derivación/vigencia.
8. Stock actual misma fecha/ámbito; déficit visible.
9. Committed composición completa.
10. M01 ámbito/metodología/agregación reconstruible.
11. `STK-006` ventana exacta; sin fallback.
12. Coverage cero demanda → UNBOUNDED.
13. `PYE-001` gobierna horizonte; 90 no default.
14. `PYE-002…006` no adquieren función no autorizada.
15. Gate temporal precede propagación de incertidumbre M05; fuera de horizonte no contamina.
16. M06 conserva supply identity/proveedor/origen y evita doble conteo.
17. Movimiento futuro aplicable estricto; sin cutoff intradía.
18. Segmentos evitan doble uso opening↔M05.
19. Tasa no crea calendario.
20. Proyección diaria; saldo negativo preservado.
21. Cada punto proyectado conserva demanda confirmada acumulada hasta su fecha.
22. Mínimo/depletion tienen estado propio; no mínimos parciales disfrazados.
23. StockReference PROJECTED usa punto concreto y su composición.
24. M07 ramas exclusivas, vigencia y autoridad.
25. M08 `NO_APLICABLE` exige exclusión demostrada; falta de evidencia → `NO_VERIFICABLE`.
26. M08 validado exige `ExcessResult.state == EXCESS`.
27. M08 horizonte = ProjectionHorizon PYE-001, no fecha paralela.
28. Ledger ausente ≠ vacío y aislado por ámbito/artículo.
29. M08 descuenta opening/M05/ledger y no sobreconsume pending.
30. Sin prioridad M08; plan suma absorción.
31. Contradicciones no heurísticas.
32. Sin defaults; determinismo.

---

## 41. Pruebas mínimas futuras

Cubrir: identidad C0/company/scope; IDs físicos; estados no determinados; `DataIssueRef` M09/M10 y contradicción con ≥2 evidencias; forecast sin fecha fuente; M01 reconstruibilidad; M02/M03; disponibilidad/déficit/committed; histórico/forecast; `STK-006`; cobertura; `PYE-001`; frontera PYE; movimientos fuera/dentro/sin fecha respecto al horizonte; M06/propuesta; proyección diaria y métricas con estado; composición por punto; M07; M08 `NO_APLICABLE` vs `NO_VERIFICABLE`, horizonte común, pedido ya incorporado, ledger ausente-vacío, aislamiento scope/article, sobreconsumo, plan y resultado; M09/M10; no decisión/no defaults/reproducibilidad.

---

## 42. Exclusiones v0.1

Forecasting interno; ventas→demanda; tasa→calendario; cobertura proyectada no autorizada expresamente; vigencia futura implícita; cutoff intradía; jerarquías/redistribución entre ámbitos; optimización/EOQ; fórmula normativa M02/M03; imputación; resolución heurística; prioridad M08; persistencia ledger; SQL STK; API; cambios C0; CRC; decisión final.

---

## 43. Criterio de cierre

El contrato solo puede marcarse `CERRADO` si Audit 2 Final independiente confirma: M01…M10 implementables dentro de frontera, ausencia/contradicción representables, identidad/ámbito/versionado reproducibles, no doble conteo opening/M05/M06/M08, compatibilidad C0/Parametrización/Rules/CRC/MED, cero defaults no autorizados y **cero hallazgos bloqueantes**.

Hasta entonces no está autorizada la creación de `eios/stock` ejecutable.
