# EIOS — Stock & Demand Implementation Contract

## 1. Identidad

**Documento:** STK Implementation Contract  
**Versión:** 0.17  
**Estado:** DEPURADO P1 — PENDIENTE DE AUDIT 2 FINAL  
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

STK materializa únicamente semántica, relaciones y cálculos previamente autorizados. No crea reglas empresariales, parámetros, defaults normativos, forecasting implícito, calendarización implícita de demanda, autoridad paralela de evidencia ni decisiones automáticas.

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

Toda estructura con `state: StockDataState` incorpora `issue_refs` y `trace_refs`.

Reglas: `KNOWN` exige payload/traza completos; no se fabrican valores; ausencia/conflicto ≠ cero; `NOT_APPLICABLE` exige exclusión demostrada; cero exige evidencia; `CONFLICTING_DATA` referencia una contradicción M10 con ≥2 evidencias cuando siga sin resolver; resolución posterior conserva la incidencia histórica. STK-M10 no sustituye CRC ni autoridad documental.

---

## 5. Ámbito empresarial STK

```text
StockScope(company_id: str, operational_scope_id: str)
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

`KNOWN` exige método, política/versionado, fuente/traza y fecha aplicable igual a `evaluation_date`; la política demuestra aplicabilidad al artículo/ámbito. Selección no `KNOWN` → el motor no elige, promedia ni hace fallback.

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

Los cinco primeros proceden de C0 sin transformación. Toda composición exige afinidad exacta. La selección de demanda no bloquea cálculos independientes; operaciones que consumen demanda exigen afinidad con `context.demand_selection`.

Selección histórica `KNOWN` → forecast_version nula. Selección forecast `KNOWN` → forecast_version no nula. Selección no demostrada no se simula mediante una versión de forecast.

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

Solo `KNOWN + items=()` evidenciado significa vacío real. Colección no `KNOWN` no se suma parcialmente para fingir completitud.

---

## 9. Magnitud física normalizada

```text
NormalizedQuantity
├── scope
├── article_id
├── value: Decimal | null
├── unit
├── source_unit: str | null
├── normalization_ref: str | null
├── state
├── source_ref: str | null
├── effective_date: date | null
├── issue_refs
└── trace_refs
```

`KNOWN` exige valor finito no negativo, compatibilidad, unidad base, fecha cuando proceda, fuente/traza y unidad fuente; conversión exige referencia reproducible.

---

## 10. Umbrales M07

`AuthorizedQuantityThreshold` conserva ámbito/artículo, purpose `STOCK_MAXIMUM | EXCESS_TOLERANCE`, valor nullable, unidad, estado, fecha aplicable, authority_ref/version, fuente, incidencias y trazas. `KNOWN` exige valor finito no negativo, autoridad/versionado y fecha exacta.

---

## 11. Valores M02/M03 sin fórmula STK

`AuthorizedStockPolicyQuantity` conserva concepto `STOCK_MINIMUM | SAFETY_STOCK`, ámbito/artículo, cantidad/unidad/estado, política/versión, `derivation_ref`, vigencia, fuente, incidencias y trazas.

`KNOWN` exige cantidad finita no negativa, política/derivación/vigencia y evidencia. STK no calcula estos valores ni asume equivalencia mínimo↔safety.

---

## 12. Parámetros e IDs físicos

IDs físicos: `STK-001…006`, `PYE-001…006`. `P-STK-* / P-PYE-*` es notación documental.

`ConfiguredParameterValue` conserva parameter_id, company_id, valor tipado nullable, unidad, estado, parameters_version, applicable_reference_date, configuration/source/normalization refs, incidencias y trazas.

`KNOWN` exige configuración efectiva y compatible. Sin fallback a catálogo.

---

## 13. Frontera PYE v0.1

- `PYE-001`: horizonte M05.
- `PYE-002/003`: no son gates operativos v0.1.
- `PYE-004`: no deriva fechas desde lead_time.
- `PYE-005`: no transforma ventas en demanda.
- `PYE-006`: no es umbral directo de R-STK-001.

---

## 14. Horizonte M05 — PYE-001

```text
ProjectionHorizon(parameter, horizon_days: int | null, horizon_end: date | null, state, issue_refs, trace_refs)
```

`KNOWN`: PYE-001 efectivo en evaluación, entero positivo no booleano, unidad días normalizada:

```text
horizon_end = evaluation_date + horizon_days
```

Movimientos contribuyentes: `evaluation_date < effective_date <= horizon_end`. 90 días no es default.

---

## 15. Composición de compromiso de apertura

`StockCommitmentComponent` conserva commitment_id, optional confirmed_demand_id+demand_segment_id, ámbito/artículo, cantidad/unidad, normalización, fecha, fuente y trazas.

`commitment_id` único; cantidad finita no negativa; suma de composición KNOWN = stock_committed. Para compromiso comercial confirmado, confirmed_demand_id y segment son ambos obligatorios; fuera de ese caso ambos son nulos.

---

## 16. Demanda confirmada incorporada — derivación exacta

`IncorporatedDemandQuantity` conserva confirmed_demand_id, cantidad, unidad, conjunto único de demand_segment_ids y trazas.

En availability se deriva exclusivamente agrupando componentes committed comerciales. Un pedido aparece una sola vez; cantidad = suma exacta; segmentos = conjunto exacto. El llamador no suministra esta composición manualmente.

---

## 17. Disponibilidad

Input: contexto + stock_on_hand + stock_committed + committed_components.

Resultado KNOWN exige cantidades KNOWN, misma identidad/fecha y composición KNOWN exacta.

```text
stock_available = max(0, stock_on_hand - stock_committed)
availability_deficit = max(0, stock_committed - stock_on_hand)
```

`StockAvailabilityResult` conserva identidad, valores, unidad, estado, committed_components exactos, incorporated_confirmed_demand derivada, incidencias y trazas.

---

## 18. Consumo M01

`ConsumptionPeriod` conserva ámbito/artículo, periodo, días evidenciados, cantidad/unidad, estado, methodology_version, aggregation_ref, fuente, incidencias y trazas.

KNOWN exige consumo real mensual, cantidad finita no negativa, periodo completo, días exactos, metodología coincidente y agregación/normalización reconstruibles. Cero solo evidenciado.

---

## 19. Política histórica

`HistoricalDemandPolicy` conserva parámetro STK-006, required_periods, calendar ref nullable, extensión de aplicabilidad, source/applicability refs, estado, incidencias y trazas.

KNOWN: STK-006 efectivo, entero positivo no booleano, unidad mensual autorizada; calendario/fuente presentes; periodos completos, únicos/no solapados y consistentes. Extensión futura requiere fecha >= evaluación y referencia de autoridad.

---

## 20. Demanda histórica

Solo con selección KNOWN/HISTORICAL, política y colección KNOWN compatibles:

```text
historical_daily_demand = sum(quantity) / sum(evidenced_days)
```

Ventana exacta; no se acorta/rellena. Aplicabilidad = evaluación salvo extensión autorizada. Forecast refs nulas.

---

## 21. Forecast autorizado y demanda común

`AuthorizedForecastRate` conserva ámbito/artículo, daily_demand, unidad, estado, forecast_version, reference_date, applicable_from/to, horizon_ref, fuente, incidencias y trazas.

Forecast KNOWN: selección KNOWN/AUTHORIZED_FORECAST, tasa finita no negativa, versión exacta, fechas no nulas con `from <= reference <= to`, toda fecha consumidora dentro de intervalo, horizonte/fuente/traza.

`DemandRateResult` conserva identidad, `selection`, method, daily_demand, unidad, estado, reference/applicable dates, applicability/window/source refs, forecast_version, incidencias y trazas.

KNOWN exige selección exacta al contexto y método coincidente. Sin fallback.

---

## 22. Cobertura M04

`CoverageState = FINITE | UNBOUNDED | UNKNOWN | NOT_EVIDENCED | CONFLICTING_DATA`.

Con disponibilidad y demanda KNOWN aplicable a evaluación:

```text
coverage_days = stock_available / daily_demand  # >0
```

Demanda cero evidenciada → UNBOUNDED, valor nulo. Cobertura v0.1 usa stock disponible actual; no inventa cobertura proyectada.

---

## 23. Calendario autorizado de demanda para M05

STK **no** convierte por sí mismo `DemandRateResult` en salidas fechadas.

```text
DemandProjectionSchedule
├── selection: DemandMethodSelection
├── demand: DemandRateResult
├── state: StockDataState
├── schedule_from: date | null
├── schedule_to: date | null
├── demand_movement_ids: tuple[str, ...]
├── transformation_ref: str | null
├── reconciliation_ref: str | null
├── source_ref: str | null
├── issue_refs
└── trace_refs
```

Para `KNOWN`:

1. selección KNOWN e igual a `context.demand_selection`;
2. `demand` KNOWN, misma selección/identidad material y aplicable al horizonte;
3. `schedule_from == evaluation_date + 1`;
4. `schedule_to == horizon.horizon_end`;
5. `transformation_ref` identifica la transformación externa/autorizada que materializa la demanda seleccionada en movimientos fechados;
6. `reconciliation_ref` identifica el tratamiento autorizado que evita doble contabilización entre esa demanda, pedidos confirmados y reservas/obligaciones explícitas;
7. `demand_movement_ids` es único y representa exactamente los movimientos de demanda utilizados por esa reconciliación;
8. fuente/trazas suficientes.

Si falta transformación o reconciliación autorizada, el schedule no es KNOWN y una proyección que dependa de demanda no puede presentarse como completa KNOWN. STK no repite automáticamente una tasa diaria.

---

## 24. Movimientos M05/M06

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
├── source_kind: PENDING_ORDER | IN_TRANSIT | AUTHORIZED_DEMAND | CONFIRMED_DEMAND | RESERVATION | OTHER_AUTHORIZED_NEED | PROPOSED_PURCHASE
├── source_ref: str | null
├── issue_refs
└── trace_refs
```

