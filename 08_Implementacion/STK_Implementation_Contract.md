# EIOS — Stock & Demand Implementation Contract

## 1. Identidad

**Documento:** STK Implementation Contract  
**Versión:** 0.10  
**Estado:** DEPURADO FINAL OPENING/M08 — PENDIENTE DE AUDIT 2 FINAL  
**Baseline de origen:** `main @ c2bd5b9b73974426d29cc234ffda42d494e720fb`  
**Dominio:** Capa 3 — Stock / Demanda  
**Autoridad metodológica:** `01_Modelo/Stock_Demand_Methodological_Matrix.md` v1.1  
**Autoridad de entrada:** `01_Modelo/STK_Contract_Entry_Authority.md` v1.0  
**Autoridad de reglas:** `04_Reglas/Matriz_Reglas_MVP.md` v2.1  
**Dependencias:** `04_Reglas/Rule_Dependency_Matrix.md` v1.4  
**Autoridad de parametrización:** `08_Implementacion/Centro_Parametrizacion_Implementation_Contract.md` v1.2

---

## 2. Propósito y frontera

Define la frontera física mínima implementable de **Stock & Demand Intelligence (STK) v0.1**. Solo materializa semántica, relaciones y cálculos previamente autorizados.

STK no crea reglas empresariales, parámetros, defaults normativos, forecasting implícito, autoridad paralela de evidencia ni decisiones automáticas. Rules conserva R-STK-001…004; CRC conserva resolución de conflictos; MED conserva integración; la autoridad decisional final permanece humana.

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

Sin dependencias circulares con `eios.core`.

---

## 4. Identidad y temporalidad

La fecha canónica STK es `evaluation_date`. La proyección v0.1 tiene granularidad diaria; no se infiere secuencia intradía.

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

Los identificadores canónicos se derivan sin transformación de `DecisionContext`; `forecast_version` expresa dependencia de forecast cuando existe. Los consumidores exigen compatibilidad exacta de identidad.

---

## 5. Estados y colecciones

Estados STK:

```text
KNOWN
UNKNOWN
NOT_EVIDENCED
NOT_APPLICABLE
CONFLICTING_DATA
```

`state != KNOWN` no presenta valor determinado. `UNKNOWN / NOT_EVIDENCED / CONFLICTING_DATA ≠ 0`. Todo `KNOWN` exige fuente o traza.

```text
CollectionEnvelope[T]
├── state: KNOWN | UNKNOWN | NOT_EVIDENCED | CONFLICTING_DATA
├── items: tuple[T, ...]
├── source_ref: str | null
└── trace_refs: tuple[str, ...]
```

Solo `KNOWN + items=()` trazable significa vacío evidenciado.

---

## 6. Magnitudes y umbrales

```text
NormalizedQuantity
├── article_id
├── value: Decimal | null
├── unit
├── state
├── source_ref
├── effective_date: date | null
└── trace_refs
```

Representa magnitud física. `KNOWN`: finita, no negativa y trazable. No representa saldo proyectado ni umbral empresarial.

```text
AuthorizedQuantityThreshold
├── article_id
├── purpose: STOCK_MAXIMUM | EXCESS_TOLERANCE
├── value: Decimal | null
├── unit
├── state
├── applicable_reference_date
├── source_ref
└── trace_refs
```

`KNOWN`: finito, no negativo, trazable, propósito correcto y fecha exactamente aplicable a la referencia consumidora. No adquiere vigencia futura por inferencia.

---

## 7. Contexto y método de demanda

```text
StockComputationContext
├── decision_context: DecisionContext
├── article_id
├── evaluation_date
├── base_unit
├── methodology_version
└── forecast_version: str | null
```

- `AUTHORIZED_FORECAST` exige `forecast_version != null`.
- `HISTORICAL_CONSUMPTION` exige `forecast_version == null`.
- No se arrastra una versión de forecast a método histórico por disponibilidad técnica.

---

## 8. Parámetros configurados

```text
ConfiguredParameterValue
├── parameter_id
├── value: Decimal | int | bool | null
├── unit
├── state
├── parameters_version
├── applicable_reference_date
├── configuration_ref
├── source_ref
├── normalization_ref: str | null
└── trace_refs
```

STK consume configuración efectiva resuelta por el Centro de Parametrización; no reimplementa vigencia ni zonas horarias. `KNOWN` exige versión coincidente, configuración efectiva identificada, fecha aplicable correcta y tipo/unidad compatibles. Sin fallback a valores iniciales.

