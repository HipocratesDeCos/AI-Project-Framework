# EIOS — Stock & Demand Implementation Contract

## 1. Identidad

**Documento:** STK Implementation Contract  
**Versión:** 0.15  
**Estado:** DEPURADO N1…N5 — PENDIENTE DE AUDIT 2 FINAL  
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

Toda estructura que exponga `state: StockDataState` incorpora además, aunque se omita en algún diagrama para evitar repetición:

```text
issue_refs: tuple[DataIssueRef, ...]
trace_refs: tuple[str, ...]
```

Reglas:

1. `KNOWN` exige payload material completo, valor finito cuando sea cuantitativo y trazabilidad suficiente.
2. Campos empresariales potencialmente ausentes son opcionales físicamente; nunca se fabrican valores.
3. Un valor singular no determinado no se presenta como cuantía verdadera.
4. `UNKNOWN / NOT_EVIDENCED / CONFLICTING_DATA ≠ 0`.
5. `NOT_APPLICABLE` es exclusión demostrada, no ausencia.
6. Cero `KNOWN` requiere evidencia explícita.
7. Todo `CONFLICTING_DATA` exige al menos un `DataIssueRef(CONTRADICTION)`; una contradicción no resuelta conserva al menos dos `evidence_refs` distintos.
8. `UNKNOWN / NOT_EVIDENCED` conserva `MISSING_DATA` cuando exista registro de ausencia.
9. Resolución posterior no elimina la incidencia histórica.
10. Estas incidencias son de datos/evidencia STK; no sustituyen CRC ni autoridad documental.

---

## 5. Ámbito empresarial STK

```text
StockScope
├── company_id: str
└── operational_scope_id: str
```

Referencias canónicas suministradas aguas arriba. STK no inventa jerarquías, equivalencias, redistribuciones ni mappings de ámbito.

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

Los cinco primeros proceden sin transformación de `DecisionContext`. Toda composición exige afinidad exacta.

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

Solo `KNOWN + items=()` con fuente/traza suficiente significa vacío evidenciado. Colección no `KNOWN` no se suma parcialmente para producir resultado completo.

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
├── issue_refs
└── trace_refs
```

`KNOWN` exige valor finito no negativo, ámbito/artículo compatibles, unidad base objetivo, fecha cuando el consumidor la requiera, fuente/traza y unidad fuente conocida. Si `source_unit != unit`, `normalization_ref` es obligatorio.

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

`KNOWN` exige valor finito no negativo, ámbito/artículo/unidad compatibles, propósito correcto, autoridad/versionado, fuente/traza y fecha exactamente aplicable.

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

`KNOWN` exige cantidad finita no negativa, unidad/ámbito/artículo compatibles, política/versión, `derivation_ref`, vigencia y fuente/traza. `STOCK_MINIMUM` y `SAFETY_STOCK` no son equivalentes ni se componen implícitamente. STK no calcula sus valores.

---

## 11. Parámetros e IDs físicos

IDs físicos:

```text
STK-001 … STK-006
PYE-001 … PYE-006
```

`P-STK-* / P-PYE-*` es solo notación documental.

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

STK consume configuración ya resuelta por el Centro de Parametrización. `KNOWN` exige compañía/versión coincidentes, configuración efectiva, fecha correcta, tipo/unidad válidos y fuente/traza. Sin fallback.

---

## 12. Frontera PYE v0.1

- `PYE-001`: operativo solo como horizonte M05.
- `PYE-002/003`: no son gates v0.1; M06 decide elegibilidad por evidencia/estado/temporalidad.
- `PYE-004`: no deriva fechas desde `lead_time`.
- `PYE-005`: no transforma ventas en demanda.
- `PYE-006`: no actúa como umbral de `R-STK-001`.

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

`KNOWN`: `parameter_id == "PYE-001"`, efectivo en `evaluation_date`, entero positivo no booleano, unidad días autorizada/normalizada y:

```text
horizon_end = evaluation_date + horizon_days
```

Movimientos contribuyentes: `evaluation_date < effective_date <= horizon_end`. 90 días no es default.

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

Cantidad finita no negativa, mismo ámbito/artículo/unidad/fecha que `stock_committed`, `commitment_id` único y normalización demostrada. Demanda comercial confirmada requiere `confirmed_demand_id + demand_segment_id`. La suma de composición `KNOWN` coincide exactamente con `stock_committed.value`.

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

Cantidad finita no negativa, segmentos no vacíos y únicos. Se agrega por pedido preservando segmentos.

---

## 16. Disponibilidad

```text
StockAvailabilityInput
├── context
├── stock_on_hand: NormalizedQuantity
├── stock_committed: NormalizedQuantity
└── committed_components: CollectionEnvelope[StockCommitmentComponent]
```

Resultado `KNOWN` exige cantidades `KNOWN`, misma identidad material, fecha evaluación y composición `KNOWN`, compatible, única y de suma exacta.

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
├── committed_components: tuple[StockCommitmentComponent, ...]
├── incorporated_confirmed_demand
├── issue_refs
└── trace_refs
```