Dirección:

- PENDING_ORDER / IN_TRANSIT / PROPOSED_PURCHASE → INFLOW;
- AUTHORIZED_DEMAND / CONFIRMED_DEMAND / RESERVATION / OTHER_AUTHORIZED_NEED → OUTFLOW.

Movimiento KNOWN contribuyente exige ID único, cantidad finita no negativa, compatibilidad, normalización/fuente/traza y fecha dentro del horizonte.

**Demanda:**

- `AUTHORIZED_DEMAND` representa demanda no confirmada comercialmente materializada por la transformación autorizada del schedule; no porta confirmed_demand_id ni demand_segment_id; su `movement_id` pertenece al schedule y su traza referencia `transformation_ref`.
- `CONFIRMED_DEMAND` representa pedido comercial confirmado; exige confirmed_demand_id + demand_segment_id y su `movement_id` pertenece al schedule/reconciliación; el segmento no se duplica con opening ni otro movimiento.
- El conjunto exacto de movimientos con source_kind AUTHORIZED_DEMAND o CONFIRMED_DEMAND debe coincidir con `DemandProjectionSchedule.demand_movement_ids` para una proyección KNOWN.
- `reconciliation_ref` demuestra que la combinación de demanda calendarizada + confirmada + reservas/obligaciones no duplica la misma necesidad; STK no inventa esa política.