---

## 9. Composición de compromiso de apertura

```text
StockCommitmentComponent
├── commitment_id: str
├── demand_segment_id: str | null
├── confirmed_demand_id: str | null
├── article_id: str
├── quantity: Decimal
├── unit: str
├── effective_date: date
├── source_ref: str
└── trace_refs: tuple[str, ...]
```

Reglas:

1. cantidad finita y no negativa;
2. mismo artículo/unidad/fecha que `stock_committed`;
3. `commitment_id` único;
4. si representa reserva/asignación vinculada a demanda comercial confirmada, `confirmed_demand_id` y `demand_segment_id` son obligatorios;
5. `demand_segment_id` es estable, trazable y único dentro de la composición;
6. un compromiso no comercial no recibe IDs de demanda inventados;
7. una composición `KNOWN` debe sumar exactamente `stock_committed.value`.

Esto no convierte automáticamente un pedido confirmado en compromiso: solo registra reservas/asignaciones físicas ya evidenciadas.

---

## 10. Demanda confirmada ya incorporada

```text
IncorporatedDemandQuantity
├── confirmed_demand_id: str
├── quantity: Decimal
├── unit: str
├── demand_segment_ids: tuple[str, ...]
└── trace_refs: tuple[str, ...]
```

Se agrega por `confirmed_demand_id`, preservando los segmentos que originaron la cantidad. Cantidad finita/no negativa; unidad única; IDs de segmento sin duplicados.

---

## 11. Disponibilidad de stock

```text
StockAvailabilityInput
├── context
├── stock_on_hand: NormalizedQuantity
├── stock_committed: NormalizedQuantity
└── committed_components: CollectionEnvelope[StockCommitmentComponent]
```

Para resultado `KNOWN`:

- `stock_on_hand` y `stock_committed` son `KNOWN`;
- artículo/unidad coinciden con contexto;
- ambas fechas = `evaluation_date`;
- `committed_components` es `KNOWN` y trazable;
- componentes compatibles, fechados en `evaluation_date` y sin IDs duplicados;
- suma de componentes = `stock_committed.value`.

```text
stock_available = max(0, stock_on_hand - stock_committed)
availability_deficit = max(0, stock_committed - stock_on_hand)
```

```text
StockAvailabilityResult
├── identity: StockResultIdentity
├── stock_on_hand
├── stock_committed
├── stock_available
├── availability_deficit
├── incorporated_confirmed_demand: tuple[IncorporatedDemandQuantity, ...]
├── state
└── trace_refs
```

`incorporated_confirmed_demand` se deriva solo de componentes vinculados a demanda confirmada. El déficit permanece visible. Sin tolerancia implícita de antigüedad.

---

## 12. Consumo M01

```text
ConsumptionPeriod
├── article_id
├── period_id
├── period_start
├── period_end
├── evidenced_days
├── quantity
├── unit
├── state
├── source_ref
└── trace_refs
```

Consumo real, no ventas/forecast. `KNOWN` exige cantidad no negativa, periodo completo y trazable. Cero solo si está evidenciado.

---

## 13. Política y demanda histórica