En resultado `KNOWN`, `committed_components` es exactamente la composición evidenciada usada en el cálculo; no se pierde al pasar a M05.

---

## 17. Consumo M01

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

`KNOWN` exige consumo real mensual, ámbito/artículo/unidad compatibles, cantidad finita no negativa, periodo completo, días exactos, metodología coincidente y agregación/normalización/fuente reconstruibles. Cero solo con evidencia.

---

## 18. Política histórica

```text
RequiredPeriodSpec(period_id, period_start, period_end)
```

```text
HistoricalDemandPolicy
├── parameter: ConfiguredParameterValue
├── required_periods: tuple[RequiredPeriodSpec, ...]
├── period_calendar_ref: str | null
├── extended_applicable_to: date | null
├── applicability_source_ref: str | null
├── source_ref: str | null
├── state: StockDataState
├── issue_refs
└── trace_refs
```

Para `KNOWN`:

- `parameter_id == "STK-006"` y parámetro `KNOWN`, efectivo en `evaluation_date`;
- valor entero positivo no booleano y unidad meses/periodos mensuales autorizada;
- `period_calendar_ref` y `source_ref` no nulos;
- `required_periods` completo, IDs únicos, intervalos válidos/no solapados y cantidad consistente con el parámetro;
- si `extended_applicable_to` existe: `extended_applicable_to >= evaluation_date` y `applicability_source_ref` obligatorio.

Política no `KNOWN` no genera meses implícitos ni reduce silenciosamente la ventana.

---

## 19. Demanda histórica

Solo política y colección `KNOWN`, correspondencia exacta de periodos, ámbito/unidad/metodología compatibles y periodos completos:

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

Para `KNOWN`:

```text
reference_date != null
applicable_from != null
applicable_to != null
applicable_from <= reference_date <= applicable_to
```

Además: mismo ámbito/artículo/unidad, tasa finita no negativa, versión exacta no nula, toda fecha consumidora dentro del intervalo, `horizon_ref`, fuente y traza. Un extremo ausente produce estado no determinado, no vigencia abierta.

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

`KNOWN` exige intervalo de aplicabilidad no nulo que contenga la fecha consumidora. `reference_date` es la fecha de referencia del cálculo STK y no fabrica fecha fuente.

Forecast exige coincidencia exacta de versión; histórico exige referencias forecast nulas. No forecasting interno, ventas→demanda ni fallback.

Una tasa no crea movimientos diarios M05; calendarización queda fuera.

---

## 21. Cobertura M04

```text
CoverageState = FINITE | UNBOUNDED | UNKNOWN | NOT_EVIDENCED | CONFLICTING_DATA
```

Con stock disponible y demanda `KNOWN` aplicable a evaluación:

```text
coverage_days = stock_available / daily_demand  # >0
```

Demanda cero confirmada → `UNBOUNDED`, valor nulo. `CoverageResult` conserva identidad, cobertura, estado, demanda, incidencias y trazas.

M04 v0.1 calcula cobertura sobre stock disponible actual. Cobertura proyectada requiere autoridad futura explícita.

---

## 22. Movimientos M05/M06

