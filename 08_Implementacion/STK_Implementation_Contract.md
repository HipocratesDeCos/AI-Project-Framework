# EIOS — Stock & Demand Implementation Contract

## 1. Identidad

**Documento:** STK Implementation Contract  
**Versión:** 0.16  
**Estado:** DEPURADO O1…O5 — PENDIENTE DE AUDIT 2 FINAL  
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

Toda estructura que exponga `state: StockDataState` incorpora `issue_refs: tuple[DataIssueRef, ...]` y `trace_refs: tuple[str, ...]`.

Reglas:

1. `KNOWN` exige payload material completo, valores finitos cuando sean cuantitativos y trazabilidad suficiente.
2. Campos empresariales potencialmente ausentes son opcionales; nunca se fabrican valores.
3. `UNKNOWN / NOT_EVIDENCED / CONFLICTING_DATA ≠ 0`.
4. `NOT_APPLICABLE` exige exclusión demostrada.
5. Cero `KNOWN` requiere evidencia explícita.
6. Todo `CONFLICTING_DATA` conserva `DataIssueRef(CONTRADICTION)`; contradicción no resuelta conserva ≥2 evidencias distintas.
7. M09 conserva `MISSING_DATA` cuando exista registro.
8. Una resolución posterior no elimina la incidencia histórica.
9. Incidencias STK no sustituyen CRC ni autoridad documental.

---

## 5. Ámbito empresarial STK

```text
StockScope
├── company_id: str
└── operational_scope_id: str
```

Referencias suministradas aguas arriba. STK no inventa jerarquías, equivalencias, redistribuciones ni mappings de ámbito.

---

## 6. Selección autorizada del método de demanda

```text
DemandMethodSelection
├── method: HISTORICAL_CONSUMPTION | AUTHORIZED_FORECAST | null
├── state: StockDataState
├── policy_ref: str | null
├── policy_version: str | null
├── applicable_reference_date: date
├── source_ref: str | null
├── issue_refs
└── trace_refs
```

`KNOWN` exige método no nulo, `policy_ref`, `policy_version`, fuente/traza y `applicable_reference_date == evaluation_date` del contexto consumidor. La referencia de política debe demostrar aplicabilidad al artículo/ámbito de la evaluación; STK no infiere esa aplicabilidad.

Si la selección no es `KNOWN`, STK no elige método, no promedia y no hace fallback.

---

## 7. Contexto e identidad