**Gate temporal:** fecha evidenciada fuera del futuro/horizonte no contribuye/contamina; fecha dentro + incertidumbre contamina desde esa fecha; fecha no demostrable contamina desde evaluación; sin roll-forward.

**Opening reconciliation:** RESERVATION KNOWN exige commitment_id + opening_reconciliation_ref; OTHER_AUTHORIZED_NEED KNOWN exige opening_reconciliation_ref y commitment_id cuando corresponda a obligación identificable. ID ya en opening no se resta otra vez. No demostración de no solapamiento impide proyección completa KNOWN.

**M06:** pending/transit KNOWN exige supply identity, proveedor, origen, fecha, cantidad/unidad/evidencia. Misma cantidad no ocupa ambos estados; recepción confirmada sale M06.

Propuesta exige escenario, cantidad normalizada, fecha futura y traza; no presume aprobación.

---

## 25. Proyección M05

```text
StockProjectionInput
├── context
├── opening: StockAvailabilityResult
├── movements: CollectionEnvelope[ProjectionMovement]
├── horizon: ProjectionHorizon
├── demand_schedule: DemandProjectionSchedule
└── scenario_id
```

Resultado completo KNOWN exige:

- escenario/horizonte/opening compatibles;
- `demand_schedule` KNOWN, compatible con contexto/horizonte;
- igualdad exacta entre `demand_schedule.demand_movement_ids` y los movement_id de `AUTHORIZED_DEMAND | CONFIRMED_DEMAND` presentes en la colección;
- movimientos aplicables válidos;
- sin duplicación de segmentos, commitments o necesidades según las referencias de reconciliación.