```text
ProjectionMovement
├── movement_id
├── commitment_id: str | null
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

Movimiento contribuyente `KNOWN`: ID único, cantidad finita no negativa, ámbito/artículo/unidad compatibles, normalización/fuente/traza y fecha dentro del horizonte futuro.

### Gate temporal previo a incertidumbre

- fecha evidenciada `> horizon_end`: fuera de horizonte, no contribuye/contamina;
- fecha evidenciada `<= evaluation_date`: no es movimiento futuro v0.1; no contribuye ni se desplaza;
- fecha dentro del horizonte + dato no determinado: incertidumbre desde esa fecha;
- fecha no demostrable: incertidumbre conservadora desde `evaluation_date`;
- `NOT_APPLICABLE` evidenciado tampoco contribuye.

### Reconciliación con opening

- `AUTHORIZED_DEMAND` comercial confirmada exige `confirmed_demand_id + demand_segment_id`; segmento no se duplica opening↔M05.
- `RESERVATION` `KNOWN` exige `commitment_id` estable/trazable.
- Un `commitment_id` ya presente en `opening.committed_components` no puede volver a contribuir como salida M05.
- Si `OTHER_AUTHORIZED_NEED` representa una obligación ya materializada o reconciliable con opening, conserva el mismo `commitment_id`; si no puede demostrarse la no duplicación respecto de opening, la proyección completa no puede ser `KNOWN`.
- Una nueva obligación/reserva posterior a evaluación puede participar cuando su identidad no figure en opening y cumpla evidencia/temporalidad.

### M06

`PENDING_ORDER | IN_TRANSIT` `KNOWN` exige `supply_identity`, proveedor, origen documental, fecha, cantidad, unidad y evidencia. Misma cantidad no puede estar simultáneamente en ambos estados. Recepción confirmada sale M06.

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

Resultado completo `KNOWN`: escenario/horizonte/opening compatibles, movimientos aplicables válidos, sin duplicación de segmentos ni `commitment_id` con opening.

Para cada día futuro:

```text
closing_stock_date = previous_closing_stock + inflows(date) - outflows(date)
```

Sin orden intradía; saldo negativo se conserva.

```text
ProjectionPoint
├── reference_date
├── projected_stock: Decimal | null
├── state
├── incorporated_confirmed_demand
├── issue_refs
└── trace_refs
```

Cada punto conserva demanda confirmada incorporada solo hasta su fecha.

```text
ProjectedDecimalMetric(value: Decimal | null, state, issue_refs, trace_refs)
ProjectedDateMetric(value: date | null, state, issue_refs, trace_refs)
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

No se publica mínimo parcial como mínimo del horizonte. Depletion conocida solo si no existe incertidumbre previa que pudiera adelantarla. Opening cero conocido → evaluación. Horizonte completamente conocido sin agotamiento → `NOT_APPLICABLE`.

---

## 24. Frontera R-STK-001 / M02 / M03

STK entrega proyección/movimientos, no evalúa `R-STK-001` ni inventa dependencias DATA/COMPONENT pendientes en RDM. M02/M03 permanecen valores autorizados sin fórmula propia STK.

---

## 25. Referencia M07

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

CURRENT deriva de disponibilidad. PROJECTED deriva de un punto concreto y copia valor/estado/composición de ese punto; puede ser negativo.

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

Ramas exclusivas. Direct usa threshold `STOCK_MAXIMUM`. Coverage usa `STK-004 + demand` KNOWN, aplicable a la fecha y demanda >0:

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

QUANTITY usa threshold `EXCESS_TOLERANCE`; RATE usa `STK-005` normalizado/trazado:

```text
excess_tolerance_quantity = stock_maximum * normalized_rate
```

---

## 27. Exceso M07

```text
ExcessState = NO_EXCESS | WITHIN_TOLERANCE | EXCESS | UNKNOWN | NOT_EVIDENCED | CONFLICTING_DATA
```

```text
excess_threshold = stock_maximum + excess_tolerance_quantity
excess_quantity = max(0, stock_reference.value - excess_threshold)
```

Clasificación autorizada M07.

```text
ExcessResult
├── identity
├── stock_reference
├── stock_maximum: Decimal | null
├── excess_tolerance_quantity: Decimal | null
├── excess_threshold: Decimal | null
├── excess_quantity: Decimal | null
├── state
├── incorporated_confirmed_demand
├── issue_refs
└── trace_refs
```