```text
StockComputationContext
├── decision_context: DecisionContext
├── scope: StockScope
├── article_id: str
├── evaluation_date: date
├── base_unit: str
├── methodology_version: str
├── demand_selection: DemandMethodSelection
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

La selección de demanda **no bloquea cálculos independientes de demanda** como disponibilidad. En operaciones que consumen demanda se exige además afinidad exacta entre `DemandRateResult.selection` y `context.demand_selection`.

Si `demand_selection.state == KNOWN`:

- `HISTORICAL_CONSUMPTION` → `forecast_version == null`;
- `AUTHORIZED_FORECAST` → `forecast_version != null`.

Si la selección no es `KNOWN`, no se produce `DemandRateResult` `KNOWN` y no se usa `forecast_version` para simular una selección.

---

## 8. Colecciones evidenciadas

```text
CollectionEnvelope[T]
├── state: KNOWN | UNKNOWN | NOT_EVIDENCED | CONFLICTING_DATA
├── items: tuple[T, ...]
├── source_ref: str | null
├── issue_refs
└── trace_refs
```

Solo `KNOWN + items=()` con fuente/traza significa vacío evidenciado. Colección no `KNOWN` no produce conclusión completa mediante suma parcial.

---

## 9. Magnitud física normalizada

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

`KNOWN` exige valor finito no negativo, ámbito/artículo compatibles, unidad base objetivo, fecha cuando se requiera, fuente/traza y unidad fuente. Conversión de unidad exige `normalization_ref`.

---

## 10. Umbral autorizado M07

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

`KNOWN` exige valor finito no negativo, compatibilidad, propósito correcto, autoridad/versionado, fuente/traza y fecha aplicable exacta.

---

## 11. Valores M02/M03 sin fórmula STK

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

`KNOWN` exige cantidad finita no negativa, compatibilidad, política/versión, derivación, vigencia y fuente/traza. STK no calcula estos valores; mínimo y safety stock no son equivalentes.

---

## 12. Parámetros e IDs físicos

IDs físicos: `STK-001…006`, `PYE-001…006`. `P-STK-* / P-PYE-*` es notación documental, nunca `parameter_id` físico.

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

`KNOWN` exige compañía/versión correctas, configuración efectiva, fecha aplicable, tipo/unidad válidos y fuente/traza. Sin fallback.

---

## 13. Frontera PYE v0.1

- `PYE-001`: operativo solo como horizonte M05.
- `PYE-002/003`: no son gates v0.1.
- `PYE-004`: no deriva fechas desde `lead_time`.
- `PYE-005`: no transforma ventas en demanda.
- `PYE-006`: no actúa como umbral de `R-STK-001`.

---

## 14. Horizonte M05 — `PYE-001`

```text
ProjectionHorizon
├── parameter: ConfiguredParameterValue
├── horizon_days: int | null
├── horizon_end: date | null
├── state
├── issue_refs
└── trace_refs
```

`KNOWN`: parámetro físico `PYE-001`, efectivo en evaluación, entero positivo no booleano, unidad días normalizada:

```text
horizon_end = evaluation_date + horizon_days
```

Movimientos contribuyentes: `evaluation_date < effective_date <= horizon_end`. 90 no es default.

---

## 15. Composición de compromiso de apertura

```text
StockCommitmentComponent
├── commitment_id
├── demand_segment_id: str | null
├── confirmed_demand_id: str | null
├── scope
├── article_id
├── quantity: Decimal
├── unit
├── source_unit: str | null
├── normalization_ref: str | null
├── effective_date
├── source_ref
└── trace_refs
```

Cantidad finita no negativa, misma identidad material que `stock_committed`, `commitment_id` único y normalización demostrada.

Para compromiso comercial confirmado, `confirmed_demand_id` y `demand_segment_id` son ambos obligatorios. Fuera de ese caso ambos son nulos; no se admite un segmento huérfano.

La suma de composición `KNOWN` coincide exactamente con `stock_committed.value`.

---

## 16. Demanda confirmada incorporada — derivación exacta

```text
IncorporatedDemandQuantity
├── confirmed_demand_id
├── quantity: Decimal
├── unit
├── demand_segment_ids: tuple[str, ...]
└── trace_refs
```

Invariantes:

1. un `confirmed_demand_id` aparece como máximo una vez en una colección agregada;
2. `demand_segment_ids` no contiene duplicados;
3. cantidad finita no negativa;
4. en `StockAvailabilityResult`, la colección se **calcula** agrupando exclusivamente `committed_components` con `confirmed_demand_id + demand_segment_id`; la cantidad es la suma exacta y los segmentos son el conjunto exacto de componentes agrupados;
5. el llamador no suministra manualmente esta colección como dato independiente.

---

## 17. Disponibilidad

```text
StockAvailabilityInput
├── context
├── stock_on_hand
├── stock_committed
└── committed_components
```

Resultado `KNOWN`: cantidades `KNOWN`, misma identidad material, fecha evaluación y composición `KNOWN`, única y suma exacta.

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
├── committed_components
├── incorporated_confirmed_demand  # derivada según §16
├── issue_refs
└── trace_refs
```

---

## 18. Consumo M01

```text
ConsumptionPeriod
├── scope
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

`KNOWN` exige consumo real mensual, compatibilidad, cantidad finita no negativa, periodo completo, días exactos, metodología coincidente y agregación/normalización/fuente reconstruibles. Cero solo evidenciado.

---

## 19. Política histórica

```text
RequiredPeriodSpec(period_id, period_start, period_end)
```

```text
HistoricalDemandPolicy
├── parameter: ConfiguredParameterValue
├── required_periods
├── period_calendar_ref: str | null
├── extended_applicable_to: date | null
├── applicability_source_ref: str | null
├── source_ref: str | null
├── state
├── issue_refs
└── trace_refs
```

`KNOWN`: `STK-006` `KNOWN` efectivo en evaluación, entero positivo no booleano, unidad mensual autorizada; calendario/fuente no nulos; periodos completos, únicos/no solapados y consistentes. Extensión futura requiere fecha `>= evaluation_date` y `applicability_source_ref`.

---

## 20. Demanda histórica

Solo con `context.demand_selection == KNOWN/HISTORICAL_CONSUMPTION`, política y colección `KNOWN` compatibles:

```text
historical_daily_demand = sum(quantity) / sum(evidenced_days)
```

No se acorta ni rellena ventana. Aplicabilidad = evaluación salvo extensión explícita. Forecast refs nulas.

---

## 21. Forecast autorizado y demanda común

```text
AuthorizedForecastRate
├── scope
├── article_id
├── daily_demand: Decimal | null
├── unit
├── state
├── forecast_version: str | null
├── reference_date: date | null
├── applicable_from: date | null
├── applicable_to: date | null
├── horizon_ref: str | null
├── source_ref: str | null
├── issue_refs
└── trace_refs
```

Forecast `KNOWN`: contexto con `demand_selection == KNOWN/AUTHORIZED_FORECAST`; tasa finita no negativa; versión exacta; fechas no nulas y `applicable_from <= reference_date <= applicable_to`; toda fecha consumidora dentro de intervalo; horizonte/fuente/traza.

```text
DemandRateResult
├── identity
├── selection: DemandMethodSelection
├── method
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