Por día futuro:

```text
closing = previous_closing + inflows(date) - outflows(date)
```

Sin orden intradía; saldo negativo preservado.

`ProjectionPoint` conserva fecha, projected_stock nullable, estado, incorporated_confirmed_demand, incidencias y trazas.

**Composición confirmada exacta:** primer punto parte de opening; añade exclusivamente `CONFIRMED_DEMAND` contabilizados hasta su fecha; cada movimiento añade exactamente su cantidad y segmento; no incluye AUTHORIZED_DEMAND genérica ni movimientos posteriores.

`ProjectedDecimalMetric` y `ProjectedDateMetric` conservan valor nullable + estado + incidencias/trazas.

`StockProjectionResult` conserva identidad, horizonte, points, minimum_projected_stock, depletion_date, composición confirmada del horizonte, estado, incidencias y trazas. La composición de horizonte = último punto exactamente.

Mínimo solo KNOWN con horizonte completamente determinable. Depletion conocida solo sin incertidumbre previa que pueda adelantarla; opening cero → evaluación; horizonte conocido sin agotamiento → NOT_APPLICABLE.

---

## 26. Frontera R-STK-001 / M02 / M03

STK entrega proyección/movimientos, no evalúa R-STK-001 ni inventa dependencias RDM pendientes. M02/M03 permanecen valores autorizados sin fórmula STK.

---

## 27. Referencia M07

`StockReferenceValue(CURRENT_AVAILABLE | PROJECTED)` conserva identidad, fecha, valor nullable, unidad, estado, composición confirmada, fuente, incidencias/trazas.

CURRENT copia disponibilidad/composición opening. PROJECTED copia exactamente valor/estado/composición del punto seleccionado.

---

## 28. Máximo y tolerancia M07

`StockMaximumBasis`: unión exclusiva DIRECT_QUANTITY o COVERAGE_MAXIMUM. Direct usa threshold STOCK_MAXIMUM. Coverage usa STK-004 + DemandRateResult KNOWN compatible/aplicable y demanda >0:

```text
stock_maximum = coverage_maximum_days * authorized_daily_demand
```

`ExcessToleranceBasis`: QUANTITY o RATE exclusivos. QUANTITY usa threshold EXCESS_TOLERANCE. RATE usa STK-005 normalizado:

```text
excess_tolerance_quantity = stock_maximum * normalized_rate
```

---

## 29. Exceso M07

`ExcessState = NO_EXCESS | WITHIN_TOLERANCE | EXCESS | UNKNOWN | NOT_EVIDENCED | CONFLICTING_DATA`.

```text
excess_threshold = stock_maximum + tolerance
excess_quantity = max(0, stock_reference.value - excess_threshold)
```

`ExcessResult` conserva identidad, referencia, máximo, tolerancia, threshold, exceso, estado, incorporated_confirmed_demand, incidencias y trazas.

Invariante: composición de ExcessResult = composición de stock_reference exactamente. Relaciones confirmadas: STK-004→R-STK-002/003; STK-005→R-STK-003.

---

## 30. M08 — demanda confirmada

`ConfirmedDemandRecord` conserva confirmed_demand_id, order/customer, ámbito/artículo, pending_quantity, fechas, estado negocio, applicability state/source, fuente, incidencias y trazas.

Colección KNOWN vacía = NO_EXISTE.

APLICABLE_Y_VALIDADA exige exceso EXCESS, atributos completos, pending KNOWN vigente, fechas coherentes, entrega posterior a referencia de exceso y dentro de horizonte. NO_APLICABLE exige exclusión demostrada. Falta que impida demostrarla → NO_VERIFICABLE con incidencias.