Estados determinados exigen cantidades completas. Incertidumbre cumple §4. Relaciones confirmadas: `STK-004→R-STK-002`, `STK-004→R-STK-003`, `STK-005→R-STK-003`.

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
├── issue_refs: tuple[DataIssueRef, ...]
└── trace_refs
```

Solo colección `KNOWN` vacía/trazada significa `NO_EXISTE`.

`APLICABLE_Y_VALIDADA`: `ExcessResult.state == EXCESS`, atributos M08 completos, pending `KNOWN` misma fecha/ámbito/artículo/unidad, fechas coherentes, entrega posterior a referencia de exceso y dentro del horizonte, fuente/traza.

`NO_APLICABLE`: exclusión demostrada con evidencia suficiente y `applicability_source_ref`. Falta que impide demostrar exclusión → `NO_VERIFICABLE`.

`NO_VERIFICABLE`: no fabrica datos; conserva `issue_refs` M09/M10 cuando existan.

---

## 29. Ledger M08 activo y aislado

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

Solo `KNOWN + entries=()` con evidencia significa cero asignaciones activas. `KNOWN` exige fecha/ámbito/artículo correctos, IDs únicos y entries compatibles. Snapshot contiene solo asignaciones activas; liberación/caducidad corresponde aguas arriba.

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

Cantidad estrictamente positiva; sin prioridad implícita.

---

## 31. Reconciliación opening/M05/M08

```text
remaining_allocatable = pending_quantity
                      - incorporated_before_M08
                      - already_allocated