`KNOWN` exige `selection == context.demand_selection`, `method == selection.method`, intervalo demostrable y compatibilidad completa. Histórico: forecast nulo. Forecast: versión exacta. Selección no `KNOWN` → resultado no `KNOWN`; sin fallback.

Una tasa no crea calendario M05.

---

## 22. Cobertura M04

`CoverageState = FINITE | UNBOUNDED | UNKNOWN | NOT_EVIDENCED | CONFLICTING_DATA`.

Con disponibilidad y demanda `KNOWN` cuya selección coincide con contexto y es aplicable a evaluación:

```text
coverage_days = stock_available / daily_demand   # > 0
```

Demanda cero evidenciada → UNBOUNDED, valor nulo. Cobertura v0.1 es sobre stock disponible actual; cobertura proyectada queda fuera sin autoridad adicional.

---

## 23. Movimientos M05/M06

```text
ProjectionMovement
├── movement_id
├── commitment_id: str | null
├── opening_reconciliation_ref: str | null
├── supply_identity: str | null
├── supplier_id: str | null
├── supply_document_ref: str | null
├── confirmed_demand_id: str | null
├── demand_segment_id: str | null
├── scenario_id: str | null
├── scope
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

Dirección: PENDING_ORDER/IN_TRANSIT/PROPOSED_PURCHASE → INFLOW; AUTHORIZED_DEMAND/RESERVATION/OTHER_AUTHORIZED_NEED → OUTFLOW.

Movimiento contribuyente `KNOWN`: ID único, cantidad finita no negativa, compatibilidad, normalización/fuente/traza y fecha dentro del horizonte.

**Gate temporal:** fecha demostrada fuera del futuro/horizonte no contribuye ni contamina; fecha dentro + dato incierto contamina desde esa fecha; fecha no demostrable contamina desde evaluación; no roll-forward.

**Opening reconciliation:**

- AUTHORIZED_DEMAND comercial: IDs de pedido/segmento; segmento no duplicado opening↔M05.
- RESERVATION `KNOWN`: `commitment_id` + `opening_reconciliation_ref` obligatorios. ID ya presente en opening → no contribuye de nuevo.
- OTHER_AUTHORIZED_NEED `KNOWN`: `opening_reconciliation_ref` obligatorio. Si corresponde a obligación identificable, conserva `commitment_id`; ID ya presente en opening → no contribuye. Si es necesidad nueva sin compromiso previo, la referencia demuestra esa no pertenencia; STK no la deduce por `commitment_id == null`.
- si no puede demostrarse la no duplicación, proyección completa no es `KNOWN`.

**M06:** pending/transit `KNOWN` exige supply identity, proveedor, origen documental, fecha, cantidad/unidad/evidencia. Misma cantidad no ocupa ambos estados; recepción confirmada sale M06.

Propuesta exige escenario, cantidad normalizada, fecha futura y traza; no presume aprobación.

---

## 24. Proyección M05

Input: contexto + opening + colección movimientos + `ProjectionHorizon` + escenario.

Resultado completo `KNOWN`: escenario/horizonte/opening compatibles, movimientos aplicables válidos, sin duplicación de segmentos ni obligaciones opening↔M05.

Por día futuro:

```text
closing = previous_closing + inflows(date) - outflows(date)
```

Sin orden intradía; saldo negativo preservado.

```text
ProjectionPoint
├── reference_date
├── projected_stock: Decimal | null
├── state
├── incorporated_confirmed_demand
├── issue_refs
└── trace_refs
```

**Composición exacta por punto:**

- primer punto parte exactamente de `opening.incorporated_confirmed_demand`;
- añade únicamente movimientos AUTHORIZED_DEMAND comerciales contabilizados hasta esa fecha;
- cada movimiento añade exactamente su cantidad al pedido y su `demand_segment_id` al conjunto;
- ningún segmento aparece dos veces;
- un punto nunca incorpora movimientos posteriores a su fecha.

`ProjectedDecimalMetric` y `ProjectedDateMetric` conservan valor nullable + estado + incidencias/trazas.

```text
StockProjectionResult
├── identity
├── horizon
├── points
├── minimum_projected_stock
├── depletion_date
├── incorporated_confirmed_demand_at_horizon
├── state
├── issue_refs
└── trace_refs
```

`incorporated_confirmed_demand_at_horizon` es exactamente la composición del último `ProjectionPoint`. No se suministra de forma independiente.

Mínimo solo `KNOWN` con horizonte suficiente completamente determinado; no mínimo parcial. Depletion solo conocida sin incertidumbre previa que pueda adelantarla; opening cero → evaluación; horizonte conocido sin agotamiento → NOT_APPLICABLE.

---

## 25. Frontera R-STK-001 / M02 / M03

STK entrega proyección/movimientos, no evalúa R-STK-001 ni inventa dependencias RDM pendientes. M02/M03 permanecen valores autorizados sin fórmula STK.

---

## 26. Referencia M07

`StockReferenceValue(CURRENT_AVAILABLE | PROJECTED)` conserva identidad, fecha, valor nullable, unidad, estado, composición confirmada, fuente, incidencias/trazas.

CURRENT copia exactamente disponibilidad/composición opening. PROJECTED copia exactamente valor/estado/composición del `ProjectionPoint` seleccionado; no usa composición de fin de horizonte para fecha intermedia.

---

## 27. Máximo y tolerancia M07

`StockMaximumBasis` es unión exclusiva DIRECT_QUANTITY o COVERAGE_MAXIMUM. Direct usa threshold STOCK_MAXIMUM. Coverage usa `STK-004 + DemandRateResult` `KNOWN`, selección compatible, aplicable a fecha y demanda >0:

```text
stock_maximum = coverage_maximum_days * authorized_daily_demand
```

`ExcessToleranceBasis` es unión exclusiva QUANTITY o RATE. QUANTITY usa threshold EXCESS_TOLERANCE. RATE usa `STK-005` normalizado:

```text
excess_tolerance_quantity = stock_maximum * normalized_rate
```

---

## 28. Exceso M07

`ExcessState = NO_EXCESS | WITHIN_TOLERANCE | EXCESS | UNKNOWN | NOT_EVIDENCED | CONFLICTING_DATA`.

```text
excess_threshold = stock_maximum + tolerance
excess_quantity = max(0, stock_reference.value - excess_threshold)
```

```text
ExcessResult
├── identity
├── stock_reference
├── stock_maximum
├── excess_tolerance_quantity
├── excess_threshold
├── excess_quantity
├── state
├── incorporated_confirmed_demand
├── issue_refs
└── trace_refs
```

**Invariante:** `ExcessResult.incorporated_confirmed_demand == stock_reference.incorporated_confirmed_demand` exactamente; no se recalcula ni se suministra manualmente.

Estados determinados exigen cantidades completas. Relaciones confirmadas: STK-004→R-STK-002; STK-004→R-STK-003; STK-005→R-STK-003.

---

## 29. M08 — demanda confirmada

```text
ConfirmedDemandRecord
├── confirmed_demand_id
├── order_id: str | null
├── customer_id: str | null
├── scope
├── article_id
├── pending_quantity: NormalizedQuantity
├── order_date: date | null
├── confirmation_date: date | null
├── expected_delivery_date: date | null
├── business_status: str | null
├── applicability_state: NO_APLICABLE | APLICABLE_Y_VALIDADA | NO_VERIFICABLE
├── applicability_source_ref: str | null
├── source_ref: str | null
├── issue_refs
└── trace_refs
```

Colección KNOWN vacía = NO_EXISTE.

APLICABLE_Y_VALIDADA exige exceso EXCESS, atributos completos, pending KNOWN vigente, fechas coherentes y entrega posterior a referencia de exceso y dentro del horizonte.

NO_APLICABLE exige exclusión demostrada. Falta que impida demostrarla → NO_VERIFICABLE con incidencias.

---

## 30. Ledger M08

```text
AllocationLedgerEntry
├── allocation_entry_id
├── confirmed_demand_id
├── scope
├── article_id
├── allocated_quantity
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
├── scope
├── article_id
├── state: KNOWN | UNKNOWN | NOT_EVIDENCED | CONFLICTING_DATA
├── entries
├── source_ref: str | null
├── issue_refs
└── trace_refs
```

KNOWN exige fecha/ámbito/artículo correctos, fuente/traza, IDs únicos y entries compatibles. KNOWN vacío evidenciado = cero asignaciones activas. Histórico liberado/caducado queda aguas arriba.

---

## 31. Plan M08 determinista

```text
DemandAllocation
├── allocation_entry_id: str
├── confirmed_demand_id: str
├── quantity_to_apply: Decimal
├── unit: str
├── allocation_source_ref: str
└── trace_refs
```

Reglas:

- cantidad finita y >0;
- `allocation_entry_id` único en plan y no presente en ledger activo;
- no prioridad implícita;
- el motor no genera IDs aleatorios;
- cada nueva `AllocationLedgerEntry` reutiliza exactamente `allocation_entry_id`;
- `AllocationLedgerEntry.allocation_result_ref == allocation_source_ref`;
- decisión, escenario y fecha de exceso se derivan de `AllocationScope/StockResultIdentity`.

---

## 32. Reconciliación opening/M05/M08

```text
remaining_allocatable = pending_quantity
                      - incorporated_before_M08
                      - already_allocated