---

## 31. Ledger M08

`AllocationLedgerEntry` conserva entry_id, confirmed_demand_id, ámbito/artículo, cantidad/unidad, decision/scenario, fecha exceso, allocation_result_ref y trazas.

`AllocationLedgerSnapshot` conserva fecha, ámbito/artículo, estado, entries, fuente, incidencias/trazas. KNOWN exige fecha/ámbito/artículo correctos, fuente/traza, IDs únicos y entries compatibles. KNOWN vacío evidenciado = cero asignaciones activas.

---

## 32. Plan M08 determinista

```text
DemandAllocation
├── allocation_entry_id
├── confirmed_demand_id
├── quantity_to_apply
├── unit
├── allocation_source_ref
└── trace_refs
```

Cantidad >0; ID único/no colisiona con ledger; motor no genera IDs; nueva ledger entry reutiliza ID y `allocation_result_ref == allocation_source_ref`; decisión/scenario/fecha exceso derivan del scope.

---

## 33. Reconciliación opening/M05/M08

```text
remaining_allocatable = pending_quantity
                      - incorporated_before_M08
                      - already_allocated
```

Incorporated procede de ExcessResult/composición exacta. Already allocated del ledger activo KNOWN. Misma unidad y suma previa <= pending; si no, contradicción, no suelo cero.

---

## 34. Alcance M08

AllocationScope conserva identidad, ámbito/artículo, evaluación, fecha de exceso y ProjectionHorizon KNOWN PYE-001. No existe horizon paralelo. Exceso proyectado usa mismo horizonte de proyección origen.

---

## 35. Absorción M08 y ledger resultante

Solo pedidos aplicables, mismo ámbito/artículo/unidad, pending vigente y entrega dentro del horizonte participan.

`total_remaining_applicable = sum(remaining_allocatable)`.

Con EXCESS y total 0 → NO_APLICABLE, absorción 0, residual = exceso, plan vacío, sin entries nuevas.

APLICABLE exige total >0, absorbed = min(exceso,total) >0, residual = max(0,exceso-absorbed), plan suma exactamente absorbed.

Resulting ledger KNOWN conserva cada entry activa previa una vez e inalterada, añade exactamente una por plan usando IDs/referencias aportados, IDs únicos, suma nueva por pedido = plan, no elimina previas. Sin nueva asignación es semánticamente igual al input ledger.

`ConfirmedDemandAbsorptionResult` conserva identidad, excess_result, business_state, total/absorbed/residual, plan, resulting_ledger, incidencias/trazas. M08 no reescribe M07.

---

## 36. M09 — ausencia

Sin imputación. Ausencia no se sustituye por cero/media/último/default. MISSING_DATA se conserva cuando exista registro. Selección de demanda conocida sin schedule autorizado produce incertidumbre de proyección, no omisión silenciosa.

---

## 37. M10 — contradicciones

CONFLICTING_DATA exige referencia CONTRADICTION y bloquea cálculo dependiente sin heurística. Registro preserva contexto/evidencias/valores/fechas/versiones/evaluaciones. Resolución posterior conserva historia.

---

## 38. Error estructural vs incertidumbre

Error estructural: no finitos; KNOWN incompleto; cantidades físicas negativas; identidades/ámbitos/versiones incompatibles; IDs P-* físicos; conversión no demostrada; conflicto sin incidencia; selección incoherente; M01 no reconstruible; M02/M03 sin derivación; PYE-001 inválido; committed/composición incorrectos; demand schedule KNOWN incoherente con selección/horizonte/movimientos; demanda genérica con IDs comerciales o confirmada sin IDs; movimiento temporal inválido; falta reconciliation opening; M06 incompleto; segmento/commitment duplicado; ramas M07 simultáneas; M07 fuera vigencia; M08 aplicable sin exceso/evidencia; NO_APLICABLE no demostrado; ledger incompatible; plan sin IDs/referencias; resulting ledger destructivo; sobreconsumo; plan ≠ absorción.

Incertidumbre: ausencia/no evidencia, contradicción, selección/política/forecast/configuración no verificables, falta de transformación/reconciliación de demanda, movimiento potencialmente aplicable incompleto, M08 no verificable.