```

Misma unidad y `incorporated_before_M08 + already_allocated <= pending_quantity`. Si no, contradicción/inconsistencia; no suelo cero.

---

## 32. Alcance M08

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

Horizonte `KNOWN`, compatible y derivado de `PYE-001`; no existe fecha final paralela. Para exceso proyectado usa el mismo horizonte de la proyección origen.

---

## 33. Absorción M08 y ledger resultante

Absorción validada solo con `ExcessResult.state == EXCESS` y pedidos/ledger `KNOWN` aplicables.

```text
total_remaining_applicable = sum(remaining_allocatable)
absorbed_excess = min(excess_quantity, total_remaining_applicable)
residual_excess = max(0, excess_quantity - absorbed_excess)
```

Si `absorbed_excess > 0`, el plan suma exactamente `absorbed_excess`.

Para `APLICABLE_Y_VALIDADA`, `resulting_ledger`:

1. es `KNOWN`, misma fecha/ámbito/artículo que el ledger de entrada;
2. conserva **cada entry activa previa exactamente una vez e inalterada**;
3. añade exactamente las entries nuevas derivadas del plan;
4. todos los `allocation_entry_id` son únicos;
5. la suma de nuevas entries por `confirmed_demand_id` coincide con la suma del plan para ese pedido;
6. ninguna entry previa se elimina/modifica desde STK;
7. si no hay asignación nueva, es semánticamente igual al ledger de entrada.

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

- `NO_EXISTE`: pedidos `KNOWN` vacíos; exceso determinado; absorción 0, residual = exceso.
- `NO_APLICABLE`: ausencia de exceso o exclusión demostrada; con exceso determinado, absorción 0 y residual = exceso.
- `APLICABLE_Y_VALIDADA`: exceso real, fórmulas, plan y ledger resultante válidos.
- `NO_VERIFICABLE`: sin absorción/residual determinados cuando falta evidencia necesaria.

M08 no reescribe M07.

---

## 34. M09 — ausencia

Sin imputación. Ausencia no se sustituye por cero, media, último valor, estimación o default. Se conserva `DataIssueRef(MISSING_DATA)` cuando exista registro.

---

## 35. M10 — contradicciones

`CONFLICTING_DATA` exige `DataIssueRef(CONTRADICTION)` y bloquea cálculo dependiente sin heurística. El registro referenciado conserva contexto, evidencias, valores/estados, fechas, versiones y evaluaciones afectadas. Resolución posterior conserva la contradicción histórica.

---

## 36. Error estructural vs incertidumbre

Error estructural, entre otros: Decimal no finito; `KNOWN` incompleto; cantidad física negativa; identidad/ámbito/versiones incompatibles; IDs `P-*` físicos; conversión no demostrada; conflicto sin incidencia; M01 sin reconstruibilidad; M02/M03 sin derivación/vigencia; `PYE-001` inválido; stock actual de otra fecha; committed inconsistente; duplicación `commitment_id` opening↔M05; movimiento aplicable fuera de frontera temporal; M06 sin proveedor/origen/supply identity; segmento duplicado; ramas simultáneas; M07 fuera de vigencia; M08 aplicable sin exceso/evidencia; `NO_APLICABLE` no demostrado; ledger incompatible/duplicado; ledger resultante que pierda/modifique entradas previas; sobreconsumo pending; plan inválido.

Incertidumbre: ausencia/no evidencia, contradicción, política histórica no evidenciada, forecast/configuración/política no verificables, movimiento potencialmente aplicable incompleto, demanda no aplicable o M08 no verificable.

---

## 37. Determinismo

Decimal; fechas explícitas; sin reloj; sin redondeo implícito; sin prioridad M08; sin selección automática de método; sin calendarización de tasa; misma entrada + identidad + ámbito + versiones + configuración + política + opening/M05 + ledger → mismo resultado.

---

## 38. Defaults prohibidos

No se hardcodean: 15 %, 30/90 días, 10 %, 12 meses, 90 días, booleanos `PYE-002…005`, 15 días. Ausencia no activa catálogo.

---

## 39. Interfaces de autoridad

Evidence/QTG valida evidencia; Centro de Parametrización resuelve configuración; adaptadores suministran ámbito/normalización/reconciliación de obligaciones; M02/M03 suministran valores autorizados; Rules evalúa reglas; CRC resuelve resultados incompatibles; MED integra. STK no emite decisión final.

`R-STK-001`: no inventar dependencias RDM pendientes. `R-STK-004`: limitado a M08 sobre M07.

---

## 40. Invariantes ejecutables

1. C0 inmutable; no decisión automática.
2. Ausencia ≠ cero; vacío evidenciado ≠ ausencia.
3. Conflictos conservan incidencia/evidencias.
4. Company/scope forman identidad.
5. IDs físicos = `STK-* / PYE-*`.
6. Histórico forecast nulo; forecast versión/intervalo completos.
7. M02/M03 sin fórmula, con derivación/vigencia.
8. Stock actual misma fecha; déficit visible; committed composición completa.
9. M01 reconstruible; `STK-006` política histórica stateful y ventana exacta.
10. Coverage cero demanda → UNBOUNDED.
11. `PYE-001` horizonte; `PYE-002…006` sin función no autorizada.
12. Gate temporal antes de incertidumbre.
13. M06 identidad/proveedor/origen.
14. `commitment_id` evita doble uso de obligaciones opening↔M05.
15. Segmentos evitan doble uso de demanda confirmada opening↔M05.
16. Tasa no crea calendario.
17. Proyección diaria, saldo negativo, composición por punto y métricas con estado.
18. M07 ramas/vigencia/autoridad.
19. M08 `NO_APLICABLE` demostrado; `NO_VERIFICABLE` conserva incidencias.
20. M08 exige exceso real y horizonte `PYE-001` común.
21. Ledger ausente ≠ vacío, aislado por ámbito/artículo.
22. Resulting ledger conserva todas las entries activas previas y añade solo las nuevas.
23. M08 descuenta opening/M05/ledger y no sobreconsume pending.
24. Sin prioridad M08; plan suma absorción.
25. Contradicciones no heurísticas; sin defaults; determinismo.

---

## 41. Pruebas mínimas futuras

Cubrir: identidad/scope; IDs físicos; estados/incidencias; M01; M02/M03; disponibilidad/déficit/committed; historical policy UNKNOWN; histórico/forecast e intervalos; `STK-006`; coverage; PYE; movimientos fuera/dentro/sin fecha; M06; reserva/other need duplicando commitment opening; propuesta; proyección/métricas/composición por punto; M07; M08 aplicabilidad, incidencias, horizonte, pedido incorporado, ledger ausente-vacío, aislamiento, preservación ledger previo, sobreconsumo y plan; M09/M10; no decisión/no defaults/reproducibilidad.

---

## 42. Exclusiones v0.1

Forecasting interno; ventas→demanda; tasa→calendario; cobertura proyectada no autorizada; vigencia futura implícita; cutoff intradía; jerarquías/redistribución entre ámbitos; optimización/EOQ; fórmula M02/M03; imputación; heurística de conflicto; prioridad M08; persistencia ledger; SQL STK; API; cambios C0; CRC; decisión final.

---

## 43. Criterio de cierre

Solo `CERRADO` si Audit 2 Final independiente confirma M01…M10 implementables dentro de frontera, ausencia/contradicción representables, identidad/ámbito/versionado reproducibles, no doble conteo opening/M05/M06/M08, compatibilidad C0/Parametrización/Rules/CRC/MED, cero defaults no autorizados y **cero bloqueos**.

Hasta entonces no se crea `eios/stock` ejecutable.