```text
RequiredPeriodSpec
├── period_id
├── period_start
└── period_end
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

`P-STK-006`: `KNOWN`, versión/fecha efectiva correctas, entero positivo no booleano, unidad meses/periodos mensuales autorizada o normalizada. IDs únicos, intervalos válidos/no solapados y calendario trazable. Extensión futura solo con autoridad explícita.

Demanda histórica `KNOWN`: colección `KNOWN`, correspondencia exacta uno-a-uno de IDs/intervalos, periodos homogéneos y completos:

```text
evidenced_days == (period_end - period_start).days + 1
historical_daily_demand = sum(quantity) / sum(evidenced_days)
```

No se acorta, rellena ni duplica la ventana.

```text
applicable_from = evaluation_date
applicable_to = extended_applicable_to or evaluation_date
context.forecast_version = null
```

---

## 14. Demanda común y forecast

```text
DemandRateResult
├── identity
├── method: HISTORICAL_CONSUMPTION | AUTHORIZED_FORECAST
├── daily_demand
├── unit
├── state
├── reference_date
├── applicable_from
├── applicable_to
├── applicability_source_ref
├── window_or_horizon
├── source_ref
├── forecast_version: str | null
└── trace_refs
```

Forecast autorizado conserva artículo, tasa, unidad, horizonte, estado, versión, fuente y traza.

Forecast `KNOWN`:

```text
context.forecast_version != null
context.forecast_version == forecast.forecast_version
identity.forecast_version == forecast.forecast_version
DemandRateResult.forecast_version == forecast.forecast_version
```

Histórico: las tres referencias de forecast son nulas. No forecasting interno, ventas→demanda ni fallback.

---

## 15. Cobertura M04

La tasa debe ser aplicable a `evaluation_date` y compartir identidad compatible.

```text
coverage_days = stock_available / daily_demand    # daily_demand > 0
```

Cero confirmado/evidenciado/aplicable → `UNBOUNDED`, `coverage_days = null`. Sin infinito numérico.

---

## 16. Movimientos M05/M06

```text
ProjectionMovement
├── movement_id
├── supply_identity: str | null
├── confirmed_demand_id: str | null
├── demand_segment_id: str | null
├── scenario_id: str | null
├── article_id
├── direction: INFLOW | OUTFLOW
├── quantity
├── unit
├── effective_date
├── state
├── source_kind: PENDING_ORDER | IN_TRANSIT | AUTHORIZED_DEMAND | RESERVATION | OTHER_AUTHORIZED_NEED | PROPOSED_PURCHASE
├── source_ref
└── trace_refs
```

Dirección:

```text
PENDING_ORDER | IN_TRANSIT | PROPOSED_PURCHASE → INFLOW
AUTHORIZED_DEMAND | RESERVATION | OTHER_AUTHORIZED_NEED → OUTFLOW
```

Movimiento `KNOWN` contribuyente: ID único, cantidad finita/no negativa, artículo/unidad compatibles, traza y:

```text
evaluation_date < effective_date <= horizon_end
```

Sin cutoff intradía ni roll-forward. `NOT_APPLICABLE` evidenciado no contribuye/contamina; otros estados no determinados propagan incertidumbre.

Para `AUTHORIZED_DEMAND` procedente de demanda comercial confirmada, `confirmed_demand_id` y `demand_segment_id` son obligatorios. Un segmento no puede aparecer más de una vez entre movimientos ni coincidir con un segmento ya incorporado en opening. Distintos segmentos del mismo pedido son admisibles si están identificados y trazados.

M06 exige `supply_identity` estable/único; parcialidades identificadas; no pendiente+tránsito simultáneo; recepción confirmada sale M06.

`PROPOSED_PURCHASE` exige escenario coincidente, cantidad normalizada, fecha futura y traza; no presume aprobación.

---

## 17. Proyección M05

```text
StockProjectionInput
├── context
├── opening_availability: StockAvailabilityResult
├── movements: CollectionEnvelope[ProjectionMovement]
├── horizon_end
├── horizon_source_ref
├── horizon_trace_refs
└── scenario_id
```

Escenario coincidente; horizonte trazable; opening `KNOWN` e identidad compatible; movimientos `KNOWN` estrictamente futuros y dentro del horizonte.

Antes de calcular se valida que ningún `demand_segment_id` confirmado aparezca simultáneamente en opening y movimientos M05.

Para cada fecha futura:

```text
closing_stock_date = opening_stock_date
                   + sum(known applicable inflows)
                   - sum(known applicable outflows)