---

## 39. Determinismo

Decimal; fechas explícitas; sin reloj/redondeo implícito; sin IDs aleatorios; sin prioridad M08; sin selección automática; **sin calendarización automática de tasa**. Misma entrada + contexto + selección + schedule + versiones + políticas + opening/M05 + ledger + plan → misma salida.

---

## 40. Defaults prohibidos

No hardcodear 15 %, 30/90 días, 10 %, 12 meses, 90 días, booleanos PYE-002…005, 15 días. Ausencia no activa catálogo.

---

## 41. Interfaces de autoridad

Evidence/QTG valida evidencia; Centro de Parametrización resuelve configuración; adaptadores suministran ámbito/normalización/reconciliación de obligaciones; política vigente suministra DemandMethodSelection; un componente/adaptador autorizado puede suministrar DemandProjectionSchedule y su transformación/reconciliación; STK valida y consume, no inventa esa política. M02/M03 suministran valores; Rules evalúa; CRC resuelve resultados; MED integra. STK no decide.

R-STK-001: no inventar dependencias RDM pendientes. R-STK-004: limitado a M08 sobre M07.

---

## 42. Invariantes ejecutables

1. C0 inmutable; no decisión automática.
2. Ausencia ≠ cero; conflictos preservados.
3. Company/scope/identidad reproducibles.
4. IDs parámetros físicos correctos.
5. Selección de demanda autorizada/versionada para demanda KNOWN.
6. Histórico/forecast coherentes; forecast intervalo completo.
7. M02/M03 sin fórmula.
8. Stock/committed y composición comercial exactos.
9. M01 reconstruible; STK-006 exacto.
10. Coverage cero demanda → UNBOUNDED.
11. PYE-001 horizonte; PYE-002…006 sin función no autorizada.
12. Proyección KNOWN exige DemandProjectionSchedule KNOWN; tasa nunca se calendariza implícitamente.
13. AUTHORIZED_DEMAND genérica ≠ CONFIRMED_DEMAND; schedule reconcilia ambas con reservas.
14. Gate temporal antes de incertidumbre.
15. Opening reconciliation para reservas/other need.
16. M06 identity/proveedor/origen.
17. Segmentos/commitments evitan doble uso opening↔M05.
18. Proyección diaria/composición exacta/métricas stateful.
19. M07 referencia/composición exactas y ramas/vigencia.
20. M08 aplicabilidad/exceso/horizonte probados.
21. Ledger aislado; plan aporta IDs; resulting ledger preserva previas.
22. Cero remaining → NO_APLICABLE; APLICABLE implica absorción >0.
23. M08 descuenta opening/M05/ledger sin sobreconsumo.
24. Sin prioridad, heurística o defaults; determinismo.

---

## 43. Pruebas mínimas futuras

Cubrir selección demanda; schedule ausente/unknown/known; mismatch schedule↔movimientos; generic vs confirmed demand; reconciliación; identidad/scope; parámetros; M09/M10; M01; M02/M03; availability; historical/forecast; coverage; PYE; movimientos/M06/opening reconciliation; proyección/composición; M07; M08/ledger/plan; no decisión/defaults/determinismo.

---

## 44. Exclusiones v0.1

Forecasting interno; ventas→demanda; **definición de la política de calendarización/reconciliación de demanda**; cobertura proyectada sin autoridad; vigencia futura implícita; cutoff intradía; jerarquías/redistribución; EOQ; fórmula M02/M03; imputación; heurística; prioridad M08; persistencia ledger; SQL STK; API; cambios C0; CRC; decisión final.

---

## 45. Criterio de cierre

Solo `CERRADO` si Audit 2 Final independiente confirma M01…M10 implementables dentro de frontera, demanda para M05 no omitida ni calendarizada implícitamente, ausencia/contradicción representables, identidad reproducible, no doble conteo opening/M05/M06/M08, determinismo de IDs/salidas, compatibilidad C0/Parametrización/Rules/CRC/MED, cero defaults no autorizados y **cero bloqueos**.

Hasta entonces no se crea `eios/stock` ejecutable.