```

`incorporated_before_M08` procede exclusivamente de `ExcessResult.incorporated_confirmed_demand`, que es copia exacta de la referencia de stock. `already_allocated` procede del ledger activo KNOWN.

Misma unidad; `incorporated + allocated <= pending`. Si no, contradicción/inconsistencia; no suelo cero.

---

## 33. Alcance M08

`AllocationScope` conserva identidad, ámbito, artículo, evaluación, fecha referencia de exceso y `ProjectionHorizon` KNOWN derivado de PYE-001. No existe horizon_end paralelo. Exceso proyectado usa el mismo horizonte de la proyección origen.

---

## 34. Absorción M08 y ledger resultante

Solo pedidos APLICABLE_Y_VALIDADA, mismo ámbito/artículo/unidad, pending vigente y entrega dentro del horizonte participan.

```text
total_remaining_applicable = sum(remaining_allocatable)
```

Si `ExcessResult.state == EXCESS` y `total_remaining_applicable == 0`:

- `business_state = NO_APLICABLE`;
- `absorbed_excess = 0`;
- `residual_excess = excess_quantity`;
- plan vacío;
- no se crean nuevas entries.

`APLICABLE_Y_VALIDADA` exige:

```text
total_remaining_applicable > 0
absorbed_excess = min(excess_quantity, total_remaining_applicable) > 0
residual_excess = max(0, excess_quantity - absorbed_excess)
sum(plan.quantity_to_apply) == absorbed_excess
```

`resulting_ledger` KNOWN:

1. misma fecha/ámbito/artículo que ledger de entrada;
2. conserva cada entry activa previa exactamente una vez e inalterada;
3. añade exactamente una nueva entry por `DemandAllocation`;
4. usa los IDs/referencias aportados por el plan;
5. IDs únicos globalmente en snapshot;
6. suma nueva por pedido = suma del plan por pedido;
7. ninguna entry previa se elimina/modifica;
8. sin nueva asignación, es semánticamente igual al ledger de entrada.

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

NO_EXISTE = pedidos KNOWN vacíos; NO_APLICABLE = ausencia de exceso o exclusión/cero saldo demostrados; APLICABLE = fórmulas/plan/ledger válidos; NO_VERIFICABLE = sin absorción/residual determinados cuando falta evidencia necesaria. M08 no reescribe M07.

---

## 35. M09 — ausencia

Sin imputación. Ausencia no se sustituye por cero/media/último/default. Se conserva MISSING_DATA cuando exista registro.

---

## 36. M10 — contradicciones

CONFLICTING_DATA exige referencia CONTRADICTION y bloquea cálculo dependiente sin heurística. Registro referenciado conserva contexto/evidencias/valores/fechas/versiones/evaluaciones. Resolución posterior conserva contradicción histórica.

---

## 37. Error estructural vs incertidumbre

Error estructural: no finitos; KNOWN incompleto; cantidades físicas negativas; identidades/ámbitos/versiones incompatibles; IDs P-* físicos; conversión no demostrada; conflicto sin incidencia; selección de demanda incoherente; M01 sin reconstruibilidad; M02/M03 sin derivación; PYE-001 inválido; committed inconsistente; composición confirmada derivada incorrectamente; movimiento temporal inválido; falta reconciliación opening para reserva/other need; M06 incompleto; segmento/commitment duplicado; ramas M07 simultáneas; M07 fuera de vigencia; M08 aplicable sin exceso/evidencia; NO_APLICABLE no demostrado; ledger incompatible; plan sin IDs/referencias estables; ledger resultante que pierda/modifique previas; sobreconsumo pending; plan ≠ absorción.

Incertidumbre: ausencia/no evidencia, contradicción, selección/política histórica/forecast/configuración no verificables, movimiento potencialmente aplicable incompleto, demanda no aplicable o M08 no verificable.

---

## 38. Determinismo

Decimal; fechas explícitas; sin reloj; sin redondeo implícito; sin IDs aleatorios; sin prioridad M08; sin selección automática de demanda; sin calendarización de tasa. Misma entrada + contexto + selección + versiones + políticas + opening/M05 + ledger + plan → misma salida.

---

## 39. Defaults prohibidos

No hardcodear 15 %, 30/90 días, 10 %, 12 meses, 90 días, booleanos PYE-002…005, 15 días. Ausencia no activa catálogo.

---

## 40. Interfaces de autoridad

Evidence/QTG valida evidencia; Centro de Parametrización resuelve configuración; adaptadores suministran ámbito/normalización/reconciliación de obligaciones; política vigente suministra `DemandMethodSelection`; M02/M03 suministran valores autorizados; Rules evalúa reglas; CRC resuelve resultados incompatibles; MED integra. STK no decide.

R-STK-001: no inventar dependencias RDM pendientes. R-STK-004: limitado a M08 sobre M07.

---

## 41. Invariantes ejecutables

1. C0 inmutable; no decisión automática.
2. Ausencia ≠ cero; conflictos preservados.
3. Company/scope e identidad reproducibles.
4. IDs parámetros físicos correctos.
5. Selección de demanda KNOWN, versionada y registrada para todo resultado de demanda KNOWN.
6. Histórico/forecast coherentes con selección; forecast intervalo completo.
7. M02/M03 sin fórmula.
8. Stock actual/committed consistentes; composición comercial derivada exactamente.
9. M01 reconstruible; STK-006 exacto.
10. Coverage cero demanda → UNBOUNDED.
11. PYE-001 horizonte; PYE-002…006 sin función no autorizada.
12. Gate temporal previo a incertidumbre.
13. Opening reconciliation demostrada para reservas/other need.
14. M06 supply identity/proveedor/origen.
15. Segmentos/commitments evitan doble uso opening↔M05.
16. Proyección diaria, composición exacta por punto, métricas stateful.
17. M07 referencia/composición exactas, ramas/vigencia/autoridad.
18. M08 aplicabilidad probada, exceso real y horizonte común.
19. Ledger aislado; plan aporta IDs estables; motor no genera identidad aleatoria.
20. Resulting ledger preserva previas y añade exactamente plan.
21. Cero remaining → NO_APLICABLE; APLICABLE implica absorción >0.
22. M08 descuenta opening/M05/ledger, sin sobreconsumo.
23. Sin prioridad, heurística o defaults; determinismo.

---

## 42. Pruebas mínimas futuras

Cubrir selección de demanda ausente/incoherente/correcta; identidad/scope; IDs parámetros; M09/M10; M01; M02/M03; disponibilidad y composición exacta; historical policy; forecast intervalo; coverage; PYE; movimientos y opening_reconciliation; M06; propuesta; proyección/composición por punto; M07 y copia exacta; M08 cero remaining, aplicabilidad, plan IDs, colisión IDs, preservación ledger previo, overconsumption; no decisión/defaults/determinismo.

---

## 43. Exclusiones v0.1

Forecasting interno; ventas→demanda; tasa→calendario; cobertura proyectada sin autoridad; vigencia futura implícita; cutoff intradía; jerarquías/redistribución; EOQ; fórmula M02/M03; imputación; heurística; prioridad M08; persistencia ledger; SQL STK; API; cambios C0; CRC; decisión final.

---

## 44. Criterio de cierre

Solo `CERRADO` si Audit 2 Final independiente confirma M01…M10 implementables dentro de frontera, autoridad de selección registrada, ausencia/contradicción representables, identidad reproducible, no doble conteo opening/M05/M06/M08, determinismo de IDs/salidas, compatibilidad C0/Parametrización/Rules/CRC/MED, cero defaults no autorizados y **cero bloqueos**.

Hasta entonces no se crea `eios/stock` ejecutable.