```

Sin orden intradía. Saldo negativo se conserva.

La composición acumulada de demanda confirmada parte de opening y añade exclusivamente segmentos M05 efectivamente contabilizados, agregados por `confirmed_demand_id`.

Incertidumbre fechada contamina desde su fecha; sin fecha, desde evaluación; `NOT_APPLICABLE` no contamina; datos posteriores no restauran `KNOWN`.

```text
minimum_projected_stock = min(opening_stock, determined daily closings)
```

Opening cero `KNOWN` → `depletion_date = evaluation_date`; si no, primera fecha futura determinada con cierre `<= 0`.

---

## 18. Frontera R-STK-001 / M02 / M03

STK entrega métricas/evidencia, no decisiones. v0.1 no calcula `stock_minimum` ni `safety_stock` con fórmula propia porque no existe fórmula cuantitativa autorizada. Ausencia ≠ cero. Valores iniciales no son defaults.

---

## 19. Referencia de stock M07

```text
StockReferenceValue
├── identity
├── reference_kind: CURRENT_AVAILABLE | PROJECTED
├── reference_date
├── value
├── unit
├── state
├── incorporated_confirmed_demand: tuple[IncorporatedDemandQuantity, ...]
├── source_ref
└── trace_refs
```

`CURRENT_AVAILABLE` deriva de `StockAvailabilityResult`, fecha = evaluación, valor no negativo y conserva exactamente la demanda confirmada ya incorporada en `stock_committed`.

`PROJECTED` deriva de punto M05, puede ser negativo y conserva opening + movimientos confirmados acumulados hasta `reference_date` sin duplicar segmentos.

---

## 20. Base máximo y tolerancia M07

`StockMaximumBasis` tiene ramas exclusivas `DIRECT_QUANTITY` (`AuthorizedQuantityThreshold` purpose `STOCK_MAXIMUM`) o `COVERAGE_MAXIMUM` (`P-STK-004 + DemandRateResult`). Todo debe ser `KNOWN`, compatible y aplicable a `stock_reference.reference_date`; cobertura exige demanda > 0 y temporalmente aplicable.

```text
stock_maximum = coverage_maximum_days * authorized_daily_demand
```

`ExcessToleranceBasis` tiene ramas exclusivas `QUANTITY` (`AuthorizedQuantityThreshold` purpose `EXCESS_TOLERANCE`) o `RATE` (`P-STK-005` normalizado/trazado). Fecha efectiva = referencia. Sin inferencia porcentual.

```text
excess_tolerance_quantity = stock_maximum * normalized_rate
```

---

## 21. Exceso M07

```text
excess_threshold = stock_maximum + excess_tolerance_quantity
excess_quantity = max(0, stock_reference.value - excess_threshold)
```

Estados: `NO_EXCESS | WITHIN_TOLERANCE | EXCESS | UNKNOWN | NOT_EVIDENCED | CONFLICTING_DATA`.

M07 conserva identidad, referencia/fecha, composición incorporada de demanda confirmada, máximo, tolerancia, umbral, exceso y trazas. No reañade M06/propuesta.

Únicas relaciones parámetro↔regla confirmadas: `P-STK-004→R-STK-002`; `P-STK-004→R-STK-003` derivada; `P-STK-005→R-STK-003` derivada.

---

## 22. M08 — demanda confirmada

```text
ConfirmedDemandRecord
├── confirmed_demand_id
├── order_id
├── customer_id
├── article_id
├── pending_quantity: NormalizedQuantity
├── order_date
├── confirmation_date
├── expected_delivery_date
├── business_status
├── applicability_state: NO_APLICABLE | APLICABLE_Y_VALIDADA | NO_VERIFICABLE
├── applicability_source_ref
├── source_ref
└── trace_refs
```

Solo colección `KNOWN` vacía/trazada significa `NO_EXISTE`.

Para `APLICABLE_Y_VALIDADA`:

```text
pending_quantity.state == KNOWN
pending_quantity.effective_date == allocation_scope.evaluation_date
order_date <= confirmation_date <= allocation_scope.evaluation_date
allocation_scope.evaluation_date <= expected_delivery_date <= allocation_scope.horizon_end
```

Fecha prevista vencida sin evidencia vigente de actualización no se desplaza ni reutiliza como futura. Cambios/cancelaciones/parcialidades requieren evidencia vigente.

---

## 23. Ledger M08 con procedencia

```text
AllocationLedgerEntry
├── confirmed_demand_id
├── allocated_quantity
├── unit
├── decision_id
├── scenario_id
├── excess_reference_date
├── allocation_result_ref
└── trace_refs
```

Cada entrada conserva el escenario/exceso que originó la asignación. `allocation_result_ref` referencia de forma trazable el resultado original. El ledger puede agregarse por pedido para impedir reutilización sin perder procedencia.

```text
DemandAllocation
├── confirmed_demand_id
├── quantity_to_apply
├── unit
├── allocation_source_ref
└── trace_refs
```

No existe prioridad implícita.

---

## 24. Reconciliación opening/M05/M08

Para cada pedido aplicable:

```text
incorporated_before_M08
= cantidad del confirmed_demand_id ya incorporada
  en stock_reference.incorporated_confirmed_demand

already_allocated
= suma de cantidades del confirmed_demand_id
  en allocation_ledger

remaining_allocatable
= pending_quantity
  - incorporated_before_M08
  - already_allocated
```

Reglas:

- misma unidad;
- cantidades >= 0;
- `incorporated_before_M08 + already_allocated <= pending_quantity`;
- si excede `pending_quantity`, no se aplica suelo cero: se rechaza como inconsistencia/contradicción;
- una misma cantidad no se usa dos veces entre opening, M05 y M08;
- no existe prioridad implícita de reparto.

---

## 25. Alcance y absorción M08

```text
AllocationScope
├── decision_id
├── scenario_id
├── article_id
├── evaluation_date
├── excess_reference_date
├── horizon_end
├── horizon_source_ref
└── trace_refs
```

Debe ser compatible con identidad STK y `ExcessResult.reference_date`; horizonte explícito/trazable.

Solo pedidos `APLICABLE_Y_VALIDADA`, mismo artículo/unidad, pending `KNOWN` vigente y entrega dentro del horizonte participan. IDs únicos. Ledger/plan solo IDs presentes. Plan no puede superar `remaining_allocatable`. Colección no `KNOWN` hace M08 no evaluable. STK no elige reparto.

```text
total_remaining_applicable = sum(remaining_allocatable aplicable)
absorbed_excess = min(excess_quantity, total_remaining_applicable)
residual_excess = max(0, excess_quantity - absorbed_excess)
```

Materialización por pedido exige:

```text
sum(allocation_plan.quantity_to_apply) == absorbed_excess
```

Si `absorbed_excess == 0`, plan vacío. Si `absorbed_excess > 0`, plan ausente/incompleto/sobreasignado bloquea reparto; no se inventa.

Ledger de salida suma únicamente cantidades del plan y conserva la procedencia de cada nueva asignación. M08 conserva exceso original, total aplicable, absorbido, residual, plan, ledger, identidad y trazas; no reescribe M07.

---

## 26. M09 — ausencia

Sin imputación. Ausencia no se sustituye por cero, media, último valor, estimación o default. La incertidumbre y fuente esperada se conservan y propagan a los cálculos dependientes.

---

## 27. M10 — contradicciones

`CONFLICTING_DATA` bloquea cálculo dependiente sin resolución por recencia, máximo, mínimo, promedio, score o prioridad arbitraria. Una resolución externa autorizada conserva evidencia original y autoridad aplicada.

---

## 28. Error estructural vs incertidumbre

Se rechaza estructuralmente, entre otros:

- Decimal no finito;
- cantidad física negativa;
- identidad/versiones incompatibles;
- histórico con `forecast_version` no nula o forecast con versión nula/diferente;
- stock actual de otra fecha;
- composición de `stock_committed` incompleta, inconsistente o duplicada;
- `demand_segment_id` repetido entre opening y M05;
- movimiento `KNOWN` no estrictamente futuro o fuera de horizonte;
- IDs incompatibles/duplicados;
- configuración efectiva incorrecta;
- ventana histórica inválida;
- umbral/demanda fuera de vigencia;
- ramas discriminadas simultáneas;
- pending M08 no vigente en `evaluation_date`;
- fechas de pedido/confirmación/entrega incompatibles;
- `incorporated + allocated > pending`;
- ledger sin procedencia o plan M08 inválido.

Se representa como incertidumbre empresarial: ausencia/no evidencia, contradicción, colección no evidenciada, forecast/configuración/umbral no verificables, demanda no temporalmente aplicable, composición no verificable cuando no sea un error de input cerrado, y M08 no verificable.

---

## 29. Determinismo

Decimal; no NaN/infinito; fechas explícitas; sin reloj; sin redondeo empresarial implícito; sin prioridad M08; misma entrada + identidad/versiones/configuración + composición opening/M05 + ledger → mismo resultado.

---

## 30. Defaults prohibidos

No se hardcodean: 15 % safety stock; 30/90 días; 10 % tolerancia; 12 meses; 90 días de horizonte; `PYE-002…005 = Sí`; 15 días. Ausencia de configuración no activa valores iniciales.

---

## 31. Interfaces de autoridad

Evidence/QTG valida evidencia; Centro de Parametrización resuelve configuración; Rules consume hechos STK; CRC queda fuera; TCO no recibe costes derivados STK v0.1; Decision Twin no mezcla escenarios/versiones; MED integra sin transferir autoridad. `R-STK-004` queda limitado a M08 sobre exceso M07 y no se amplía a cobertura elevada por interpretación.

---

## 32. Invariantes ejecutables

1. No decisión automática; C0 inmutable.
2. Ausencia ≠ cero; `KNOWN` exige traza; vacío evidenciado ≠ ausencia.
3. Magnitud física ≠ umbral.
4. Identidad conserva decision/scenario/rules/parameters/snapshot y forecast cuando aplica.
5. Histórico exige `forecast_version` nula; forecast exige versión exacta no nula.
6. Stock actual pertenece a `evaluation_date`; déficit visible.
7. `stock_committed` KNOWN tiene composición completa y reconciliada.
8. Demanda confirmada ya descontada en opening queda identificada cuantitativamente.
9. Demanda histórica/forecast son métodos exclusivos; ventas ≠ demanda; sin fallback.
10. Aplicabilidad temporal de demanda explícita.
11. P-STK-006 versión/fecha/unidad; ventana histórica exacta/completa.
12. Coverage consume demanda aplicable.
13. `movement_id` único; `supply_identity` evita doble conteo M06.
14. Movimiento contribuyente estrictamente futuro; sin cutoff intradía.
15. `demand_segment_id` evita doble uso opening↔M05 y permite parcialidades legítimas.
16. source kind/dirección compatibles; `NOT_APPLICABLE` no contamina.
17. Tasa no crea calendario; propuesta exige escenario.
18. Horizonte trazable; proyección diaria; saldo negativo preservado; incertidumbre temporal.
19. Opening cero → `depletion_date=evaluation_date`; mínimo incluye opening.
20. Composición confirmada de M05 se acumula cuantitativamente por pedido/segmento.
21. M07 conserva composición y no reañade entradas.
22. Umbrales directos usan tipo autorizado; P-STK-004/P-STK-005 solo para fecha resuelta.
23. Coverage maximum exige demanda >0 aplicable; ramas exclusivas; tolerancia RATE trazada.
24. M08 usa pending vigente en fecha de evaluación y fechas comerciales coherentes.
25. M08 descuenta cantidades ya incorporadas en opening/M05 y ledger previo.
26. `incorporated + allocated` nunca supera pending; no suelo cero ante inconsistencia.
27. Ledger conserva decisión, escenario, fecha de exceso y referencia de asignación original.
28. M08 no inventa prioridad; plan suma exactamente absorción; no reescribe M07.
29. R-STK-004 no se amplía fuera de M08/M07.
30. M02/M03 sin fórmula/default implícito.
31. Contradicción no se resuelve heurísticamente.
32. Sin defaults normativos; determinismo.

---

## 33. Pruebas mínimas futuras

Cubrir al menos: identidad rules/parameters/snapshot/forecast; histórico con forecast indebido; forecast sin versión; disponibilidad/snapshot; composición de `stock_committed` completa/incompleta; segmento duplicado opening↔M05; vacío evidenciado; parámetros efectivos; P-STK-006; ventana histórica; aplicabilidad de demanda; cobertura; movimientos duplicados/mismo día/fuera de horizonte/NOT_APPLICABLE; M06; propuesta; mezcla de contextos; proyección diaria/opening cero/saldo negativo/incertidumbre; M07 actual/proyectado/umbrales/fechas; M08 pedido ya incluido total/parcialmente en opening y/o M05, pending de otra fecha, fechas comerciales inválidas, ledger sin procedencia, ledger previo, sobreconsumo, plan inválido y absorción; M09/M10; no decisión/no defaults/reproducibilidad.

---

## 34. Exclusiones v0.1

Fuera de alcance: forecasting interno; ventas→demanda; tasa→calendario; vigencia futura implícita; cutoff intradía; tolerancia temporal implícita; optimización/EOQ; fórmula normativa `stock_minimum`/`safety_stock`; imputación; resolución heurística; prioridad M08; costes TCO derivados; acciones automáticas; persistencia SQL STK; API externa; cambios C0; CRC; decisión final.

---

## 35. Estado

**Contrato v0.10:** DEPURADO FINAL OPENING/M08.  
**Hallazgos A…H:** resueltos.  
**Hallazgos I1…I3:** resueltos.  
**Frontera R-STK-004:** verificada sin ampliación.  
**M02/M03:** sin fórmula cuantitativa ni default implícito.  
**Siguiente paso:** AUDIT 2 FINAL independiente.  
**Implementación ejecutable:** NO AUTORIZADA TODAVÍA.
